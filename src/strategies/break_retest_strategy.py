#!/usr/bin/env python3
"""
Enhanced Break and Retest Swing Trading Strategy
Advanced implementation with selective entry, adaptive exits, and comprehensive filtering
"""

import backtrader as bt
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

class BreakRetestSwingStrategy(bt.Strategy):
    """
    Enhanced Break and Retest Swing Trading Strategy
    
    Key Enhancements:
    1. Selective Entry: Candlestick patterns + momentum confirmation
    2. Adaptive Exits: Structure-based stops and dynamic take profits
    3. Close-based Breakouts: More reliable than intrabar highs/lows
    4. Trade Clustering Prevention: Cooldown periods between trades
    5. Dynamic Stop/TP: Based on swing points rather than fixed ratios
    6. Enhanced Metrics: Retest success tracking and performance analysis
    
    Strategy Logic:
    1. Identify key support/resistance levels using swing highs/lows
    2. Wait for a significant CLOSE-based breakout with volume confirmation
    3. Wait for price to retest the broken level
    4. Confirm retest with candlestick patterns and momentum
    5. Enter trade with structure-based stops and adaptive targets
    6. Use comprehensive risk management and position sizing
    """
    
    params = (
        # Level Detection Parameters
        ('lookback_period', 20),        # Period to look back for swing highs/lows
        ('min_level_strength', 3),      # Minimum touches to consider a level significant
        ('level_tolerance', 0.002),     # 0.2% tolerance for level identification
        
        # Enhanced Breakout Parameters
        ('min_breakout_strength', 0.01), # 1% minimum breakout strength
        ('breakout_volume_factor', 1.5), # Volume should be 1.5x average for valid breakout
        ('max_breakout_age', 10),       # Maximum days since breakout to consider retest
        ('use_close_breakout', True),   # Use closing price for breakout confirmation
        
        # Enhanced Retest Parameters
        ('retest_tolerance', 0.005),    # 0.5% tolerance for retest identification
        ('min_retest_bounce', 0.003),   # 0.3% minimum bounce from retest level
        ('retest_confirmation_bars', 2), # Bars to confirm retest held
        ('require_pattern_confirmation', True), # Require candlestick pattern confirmation
        ('require_momentum_confirmation', True), # Require momentum confirmation
        
        # Enhanced Risk Management
        ('position_size_pct', 0.02),    # 2% risk per trade
        ('use_structure_stops', True),  # Use swing-based stops instead of ATR
        ('stop_loss_atr_mult', 2.0),    # Fallback ATR stop if no structure available
        ('use_adaptive_tp', True),      # Use adaptive take profit based on structure
        ('take_profit_ratio', 3.0),     # Fallback fixed R:R ratio
        ('max_holding_days', 30),       # Maximum holding period for swing trades
        
        # Trade Management Enhancements
        ('enable_trailing_stop', True), # Enable trailing stop loss
        ('trailing_stop_atr_mult', 1.5), # Trailing stop at 1.5x ATR
        ('partial_profit_level', 0.5),  # Take 50% profit at 1.5:1 R:R
        ('trade_cooldown_days', 3),     # Days to wait between trades in same area
        
        # Confirmation Indicators
        ('rsi_period', 7),              # RSI period for momentum confirmation
        ('rsi_momentum_threshold', 2),  # RSI must improve by this amount
        ('pattern_lookback', 3),        # Bars to look back for pattern confirmation
        
        # Filters
        ('min_atr_pct', 0.01),          # Minimum 1% ATR for volatility filter
        ('trend_filter_period', 50),    # Use 50-day MA for trend filter
        ('enable_trend_filter', True),  # Only trade in direction of trend
        ('max_concurrent_trades', 1),   # Maximum concurrent positions
        
        # Performance Tracking
        ('track_retest_success', True), # Track retest success rates
        ('min_trade_spacing', 0.02),    # Minimum 2% price difference between trades
    )
    
    def __init__(self):
        """Initialize the Enhanced Break and Retest strategy"""
        
        # Technical Indicators
        self.atr = bt.indicators.ATR(period=14)
        self.sma_trend = bt.indicators.SMA(period=self.params.trend_filter_period)
        self.volume_sma = bt.indicators.SMA(self.data.volume, period=20)
        
        # Enhanced Confirmation Indicators
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.roc = bt.indicators.RateOfChange(period=3)  # Price momentum
        
        # Strategy State
        self.support_levels = []        # List of identified support levels
        self.resistance_levels = []     # List of identified resistance levels
        self.recent_breakouts = []      # List of recent breakouts waiting for retest
        self.swing_highs = []          # Historical swing highs
        self.swing_lows = []           # Historical swing lows
        
        # Enhanced Trade Tracking
        self.entry_price = 0
        self.stop_loss_price = 0
        self.take_profit_price = 0
        self.entry_date = None
        self.trade_direction = None     # 'long' or 'short'
        self.breakout_level = 0
        self.structure_stop = 0         # Structure-based stop level
        self.structure_target = 0       # Structure-based target level
        
        # Trade History and Cooldown
        self.recent_trade_levels = []   # Recent trade levels for clustering prevention
        self.last_trade_date = None     # Last trade date for cooldown
        
        # Enhanced Performance Tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.retest_attempts = 0        # Total retest attempts
        self.successful_retests = 0     # Successful retests that led to trades
        self.breakout_success_rate = 0.0
        
        # Pattern Recognition State
        self.pattern_confirmed = False
        self.momentum_confirmed = False
        
        print("🎯 Enhanced Break and Retest Swing Strategy Initialized")
        print(f"   Lookback Period: {self.params.lookback_period} bars")
        print(f"   Min Breakout Strength: {self.params.min_breakout_strength:.1%}")
        print(f"   Position Size: {self.params.position_size_pct:.1%} risk per trade")
        print(f"   Enhanced Features: Pattern Confirmation, Structure Stops, Adaptive TP")
        print(f"   Trade Cooldown: {self.params.trade_cooldown_days} days")
    
    def next(self):
        """Main strategy logic executed on each bar"""
        
        # Skip if not enough data
        if len(self.data) < self.params.lookback_period + 1:
            return
        
        # Update swing highs and lows
        self._update_swing_points()
        
        # Update support and resistance levels
        self._update_levels()
        
        # Check for breakouts (enhanced with close-based confirmation)
        self._check_for_enhanced_breakouts()
        
        # Check for retests with enhanced confirmation
        self._check_for_enhanced_retests()
        
        # Manage existing positions with enhanced logic
        if self.position:
            self._manage_enhanced_position()
        
        # Clean up old breakouts and trade history
        self._cleanup_old_data()
        
        # Update performance metrics
        self._update_performance_metrics()
    
    def _update_swing_points(self):
        """Identify and update swing highs and lows with enhanced logic"""
        
        if len(self.data) < self.params.lookback_period * 2:
            return
        
        current_idx = len(self.data) - 1
        lookback = self.params.lookback_period
        
        # Enhanced swing high detection
        current_high = self.data.high[0]
        is_swing_high = True
        
        # Check if current high is higher than surrounding bars
        for i in range(1, lookback + 1):
            if (current_idx - i >= 0 and 
                self.data.high[-i] >= current_high):
                is_swing_high = False
                break
        
        # Additional confirmation: volume should be above average
        if is_swing_high and self.data.volume[0] > self.volume_sma[0] * 0.8:
            swing_high = {
                'price': current_high,
                'date': self.data.datetime.date(0),
                'bar_index': current_idx,
                'volume_confirmed': self.data.volume[0] > self.volume_sma[0],
                'strength_score': self._calculate_swing_strength(current_high, 'high')
            }
            self.swing_highs.append(swing_high)
            
            # Keep only recent swing highs
            if len(self.swing_highs) > 50:
                self.swing_highs = self.swing_highs[-50:]
        
        # Enhanced swing low detection
        current_low = self.data.low[0]
        is_swing_low = True
        
        # Check if current low is lower than surrounding bars
        for i in range(1, lookback + 1):
            if (current_idx - i >= 0 and 
                self.data.low[-i] <= current_low):
                is_swing_low = False
                break
        
        # Additional confirmation: volume should be above average
        if is_swing_low and self.data.volume[0] > self.volume_sma[0] * 0.8:
            swing_low = {
                'price': current_low,
                'date': self.data.datetime.date(0),
                'bar_index': current_idx,
                'volume_confirmed': self.data.volume[0] > self.volume_sma[0],
                'strength_score': self._calculate_swing_strength(current_low, 'low')
            }
            self.swing_lows.append(swing_low)
            
            # Keep only recent swing lows
            if len(self.swing_lows) > 50:
                self.swing_lows = self.swing_lows[-50:]
    
    def _calculate_swing_strength(self, price: float, swing_type: str) -> float:
        """Calculate the strength of a swing point based on multiple factors"""
        
        strength = 1.0
        
        # Volume confirmation adds strength
        if self.data.volume[0] > self.volume_sma[0] * 1.2:
            strength += 0.5
        
        # Distance from recent swings adds strength
        recent_swings = self.swing_highs[-5:] if swing_type == 'high' else self.swing_lows[-5:]
        if recent_swings:
            avg_distance = np.mean([abs(price - swing['price']) / price for swing in recent_swings])
            if avg_distance > 0.02:  # 2% or more difference
                strength += 0.3
        
        # ATR-relative strength
        if self.atr[0] > 0:
            atr_multiple = abs(price - self.data.close[-1]) / self.atr[0]
            if atr_multiple > 1.5:
                strength += 0.2
        
        return min(strength, 3.0)  # Cap at 3.0
    def _check_for_enhanced_breakouts(self):
        """Enhanced breakout detection with close-based confirmation"""
        
        current_close = self.data.close[0]
        current_high = self.data.high[0]
        current_low = self.data.low[0]
        current_volume = self.data.volume[0]
        avg_volume = self.volume_sma[0]
        
        # Use close-based breakouts for more reliability
        breakout_price = current_close if self.params.use_close_breakout else current_high
        breakdown_price = current_close if self.params.use_close_breakout else current_low
        
        # Check resistance breakouts (bullish)
        for resistance in self.resistance_levels:
            if (breakout_price > resistance['price'] * (1 + self.params.min_breakout_strength) and
                current_volume > avg_volume * self.params.breakout_volume_factor):
                
                # Additional confirmation: ensure it's not a false breakout
                if self._confirm_breakout_strength(resistance['price'], 'bullish'):
                    breakout = {
                        'type': 'resistance_break',
                        'level_price': resistance['price'],
                        'breakout_price': breakout_price,
                        'breakout_date': self.data.datetime.date(0),
                        'volume_confirmation': True,
                        'direction': 'bullish',
                        'level_strength': resistance['strength'],
                        'close_based': self.params.use_close_breakout,
                        'strength_score': self._calculate_breakout_strength(resistance, 'bullish')
                    }
                    
                    # Check if we already have this breakout
                    if not self._is_duplicate_breakout(breakout):
                        self.recent_breakouts.append(breakout)
                        print(f"📈 Enhanced Resistance Breakout: {resistance['price']:.2f} -> {breakout_price:.2f} (Close-based: {self.params.use_close_breakout})")
        
        # Check support breakouts (bearish)
        for support in self.support_levels:
            if (breakdown_price < support['price'] * (1 - self.params.min_breakout_strength) and
                current_volume > avg_volume * self.params.breakout_volume_factor):
                
                # Additional confirmation: ensure it's not a false breakdown
                if self._confirm_breakout_strength(support['price'], 'bearish'):
                    breakout = {
                        'type': 'support_break',
                        'level_price': support['price'],
                        'breakout_price': breakdown_price,
                        'breakout_date': self.data.datetime.date(0),
                        'volume_confirmation': True,
                        'direction': 'bearish',
                        'level_strength': support['strength'],
                        'close_based': self.params.use_close_breakout,
                        'strength_score': self._calculate_breakout_strength(support, 'bearish')
                    }
                    
                    # Check if we already have this breakout
                    if not self._is_duplicate_breakout(breakout):
                        self.recent_breakouts.append(breakout)
                        print(f"📉 Enhanced Support Breakout: {support['price']:.2f} -> {breakdown_price:.2f} (Close-based: {self.params.use_close_breakout})")
    
    def _confirm_breakout_strength(self, level_price: float, direction: str) -> bool:
        """Confirm breakout strength with additional filters"""
        
        current_close = self.data.close[0]
        
        # Ensure breakout is decisive (not just barely breaking)
        if direction == 'bullish':
            breakout_strength = (current_close - level_price) / level_price
            return breakout_strength >= self.params.min_breakout_strength * 1.2  # 20% buffer
        else:
            breakout_strength = (level_price - current_close) / level_price
            return breakout_strength >= self.params.min_breakout_strength * 1.2  # 20% buffer
    
    def _calculate_breakout_strength(self, level: Dict, direction: str) -> float:
        """Calculate the overall strength of a breakout"""
        
        strength = level.get('strength', 1)
        
        # Volume confirmation adds strength
        volume_ratio = self.data.volume[0] / self.volume_sma[0]
        if volume_ratio > 2.0:
            strength += 1.0
        elif volume_ratio > 1.5:
            strength += 0.5
        
        # ATR-relative breakout size
        if self.atr[0] > 0:
            current_close = self.data.close[0]
            level_price = level['price']
            atr_multiple = abs(current_close - level_price) / self.atr[0]
            if atr_multiple > 2.0:
                strength += 0.5
        
        return strength
    
    def _check_for_enhanced_retests(self):
        """Enhanced retest detection with pattern and momentum confirmation"""
        
        if not self.recent_breakouts or self.position:
            return
        
        # Check cooldown period
        if self._is_in_cooldown():
            return
        
        current_price = self.data.close[0]
        current_high = self.data.high[0]
        current_low = self.data.low[0]
        
        for breakout in self.recent_breakouts[:]:  # Copy list to allow modification
            level_price = breakout['level_price']
            direction = breakout['direction']
            
            self.retest_attempts += 1
            
            # Check for bullish retest (price comes back down to test broken resistance)
            if (direction == 'bullish' and 
                current_low <= level_price * (1 + self.params.retest_tolerance) and
                current_low >= level_price * (1 - self.params.retest_tolerance)):
                
                # Enhanced retest confirmation
                if self._confirm_enhanced_retest_hold(breakout, 'bullish'):
                    if self._enter_enhanced_long_trade(breakout):
                        self.successful_retests += 1
                        self.recent_breakouts.remove(breakout)
                        print(f"✅ Successful Bullish Retest Trade Entered at {current_price:.2f}")
            
            # Check for bearish retest (price comes back up to test broken support)
            elif (direction == 'bearish' and 
                  current_high >= level_price * (1 - self.params.retest_tolerance) and
                  current_high <= level_price * (1 + self.params.retest_tolerance)):
                
                # Enhanced retest confirmation
                if self._confirm_enhanced_retest_hold(breakout, 'bearish'):
                    if self._enter_enhanced_short_trade(breakout):
                        self.successful_retests += 1
                        self.recent_breakouts.remove(breakout)
                        print(f"✅ Successful Bearish Retest Trade Entered at {current_price:.2f}")
    
    def _confirm_enhanced_retest_hold(self, breakout: Dict, direction: str) -> bool:
        """Enhanced retest confirmation with patterns and momentum"""
        
        # Basic bounce confirmation
        current_price = self.data.close[0]
        level_price = breakout['level_price']
        min_bounce = self.params.min_retest_bounce
        
        basic_bounce = False
        if direction == 'bullish':
            basic_bounce = current_price > level_price * (1 + min_bounce)
        else:
            basic_bounce = current_price < level_price * (1 - min_bounce)
        
        if not basic_bounce:
            return False
        
        # Enhanced confirmations
        confirmations = []
        
        # 1. Candlestick Pattern Confirmation
        if self.params.require_pattern_confirmation:
            pattern_confirmed = self._check_candlestick_patterns(direction)
            confirmations.append(pattern_confirmed)
            if pattern_confirmed:
                print(f"   ✓ Candlestick pattern confirmed for {direction} retest")
        
        # 2. Momentum Confirmation (RSI turning in favor)
        if self.params.require_momentum_confirmation:
            momentum_confirmed = self._check_momentum_confirmation(direction)
            confirmations.append(momentum_confirmed)
            if momentum_confirmed:
                print(f"   ✓ Momentum confirmed for {direction} retest (RSI: {self.rsi[0]:.1f})")
        
        # 3. Volume Confirmation (retest on decent volume)
        volume_confirmed = self.data.volume[0] > self.volume_sma[0] * 0.8
        confirmations.append(volume_confirmed)
        if volume_confirmed:
            print(f"   ✓ Volume confirmed for retest")
        
        # Require at least 2 out of 3 confirmations
        confirmed_count = sum(confirmations)
        total_required = len([c for c in [self.params.require_pattern_confirmation, 
                                        self.params.require_momentum_confirmation, True] if c])
        
        success_rate = confirmed_count / len(confirmations) if confirmations else 0
        return success_rate >= 0.67  # At least 67% of confirmations must pass
    
    def _check_candlestick_patterns(self, direction: str) -> bool:
        """Check for bullish/bearish candlestick patterns"""
        
        if len(self.data) < 3:
            return False
        
        # Current and previous candles
        curr_open = self.data.open[0]
        curr_high = self.data.high[0]
        curr_low = self.data.low[0]
        curr_close = self.data.close[0]
        
        prev_open = self.data.open[-1]
        prev_high = self.data.high[-1]
        prev_low = self.data.low[-1]
        prev_close = self.data.close[-1]
        
        if direction == 'bullish':
            # Look for bullish patterns
            
            # Bullish Engulfing
            if (prev_close < prev_open and  # Previous red candle
                curr_close > curr_open and  # Current green candle
                curr_open < prev_close and  # Current opens below previous close
                curr_close > prev_open):    # Current closes above previous open
                print("   📊 Bullish Engulfing pattern detected")
                return True
            
            # Hammer/Doji at support
            body_size = abs(curr_close - curr_open)
            total_range = curr_high - curr_low
            lower_shadow = curr_open - curr_low if curr_close > curr_open else curr_close - curr_low
            
            if (total_range > 0 and 
                body_size / total_range < 0.3 and  # Small body
                lower_shadow / total_range > 0.6): # Long lower shadow
                print("   📊 Hammer/Doji pattern detected")
                return True
            
            # Simple green candle after red
            if prev_close < prev_open and curr_close > curr_open:
                return True
        
        else:  # bearish
            # Look for bearish patterns
            
            # Bearish Engulfing
            if (prev_close > prev_open and  # Previous green candle
                curr_close < curr_open and  # Current red candle
                curr_open > prev_close and  # Current opens above previous close
                curr_close < prev_open):    # Current closes below previous open
                print("   📊 Bearish Engulfing pattern detected")
                return True
            
            # Shooting Star/Doji at resistance
            body_size = abs(curr_close - curr_open)
            total_range = curr_high - curr_low
            upper_shadow = curr_high - curr_open if curr_close < curr_open else curr_high - curr_close
            
            if (total_range > 0 and 
                body_size / total_range < 0.3 and  # Small body
                upper_shadow / total_range > 0.6): # Long upper shadow
                print("   📊 Shooting Star/Doji pattern detected")
                return True
            
            # Simple red candle after green
            if prev_close > prev_open and curr_close < curr_open:
                return True
        
        return False
    
    def _check_momentum_confirmation(self, direction: str) -> bool:
        """Check for momentum confirmation using RSI"""
        
        if len(self.data) < self.params.rsi_period + 2:
            return False
        
        current_rsi = self.rsi[0]
        previous_rsi = self.rsi[-1]
        rsi_change = current_rsi - previous_rsi
        
        if direction == 'bullish':
            # For bullish retest, RSI should be turning up
            # and not be overbought
            return (rsi_change >= self.params.rsi_momentum_threshold and 
                    current_rsi < 70 and current_rsi > 30)
        else:
            # For bearish retest, RSI should be turning down
            # and not be oversold
            return (rsi_change <= -self.params.rsi_momentum_threshold and 
                    current_rsi > 30 and current_rsi < 70)
    
    def _is_in_cooldown(self) -> bool:
        """Check if we're in cooldown period between trades"""
        
        if not self.last_trade_date:
            return False
        
        current_date = self.data.datetime.date(0)
        days_since_last_trade = (current_date - self.last_trade_date).days
        
        return days_since_last_trade < self.params.trade_cooldown_days
    
    def _is_near_recent_trade(self, price: float) -> bool:
        """Check if price is too close to recent trade levels"""
        
        for trade_level in self.recent_trade_levels:
            if abs(price - trade_level) / trade_level < self.params.min_trade_spacing:
                return True
        return False
    def _enter_enhanced_long_trade(self, breakout: Dict) -> bool:
        """Enter enhanced long position with structure-based stops and adaptive targets"""
        
        if not self._apply_enhanced_filters('long'):
            return False
        
        current_price = self.data.close[0]
        
        # Check if too close to recent trades
        if self._is_near_recent_trade(current_price):
            print(f"   ⚠️ Skipping trade - too close to recent trade level")
            return False
        
        # Calculate structure-based stop loss
        structure_stop = self._calculate_structure_stop('long')
        if structure_stop == 0:
            # Fallback to ATR-based stop
            atr_value = self.atr[0]
            structure_stop = current_price - (atr_value * self.params.stop_loss_atr_mult)
        
        # Calculate structure-based take profit
        structure_target = self._calculate_structure_target('long', current_price, structure_stop)
        
        # Calculate position size based on actual risk
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        actual_stop_distance = current_price - structure_stop
        
        if actual_stop_distance <= 0:
            print(f"   ⚠️ Invalid stop distance: {actual_stop_distance}")
            return False
        
        position_size = int(risk_amount / actual_stop_distance)
        
        if position_size <= 0:
            print(f"   ⚠️ Invalid position size: {position_size}")
            return False
        
        # Execute the trade
        order = self.buy(size=position_size)
        
        if order:
            # Set trade tracking variables
            self.entry_price = current_price
            self.stop_loss_price = structure_stop
            self.take_profit_price = structure_target
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'long'
            self.breakout_level = breakout['level_price']
            self.structure_stop = structure_stop
            self.structure_target = structure_target
            
            # Add to recent trade levels
            self.recent_trade_levels.append(current_price)
            self.last_trade_date = self.data.datetime.date(0)
            
            # Calculate risk-reward ratio
            risk = current_price - structure_stop
            reward = structure_target - current_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            print(f"🟢 LONG ENTRY: Price: {current_price:.2f}")
            print(f"   📍 Structure Stop: {structure_stop:.2f} (Risk: {risk:.2f})")
            print(f"   🎯 Structure Target: {structure_target:.2f} (Reward: {reward:.2f})")
            print(f"   📊 R:R Ratio: 1:{rr_ratio:.2f}")
            print(f"   📦 Position Size: {position_size} shares")
            print(f"   💰 Risk Amount: ${risk_amount:.2f}")
            
            return True
        
        return False
    
    def _enter_enhanced_short_trade(self, breakout: Dict) -> bool:
        """Enter enhanced short position with structure-based stops and adaptive targets"""
        
        if not self._apply_enhanced_filters('short'):
            return False
        
        current_price = self.data.close[0]
        
        # Check if too close to recent trades
        if self._is_near_recent_trade(current_price):
            print(f"   ⚠️ Skipping trade - too close to recent trade level")
            return False
        
        # Calculate structure-based stop loss
        structure_stop = self._calculate_structure_stop('short')
        if structure_stop == 0:
            # Fallback to ATR-based stop
            atr_value = self.atr[0]
            structure_stop = current_price + (atr_value * self.params.stop_loss_atr_mult)
        
        # Calculate structure-based take profit
        structure_target = self._calculate_structure_target('short', current_price, structure_stop)
        
        # Calculate position size based on actual risk
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        actual_stop_distance = structure_stop - current_price
        
        if actual_stop_distance <= 0:
            print(f"   ⚠️ Invalid stop distance: {actual_stop_distance}")
            return False
        
        position_size = int(risk_amount / actual_stop_distance)
        
        if position_size <= 0:
            print(f"   ⚠️ Invalid position size: {position_size}")
            return False
        
        # Execute the trade
        order = self.sell(size=position_size)
        
        if order:
            # Set trade tracking variables
            self.entry_price = current_price
            self.stop_loss_price = structure_stop
            self.take_profit_price = structure_target
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'short'
            self.breakout_level = breakout['level_price']
            self.structure_stop = structure_stop
            self.structure_target = structure_target
            
            # Add to recent trade levels
            self.recent_trade_levels.append(current_price)
            self.last_trade_date = self.data.datetime.date(0)
            
            # Calculate risk-reward ratio
            risk = structure_stop - current_price
            reward = current_price - structure_target
            rr_ratio = reward / risk if risk > 0 else 0
            
            print(f"🔴 SHORT ENTRY: Price: {current_price:.2f}")
            print(f"   📍 Structure Stop: {structure_stop:.2f} (Risk: {risk:.2f})")
            print(f"   🎯 Structure Target: {structure_target:.2f} (Reward: {reward:.2f})")
            print(f"   📊 R:R Ratio: 1:{rr_ratio:.2f}")
            print(f"   📦 Position Size: {position_size} shares")
            print(f"   💰 Risk Amount: ${risk_amount:.2f}")
            
            return True
        
        return False
    
    def _calculate_structure_stop(self, direction: str) -> float:
        """Calculate structure-based stop loss using swing points"""
        
        if not self.params.use_structure_stops:
            return 0
        
        current_price = self.data.close[0]
        
        if direction == 'long':
            # For long trades, stop below recent swing low
            recent_lows = [swing['price'] for swing in self.swing_lows[-5:]]
            if recent_lows:
                # Find the highest low below current price (most recent support)
                valid_lows = [low for low in recent_lows if low < current_price * 0.98]
                if valid_lows:
                    structure_stop = max(valid_lows) * 0.995  # Slightly below the swing low
                    print(f"   📍 Structure stop (long): {structure_stop:.2f} based on swing low")
                    return structure_stop
        
        else:  # short
            # For short trades, stop above recent swing high
            recent_highs = [swing['price'] for swing in self.swing_highs[-5:]]
            if recent_highs:
                # Find the lowest high above current price (most recent resistance)
                valid_highs = [high for high in recent_highs if high > current_price * 1.02]
                if valid_highs:
                    structure_stop = min(valid_highs) * 1.005  # Slightly above the swing high
                    print(f"   📍 Structure stop (short): {structure_stop:.2f} based on swing high")
                    return structure_stop
        
        return 0  # No valid structure found
    
    def _calculate_structure_target(self, direction: str, entry_price: float, stop_price: float) -> float:
        """Calculate adaptive take profit target based on structure and risk"""
        
        if not self.params.use_adaptive_tp:
            # Use fixed risk-reward ratio
            risk = abs(entry_price - stop_price)
            if direction == 'long':
                return entry_price + (risk * self.params.take_profit_ratio)
            else:
                return entry_price - (risk * self.params.take_profit_ratio)
        
        # Structure-based targets
        if direction == 'long':
            # Look for next resistance level as target
            potential_targets = []
            
            # Check resistance levels
            for resistance in self.resistance_levels:
                if resistance['price'] > entry_price * 1.01:  # At least 1% above entry
                    potential_targets.append(resistance['price'])
            
            # Check recent swing highs
            for swing in self.swing_highs[-10:]:
                if swing['price'] > entry_price * 1.01:
                    potential_targets.append(swing['price'])
            
            if potential_targets:
                # Use the nearest significant target
                nearest_target = min(potential_targets)
                
                # Ensure minimum risk-reward ratio
                risk = entry_price - stop_price
                min_target = entry_price + (risk * 1.5)  # Minimum 1.5:1 R:R
                
                structure_target = max(nearest_target, min_target)
                print(f"   🎯 Structure target (long): {structure_target:.2f}")
                return structure_target
        
        else:  # short
            # Look for next support level as target
            potential_targets = []
            
            # Check support levels
            for support in self.support_levels:
                if support['price'] < entry_price * 0.99:  # At least 1% below entry
                    potential_targets.append(support['price'])
            
            # Check recent swing lows
            for swing in self.swing_lows[-10:]:
                if swing['price'] < entry_price * 0.99:
                    potential_targets.append(swing['price'])
            
            if potential_targets:
                # Use the nearest significant target
                nearest_target = max(potential_targets)
                
                # Ensure minimum risk-reward ratio
                risk = stop_price - entry_price
                min_target = entry_price - (risk * 1.5)  # Minimum 1.5:1 R:R
                
                structure_target = min(nearest_target, min_target)
                print(f"   🎯 Structure target (short): {structure_target:.2f}")
                return structure_target
        
        # Fallback to fixed ratio
        risk = abs(entry_price - stop_price)
        if direction == 'long':
            return entry_price + (risk * self.params.take_profit_ratio)
        else:
            return entry_price - (risk * self.params.take_profit_ratio)
    
    def _apply_enhanced_filters(self, direction: str) -> bool:
        """Apply enhanced filters before entering trades"""
        
        # Basic filters
        if not self._apply_basic_filters(direction):
            return False
        
        # Maximum concurrent trades filter
        if self.position and self.params.max_concurrent_trades <= 1:
            print(f"   ⚠️ Max concurrent trades reached: {self.params.max_concurrent_trades}")
            return False
        
        # Volatility filter (enhanced)
        atr_pct = self.atr[0] / self.data.close[0]
        if atr_pct < self.params.min_atr_pct:
            print(f"   ⚠️ Insufficient volatility: {atr_pct:.3f} < {self.params.min_atr_pct:.3f}")
            return False
        
        # Trend filter (enhanced)
        if self.params.enable_trend_filter:
            current_price = self.data.close[0]
            trend_ma = self.sma_trend[0]
            
            if direction == 'long' and current_price < trend_ma * 1.02:
                print(f"   ⚠️ Against trend: Price {current_price:.2f} below trend MA {trend_ma:.2f}")
                return False
            elif direction == 'short' and current_price > trend_ma * 0.98:
                print(f"   ⚠️ Against trend: Price {current_price:.2f} above trend MA {trend_ma:.2f}")
                return False
        
        return True
    
    def _apply_basic_filters(self, direction: str) -> bool:
        """Apply basic trading filters"""
        
        # Ensure we have enough cash
        if self.broker.getcash() < 1000:  # Minimum $1000
            return False
        
        # Ensure we have valid ATR
        if self.atr[0] <= 0:
            return False
        
        # Ensure we have valid price data
        if self.data.close[0] <= 0:
            return False
        
        return True
    def _manage_enhanced_position(self):
        """Enhanced position management with trailing stops and partial profits"""
        
        if not self.position:
            return
        
        current_price = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # Check maximum holding period
        if self.entry_date:
            days_held = (current_date - self.entry_date).days
            if days_held >= self.params.max_holding_days:
                self.close()
                print(f"🕐 Position closed due to max holding period: {days_held} days")
                return
        
        position_size = self.position.size
        entry_price = self.entry_price
        
        if position_size > 0:  # Long position
            self._manage_long_position(current_price)
        else:  # Short position
            self._manage_short_position(current_price)
    
    def _manage_long_position(self, current_price: float):
        """Manage long position with enhanced logic"""
        
        entry_price = self.entry_price
        stop_price = self.stop_loss_price
        target_price = self.take_profit_price
        
        # Calculate current P&L
        unrealized_pnl = (current_price - entry_price) * abs(self.position.size)
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Stop loss check
        if current_price <= stop_price:
            self.close()
            print(f"🛑 Long position stopped out at {current_price:.2f} (Stop: {stop_price:.2f})")
            return
        
        # Take profit check
        if current_price >= target_price:
            self.close()
            print(f"🎯 Long position target reached at {current_price:.2f} (Target: {target_price:.2f})")
            return
        
        # Partial profit taking
        if (self.params.partial_profit_level > 0 and 
            pnl_pct >= (target_price - entry_price) / entry_price * self.params.partial_profit_level):
            
            # Take partial profit (reduce position size)
            partial_size = int(abs(self.position.size) * 0.5)
            if partial_size > 0:
                self.sell(size=partial_size)
                print(f"💰 Partial profit taken: {partial_size} shares at {current_price:.2f}")
                # Reset partial profit flag to avoid multiple partial exits
                self.params.partial_profit_level = 0
        
        # Trailing stop logic
        if self.params.enable_trailing_stop:
            atr_value = self.atr[0]
            trailing_stop = current_price - (atr_value * self.params.trailing_stop_atr_mult)
            
            # Update stop if trailing stop is higher
            if trailing_stop > self.stop_loss_price:
                self.stop_loss_price = trailing_stop
                print(f"📈 Trailing stop updated to {trailing_stop:.2f}")
        
        # Structure-based trailing stop
        if self.params.use_structure_stops:
            new_structure_stop = self._calculate_structure_stop('long')
            if new_structure_stop > self.stop_loss_price:
                self.stop_loss_price = new_structure_stop
                print(f"📊 Structure stop updated to {new_structure_stop:.2f}")
    
    def _manage_short_position(self, current_price: float):
        """Manage short position with enhanced logic"""
        
        entry_price = self.entry_price
        stop_price = self.stop_loss_price
        target_price = self.take_profit_price
        
        # Calculate current P&L
        unrealized_pnl = (entry_price - current_price) * abs(self.position.size)
        pnl_pct = (entry_price - current_price) / entry_price
        
        # Stop loss check
        if current_price >= stop_price:
            self.close()
            print(f"🛑 Short position stopped out at {current_price:.2f} (Stop: {stop_price:.2f})")
            return
        
        # Take profit check
        if current_price <= target_price:
            self.close()
            print(f"🎯 Short position target reached at {current_price:.2f} (Target: {target_price:.2f})")
            return
        
        # Partial profit taking
        if (self.params.partial_profit_level > 0 and 
            pnl_pct >= (entry_price - target_price) / entry_price * self.params.partial_profit_level):
            
            # Take partial profit (reduce position size)
            partial_size = int(abs(self.position.size) * 0.5)
            if partial_size > 0:
                self.buy(size=partial_size)  # Buy to cover for short
                print(f"💰 Partial profit taken: {partial_size} shares at {current_price:.2f}")
                # Reset partial profit flag to avoid multiple partial exits
                self.params.partial_profit_level = 0
        
        # Trailing stop logic
        if self.params.enable_trailing_stop:
            atr_value = self.atr[0]
            trailing_stop = current_price + (atr_value * self.params.trailing_stop_atr_mult)
            
            # Update stop if trailing stop is lower
            if trailing_stop < self.stop_loss_price:
                self.stop_loss_price = trailing_stop
                print(f"📉 Trailing stop updated to {trailing_stop:.2f}")
        
        # Structure-based trailing stop
        if self.params.use_structure_stops:
            new_structure_stop = self._calculate_structure_stop('short')
            if new_structure_stop < self.stop_loss_price:
                self.stop_loss_price = new_structure_stop
                print(f"📊 Structure stop updated to {new_structure_stop:.2f}")
    
    def _cleanup_old_data(self):
        """Clean up old breakouts and trade history"""
        
        current_date = self.data.datetime.date(0)
        
        # Remove old breakouts
        self.recent_breakouts = [
            breakout for breakout in self.recent_breakouts
            if (current_date - breakout['breakout_date']).days <= self.params.max_breakout_age
        ]
        
        # Remove old trade levels (keep last 10)
        if len(self.recent_trade_levels) > 10:
            self.recent_trade_levels = self.recent_trade_levels[-10:]
    
    def _update_performance_metrics(self):
        """Update enhanced performance tracking metrics"""
        
        if self.params.track_retest_success and self.retest_attempts > 0:
            self.breakout_success_rate = self.successful_retests / self.retest_attempts
    
    def notify_order(self, order):
        """Enhanced order notification with detailed logging"""
        
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status == order.Completed:
            if order.isbuy():
                action = "BUY" if not self.position else "COVER"
                print(f"✅ {action} EXECUTED: {order.executed.size} @ {order.executed.price:.2f}")
            else:
                action = "SELL" if self.position.size > 0 else "SHORT"
                print(f"✅ {action} EXECUTED: {order.executed.size} @ {order.executed.price:.2f}")
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"❌ ORDER FAILED: {order.getstatusname()}")
    
    def notify_trade(self, trade):
        """Enhanced trade notification with comprehensive metrics"""
        
        if not trade.isclosed:
            return
        
        self.total_trades += 1
        pnl = trade.pnl
        pnl_pct = (pnl / abs(trade.value)) * 100 if trade.value != 0 else 0
        
        if pnl > 0:
            self.winning_trades += 1
            result = "WIN"
            emoji = "🟢"
        else:
            self.losing_trades += 1
            result = "LOSS"
            emoji = "🔴"
        
        self.total_pnl += pnl
        
        # Calculate metrics
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        avg_pnl = self.total_pnl / self.total_trades if self.total_trades > 0 else 0
        
        print(f"{emoji} TRADE CLOSED ({result})")
        print(f"   💰 P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
        print(f"   📊 Duration: {trade.barlen} bars")
        print(f"   📈 Win Rate: {win_rate:.1f}% ({self.winning_trades}/{self.total_trades})")
        print(f"   💵 Avg P&L: ${avg_pnl:.2f}")
        print(f"   🎯 Total P&L: ${self.total_pnl:.2f}")
        
        if self.params.track_retest_success:
            print(f"   📊 Retest Success Rate: {self.breakout_success_rate:.1%} ({self.successful_retests}/{self.retest_attempts})")
    
    def stop(self):
        """Enhanced strategy completion summary"""
        
        final_value = self.broker.getvalue()
        
        print("\n" + "="*60)
        print("🎯 ENHANCED BREAK & RETEST STRATEGY COMPLETED")
        print("="*60)
        print(f"📊 Final Portfolio Value: ${final_value:.2f}")
        print(f"📈 Total Trades: {self.total_trades}")
        print(f"🟢 Winning Trades: {self.winning_trades}")
        print(f"🔴 Losing Trades: {self.losing_trades}")
        
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            avg_pnl = self.total_pnl / self.total_trades
            print(f"📊 Win Rate: {win_rate:.1f}%")
            print(f"💰 Average P&L per Trade: ${avg_pnl:.2f}")
            print(f"💵 Total P&L: ${self.total_pnl:.2f}")
        
        if self.params.track_retest_success and self.retest_attempts > 0:
            print(f"🎯 Retest Success Rate: {self.breakout_success_rate:.1%}")
            print(f"📊 Successful Retests: {self.successful_retests}/{self.retest_attempts}")
        
        print(f"\n🔧 Strategy Parameters:")
        print(f"   📏 Lookback Period: {self.params.lookback_period}")
        print(f"   💪 Min Breakout Strength: {self.params.min_breakout_strength:.1%}")
        print(f"   🎯 Position Size: {self.params.position_size_pct:.1%}")
        print(f"   🛑 Use Structure Stops: {self.params.use_structure_stops}")
        print(f"   📊 Use Adaptive TP: {self.params.use_adaptive_tp}")
        print(f"   🕐 Trade Cooldown: {self.params.trade_cooldown_days} days")
        print(f"   📈 Pattern Confirmation: {self.params.require_pattern_confirmation}")
        print(f"   📊 Momentum Confirmation: {self.params.require_momentum_confirmation}")
        print("="*60)
    
    # Utility methods for duplicate detection and level updates
    def _is_duplicate_breakout(self, new_breakout: Dict) -> bool:
        """Check if breakout is duplicate of recent breakout"""
        
        for existing in self.recent_breakouts:
            if (abs(new_breakout['level_price'] - existing['level_price']) / 
                existing['level_price'] < self.params.level_tolerance and
                new_breakout['direction'] == existing['direction']):
                return True
        return False
    
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
                    level['strength'] += swing.get('strength_score', 1)
                    # Update level price to weighted average
                    total_weight = sum(touch.get('strength_score', 1) for touch in level['touches'])
                    weighted_sum = sum(touch['price'] * touch.get('strength_score', 1) for touch in level['touches'])
                    level['price'] = weighted_sum / total_weight
                    level_found = True
                    break
            
            if not level_found:
                # Create new level
                new_level = {
                    'price': swing_price,
                    'type': level_type,
                    'touches': [swing],
                    'strength': swing.get('strength_score', 1),
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


# === Strategy Metadata ===
__strategy_name__ = "Enhanced Break & Retest Strategy"
__strategy_version__ = "2.0.0"
__strategy_description__ = "Advanced break and retest strategy with selective entry, adaptive exits, and comprehensive filtering"
__strategy_author__ = "SentimentTrade Development Team"
__strategy_risk_level__ = "Medium-High"
__strategy_market_type__ = "Trending and Volatile Markets"
__strategy_enhancements__ = [
    "Candlestick pattern confirmation",
    "Momentum-based entry filtering", 
    "Structure-based stops and targets",
    "Close-based breakout confirmation",
    "Trade clustering prevention",
    "Enhanced performance tracking"
]
