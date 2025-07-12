#!/usr/bin/env python3
"""
Mean Reversion Trading Strategy for SentimentTrade Platform

This module implements a Bollinger Bands-based mean reversion strategy that identifies
oversold and overbought conditions to trade price reversals back to the mean.

Strategy Logic:
- BUY: When price touches or breaks below lower Bollinger Band (oversold)
- SELL: When price touches or breaks above upper Bollinger Band (overbought)
- EXIT: When price reverts to the middle Bollinger Band (mean)

Author: SentimentTrade Development Team
Version: 1.0.0
Last Updated: July 2025
"""

import backtrader as bt


class MeanReversionStrategy(bt.Strategy):
    """
    Bollinger Bands Mean Reversion Strategy
    
    A contrarian strategy that assumes prices will revert to their statistical mean
    after extreme movements. Uses Bollinger Bands to identify overbought/oversold
    conditions and trades the expected reversion.
    
    Strategy Characteristics:
    - Type: Mean Reversion / Contrarian
    - Timeframe: Any (optimized for daily/4-hour)
    - Market Conditions: Works best in range-bound, volatile markets
    - Risk Level: Medium-High (can face extended trends)
    
    Signal Generation:
    1. Price < Lower BB → BUY (oversold condition)
    2. Price > Upper BB → SELL (overbought condition)
    3. Price crosses middle BB → EXIT (mean reversion complete)
    
    Parameters:
    - period (int): Bollinger Bands calculation period (default: 20)
    - devfactor (float): Standard deviation multiplier (default: 2.0)
    
    Performance Characteristics:
    - Win Rate: Typically 60-75% (high win rate, smaller average wins)
    - Risk/Reward: Often 1:1 or lower (many small wins, few large losses)
    - Drawdown: Can be significant during strong trends
    - Best Markets: Sideways, volatile, range-bound conditions
    
    Usage Example:
        # Create strategy with custom parameters
        strategy = MeanReversionStrategy()
        strategy.params.period = 14
        strategy.params.devfactor = 2.5
        
        # Or use in backtrader cerebro
        cerebro.addstrategy(MeanReversionStrategy, period=14, devfactor=2.5)
    """
    
    # === Strategy Parameters ===
    params = dict(
        period=20,      # Bollinger Bands period (moving average length)
        devfactor=2.0,  # Standard deviation multiplier for bands
    )

    def __init__(self):
        """
        Initialize the Mean Reversion Strategy
        
        Sets up Bollinger Bands indicator and internal state variables required
        for mean reversion trading decisions.
        
        Indicators Created:
        - Bollinger Bands: Upper, Middle (SMA), and Lower bands
        - Band Width: For volatility assessment
        - Band Position: Price position relative to bands
        
        State Variables:
        - order: Tracks pending orders to prevent multiple simultaneous orders
        """
        # === Technical Indicators ===
        self.bb = bt.ind.BollingerBands(
            period=self.p.period,
            devfactor=self.p.devfactor,
            plotname=f'BB({self.p.period},{self.p.devfactor})'
        )
        
        # === Additional Bollinger Band Analysis ===
        # Band width for volatility measurement
        self.bb_width = (self.bb.lines.top - self.bb.lines.bot) / self.bb.lines.mid * 100
        
        # Price position within bands (0 = lower band, 100 = upper band)
        self.bb_position = ((self.data.close - self.bb.lines.bot) / 
                           (self.bb.lines.top - self.bb.lines.bot)) * 100

        # === Internal State Management ===
        self.order = None  # Track pending orders
        
        # === Strategy Statistics ===
        self.trade_count = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        # === Risk Management ===
        self.max_position_size = 1000  # Maximum shares per position
        self.min_band_width = 2.0      # Minimum band width to trade (avoid low volatility)
        
        # === Logging Setup ===
        self.log_enabled = True

    def log(self, txt, dt=None):
        """
        Logging function for strategy events
        
        Args:
            txt (str): Message to log
            dt (datetime, optional): Timestamp for the log entry
        """
        if self.log_enabled:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}: {txt}')

    def next(self):
        """
        Main strategy logic executed on each bar
        
        This method contains the core mean reversion trading logic, evaluating
        Bollinger Band conditions and executing trades accordingly.
        
        Logic Flow:
        1. Check for pending orders (skip if any)
        2. Assess market volatility (band width)
        3. Evaluate entry conditions if no position
        4. Evaluate exit conditions if position exists
        5. Execute trades based on mean reversion signals
        
        Entry Signals:
        - Oversold: Price below lower Bollinger Band → BUY
        - Overbought: Price above upper Bollinger Band → SELL
        
        Exit Signals:
        - Mean Reversion: Price crosses back to middle band → CLOSE
        """
        # === Skip if order is pending ===
        if self.order:
            return

        # === Current market data ===
        current_close = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # === Bollinger Band values ===
        bb_upper = self.bb.lines.top[0]
        bb_middle = self.bb.lines.mid[0]
        bb_lower = self.bb.lines.bot[0]
        band_width = self.bb_width[0]
        band_position = self.bb_position[0]
        
        # === Volatility Filter ===
        # Skip trading if bands are too narrow (low volatility)
        if band_width < self.min_band_width:
            return

        # === Entry Logic (No Position) ===
        if not self.position:
            
            # === Oversold Condition (Mean Reversion Buy) ===
            if current_close < bb_lower:
                # Additional confirmation: ensure we're significantly below lower band
                deviation_percent = ((bb_lower - current_close) / bb_lower) * 100
                
                if deviation_percent > 0.1:  # At least 0.1% below lower band
                    size = self._calculate_position_size()
                    
                    if size > 0:
                        self.order = self.buy(size=size)
                        self.log(f'BUY SIGNAL (Oversold): Price: {current_close:.2f} < Lower BB: {bb_lower:.2f} | '
                               f'Band Position: {band_position:.1f}% | Width: {band_width:.2f}%')
            
            # === Overbought Condition (Mean Reversion Sell) ===
            elif current_close > bb_upper:
                # Additional confirmation: ensure we're significantly above upper band
                deviation_percent = ((current_close - bb_upper) / bb_upper) * 100
                
                if deviation_percent > 0.1:  # At least 0.1% above upper band
                    size = self._calculate_position_size()
                    
                    if size > 0:
                        self.order = self.sell(size=size)
                        self.log(f'SELL SIGNAL (Overbought): Price: {current_close:.2f} > Upper BB: {bb_upper:.2f} | '
                               f'Band Position: {band_position:.1f}% | Width: {band_width:.2f}%')

        # === Exit Logic (Position Exists) ===
        else:
            position_size = self.position.size
            entry_price = self.position.price
            current_pnl = (current_close - entry_price) * position_size
            
            # === Exit Long Position ===
            if position_size > 0:
                # Primary exit: price reverts to middle band
                if current_close >= bb_middle:
                    self.order = self.close()
                    self.log(f'EXIT LONG (Mean Reversion): Price: {current_close:.2f} >= Middle BB: {bb_middle:.2f} | '
                           f'PnL: {current_pnl:.2f} | Band Position: {band_position:.1f}%')
                
                # Secondary exit: stop loss if price continues down significantly
                elif current_close < bb_lower * 0.98:  # 2% below lower band
                    self.order = self.close()
                    self.log(f'EXIT LONG (Stop Loss): Price: {current_close:.2f} | Extended breakdown | PnL: {current_pnl:.2f}')
            
            # === Exit Short Position ===
            elif position_size < 0:
                # Primary exit: price reverts to middle band
                if current_close <= bb_middle:
                    self.order = self.close()
                    self.log(f'EXIT SHORT (Mean Reversion): Price: {current_close:.2f} <= Middle BB: {bb_middle:.2f} | '
                           f'PnL: {current_pnl:.2f} | Band Position: {band_position:.1f}%')
                
                # Secondary exit: stop loss if price continues up significantly
                elif current_close > bb_upper * 1.02:  # 2% above upper band
                    self.order = self.close()
                    self.log(f'EXIT SHORT (Stop Loss): Price: {current_close:.2f} | Extended breakout | PnL: {current_pnl:.2f}')

    def _calculate_position_size(self):
        """
        Calculate appropriate position size based on available capital and risk management
        
        Implements position sizing that considers:
        - Available cash
        - Maximum position size limits
        - Volatility-based sizing (wider bands = smaller positions)
        
        Returns:
            int: Number of shares/contracts to trade
        """
        # Base position size calculation
        available_cash = self.broker.getcash() * 0.90  # Use 90% of available cash
        current_price = self.data.close[0]
        
        # Calculate base position size
        base_size = int(available_cash / current_price) if current_price > 0 else 0
        
        # Apply maximum position size limit
        max_size = min(base_size, self.max_position_size)
        
        # Volatility-based position sizing
        # Reduce position size when bands are very wide (high volatility)
        band_width = self.bb_width[0]
        if band_width > 5.0:  # High volatility
            volatility_factor = 0.5
        elif band_width > 3.0:  # Medium volatility
            volatility_factor = 0.75
        else:  # Normal volatility
            volatility_factor = 1.0
        
        final_size = int(max_size * volatility_factor)
        
        # Ensure minimum viable position
        return max(1, final_size) if available_cash >= current_price else 0

    def notify_order(self, order):
        """
        Handle order status notifications
        
        This method is called whenever an order status changes, allowing us to
        track order execution and manage our internal state.
        
        Args:
            order: Backtrader order object with status information
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - no action needed
            return

        # === Order Completed ===
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED: Price: {order.executed.price:.2f}, Size: {order.executed.size}, '
                        f'Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED: Price: {order.executed.price:.2f}, Size: {order.executed.size}, '
                        f'Cost: {order.executed.value:.2f}, Commission: {order.executed.comm:.2f}')
            
            # Clear the order reference
            self.order = None

        # === Order Canceled/Margin/Rejected ===
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'ORDER FAILED: Status: {order.getstatusname()}')
            self.order = None

    def notify_trade(self, trade):
        """
        Handle trade completion notifications
        
        Called when a trade is closed, providing detailed trade statistics
        and performance metrics specific to mean reversion trading.
        
        Args:
            trade: Backtrader trade object with trade details
        """
        if not trade.isclosed:
            return

        # === Trade Statistics ===
        self.trade_count += 1
        pnl = trade.pnl
        pnl_percent = (pnl / abs(trade.value)) * 100 if trade.value != 0 else 0
        self.total_pnl += pnl
        
        if pnl > 0:
            self.winning_trades += 1
            
        # === Mean Reversion Specific Metrics ===
        trade_duration = trade.barlen
        avg_pnl = self.total_pnl / self.trade_count if self.trade_count > 0 else 0
        
        # === Log Trade Results ===
        self.log(f'TRADE CLOSED: PnL: {pnl:.2f} ({pnl_percent:.2f}%) | Duration: {trade_duration} bars | '
                f'Entry: {trade.price:.2f} | Exit: {trade.price + (pnl/trade.size):.2f}')
        
        # === Strategy Performance Summary ===
        if self.trade_count > 0:
            win_rate = (self.winning_trades / self.trade_count) * 100
            self.log(f'PERFORMANCE: Trades: {self.trade_count} | Win Rate: {win_rate:.1f}% | '
                    f'Avg PnL: {avg_pnl:.2f} | Total PnL: {self.total_pnl:.2f}')

    def stop(self):
        """
        Called when the strategy stops (end of backtest)
        
        Provides comprehensive final performance summary with mean reversion
        specific metrics and analysis.
        """
        final_value = self.broker.getvalue()
        self.log(f'MEAN REVERSION STRATEGY COMPLETED')
        self.log(f'=' * 50)
        self.log(f'Final Portfolio Value: {final_value:.2f}')
        self.log(f'Total Trades: {self.trade_count}')
        self.log(f'Total PnL: {self.total_pnl:.2f}')
        
        if self.trade_count > 0:
            win_rate = (self.winning_trades / self.trade_count) * 100
            avg_pnl = self.total_pnl / self.trade_count
            avg_winner = self.total_pnl / self.winning_trades if self.winning_trades > 0 else 0
            losing_trades = self.trade_count - self.winning_trades
            avg_loser = (self.total_pnl - (avg_winner * self.winning_trades)) / losing_trades if losing_trades > 0 else 0
            
            self.log(f'Win Rate: {win_rate:.1f}% ({self.winning_trades}/{self.trade_count})')
            self.log(f'Average PnL per Trade: {avg_pnl:.2f}')
            self.log(f'Average Winner: {avg_winner:.2f}')
            self.log(f'Average Loser: {avg_loser:.2f}')
            
            if avg_loser != 0:
                profit_factor = abs(avg_winner * self.winning_trades) / abs(avg_loser * losing_trades)
                self.log(f'Profit Factor: {profit_factor:.2f}')
        
        self.log(f'Strategy Parameters: Period: {self.p.period}, Deviation: {self.p.devfactor}')
        self.log(f'=' * 50)


# === Strategy Metadata ===
__strategy_name__ = "Mean Reversion Strategy"
__strategy_version__ = "1.0.0"
__strategy_description__ = "Bollinger Bands-based mean reversion strategy"
__strategy_author__ = "SentimentTrade Development Team"
__strategy_risk_level__ = "Medium-High"
__strategy_market_type__ = "Range-bound, Volatile Markets"
