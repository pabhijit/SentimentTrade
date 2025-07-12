#!/usr/bin/env python3
"""
ETF Backtesting - SPY and QQQ
Comprehensive backtesting on major ETFs with parameter optimization
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
import itertools
from typing import Dict, List, Any

from final_real_backtest import FinalTradingStrategy

class ETFBacktester:
    """Comprehensive ETF backtesting system"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data_file = f"data/real_data/{symbol}_historical.csv"
        
        if not Path(self.data_file).exists():
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
    
    def run_single_backtest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run backtest with specific parameters"""
        
        try:
            cerebro = bt.Cerebro()
            
            cerebro.addstrategy(
                FinalTradingStrategy,
                sentiment_style=params['sentiment_style'],
                min_confidence=params['min_confidence']
            )
            
            # Load data
            data = bt.feeds.GenericCSVData(
                dataname=self.data_file,
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
            
            # Run backtest
            initial_value = cerebro.broker.getvalue()
            results = cerebro.run()
            final_value = cerebro.broker.getvalue()
            
            strat = results[0]
            
            # Calculate metrics
            total_return = ((final_value / initial_value) - 1) * 100
            
            # Get data info for annualized return calculation
            df = pd.read_csv(self.data_file)
            years = (pd.to_datetime(df.iloc[-1]['datetime']) - pd.to_datetime(df.iloc[0]['datetime'])).days / 365.25
            annualized_return = ((final_value / initial_value) ** (1/years) - 1) * 100
            
            strategy_stats = strat.get_stats()
            
            # Get analyzer results
            sharpe_ratio = 0
            max_drawdown = 0
            total_trades = 0
            
            try:
                sharpe = strat.analyzers.sharpe.get_analysis()
                if sharpe and 'sharperatio' in sharpe:
                    sharpe_ratio = sharpe['sharperatio'] or 0
                
                drawdown = strat.analyzers.drawdown.get_analysis()
                if drawdown and 'max' in drawdown:
                    max_drawdown = drawdown['max'].get('drawdown', 0)
                
                trades = strat.analyzers.trades.get_analysis()
                if trades and 'total' in trades:
                    total_trades = trades['total'].get('closed', 0)
            except:
                pass
            
            return {
                'parameters': params,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': strategy_stats['win_rate'],
                'total_trades': total_trades,
                'avg_pnl_per_trade': strategy_stats['avg_pnl_per_trade'],
                'final_value': final_value,
                'signals_generated': strategy_stats['signal_count'],
                'buy_signals': strategy_stats['buy_signals'],
                'sell_signals': strategy_stats['sell_signals'],
                'years': years
            }
            
        except Exception as e:
            return {
                'parameters': params,
                'error': str(e)
            }
    
    def optimize_etf_parameters(self) -> List[Dict[str, Any]]:
        """Optimize parameters for ETF"""
        
        print(f"🔬 Optimizing ETF Strategy for {self.symbol}")
        print("=" * 60)
        
        # ETF-specific parameter ranges (ETFs are generally less volatile than individual stocks)
        test_combinations = [
            {'sentiment_style': 'realistic', 'min_confidence': 0.05},
            {'sentiment_style': 'realistic', 'min_confidence': 0.08},
            {'sentiment_style': 'realistic', 'min_confidence': 0.10},
            {'sentiment_style': 'realistic', 'min_confidence': 0.12},
            {'sentiment_style': 'realistic', 'min_confidence': 0.15},
            {'sentiment_style': 'momentum', 'min_confidence': 0.05},
            {'sentiment_style': 'momentum', 'min_confidence': 0.08},
            {'sentiment_style': 'momentum', 'min_confidence': 0.10},
            {'sentiment_style': 'contrarian', 'min_confidence': 0.08},
            {'sentiment_style': 'contrarian', 'min_confidence': 0.10},
            {'sentiment_style': 'contrarian', 'min_confidence': 0.12},
        ]
        
        results = []
        
        for i, params in enumerate(test_combinations):
            print(f"🧪 Test {i+1}/{len(test_combinations)}: {params['sentiment_style']} sentiment, {params['min_confidence']:.2f} confidence")
            
            result = self.run_single_backtest(params)
            if 'error' not in result:
                results.append(result)
                print(f"   Return: {result['total_return']:+.1f}% ({result['annualized_return']:+.1f}% annual)")
                print(f"   Trades: {result['total_trades']} | Win Rate: {result['win_rate']:.1f}%")
                print(f"   Sharpe: {result['sharpe_ratio']:.2f} | Drawdown: {result['max_drawdown']:.1f}%")
            else:
                print(f"   ❌ Error: {result['error']}")
        
        # Sort by total return (considering trade activity)
        valid_results = [r for r in results if r['total_trades'] > 10]  # Require minimum activity
        if not valid_results:
            valid_results = results  # Fall back to all results if none have enough trades
        
        valid_results.sort(key=lambda x: x['total_return'], reverse=True)
        
        return valid_results
    
    def print_etf_results(self, results: List[Dict[str, Any]]):
        """Print comprehensive ETF results"""
        
        if not results:
            print("❌ No valid results found")
            return
        
        # Get buy & hold benchmark
        df = pd.read_csv(self.data_file)
        buy_hold_return = ((df.iloc[-1]['close'] / df.iloc[0]['close']) - 1) * 100
        years = (pd.to_datetime(df.iloc[-1]['datetime']) - pd.to_datetime(df.iloc[0]['datetime'])).days / 365.25
        buy_hold_annual = ((df.iloc[-1]['close'] / df.iloc[0]['close']) ** (1/years) - 1) * 100
        
        print(f"\n📊 {self.symbol} Optimization Results")
        print("=" * 80)
        print(f"📈 Buy & Hold Benchmark: {buy_hold_return:+.1f}% total ({buy_hold_annual:+.1f}% annual over {years:.1f} years)")
        print(f"✅ Valid Results: {len(results)}")
        
        print(f"\n🏆 Top 5 Parameter Combinations:")
        print("-" * 80)
        
        for i, result in enumerate(results[:5]):
            params = result['parameters']
            outperformance = result['total_return'] - buy_hold_return
            
            print(f"\n#{i+1} - Total Return: {result['total_return']:+.1f}% | Outperformance: {outperformance:+.1f}%")
            print(f"   📊 Annual Return: {result['annualized_return']:+.1f}%")
            print(f"   📈 Risk: Sharpe {result['sharpe_ratio']:.2f} | Drawdown {result['max_drawdown']:.1f}%")
            print(f"   🎯 Trading: {result['total_trades']} trades | {result['win_rate']:.1f}% win rate")
            print(f"   📡 Signals: {result['signals_generated']} total | {result['buy_signals']} buy | {result['sell_signals']} sell")
            print(f"   ⚙️ Params: {params['sentiment_style']} sentiment | confidence {params['min_confidence']:.2f}")
        
        # Best result analysis
        best_result = results[0]
        best_params = best_result['parameters']
        
        print(f"\n🎯 OPTIMAL PARAMETERS for {self.symbol}:")
        print("-" * 40)
        for param, value in best_params.items():
            print(f"   {param}: {value}")
        
        print(f"\n📈 EXPECTED PERFORMANCE:")
        print(f"   Total Return ({years:.1f} years): {best_result['total_return']:+.1f}%")
        print(f"   Annualized Return: {best_result['annualized_return']:+.1f}%")
        print(f"   vs Buy & Hold: {best_result['total_return'] - buy_hold_return:+.1f}%")
        print(f"   Sharpe Ratio: {best_result['sharpe_ratio']:.3f}")
        print(f"   Max Drawdown: {best_result['max_drawdown']:.2f}%")
        print(f"   Win Rate: {best_result['win_rate']:.1f}%")
        print(f"   Total Trades: {best_result['total_trades']}")
        print(f"   Avg PnL/Trade: ${best_result['avg_pnl_per_trade']:,.2f}")
        
        return best_params, results

def run_etf_comparison():
    """Run comprehensive ETF comparison"""
    
    etfs = ['SPY', 'QQQ']
    all_results = {}
    
    print("🚀 ETF Strategy Optimization Comparison")
    print("=" * 70)
    
    for etf in etfs:
        print(f"\n{'='*20} {etf} OPTIMIZATION {'='*20}")
        
        try:
            backtester = ETFBacktester(etf)
            results = backtester.optimize_etf_parameters()
            best_params, all_results_etf = backtester.print_etf_results(results)
            
            all_results[etf] = {
                'best_parameters': best_params,
                'best_result': all_results_etf[0] if all_results_etf else None,
                'top_5_results': all_results_etf[:5] if all_results_etf else []
            }
            
        except Exception as e:
            print(f"❌ Error optimizing {etf}: {e}")
            all_results[etf] = {'error': str(e)}
    
    # Summary comparison
    print(f"\n📊 ETF OPTIMIZATION SUMMARY")
    print("=" * 90)
    print(f"{'ETF':<6} {'Best Return':<12} {'Annual':<10} {'Trades':<8} {'Win%':<8} {'Sharpe':<8} {'Sentiment':<12}")
    print("-" * 90)
    
    for etf, data in all_results.items():
        if 'error' not in data and data['best_result']:
            result = data['best_result']
            params = result['parameters']
            print(f"{etf:<6} {result['total_return']:>+10.1f}% {result['annualized_return']:>+8.1f}% "
                  f"{result['total_trades']:>6} {result['win_rate']:>6.1f}% "
                  f"{result['sharpe_ratio']:>6.2f} {params['sentiment_style']:<12}")
        else:
            print(f"{etf:<6} ERROR")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"etf_optimization_results_{timestamp}.json"
    
    try:
        import json
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\n💾 Complete results saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
    
    return all_results

def main():
    """Main ETF backtesting function"""
    
    print("📊 SentimentTrade ETF Backtesting")
    print("Testing AI strategy on SPY and QQQ with historical data")
    print("=" * 70)
    
    # Run comprehensive ETF comparison
    results = run_etf_comparison()
    
    print(f"\n💡 Key Insights:")
    print(f"   • ETFs are generally less volatile than individual stocks")
    print(f"   • Lower confidence thresholds may work better for ETFs")
    print(f"   • Momentum strategies often work well for broad market ETFs")
    print(f"   • SPY represents broad market, QQQ represents tech-heavy NASDAQ")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Use optimal parameters for ETF trading")
    print(f"   2. Consider ETFs for more conservative portfolio allocation")
    print(f"   3. Compare ETF results with individual stock performance")
    print(f"   4. Test portfolio combinations of ETFs and individual stocks")

if __name__ == "__main__":
    main()
