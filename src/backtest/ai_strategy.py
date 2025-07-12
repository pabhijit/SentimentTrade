"""
AI-Integrated Backtest Strategy
Uses the actual SentimentTrade AI signal generator for backtesting
with mocked sentiment signals for historical data
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import backtrader as bt
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import our AI components
from ai_trade_signal import TradingSignalGenerator
from trading_config import get_trading_config
from technical_indicators import TechnicalIndicators
from database import UserPreferences
from backtest.sentiment_mocker import BacktestSentimentMocker

class AITradingStrategy(bt.Strategy):
    """
    Backtest strategy that uses the actual SentimentTrade AI signal generator
    """
    
    params = (
        ('user_preferences', None),  # UserPreferences object
        ('sentiment_style', 'realistic'),  # Sentiment generation style
        ('min_confidence', 0.7),  # Minimum confidence for trades
        ('max_position_size', 0.95),  # Maximum position size (95% of portfolio)
        ('enable_stop_loss', True),  # Enable stop loss orders
        ('enable_take_profit', True),  # Enable take profit orders
        ('trade_logging', True),  # Enable detailed trade logging
        ('sentiment_seed', 42),  # Seed for reproducible sentiment
    )
    
    def __init__(self):
        """Initialize the AI trading strategy"""
        
        # Initialize AI signal generator
        self.signal_generator = TradingSignalGenerator(self.params.user_preferences)
        self.config = get_trading_config(self.params.user_preferences)
        
        # Initialize sentiment mocker
        self.sentiment_mocker = BacktestSentimentMocker(
            sentiment_style=self.params.sentiment_style,
            seed=self.params.sentiment_seed
        )
        
        # Data references
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.datavolume = self.datas[0].volume
        
        # Technical indicators for sentiment generation
        self.rsi = bt.ind.RSI(period=self.config.rsi_period)
        self.macd = bt.ind.MACD(
            period_me1=self.config.macd_fast,
            period_me2=self.config.macd_slow,
            period_signal=self.config.macd_signal
        )
        self.atr = bt.ind.ATR(period=self.config.atr_period)
        self.sma_short = bt.ind.SMA(period=20)
        self.sma_long = bt.ind.SMA(period=50)
        
        # Order management
        self.order = None
        self.stop_order = None
        self.limit_order = None
        
        # Trade tracking
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        
        # Signal history for analysis
        self.signal_history = []
        self.trade_history = []
        
        # Position tracking
        self.entry_price = None
        self.entry_signal = None
        
        if self.params.trade_logging:
            print(f"🤖 AI Trading Strategy initialized")
            print(f"   Strategy: {self.signal_generator.strategy_name}")
            print(f"   Sentiment Style: {self.params.sentiment_style}")
            print(f"   Min Confidence: {self.params.min_confidence:.1%}")
    
    def next(self):
        """Execute strategy logic for each bar"""
        
        # Skip if we have pending orders
        if self.order:
            return
        
        # Get current market data
        current_data = self._get_current_market_data()
        
        # Generate AI signal
        signal_result = self._generate_ai_signal(current_data)
        
        # Store signal for analysis
        self.signal_history.append({
            'datetime': self.datas[0].datetime.datetime(0),
            'price': self.dataclose[0],
            'signal': signal_result
        })
        
        # Execute trading logic based on signal
        self._execute_trading_logic(signal_result)
    
    def _get_current_market_data(self) -> Dict[str, Any]:
        """Get current market data in the format expected by AI signal generator"""
        
        # Get recent price history (last 60 bars for technical analysis)
        lookback = min(60, len(self.datas[0]))
        
        close_prices = [self.dataclose[-i] for i in range(lookback-1, -1, -1)]
        high_prices = [self.datahigh[-i] for i in range(lookback-1, -1, -1)]
        low_prices = [self.datalow[-i] for i in range(lookback-1, -1, -1)]
        open_prices = [self.dataopen[-i] for i in range(lookback-1, -1, -1)]
        volumes = [self.datavolume[-i] for i in range(lookback-1, -1, -1)]
        
        return {
            'close': close_prices,
            'high': high_prices,
            'low': low_prices,
            'open': open_prices,
            'volume': volumes
        }
    
    def _generate_ai_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI trading signal with mocked sentiment"""
        
        try:
            # Get current technical indicators for sentiment generation
            technical_indicators = {
                'rsi': self.rsi[0],
                'macd': self.macd.macd[0],
                'macd_signal': self.macd.signal[0],
                'ma_short': self.sma_short[0],
                'ma_long': self.sma_long[0],
                'price': self.dataclose[0],
                'atr': self.atr[0]
            }
            
            # Generate mocked sentiment
            mocked_sentiment = self.sentiment_mocker.generate_sentiment(
                market_data={
                    'close': self.dataclose[0],
                    'open': self.dataopen[0],
                    'high': self.datahigh[0],
                    'low': self.datalow[0],
                    'volume': self.datavolume[0]
                },
                technical_indicators=technical_indicators,
                timestamp=self.datas[0].datetime.datetime(0)
            )
            
            # Use the strategy factory to analyze with mocked sentiment
            from strategies.strategy_factory import analyze_symbol
            
            signal_result = analyze_symbol(
                strategy_name=self.signal_generator.strategy_name,
                symbol='BACKTEST',  # Placeholder symbol for backtesting
                market_data=market_data,
                sentiment_score=mocked_sentiment,
                user_preferences=self.params.user_preferences
            )
            
            # Add mocked sentiment to result
            signal_result['mocked_sentiment'] = mocked_sentiment
            
            return signal_result
            
        except Exception as e:
            if self.params.trade_logging:
                print(f"❌ Error generating AI signal: {e}")
            
            # Return neutral signal on error
            return {
                'symbol': 'BACKTEST',
                'action': 'HOLD',
                'confidence': 0.0,
                'current_price': self.dataclose[0],
                'entry_price': self.dataclose[0],
                'stop_loss': self.dataclose[0],
                'target_price': self.dataclose[0],
                'risk_reward_ratio': 0.0,
                'sentiment': 0.0,
                'mocked_sentiment': 0.0,
                'reasoning': f'Signal generation failed: {str(e)}',
                'error': str(e)
            }
    
    def _execute_trading_logic(self, signal_result: Dict[str, Any]):
        """Execute trading logic based on AI signal"""
        
        action = signal_result.get('action', 'HOLD')
        confidence = signal_result.get('confidence', 0.0)
        current_price = signal_result.get('current_price', self.dataclose[0])
        stop_loss = signal_result.get('stop_loss', 0.0)
        target_price = signal_result.get('target_price', 0.0)
        
        # Check confidence threshold
        if confidence < self.params.min_confidence:
            return
        
        # Calculate position size based on confidence and risk management
        portfolio_value = self.broker.getvalue()
        max_position_value = portfolio_value * self.params.max_position_size
        
        if current_price > 0:
            max_shares = int(max_position_value / current_price)
            
            # Scale position size by confidence
            position_size = int(max_shares * confidence)
            position_size = max(1, position_size)  # At least 1 share
        else:
            position_size = 1
        
        # Execute trades based on signal
        if not self.position:  # No current position
            
            if action == 'BUY' and position_size > 0:
                self._execute_buy_signal(signal_result, position_size)
                
            elif action == 'SELL' and position_size > 0:
                self._execute_sell_signal(signal_result, position_size)
                
        else:  # Have current position
            self._manage_existing_position(signal_result)
    
    def _execute_buy_signal(self, signal_result: Dict[str, Any], position_size: int):
        """Execute buy signal"""
        
        self.order = self.buy(size=position_size)
        self.entry_price = self.dataclose[0]
        self.entry_signal = signal_result
        
        if self.params.trade_logging:
            print(f"📈 BUY Signal: {position_size} shares at ${self.dataclose[0]:.2f}")
            print(f"   Confidence: {signal_result.get('confidence', 0):.1%}")
            print(f"   Sentiment: {signal_result.get('mocked_sentiment', 0):.3f}")
            print(f"   Target: ${signal_result.get('target_price', 0):.2f}")
            print(f"   Stop Loss: ${signal_result.get('stop_loss', 0):.2f}")
    
    def _execute_sell_signal(self, signal_result: Dict[str, Any], position_size: int):
        """Execute sell signal (short position)"""
        
        self.order = self.sell(size=position_size)
        self.entry_price = self.dataclose[0]
        self.entry_signal = signal_result
        
        if self.params.trade_logging:
            print(f"📉 SELL Signal: {position_size} shares at ${self.dataclose[0]:.2f}")
            print(f"   Confidence: {signal_result.get('confidence', 0):.1%}")
            print(f"   Sentiment: {signal_result.get('mocked_sentiment', 0):.3f}")
            print(f"   Target: ${signal_result.get('target_price', 0):.2f}")
            print(f"   Stop Loss: ${signal_result.get('stop_loss', 0):.2f}")
    
    def _manage_existing_position(self, signal_result: Dict[str, Any]):
        """Manage existing position based on new signal"""
        
        action = signal_result.get('action', 'HOLD')
        current_price = self.dataclose[0]
        
        # Check for position reversal signals
        if self.position.size > 0 and action == 'SELL':
            # Long position, got sell signal - close and reverse
            if signal_result.get('confidence', 0) >= self.params.min_confidence:
                self.close()
                if self.params.trade_logging:
                    print(f"🔄 Reversing position: LONG → SHORT at ${current_price:.2f}")
        
        elif self.position.size < 0 and action == 'BUY':
            # Short position, got buy signal - close and reverse
            if signal_result.get('confidence', 0) >= self.params.min_confidence:
                self.close()
                if self.params.trade_logging:
                    print(f"🔄 Reversing position: SHORT → LONG at ${current_price:.2f}")
    
    def notify_order(self, order):
        """Handle order notifications"""
        
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self._handle_buy_completed(order)
            elif order.issell():
                self._handle_sell_completed(order)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.params.trade_logging:
                print(f"❌ Order {order.status}: {order}")
        
        self.order = None
    
    def _handle_buy_completed(self, order):
        """Handle completed buy order"""
        
        if self.params.trade_logging:
            print(f"✅ BUY Executed: {order.executed.size} shares at ${order.executed.price:.2f}")
        
        # Set stop loss and take profit if enabled
        if self.entry_signal and self.params.enable_stop_loss:
            stop_price = self.entry_signal.get('stop_loss', 0)
            if stop_price > 0:
                self.stop_order = self.sell(
                    size=order.executed.size,
                    exectype=bt.Order.Stop,
                    price=stop_price
                )
        
        if self.entry_signal and self.params.enable_take_profit:
            target_price = self.entry_signal.get('target_price', 0)
            if target_price > 0:
                self.limit_order = self.sell(
                    size=order.executed.size,
                    exectype=bt.Order.Limit,
                    price=target_price
                )
    
    def _handle_sell_completed(self, order):
        """Handle completed sell order"""
        
        if self.params.trade_logging:
            print(f"✅ SELL Executed: {order.executed.size} shares at ${order.executed.price:.2f}")
        
        # Set stop loss and take profit for short positions if enabled
        if self.entry_signal and self.params.enable_stop_loss:
            stop_price = self.entry_signal.get('stop_loss', 0)
            if stop_price > 0:
                self.stop_order = self.buy(
                    size=order.executed.size,
                    exectype=bt.Order.Stop,
                    price=stop_price
                )
        
        if self.entry_signal and self.params.enable_take_profit:
            target_price = self.entry_signal.get('target_price', 0)
            if target_price > 0:
                self.limit_order = self.buy(
                    size=order.executed.size,
                    exectype=bt.Order.Limit,
                    price=target_price
                )
    
    def notify_trade(self, trade):
        """Handle trade notifications"""
        
        if not trade.isclosed:
            return
        
        self.trade_count += 1
        pnl = trade.pnl
        self.total_pnl += pnl
        
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Store trade details
        trade_record = {
            'trade_number': self.trade_count,
            'entry_date': bt.num2date(trade.dtopen),
            'exit_date': bt.num2date(trade.dtclose),
            'entry_price': trade.price,
            'exit_price': trade.price + trade.pnl / trade.size,
            'size': trade.size,
            'pnl': pnl,
            'pnl_percent': (pnl / (trade.price * abs(trade.size))) * 100,
            'duration': trade.barlen,
            'entry_signal': self.entry_signal
        }
        
        self.trade_history.append(trade_record)
        
        if self.params.trade_logging:
            print(f"💰 Trade #{self.trade_count} Closed:")
            print(f"   PnL: ${pnl:.2f} ({trade_record['pnl_percent']:.2f}%)")
            print(f"   Duration: {trade.barlen} bars")
            print(f"   Entry: ${trade.price:.2f} → Exit: ${trade_record['exit_price']:.2f}")
    
    def stop(self):
        """Called when backtest ends"""
        
        if self.params.trade_logging:
            print(f"\n📊 AI Strategy Backtest Complete")
            print(f"   Total Trades: {self.trade_count}")
            print(f"   Winning Trades: {self.winning_trades}")
            print(f"   Losing Trades: {self.losing_trades}")
            if self.trade_count > 0:
                win_rate = (self.winning_trades / self.trade_count) * 100
                print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Total PnL: ${self.total_pnl:.2f}")
    
    def get_signal_history(self) -> List[Dict]:
        """Get history of all generated signals"""
        return self.signal_history
    
    def get_trade_history(self) -> List[Dict]:
        """Get history of all completed trades"""
        return self.trade_history
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """Get comprehensive strategy statistics"""
        
        return {
            'total_trades': self.trade_count,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': (self.winning_trades / self.trade_count * 100) if self.trade_count > 0 else 0,
            'total_pnl': self.total_pnl,
            'avg_pnl_per_trade': self.total_pnl / self.trade_count if self.trade_count > 0 else 0,
            'signal_count': len(self.signal_history),
            'signals_per_trade': len(self.signal_history) / self.trade_count if self.trade_count > 0 else 0
        }
