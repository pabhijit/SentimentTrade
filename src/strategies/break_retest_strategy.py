#!/usr/bin/env python3
"""
Break and Retest Swing Trading Strategy
A dedicated strategy for swing trading based on support/resistance breaks and retests
"""

import backtrader as bt
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

class BreakRetestSwingStrategy(bt.Strategy):
    """
    Break and Retest Swing Trading Strategy
    
    Strategy Logic:
    1. Identify key support/resistance levels using swing highs/lows
    2. Wait for a significant breakout above resistance or below support
    3. Wait for price to retest the broken level
    4. Enter trade if retest holds (level acts as new support/resistance)
    5. Use swing trading position sizing and risk management
    """
    
    params = (
        # Level Detection Parameters
        ('lookback_period', 20),        # Period to look back for swing highs/lows
        ('min_level_strength', 3),      # Minimum touches to consider a level significant
        ('level_tolerance', 0.002),     # 0.2% tolerance for level identification
        
        # Breakout Parameters
        ('min_breakout_strength', 0.01), # 1% minimum breakout strength
        ('breakout_volume_factor', 1.5), # Volume should be 1.5x average for valid breakout
        ('max_breakout_age', 10),       # Maximum days since breakout to consider retest
        
        # Retest Parameters
        ('retest_tolerance', 0.005),    # 0.5% tolerance for retest identification
        ('min_retest_bounce', 0.003),   # 0.3% minimum bounce from retest level
        ('retest_confirmation_bars', 2), # Bars to confirm retest held
        
        # Risk Management
        ('position_size_pct', 0.02),    # 2% risk per trade
        ('stop_loss_atr_mult', 2.0),    # Stop loss at 2x ATR from entry
        ('take_profit_ratio', 3.0),     # Risk:Reward ratio of 1:3
        ('max_holding_days', 30),       # Maximum holding period for swing trades
        
        # Trade Management
        ('enable_trailing_stop', True), # Enable trailing stop loss
        ('trailing_stop_atr_mult', 1.5), # Trailing stop at 1.5x ATR
        ('partial_profit_level', 0.5),  # Take 50% profit at 1.5:1 R:R
        
        # Filters
        ('min_atr_pct', 0.01),          # Minimum 1% ATR for volatility filter
        ('trend_filter_period', 50),    # Use 50-day MA for trend filter
        ('enable_trend_filter', True),  # Only trade in direction of trend
    )
    
    def __init__(self):
        """Initialize the Break and Retest strategy"""
        
        # Technical Indicators
        self.atr = bt.indicators.ATR(period=14)
        self.sma_trend = bt.indicators.SMA(period=self.params.trend_filter_period)
        self.volume_sma = bt.indicators.SMA(self.data.volume, period=20)
        
        # Strategy State
        self.support_levels = []        # List of identified support levels
        self.resistance_levels = []     # List of identified resistance levels
        self.recent_breakouts = []      # List of recent breakouts waiting for retest
        self.swing_highs = []          # Historical swing highs
        self.swing_lows = []           # Historical swing lows
        
        # Trade Tracking
        self.entry_price = 0
        self.stop_loss_price = 0
        self.take_profit_price = 0
        self.entry_date = None
        self.trade_direction = None     # 'long' or 'short'
        self.breakout_level = 0
        
        # Performance Tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        
        print("🎯 Break and Retest Swing Strategy Initialized")
        print(f"   Lookback Period: {self.params.lookback_period} bars")
        print(f"   Min Breakout Strength: {self.params.min_breakout_strength:.1%}")
        print(f"   Position Size: {self.params.position_size_pct:.1%} risk per trade")
    
    def next(self):
        """Main strategy logic executed on each bar"""
        
        # Skip if not enough data
        if len(self.data) < self.params.lookback_period + 1:
            return
        
        # Update swing highs and lows
        self._update_swing_points()
        
        # Update support and resistance levels
        self._update_levels()
        
        # Check for breakouts
        self._check_for_breakouts()
        
        # Check for retests if we have recent breakouts
        self._check_for_retests()
        
        # Manage existing positions
        if self.position:
            self._manage_position()
        
        # Clean up old breakouts
        self._cleanup_old_breakouts()
    
    def _update_swing_points(self):
        """Identify and update swing highs and lows"""
        
        if len(self.data) < self.params.lookback_period * 2:
            return
        
        current_idx = len(self.data) - 1
        lookback = self.params.lookback_period
        
        # Check for swing high
        current_high = self.data.high[0]
        is_swing_high = True
        
        # Check if current high is higher than surrounding bars
        for i in range(1, lookback + 1):
            if (current_idx - i >= 0 and 
                self.data.high[-i] >= current_high):
                is_swing_high = False
                break
        
        if is_swing_high:
            swing_high = {
                'price': current_high,
                'date': self.data.datetime.date(0),
                'bar_index': current_idx
            }
            self.swing_highs.append(swing_high)
            
            # Keep only recent swing highs
            if len(self.swing_highs) > 50:
                self.swing_highs = self.swing_highs[-50:]
        
        # Check for swing low
        current_low = self.data.low[0]
        is_swing_low = True
        
        # Check if current low is lower than surrounding bars
        for i in range(1, lookback + 1):
            if (current_idx - i >= 0 and 
                self.data.low[-i] <= current_low):
                is_swing_low = False
                break
        
        if is_swing_low:
            swing_low = {
                'price': current_low,
                'date': self.data.datetime.date(0),
                'bar_index': current_idx
            }
            self.swing_lows.append(swing_low)
            
            # Keep only recent swing lows
            if len(self.swing_lows) > 50:
                self.swing_lows = self.swing_lows[-50:]
    
    def _update_levels(self):
        """Update support and resistance levels based on swing points"""
        
        # Update resistance levels from swing highs
        self.resistance_levels = self._identify_levels(self.swing_highs, 'resistance')
        
        # Update support levels from swing lows
        self.support_levels = self._identify_levels(self.swing_lows, 'support')
    
    def _identify_levels(self, swing_points: List[Dict], level_type: str) -> List[Dict]:
        """Identify significant support/resistance levels from swing points"""
        
        if len(swing_points) < self.params.min_level_strength:
            return []
        
        levels = []
        tolerance = self.params.level_tolerance
        
        # Group swing points into levels
        for swing in swing_points[-20:]:  # Look at recent 20 swing points
            swing_price = swing['price']
            
            # Check if this swing point is near an existing level
            level_found = False
            for level in levels:
                if abs(swing_price - level['price']) / level['price'] <= tolerance:
                    # Add this swing to existing level
                    level['touches'].append(swing)
                    level['strength'] += 1
                    # Update level price to average
                    level['price'] = np.mean([touch['price'] for touch in level['touches']])
                    level_found = True
                    break
            
            if not level_found:
                # Create new level
                new_level = {
                    'price': swing_price,
                    'type': level_type,
                    'touches': [swing],
                    'strength': 1,
                    'last_touch_date': swing['date']
                }
                levels.append(new_level)
        
        # Filter levels by minimum strength
        significant_levels = [
            level for level in levels 
            if level['strength'] >= self.params.min_level_strength
        ]
        
        # Sort by strength (most significant first)
        significant_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return significant_levels[:10]  # Keep top 10 levels
    
    def _check_for_breakouts(self):
        """Check for breakouts of significant levels"""
        
        current_price = self.data.close[0]
        current_high = self.data.high[0]
        current_low = self.data.low[0]
        current_volume = self.data.volume[0]
        avg_volume = self.volume_sma[0]
        
        # Check resistance breakouts (bullish)
        for resistance in self.resistance_levels:
            if (current_high > resistance['price'] * (1 + self.params.min_breakout_strength) and
                current_volume > avg_volume * self.params.breakout_volume_factor):
                
                breakout = {
                    'type': 'resistance_break',
                    'level_price': resistance['price'],
                    'breakout_price': current_high,
                    'breakout_date': self.data.datetime.date(0),
                    'volume_confirmation': True,
                    'direction': 'bullish',
                    'level_strength': resistance['strength']
                }
                
                # Check if we already have this breakout
                if not self._is_duplicate_breakout(breakout):
                    self.recent_breakouts.append(breakout)
                    print(f"📈 Resistance Breakout Detected: {resistance['price']:.2f} -> {current_high:.2f}")
        
        # Check support breakouts (bearish)
        for support in self.support_levels:
            if (current_low < support['price'] * (1 - self.params.min_breakout_strength) and
                current_volume > avg_volume * self.params.breakout_volume_factor):
                
                breakout = {
                    'type': 'support_break',
                    'level_price': support['price'],
                    'breakout_price': current_low,
                    'breakout_date': self.data.datetime.date(0),
                    'volume_confirmation': True,
                    'direction': 'bearish',
                    'level_strength': support['strength']
                }
                
                # Check if we already have this breakout
                if not self._is_duplicate_breakout(breakout):
                    self.recent_breakouts.append(breakout)
                    print(f"📉 Support Breakout Detected: {support['price']:.2f} -> {current_low:.2f}")
    
    def _is_duplicate_breakout(self, new_breakout: Dict) -> bool:
        """Check if breakout is duplicate of recent breakout"""
        
        for existing in self.recent_breakouts:
            if (abs(new_breakout['level_price'] - existing['level_price']) / 
                existing['level_price'] < self.params.level_tolerance and
                new_breakout['direction'] == existing['direction']):
                return True
        return False
    
    def _check_for_retests(self):
        """Check for retests of broken levels"""
        
        if not self.recent_breakouts or self.position:
            return
        
        current_price = self.data.close[0]
        current_high = self.data.high[0]
        current_low = self.data.low[0]
        
        for breakout in self.recent_breakouts[:]:  # Copy list to allow modification
            level_price = breakout['level_price']
            direction = breakout['direction']
            
            # Check for bullish retest (price comes back down to test broken resistance)
            if (direction == 'bullish' and 
                current_low <= level_price * (1 + self.params.retest_tolerance) and
                current_low >= level_price * (1 - self.params.retest_tolerance)):
                
                # Check if retest holds (price bounces back up)
                if self._confirm_retest_hold(breakout, 'bullish'):
                    self._enter_long_trade(breakout)
                    self.recent_breakouts.remove(breakout)
            
            # Check for bearish retest (price comes back up to test broken support)
            elif (direction == 'bearish' and 
                  current_high >= level_price * (1 - self.params.retest_tolerance) and
                  current_high <= level_price * (1 + self.params.retest_tolerance)):
                
                # Check if retest holds (price bounces back down)
                if self._confirm_retest_hold(breakout, 'bearish'):
                    self._enter_short_trade(breakout)
                    self.recent_breakouts.remove(breakout)
    
    def _confirm_retest_hold(self, breakout: Dict, direction: str) -> bool:
        """Confirm that the retest level is holding"""
        
        # Simple confirmation: check if price has moved away from level
        current_price = self.data.close[0]
        level_price = breakout['level_price']
        min_bounce = self.params.min_retest_bounce
        
        if direction == 'bullish':
            # For bullish retest, price should bounce up from the level
            return current_price > level_price * (1 + min_bounce)
        else:
            # For bearish retest, price should bounce down from the level
            return current_price < level_price * (1 - min_bounce)
    
    def _enter_long_trade(self, breakout: Dict):
        """Enter a long position after successful bullish retest"""
        
        if not self._apply_filters('long'):
            return
        
        current_price = self.data.close[0]
        atr_value = self.atr[0]
        
        # Calculate position size based on risk
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        stop_distance = atr_value * self.params.stop_loss_atr_mult
        position_size = int(risk_amount / stop_distance)
        
        if position_size > 0:
            # Enter long position
            self.buy(size=position_size)
            
            # Set trade parameters
            self.entry_price = current_price
            self.stop_loss_price = current_price - stop_distance
            self.take_profit_price = current_price + (stop_distance * self.params.take_profit_ratio)
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'long'
            self.breakout_level = breakout['level_price']
            
            print(f"🟢 LONG Entry: ${current_price:.2f} | Stop: ${self.stop_loss_price:.2f} | Target: ${self.take_profit_price:.2f}")
    
    def _enter_short_trade(self, breakout: Dict):
        """Enter a short position after successful bearish retest"""
        
        if not self._apply_filters('short'):
            return
        
        current_price = self.data.close[0]
        atr_value = self.atr[0]
        
        # Calculate position size based on risk
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        stop_distance = atr_value * self.params.stop_loss_atr_mult
        position_size = int(risk_amount / stop_distance)
        
        if position_size > 0:
            # Enter short position
            self.sell(size=position_size)
            
            # Set trade parameters
            self.entry_price = current_price
            self.stop_loss_price = current_price + stop_distance
            self.take_profit_price = current_price - (stop_distance * self.params.take_profit_ratio)
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'short'
            self.breakout_level = breakout['level_price']
            
            print(f"🔴 SHORT Entry: ${current_price:.2f} | Stop: ${self.stop_loss_price:.2f} | Target: ${self.take_profit_price:.2f}")
    
    def _apply_filters(self, direction: str) -> bool:
        """Apply filters to determine if trade should be taken"""
        
        # ATR filter - ensure sufficient volatility
        if self.atr[0] / self.data.close[0] < self.params.min_atr_pct:
            return False
        
        # Trend filter - only trade in direction of trend
        if self.params.enable_trend_filter:
            current_price = self.data.close[0]
            trend_ma = self.sma_trend[0]
            
            if direction == 'long' and current_price < trend_ma:
                return False
            elif direction == 'short' and current_price > trend_ma:
                return False
        
        return True
    
    def _manage_position(self):
        """Manage existing position with stops, targets, and time-based exit"""
        
        current_price = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # Time-based exit
        if self.entry_date:
            days_held = (current_date - self.entry_date).days
            if days_held >= self.params.max_holding_days:
                self.close()
                print(f"⏰ Time-based exit after {days_held} days")
                return
        
        # Stop loss and take profit
        if self.trade_direction == 'long':
            if current_price <= self.stop_loss_price:
                self.close()
                print(f"🛑 Long Stop Loss hit: ${current_price:.2f}")
                return
            elif current_price >= self.take_profit_price:
                self.close()
                print(f"🎯 Long Take Profit hit: ${current_price:.2f}")
                return
        
        elif self.trade_direction == 'short':
            if current_price >= self.stop_loss_price:
                self.close()
                print(f"🛑 Short Stop Loss hit: ${current_price:.2f}")
                return
            elif current_price <= self.take_profit_price:
                self.close()
                print(f"🎯 Short Take Profit hit: ${current_price:.2f}")
                return
        
        # Trailing stop logic
        if self.params.enable_trailing_stop:
            self._update_trailing_stop()
    
    def _update_trailing_stop(self):
        """Update trailing stop loss"""
        
        current_price = self.data.close[0]
        atr_value = self.atr[0]
        trailing_distance = atr_value * self.params.trailing_stop_atr_mult
        
        if self.trade_direction == 'long':
            new_stop = current_price - trailing_distance
            if new_stop > self.stop_loss_price:
                self.stop_loss_price = new_stop
        
        elif self.trade_direction == 'short':
            new_stop = current_price + trailing_distance
            if new_stop < self.stop_loss_price:
                self.stop_loss_price = new_stop
    
    def _cleanup_old_breakouts(self):
        """Remove old breakouts that are no longer relevant"""
        
        current_date = self.data.datetime.date(0)
        max_age = timedelta(days=self.params.max_breakout_age)
        
        self.recent_breakouts = [
            breakout for breakout in self.recent_breakouts
            if (current_date - breakout['breakout_date']) <= max_age
        ]
    
    def notify_trade(self, trade):
        """Handle trade notifications"""
        
        if trade.isclosed:
            self.total_trades += 1
            pnl = trade.pnl
            self.total_pnl += pnl
            
            if pnl > 0:
                self.winning_trades += 1
                print(f"✅ Trade Closed: +${pnl:.2f}")
            else:
                self.losing_trades += 1
                print(f"❌ Trade Closed: ${pnl:.2f}")
            
            # Reset trade parameters
            self.entry_price = 0
            self.stop_loss_price = 0
            self.take_profit_price = 0
            self.entry_date = None
            self.trade_direction = None
            self.breakout_level = 0
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get strategy performance statistics"""
        
        win_rate = (self.winning_trades / max(self.total_trades, 1)) * 100
        avg_pnl = self.total_pnl / max(self.total_trades, 1)
        
        return {
            'strategy_name': 'Break and Retest Swing',
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'total_pnl': self.total_pnl,
            'avg_pnl_per_trade': avg_pnl,
            'support_levels_count': len(self.support_levels),
            'resistance_levels_count': len(self.resistance_levels),
            'active_breakouts': len(self.recent_breakouts)
        }
