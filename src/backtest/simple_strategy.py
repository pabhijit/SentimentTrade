"""
Simplified Backtest Strategy
A working strategy for testing the backtesting system without complex dependencies
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import backtrader as bt
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any

from backtest.sentiment_mocker import BacktestSentimentMocker

class SimpleTradingStrategy(bt.Strategy):
    """
    Simplified trading strategy for backtesting
    Uses basic technical indicators and mocked sentiment
    """
    
    params = (
        ('sentiment_style', 'realistic'),  # Sentiment generation style
        ('min_confidence', 0.7),  # Minimum confidence for trades
        ('rsi_period', 14),  # RSI period
        ('rsi_oversold', 30),  # RSI oversold threshold
        ('rsi_overbought', 70),  # RSI overbought threshold
        ('atr_period', 14),  # ATR period for stop loss
        ('atr_multiplier', 1.5),  # ATR multiplier for stop loss
        ('max_position_size', 0.95),  # Maximum position size
        ('trade_logging', True),  # Enable detailed trade logging
        ('sentiment_seed', 42),  # Seed for reproducible sentiment
    )
    
    def __init__(self):
        """Initialize the simple trading strategy"""
        
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
        
        # Technical indicators
        self.rsi = bt.ind.RSI(period=self.params.rsi_period)
        self.atr = bt.ind.ATR(period=self.params.atr_period)
        self.sma_short = bt.ind.SMA(period=20)
        self.sma_long = bt.ind.SMA(period=50)
        
        # Order management
        self.order = None
        self.stop_order = None
        
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
        self.entry_sentiment = None
        
        if self.params.trade_logging:
            print(f"🤖 Simple Trading Strategy initialized")
            print(f"   Sentiment Style: {self.params.sentiment_style}")
            print(f"   Min Confidence: {self.params.min_confidence:.1%}")
            print(f"   RSI Period: {self.params.rsi_period}")
    
    def next(self):
        """Execute strategy logic for each bar"""
        
        # Skip if we have pending orders
        if self.order:
            return
        
        # Generate mocked sentiment
        sentiment = self._generate_sentiment()
        
        # Generate trading signal
        signal_result = self._generate_signal(sentiment)
        
        # Store signal for analysis
        self.signal_history.append({
            'datetime': self.datas[0].datetime.datetime(0),
            'price': self.dataclose[0],
            'sentiment': sentiment,
            'signal': signal_result
        })
        
        # Execute trading logic based on signal
        self._execute_trading_logic(signal_result)
    
    def _generate_sentiment(self) -> float:
        """Generate mocked sentiment for current market conditions"""
        
        # Get current technical indicators for sentiment generation
        technical_indicators = {
            'rsi': self.rsi[0] if len(self.rsi) > 0 else 50,
            'ma_short': self.sma_short[0] if len(self.sma_short) > 0 else self.dataclose[0],
            'ma_long': self.sma_long[0] if len(self.sma_long) > 0 else self.dataclose[0],
            'price': self.dataclose[0],
            'atr': self.atr[0] if len(self.atr) > 0 else 1.0
        }
        
        # Generate mocked sentiment
        sentiment = self.sentiment_mocker.generate_sentiment(
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
        
        return sentiment
    
    def _generate_signal(self, sentiment: float) -> Dict[str, Any]:
        """Generate trading signal based on technical indicators and sentiment"""
        
        try:
            current_price = self.dataclose[0]
            rsi_value = self.rsi[0] if len(self.rsi) > 0 else 50
            atr_value = self.atr[0] if len(self.atr) > 0 else current_price * 0.02
            
            # Initialize signal
            action = 'HOLD'
            confidence = 0.0
            reasoning = "No clear signal"
            
            # RSI-based signals
            rsi_signal = 0.0
            if rsi_value < self.params.rsi_oversold:
                rsi_signal = 0.5  # Bullish
            elif rsi_value > self.params.rsi_overbought:
                rsi_signal = -0.5  # Bearish
            
            # Moving average signals
            ma_signal = 0.0
            if len(self.sma_short) > 0 and len(self.sma_long) > 0:
                if self.sma_short[0] > self.sma_long[0]:
                    ma_signal = 0.3  # Bullish
                else:
                    ma_signal = -0.3  # Bearish
            
            # Combine signals
            combined_signal = (rsi_signal + ma_signal + sentiment) / 3
            confidence = abs(combined_signal)
            
            # Determine action
            if combined_signal > 0.05 and confidence >= self.params.min_confidence:  # Lowered from 0.2
                action = 'BUY'
                reasoning = f"Bullish signal: RSI={rsi_value:.1f}, Sentiment={sentiment:.3f}"
            elif combined_signal < -0.05 and confidence >= self.params.min_confidence:  # Lowered from -0.2
                action = 'SELL'
                reasoning = f"Bearish signal: RSI={rsi_value:.1f}, Sentiment={sentiment:.3f}"
            else:
                reasoning = f"Weak signal: Combined={combined_signal:.3f}, Confidence={confidence:.3f}"
            
            # Calculate stop loss and target
            stop_loss = current_price - (atr_value * self.params.atr_multiplier) if action == 'BUY' else current_price + (atr_value * self.params.atr_multiplier)
            target_price = current_price + (atr_value * 2) if action == 'BUY' else current_price - (atr_value * 2)
            
            return {
                'symbol': 'BACKTEST',
                'action': action,
                'confidence': confidence,
                'current_price': current_price,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_reward_ratio': 2.0,  # Fixed 2:1 ratio
                'sentiment': sentiment,
                'rsi': rsi_value,
                'reasoning': reasoning
            }
            
        except Exception as e:
            if self.params.trade_logging:
                print(f"❌ Error generating signal: {e}")
            
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
                'reasoning': f'Signal generation failed: {str(e)}',
                'error': str(e)
            }
    
    def _execute_trading_logic(self, signal_result: Dict[str, Any]):
        """Execute trading logic based on signal"""
        
        action = signal_result.get('action', 'HOLD')
        confidence = signal_result.get('confidence', 0.0)
        current_price = signal_result.get('current_price', self.dataclose[0])
        
        # Check confidence threshold
        if confidence < self.params.min_confidence:
            return
        
        # Calculate position size
        portfolio_value = self.broker.getvalue()
        max_position_value = portfolio_value * self.params.max_position_size
        
        if current_price > 0 and max_position_value > 0:
            max_shares = int(max_position_value / current_price)
            position_size = max(1, max_shares)  # At least 1 share
        else:
            position_size = 1
        
        # Execute trades based on signal
        if not self.position:  # No current position
            
            if action == 'BUY' and position_size > 0:
                self._execute_buy_signal(signal_result, position_size)
                
            elif action == 'SELL' and position_size > 0:
                self._execute_sell_signal(signal_result, position_size)
        
        else:  # Have current position - manage existing position
            self._manage_existing_position(signal_result)
    
    def _execute_buy_signal(self, signal_result: Dict[str, Any], position_size: int):
        """Execute buy signal"""
        
        self.order = self.buy(size=position_size)
        self.entry_price = self.dataclose[0]
        self.entry_sentiment = signal_result.get('sentiment', 0.0)
        
        if self.params.trade_logging:
            print(f"📈 BUY Signal: {position_size} shares at ${self.dataclose[0]:.2f}")
            print(f"   Confidence: {signal_result.get('confidence', 0):.1%}")
            print(f"   Sentiment: {signal_result.get('sentiment', 0):.3f}")
            print(f"   RSI: {signal_result.get('rsi', 0):.1f}")
    
    def _execute_sell_signal(self, signal_result: Dict[str, Any], position_size: int):
        """Execute sell signal (short position)"""
        
        self.order = self.sell(size=position_size)
        self.entry_price = self.dataclose[0]
        self.entry_sentiment = signal_result.get('sentiment', 0.0)
        
        if self.params.trade_logging:
            print(f"📉 SELL Signal: {position_size} shares at ${self.dataclose[0]:.2f}")
            print(f"   Confidence: {signal_result.get('confidence', 0):.1%}")
            print(f"   Sentiment: {signal_result.get('sentiment', 0):.3f}")
            print(f"   RSI: {signal_result.get('rsi', 0):.1f}")
    
    def _manage_existing_position(self, signal_result: Dict[str, Any]):
        """Manage existing position based on new signal"""
        
        action = signal_result.get('action', 'HOLD')
        current_price = self.dataclose[0]
        
        # Simple exit logic - close position if opposite signal with high confidence
        if self.position.size > 0 and action == 'SELL':
            if signal_result.get('confidence', 0) >= 0.8:  # High confidence reversal
                self.close()
                if self.params.trade_logging:
                    print(f"🔄 Closing LONG position at ${current_price:.2f}")
        
        elif self.position.size < 0 and action == 'BUY':
            if signal_result.get('confidence', 0) >= 0.8:  # High confidence reversal
                self.close()
                if self.params.trade_logging:
                    print(f"🔄 Closing SHORT position at ${current_price:.2f}")
    
    def notify_order(self, order):
        """Handle order notifications"""
        
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.trade_logging:
                    print(f"✅ BUY Executed: {order.executed.size} shares at ${order.executed.price:.2f}")
            elif order.issell():
                if self.params.trade_logging:
                    print(f"✅ SELL Executed: {order.executed.size} shares at ${order.executed.price:.2f}")
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.params.trade_logging:
                print(f"❌ Order {order.status}: {order}")
        
        self.order = None
    
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
            'entry_sentiment': self.entry_sentiment
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
            print(f"\n📊 Simple Strategy Backtest Complete")
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
            'win_rate': (self.winning_trades / max(self.trade_count, 1) * 100),  # Avoid division by zero
            'total_pnl': self.total_pnl,
            'avg_pnl_per_trade': self.total_pnl / max(self.trade_count, 1),  # Avoid division by zero
            'signal_count': len(self.signal_history),
            'signals_per_trade': len(self.signal_history) / max(self.trade_count, 1)  # Avoid division by zero
        }
