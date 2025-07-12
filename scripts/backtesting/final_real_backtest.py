#!/usr/bin/env python3
"""
Final Real Data Backtest Analysis
Comprehensive 15-year backtest results with working strategy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import backtrader as bt
import pandas as pd
from datetime import datetime
from src.backtest.sentiment_mocker import BacktestSentimentMocker

class FinalTradingStrategy(bt.Strategy):
    """Final working trading strategy for real data analysis"""
    
    params = (
        ('min_confidence', 0.1),
        ('sentiment_style', 'realistic'),
        ('signal_threshold', 0.05),  # Lower threshold for more trades
    )
    
    def __init__(self):
        self.sentiment_mocker = BacktestSentimentMocker(
            sentiment_style=self.params.sentiment_style,
            seed=42
        )
        
        # Technical indicators
        self.rsi = bt.ind.RSI(period=14)
        self.sma_short = bt.ind.SMA(period=10)
        self.sma_long = bt.ind.SMA(period=20)
        
        # Trade tracking
        self.trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.signal_count = 0
        self.buy_signals = 0
        self.sell_signals = 0
        
    def next(self):
        """Strategy logic for each bar"""
        
        # Generate sentiment
        sentiment = self.sentiment_mocker.generate_sentiment(
            market_data={
                'close': self.data.close[0],
                'open': self.data.open[0],
                'high': self.data.high[0],
                'low': self.data.low[0],
                'volume': self.data.volume[0]
            },
            technical_indicators={
                'rsi': self.rsi[0] if len(self.rsi) > 0 else 50,
                'price': self.data.close[0]
            }
        )
        
        # Generate signal
        current_price = self.data.close[0]
        rsi_value = self.rsi[0] if len(self.rsi) > 0 else 50
        
        # RSI signals
        rsi_signal = 0.0
        if rsi_value < 30:
            rsi_signal = 0.5
        elif rsi_value > 70:
            rsi_signal = -0.5
        
        # MA signals
        ma_signal = 0.0
        if len(self.sma_short) > 0 and len(self.sma_long) > 0:
            if self.sma_short[0] > self.sma_long[0]:
                ma_signal = 0.3
            else:
                ma_signal = -0.3
        
        # Combine signals
        combined_signal = (rsi_signal + ma_signal + sentiment) / 3
        confidence = abs(combined_signal)
        
        # Count signals
        self.signal_count += 1
        
        # Determine action
        if combined_signal > self.params.signal_threshold and confidence >= self.params.min_confidence:
            action = 'BUY'
            self.buy_signals += 1
        elif combined_signal < -self.params.signal_threshold and confidence >= self.params.min_confidence:
            action = 'SELL'
            self.sell_signals += 1
        else:
            action = 'HOLD'
        
        # Execute trades
        if not self.position:  # No position
            if action == 'BUY':
                size = int(self.broker.getcash() * 0.95 / current_price)
                if size > 0:
                    self.buy(size=size)
        else:  # Have position
            if action == 'SELL':
                self.close()
    
    def notify_trade(self, trade):
        """Handle completed trades"""
        if trade.isclosed:
            self.trade_count += 1
            pnl = trade.pnl
            self.total_pnl += pnl
            
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
    
    def get_stats(self):
        """Get strategy statistics"""
        return {
            'total_trades': self.trade_count,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': (self.winning_trades / max(self.trade_count, 1)) * 100,
            'total_pnl': self.total_pnl,
            'avg_pnl_per_trade': self.total_pnl / max(self.trade_count, 1),
            'signal_count': self.signal_count,
            'buy_signals': self.buy_signals,
            'sell_signals': self.sell_signals,
            'signal_conversion_rate': (self.trade_count / max(self.buy_signals + self.sell_signals, 1)) * 100
        }

def run_comprehensive_backtest(symbol, sentiment_style='realistic', min_confidence=0.1):
    """Run comprehensive backtest analysis"""
    
    print(f"📊 Comprehensive Backtest: {symbol}")
    print(f"   Sentiment: {sentiment_style}, Confidence: {min_confidence:.1%}")
    print("=" * 70)
    
    # Setup
    cerebro = bt.Cerebro()
    
    cerebro.addstrategy(
        FinalTradingStrategy,
        sentiment_style=sentiment_style,
        min_confidence=min_confidence
    )
    
    # Load data
    data_file = f"data/real_data/{symbol}_15years.csv"
    
    try:
        # Check data
        df = pd.read_csv(data_file)
        print(f"📈 Data: {len(df)} trading days ({df.iloc[0]['datetime'][:10]} to {df.iloc[-1]['datetime'][:10]})")
        
        buy_hold_return = ((df.iloc[-1]['close'] / df.iloc[0]['close']) - 1) * 100
        initial_price = df.iloc[0]['close']
        final_price = df.iloc[-1]['close']
        
        print(f"💰 Buy & Hold: ${initial_price:.2f} → ${final_price:.2f} ({buy_hold_return:+.1f}%)")
        
        # Create data feed
        data = bt.feeds.GenericCSVData(
            dataname=data_file,
            dtformat='%Y-%m-%d %H:%M:%S.%f',
            datetime=0, open=1, high=2, low=3, close=4, volume=5,
            openinterest=-1, headers=True, timeframe=bt.TimeFrame.Days
        )
        
        cerebro.adddata(data)
        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(commission=0.001)
        
        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        # Run
        print(f"🔄 Running 15-year backtest...")
        initial_value = cerebro.broker.getvalue()
        
        start_time = datetime.now()
        results = cerebro.run()
        end_time = datetime.now()
        
        final_value = cerebro.broker.getvalue()
        strat = results[0]
        
        # Calculate results
        strategy_return = ((final_value / initial_value) - 1) * 100
        outperformance = strategy_return - buy_hold_return
        annualized_return = ((final_value / initial_value) ** (1/15) - 1) * 100
        
        # Get strategy stats
        stats = strat.get_stats()
        
        # Print comprehensive results
        print(f"\n📊 Performance Results:")
        print(f"   Initial Portfolio: ${initial_value:,.2f}")
        print(f"   Final Portfolio: ${final_value:,.2f}")
        print(f"   Strategy Return: {strategy_return:+.1f}%")
        print(f"   Buy & Hold Return: {buy_hold_return:+.1f}%")
        print(f"   Outperformance: {outperformance:+.1f}%")
        print(f"   Annualized Return: {annualized_return:+.1f}%")
        
        print(f"\n🎯 Trading Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Winning Trades: {stats['winning_trades']}")
        print(f"   Losing Trades: {stats['losing_trades']}")
        print(f"   Win Rate: {stats['win_rate']:.1f}%")
        print(f"   Average PnL/Trade: ${stats['avg_pnl_per_trade']:,.2f}")
        print(f"   Total PnL: ${stats['total_pnl']:,.2f}")
        
        print(f"\n📡 Signal Analysis:")
        print(f"   Total Signals: {stats['signal_count']:,}")
        print(f"   Buy Signals: {stats['buy_signals']:,}")
        print(f"   Sell Signals: {stats['sell_signals']:,}")
        print(f"   Signal Conversion: {stats['signal_conversion_rate']:.1f}%")
        
        # Analyzer results
        try:
            sharpe = strat.analyzers.sharpe.get_analysis()
            drawdown = strat.analyzers.drawdown.get_analysis()
            trades = strat.analyzers.trades.get_analysis()
            
            print(f"\n📈 Risk Metrics:")
            if sharpe and 'sharperatio' in sharpe:
                print(f"   Sharpe Ratio: {sharpe['sharperatio']:.3f}")
            
            if drawdown and 'max' in drawdown:
                max_dd = drawdown['max'].get('drawdown', 0)
                print(f"   Max Drawdown: {max_dd:.2f}%")
            
            if trades and 'total' in trades:
                total_closed = trades['total'].get('closed', 0)
                print(f"   Closed Trades: {total_closed}")
                
                if 'won' in trades and 'lost' in trades:
                    won_total = trades['won'].get('total', 0)
                    lost_total = trades['lost'].get('total', 0)
                    won_avg = trades['won'].get('pnl', {}).get('average', 0)
                    lost_avg = trades['lost'].get('pnl', {}).get('average', 0)
                    
                    print(f"   Average Win: ${won_avg:,.2f}")
                    print(f"   Average Loss: ${lost_avg:,.2f}")
                    
                    if lost_avg != 0:
                        profit_factor = abs(won_avg * won_total / (lost_avg * lost_total))
                        print(f"   Profit Factor: {profit_factor:.2f}")
        
        except Exception as e:
            print(f"⚠️ Some metrics unavailable: {e}")
        
        print(f"\n⏱️  Execution Time: {end_time - start_time}")
        
        return {
            'symbol': symbol,
            'strategy_return': strategy_return,
            'buy_hold_return': buy_hold_return,
            'outperformance': outperformance,
            'annualized_return': annualized_return,
            'final_value': final_value,
            'stats': stats,
            'sharpe_ratio': sharpe.get('sharperatio', 0) if sharpe else 0,
            'max_drawdown': drawdown['max'].get('drawdown', 0) if drawdown and 'max' in drawdown else 0
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def run_all_stocks_analysis():
    """Run comprehensive analysis on all stocks"""
    
    symbols = ['NVDA', 'AAPL', 'AMZN', 'MSFT', 'GOOGL']
    results = []
    
    print(f"🔬 15-Year Real Data Backtest Analysis")
    print(f"   AI Trading Strategy vs Buy & Hold")
    print("=" * 100)
    
    for symbol in symbols:
        print(f"\n{'='*20} {symbol} {'='*20}")
        result = run_comprehensive_backtest(symbol, 'realistic', 0.1)
        if result:
            results.append(result)
    
    # Final comparison table
    if results:
        print(f"\n📊 FINAL PERFORMANCE COMPARISON (15 Years)")
        print("=" * 120)
        print(f"{'Symbol':<8} {'Strategy':<12} {'Buy&Hold':<12} {'Outperf':<12} {'Annual':<10} {'Trades':<8} {'Win%':<8} {'Sharpe':<8}")
        print("-" * 120)
        
        for r in results:
            print(f"{r['symbol']:<8} {r['strategy_return']:>+10.1f}% "
                  f"{r['buy_hold_return']:>+10.1f}% {r['outperformance']:>+10.1f}% "
                  f"{r['annualized_return']:>+8.1f}% {r['stats']['total_trades']:>6} "
                  f"{r['stats']['win_rate']:>6.1f}% {r['sharpe_ratio']:>6.2f}")
        
        # Summary statistics
        avg_strategy = sum(r['strategy_return'] for r in results) / len(results)
        avg_buy_hold = sum(r['buy_hold_return'] for r in results) / len(results)
        avg_outperf = avg_strategy - avg_buy_hold
        
        print("-" * 120)
        print(f"{'AVERAGE':<8} {avg_strategy:>+10.1f}% {avg_buy_hold:>+10.1f}% {avg_outperf:>+10.1f}%")
        
        # Best performers
        best_strategy = max(results, key=lambda x: x['strategy_return'])
        best_outperform = max(results, key=lambda x: x['outperformance'])
        most_trades = max(results, key=lambda x: x['stats']['total_trades'])
        
        print(f"\n🏆 15-Year Performance Highlights:")
        print(f"   🥇 Best Strategy Return: {best_strategy['symbol']} ({best_strategy['strategy_return']:+.1f}%)")
        print(f"   🎯 Best Outperformance: {best_outperform['symbol']} ({best_outperform['outperformance']:+.1f}%)")
        print(f"   📈 Most Active Trading: {most_trades['symbol']} ({most_trades['stats']['total_trades']} trades)")
        
        # Calculate total portfolio value
        total_final_value = sum(r['final_value'] for r in results)
        total_initial_value = len(results) * 100000
        total_return = ((total_final_value / total_initial_value) - 1) * 100
        
        print(f"\n💰 Portfolio Summary:")
        print(f"   Total Initial Investment: ${total_initial_value:,.2f}")
        print(f"   Total Final Value: ${total_final_value:,.2f}")
        print(f"   Total Portfolio Return: {total_return:+.1f}%")
    
    return results

def main():
    """Main function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Final Real Data Backtest Analysis')
    parser.add_argument('--symbol', '-s', type=str, choices=['NVDA', 'AAPL', 'AMZN', 'MSFT', 'GOOGL'])
    parser.add_argument('--all', action='store_true', help='Analyze all symbols')
    
    args = parser.parse_args()
    
    if args.symbol:
        run_comprehensive_backtest(args.symbol)
    else:
        # Default: run all symbols
        run_all_stocks_analysis()

if __name__ == "__main__":
    main()
