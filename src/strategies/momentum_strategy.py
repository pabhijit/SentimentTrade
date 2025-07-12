#!/usr/bin/env python3
"""
Momentum Trading Strategy for SentimentTrade Platform

This module implements a dual moving average crossover momentum strategy that identifies
and trades trending market movements. The strategy uses fast and slow moving averages
to generate buy/sell signals based on momentum shifts.

Strategy Logic:
- BUY: When fast MA crosses above slow MA (bullish momentum)
- SELL: When fast MA crosses below slow MA (bearish momentum)
- EXIT: Reverse crossover signals exit existing positions

Author: SentimentTrade Development Team
Version: 1.0.0
Last Updated: July 2025
"""

import backtrader as bt


class MomentumStrategy(bt.Strategy):
    """
    Dual Moving Average Crossover Momentum Strategy
    
    A classic momentum strategy that uses two simple moving averages to identify
    trend changes and generate trading signals. This strategy is designed to
    capture sustained price movements in either direction.
    
    Strategy Characteristics:
    - Type: Trend Following / Momentum
    - Timeframe: Any (optimized for daily/hourly)
    - Market Conditions: Works best in trending markets
    - Risk Level: Medium (whipsaw risk in sideways markets)
    
    Signal Generation:
    1. Fast MA > Slow MA (and previous fast MA <= slow MA) → BUY
    2. Fast MA < Slow MA (and previous fast MA >= slow MA) → SELL
    3. Reverse crossover → EXIT position
    
    Parameters:
    - fast_ma (int): Period for fast moving average (default: 10)
    - slow_ma (int): Period for slow moving average (default: 30)
    
    Performance Characteristics:
    - Win Rate: Typically 40-60% (depends on market conditions)
    - Risk/Reward: Variable (trend-dependent)
    - Drawdown: Moderate during sideways markets
    - Best Markets: Strong trending environments
    
    Usage Example:
        # Create strategy with custom parameters
        strategy = MomentumStrategy()
        strategy.params.fast_ma = 12
        strategy.params.slow_ma = 26
        
        # Or use in backtrader cerebro
        cerebro.addstrategy(MomentumStrategy, fast_ma=12, slow_ma=26)
    """
    
    # === Strategy Parameters ===
    params = dict(
        fast_ma=10,     # Fast moving average period (shorter timeframe)
        slow_ma=30,     # Slow moving average period (longer timeframe)
    )

    def __init__(self):
        """
        Initialize the Momentum Strategy
        
        Sets up technical indicators and internal state variables required
        for momentum-based trading decisions.
        
        Indicators Created:
        - Fast SMA: Short-term trend identification
        - Slow SMA: Long-term trend identification
        
        State Variables:
        - order: Tracks pending orders to prevent multiple simultaneous orders
        """
        # === Technical Indicators ===
        self.ma_fast = bt.ind.SMA(
            period=self.p.fast_ma,
            plotname=f'Fast MA ({self.p.fast_ma})'
        )
        self.ma_slow = bt.ind.SMA(
            period=self.p.slow_ma,
            plotname=f'Slow MA ({self.p.slow_ma})'
        )
        
        # === Crossover Signal (for cleaner logic) ===
        self.crossover = bt.ind.CrossOver(self.ma_fast, self.ma_slow)

        # === Internal State Management ===
        self.order = None  # Track pending orders
        
        # === Strategy Statistics ===
        self.trade_count = 0
        self.winning_trades = 0
        
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
        
        This method is called for every new data point and contains the core
        trading logic for the momentum strategy.
        
        Logic Flow:
        1. Check for pending orders (skip if any)
        2. Evaluate entry conditions if no position
        3. Evaluate exit conditions if position exists
        4. Execute trades based on momentum signals
        
        Entry Signals:
        - Bullish Crossover: Fast MA crosses above Slow MA → BUY
        - Bearish Crossover: Fast MA crosses below Slow MA → SELL
        
        Exit Signals:
        - Reverse crossover closes existing positions
        """
        # === Skip if order is pending ===
        if self.order:
            return

        # === Current market data ===
        current_close = self.data.close[0]
        current_date = self.data.datetime.date(0)
        
        # === Entry Logic (No Position) ===
        if not self.position:
            
            # === Bullish Momentum Signal ===
            if self.crossover[0] > 0:  # Fast MA crossed above Slow MA
                # Calculate position size (could be enhanced with risk management)
                size = self._calculate_position_size()
                
                # Execute buy order
                self.order = self.buy(size=size)
                self.log(f'BUY SIGNAL: Fast MA ({self.ma_fast[0]:.2f}) > Slow MA ({self.ma_slow[0]:.2f}) | Price: {current_close:.2f}')
            
            # === Bearish Momentum Signal ===
            elif self.crossover[0] < 0:  # Fast MA crossed below Slow MA
                # Calculate position size for short
                size = self._calculate_position_size()
                
                # Execute sell order
                self.order = self.sell(size=size)
                self.log(f'SELL SIGNAL: Fast MA ({self.ma_fast[0]:.2f}) < Slow MA ({self.ma_slow[0]:.2f}) | Price: {current_close:.2f}')

        # === Exit Logic (Position Exists) ===
        else:
            position_size = self.position.size
            
            # === Exit Long Position ===
            if position_size > 0 and self.crossover[0] < 0:
                self.order = self.close()
                self.log(f'EXIT LONG: Bearish crossover | Price: {current_close:.2f} | Position: {position_size}')
            
            # === Exit Short Position ===
            elif position_size < 0 and self.crossover[0] > 0:
                self.order = self.close()
                self.log(f'EXIT SHORT: Bullish crossover | Price: {current_close:.2f} | Position: {position_size}')

    def _calculate_position_size(self):
        """
        Calculate appropriate position size based on available capital
        
        This is a basic implementation that uses a fixed percentage of available
        cash. Can be enhanced with more sophisticated risk management.
        
        Returns:
            int: Number of shares/contracts to trade
        """
        # Use 95% of available cash (leaving some buffer)
        available_cash = self.broker.getcash() * 0.95
        current_price = self.data.close[0]
        
        # Calculate maximum shares we can afford
        max_shares = int(available_cash / current_price)
        
        # Return at least 1 share if we have enough cash
        return max(1, max_shares) if available_cash >= current_price else 0

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
                self.log(f'BUY EXECUTED: Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: {order.executed.value:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED: Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: {order.executed.value:.2f}')
            
            # Clear the order reference
            self.order = None

        # === Order Canceled/Margin/Rejected ===
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'ORDER FAILED: Status: {order.getstatusname()}')
            self.order = None

    def notify_trade(self, trade):
        """
        Handle trade completion notifications
        
        Called when a trade is closed, providing trade statistics and P&L information.
        
        Args:
            trade: Backtrader trade object with trade details
        """
        if not trade.isclosed:
            return

        # === Trade Statistics ===
        self.trade_count += 1
        pnl = trade.pnl
        pnl_percent = (pnl / trade.value) * 100 if trade.value != 0 else 0
        
        if pnl > 0:
            self.winning_trades += 1
            
        # === Log Trade Results ===
        self.log(f'TRADE CLOSED: PnL: {pnl:.2f} ({pnl_percent:.2f}%) | Duration: {trade.barlen} bars')
        
        # === Strategy Performance Summary ===
        if self.trade_count > 0:
            win_rate = (self.winning_trades / self.trade_count) * 100
            self.log(f'PERFORMANCE: Trades: {self.trade_count} | Win Rate: {win_rate:.1f}% | Winners: {self.winning_trades}')

    def stop(self):
        """
        Called when the strategy stops (end of backtest)
        
        Provides final performance summary and cleanup.
        """
        final_value = self.broker.getvalue()
        self.log(f'STRATEGY COMPLETED')
        self.log(f'Final Portfolio Value: {final_value:.2f}')
        self.log(f'Total Trades: {self.trade_count}')
        
        if self.trade_count > 0:
            win_rate = (self.winning_trades / self.trade_count) * 100
            self.log(f'Final Win Rate: {win_rate:.1f}%')
        
        self.log(f'Strategy Parameters: Fast MA: {self.p.fast_ma}, Slow MA: {self.p.slow_ma}')


# === Strategy Metadata ===
__strategy_name__ = "Momentum Strategy"
__strategy_version__ = "1.0.0"
__strategy_description__ = "Dual moving average crossover momentum strategy"
__strategy_author__ = "SentimentTrade Development Team"
__strategy_risk_level__ = "Medium"
__strategy_market_type__ = "Trending Markets"
