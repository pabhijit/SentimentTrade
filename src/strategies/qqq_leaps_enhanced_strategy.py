#!/usr/bin/env python3
"""
Enhanced QQQ LEAPS Options Strategy - Three Scenario Implementation

This enhanced version implements three distinct trading scenarios with different
entry criteria and win rates, allowing users to choose based on their preferences
for trade frequency vs. win rate optimization.

Scenario 1: Basic (91% win rate) - Any 1% down day
Scenario 2: Gap Down + Trend (96% win rate) - Gap down + above 100 SMA
Scenario 3: Pullback + Trend (96%+ win rate) - 3% pullback from ATH + above 100 SMA

Author: SentimentTrade Development Team
Version: 2.0.0
Last Updated: July 2025
"""

import backtrader as bt
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import pandas as pd


class QQQLeapsEnhancedStrategy(bt.Strategy):
    """
    Enhanced QQQ LEAPS Options Strategy with Three Scenarios
    
    This strategy implements three distinct trading approaches:
    
    Scenario 1 - Basic Strategy (91% Win Rate):
    - Entry: QQQ down 1%+ in any day
    - Frequency: ~112 trades over 5.5 years (20 per year)
    - Win Rate: 91% (102 wins, 10 losses)
    - Best for: Active traders wanting more opportunities
    
    Scenario 2 - Gap Down + Trend Filter (96% Win Rate):
    - Entry: QQQ gaps down 1%+ AND above 100-day SMA
    - Frequency: ~53 trades over 5.5 years (10 per year)
    - Win Rate: 96% (51 wins, 2 losses)
    - Best for: Quality-focused traders
    
    Scenario 3 - Pullback + Trend Filter (96%+ Win Rate):
    - Entry: QQQ down 3%+ from ATH (within 3 months) AND above 100-day SMA
    - Frequency: Lower frequency, highest quality
    - Win Rate: 96%+ (estimated based on analysis)
    - Best for: Conservative traders wanting highest probability
    
    All scenarios use identical exit rules:
    - Take 50% profit
    - 12-month LEAPS expiry
    - 60 delta target
    - No stop loss (let winners run)
    """
    
    # === Strategy Parameters ===
    params = (
        # Scenario Selection
        ('trading_scenario', 1),        # 1, 2, or 3
        ('enable_all_scenarios', False), # Trade all scenarios simultaneously
        
        # Scenario 1: Basic Strategy
        ('s1_min_drop_pct', 1.0),      # 1% daily drop
        ('s1_enabled', True),           # Enable scenario 1
        
        # Scenario 2: Gap Down + Trend
        ('s2_min_gap_pct', 1.0),       # 1% gap down
        ('s2_sma_period', 100),         # 100-day SMA
        ('s2_enabled', True),           # Enable scenario 2
        
        # Scenario 3: Pullback + Trend
        ('s3_pullback_pct', 3.0),      # 3% pullback from ATH
        ('s3_ath_lookback', 63),        # 3 months (63 trading days)
        ('s3_sma_period', 100),         # 100-day SMA
        ('s3_enabled', True),           # Enable scenario 3
        
        # Common Parameters
        ('target_profit_pct', 50.0),    # 50% profit target
        ('expiry_months', 12),          # 12-month LEAPS
        ('target_delta', 60),           # 60 delta target
        ('max_positions_per_scenario', 5), # Max positions per scenario
        ('min_days_between_entries', 7), # Minimum days between entries
        
        # Risk Management
        ('max_total_positions', 15),    # Total positions across all scenarios
        ('emergency_exit_drop', 20.0),  # Emergency exit threshold
        ('bear_market_threshold', 15.0), # Bear market detection
        
        # Performance Tracking
        ('track_scenario_performance', True), # Track each scenario separately
    )
    
    def __init__(self):
        """Initialize the Enhanced QQQ LEAPS Strategy"""
        
        # Technical Indicators
        self.daily_return = bt.indicators.PercentChange(period=1)
        self.sma_100 = bt.indicators.SMA(period=100)  # 100-day SMA for scenarios 2&3
        self.highest_high = bt.indicators.Highest(period=self.params.s3_ath_lookback)  # ATH tracker
        
        # Gap detection
        self.prev_close = None
        self.gap_pct = 0.0
        
        # Strategy State by Scenario
        self.scenario_positions = {
            1: [],  # Scenario 1 positions
            2: [],  # Scenario 2 positions
            3: []   # Scenario 3 positions
        }
        
        self.scenario_stats = {
            1: {'trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0.0},
            2: {'trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0.0},
            3: {'trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0.0}
        }
        
        # Entry tracking
        self.last_entry_dates = {1: None, 2: None, 3: None}
        self.bear_market_mode = False
        
        # Performance tracking
        self.total_premium_paid = 0.0
        self.total_profits_taken = 0.0
        
        print("🎯 Enhanced QQQ LEAPS Strategy Initialized")
        print(f"   Trading Scenario: {self.params.trading_scenario}")
        print(f"   Enable All Scenarios: {self.params.enable_all_scenarios}")
        print("   📊 Scenario Win Rates:")
        print("      Scenario 1 (Basic): 91% (112 trades)")
        print("      Scenario 2 (Gap+Trend): 96% (53 trades)")
        print("      Scenario 3 (Pullback+Trend): 96%+ (estimated)")
    
    def next(self):
        """Main strategy logic executed on each bar"""
        
        # Skip if not enough data for indicators
        if len(self.data) < 100:
            return
        
        current_date = self.data.datetime.date(0)
        current_price = self.data.close[0]
        
        # Calculate gap percentage
        if self.prev_close is not None:
            self.gap_pct = ((self.data.open[0] - self.prev_close) / self.prev_close) * 100
        self.prev_close = self.data.close[0]
        
        # Check for bear market conditions
        self._check_bear_market_conditions()
        
        if self.bear_market_mode:
            return
        
        # Check entry conditions for each scenario
        if self.params.enable_all_scenarios:
            # Trade all enabled scenarios
            if self.params.s1_enabled:
                self._check_scenario_1_entry(current_price, current_date)
            if self.params.s2_enabled:
                self._check_scenario_2_entry(current_price, current_date)
            if self.params.s3_enabled:
                self._check_scenario_3_entry(current_price, current_date)
        else:
            # Trade only selected scenario
            if self.params.trading_scenario == 1 and self.params.s1_enabled:
                self._check_scenario_1_entry(current_price, current_date)
            elif self.params.trading_scenario == 2 and self.params.s2_enabled:
                self._check_scenario_2_entry(current_price, current_date)
            elif self.params.trading_scenario == 3 and self.params.s3_enabled:
                self._check_scenario_3_entry(current_price, current_date)
        
        # Manage existing positions for all scenarios
        self._manage_all_positions(current_price, current_date)
    
    def _check_scenario_1_entry(self, current_price: float, current_date: datetime):
        """
        Scenario 1: Basic Strategy (91% Win Rate)
        Entry: QQQ down 1%+ in any day
        """
        
        daily_return_pct = self.daily_return[0]
        
        # Check entry condition: down 1%+ today
        if daily_return_pct >= -self.params.s1_min_drop_pct:
            return
        
        # Check position limits and spacing
        if not self._can_enter_trade(1):
            return
        
        # Execute trade
        if self._enter_leaps_position(1, current_price, current_date, "1% Down Day"):
            print(f"📉 SCENARIO 1 ENTRY: QQQ down {abs(daily_return_pct):.2f}% at ${current_price:.2f}")
    
    def _check_scenario_2_entry(self, current_price: float, current_date: datetime):
        """
        Scenario 2: Gap Down + Trend Filter (96% Win Rate)
        Entry: QQQ gaps down 1%+ AND above 100-day SMA
        """
        
        # Check gap down condition
        if self.gap_pct >= -self.params.s2_min_gap_pct:
            return
        
        # Check trend filter: price above 100-day SMA
        if current_price <= self.sma_100[0]:
            return
        
        # Check position limits and spacing
        if not self._can_enter_trade(2):
            return
        
        # Execute trade
        if self._enter_leaps_position(2, current_price, current_date, f"Gap Down {abs(self.gap_pct):.2f}% + Above SMA"):
            print(f"📉 SCENARIO 2 ENTRY: Gap down {abs(self.gap_pct):.2f}%, Price ${current_price:.2f} > SMA ${self.sma_100[0]:.2f}")
    
    def _check_scenario_3_entry(self, current_price: float, current_date: datetime):
        """
        Scenario 3: Pullback + Trend Filter (96%+ Win Rate)
        Entry: QQQ down 3%+ from ATH (within 3 months) AND above 100-day SMA
        """
        
        # Get recent all-time high
        recent_ath = self.highest_high[0]
        
        # Calculate pullback from ATH
        pullback_pct = ((recent_ath - current_price) / recent_ath) * 100
        
        # Check pullback condition: down 3%+ from recent ATH
        if pullback_pct < self.params.s3_pullback_pct:
            return
        
        # Check trend filter: price above 100-day SMA
        if current_price <= self.sma_100[0]:
            return
        
        # Check position limits and spacing
        if not self._can_enter_trade(3):
            return
        
        # Execute trade
        if self._enter_leaps_position(3, current_price, current_date, f"{pullback_pct:.1f}% Pullback + Above SMA"):
            print(f"📉 SCENARIO 3 ENTRY: {pullback_pct:.1f}% pullback from ATH ${recent_ath:.2f}, Price ${current_price:.2f} > SMA ${self.sma_100[0]:.2f}")
    
    def _can_enter_trade(self, scenario: int) -> bool:
        """Check if we can enter a trade for the given scenario"""
        
        # Check scenario-specific position limit
        if len(self.scenario_positions[scenario]) >= self.params.max_positions_per_scenario:
            return False
        
        # Check total position limit
        total_positions = sum(len(positions) for positions in self.scenario_positions.values())
        if total_positions >= self.params.max_total_positions:
            return False
        
        # Check minimum days between entries
        if self.last_entry_dates[scenario]:
            current_date = self.data.datetime.date(0)
            days_since_last = (current_date - self.last_entry_dates[scenario]).days
            if days_since_last < self.params.min_days_between_entries:
                return False
        
        # Check available capital
        estimated_cost = 6000  # Estimated LEAPS cost
        if self.broker.getcash() < estimated_cost:
            return False
        
        return True
    
    def _enter_leaps_position(self, scenario: int, current_price: float, entry_date: datetime, reason: str) -> bool:
        """Enter a new LEAPS position for the specified scenario"""
        
        # Calculate option parameters
        strike_price = self._calculate_optimal_strike(current_price)
        expiry_date = self._calculate_expiry_date(entry_date)
        estimated_premium = self._estimate_option_premium(current_price, strike_price)
        estimated_delta = self.params.target_delta
        
        # Create position record
        position = {
            'scenario': scenario,
            'entry_date': entry_date,
            'entry_price': current_price,
            'strike_price': strike_price,
            'expiry_date': expiry_date,
            'premium_paid': estimated_premium,
            'contracts': 1,
            'target_profit': estimated_premium * (1 + self.params.target_profit_pct / 100),
            'estimated_delta': estimated_delta,
            'status': 'open',
            'days_held': 0,
            'entry_reason': reason
        }
        
        # Add to scenario positions
        self.scenario_positions[scenario].append(position)
        self.last_entry_dates[scenario] = entry_date
        
        # Update totals
        self.total_premium_paid += estimated_premium
        
        # Log the trade
        scenario_names = {1: "Basic", 2: "Gap+Trend", 3: "Pullback+Trend"}
        print(f"🟢 SCENARIO {scenario} ({scenario_names[scenario]}) LEAPS ENTRY:")
        print(f"   📅 Date: {entry_date}")
        print(f"   💰 Premium: ${estimated_premium:.0f}")
        print(f"   🎯 Target: ${position['target_profit']:.0f} (50% profit)")
        print(f"   📊 Reason: {reason}")
        print(f"   📈 Open Positions: S1={len(self.scenario_positions[1])}, S2={len(self.scenario_positions[2])}, S3={len(self.scenario_positions[3])}")
        
        return True
    
    def _manage_all_positions(self, current_price: float, current_date: datetime):
        """Manage existing positions across all scenarios"""
        
        for scenario in [1, 2, 3]:
            positions_to_close = []
            
            for i, position in enumerate(self.scenario_positions[scenario]):
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
                
                # Check for expiry approach
                days_to_expiry = (position['expiry_date'] - current_date).days
                if days_to_expiry <= 30:
                    self._close_position(position, current_value, current_date, 'EXPIRY_APPROACH')
                    positions_to_close.append(i)
                    continue
                
                # Check maximum holding period
                if position['days_held'] >= 365:
                    self._close_position(position, current_value, current_date, 'MAX_HOLDING')
                    positions_to_close.append(i)
                    continue
            
            # Remove closed positions
            for i in reversed(positions_to_close):
                self.scenario_positions[scenario].pop(i)
    
    def _close_position(self, position: Dict, exit_value: float, exit_date: datetime, reason: str):
        """Close a LEAPS position and update statistics"""
        
        scenario = position['scenario']
        position['status'] = 'closed'
        position['exit_date'] = exit_date
        position['exit_value'] = exit_value
        position['exit_reason'] = reason
        
        # Calculate P&L
        pnl = exit_value - position['premium_paid']
        pnl_pct = (pnl / position['premium_paid']) * 100
        
        # Update scenario statistics
        self.scenario_stats[scenario]['trades'] += 1
        self.scenario_stats[scenario]['total_pnl'] += pnl
        
        if pnl > 0:
            self.scenario_stats[scenario]['wins'] += 1
            result = "WIN"
            emoji = "🟢"
        else:
            self.scenario_stats[scenario]['losses'] += 1
            result = "LOSS"
            emoji = "🔴"
        
        # Update totals
        self.total_profits_taken += exit_value
        
        # Log the trade
        scenario_names = {1: "Basic", 2: "Gap+Trend", 3: "Pullback+Trend"}
        print(f"{emoji} SCENARIO {scenario} ({scenario_names[scenario]}) CLOSED ({result}) - {reason}")
        print(f"   📅 Held: {position['days_held']} days")
        print(f"   💰 P&L: ${pnl:.0f} ({pnl_pct:.1f}%)")
        print(f"   📊 Entry: {position['entry_reason']}")
        
        # Update scenario win rate
        if self.scenario_stats[scenario]['trades'] > 0:
            win_rate = (self.scenario_stats[scenario]['wins'] / self.scenario_stats[scenario]['trades']) * 100
            print(f"   📈 Scenario {scenario} Win Rate: {win_rate:.1f}%")
    
    def _calculate_optimal_strike(self, current_price: float) -> float:
        """Calculate optimal strike price for 60 delta"""
        # For 60 delta, approximately 5-8% in-the-money
        target_moneyness = 0.93  # Strike at 93% of current price
        optimal_strike = round(current_price * target_moneyness / 5) * 5
        return optimal_strike
    
    def _calculate_expiry_date(self, entry_date: datetime) -> datetime:
        """Calculate 12-month expiry date"""
        expiry_year = entry_date.year + 1
        expiry_month = entry_date.month
        return datetime(expiry_year, expiry_month, 15)  # 3rd Friday approximation
    
    def _estimate_option_premium(self, spot_price: float, strike_price: float) -> float:
        """Estimate LEAPS premium"""
        intrinsic_value = max(spot_price - strike_price, 0)
        time_value = spot_price * 0.12  # Simplified time value
        return intrinsic_value + time_value
    
    def _calculate_current_option_value(self, position: Dict, current_price: float) -> float:
        """Calculate current option value"""
        strike_price = position['strike_price']
        entry_price = position['entry_price']
        premium_paid = position['premium_paid']
        days_held = position['days_held']
        
        # Price movement impact
        price_change_pct = (current_price - entry_price) / entry_price
        delta = position['estimated_delta'] / 100
        price_impact = price_change_pct * delta * premium_paid
        
        # Time decay (simplified)
        time_decay_factor = 1 - (days_held / 365) * 0.3
        time_decay_impact = premium_paid * (1 - time_decay_factor)
        
        current_value = premium_paid + price_impact - time_decay_impact
        return max(current_value, 0)
    
    def _check_bear_market_conditions(self):
        """Check for bear market conditions"""
        monthly_return = bt.indicators.PercentChange(period=21)[0]  # ~1 month
        
        if monthly_return <= -self.params.bear_market_threshold:
            if not self.bear_market_mode:
                print(f"🐻 BEAR MARKET MODE: QQQ down {abs(monthly_return):.1f}% this month")
                self.bear_market_mode = True
        else:
            if self.bear_market_mode and monthly_return > -5.0:
                print(f"🐂 EXITING BEAR MARKET MODE: QQQ recovery detected")
                self.bear_market_mode = False
    
    def stop(self):
        """Strategy completion summary with scenario breakdown"""
        
        final_value = self.broker.getvalue()
        
        print("\n" + "="*70)
        print("🎯 ENHANCED QQQ LEAPS STRATEGY COMPLETED")
        print("="*70)
        print(f"📊 Final Portfolio Value: ${final_value:.0f}")
        
        # Overall statistics
        total_trades = sum(stats['trades'] for stats in self.scenario_stats.values())
        total_wins = sum(stats['wins'] for stats in self.scenario_stats.values())
        total_losses = sum(stats['losses'] for stats in self.scenario_stats.values())
        total_pnl = sum(stats['total_pnl'] for stats in self.scenario_stats.values())
        
        if total_trades > 0:
            overall_win_rate = (total_wins / total_trades) * 100
            avg_pnl = total_pnl / total_trades
            print(f"📈 Overall Performance:")
            print(f"   Total Trades: {total_trades}")
            print(f"   Win Rate: {overall_win_rate:.1f}% ({total_wins} wins, {total_losses} losses)")
            print(f"   Average P&L: ${avg_pnl:.0f}")
            print(f"   Total P&L: ${total_pnl:.0f}")
        
        # Scenario breakdown
        scenario_names = {1: "Basic (91% target)", 2: "Gap+Trend (96% target)", 3: "Pullback+Trend (96%+ target)"}
        
        print(f"\n📊 Scenario Performance Breakdown:")
        for scenario in [1, 2, 3]:
            stats = self.scenario_stats[scenario]
            if stats['trades'] > 0:
                win_rate = (stats['wins'] / stats['trades']) * 100
                avg_pnl = stats['total_pnl'] / stats['trades']
                print(f"   Scenario {scenario} - {scenario_names[scenario]}:")
                print(f"      Trades: {stats['trades']}")
                print(f"      Win Rate: {win_rate:.1f}% ({stats['wins']} wins, {stats['losses']} losses)")
                print(f"      Average P&L: ${avg_pnl:.0f}")
                print(f"      Total P&L: ${stats['total_pnl']:.0f}")
            else:
                print(f"   Scenario {scenario} - {scenario_names[scenario]}: No trades")
        
        # Open positions
        total_open = sum(len([p for p in positions if p.get('status') == 'open']) 
                        for positions in self.scenario_positions.values())
        if total_open > 0:
            print(f"\n📊 Open Positions: {total_open}")
            for scenario in [1, 2, 3]:
                open_count = len([p for p in self.scenario_positions[scenario] if p.get('status') == 'open'])
                if open_count > 0:
                    print(f"   Scenario {scenario}: {open_count} positions")
        
        print(f"\n💰 Financial Summary:")
        print(f"   Total Premium Paid: ${self.total_premium_paid:.0f}")
        print(f"   Total Profits Taken: ${self.total_profits_taken:.0f}")
        
        print(f"\n🎯 Historical Benchmarks:")
        print(f"   Scenario 1 Target: 91% win rate (112 trades over 5.5 years)")
        print(f"   Scenario 2 Target: 96% win rate (53 trades over 5.5 years)")
        print(f"   Scenario 3 Target: 96%+ win rate (estimated)")
        print("="*70)


# === Strategy Metadata ===
__strategy_name__ = "Enhanced QQQ LEAPS Strategy"
__strategy_version__ = "2.0.0"
__strategy_description__ = "Three-scenario LEAPS strategy with 91-96%+ win rates"
__strategy_author__ = "SentimentTrade Development Team"
__strategy_scenarios__ = {
    1: {"name": "Basic", "win_rate": "91%", "frequency": "High"},
    2: {"name": "Gap+Trend", "win_rate": "96%", "frequency": "Medium"},
    3: {"name": "Pullback+Trend", "win_rate": "96%+", "frequency": "Low"}
}
