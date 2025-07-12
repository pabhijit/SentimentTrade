#!/usr/bin/env python3
"""
ETF vs Individual Stocks Comparison Visualization
Comprehensive analysis of ETF performance vs individual stock performance
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_etf_summary_comparison():
    """Create a focused comparison between ETFs and individual stocks"""
    
    # Our results data
    individual_stocks = {
        'NVDA': {'annual_return': 31.4, 'sharpe': 0.91, 'win_rate': 54.9, 'max_drawdown': 41.9},
        'AAPL': {'annual_return': 13.0, 'sharpe': 0.44, 'win_rate': 61.1, 'max_drawdown': 56.6},
        'AMZN': {'annual_return': 12.1, 'sharpe': 0.61, 'win_rate': 59.3, 'max_drawdown': 52.3},
        'MSFT': {'annual_return': 9.5, 'sharpe': 0.53, 'win_rate': 60.4, 'max_drawdown': 56.6},
        'GOOGL': {'annual_return': 6.5, 'sharpe': 0.35, 'win_rate': 56.9, 'max_drawdown': 56.9}
    }
    
    etfs = {
        'SPY': {'annual_return': 5.2, 'sharpe': 0.42, 'win_rate': 53.7, 'max_drawdown': 27.9, 'buy_hold': 8.1},
        'QQQ': {'annual_return': 3.3, 'sharpe': 0.23, 'win_rate': 52.8, 'max_drawdown': 70.1, 'buy_hold': 5.9}
    }
    
    # Create comparison dashboard
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('📊 SentimentTrade: ETFs vs Individual Stocks Performance', 
                 fontsize=18, fontweight='bold', y=0.98)
    
    # Combine all data
    all_assets = {**individual_stocks, **etfs}
    asset_names = list(all_assets.keys())
    
    # Plot 1: Annual Returns Comparison
    ax1 = axes[0, 0]
    annual_returns = [all_assets[asset]['annual_return'] for asset in asset_names]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    bars = ax1.bar(asset_names, annual_returns, color=colors, alpha=0.8)
    ax1.set_title('📈 Annual Returns Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Annual Return (%)')
    ax1.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='S&P 500 (~10%)')
    ax1.legend()
    plt.setp(ax1.get_xticklabels(), rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, annual_returns):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Risk-Adjusted Returns (Sharpe Ratios)
    ax2 = axes[0, 1]
    sharpe_ratios = [all_assets[asset]['sharpe'] for asset in asset_names]
    
    bars = ax2.bar(asset_names, sharpe_ratios, color=colors, alpha=0.8)
    ax2.set_title('⚖️ Risk-Adjusted Performance (Sharpe Ratio)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Sharpe Ratio')
    ax2.axhline(y=0.5, color='orange', linestyle='--', alpha=0.7, label='Good (>0.5)')
    ax2.axhline(y=1.0, color='green', linestyle='--', alpha=0.7, label='Excellent (>1.0)')
    ax2.legend()
    plt.setp(ax2.get_xticklabels(), rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, sharpe_ratios):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 3: Win Rates
    ax3 = axes[1, 0]
    win_rates = [all_assets[asset]['win_rate'] for asset in asset_names]
    
    bars = ax3.bar(asset_names, win_rates, color=colors, alpha=0.8)
    ax3.set_title('🎯 Win Rates', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Win Rate (%)')
    ax3.set_ylim(50, 65)
    ax3.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Random (50%)')
    ax3.legend()
    plt.setp(ax3.get_xticklabels(), rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, win_rates):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 4: Max Drawdown (Risk)
    ax4 = axes[1, 1]
    drawdowns = [all_assets[asset]['max_drawdown'] for asset in asset_names]
    
    bars = ax4.bar(asset_names, drawdowns, color=colors, alpha=0.8)
    ax4.set_title('📉 Maximum Drawdown (Risk)', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Max Drawdown (%)')
    ax4.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Low Risk (<30%)')
    ax4.axhline(y=50, color='orange', linestyle='--', alpha=0.7, label='Moderate Risk (<50%)')
    ax4.legend()
    plt.setp(ax4.get_xticklabels(), rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, drawdowns):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'etf_vs_stocks_comparison_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 ETF vs Stocks comparison saved as: {filename}")
    
    plt.show()

def create_etf_detailed_analysis():
    """Create detailed analysis of ETF performance"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('📊 ETF Detailed Performance Analysis', fontsize=16, fontweight='bold')
    
    # ETF data
    etf_data = {
        'SPY': {
            'annual_return': 5.2,
            'buy_hold_annual': 8.1,
            'sharpe': 0.42,
            'max_drawdown': 27.9,
            'win_rate': 53.7,
            'trades': 218,
            'years': 31.2
        },
        'QQQ': {
            'annual_return': 3.3,
            'buy_hold_annual': 5.9,
            'sharpe': 0.23,
            'max_drawdown': 70.1,
            'win_rate': 52.8,
            'trades': 180,
            'years': 25.1
        }
    }
    
    # Plot 1: Strategy vs Buy & Hold
    ax1 = axes[0, 0]
    etfs = list(etf_data.keys())
    strategy_returns = [etf_data[etf]['annual_return'] for etf in etfs]
    buy_hold_returns = [etf_data[etf]['buy_hold_annual'] for etf in etfs]
    
    x = np.arange(len(etfs))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, strategy_returns, width, label='AI Strategy', color='#4ECDC4', alpha=0.8)
    bars2 = ax1.bar(x + width/2, buy_hold_returns, width, label='Buy & Hold', color='#FF6B6B', alpha=0.8)
    
    ax1.set_title('📈 AI Strategy vs Buy & Hold', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Annual Return (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(etfs)
    ax1.legend()
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Risk Comparison
    ax2 = axes[0, 1]
    sharpe_ratios = [etf_data[etf]['sharpe'] for etf in etfs]
    drawdowns = [etf_data[etf]['max_drawdown'] for etf in etfs]
    
    # Create grouped bar chart
    x = np.arange(len(etfs))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, sharpe_ratios, width, label='Sharpe Ratio', color='#45B7D1', alpha=0.8)
    bars2 = ax2.bar(x + width/2, [d/100 for d in drawdowns], width, label='Max Drawdown (scaled)', color='#FF9999', alpha=0.8)
    
    ax2.set_title('⚖️ Risk Metrics Comparison', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Value')
    ax2.set_xticks(x)
    ax2.set_xticklabels(etfs)
    ax2.legend()
    
    # Plot 3: Trading Efficiency
    ax3 = axes[1, 0]
    win_rates = [etf_data[etf]['win_rate'] for etf in etfs]
    trade_counts = [etf_data[etf]['trades'] for etf in etfs]
    
    # Scatter plot
    colors = ['#4ECDC4', '#FF6B6B']
    for i, etf in enumerate(etfs):
        ax3.scatter(trade_counts[i], win_rates[i], s=200, c=colors[i], alpha=0.7, label=etf)
        ax3.annotate(etf, (trade_counts[i], win_rates[i]), xytext=(5, 5), 
                    textcoords='offset points', fontsize=12, fontweight='bold')
    
    ax3.set_title('🎯 Trading Efficiency', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Total Trades')
    ax3.set_ylabel('Win Rate (%)')
    ax3.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Random (50%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Time Period Analysis
    ax4 = axes[1, 1]
    years = [etf_data[etf]['years'] for etf in etfs]
    annual_returns = [etf_data[etf]['annual_return'] for etf in etfs]
    
    bars = ax4.bar(etfs, annual_returns, color=['#4ECDC4', '#FF6B6B'], alpha=0.8)
    ax4.set_title('📅 Performance by Time Period', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Annual Return (%)')
    
    # Add time period labels
    for i, (bar, year) in enumerate(zip(bars, years)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}%\n({year:.1f} years)', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'etf_detailed_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 ETF detailed analysis saved as: {filename}")
    
    plt.show()

def main():
    """Generate all ETF comparison visualizations"""
    
    print("🎨 Generating ETF vs Stocks Comparison Reports")
    print("=" * 60)
    
    try:
        # Create comprehensive comparison
        print("\n📊 Creating ETF vs Stocks Comparison...")
        create_etf_summary_comparison()
        
        # Create ETF detailed analysis
        print("\n📈 Creating ETF Detailed Analysis...")
        create_etf_detailed_analysis()
        
        print(f"\n✅ All ETF comparison reports generated successfully!")
        print(f"📁 Check the current directory for PNG files")
        
    except Exception as e:
        print(f"❌ Error generating plots: {e}")

if __name__ == "__main__":
    main()
