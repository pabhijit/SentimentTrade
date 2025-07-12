#!/usr/bin/env python3
"""
Real Data Backtest Runner
Comprehensive backtesting with 15 years of real stock data
"""

import sys
import os
from pathlib import Path
import argparse
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import backtrader as bt
from src.backtest.simple_strategy import SimpleTradingStrategy

class RealDataBacktestRunner:
    """Comprehensive backtest runner for real stock data"""
    
    def __init__(self):
        self.cerebro = None
        self.results = None
        self.strategy_instance = None
        
    def setup_backtest(self, 
                      symbol: str,
                      initial_cash: float = 100000.0,
                      commission: float = 0.001,
                      sentiment_style: str = 'realistic',
                      min_confidence: float = 0.3,
                      start_date: str = None,
                      end_date: str = None):
        """Setup backtest environment for real data"""
        
        data_file = f"data/real_data/{symbol}_15years.csv"
        
        print(f"🚀 Setting up Real Data Backtest")
        print(f"   Symbol: {symbol}")
        print(f"   Data File: {data_file}")
        print(f"   Initial Cash: ${initial_cash:,.2f}")
        print(f"   Commission: {commission:.3%}")
        print(f"   Sentiment Style: {sentiment_style}")
        print(f"   Min Confidence: {min_confidence:.1%}")
        
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        # Initialize Cerebro
        self.cerebro = bt.Cerebro()
        
        # Add strategy with real data parameters
        self.cerebro.addstrategy(
            SimpleTradingStrategy,
            sentiment_style=sentiment_style,
            min_confidence=min_confidence,
            trade_logging=False,  # Disable for long backtests
            rsi_period=14,
            atr_period=14,
            atr_multiplier=2.0,  # More conservative for real data
            max_position_size=0.95
        )
        
        # Load and add data
        self._load_real_data(data_file, start_date, end_date)
        
        # Set broker parameters
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)
        
        # Add analyzers
        self._add_analyzers()
        
        print(f"✅ Real data backtest setup complete")
        
    def _load_real_data(self, data_file: str, start_date: str = None, end_date: str = None):
        """Load real stock data with optional date filtering"""
        
        try:
            # Read CSV to check format
            df = pd.read_csv(data_file)
            
            # Filter by date range if specified
            if start_date or end_date:
                df['date'] = pd.to_datetime(df['datetime'])
                if start_date:
                    df = df[df['date'] >= start_date]
                if end_date:
                    df = df[df['date'] <= end_date]
            
            print(f"📊 Loaded {len(df)} trading days")
            if len(df) > 0:
                print(f"   Date range: {df.iloc[0]['datetime'][:10]} to {df.iloc[-1]['datetime'][:10]}")
                print(f"   Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
                print(f"   Total return (buy & hold): {((df.iloc[-1]['close'] / df.iloc[0]['close']) - 1) * 100:+.1f}%")
            
            # Create Backtrader data feed
            data = bt.feeds.GenericCSVData(
                dataname=data_file,
                dtformat='%Y-%m-%d %H:%M:%S.%f',
                datetime=0,
                open=1,
                high=2,
                low=3,
                close=4,
                volume=5,
                openinterest=-1,
                headers=True,
                timeframe=bt.TimeFrame.Days,
                compression=1,
                fromdate=pd.to_datetime(start_date) if start_date else None,
                todate=pd.to_datetime(end_date) if end_date else None
            )
            
            self.cerebro.adddata(data)
            print(f"✅ Data feed added to backtest engine")
            
        except Exception as e:
            print(f"❌ Error loading real data: {e}")
            raise
    
    def _add_analyzers(self):
        """Add comprehensive performance analyzers"""
        
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
        self.cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
        self.cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual')
        
        print(f"✅ Performance analyzers added")
    
    def run_backtest(self) -> Dict[str, Any]:
        """Run the backtest and return comprehensive results"""
        
        if not self.cerebro:
            raise ValueError("Backtest not setup. Call setup_backtest() first.")
        
        print(f"\n🚀 Starting Real Data Backtest")
        print(f"   Starting Portfolio Value: ${self.cerebro.broker.getvalue():,.2f}")
        
        # Run backtest
        start_time = datetime.now()
        self.results = self.cerebro.run()
        end_time = datetime.now()
        
        self.strategy_instance = self.results[0]
        
        final_value = self.cerebro.broker.getvalue()
        initial_value = 100000.0  # Default
        total_return = ((final_value / initial_value) - 1) * 100
        
        print(f"   Final Portfolio Value: ${final_value:,.2f}")
        print(f"   Total Return: {total_return:+.2f}%")
        print(f"   Backtest Duration: {end_time - start_time}")
        
        # Extract and return results
        return self._extract_comprehensive_results()
    
    def _extract_comprehensive_results(self) -> Dict[str, Any]:
        """Extract comprehensive results from real data backtest"""
        
        if not self.results or not self.strategy_instance:
            return {}
        
        strat = self.strategy_instance
        
        # Basic performance metrics
        final_value = self.cerebro.broker.getvalue()
        initial_value = 100000.0
        total_return = ((final_value / initial_value) - 1) * 100
        
        # Analyzer results
        analyzers = {}
        try:
            analyzers['sharpe'] = strat.analyzers.sharpe.get_analysis()
            analyzers['drawdown'] = strat.analyzers.drawdown.get_analysis()
            analyzers['trades'] = strat.analyzers.trades.get_analysis()
            analyzers['returns'] = strat.analyzers.returns.get_analysis()
            analyzers['sqn'] = strat.analyzers.sqn.get_analysis()
            analyzers['vwr'] = strat.analyzers.vwr.get_analysis()
            analyzers['annual'] = strat.analyzers.annual.get_analysis()
        except Exception as e:
            print(f"⚠️ Warning: Some analyzers failed: {e}")
        
        # Strategy-specific results
        strategy_stats = strat.get_strategy_stats()
        signal_history = strat.get_signal_history()
        trade_history = strat.get_trade_history()
        
        # Calculate additional metrics
        additional_metrics = self._calculate_additional_metrics(
            initial_value, final_value, trade_history, signal_history
        )
        
        # Compile comprehensive results
        results = {
            'performance': {
                'initial_value': initial_value,
                'final_value': final_value,
                'total_return_pct': total_return,
                'total_return_abs': final_value - initial_value,
                'annualized_return': self._calculate_annualized_return(total_return, len(signal_history)),
                'max_drawdown_pct': analyzers.get('drawdown', {}).get('max', {}).get('drawdown', 0),
                'sharpe_ratio': analyzers.get('sharpe', {}).get('sharperatio', 0)
            },
            'analyzers': analyzers,
            'strategy_stats': strategy_stats,
            'signal_history': signal_history[-100:] if len(signal_history) > 100 else signal_history,  # Last 100 for size
            'trade_history': trade_history,
            'additional_metrics': additional_metrics,
            'backtest_info': {
                'strategy': 'Real Data Trading Strategy',
                'data_points': len(signal_history),
                'backtest_date': datetime.now().isoformat(),
                'trading_days': len(signal_history)
            }
        }
        
        return results
    
    def _calculate_additional_metrics(self, initial_value, final_value, trade_history, signal_history):
        """Calculate additional performance metrics"""
        
        metrics = {}
        
        if trade_history:
            # Trade metrics
            profits = [t['pnl'] for t in trade_history if t['pnl'] > 0]
            losses = [t['pnl'] for t in trade_history if t['pnl'] < 0]
            
            metrics['avg_win'] = sum(profits) / len(profits) if profits else 0
            metrics['avg_loss'] = sum(losses) / len(losses) if losses else 0
            metrics['profit_factor'] = abs(sum(profits) / sum(losses)) if losses else float('inf')
            metrics['largest_win'] = max(profits) if profits else 0
            metrics['largest_loss'] = min(losses) if losses else 0
            
            # Duration metrics
            durations = [t['duration'] for t in trade_history]
            metrics['avg_trade_duration'] = sum(durations) / len(durations) if durations else 0
            metrics['max_trade_duration'] = max(durations) if durations else 0
        
        if signal_history:
            # Signal metrics
            actionable_signals = [s for s in signal_history if s['signal']['action'] != 'HOLD']
            if actionable_signals:
                confidences = [s['signal']['confidence'] for s in actionable_signals]
                sentiments = [s['sentiment'] for s in actionable_signals]
                
                metrics['avg_signal_confidence'] = sum(confidences) / len(confidences)
                metrics['avg_sentiment'] = sum(sentiments) / len(sentiments)
                metrics['signal_conversion_rate'] = len(trade_history) / len(actionable_signals) if actionable_signals else 0
        
        # Time-based metrics
        if signal_history:
            trading_days = len(signal_history)
            years = trading_days / 252  # Approximate trading days per year
            metrics['trading_years'] = years
            metrics['trades_per_year'] = len(trade_history) / years if years > 0 else 0
        
        return metrics
    
    def _calculate_annualized_return(self, total_return_pct, trading_days):
        """Calculate annualized return"""
        if trading_days <= 0:
            return 0
        
        years = trading_days / 252  # Approximate trading days per year
        if years <= 0:
            return 0
        
        return ((1 + total_return_pct / 100) ** (1 / years) - 1) * 100
    
    def print_comprehensive_results(self, results: Dict[str, Any], symbol: str):
        """Print comprehensive backtest results"""
        
        print(f"\n📊 {symbol} - Real Data Backtest Results (15 Years)")
        print("=" * 80)
        
        # Performance Summary
        perf = results.get('performance', {})
        print(f"💰 Performance Summary:")
        print(f"   Initial Value: ${perf.get('initial_value', 0):,.2f}")
        print(f"   Final Value: ${perf.get('final_value', 0):,.2f}")
        print(f"   Total Return: {perf.get('total_return_pct', 0):+.2f}%")
        print(f"   Annualized Return: {perf.get('annualized_return', 0):+.2f}%")
        print(f"   Absolute Gain: ${perf.get('total_return_abs', 0):,.2f}")
        
        # Risk Metrics
        print(f"\n📉 Risk Metrics:")
        print(f"   Max Drawdown: {perf.get('max_drawdown_pct', 0):.2f}%")
        print(f"   Sharpe Ratio: {perf.get('sharpe_ratio', 0):.3f}")
        
        # Trading Statistics
        stats = results.get('strategy_stats', {})
        print(f"\n🎯 Trading Statistics:")
        print(f"   Total Trades: {stats.get('total_trades', 0)}")
        print(f"   Winning Trades: {stats.get('winning_trades', 0)}")
        print(f"   Losing Trades: {stats.get('losing_trades', 0)}")
        print(f"   Win Rate: {stats.get('win_rate', 0):.1f}%")
        print(f"   Average PnL per Trade: ${stats.get('avg_pnl_per_trade', 0):,.2f}")
        
        # Additional Metrics
        additional = results.get('additional_metrics', {})
        if additional:
            print(f"\n📈 Advanced Metrics:")
            print(f"   Average Win: ${additional.get('avg_win', 0):,.2f}")
            print(f"   Average Loss: ${additional.get('avg_loss', 0):,.2f}")
            print(f"   Profit Factor: {additional.get('profit_factor', 0):.2f}")
            print(f"   Largest Win: ${additional.get('largest_win', 0):,.2f}")
            print(f"   Largest Loss: ${additional.get('largest_loss', 0):,.2f}")
            print(f"   Avg Trade Duration: {additional.get('avg_trade_duration', 0):.1f} days")
            print(f"   Trades per Year: {additional.get('trades_per_year', 0):.1f}")
        
        # Signal Analysis
        print(f"\n🎯 Signal Analysis:")
        print(f"   Total Signals Generated: {stats.get('signal_count', 0)}")
        if additional:
            print(f"   Average Signal Confidence: {additional.get('avg_signal_confidence', 0):.1%}")
            print(f"   Average Sentiment: {additional.get('avg_sentiment', 0):+.3f}")
            print(f"   Signal Conversion Rate: {additional.get('signal_conversion_rate', 0):.1%}")
        
        # Annual Returns
        analyzers = results.get('analyzers', {})
        annual_returns = analyzers.get('annual', {})
        if annual_returns:
            print(f"\n📅 Annual Returns:")
            for year, return_pct in sorted(annual_returns.items()):
                if isinstance(return_pct, (int, float)):
                    print(f"   {year}: {return_pct:+.1f}%")
        
        # System Quality
        sqn = analyzers.get('sqn', {}).get('sqn', 0)
        if sqn:
            print(f"\n🎲 System Quality:")
            print(f"   SQN Score: {sqn:.2f}")
            if sqn >= 3.0:
                quality = "Excellent"
            elif sqn >= 2.0:
                quality = "Good"
            elif sqn >= 1.0:
                quality = "Average"
            else:
                quality = "Poor"
            print(f"   Quality Rating: {quality}")
    
    def save_results(self, results: Dict[str, Any], symbol: str, sentiment_style: str):
        """Save comprehensive results to JSON file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"real_backtest_{symbol}_{sentiment_style}_{timestamp}.json"
        
        try:
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=json_serializer)
            
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def run_multi_symbol_analysis(symbols, sentiment_style='realistic', min_confidence=0.3):
    """Run backtest analysis across multiple symbols"""
    
    print(f"\n🔬 Multi-Symbol Analysis")
    print(f"   Symbols: {', '.join(symbols)}")
    print(f"   Sentiment Style: {sentiment_style}")
    print(f"   Min Confidence: {min_confidence:.1%}")
    print("=" * 80)
    
    results_summary = []
    
    for symbol in symbols:
        print(f"\n📈 Analyzing {symbol}...")
        
        try:
            runner = RealDataBacktestRunner()
            runner.setup_backtest(
                symbol=symbol,
                sentiment_style=sentiment_style,
                min_confidence=min_confidence
            )
            
            results = runner.run_backtest()
            
            # Extract key metrics for comparison
            perf = results.get('performance', {})
            stats = results.get('strategy_stats', {})
            
            summary = {
                'symbol': symbol,
                'total_return': perf.get('total_return_pct', 0),
                'annualized_return': perf.get('annualized_return', 0),
                'max_drawdown': perf.get('max_drawdown_pct', 0),
                'sharpe_ratio': perf.get('sharpe_ratio', 0),
                'total_trades': stats.get('total_trades', 0),
                'win_rate': stats.get('win_rate', 0),
                'avg_pnl_per_trade': stats.get('avg_pnl_per_trade', 0)
            }
            
            results_summary.append(summary)
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            results_summary.append({
                'symbol': symbol,
                'error': str(e)
            })
    
    # Print comparison table
    print(f"\n📊 Multi-Symbol Comparison")
    print("=" * 100)
    print(f"{'Symbol':<8} {'Total Return':<12} {'Annual Return':<13} {'Max DD':<8} {'Sharpe':<8} {'Trades':<8} {'Win Rate':<9}")
    print("-" * 100)
    
    for summary in results_summary:
        if 'error' not in summary:
            print(f"{summary['symbol']:<8} {summary['total_return']:>+10.1f}% "
                  f"{summary['annualized_return']:>+11.1f}% {summary['max_drawdown']:>6.1f}% "
                  f"{summary['sharpe_ratio']:>6.2f} {summary['total_trades']:>6} "
                  f"{summary['win_rate']:>7.1f}%")
        else:
            print(f"{summary['symbol']:<8} ERROR: {summary['error']}")
    
    return results_summary

def main():
    """Main backtest runner function"""
    
    parser = argparse.ArgumentParser(description='Real Data Backtest Runner (15 Years)')
    
    parser.add_argument('--symbol', '-s', type=str, default='NVDA',
                       choices=['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN'],
                       help='Stock symbol to backtest')
    parser.add_argument('--all', action='store_true',
                       help='Run backtest on all symbols')
    parser.add_argument('--cash', '-c', type=float, default=100000.0,
                       help='Initial cash amount')
    parser.add_argument('--commission', type=float, default=0.001,
                       help='Commission rate')
    parser.add_argument('--sentiment', type=str, default='realistic',
                       choices=['realistic', 'contrarian', 'momentum', 'random', 'neutral'],
                       help='Sentiment generation style')
    parser.add_argument('--confidence', type=float, default=0.3,
                       help='Minimum confidence threshold for trades')
    parser.add_argument('--start-date', type=str,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--save', action='store_true',
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    try:
        if args.all:
            # Run multi-symbol analysis
            symbols = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN']
            run_multi_symbol_analysis(symbols, args.sentiment, args.confidence)
        else:
            # Run single symbol backtest
            runner = RealDataBacktestRunner()
            
            runner.setup_backtest(
                symbol=args.symbol,
                initial_cash=args.cash,
                commission=args.commission,
                sentiment_style=args.sentiment,
                min_confidence=args.confidence,
                start_date=args.start_date,
                end_date=args.end_date
            )
            
            results = runner.run_backtest()
            runner.print_comprehensive_results(results, args.symbol)
            
            if args.save:
                runner.save_results(results, args.symbol, args.sentiment)
        
        print(f"\n🎉 Real data backtest completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Backtest interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
