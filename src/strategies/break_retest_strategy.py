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
        
        # Enhanced Breakout Parameters - OPTIMIZATION 1: Parameter Tuning
        ('min_breakout_strength', 0.008), # Reduced from 1% to 0.8% for more opportunities
        ('breakout_volume_factor', 1.3), # Reduced from 1.5x to 1.3x for more flexibility
        ('max_breakout_age', 15),       # Increased from 10 to 15 days for more opportunities
        ('use_close_breakout', True),   # Use closing price for breakout confirmation
        
        # Enhanced Retest Parameters - OPTIMIZATION 1: Parameter Tuning
        ('retest_tolerance', 0.007),    # Increased from 0.5% to 0.7% for more flexibility
        ('min_retest_bounce', 0.002),   # Reduced from 0.3% to 0.2% for easier confirmation
        ('retest_confirmation_bars', 1), # Reduced from 2 to 1 for faster entries
        ('require_pattern_confirmation', True), # Keep pattern confirmation
        ('require_momentum_confirmation', True), # Keep momentum confirmation
        
        # Enhanced Risk Management - OPTIMIZATION 4: Risk Management Enhancement
        ('position_size_pct', 0.015),   # Reduced from 2% to 1.5% for better risk control
        ('use_structure_stops', True),  # Use swing-based stops instead of ATR
        ('stop_loss_atr_mult', 1.8),    # Reduced from 2.0 to 1.8 for tighter stops
        ('use_adaptive_tp', True),      # Use adaptive take profit based on structure
        ('take_profit_ratio', 2.5),     # Reduced from 3.0 to 2.5 for more realistic targets
        ('max_holding_days', 25),       # Reduced from 30 to 25 days
        
        # Trade Management Enhancements - OPTIMIZATION 4: Risk Management Enhancement
        ('enable_trailing_stop', True), # Enable trailing stop loss
        ('trailing_stop_atr_mult', 1.3), # Reduced from 1.5 to 1.3 for tighter trailing
        ('partial_profit_level', 0.6),  # Increased from 0.5 to 0.6 for earlier profit taking
        ('trade_cooldown_days', 2),     # Reduced from 3 to 2 days for more opportunities
        
        # Confirmation Indicators - OPTIMIZATION 1: Parameter Tuning
        ('rsi_period', 9),              # Increased from 7 to 9 for smoother signals
        ('rsi_momentum_threshold', 1.5), # Reduced from 2 to 1.5 for easier confirmation
        ('pattern_lookback', 2),        # Reduced from 3 to 2 for faster pattern recognition
        
        # Filters - OPTIMIZATION 2: Market Regime Adaptation
        ('min_atr_pct', 0.008),         # Reduced from 1% to 0.8% for lower volatility markets
        ('trend_filter_period', 50),    # Keep 50-day MA for trend filter
        ('enable_trend_filter', True),  # Only trade in direction of trend
        ('max_concurrent_trades', 2),   # Increased from 1 to 2 for more opportunities
        
        # Performance Tracking
        ('track_retest_success', True), # Track retest success rates
        ('min_trade_spacing', 0.015),   # Reduced from 2% to 1.5% for closer trades
        
        # OPTIMIZATION 2: Market Regime Adaptation - New Parameters
        ('enable_regime_detection', True), # Enable market regime detection
        ('regime_lookback', 100),       # Period for regime analysis
        ('trending_threshold', 0.7),    # Threshold for trending vs ranging market
        ('volatility_regime_period', 20), # Period for volatility regime detection
        ('adaptive_confirmation', True), # Adapt confirmation requirements to market regime
        
        # OPTIMIZATION 4: Risk Management Enhancement - New Parameters
        ('enable_volatility_sizing', True), # Enable volatility-based position sizing
        ('max_portfolio_risk', 0.06),   # Maximum 6% portfolio risk across all positions
        ('correlation_limit', 0.7),     # Maximum correlation between positions
        ('drawdown_protection', True),  # Enable drawdown protection
        ('max_consecutive_losses', 3),  # Maximum consecutive losses before reducing size
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
        
        # Enhancement 3: Add cooldown timer between trades
        self.last_trade_bar = None
        self.trade_cooldown_bars = 10  # cooldown period (adjustable)
        
        # OPTIMIZATION 2: Market Regime Detection
        self.market_regime = 'neutral'  # 'trending', 'ranging', 'volatile'
        self.trend_strength = 0.0       # Current trend strength
        self.volatility_regime = 'normal' # 'low', 'normal', 'high'
        self.regime_history = []        # Historical regime data
        
        # OPTIMIZATION 4: Enhanced Risk Management
        self.portfolio_risk = 0.0       # Current portfolio risk
        self.position_correlations = {} # Track position correlations
        self.consecutive_losses = 0     # Track consecutive losses
        self.drawdown_protection_active = False # Drawdown protection status
        self.volatility_multiplier = 1.0 # Volatility-based sizing multiplier
        
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
        
        # OPTIMIZATION 2: Update market regime detection
        if self.params.enable_regime_detection:
            self._update_market_regime()
        
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
    
    def _update_market_regime(self):
        """OPTIMIZATION 2: Detect and adapt to market regime"""
        
        if len(self.data) < self.params.regime_lookback:
            return
        
        # Calculate trend strength using linear regression
        prices = [self.data.close[-i] for i in range(self.params.regime_lookback)]
        x = np.arange(len(prices))
        
        # Linear regression to determine trend
        slope, intercept = np.polyfit(x, prices, 1)
        r_squared = np.corrcoef(x, prices)[0, 1] ** 2
        
        # Normalize slope by price for percentage trend
        trend_strength = (slope * len(prices)) / prices[0]
        self.trend_strength = abs(trend_strength)
        
        # Determine market regime
        if r_squared > self.params.trending_threshold:
            self.market_regime = 'trending'
        else:
            self.market_regime = 'ranging'
        
        # Volatility regime detection
        recent_returns = []
        for i in range(1, self.params.volatility_regime_period + 1):
            if len(self.data) > i:
                ret = (self.data.close[-i] - self.data.close[-i-1]) / self.data.close[-i-1]
                recent_returns.append(abs(ret))
        
        if recent_returns:
            avg_volatility = np.mean(recent_returns)
            if avg_volatility > 0.02:  # 2% average daily moves
                self.volatility_regime = 'high'
            elif avg_volatility < 0.01:  # 1% average daily moves
                self.volatility_regime = 'low'
            else:
                self.volatility_regime = 'normal'
        
        # Store regime history
        regime_data = {
            'date': self.data.datetime.date(0),
            'regime': self.market_regime,
            'trend_strength': self.trend_strength,
            'volatility': self.volatility_regime,
            'r_squared': r_squared
        }
        self.regime_history.append(regime_data)
        
        # Keep only recent history
        if len(self.regime_history) > 100:
            self.regime_history = self.regime_history[-100:]
        
        # Update volatility multiplier for position sizing
        if self.volatility_regime == 'high':
            self.volatility_multiplier = 0.7  # Reduce size in high volatility
        elif self.volatility_regime == 'low':
            self.volatility_multiplier = 1.2  # Increase size in low volatility
        else:
            self.volatility_multiplier = 1.0  # Normal sizing
    
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
        
        # Enhancement 1: Add close price confirmation
        last_close = self.data.close[0]
        current_high = self.data.high[0]
        current_low = self.data.low[0]
        current_volume = self.data.volume[0]
        avg_volume = self.volume_sma[0]
        
        # Check resistance breakouts (bullish) - Enhanced with close confirmation
        for resistance in self.resistance_levels:
            if (current_high > resistance['price'] * (1 + self.params.min_breakout_strength) and
                last_close > resistance['price'] * (1 + self.params.min_breakout_strength) and
                current_volume > avg_volume * self.params.breakout_volume_factor):
                
                # Additional confirmation: ensure it's not a false breakout
                if self._confirm_breakout_strength(resistance['price'], 'bullish'):
                    breakout = {
                        'type': 'resistance_break',
                        'level_price': resistance['price'],
                        'breakout_price': last_close,
                        'breakout_date': self.data.datetime.date(0),
                        'volume_confirmation': True,
                        'direction': 'bullish',
                        'level_strength': resistance['strength'],
                        'close_based': True,
                        'strength_score': self._calculate_breakout_strength(resistance, 'bullish')
                    }
                    
                    # Check if we already have this breakout
                    if not self._is_duplicate_breakout(breakout):
                        self.recent_breakouts.append(breakout)
                        print(f"📈 Enhanced Resistance Breakout: {resistance['price']:.2f} -> {last_close:.2f} (Close-confirmed)")
        
        # Check support breakouts (bearish) - Enhanced with close confirmation
        for support in self.support_levels:
            if (current_low < support['price'] * (1 - self.params.min_breakout_strength) and
                last_close < support['price'] * (1 - self.params.min_breakout_strength) and
                current_volume > avg_volume * self.params.breakout_volume_factor):
                
                # Additional confirmation: ensure it's not a false breakdown
                if self._confirm_breakout_strength(support['price'], 'bearish'):
                    breakout = {
                        'type': 'support_break',
                        'level_price': support['price'],
                        'breakout_price': last_close,
                        'breakout_date': self.data.datetime.date(0),
                        'volume_confirmation': True,
                        'direction': 'bearish',
                        'level_strength': support['strength'],
                        'close_based': True,
                        'strength_score': self._calculate_breakout_strength(support, 'bearish')
                    }
                    
                    # Check if we already have this breakout
                    if not self._is_duplicate_breakout(breakout):
                        self.recent_breakouts.append(breakout)
                        print(f"📉 Enhanced Support Breakout: {support['price']:.2f} -> {last_close:.2f} (Close-confirmed)")
    
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
        
        # Enhancement 2: Add candle body confirmation
        bullish_body = self.data.close[0] > self.data.open[0]
        current_price = self.data.close[0]
        level_price = breakout['level_price']
        min_bounce = self.params.min_retest_bounce
        
        # Enhanced bounce confirmation with candle body structure
        basic_bounce = False
        if direction == 'bullish':
            basic_bounce = bullish_body and current_price > level_price * (1 + min_bounce)
        else:
            basic_bounce = not bullish_body and current_price < level_price * (1 - min_bounce)
        
        if not basic_bounce:
            return False
        
        # OPTIMIZATION 2: Adaptive confirmation based on market regime
        required_confirmations = self._get_required_confirmations()
        
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
        
        # OPTIMIZATION 2: Regime-adaptive confirmation requirements
        confirmed_count = sum(confirmations)
        success_rate = confirmed_count / len(confirmations) if confirmations else 0
        
        return success_rate >= required_confirmations
    
    def _get_required_confirmations(self) -> float:
        """OPTIMIZATION 2: Get required confirmation threshold based on market regime"""
        
        if not self.params.adaptive_confirmation:
            return 0.67  # Default 67% requirement
        
        # Adapt based on market regime
        if self.market_regime == 'trending':
            # In trending markets, be less strict to catch more moves
            if self.trend_strength > 0.05:  # Strong trend
                return 0.5   # 50% confirmations needed
            else:
                return 0.6   # 60% confirmations needed
        
        elif self.market_regime == 'ranging':
            # In ranging markets, be more strict for quality
            return 0.75  # 75% confirmations needed
        
        else:
            return 0.67  # Default for neutral/unknown regime
    
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
        
        # Enhancement 3: Check bar-based cooldown
        if self.last_trade_bar is None:
            return False
        return len(self.data) - self.last_trade_bar < self.trade_cooldown_bars
        
        # Original date-based cooldown (keep as backup)
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
        
        # Enhancement 3: Add cooldown check
        if self._is_in_cooldown():
            print("🕐 Cooldown active, skipping trade.")
            return False
        
        # Enhancement 5: Prevent duplicate trade setups on same level
        if self.breakout_level in [b['level_price'] for b in self.recent_breakouts]:
            print("⚠️ Already traded this breakout level recently.")
            return False
        
        if not self._apply_enhanced_filters('long'):
            return False
        
        current_price = self.data.close[0]
        
        # Check if too close to recent trades
        if self._is_near_recent_trade(current_price):
            print(f"   ⚠️ Skipping trade - too close to recent trade level")
            return False
        
        # Enhancement 4: Smarter stop loss using swing low/high if closer than ATR
        atr_value = self.atr[0]
        stop_distance = atr_value * self.params.stop_loss_atr_mult
        
        # Check for nearby swing lows for better stop placement
        swing_lows_nearby = [low['price'] for low in self.swing_lows if abs(current_price - low['price']) < 2 * stop_distance]
        if swing_lows_nearby:
            structure_stop = max(swing_lows_nearby)
            self.stop_loss_price = min(current_price - stop_distance, structure_stop)
        else:
            self.stop_loss_price = current_price - stop_distance
        
        # Calculate structure-based take profit
        structure_target = self._calculate_structure_target('long', current_price, self.stop_loss_price)
        
        # OPTIMIZATION 4: Use enhanced position sizing
        position_size = self._calculate_optimized_position_size(current_price, self.stop_loss_price, 'long')
        
        if position_size <= 0:
            print(f"   ⚠️ Invalid position size: {position_size}")
            return False
        
        # Execute the trade
        order = self.buy(size=position_size)
        
        if order:
            # Enhancement 3: Update cooldown tracking
            self.last_trade_bar = len(self.data)
            
            # Set trade tracking variables
            self.entry_price = current_price
            self.take_profit_price = structure_target
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'long'
            self.breakout_level = breakout['level_price']
            self.structure_stop = self.stop_loss_price
            self.structure_target = structure_target
            
            # Add to recent trade levels
            self.recent_trade_levels.append(current_price)
            self.last_trade_date = self.data.datetime.date(0)
            
            # Calculate risk-reward ratio
            risk = current_price - self.stop_loss_price
            reward = structure_target - current_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            # OPTIMIZATION 2: Log market regime context
            regime_info = f"Regime: {self.market_regime}, Volatility: {self.volatility_regime}, Trend: {self.trend_strength:.3f}"
            
            print(f"🟢 LONG ENTRY: Price: {current_price:.2f}")
            print(f"   📍 Smart Stop: {self.stop_loss_price:.2f} (Risk: {risk:.2f})")
            print(f"   🎯 Structure Target: {structure_target:.2f} (Reward: {reward:.2f})")
            print(f"   📊 R:R Ratio: 1:{rr_ratio:.2f}")
            print(f"   📦 Position Size: {position_size} shares")
            print(f"   🌍 Market Context: {regime_info}")
            
            return True
        
        return False
        
    def _calculate_optimized_position_size(self, entry_price: float, stop_price: float, direction: str) -> int:
        """OPTIMIZATION 4: Enhanced position sizing with volatility and risk management"""
        
        # Base risk amount
        base_risk = self.broker.getvalue() * self.params.position_size_pct
        
        # OPTIMIZATION 4: Apply volatility-based sizing
        if self.params.enable_volatility_sizing:
            base_risk *= self.volatility_multiplier
        
        # OPTIMIZATION 4: Reduce size after consecutive losses
        if self.params.drawdown_protection and self.consecutive_losses >= self.params.max_consecutive_losses:
            consecutive_loss_multiplier = max(0.5, 1.0 - (self.consecutive_losses - self.params.max_consecutive_losses) * 0.1)
            base_risk *= consecutive_loss_multiplier
            print(f"   📉 Reducing position size due to {self.consecutive_losses} consecutive losses (multiplier: {consecutive_loss_multiplier:.2f})")
        
        # Calculate actual stop distance
        actual_stop_distance = abs(entry_price - stop_price)
        
        if actual_stop_distance <= 0:
            return 0
        
        # Calculate base position size
        position_size = int(base_risk / actual_stop_distance)
        
        # OPTIMIZATION 4: Portfolio risk management
        if self.params.enable_volatility_sizing:
            # Check total portfolio risk
            current_portfolio_risk = self._calculate_current_portfolio_risk()
            additional_risk = (position_size * actual_stop_distance) / self.broker.getvalue()
            
            if current_portfolio_risk + additional_risk > self.params.max_portfolio_risk:
                # Reduce position size to stay within portfolio risk limit
                max_additional_risk = self.params.max_portfolio_risk - current_portfolio_risk
                if max_additional_risk > 0:
                    position_size = int((max_additional_risk * self.broker.getvalue()) / actual_stop_distance)
                    print(f"   📊 Position size reduced for portfolio risk management: {position_size}")
                else:
                    print(f"   ⚠️ Portfolio risk limit reached, skipping trade")
                    return 0
        
        return max(position_size, 1)  # Minimum 1 share
    
    def _calculate_current_portfolio_risk(self) -> float:
        """Calculate current portfolio risk from open positions"""
        
        if not self.position:
            return 0.0
        
        # For simplicity, estimate risk as current position value * stop distance percentage
        current_price = self.data.close[0]
        position_value = abs(self.position.size) * current_price
        
        if self.stop_loss_price > 0:
            stop_distance_pct = abs(current_price - self.stop_loss_price) / current_price
            position_risk = (position_value * stop_distance_pct) / self.broker.getvalue()
            return position_risk
        
        return 0.0
        
        if position_size <= 0:
            print(f"   ⚠️ Invalid position size: {position_size}")
            return False
        
        # Execute the trade
        order = self.buy(size=position_size)
        
        if order:
            # Enhancement 3: Update cooldown tracking
            self.last_trade_bar = len(self.data)
            
            # Set trade tracking variables
            self.entry_price = current_price
            self.take_profit_price = structure_target
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'long'
            self.breakout_level = breakout['level_price']
            self.structure_stop = self.stop_loss_price
            self.structure_target = structure_target
            
            # Add to recent trade levels
            self.recent_trade_levels.append(current_price)
            self.last_trade_date = self.data.datetime.date(0)
            
            # Calculate risk-reward ratio
            risk = current_price - self.stop_loss_price
            reward = structure_target - current_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            print(f"🟢 LONG ENTRY: Price: {current_price:.2f}")
            print(f"   📍 Smart Stop: {self.stop_loss_price:.2f} (Risk: {risk:.2f})")
            print(f"   🎯 Structure Target: {structure_target:.2f} (Reward: {reward:.2f})")
            print(f"   📊 R:R Ratio: 1:{rr_ratio:.2f}")
            print(f"   📦 Position Size: {position_size} shares")
            print(f"   💰 Risk Amount: ${risk_amount:.2f}")
            
            return True
        
        return False
    
    def _enter_enhanced_short_trade(self, breakout: Dict) -> bool:
        """Enter enhanced short position with structure-based stops and adaptive targets"""
        
        # Enhancement 3: Add cooldown check
        if self._is_in_cooldown():
            print("🕐 Cooldown active, skipping trade.")
            return False
        
        # Enhancement 5: Prevent duplicate trade setups on same level
        if self.breakout_level in [b['level_price'] for b in self.recent_breakouts]:
            print("⚠️ Already traded this breakout level recently.")
            return False
        
        if not self._apply_enhanced_filters('short'):
            return False
        
        current_price = self.data.close[0]
        
        # Check if too close to recent trades
        if self._is_near_recent_trade(current_price):
            print(f"   ⚠️ Skipping trade - too close to recent trade level")
            return False
        
        # Enhancement 4: Smarter stop loss using swing high if closer than ATR
        atr_value = self.atr[0]
        stop_distance = atr_value * self.params.stop_loss_atr_mult
        
        # Check for nearby swing highs for better stop placement
        swing_highs_nearby = [high['price'] for high in self.swing_highs if abs(current_price - high['price']) < 2 * stop_distance]
        if swing_highs_nearby:
            structure_stop = min(swing_highs_nearby)
            self.stop_loss_price = max(current_price + stop_distance, structure_stop)
        else:
            self.stop_loss_price = current_price + stop_distance
        
        # Calculate structure-based take profit
        structure_target = self._calculate_structure_target('short', current_price, self.stop_loss_price)
        
        # Calculate position size based on actual risk
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        actual_stop_distance = self.stop_loss_price - current_price
        
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
            # Enhancement 3: Update cooldown tracking
            self.last_trade_bar = len(self.data)
            
            # Set trade tracking variables
            self.entry_price = current_price
            self.take_profit_price = structure_target
            self.entry_date = self.data.datetime.date(0)
            self.trade_direction = 'short'
            self.breakout_level = breakout['level_price']
            self.structure_stop = self.stop_loss_price
            self.structure_target = structure_target
            
            # Add to recent trade levels
            self.recent_trade_levels.append(current_price)
            self.last_trade_date = self.data.datetime.date(0)
            
            # Calculate risk-reward ratio
            risk = self.stop_loss_price - current_price
            reward = current_price - structure_target
            rr_ratio = reward / risk if risk > 0 else 0
            
            print(f"🔴 SHORT ENTRY: Price: {current_price:.2f}")
            print(f"   📍 Smart Stop: {self.stop_loss_price:.2f} (Risk: {risk:.2f})")
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
            # OPTIMIZATION 4: Reset consecutive losses on win
            self.consecutive_losses = 0
        else:
            self.losing_trades += 1
            result = "LOSS"
            emoji = "🔴"
            # OPTIMIZATION 4: Track consecutive losses
            self.consecutive_losses += 1
        
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
        
        # OPTIMIZATION 4: Log consecutive losses for risk management
        if self.consecutive_losses > 0:
            print(f"   📉 Consecutive Losses: {self.consecutive_losses}")
        
        if self.params.track_retest_success:
            print(f"   📊 Retest Success Rate: {self.breakout_success_rate:.1%} ({self.successful_retests}/{self.retest_attempts})")
        
        # OPTIMIZATION 2: Log market regime context
        if hasattr(self, 'market_regime'):
            print(f"   🌍 Market Regime: {self.market_regime} (Volatility: {self.volatility_regime})")
    
    def stop(self):
        """Enhanced strategy completion summary"""
        
        final_value = self.broker.getvalue()
        
        print("\n" + "="*60)
        print("🎯 OPTIMIZED BREAK & RETEST STRATEGY COMPLETED")
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
        
        # OPTIMIZATION 2: Market Regime Summary
        if hasattr(self, 'regime_history') and self.regime_history:
            trending_periods = len([r for r in self.regime_history if r['regime'] == 'trending'])
            ranging_periods = len([r for r in self.regime_history if r['regime'] == 'ranging'])
            high_vol_periods = len([r for r in self.regime_history if r['volatility'] == 'high'])
            
            print(f"\n🌍 Market Regime Analysis:")
            print(f"   Trending Periods: {trending_periods}/{len(self.regime_history)} ({trending_periods/len(self.regime_history)*100:.1f}%)")
            print(f"   Ranging Periods: {ranging_periods}/{len(self.regime_history)} ({ranging_periods/len(self.regime_history)*100:.1f}%)")
            print(f"   High Volatility Periods: {high_vol_periods}/{len(self.regime_history)} ({high_vol_periods/len(self.regime_history)*100:.1f}%)")
            print(f"   Final Regime: {self.market_regime} (Trend Strength: {self.trend_strength:.3f})")
        
        # OPTIMIZATION 4: Risk Management Summary
        print(f"\n📊 Risk Management Summary:")
        print(f"   Max Consecutive Losses: {self.consecutive_losses}")
        print(f"   Volatility Multiplier: {self.volatility_multiplier:.2f}")
        if hasattr(self, 'drawdown_protection_active'):
            print(f"   Drawdown Protection: {'Active' if self.drawdown_protection_active else 'Inactive'}")
        
        print(f"\n🔧 Optimized Strategy Parameters:")
        print(f"   📏 Lookback Period: {self.params.lookback_period}")
        print(f"   💪 Min Breakout Strength: {self.params.min_breakout_strength:.1%}")
        print(f"   🎯 Position Size: {self.params.position_size_pct:.1%}")
        print(f"   🛑 Use Structure Stops: {self.params.use_structure_stops}")
        print(f"   📊 Use Adaptive TP: {self.params.use_adaptive_tp}")
        print(f"   🕐 Trade Cooldown: {self.params.trade_cooldown_days} days")
        print(f"   📈 Pattern Confirmation: {self.params.require_pattern_confirmation}")
        print(f"   📊 Momentum Confirmation: {self.params.require_momentum_confirmation}")
        
        # OPTIMIZATION FEATURES
        print(f"\n🚀 OPTIMIZATION FEATURES ACTIVE:")
        print(f"   ✅ OPTIMIZATION 1: Parameter Tuning")
        print(f"      - Reduced breakout strength: {self.params.min_breakout_strength:.1%}")
        print(f"      - Flexible retest tolerance: {self.params.retest_tolerance:.1%}")
        print(f"      - Faster confirmation: {self.params.retest_confirmation_bars} bar(s)")
        print(f"   ✅ OPTIMIZATION 2: Market Regime Adaptation")
        print(f"      - Regime Detection: {self.params.enable_regime_detection}")
        print(f"      - Adaptive Confirmation: {self.params.adaptive_confirmation}")
        print(f"      - Current Regime: {getattr(self, 'market_regime', 'Unknown')}")
        print(f"   ✅ OPTIMIZATION 4: Enhanced Risk Management")
        print(f"      - Volatility Sizing: {self.params.enable_volatility_sizing}")
        print(f"      - Max Portfolio Risk: {self.params.max_portfolio_risk:.1%}")
        print(f"      - Drawdown Protection: {self.params.drawdown_protection}")
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
