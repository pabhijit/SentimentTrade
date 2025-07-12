#!/usr/bin/env python3
"""
SentimentTrade AI Backtest Runner
Comprehensive backtesting system for the AI trading signal generator
"""

import sys
import os
from pathlib import Path
import argparse
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Handle optional plotting dependencies
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️ Matplotlib/Seaborn not available. Install with: pip install matplotlib seaborn")

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import backtrader as bt
from src.backtest.ai_strategy import AITradingStrategy
from src.backtest.sentiment_mocker import BacktestSentimentMocker
from database import init_database, get_db, User, UserPreferences
from preferences_service import PreferencesService

class AIBacktestRunner:
    """Comprehensive backtest runner for AI trading strategies"""
    
    def __init__(self):
        self.cerebro = None
        self.results = None
        self.strategy_instance = None
        
    def setup_backtest(self, 
                      data_file: str,
                      initial_cash: float = 100000.0,
                      commission: float = 0.001,
                      user_email: Optional[str] = None,
                      sentiment_style: str = 'realistic',
                      min_confidence: float = 0.7,
                      enable_plotting: bool = True):
        """
        Setup backtest environment
        
        Args:
            data_file: Path to CSV data file
            initial_cash: Starting portfolio value
            commission: Commission rate (0.001 = 0.1%)
            user_email: User email for preferences (optional)
            sentiment_style: Sentiment generation style
            min_confidence: Minimum confidence for trades
            enable_plotting: Enable result plotting
        """
        
        print(f"🚀 Setting up AI Backtest")
        print(f"   Data File: {data_file}")
        print(f"   Initial Cash: ${initial_cash:,.2f}")
        print(f"   Commission: {commission:.3%}")
        print(f"   Sentiment Style: {sentiment_style}")
        print(f"   Min Confidence: {min_confidence:.1%}")
        
        # Initialize Cerebro
        self.cerebro = bt.Cerebro()
        
        # Load user preferences
        user_preferences = self._load_user_preferences(user_email)
        
        # Add AI strategy
        self.cerebro.addstrategy(
            AITradingStrategy,
            user_preferences=user_preferences,
            sentiment_style=sentiment_style,
            min_confidence=min_confidence,
            trade_logging=True
        )
        
        # Load and add data
        self._load_data(data_file)
        
        # Set broker parameters
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)
        
        # Add analyzers
        self._add_analyzers()
        
        print(f"✅ Backtest setup complete")
        
    def _load_user_preferences(self, user_email: Optional[str]) -> Optional[UserPreferences]:
        """Load user preferences for personalized backtesting"""
        
        if not user_email:
            print(f"📊 Using default trading configuration")
            return None
        
        try:
            init_database()
            db = next(get_db())
            
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                print(f"⚠️ User {user_email} not found, using default preferences")
                db.close()
                return None
            
            preferences_service = PreferencesService(db)
            user_preferences = preferences_service.get_or_create_preferences(user.id)
            
            print(f"✅ Loaded preferences for {user_email}")
            print(f"   Risk Appetite: {user_preferences.risk_appetite}")
            print(f"   Strategy: {user_preferences.strategy}")
            print(f"   Min Confidence: {user_preferences.min_confidence:.1%}")
            
            db.close()
            return user_preferences
            
        except Exception as e:
            print(f"❌ Failed to load user preferences: {e}")
            return None
    
    def _load_data(self, data_file: str):
        """Load market data for backtesting"""
        
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        # Determine data format and load accordingly
        if data_file.endswith('.csv'):
            self._load_csv_data(data_file)
        else:
            raise ValueError(f"Unsupported data format: {data_file}")
    
    def _load_csv_data(self, csv_file: str):
        """Load CSV data file"""
        
        try:
            # Read CSV to determine format
            df = pd.read_csv(csv_file)
            print(f"📊 Loaded {len(df)} rows from {csv_file}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Date range: {df.iloc[0]['datetime']} to {df.iloc[-1]['datetime']}")
            
            # Create Backtrader data feed
            data = bt.feeds.GenericCSVData(
                dataname=csv_file,
                dtformat='%Y-%m-%d %H:%M:%S.%f',  # Match the format in random_gen.csv
                datetime=0,  # datetime column index
                open=1,      # open column index
                high=2,      # high column index
                low=3,       # low column index
                close=4,     # close column index
                volume=5,    # volume column index
                openinterest=-1,  # no open interest
                headers=True,     # CSV has headers
                timeframe=bt.TimeFrame.Minutes,
                compression=1
            )
            
            self.cerebro.adddata(data)
            print(f"✅ Data feed added to backtest engine")
            
        except Exception as e:
            print(f"❌ Error loading CSV data: {e}")
            raise
    
    def _add_analyzers(self):
        """Add performance analyzers to backtest"""
        
        # Standard analyzers
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
        self.cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  # Variability-Weighted Return
        
        # Custom analyzers
        from src.backtest.turnover import TurnoverAnalyzer
        self.cerebro.addanalyzer(TurnoverAnalyzer, _name='turnover')
        
        print(f"✅ Performance analyzers added")
    
    def run_backtest(self) -> Dict[str, Any]:
        """Run the backtest and return results"""
        
        if not self.cerebro:
            raise ValueError("Backtest not setup. Call setup_backtest() first.")
        
        print(f"\n🚀 Starting AI Backtest")
        print(f"   Starting Portfolio Value: ${self.cerebro.broker.getvalue():,.2f}")
        
        # Run backtest
        start_time = datetime.now()
        self.results = self.cerebro.run()
        end_time = datetime.now()
        
        self.strategy_instance = self.results[0]
        
        final_value = self.cerebro.broker.getvalue()
        print(f"   Final Portfolio Value: ${final_value:,.2f}")
        print(f"   Total Return: {((final_value / 100000.0) - 1) * 100:.2f}%")
        print(f"   Backtest Duration: {end_time - start_time}")
        
        # Extract and return results
        return self._extract_results()
    
    def _extract_results(self) -> Dict[str, Any]:
        """Extract comprehensive results from backtest"""
        
        if not self.results or not self.strategy_instance:
            return {}
        
        strat = self.strategy_instance
        
        # Basic performance metrics
        final_value = self.cerebro.broker.getvalue()
        initial_value = 100000.0  # Default initial cash
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
            analyzers['turnover'] = strat.analyzers.turnover.get_analysis()
        except Exception as e:
            print(f"⚠️ Warning: Some analyzers failed: {e}")
        
        # Strategy-specific results
        strategy_stats = strat.get_strategy_stats()
        signal_history = strat.get_signal_history()
        trade_history = strat.get_trade_history()
        
        # Compile comprehensive results
        results = {
            'performance': {
                'initial_value': initial_value,
                'final_value': final_value,
                'total_return_pct': total_return,
                'total_return_abs': final_value - initial_value
            },
            'analyzers': analyzers,
            'strategy_stats': strategy_stats,
            'signal_history': signal_history,
            'trade_history': trade_history,
            'backtest_info': {
                'strategy': 'AI Trading Strategy',
                'data_points': len(signal_history),
                'backtest_date': datetime.now().isoformat()
            }
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print comprehensive backtest results"""
        
        print(f"\n📊 AI Backtest Results")
        print("=" * 60)
        
        # Performance Summary
        perf = results.get('performance', {})
        print(f"💰 Performance Summary:")
        print(f"   Initial Value: ${perf.get('initial_value', 0):,.2f}")
        print(f"   Final Value: ${perf.get('final_value', 0):,.2f}")
        print(f"   Total Return: {perf.get('total_return_pct', 0):.2f}%")
        print(f"   Absolute Gain: ${perf.get('total_return_abs', 0):,.2f}")
        
        # Strategy Statistics
        stats = results.get('strategy_stats', {})
        print(f"\n🎯 Trading Statistics:")
        print(f"   Total Trades: {stats.get('total_trades', 0)}")
        print(f"   Winning Trades: {stats.get('winning_trades', 0)}")
        print(f"   Losing Trades: {stats.get('losing_trades', 0)}")
        print(f"   Win Rate: {stats.get('win_rate', 0):.1f}%")
        print(f"   Average PnL per Trade: ${stats.get('avg_pnl_per_trade', 0):.2f}")
        print(f"   Total Signals Generated: {stats.get('signal_count', 0)}")
        
        # Analyzer Results
        analyzers = results.get('analyzers', {})
        
        # Sharpe Ratio
        sharpe = analyzers.get('sharpe', {})
        if sharpe:
            print(f"\n📈 Risk-Adjusted Performance:")
            print(f"   Sharpe Ratio: {sharpe.get('sharperatio', 0):.3f}")
        
        # Drawdown
        drawdown = analyzers.get('drawdown', {})
        if drawdown:
            print(f"   Max Drawdown: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
            print(f"   Max Drawdown Duration: {drawdown.get('max', {}).get('len', 0)} periods")
        
        # Trade Analysis
        trades = analyzers.get('trades', {})
        if trades:
            total_trades = trades.get('total', {})
            if total_trades:
                print(f"\n📋 Trade Analysis:")
                print(f"   Total Closed Trades: {total_trades.get('closed', 0)}")
                print(f"   Total Open Trades: {total_trades.get('open', 0)}")
                
                won = trades.get('won', {})
                lost = trades.get('lost', {})
                if won:
                    print(f"   Won Trades: {won.get('total', 0)} (Avg: ${won.get('pnl', {}).get('average', 0):.2f})")
                if lost:
                    print(f"   Lost Trades: {lost.get('total', 0)} (Avg: ${lost.get('pnl', {}).get('average', 0):.2f})")
        
        # SQN (System Quality Number)
        sqn = analyzers.get('sqn', {})
        if sqn:
            sqn_value = sqn.get('sqn', 0)
            print(f"\n🎲 System Quality:")
            print(f"   SQN Score: {sqn_value:.2f}")
            if sqn_value >= 3.0:
                print(f"   Quality: Excellent (>= 3.0)")
            elif sqn_value >= 2.0:
                print(f"   Quality: Good (>= 2.0)")
            elif sqn_value >= 1.0:
                print(f"   Quality: Average (>= 1.0)")
            else:
                print(f"   Quality: Poor (< 1.0)")
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save backtest results to JSON file"""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtest_results_{timestamp}.json"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, 'isoformat'):  # Handle pandas timestamps
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=json_serializer)
            
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def plot_results(self, results: Dict[str, Any], save_plots: bool = True):
        """Create visualization plots for backtest results"""
        
        if not PLOTTING_AVAILABLE:
            print("❌ Plotting not available. Install matplotlib and seaborn:")
            print("   pip install matplotlib seaborn")
            return
        
        try:
            # Set up plotting style
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('AI Trading Strategy Backtest Results', fontsize=16, fontweight='bold')
            
            # Plot 1: Portfolio Value Over Time (if we had time series data)
            ax1 = axes[0, 0]
            ax1.set_title('Portfolio Performance')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Portfolio Value ($)')
            
            # For now, show initial vs final value
            perf = results.get('performance', {})
            initial = perf.get('initial_value', 100000)
            final = perf.get('final_value', 100000)
            ax1.bar(['Initial', 'Final'], [initial, final], color=['blue', 'green' if final > initial else 'red'])
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Plot 2: Win/Loss Distribution
            ax2 = axes[0, 1]
            stats = results.get('strategy_stats', {})
            winning = stats.get('winning_trades', 0)
            losing = stats.get('losing_trades', 0)
            
            if winning + losing > 0:
                ax2.pie([winning, losing], labels=['Winning Trades', 'Losing Trades'], 
                       colors=['green', 'red'], autopct='%1.1f%%')
                ax2.set_title(f'Trade Distribution (Win Rate: {stats.get("win_rate", 0):.1f}%)')
            else:
                ax2.text(0.5, 0.5, 'No Trades Executed', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Trade Distribution')
            
            # Plot 3: Signal Confidence Distribution
            ax3 = axes[1, 0]
            signal_history = results.get('signal_history', [])
            if signal_history:
                confidences = [s['signal'].get('confidence', 0) for s in signal_history if s['signal'].get('action') != 'HOLD']
                if confidences:
                    ax3.hist(confidences, bins=20, alpha=0.7, color='blue', edgecolor='black')
                    ax3.set_title('Signal Confidence Distribution')
                    ax3.set_xlabel('Confidence Level')
                    ax3.set_ylabel('Frequency')
                    import numpy as np
                    ax3.axvline(np.mean(confidences), color='red', linestyle='--', label=f'Mean: {np.mean(confidences):.2f}')
                    ax3.legend()
                else:
                    ax3.text(0.5, 0.5, 'No Actionable Signals', ha='center', va='center', transform=ax3.transAxes)
            else:
                ax3.text(0.5, 0.5, 'No Signal Data', ha='center', va='center', transform=ax3.transAxes)
            
            # Plot 4: Performance Metrics
            ax4 = axes[1, 1]
            analyzers = results.get('analyzers', {})
            
            metrics = []
            values = []
            
            # Sharpe Ratio
            sharpe = analyzers.get('sharpe', {}).get('sharperatio', 0)
            if sharpe:
                metrics.append('Sharpe Ratio')
                values.append(sharpe)
            
            # Max Drawdown (as positive value for visualization)
            drawdown = analyzers.get('drawdown', {}).get('max', {}).get('drawdown', 0)
            if drawdown:
                metrics.append('Max Drawdown %')
                values.append(abs(drawdown))
            
            # SQN Score
            sqn = analyzers.get('sqn', {}).get('sqn', 0)
            if sqn:
                metrics.append('SQN Score')
                values.append(sqn)
            
            if metrics:
                bars = ax4.bar(metrics, values, color=['green', 'red', 'blue'][:len(metrics)])
                ax4.set_title('Key Performance Metrics')
                ax4.set_ylabel('Value')
                
                # Add value labels on bars
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                            f'{value:.2f}', ha='center', va='bottom')
            else:
                ax4.text(0.5, 0.5, 'No Metrics Available', ha='center', va='center', transform=ax4.transAxes)
            
            plt.tight_layout()
            
            if save_plots:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                plot_filename = f"backtest_plots_{timestamp}.png"
                plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
                print(f"📊 Plots saved to: {plot_filename}")
            
            plt.show()
            
        except Exception as e:
            print(f"❌ Error creating plots: {e}")
    
    def run_cerebro_plot(self):
        """Run Cerebro's built-in plotting"""
        
        if self.cerebro and self.results:
            try:
                print(f"📈 Generating Cerebro plot...")
                self.cerebro.plot(style='candlestick', barup='green', bardown='red')
            except Exception as e:
                print(f"❌ Error generating Cerebro plot: {e}")

def main():
    """Main backtest runner function"""
    
    parser = argparse.ArgumentParser(description='SentimentTrade AI Backtest Runner')
    
    parser.add_argument('--data', '-d', type=str, 
                       default='data/test_data/random_gen.csv',
                       help='Path to CSV data file')
    parser.add_argument('--cash', '-c', type=float, default=100000.0,
                       help='Initial cash amount')
    parser.add_argument('--commission', type=float, default=0.001,
                       help='Commission rate (0.001 = 0.1 percent)')
    parser.add_argument('--user', '-u', type=str,
                       help='User email for personalized preferences')
    parser.add_argument('--sentiment', '-s', type=str, default='realistic',
                       choices=['realistic', 'contrarian', 'momentum', 'random', 'neutral'],
                       help='Sentiment generation style')
    parser.add_argument('--confidence', type=float, default=0.7,
                       help='Minimum confidence threshold for trades')
    parser.add_argument('--save', action='store_true',
                       help='Save results to JSON file')
    parser.add_argument('--plot', action='store_true',
                       help='Generate result plots')
    parser.add_argument('--cerebro-plot', action='store_true',
                       help='Show Cerebro candlestick plot')
    
    args = parser.parse_args()
    
    try:
        # Initialize backtest runner
        runner = AIBacktestRunner()
        
        # Setup backtest
        runner.setup_backtest(
            data_file=args.data,
            initial_cash=args.cash,
            commission=args.commission,
            user_email=args.user,
            sentiment_style=args.sentiment,
            min_confidence=args.confidence
        )
        
        # Run backtest
        results = runner.run_backtest()
        
        # Print results
        runner.print_results(results)
        
        # Save results if requested
        if args.save:
            runner.save_results(results)
        
        # Generate plots if requested
        if args.plot:
            runner.plot_results(results)
        
        # Show Cerebro plot if requested
        if args.cerebro_plot:
            runner.run_cerebro_plot()
        
        print(f"\n🎉 Backtest completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Backtest interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
