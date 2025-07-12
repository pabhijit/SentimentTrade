#!/usr/bin/env python3
"""
QQQ LEAPS Options Strategy - "The Pelosi Special"

A mechanical options strategy with 91% win rate based on buying QQQ LEAPS calls
on 1%+ down days and taking 50% profits. This strategy requires no technical analysis
and is designed for set-and-forget monthly management.

Strategy Overview:
- Buy QQQ LEAPS calls (12-month expiry, 60-80 delta) when QQQ drops 1%+ in a day
- Target 50% profit (typically achieved in 3-4 months)
- No stop loss - let winners run and losers expire
- Dollar cost averaging approach with monthly entries
- Historical performance: 91% win rate over 5 years, $176K profit from $25K

Author: SentimentTrade Development Team
Version: 1.0.0
Last Updated: July 2025
"""

import backtrader as bt
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import pandas as pd


class QQQLeapsStrategy(bt.Strategy):
    """
    QQQ LEAPS Options Strategy Implementation
    
    This strategy implements the mechanical LEAPS buying system described in the
    trading video, designed to capture QQQ's quarterly upward movements with
    high probability and excellent risk-adjusted returns.
    
    Strategy Characteristics:
    - Type: Long-term Options / LEAPS
    - Timeframe: 3-4 month holding periods
    - Market: QQQ (NASDAQ-100 ETF) only
    - Win Rate: 91% historical (85% quarterly up moves)
    - Risk Level: Medium (limited downside, unlimited upside)
    
    Key Statistics (5-year backtest):
    - Total Return: 705% ($25K → $201K)
    - Win Rate: 91% (102 wins, 10 losses)
    - Average Trade Duration: 127 days
    - Average Winner: $2,560
    - Average Loser: $3,348
    - Maximum Drawdown: $18,000 (2022 bear market)
    
    Entry Rules:
    1. QQQ drops 1%+ in a single day (gap down or intraday)
    2. Buy 1 LEAPS call contract (12-month expiry)
    3. Target 60-80 delta (in-the-money options)
    4. No more than 1 contract per entry signal
    
    Exit Rules:
    1. Take 50% profit when achieved
    2. No stop loss (let losers run to expiry)
    3. Close all positions during major market crashes
    4. Monthly position review and management
    
    Risk Management:
    - Position sizing: 1 contract per signal
    - Dollar cost averaging through regular entries
    - Cash reserves for market crashes
    - Macro event awareness (Fed policy, recessions)
    
    Usage Example:
        # Create strategy with default parameters
        strategy = QQQLeapsStrategy()
        
        # Or customize parameters
        cerebro.addstrategy(QQQLeapsStrategy, 
                          min_drop_pct=1.0,
                          target_profit_pct=50.0,
                          target_delta=70)
    """
    
    # === Strategy Parameters ===
    params = (
        # Entry Criteria
        ('min_drop_pct', 1.0),          # Minimum 1% drop to trigger entry
        ('max_entries_per_month', 2),    # Maximum 2 entries per month
        ('min_days_between_entries', 7), # Minimum 7 days between entries
        
        # Options Specifications
        ('expiry_months', 12),          # 12-month LEAPS expiry
        ('target_delta', 65),           # Target 65 delta (60-80 range)
        ('delta_tolerance', 10),        # ±10 delta tolerance
        
        # Exit Criteria
        ('target_profit_pct', 50.0),    # Take 50% profit
        ('max_holding_days', 365),      # Maximum 1 year holding
        ('monthly_review_day', 1),      # Review positions on 1st of month
        
        # Risk Management
        ('max_concurrent_positions', 10), # Maximum 10 open positions
        ('emergency_exit_drop', 20.0),   # Close all if QQQ drops 20%+ in month
        ('bear_market_threshold', 15.0), # Stop trading if 15%+ monthly drop
        
        # Position Sizing
        ('contract_cost_estimate', 6000), # Estimated cost per LEAPS contract
        ('max_portfolio_risk', 0.8),     # Use 80% of portfolio for options
        
        # Performance Tracking
        ('track_greeks', True),          # Track option Greeks
        ('log_detailed_trades', True),   # Detailed trade logging
    )
    
    def __init__(self):
        """Initialize the QQQ LEAPS Strategy"""
        
        # Technical Indicators (minimal - this is a mechanical strategy)
        self.daily_return = bt.indicators.PercentChange(period=1)
        self.monthly_return = bt.indicators.PercentChange(period=21)  # ~1 month
        self.sma_200 = bt.indicators.SMA(period=200)  # Long-term trend
        
        # Strategy State
        self.open_positions = []        # List of open LEAPS positions
        self.entry_dates = []          # Track entry dates for spacing
        self.last_review_date = None   # Last monthly review date
        self.bear_market_mode = False  # Emergency mode flag
        
        # Position Tracking
        self.total_contracts = 0       # Total contracts purchased
        self.total_premium_paid = 0.0  # Total premium paid
        self.total_profits_taken = 0.0 # Total profits realized
        self.current_month_entries = 0 # Entries this month
        
        # Performance Metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_portfolio_value = 0.0
        
        # Greeks Tracking (simulated)
        self.total_delta = 0.0
        self.total_gamma = 0.0
        self.total_theta = 0.0
        self.total_vega = 0.0
        
        print("🎯 QQQ LEAPS Strategy - 'The Pelosi Special' Initialized")
        print(f"   Entry Trigger: {self.params.min_drop_pct}% daily drop")
        print(f"   Target Profit: {self.params.target_profit_pct}%")
        print(f"   Target Delta: {self.params.target_delta} ±{self.params.delta_tolerance}")
        print(f"   Max Positions: {self.params.max_concurrent_positions}")
        print(f"   Historical Win Rate: 91% (5-year backtest)")
        print(f"   Expected Return: 705% over 5 years")
    
    def next(self):
        """Main strategy logic executed on each bar"""
        
        # Skip if not enough data
        if len(self.data) < 200:  # Need 200 days for trend analysis
            return
        
        current_date = self.data.datetime.date(0)
        current_price = self.data.close[0]
        daily_return_pct = self.daily_return[0]
        monthly_return_pct = self.monthly_return[0]
        
        # Monthly position review (1st trading day of month)
        if self._is_monthly_review_day(current_date):
            self._conduct_monthly_review()
        
        # Check for bear market conditions
        self._check_bear_market_conditions(monthly_return_pct)
        
        # Skip trading in bear market mode
        if self.bear_market_mode:
            return
        
        # Check for entry signals
        if self._check_entry_conditions(daily_return_pct, current_date):
            self._enter_leaps_position(current_price, current_date)
        
        # Manage existing positions
        self._manage_existing_positions(current_price, current_date)
        
        # Update performance metrics
        self._update_performance_metrics()
    
    def _check_entry_conditions(self, daily_return_pct: float, current_date: datetime) -> bool:
        """Check if entry conditions are met"""
        
        # Primary condition: QQQ down 1%+ today
        if daily_return_pct >= -self.params.min_drop_pct:
            return False
        
        # Check maximum concurrent positions
        if len(self.open_positions) >= self.params.max_concurrent_positions:
            print(f"   ⚠️ Max concurrent positions reached: {len(self.open_positions)}")
            return False
        
        # Check monthly entry limit
        if self.current_month_entries >= self.params.max_entries_per_month:
            print(f"   ⚠️ Max monthly entries reached: {self.current_month_entries}")
            return False
        
        # Check minimum days between entries
        if self.entry_dates:
            days_since_last = (current_date - self.entry_dates[-1]).days
            if days_since_last < self.params.min_days_between_entries:
                print(f"   ⚠️ Too soon since last entry: {days_since_last} days")
                return False
        
        # Check available capital
        estimated_cost = self.params.contract_cost_estimate
        available_cash = self.broker.getcash()
        if available_cash < estimated_cost:
            print(f"   ⚠️ Insufficient cash: ${available_cash:.0f} < ${estimated_cost:.0f}")
            return False
        
        return True
    
    def _enter_leaps_position(self, current_price: float, entry_date: datetime):
        """Enter a new LEAPS position"""
        
        # Calculate option parameters
        strike_price = self._calculate_optimal_strike(current_price)
        expiry_date = self._calculate_expiry_date(entry_date)
        estimated_premium = self._estimate_option_premium(current_price, strike_price)
        estimated_delta = self._estimate_delta(current_price, strike_price)
        
        # Create position record
        position = {
            'entry_date': entry_date,
            'entry_price': current_price,
            'strike_price': strike_price,
            'expiry_date': expiry_date,
            'premium_paid': estimated_premium,
            'contracts': 1,
            'target_profit': estimated_premium * (1 + self.params.target_profit_pct / 100),
            'estimated_delta': estimated_delta,
            'status': 'open',
            'days_held': 0
        }
        
        # Execute the trade (simulated)
        self.open_positions.append(position)
        self.entry_dates.append(entry_date)
        self.current_month_entries += 1
        self.total_contracts += 1
        self.total_premium_paid += estimated_premium
        
        # Update Greeks
        self.total_delta += estimated_delta
        
        # Log the trade
        print(f"🟢 LEAPS ENTRY: QQQ @ ${current_price:.2f} (Down {abs(self.daily_return[0]):.2f}%)")
        print(f"   📅 Entry Date: {entry_date}")
        print(f"   🎯 Strike: ${strike_price:.0f} (Delta: {estimated_delta:.0f})")
        print(f"   📅 Expiry: {expiry_date} ({(expiry_date - entry_date).days} days)")
        print(f"   💰 Premium: ${estimated_premium:.0f}")
        print(f"   🎯 Target: ${position['target_profit']:.0f} (50% profit)")
        print(f"   📊 Open Positions: {len(self.open_positions)}")
    
    def _calculate_optimal_strike(self, current_price: float) -> float:
        """Calculate optimal strike price for target delta"""
        
        # For 60-80 delta, we want in-the-money options
        # Approximate: 65 delta ≈ 5-10% in-the-money
        target_moneyness = 0.92  # Strike at 92% of current price (8% ITM)
        
        # Round to nearest $5 strike
        optimal_strike = round(current_price * target_moneyness / 5) * 5
        
        return optimal_strike
    
    def _calculate_expiry_date(self, entry_date: datetime) -> datetime:
        """Calculate expiry date (12 months out)"""
        
        # Add 12 months to entry date
        expiry_year = entry_date.year + (entry_date.month + self.params.expiry_months - 1) // 12
        expiry_month = (entry_date.month + self.params.expiry_months - 1) % 12 + 1
        
        # Use 3rd Friday of expiry month (standard options expiry)
        expiry_date = datetime(expiry_year, expiry_month, 15)  # Approximate
        
        return expiry_date
    
    def _estimate_option_premium(self, spot_price: float, strike_price: float) -> float:
        """Estimate LEAPS option premium using simplified Black-Scholes"""
        
        # Simplified premium estimation
        # Real implementation would use actual options pricing
        
        moneyness = spot_price / strike_price
        time_to_expiry = self.params.expiry_months / 12.0
        
        # Base premium calculation
        intrinsic_value = max(spot_price - strike_price, 0)
        time_value_factor = 0.15 * spot_price * np.sqrt(time_to_expiry)  # Simplified
        
        estimated_premium = intrinsic_value + time_value_factor
        
        # Adjust based on historical data (average LEAPS cost ~$6000)
        premium_multiplier = 6000 / (spot_price * 0.12)  # Calibration factor
        estimated_premium *= premium_multiplier
        
        return max(estimated_premium, 1000)  # Minimum $1000 premium
    
    def _estimate_delta(self, spot_price: float, strike_price: float) -> float:
        """Estimate option delta"""
        
        # Simplified delta estimation
        moneyness = spot_price / strike_price
        
        if moneyness >= 1.1:  # Deep ITM
            return 85
        elif moneyness >= 1.05:  # ITM
            return 75
        elif moneyness >= 0.95:  # ATM
            return 55
        else:  # OTM
            return 35
    
    def _manage_existing_positions(self, current_price: float, current_date: datetime):
        """Manage existing LEAPS positions"""
        
        positions_to_close = []
        
        for i, position in enumerate(self.open_positions):
            if position['status'] != 'open':
                continue
            
            # Update days held
            position['days_held'] = (current_date - position['entry_date']).days
            
            # Calculate current option value
            current_value = self._calculate_current_option_value(position, current_price)
            current_pnl = current_value - position['premium_paid']
            current_pnl_pct = (current_pnl / position['premium_paid']) * 100
            
            # Check for profit target
            if current_pnl_pct >= self.params.target_profit_pct:
                self._close_position(position, current_value, current_date, 'PROFIT_TARGET')
                positions_to_close.append(i)
                continue
            
            # Check for expiry
            days_to_expiry = (position['expiry_date'] - current_date).days
            if days_to_expiry <= 30:  # Close 30 days before expiry
                self._close_position(position, current_value, current_date, 'EXPIRY_APPROACH')
                positions_to_close.append(i)
                continue
            
            # Check maximum holding period
            if position['days_held'] >= self.params.max_holding_days:
                self._close_position(position, current_value, current_date, 'MAX_HOLDING')
                positions_to_close.append(i)
                continue
        
        # Remove closed positions
        for i in reversed(positions_to_close):
            self.open_positions.pop(i)
    
    def _calculate_current_option_value(self, position: Dict, current_price: float) -> float:
        """Calculate current option value"""
        
        # Simplified current value calculation
        strike_price = position['strike_price']
        entry_price = position['entry_price']
        premium_paid = position['premium_paid']
        days_held = position['days_held']
        
        # Price movement factor
        price_change_pct = (current_price - entry_price) / entry_price
        
        # Time decay factor (theta)
        time_decay_factor = 1 - (days_held / 365) * 0.3  # Lose 30% to time decay over year
        
        # Delta approximation for price sensitivity
        delta = position['estimated_delta'] / 100
        
        # Simplified value calculation
        price_impact = price_change_pct * delta * premium_paid
        time_decay_impact = premium_paid * (1 - time_decay_factor)
        
        current_value = premium_paid + price_impact - time_decay_impact
        
        return max(current_value, 0)  # Options can't go below 0
    
    def _close_position(self, position: Dict, exit_value: float, exit_date: datetime, reason: str):
        """Close a LEAPS position"""
        
        position['status'] = 'closed'
        position['exit_date'] = exit_date
        position['exit_value'] = exit_value
        position['exit_reason'] = reason
        
        # Calculate P&L
        pnl = exit_value - position['premium_paid']
        pnl_pct = (pnl / position['premium_paid']) * 100
        
        # Update statistics
        self.total_trades += 1
        self.total_pnl += pnl
        self.total_profits_taken += exit_value
        
        if pnl > 0:
            self.winning_trades += 1
            result = "WIN"
            emoji = "🟢"
        else:
            self.losing_trades += 1
            result = "LOSS"
            emoji = "🔴"
        
        # Update Greeks
        self.total_delta -= position['estimated_delta']
        
        # Log the trade
        print(f"{emoji} LEAPS CLOSED ({result}) - {reason}")
        print(f"   📅 Held: {position['days_held']} days")
        print(f"   💰 P&L: ${pnl:.0f} ({pnl_pct:.1f}%)")
        print(f"   🎯 Strike: ${position['strike_price']:.0f}")
        print(f"   📊 Remaining Positions: {len([p for p in self.open_positions if p['status'] == 'open']) - 1}")
    
    def _is_monthly_review_day(self, current_date: datetime) -> bool:
        """Check if today is monthly review day"""
        
        if self.last_review_date is None:
            return current_date.day == self.params.monthly_review_day
        
        # Check if we're in a new month
        return (current_date.month != self.last_review_date.month and 
                current_date.day >= self.params.monthly_review_day)
    
    def _conduct_monthly_review(self):
        """Conduct monthly position review"""
        
        current_date = self.data.datetime.date(0)
        current_price = self.data.close[0]
        
        print(f"\n📅 MONTHLY REVIEW - {current_date.strftime('%B %Y')}")
        print("=" * 50)
        
        # Reset monthly counters
        self.current_month_entries = 0
        self.last_review_date = current_date
        
        # Review open positions
        open_positions = [p for p in self.open_positions if p['status'] == 'open']
        total_premium_at_risk = sum(p['premium_paid'] for p in open_positions)
        
        print(f"📊 Open Positions: {len(open_positions)}")
        print(f"💰 Total Premium at Risk: ${total_premium_at_risk:.0f}")
        print(f"📈 Current QQQ Price: ${current_price:.2f}")
        
        # Calculate unrealized P&L
        total_unrealized_pnl = 0
        for position in open_positions:
            current_value = self._calculate_current_option_value(position, current_price)
            unrealized_pnl = current_value - position['premium_paid']
            total_unrealized_pnl += unrealized_pnl
        
        print(f"💵 Unrealized P&L: ${total_unrealized_pnl:.0f}")
        
        # Performance summary
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            avg_pnl = self.total_pnl / self.total_trades
            print(f"🎯 Win Rate: {win_rate:.1f}% ({self.winning_trades}/{self.total_trades})")
            print(f"💰 Average P&L: ${avg_pnl:.0f}")
            print(f"💵 Total Realized P&L: ${self.total_pnl:.0f}")
        
        print("=" * 50)
    
    def _check_bear_market_conditions(self, monthly_return_pct: float):
        """Check for bear market conditions and emergency exits"""
        
        # Check for emergency exit conditions
        if monthly_return_pct <= -self.params.emergency_exit_drop:
            print(f"🚨 EMERGENCY EXIT: QQQ down {abs(monthly_return_pct):.1f}% this month")
            self._emergency_exit_all_positions()
            self.bear_market_mode = True
            return
        
        # Check for bear market entry
        if monthly_return_pct <= -self.params.bear_market_threshold:
            if not self.bear_market_mode:
                print(f"🐻 BEAR MARKET MODE: QQQ down {abs(monthly_return_pct):.1f}% this month")
                self.bear_market_mode = True
        else:
            # Exit bear market mode if conditions improve
            if self.bear_market_mode and monthly_return_pct > -5.0:
                print(f"🐂 EXITING BEAR MARKET MODE: QQQ recovery detected")
                self.bear_market_mode = False
    
    def _emergency_exit_all_positions(self):
        """Emergency exit all positions during market crash"""
        
        current_date = self.data.datetime.date(0)
        current_price = self.data.close[0]
        
        open_positions = [p for p in self.open_positions if p['status'] == 'open']
        
        for position in open_positions:
            # Estimate emergency exit value (typically much lower)
            emergency_value = position['premium_paid'] * 0.3  # Assume 70% loss in crash
            self._close_position(position, emergency_value, current_date, 'EMERGENCY_EXIT')
        
        print(f"🚨 EMERGENCY EXIT COMPLETE: Closed {len(open_positions)} positions")
    
    def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        
        current_portfolio_value = self.broker.getvalue()
        
        # Track peak value for drawdown calculation
        if current_portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_portfolio_value
        
        # Calculate current drawdown
        if self.peak_portfolio_value > 0:
            current_drawdown = (self.peak_portfolio_value - current_portfolio_value) / self.peak_portfolio_value
            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown
    
    def notify_order(self, order):
        """Handle order notifications (simplified for options)"""
        
        if order.status in [order.Completed]:
            print(f"✅ ORDER EXECUTED: Simulated LEAPS transaction")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"❌ ORDER FAILED: {order.getstatusname()}")
    
    def stop(self):
        """Strategy completion summary"""
        
        final_value = self.broker.getvalue()
        
        print("\n" + "="*60)
        print("🎯 QQQ LEAPS STRATEGY - 'THE PELOSI SPECIAL' COMPLETED")
        print("="*60)
        print(f"📊 Final Portfolio Value: ${final_value:.0f}")
        print(f"📈 Total Trades: {self.total_trades}")
        print(f"🟢 Winning Trades: {self.winning_trades}")
        print(f"🔴 Losing Trades: {self.losing_trades}")
        
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            avg_pnl = self.total_pnl / self.total_trades
            avg_winner = self.total_pnl / self.winning_trades if self.winning_trades > 0 else 0
            avg_loser = (self.total_pnl - (avg_winner * self.winning_trades)) / self.losing_trades if self.losing_trades > 0 else 0
            
            print(f"📊 Win Rate: {win_rate:.1f}% (Target: 91%)")
            print(f"💰 Average P&L per Trade: ${avg_pnl:.0f}")
            print(f"🟢 Average Winner: ${avg_winner:.0f}")
            print(f"🔴 Average Loser: ${avg_loser:.0f}")
            print(f"💵 Total P&L: ${self.total_pnl:.0f}")
        
        print(f"📉 Maximum Drawdown: {self.max_drawdown:.1%}")
        print(f"📊 Total Contracts Traded: {self.total_contracts}")
        print(f"💰 Total Premium Paid: ${self.total_premium_paid:.0f}")
        print(f"💵 Total Profits Taken: ${self.total_profits_taken:.0f}")
        
        # Open positions summary
        open_positions = [p for p in self.open_positions if p['status'] == 'open']
        if open_positions:
            print(f"📊 Open Positions: {len(open_positions)}")
            total_open_premium = sum(p['premium_paid'] for p in open_positions)
            print(f"💰 Open Premium at Risk: ${total_open_premium:.0f}")
        
        print(f"\n🔧 Strategy Parameters:")
        print(f"   📏 Entry Trigger: {self.params.min_drop_pct}% daily drop")
        print(f"   🎯 Profit Target: {self.params.target_profit_pct}%")
        print(f"   📅 LEAPS Expiry: {self.params.expiry_months} months")
        print(f"   🎯 Target Delta: {self.params.target_delta}")
        print(f"   📊 Max Positions: {self.params.max_concurrent_positions}")
        
        print("\n📈 Historical Benchmark (5-year backtest):")
        print(f"   🎯 Target Win Rate: 91%")
        print(f"   💰 Target Return: 705% over 5 years")
        print(f"   📊 Expected Avg Winner: $2,560")
        print(f"   📉 Expected Avg Loser: $3,348")
        print(f"   📅 Expected Avg Duration: 127 days")
        print("="*60)


# === Strategy Metadata ===
__strategy_name__ = "QQQ LEAPS Strategy"
__strategy_version__ = "1.0.0"
__strategy_description__ = "Mechanical LEAPS options strategy with 91% win rate"
__strategy_author__ = "SentimentTrade Development Team"
__strategy_risk_level__ = "Medium"
__strategy_market_type__ = "Bull Markets and Corrections"
__strategy_nickname__ = "The Pelosi Special"
__historical_performance__ = {
    "win_rate": "91%",
    "total_return": "705%",
    "time_period": "5 years",
    "max_drawdown": "18%",
    "avg_trade_duration": "127 days"
}
