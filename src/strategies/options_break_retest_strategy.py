#!/usr/bin/env python3
"""
Options Break and Retest Strategy
Enhanced Break and Retest strategy that trades ITM options instead of stocks
"""

import backtrader as bt
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import the base strategy
from .break_retest_strategy import BreakRetestSwingStrategy

class OptionsBreakRetestStrategy(BreakRetestSwingStrategy):
    """
    Options-based Break and Retest Strategy
    
    This strategy extends the optimized Break and Retest strategy to trade
    in-the-money (ITM) options instead of stocks directly.
    
    Key Features:
    1. Uses same break and retest logic for entry/exit signals
    2. Buys ITM call options on bullish signals
    3. Buys ITM put options on bearish signals
    4. Enhanced position sizing based on option Greeks
    5. Time decay management for options
    6. Volatility-based option selection
    """
    
    params = (
        # Inherit all base strategy parameters
        
        # Options-specific parameters
        ('options_data_file', ''),          # Path to options chain data
        ('min_days_to_expiry', 30),         # Minimum days to expiration
        ('max_days_to_expiry', 90),         # Maximum days to expiration
        ('target_delta_range', (0.6, 0.8)), # Target delta range for ITM options
        ('min_option_price', 1.0),          # Minimum option price ($1.00)
        ('max_option_price', 50.0),         # Maximum option price ($50.00)
        ('min_volume', 10),                 # Minimum daily volume
        ('min_open_interest', 50),          # Minimum open interest
        
        # Options risk management
        ('max_theta_decay', -0.05),         # Maximum theta (time decay) per day
        ('volatility_adjustment', True),    # Adjust position size for volatility
        ('early_exit_theta', -0.10),       # Exit if theta becomes too negative
        ('profit_target_pct', 0.50),       # Take profit at 50%
        ('stop_loss_pct', 0.30),           # Stop loss at 30%
        
        # Options selection criteria
        ('prefer_higher_volume', True),     # Prefer options with higher volume
        ('prefer_tighter_spreads', True),   # Prefer options with tighter bid-ask spreads
        ('max_bid_ask_spread_pct', 0.10),  # Maximum 10% bid-ask spread
    )
    
    def __init__(self):
        """Initialize the Options Break and Retest strategy"""
        
        # Initialize base strategy
        super().__init__()
        
        # Options-specific state
        self.options_data = None
        self.current_options_positions = []
        self.options_universe = {}
        
        # Load options data
        self._load_options_data()
        
        print("🎯 Options Break and Retest Strategy Initialized")
        print(f"   Base Strategy: Enhanced Break and Retest")
        print(f"   Options Mode: ITM Calls/Puts")
        print(f"   Target Delta Range: {self.params.target_delta_range}")
        print(f"   Days to Expiry: {self.params.min_days_to_expiry}-{self.params.max_days_to_expiry}")
    
    def _load_options_data(self):
        """Load options chain data for backtesting"""
        
        if not self.params.options_data_file:
            print("⚠️ No options data file specified - using simulated options")
            return
        
        try:
            self.options_data = pd.read_csv(self.params.options_data_file)
            
            # Convert date columns
            self.options_data['expirationDate'] = pd.to_datetime(self.options_data['expirationDate'])
            if 'downloadDate' in self.options_data.columns:
                self.options_data['downloadDate'] = pd.to_datetime(self.options_data['downloadDate'])
            
            # Create options universe by symbol
            for symbol in self.options_data['symbol'].unique():
                symbol_options = self.options_data[self.options_data['symbol'] == symbol]
                self.options_universe[symbol] = symbol_options
            
            print(f"✅ Loaded options data: {len(self.options_data)} options across {len(self.options_universe)} symbols")
            
        except Exception as e:
            print(f"⚠️ Error loading options data: {e}")
            print("   Using simulated options pricing")
    
    def _find_suitable_option(self, direction: str, underlying_price: float, 
                            current_date: datetime, symbol: str = None) -> Dict:
        """Find suitable ITM option for the trade direction"""
        
        if symbol is None:
            symbol = 'UNKNOWN'  # Will use simulated pricing
        
        # If we have real options data, use it
        if symbol in self.options_universe:
            return self._find_real_option(direction, underlying_price, current_date, symbol)
        else:
            return self._simulate_option(direction, underlying_price, current_date, symbol)
    
    def _find_real_option(self, direction: str, underlying_price: float, 
                         current_date: datetime, symbol: str) -> Dict:
        """Find real option from loaded options data"""
        
        symbol_options = self.options_universe[symbol]
        
        # Filter options based on criteria
        option_type = 'call' if direction == 'bullish' else 'put'
        
        filtered_options = symbol_options[
            (symbol_options['optionType'] == option_type) &
            (symbol_options['daysToExpiry'] >= self.params.min_days_to_expiry) &
            (symbol_options['daysToExpiry'] <= self.params.max_days_to_expiry) &
            (symbol_options['lastPrice'] >= self.params.min_option_price) &
            (symbol_options['lastPrice'] <= self.params.max_option_price) &
            (symbol_options['volume'].fillna(0) >= self.params.min_volume) &
            (symbol_options['openInterest'].fillna(0) >= self.params.min_open_interest)
        ].copy()
        
        if filtered_options.empty:
            print(f"⚠️ No suitable {option_type} options found for {symbol}")
            return self._simulate_option(direction, underlying_price, current_date, symbol)
        
        # Filter by delta range for ITM options
        if 'delta' in filtered_options.columns:
            target_min, target_max = self.params.target_delta_range
            
            if direction == 'bullish':
                # For calls, delta should be positive and in range
                filtered_options = filtered_options[
                    (filtered_options['delta'] >= target_min) &
                    (filtered_options['delta'] <= target_max)
                ]
            else:
                # For puts, delta should be negative, so we check absolute value
                filtered_options = filtered_options[
                    (abs(filtered_options['delta']) >= target_min) &
                    (abs(filtered_options['delta']) <= target_max)
                ]
        
        if filtered_options.empty:
            print(f"⚠️ No options in target delta range for {symbol}")
            return self._simulate_option(direction, underlying_price, current_date, symbol)
        
        # Select best option based on criteria
        if self.params.prefer_higher_volume:
            best_option = filtered_options.loc[filtered_options['volume'].idxmax()]
        else:
            # Select option closest to middle of delta range
            target_delta = sum(self.params.target_delta_range) / 2
            if direction == 'bearish':
                target_delta = -target_delta
            
            filtered_options['delta_diff'] = abs(filtered_options['delta'] - target_delta)
            best_option = filtered_options.loc[filtered_options['delta_diff'].idxmin()]
        
        return {
            'type': option_type,
            'strike': best_option['strike'],
            'expiry': best_option['expirationDate'],
            'price': best_option['lastPrice'],
            'delta': best_option.get('delta', 0.7 if direction == 'bullish' else -0.7),
            'theta': best_option.get('theta', -0.02),
            'gamma': best_option.get('gamma', 0.05),
            'vega': best_option.get('vega', 0.1),
            'volume': best_option.get('volume', 100),
            'openInterest': best_option.get('openInterest', 500),
            'bid': best_option.get('bid', best_option['lastPrice'] * 0.98),
            'ask': best_option.get('ask', best_option['lastPrice'] * 1.02),
            'days_to_expiry': best_option['daysToExpiry'],
            'data_source': 'real'
        }
    
    def _simulate_option(self, direction: str, underlying_price: float, 
                        current_date: datetime, symbol: str) -> Dict:
        """Simulate option pricing using Black-Scholes approximation"""
        
        option_type = 'call' if direction == 'bullish' else 'put'
        
        # Target delta for ITM options
        target_delta = 0.7 if direction == 'bullish' else -0.7
        
        # Estimate strike price for target delta
        # For ITM calls: strike < underlying, for ITM puts: strike > underlying
        if direction == 'bullish':
            strike = underlying_price * 0.95  # 5% ITM call
        else:
            strike = underlying_price * 1.05  # 5% ITM put
        
        # Round strike to nearest $5 or $10
        if underlying_price > 100:
            strike = round(strike / 5) * 5
        else:
            strike = round(strike)
        
        # Estimate days to expiry (middle of range)
        days_to_expiry = (self.params.min_days_to_expiry + self.params.max_days_to_expiry) // 2
        
        # Simplified option pricing
        intrinsic_value = max(underlying_price - strike, 0) if direction == 'bullish' else max(strike - underlying_price, 0)
        time_value = underlying_price * 0.02 * (days_to_expiry / 30)  # Rough time value
        option_price = intrinsic_value + time_value
        
        # Ensure minimum price
        option_price = max(option_price, self.params.min_option_price)
        
        return {
            'type': option_type,
            'strike': strike,
            'expiry': current_date + timedelta(days=days_to_expiry),
            'price': option_price,
            'delta': target_delta,
            'theta': -0.02,  # Estimated theta
            'gamma': 0.05,   # Estimated gamma
            'vega': 0.1,     # Estimated vega
            'volume': 100,   # Simulated volume
            'openInterest': 500,  # Simulated OI
            'bid': option_price * 0.98,
            'ask': option_price * 1.02,
            'days_to_expiry': days_to_expiry,
            'data_source': 'simulated'
        }
    
    def _calculate_option_position_size(self, option_info: Dict, risk_amount: float) -> int:
        """Calculate position size for options trade"""
        
        option_price = option_info['price']
        
        # Basic position sizing
        contracts = int(risk_amount / (option_price * 100))  # 100 shares per contract
        
        # Adjust for volatility if enabled
        if self.params.volatility_adjustment:
            # Higher vega = more volatile = smaller position
            vega_adjustment = max(0.5, 1.0 - (abs(option_info.get('vega', 0.1)) * 2))
            contracts = int(contracts * vega_adjustment)
        
        # Ensure minimum 1 contract
        contracts = max(1, contracts)
        
        return contracts
    
    def _enter_options_long_trade(self, breakout: Dict) -> bool:
        """Enter long options position (buy call)"""
        
        current_price = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # Find suitable call option
        option_info = self._find_suitable_option('bullish', current_price, current_date)
        
        # Calculate position size
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        contracts = self._calculate_option_position_size(option_info, risk_amount)
        
        # Calculate total cost
        total_cost = contracts * option_info['price'] * 100
        
        if total_cost > self.broker.getcash():
            print(f"⚠️ Insufficient cash for options trade: ${total_cost:.2f} needed")
            return False
        
        # Simulate buying the option (we'll track this manually)
        option_position = {
            'direction': 'long_call',
            'contracts': contracts,
            'entry_price': option_info['price'],
            'entry_date': current_date,
            'underlying_entry_price': current_price,
            'option_info': option_info,
            'total_cost': total_cost,
            'breakout_level': breakout['level_price'],
            'profit_target': option_info['price'] * (1 + self.params.profit_target_pct),
            'stop_loss': option_info['price'] * (1 - self.params.stop_loss_pct)
        }
        
        self.current_options_positions.append(option_position)
        
        # Reduce cash (simulate purchase)
        # Note: In real backtrader, we'd create a custom order type
        
        print(f"🟢 CALL OPTION ENTRY:")
        print(f"   📊 Option: {option_info['type'].upper()} ${option_info['strike']} exp {option_info['expiry'].strftime('%Y-%m-%d')}")
        print(f"   💰 Price: ${option_info['price']:.2f} x {contracts} contracts")
        print(f"   📈 Delta: {option_info['delta']:.3f}, Theta: {option_info['theta']:.3f}")
        print(f"   💵 Total Cost: ${total_cost:.2f}")
        print(f"   🎯 Profit Target: ${option_position['profit_target']:.2f}")
        print(f"   🛑 Stop Loss: ${option_position['stop_loss']:.2f}")
        
        return True
    
    def _enter_options_short_trade(self, breakout: Dict) -> bool:
        """Enter short options position (buy put)"""
        
        current_price = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # Find suitable put option
        option_info = self._find_suitable_option('bearish', current_price, current_date)
        
        # Calculate position size
        risk_amount = self.broker.getvalue() * self.params.position_size_pct
        contracts = self._calculate_option_position_size(option_info, risk_amount)
        
        # Calculate total cost
        total_cost = contracts * option_info['price'] * 100
        
        if total_cost > self.broker.getcash():
            print(f"⚠️ Insufficient cash for options trade: ${total_cost:.2f} needed")
            return False
        
        # Simulate buying the option
        option_position = {
            'direction': 'long_put',
            'contracts': contracts,
            'entry_price': option_info['price'],
            'entry_date': current_date,
            'underlying_entry_price': current_price,
            'option_info': option_info,
            'total_cost': total_cost,
            'breakout_level': breakout['level_price'],
            'profit_target': option_info['price'] * (1 + self.params.profit_target_pct),
            'stop_loss': option_info['price'] * (1 - self.params.stop_loss_pct)
        }
        
        self.current_options_positions.append(option_position)
        
        print(f"🔴 PUT OPTION ENTRY:")
        print(f"   📊 Option: {option_info['type'].upper()} ${option_info['strike']} exp {option_info['expiry'].strftime('%Y-%m-%d')}")
        print(f"   💰 Price: ${option_info['price']:.2f} x {contracts} contracts")
        print(f"   📈 Delta: {option_info['delta']:.3f}, Theta: {option_info['theta']:.3f}")
        print(f"   💵 Total Cost: ${total_cost:.2f}")
        print(f"   🎯 Profit Target: ${option_position['profit_target']:.2f}")
        print(f"   🛑 Stop Loss: ${option_position['stop_loss']:.2f}")
        
        return True
    
    # Override the base strategy entry methods to use options
    def _enter_enhanced_long_trade(self, breakout: Dict) -> bool:
        """Override to use options instead of stocks"""
        
        # Apply same filters as base strategy
        if self._is_in_cooldown():
            print("🕐 Cooldown active, skipping trade.")
            return False
        
        if not self._apply_enhanced_filters('long'):
            return False
        
        # Enter options trade instead of stock trade
        return self._enter_options_long_trade(breakout)
    
    def _enter_enhanced_short_trade(self, breakout: Dict) -> bool:
        """Override to use options instead of stocks"""
        
        # Apply same filters as base strategy
        if self._is_in_cooldown():
            print("🕐 Cooldown active, skipping trade.")
            return False
        
        if not self._apply_enhanced_filters('short'):
            return False
        
        # Enter options trade instead of stock trade
        return self._enter_options_short_trade(breakout)
    
    def _manage_options_positions(self):
        """Manage existing options positions"""
        
        if not self.current_options_positions:
            return
        
        current_price = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        positions_to_close = []
        
        for i, position in enumerate(self.current_options_positions):
            # Calculate current option value
            current_option_price = self._estimate_current_option_price(position, current_price, current_date)
            
            # Calculate P&L
            pnl_per_contract = current_option_price - position['entry_price']
            total_pnl = pnl_per_contract * position['contracts'] * 100
            pnl_pct = (current_option_price / position['entry_price'] - 1) * 100
            
            # Check exit conditions
            should_exit = False
            exit_reason = ""
            
            # Profit target
            if current_option_price >= position['profit_target']:
                should_exit = True
                exit_reason = "PROFIT_TARGET"
            
            # Stop loss
            elif current_option_price <= position['stop_loss']:
                should_exit = True
                exit_reason = "STOP_LOSS"
            
            # Time decay exit
            elif position['option_info']['theta'] < self.params.early_exit_theta:
                days_held = (current_date - position['entry_date']).days
                if days_held > 7:  # Only after holding for a week
                    should_exit = True
                    exit_reason = "THETA_DECAY"
            
            # Expiration approach
            elif position['option_info']['days_to_expiry'] <= 7:
                should_exit = True
                exit_reason = "EXPIRATION_APPROACH"
            
            if should_exit:
                self._close_options_position(position, current_option_price, exit_reason, total_pnl, pnl_pct)
                positions_to_close.append(i)
        
        # Remove closed positions
        for i in reversed(positions_to_close):
            self.current_options_positions.pop(i)
    
    def _estimate_current_option_price(self, position: Dict, current_underlying: float, current_date: datetime) -> float:
        """Estimate current option price based on underlying movement"""
        
        option_info = position['option_info']
        entry_underlying = position['underlying_entry_price']
        
        # Calculate underlying price change
        underlying_change = current_underlying - entry_underlying
        underlying_change_pct = underlying_change / entry_underlying
        
        # Estimate option price change using delta
        delta_pnl = underlying_change * option_info['delta']
        
        # Account for time decay (theta)
        days_held = (current_date - position['entry_date']).days
        theta_decay = option_info['theta'] * days_held
        
        # Estimate current option price
        estimated_price = position['entry_price'] + delta_pnl + theta_decay
        
        # Ensure option price doesn't go below intrinsic value
        if option_info['type'] == 'call':
            intrinsic = max(current_underlying - option_info['strike'], 0)
        else:
            intrinsic = max(option_info['strike'] - current_underlying, 0)
        
        estimated_price = max(estimated_price, intrinsic)
        
        return estimated_price
    
    def _close_options_position(self, position: Dict, exit_price: float, reason: str, total_pnl: float, pnl_pct: float):
        """Close an options position"""
        
        # Update strategy statistics
        self.total_trades += 1
        self.total_pnl += total_pnl
        
        if total_pnl > 0:
            self.winning_trades += 1
            result = "WIN"
            emoji = "🟢"
            self.consecutive_losses = 0
        else:
            self.losing_trades += 1
            result = "LOSS"
            emoji = "🔴"
            self.consecutive_losses += 1
        
        # Calculate metrics
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        avg_pnl = self.total_pnl / self.total_trades if self.total_trades > 0 else 0
        
        days_held = (self.data.datetime.date(0) - position['entry_date']).days
        
        print(f"{emoji} OPTIONS TRADE CLOSED ({result}) - {reason}")
        print(f"   📊 Option: {position['option_info']['type'].upper()} ${position['option_info']['strike']}")
        print(f"   💰 Entry: ${position['entry_price']:.2f} → Exit: ${exit_price:.2f}")
        print(f"   📈 P&L: ${total_pnl:.2f} ({pnl_pct:+.1f}%)")
        print(f"   📅 Held: {days_held} days")
        print(f"   📊 Win Rate: {win_rate:.1f}% ({self.winning_trades}/{self.total_trades})")
        print(f"   💵 Avg P&L: ${avg_pnl:.2f}")
    
    def next(self):
        """Main strategy logic - enhanced for options"""
        
        # Run base strategy logic for signal generation
        super().next()
        
        # Manage options positions
        self._manage_options_positions()


# === Strategy Metadata ===
__strategy_name__ = "Options Break & Retest Strategy"
__strategy_version__ = "1.0.0"
__strategy_description__ = "Break and retest strategy using ITM options instead of stocks"
__strategy_author__ = "SentimentTrade Development Team"
__strategy_risk_level__ = "Medium-High"
__strategy_market_type__ = "Trending and Volatile Markets"
__strategy_features__ = [
    "ITM options trading",
    "Real options chain data support",
    "Greeks-based position sizing",
    "Time decay management",
    "Volatility adjustments"
]
