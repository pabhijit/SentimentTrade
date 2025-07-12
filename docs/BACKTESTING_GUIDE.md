# 📊 SentimentTrade AI Backtesting Guide

Comprehensive backtesting system for validating AI trading strategies using historical data with mocked sentiment signals.

## 🎯 **What is Backtesting?**

**Backtesting** tests your AI trading strategy against historical market data to evaluate how it would have performed in the past. This helps you:

- **📈 Validate Strategy Performance** - See if your AI signals would have been profitable
- **📊 Calculate Risk Metrics** - Understand drawdowns, volatility, and risk-adjusted returns
- **🔧 Optimize Parameters** - Fine-tune confidence thresholds and risk management
- **🛡️ Build Confidence** - Validate strategy before live trading
- **📋 Compare Approaches** - Test different sentiment styles and user preferences

## 🚀 **Quick Start**

### **Basic Backtest**
```bash
# Run backtest with default settings
python run_backtest.py

# Expected output:
# 🚀 Setting up AI Backtest
#    Data File: data/test_data/random_gen.csv
#    Initial Cash: $100,000.00
#    Sentiment Style: realistic
# 
# 🚀 Starting AI Backtest
#    Starting Portfolio Value: $100,000.00
#    Final Portfolio Value: $102,450.00
#    Total Return: 2.45%
```

### **Custom Backtest**
```bash
# Custom parameters
python run_backtest.py \
  --cash 50000 \
  --sentiment contrarian \
  --confidence 0.8 \
  --save \
  --plot

# With user preferences
python run_backtest.py \
  --user john@example.com \
  --sentiment realistic \
  --save
```

## 📋 **Command Options**

### **Available Arguments**
```
python run_backtest.py [OPTIONS]

Data & Setup:
  -d, --data FILE       Path to CSV data file (default: data/test_data/random_gen.csv)
  -c, --cash AMOUNT     Initial cash amount (default: 100000.0)
  --commission RATE     Commission rate (default: 0.001 = 0.1%)

Strategy Configuration:
  -u, --user EMAIL      User email for personalized preferences
  -s, --sentiment STYLE Sentiment generation style (see below)
  --confidence LEVEL    Minimum confidence threshold (default: 0.7)

Output Options:
  --save               Save results to JSON file
  --plot               Generate result plots (requires matplotlib)
  --cerebro-plot       Show Cerebro candlestick plot
```

### **Sentiment Generation Styles**

#### **realistic** *(Default)*
- Combines price momentum, volume analysis, and technical indicators
- Adds realistic noise and sentiment persistence
- Most representative of real market sentiment

#### **contrarian**
- Generates sentiment opposite to price momentum
- Useful for testing contrarian strategies
- Higher sentiment when prices fall, lower when prices rise

#### **momentum**
- Generates sentiment aligned with price momentum
- Tests momentum-following strategies
- Higher sentiment when prices rise, lower when prices fall

#### **random**
- Pure random sentiment between -1.0 and 1.0
- Baseline for testing if strategy beats random signals
- Useful for statistical significance testing

#### **neutral**
- Always returns 0.0 sentiment (neutral)
- Tests strategy performance without sentiment influence
- Pure technical analysis approach

## 📊 **Understanding Results**

### **Performance Summary**
```
💰 Performance Summary:
   Initial Value: $100,000.00
   Final Value: $102,450.00
   Total Return: 2.45%
   Absolute Gain: $2,450.00
```

### **Trading Statistics**
```
🎯 Trading Statistics:
   Total Trades: 15
   Winning Trades: 9
   Losing Trades: 6
   Win Rate: 60.0%
   Average PnL per Trade: $163.33
   Total Signals Generated: 1,247
```

### **Risk-Adjusted Performance**
```
📈 Risk-Adjusted Performance:
   Sharpe Ratio: 1.245        # > 1.0 is good, > 2.0 is excellent
   Max Drawdown: -3.2%        # Maximum peak-to-trough decline
   Max Drawdown Duration: 45  # Periods in drawdown
```

### **System Quality**
```
🎲 System Quality:
   SQN Score: 2.15            # System Quality Number
   Quality: Good (>= 2.0)     # Excellent >= 3.0, Good >= 2.0, Average >= 1.0
```

## 🔧 **Advanced Usage**

### **Testing Different Strategies**

#### **Conservative User Profile**
```bash
# Test with conservative user preferences
python run_backtest.py \
  --user conservative@example.com \
  --sentiment realistic \
  --confidence 0.8 \
  --save

# Expected: Higher confidence threshold, tighter risk management
```

#### **Aggressive User Profile**
```bash
# Test with aggressive user preferences
python run_backtest.py \
  --user aggressive@example.com \
  --sentiment momentum \
  --confidence 0.6 \
  --save

# Expected: Lower confidence threshold, wider risk management
```

### **Sentiment Style Comparison**
```bash
# Test all sentiment styles
for style in realistic contrarian momentum random neutral; do
  echo "Testing $style sentiment..."
  python run_backtest.py \
    --sentiment $style \
    --save \
    --confidence 0.7
done

# Compare results from saved JSON files
```

### **Parameter Optimization**
```bash
# Test different confidence thresholds
for conf in 0.5 0.6 0.7 0.8 0.9; do
  echo "Testing confidence $conf..."
  python run_backtest.py \
    --confidence $conf \
    --sentiment realistic \
    --save
done
```

## 📈 **Data Requirements**

### **CSV Data Format**
Your CSV file should have these columns:
```csv
datetime,open,high,low,close,volume
2025-07-10 18:12:58.895192,150.22,150.33,149.88,149.98,4668
2025-07-10 18:13:58.895192,150.08,150.26,149.92,150.05,4729
```

### **Using Your Own Data**
```bash
# Use custom data file
python run_backtest.py --data /path/to/your/data.csv

# Data requirements:
# - CSV format with headers
# - datetime column in YYYY-MM-DD HH:MM:SS format
# - OHLCV columns (open, high, low, close, volume)
# - At least 60+ rows for technical analysis
```

### **Data Sources**
- **Provided**: `data/test_data/random_gen.csv` (synthetic data for testing)
- **Real Data**: Download from Yahoo Finance, Alpha Vantage, or TwelveData
- **Custom Data**: Any CSV following the required format

## 🎨 **Visualization & Analysis**

### **Result Plots**
```bash
# Generate comprehensive plots
python run_backtest.py --plot --save

# Creates:
# - Portfolio performance chart
# - Win/loss distribution pie chart
# - Signal confidence histogram
# - Key performance metrics bar chart
```

### **Cerebro Candlestick Plot**
```bash
# Show detailed candlestick chart with trades
python run_backtest.py --cerebro-plot

# Shows:
# - Price candlesticks
# - Buy/sell markers
# - Technical indicators
# - Trade entry/exit points
```

### **JSON Results Analysis**
```python
import json
import pandas as pd

# Load saved results
with open('backtest_results_20240712_103000.json', 'r') as f:
    results = json.load(f)

# Analyze trade history
trades_df = pd.DataFrame(results['trade_history'])
print(f"Average trade duration: {trades_df['duration'].mean():.1f} periods")
print(f"Best trade: ${trades_df['pnl'].max():.2f}")
print(f"Worst trade: ${trades_df['pnl'].min():.2f}")

# Analyze signal history
signals_df = pd.DataFrame([s['signal'] for s in results['signal_history']])
actionable_signals = signals_df[signals_df['action'] != 'HOLD']
print(f"Signal conversion rate: {len(trades_df) / len(actionable_signals):.1%}")
```

## 🔍 **Interpreting Results**

### **Good Performance Indicators**
- **✅ Positive Total Return** - Strategy is profitable
- **✅ Win Rate > 50%** - More winning than losing trades
- **✅ Sharpe Ratio > 1.0** - Good risk-adjusted returns
- **✅ Max Drawdown < 10%** - Reasonable risk management
- **✅ SQN Score > 2.0** - Good system quality

### **Warning Signs**
- **⚠️ High Drawdown** - Strategy may be too risky
- **⚠️ Low Win Rate** - Many losing trades (but could be offset by large winners)
- **⚠️ Few Trades** - Strategy may be too conservative
- **⚠️ Negative Sharpe** - Poor risk-adjusted performance

### **Strategy Validation**
```bash
# Test against random baseline
python run_backtest.py --sentiment random --save
python run_backtest.py --sentiment realistic --save

# Compare results:
# - Realistic sentiment should outperform random
# - If not, strategy may not be adding value
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Data Loading Errors**
```bash
# Error: Data file not found
# Solution: Check file path and format
ls -la data/test_data/random_gen.csv
head -5 data/test_data/random_gen.csv
```

#### **No Trades Executed**
```bash
# Possible causes:
# 1. Confidence threshold too high
python run_backtest.py --confidence 0.5

# 2. Sentiment style not generating actionable signals
python run_backtest.py --sentiment momentum

# 3. Insufficient data
# Ensure CSV has 60+ rows for technical analysis
```

#### **Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Install missing dependencies
pip install backtrader matplotlib seaborn

# Or run from project root
cd SentimentTrade-main
python run_backtest.py
```

#### **Plotting Issues**
```bash
# Error: Matplotlib not available
# Solution: Install plotting libraries
pip install matplotlib seaborn

# Or run without plots
python run_backtest.py --save  # Skip --plot flag
```

### **Performance Issues**
```bash
# Slow backtests with large datasets:
# 1. Reduce data size for testing
head -1000 large_data.csv > test_data.csv

# 2. Increase confidence threshold to reduce trades
python run_backtest.py --confidence 0.8

# 3. Use simpler sentiment style
python run_backtest.py --sentiment neutral
```

## 📊 **Best Practices**

### **Strategy Development Workflow**
1. **Start Simple** - Test with default parameters
2. **Validate Data** - Ensure data quality and completeness
3. **Test Baselines** - Compare against random and neutral sentiment
4. **Optimize Parameters** - Test different confidence thresholds
5. **Validate Robustness** - Test with different sentiment styles
6. **Document Results** - Save and analyze comprehensive results

### **Statistical Significance**
```bash
# Run multiple backtests with different random seeds
for seed in 1 2 3 4 5; do
  python run_backtest.py \
    --sentiment realistic \
    --save \
    # Note: Add seed parameter to sentiment mocker if needed
done

# Analyze consistency across runs
```

### **Risk Management Validation**
```bash
# Test extreme scenarios
python run_backtest.py --sentiment contrarian --confidence 0.5
python run_backtest.py --sentiment momentum --confidence 0.9

# Ensure strategy handles different market conditions
```

## 🎯 **Next Steps**

### **Strategy Improvement**
- **Optimize Confidence Thresholds** - Find optimal risk/reward balance
- **Test Multiple Timeframes** - Validate across different time periods
- **Add Position Sizing** - Implement dynamic position sizing based on confidence
- **Enhance Risk Management** - Add trailing stops and dynamic targets

### **Advanced Analysis**
- **Monte Carlo Simulation** - Test strategy robustness
- **Walk-Forward Analysis** - Test strategy stability over time
- **Multi-Asset Backtesting** - Test across different symbols
- **Market Regime Analysis** - Performance in different market conditions

### **Production Deployment**
- **Paper Trading** - Test with live data but no real money
- **Small Position Testing** - Start with minimal capital
- **Performance Monitoring** - Track live vs backtest performance
- **Continuous Optimization** - Regular strategy review and improvement

The backtesting system provides a comprehensive foundation for validating and optimizing your AI trading strategies before risking real capital! 🚀
