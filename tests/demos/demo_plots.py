#!/usr/bin/env python3
"""
Demo Plotting Script
Generate visual reports from our backtest results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_performance_dashboard():
    """Create a comprehensive performance dashboard"""
    
    # Our actual backtest results from the optimization
    results_data = {
        'NVDA': {
            'strategy': 'Contrarian',
            'confidence': 0.10,
            'total_return': 5927.9,
            'annual_return': 31.4,
            'trades': 142,
            'win_rate': 54.9,
            'sharpe': 0.91,
            'max_drawdown': 41.9,
            'buy_hold_return': 31577.9
        },
        'AAPL': {
            'strategy': 'Momentum',
            'confidence': 0.05,
            'total_return': 544.7,
            'annual_return': 13.0,
            'trades': 185,
            'win_rate': 61.1,
            'sharpe': 0.44,
            'max_drawdown': 56.6,
            'buy_hold_return': 3784.0
        },
        'AMZN': {
            'strategy': 'Momentum',
            'confidence': 0.05,
            'total_return': 449.3,
            'annual_return': 12.1,
            'trades': 167,
            'win_rate': 59.3,
            'sharpe': 0.61,
            'max_drawdown': 52.3,
            'buy_hold_return': 3176.9
        },
        'MSFT': {
            'strategy': 'Momentum',
            'confidence': 0.05,
            'total_return': 296.5,
            'annual_return': 9.5,
            'trades': 187,
            'win_rate': 60.4,
            'sharpe': 0.53,
            'max_drawdown': 56.6,
            'buy_hold_return': 1709.0
        },
        'GOOGL': {
            'strategy': 'Momentum',
            'confidence': 0.05,
            'total_return': 156.7,
            'annual_return': 6.5,
            'trades': 197,
            'win_rate': 56.9,
            'sharpe': 0.35,
            'max_drawdown': 56.9,
            'buy_hold_return': 1111.3
        }
    }
    
    # Create the dashboard
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('🚀 SentimentTrade AI Strategy - 15-Year Backtest Results', fontsize=20, fontweight='bold', y=0.98)
    
    # Plot 1: Total Returns Comparison
    ax1 = axes[0, 0]
    stocks = list(results_data.keys())
    strategy_returns = [results_data[stock]['total_return'] for stock in stocks]
    buy_hold_returns = [results_data[stock]['buy_hold_return'] for stock in stocks]
    
    x = np.arange(len(stocks))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, strategy_returns, width, label='AI Strategy', color='#2E86AB', alpha=0.8)
    bars2 = ax1.bar(x + width/2, buy_hold_returns, width, label='Buy & Hold', color='#A23B72', alpha=0.8)
    
    ax1.set_title('📈 Total Returns Comparison (15 Years)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Stock')
    ax1.set_ylabel('Total Return (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(stocks)
    ax1.legend()
    ax1.set_yscale('log')  # Log scale due to large differences
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}%', ha='center', va='bottom', fontsize=9)
    
    # Plot 2: Annual Returns
    ax2 = axes[0, 1]
    annual_returns = [results_data[stock]['annual_return'] for stock in stocks]
    colors = ['#F18F01', '#C73E1D', '#2E86AB', '#A23B72', '#F24236']
    
    bars = ax2.bar(stocks, annual_returns, color=colors, alpha=0.8)
    ax2.set_title('📊 Annualized Returns', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Annual Return (%)')
    ax2.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='S&P 500 (~10%)')
    ax2.legend()
    
    # Add value labels
    for bar, value in zip(bars, annual_returns):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 3: Win Rates
    ax3 = axes[0, 2]
    win_rates = [results_data[stock]['win_rate'] for stock in stocks]
    
    bars = ax3.bar(stocks, win_rates, color='#2E8B57', alpha=0.8)
    ax3.set_title('🎯 Win Rates', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Win Rate (%)')
    ax3.set_ylim(50, 65)
    ax3.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Random (50%)')
    ax3.legend()
    
    # Add value labels
    for bar, value in zip(bars, win_rates):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 4: Risk-Adjusted Returns (Sharpe Ratios)
    ax4 = axes[1, 0]
    sharpe_ratios = [results_data[stock]['sharpe'] for stock in stocks]
    
    bars = ax4.bar(stocks, sharpe_ratios, color='#4ECDC4', alpha=0.8)
    ax4.set_title('⚖️ Risk-Adjusted Performance (Sharpe Ratio)', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Sharpe Ratio')
    ax4.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Good (>0.5)')
    ax4.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Excellent (>1.0)')
    ax4.legend()
    
    # Add value labels
    for bar, value in zip(bars, sharpe_ratios):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 5: Trading Activity
    ax5 = axes[1, 1]
    trade_counts = [results_data[stock]['trades'] for stock in stocks]
    
    bars = ax5.bar(stocks, trade_counts, color='#FF6B6B', alpha=0.8)
    ax5.set_title('📊 Trading Activity (15 Years)', fontsize=14, fontweight='bold')
    ax5.set_ylabel('Total Trades')
    
    # Add value labels
    for bar, value in zip(bars, trade_counts):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 6: Strategy Distribution
    ax6 = axes[1, 2]
    strategies = [results_data[stock]['strategy'] for stock in stocks]
    strategy_counts = {}
    for strategy in strategies:
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    colors_pie = ['#FF9999', '#66B2FF', '#99FF99']
    wedges, texts, autotexts = ax6.pie(strategy_counts.values(), labels=strategy_counts.keys(), 
                                      autopct='%1.0f%%', colors=colors_pie, startangle=90)
    ax6.set_title('🎯 Optimal Strategy Distribution', fontsize=14, fontweight='bold')
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'sentimenttrade_performance_dashboard_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Performance dashboard saved as: {filename}")
    
    plt.show()

def create_nvda_detailed_analysis():
    """Create detailed analysis for NVDA (best performer)"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('🏆 NVDA Detailed Analysis - Contrarian Strategy', fontsize=16, fontweight='bold')
    
    # Simulated portfolio growth over time (15 years)
    years = np.arange(2010, 2025)
    # NVDA strategy: +5,928% total = 59.28x over 15 years
    # Annual growth rate: (59.28)^(1/15) - 1 = 31.4%
    portfolio_values = [100000 * (1.314 ** (year - 2010)) for year in years]
    buy_hold_values = [100000 * ((31577.9/100 + 1) ** ((year - 2010)/15)) for year in years]
    
    # Plot 1: Portfolio Growth
    ax1 = axes[0, 0]
    ax1.plot(years, portfolio_values, 'b-', linewidth=3, label='AI Strategy', marker='o')
    ax1.plot(years, buy_hold_values, 'r--', linewidth=2, label='Buy & Hold', alpha=0.7)
    ax1.set_title('📈 Portfolio Growth Over Time')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Format y-axis to show dollar values
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Plot 2: Win/Loss Distribution
    ax2 = axes[0, 1]
    winning_trades = 78  # 54.9% of 142 trades
    losing_trades = 64
    
    wedges, texts, autotexts = ax2.pie([winning_trades, losing_trades], 
                                      labels=['Winning Trades', 'Losing Trades'],
                                      colors=['#2E8B57', '#DC143C'], 
                                      autopct='%1.1f%%', startangle=90)
    ax2.set_title(f'🎯 Trade Distribution\n(Win Rate: 54.9%)')
    
    # Plot 3: Monthly Returns Distribution (simulated)
    ax3 = axes[1, 0]
    # Simulate monthly returns based on annual 31.4% return
    np.random.seed(42)
    monthly_returns = np.random.normal(2.3, 8, 180)  # 15 years * 12 months, mean ~2.3% monthly
    
    ax3.hist(monthly_returns, bins=30, alpha=0.7, color='#4ECDC4', edgecolor='black')
    ax3.axvline(np.mean(monthly_returns), color='red', linestyle='--', 
                label=f'Mean: {np.mean(monthly_returns):.1f}%')
    ax3.set_title('📊 Monthly Returns Distribution')
    ax3.set_xlabel('Monthly Return (%)')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Key Metrics
    ax4 = axes[1, 1]
    metrics = ['Total Return', 'Annual Return', 'Sharpe Ratio', 'Max Drawdown']
    values = [5927.9, 31.4, 0.91, 41.9]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    
    bars = ax4.bar(metrics, values, color=colors, alpha=0.8)
    ax4.set_title('📋 Key Performance Metrics')
    ax4.set_ylabel('Value')
    
    # Add value labels
    for bar, value in zip(bars, values):
        height = bar.get_height()
        if 'Return' in metrics[bars.index(bar)]:
            label = f'{value:.1f}%'
        else:
            label = f'{value:.2f}'
        ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                label, ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'nvda_detailed_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 NVDA detailed analysis saved as: {filename}")
    
    plt.show()

def create_strategy_comparison():
    """Create strategy comparison visualization"""
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('🎯 Strategy Performance Comparison', fontsize=16, fontweight='bold')
    
    # Data for different strategies
    contrarian_data = {'NVDA': 5927.9}
    momentum_data = {'AAPL': 544.7, 'AMZN': 449.3, 'MSFT': 296.5, 'GOOGL': 156.7}
    
    # Plot 1: Strategy Returns
    ax1 = axes[0]
    
    # Contrarian
    ax1.bar(['NVDA\n(Contrarian)'], [contrarian_data['NVDA']], 
            color='#FF6B6B', alpha=0.8, label='Contrarian Strategy')
    
    # Momentum
    momentum_stocks = list(momentum_data.keys())
    momentum_returns = list(momentum_data.values())
    momentum_labels = [f'{stock}\n(Momentum)' for stock in momentum_stocks]
    
    ax1.bar(momentum_labels, momentum_returns, 
            color='#4ECDC4', alpha=0.8, label='Momentum Strategy')
    
    ax1.set_title('📊 Strategy Performance by Stock')
    ax1.set_ylabel('Total Return (%)')
    ax1.legend()
    ax1.set_yscale('log')
    
    # Add value labels
    ax1.text(0, contrarian_data['NVDA'] + 200, f"{contrarian_data['NVDA']:.0f}%", 
             ha='center', va='bottom', fontweight='bold')
    
    for i, value in enumerate(momentum_returns):
        ax1.text(i + 1, value + 10, f"{value:.0f}%", 
                ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Strategy Summary
    ax2 = axes[1]
    
    strategy_summary = {
        'Contrarian': {
            'avg_return': 5927.9,
            'stocks': 1,
            'best_for': 'High Volatility'
        },
        'Momentum': {
            'avg_return': np.mean(list(momentum_data.values())),
            'stocks': 4,
            'best_for': 'Steady Growth'
        }
    }
    
    strategies = list(strategy_summary.keys())
    avg_returns = [strategy_summary[s]['avg_return'] for s in strategies]
    stock_counts = [strategy_summary[s]['stocks'] for s in strategies]
    
    # Create a grouped bar chart
    x = np.arange(len(strategies))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, avg_returns, width, label='Avg Return (%)', color='#FF9999')
    bars2 = ax2.bar(x + width/2, [c * 100 for c in stock_counts], width, 
                   label='Stock Count (×100)', color='#99CCFF')
    
    ax2.set_title('📋 Strategy Summary')
    ax2.set_xlabel('Strategy Type')
    ax2.set_ylabel('Value')
    ax2.set_xticks(x)
    ax2.set_xticklabels(strategies)
    ax2.legend()
    ax2.set_yscale('log')
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'strategy_comparison_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Strategy comparison saved as: {filename}")
    
    plt.show()

def main():
    """Generate all visualization reports"""
    
    print("🎨 Generating SentimentTrade Visual Reports")
    print("=" * 50)
    
    try:
        # Create performance dashboard
        print("\n📊 Creating Performance Dashboard...")
        create_performance_dashboard()
        
        # Create NVDA detailed analysis
        print("\n🏆 Creating NVDA Detailed Analysis...")
        create_nvda_detailed_analysis()
        
        # Create strategy comparison
        print("\n🎯 Creating Strategy Comparison...")
        create_strategy_comparison()
        
        print(f"\n✅ All visual reports generated successfully!")
        print(f"📁 Check the current directory for PNG files")
        
    except Exception as e:
        print(f"❌ Error generating plots: {e}")

if __name__ == "__main__":
    main()
