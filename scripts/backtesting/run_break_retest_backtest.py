#!/usr/bin/env python3
"""
Break and Retest Strategy Backtesting
Comprehensive backtesting for the Break and Retest swing trading strategy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
from typing import Dict, Any

from src.strategies.break_retest_strategy import BreakRetestSwingStrategy

class BreakRetestBacktester:
    """Comprehensive backtesting system for Break and Retest strategy"""
    
    def __init__(self, data_file: str, symbol: str):
        self.data_file = data_file
        self.symbol = symbol
        self.cerebro = None
        self.results = None
        
    def setup_backtest(self, 
                      initial_cash: float = 100000.0,
                      commission: float = 0.001,
                      **strategy_params):
        """Setup the backtesting environment"""
        
        print(f"🎯 Setting up Break and Retest Backtest")
        print(f"   Symbol: {self.symbol}")
        print(f"   Data File: {self.data_file}")
        print(f"   Initial Cash: ${initial_cash:,.2f}")
        print(f"   Commission: {commission:.3%}")
        
        # Initialize Cerebro
        self.cerebro = bt.Cerebro()
        
        # Add strategy with custom parameters
        self.cerebro.addstrategy(
            BreakRetestSwingStrategy,
            **strategy_params
        )
        
        # Load data
        try:
            data = bt.feeds.GenericCSVData(
                dataname=self.data_file,
                dtformat='%Y-%m-%d %H:%M:%S.%f',
                datetime=0, open=1, high=2, low=3, close=4, volume=5,
                openinterest=-1, headers=True, timeframe=bt.TimeFrame.Days
            )
            
            self.cerebro.adddata(data)
            print(f"✅ Data loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        # Set broker parameters
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)
        
        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
        
        print(f"✅ Break and Retest backtest setup complete")
        return True
        
    def run_backtest(self) -> Dict[str, Any]:
        """Run the backtest and return results"""
        
        if not self.cerebro:
            raise ValueError("Backtest not setup. Call setup_backtest() first.")
        
        print(f"\n🚀 Starting Break and Retest Backtest")
        print(f"   Strategy: Break and Retest Swing Trading")
        
        # Get initial value
        initial_value = self.cerebro.broker.getvalue()
        print(f"   Starting Portfolio Value: ${initial_value:,.2f}")
        
        # Run backtest
        start_time = datetime.now()
        self.results = self.cerebro.run()
        end_time = datetime.now()
        
        # Get final value and strategy instance
        final_value = self.cerebro.broker.getvalue()
        strategy_instance = self.results[0]
        
        print(f"   Final Portfolio Value: ${final_value:,.2f}")
        print(f"   Total Return: {((final_value / initial_value) - 1) * 100:+.2f}%")
        print(f"   Execution Time: {end_time - start_time}")
        
        # Extract comprehensive results
        return self._extract_results(initial_value, final_value, strategy_instance)
    
    def _extract_results(self, initial_value: float, final_value: float, 
                        strategy_instance) -> Dict[str, Any]:
        """Extract comprehensive results from backtest"""
        
        # Basic performance metrics
        total_return = ((final_value / initial_value) - 1) * 100
        
        # Get data info for time period calculation
        df = pd.read_csv(self.data_file)
        start_date = pd.to_datetime(df.iloc[0]['datetime'])
        end_date = pd.to_datetime(df.iloc[-1]['datetime'])
        years = (end_date - start_date).days / 365.25
        annualized_return = ((final_value / initial_value) ** (1/years) - 1) * 100
        
        # Strategy-specific stats
        strategy_stats = strategy_instance.get_strategy_stats()
        
        # Analyzer results
        analyzers = {}
        try:
            analyzers['sharpe'] = strategy_instance.analyzers.sharpe.get_analysis()
            analyzers['drawdown'] = strategy_instance.analyzers.drawdown.get_analysis()
            analyzers['trades'] = strategy_instance.analyzers.trades.get_analysis()
            analyzers['returns'] = strategy_instance.analyzers.returns.get_analysis()
            analyzers['sqn'] = strategy_instance.analyzers.sqn.get_analysis()
        except Exception as e:
            print(f"⚠️ Warning: Some analyzers failed: {e}")
        
        # Compile results
        results = {
            'performance': {
                'initial_value': initial_value,
                'final_value': final_value,
                'total_return_pct': total_return,
                'annualized_return_pct': annualized_return,
                'years': years,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'strategy_stats': strategy_stats,
            'analyzers': analyzers,
            'symbol': self.symbol,
            'strategy_name': 'Break and Retest Swing'
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print comprehensive backtest results"""
        
        print(f"\n📊 {self.symbol} - Break and Retest Strategy Results")
        print("=" * 80)
        
        # Performance Summary
        perf = results['performance']
        print(f"💰 Performance Summary:")
        print(f"   Time Period: {perf['start_date']} to {perf['end_date']} ({perf['years']:.1f} years)")
        print(f"   Initial Value: ${perf['initial_value']:,.2f}")
        print(f"   Final Value: ${perf['final_value']:,.2f}")
        print(f"   Total Return: {perf['total_return_pct']:+.2f}%")
        print(f"   Annualized Return: {perf['annualized_return_pct']:+.2f}%")
        
        # Strategy Statistics
        stats = results['strategy_stats']
        print(f"\n🎯 Break and Retest Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Winning Trades: {stats['winning_trades']}")
        print(f"   Losing Trades: {stats['losing_trades']}")
        print(f"   Win Rate: {stats['win_rate']:.1f}%")
        print(f"   Average PnL per Trade: ${stats['avg_pnl_per_trade']:,.2f}")
        print(f"   Total PnL: ${stats['total_pnl']:,.2f}")
        
        # Level Detection Stats
        print(f"\n📊 Level Detection:")
        print(f"   Support Levels Identified: {stats['support_levels_count']}")
        print(f"   Resistance Levels Identified: {stats['resistance_levels_count']}")
        print(f"   Active Breakouts: {stats['active_breakouts']}")
        
        # Risk Metrics
        analyzers = results['analyzers']
        print(f"\n📉 Risk Metrics:")
        
        if 'sharpe' in analyzers and analyzers['sharpe']:
            sharpe_ratio = analyzers['sharpe'].get('sharperatio', 0)
            print(f"   Sharpe Ratio: {sharpe_ratio:.3f}")
        
        if 'drawdown' in analyzers and analyzers['drawdown']:
            max_dd = analyzers['drawdown'].get('max', {}).get('drawdown', 0)
            print(f"   Max Drawdown: {max_dd:.2f}%")
        
        if 'sqn' in analyzers and analyzers['sqn']:
            sqn_score = analyzers['sqn'].get('sqn', 0)
            print(f"   SQN Score: {sqn_score:.2f}")
            
            # SQN Quality Rating
            if sqn_score >= 3.0:
                quality = "Excellent"
            elif sqn_score >= 2.0:
                quality = "Good"
            elif sqn_score >= 1.0:
                quality = "Average"
            else:
                quality = "Poor"
            print(f"   System Quality: {quality}")
        
        # Trade Analysis
        if 'trades' in analyzers and analyzers['trades']:
            trades_data = analyzers['trades']
            if 'total' in trades_data:
                total_trades = trades_data['total'].get('closed', 0)
                print(f"\n📈 Trade Analysis:")
                print(f"   Closed Trades: {total_trades}")
                
                if 'won' in trades_data and 'lost' in trades_data:
                    won_data = trades_data['won']
                    lost_data = trades_data['lost']
                    
                    won_total = won_data.get('total', 0)
                    lost_total = lost_data.get('total', 0)
                    
                    if won_total > 0:
                        avg_win = won_data.get('pnl', {}).get('average', 0)
                        max_win = won_data.get('pnl', {}).get('max', 0)
                        print(f"   Average Win: ${avg_win:,.2f}")
                        print(f"   Largest Win: ${max_win:,.2f}")
                    
                    if lost_total > 0:
                        avg_loss = lost_data.get('pnl', {}).get('average', 0)
                        max_loss = lost_data.get('pnl', {}).get('max', 0)
                        print(f"   Average Loss: ${avg_loss:,.2f}")
                        print(f"   Largest Loss: ${max_loss:,.2f}")
                        
                        # Profit Factor
                        if avg_loss != 0:
                            profit_factor = abs((avg_win * won_total) / (avg_loss * lost_total))
                            print(f"   Profit Factor: {profit_factor:.2f}")

def run_parameter_optimization(symbol: str, data_file: str):
    """Run parameter optimization for Break and Retest strategy"""
    
    print(f"\n🔬 Break and Retest Parameter Optimization - {symbol}")
    print("=" * 60)
    
    # Parameter combinations to test
    param_combinations = [
        # Conservative settings
        {
            'name': 'Conservative',
            'lookback_period': 30,
            'min_breakout_strength': 0.015,
            'position_size_pct': 0.01,
            'stop_loss_atr_mult': 2.5,
            'take_profit_ratio': 2.0
        },
        # Balanced settings
        {
            'name': 'Balanced',
            'lookback_period': 20,
            'min_breakout_strength': 0.01,
            'position_size_pct': 0.02,
            'stop_loss_atr_mult': 2.0,
            'take_profit_ratio': 3.0
        },
        # Aggressive settings
        {
            'name': 'Aggressive',
            'lookback_period': 15,
            'min_breakout_strength': 0.008,
            'position_size_pct': 0.03,
            'stop_loss_atr_mult': 1.5,
            'take_profit_ratio': 4.0
        },
        # High Frequency
        {
            'name': 'High Frequency',
            'lookback_period': 10,
            'min_breakout_strength': 0.005,
            'position_size_pct': 0.015,
            'stop_loss_atr_mult': 1.8,
            'take_profit_ratio': 2.5
        }
    ]
    
    results = []
    
    for params in param_combinations:
        print(f"\n🧪 Testing {params['name']} Parameters...")
        
        try:
            backtester = BreakRetestBacktester(data_file, symbol)
            
            # Remove 'name' from params before passing to strategy
            strategy_params = {k: v for k, v in params.items() if k != 'name'}
            
            if backtester.setup_backtest(**strategy_params):
                result = backtester.run_backtest()
                result['parameter_set'] = params['name']
                results.append(result)
                
                # Print quick summary
                perf = result['performance']
                stats = result['strategy_stats']
                print(f"   Return: {perf['total_return_pct']:+.1f}% | "
                      f"Trades: {stats['total_trades']} | "
                      f"Win Rate: {stats['win_rate']:.1f}%")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Print optimization summary
    if results:
        print(f"\n📊 Parameter Optimization Summary")
        print("=" * 70)
        print(f"{'Parameter Set':<15} {'Return':<10} {'Ann. Return':<12} {'Trades':<8} {'Win Rate':<10}")
        print("-" * 70)
        
        for result in results:
            perf = result['performance']
            stats = result['strategy_stats']
            print(f"{result['parameter_set']:<15} {perf['total_return_pct']:>+8.1f}% "
                  f"{perf['annualized_return_pct']:>+10.1f}% {stats['total_trades']:>6} "
                  f"{stats['win_rate']:>8.1f}%")
        
        # Find best performing parameter set
        best_result = max(results, key=lambda x: x['performance']['total_return_pct'])
        print(f"\n🏆 Best Parameter Set: {best_result['parameter_set']}")
        print(f"   Total Return: {best_result['performance']['total_return_pct']:+.1f}%")
        print(f"   Annualized Return: {best_result['performance']['annualized_return_pct']:+.1f}%")
        print(f"   Win Rate: {best_result['strategy_stats']['win_rate']:.1f}%")
    
    return results

def main():
    """Main backtesting function"""
    
    parser = argparse.ArgumentParser(description='Break and Retest Strategy Backtesting')
    parser.add_argument('--symbol', '-s', type=str, default='SPY',
                       help='Symbol to backtest (SPY, QQQ, NVDA, AAPL, etc.)')
    parser.add_argument('--optimize', action='store_true',
                       help='Run parameter optimization')
    parser.add_argument('--cash', type=float, default=100000.0,
                       help='Initial cash amount')
    parser.add_argument('--commission', type=float, default=0.001,
                       help='Commission rate')
    
    args = parser.parse_args()
    
    # Determine data file based on symbol
    if args.symbol in ['SPY', 'QQQ']:
        data_file = f"data/real_data/{args.symbol}_historical.csv"
    else:
        data_file = f"data/real_data/{args.symbol}_15years.csv"
    
    if not Path(data_file).exists():
        print(f"❌ Data file not found: {data_file}")
        print("Available data files:")
        data_dir = Path("data/real_data")
        if data_dir.exists():
            for file in data_dir.glob("*.csv"):
                print(f"   {file.name}")
        return 1
    
    try:
        if args.optimize:
            # Run parameter optimization
            run_parameter_optimization(args.symbol, data_file)
        else:
            # Run single backtest with default parameters
            backtester = BreakRetestBacktester(data_file, args.symbol)
            
            if backtester.setup_backtest(
                initial_cash=args.cash,
                commission=args.commission
            ):
                results = backtester.run_backtest()
                backtester.print_results(results)
        
        print(f"\n🎉 Break and Retest backtest completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
