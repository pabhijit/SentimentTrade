# 🤖 SentimentTrade Multi-Strategy Daily Runner

Comprehensive automated trading strategy execution with Telegram alerts. Runs **ALL your strategies** every 30 minutes during market hours with intelligent signal filtering and risk management.

## 🎯 Complete Strategy Suite

### 📊 **All Strategies Included:**
1. **Enhanced Break & Retest Strategy**: Optimized based on backtesting (AMD 57.1% win rate)
2. **Options Break & Retest Strategy**: Mechanical options trading on QQQ
3. **Default Multi-Factor Strategy**: Technical + sentiment analysis
4. **Mean Reversion Strategy**: Bollinger Bands + RSI oversold/overbought
5. **Momentum Strategy**: Trend following with breakout confirmation

### 📱 **Smart Alert System**
- **Strategy-specific thresholds** (60-70% confidence)
- **Real-time signal notifications** with detailed analysis
- **Daily comprehensive summaries** across all strategies
- **Risk management alerts** and system status updates

### ⏰ **Intelligent Automation**
- **Every 30 minutes** during market hours (9:30 AM - 4:00 PM ET)
- **Staggered execution** to avoid API rate limits
- **Market hours detection** with weekend/holiday awareness
- **Configurable limits** and risk controls

### 📈 **Based on Backtesting Results**
- **AMD**: 57.1% win rate (top performer)
- **MSFT**: 47.8% win rate (consistent performer)
- **Options on QQQ**: Mechanical strategy with ITM options
- **Risk-optimized parameters** from comprehensive backtesting

## 🚀 Quick Start

### 1. **Setup Telegram Bot**
```bash
cd scripts/automation
python setup_telegram.py
```
Follow the interactive guide to:
- Create a Telegram bot via @BotFather
- Get your bot token and chat ID
- Test the connection
- Save configuration to `.env` file

### 2. **Install Requirements**
```bash
pip install -r requirements.txt
```

### 3. **Configure Your Watchlist**
Edit `runner_config.py` to customize:
- Stock symbols to monitor
- Strategy parameters
- Alert thresholds
- Risk management settings

### 4. **Launch the Bot**
```bash
python launch_trading_bot.py
```

Or start directly:
```bash
python launch_trading_bot.py --start
```

## 📋 Configuration

### **Watchlist Configuration** (`runner_config.py`)

```python
# Break & Retest Strategy - Top performers from backtesting
BREAK_RETEST_WATCHLIST = [
    'AMD',    # 57.1% win rate
    'MSFT',   # 47.8% win rate  
    'BAC',    # 13.4% return
    'AAPL', 'NVDA', 'GOOGL', 'AMZN',
    'SPY', 'QQQ', 'JPM', 'XLF'
]

# Options Strategy - High liquidity ETFs
OPTIONS_WATCHLIST = [
    'QQQ',    # Primary focus - excellent options liquidity
]
```

### **Strategy Parameters**

Based on optimization results:
```python
'enhanced_break_retest': {
    'lookback_period': 20,
    'min_breakout_strength': 0.008,  # 0.8% optimized
    'position_size': 0.03,           # 3% risk per trade
    'trade_cooldown_days': 2,
    'regime_detection': True,        # Market adaptation
    'volatility_sizing': True,       # Dynamic sizing
    'max_portfolio_risk': 0.06,      # 6% max risk
}
```

### **Alert Settings**
```python
ALERT_CONFIG = {
    'min_confidence_for_alert': 0.60,  # 60% minimum
    'max_alerts_per_hour': 10,
    'send_daily_summary': True,
    'include_market_regime': True,
}
```

## 📱 Multi-Strategy Telegram Alerts

### **Enhanced Signal Alerts**
```
🟢 BUY SIGNAL 🟢

📊 Symbol: AMD
💰 Current Price: $142.50
🎯 Entry Price: $142.50
🛑 Stop Loss: $135.38
🚀 Target: $153.90
📈 Confidence: 72.5%

⏰ Time: 2025-01-15 10:30:00
🔧 Strategy: Enhanced Break Retest
📊 Market Regime: trending
📈 RSI: 58.3
💭 Reasoning: Bullish breakout above resistance...

SentimentTrade Multi-Strategy Bot
```

### **Mean Reversion Alert**
```
🟢 BUY SIGNAL 🟢

📊 Symbol: TSLA
💰 Current Price: $238.45
🎯 Entry Price: $238.45
🛑 Stop Loss: $226.53
🚀 Target: $257.53
📈 Confidence: 68.2%

⏰ Time: 2025-01-15 11:00:00
🔧 Strategy: Mean Reversion
📈 RSI: 24.1
📊 BB Position: 5.2%
💭 Reasoning: Oversold bounce opportunity...

SentimentTrade Multi-Strategy Bot
```

### **Comprehensive Daily Summary**
```
📊 DAILY MULTI-STRATEGY SUMMARY 📊

📅 Date: 2025-01-15
🔄 Strategy Runs: 16
📈 Total Signals: 47
🎯 Actionable Signals: 12

📊 SIGNAL BREAKDOWN:
🟢 Buy Signals: 8
🔴 Sell Signals: 4
🟡 Hold Signals: 35
📈 Avg Confidence: 64.3%

🔧 STRATEGY PERFORMANCE:
• Enhanced Break Retest: 3/12
• Options Break Retest: 1/2
• Default Strategy: 4/15
• Mean Reversion: 2/9
• Momentum: 2/9

⏰ Next Run: Every 30 minutes during market hours
🤖 Status: Active

SentimentTrade Multi-Strategy Bot
```

## 📊 Complete Strategy Details

### **1. Enhanced Break & Retest Strategy**
- **Watchlist**: AMD, MSFT, BAC, AAPL, NVDA, GOOGL, AMZN, SPY, QQQ, JPM, XLF
- **Performance**: 57.1% win rate on AMD, 47.8% on MSFT (from backtesting)
- **Features**: Market regime adaptation, volatility sizing, structure stops
- **Alert Threshold**: 65% confidence

### **2. Options Break & Retest Strategy**
- **Watchlist**: QQQ (primary), SPY (backup)
- **Target**: ITM options (0.6-0.8 delta), 30-90 days expiry
- **Risk Management**: 50% profit target, 30% stop loss
- **Alert Threshold**: 70% confidence (higher for options)

### **3. Default Multi-Factor Strategy**
- **Watchlist**: Broad market coverage (25+ symbols)
- **Analysis**: RSI, Moving Averages, Volume, Sentiment
- **Approach**: Technical (70%) + Sentiment (30%) weighting
- **Alert Threshold**: 60% confidence

### **4. Mean Reversion Strategy**
- **Watchlist**: High volatility stocks (TSLA, NVDA, AMD, etc.)
- **Indicators**: Bollinger Bands, RSI extremes, Volume confirmation
- **Focus**: Oversold/overbought conditions in ranging markets
- **Alert Threshold**: 65% confidence

### **5. Momentum Strategy**
- **Watchlist**: Trending stocks and growth ETFs
- **Analysis**: Price momentum, RSI trends, MA alignment, breakouts
- **Approach**: Multi-timeframe trend confirmation
- **Alert Threshold**: 60% confidence

## 📁 File Structure

```
scripts/automation/
├── daily_strategy_runner.py    # Main automation engine
├── runner_config.py            # Configuration settings
├── setup_telegram.py           # Telegram bot setup
├── launch_trading_bot.py       # Easy launcher
├── requirements.txt            # Python dependencies
└── README.md                   # This file

results/daily_runs/             # Strategy results
├── strategy_run_20250115_1030.json
├── strategy_run_20250115_1100.json
└── ...

logs/                          # System logs
└── daily_runner.log
```

## 🔧 Advanced Configuration

### **Environment Variables** (`.env`)
```bash
# Telegram Configuration
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional: API Keys for enhanced data
TWELVE_DATA_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### **Custom Strategy Parameters**
```python
# In runner_config.py
STRATEGY_CONFIGS = {
    'enhanced_break_retest': {
        'parameters': {
            'lookback_period': 20,
            'min_breakout_strength': 0.008,
            # ... customize as needed
        },
        'alert_threshold': 0.65,  # Custom alert threshold
    }
}
```

### **Risk Management**
```python
RISK_CONFIG = {
    'max_concurrent_signals': 8,
    'max_daily_signals': 15,
    'max_portfolio_risk': 0.10,      # 10% max portfolio risk
    'daily_loss_limit': 0.05,        # Stop if daily loss > 5%
    'consecutive_loss_limit': 3,     # Stop after 3 losses
}
```

## 📈 Monitoring & Results

### **Real-time Monitoring**
- Telegram alerts for all actionable signals
- System status updates
- Error notifications
- Daily performance summaries

### **Results Storage**
- JSON files for each strategy run
- Historical performance tracking
- Configurable retention (90 days default)
- Compressed archives for long-term storage

### **Performance Metrics**
- Win rate tracking
- Average P&L per signal
- Strategy-specific performance
- Market regime analysis

## 🛠️ Troubleshooting

### **Common Issues**

1. **Telegram Not Working**
   ```bash
   python setup_telegram.py  # Reconfigure
   ```

2. **Missing Data**
   - Check internet connection
   - Verify yfinance is working
   - Check symbol validity

3. **No Signals Generated**
   - Market may be outside hours
   - No setups detected (normal)
   - Check configuration thresholds

4. **High Memory Usage**
   - Reduce lookback_days in DATA_CONFIG
   - Enable data caching
   - Restart daily to clear memory

### **Logs and Debugging**
```bash
# Check logs
tail -f logs/daily_runner.log

# Test individual components
python -c "from telegram_alerts import test_telegram; test_telegram()"
```

## 🔒 Security Notes

- **Never commit `.env` file** to version control
- **Keep Telegram bot token secure**
- **Use paper trading first** to validate
- **Monitor for unusual activity**
- **Set appropriate risk limits**

## 📞 Support

For issues or questions:
1. Check the logs in `logs/daily_runner.log`
2. Review configuration in `runner_config.py`
3. Test Telegram connection
4. Verify market hours and data availability

## 🎯 Next Steps

1. **Run for 2-3 months** to validate live performance
2. **Track results** vs backtesting expectations
3. **Adjust parameters** based on live performance
4. **Scale up position sizes** once confident
5. **Add more strategies** as they're developed

---

**⚠️ Disclaimer**: This is for educational and research purposes. Always paper trade first and never risk more than you can afford to lose.
