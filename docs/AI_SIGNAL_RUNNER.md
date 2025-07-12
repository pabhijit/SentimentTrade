# 🤖 AI Signal Generator Runner

Independent runner for testing and executing the SentimentTrade AI trading signal generator.

## 🚀 **Quick Start**

### **Basic Usage**
```bash
# Demo mode (recommended first test)
python run_ai_signals.py --demo

# Single symbol analysis
python run_ai_signals.py --symbol AAPL

# Multiple symbols
python run_ai_signals.py --watchlist AAPL MSFT GOOGL

# Configuration check
python run_ai_signals.py --config-check
```

## 📋 **Command Options**

### **Available Arguments**
```
python run_ai_signals.py [OPTIONS]

Options:
  -s, --symbol SYMBOL     Single symbol to analyze (e.g., AAPL)
  -w, --watchlist SYMBOLS Multiple symbols (e.g., AAPL MSFT GOOGL)
  -u, --user EMAIL        User email for personalized preferences
  -d, --demo             Run demonstration mode
  --save                 Save results to JSON file
  --config-check         Check configuration and exit
  -h, --help             Show help message
```

### **Usage Examples**

#### **Configuration Check**
```bash
# Verify API keys and setup
python run_ai_signals.py --config-check

# Expected output:
# ⚙️ Configuration Check
# Configuration Valid: ✅ YES
# 
# Or if missing keys:
# Configuration Valid: ❌ NO
# Missing API Keys: OPENAI_API_KEY, TWELVE_DATA_API_KEY
```

#### **Demo Mode**
```bash
# Run comprehensive demo
python run_ai_signals.py --demo

# Save demo results
python run_ai_signals.py --demo --save

# Expected output:
# 🎬 SentimentTrade AI Signal Generator Demo
# ============================================================
# 📅 Date: 2024-07-12 10:30:00
# ⚙️ Using default configuration
# 
# 🔍 Single Symbol Test: AAPL
# Action: BUY
# Confidence: 75.2%
# Current Price: $150.25
# Risk/Reward Ratio: 2.15
```

#### **Single Symbol Analysis**
```bash
# Analyze specific stock
python run_ai_signals.py --symbol AAPL
python run_ai_signals.py --symbol MSFT

# With user preferences
python run_ai_signals.py --symbol AAPL --user john@example.com

# Save results
python run_ai_signals.py --symbol AAPL --save
```

#### **Watchlist Analysis**
```bash
# Multiple symbols
python run_ai_signals.py --watchlist AAPL MSFT GOOGL AMZN TSLA

# Large watchlist with results saved
python run_ai_signals.py --watchlist AAPL MSFT GOOGL AMZN TSLA NVDA META --save

# Expected output:
# 📊 Watchlist Signal Results
# ============================================================
# Total Symbols Analyzed: 5
# Actionable Signals: 3
# Hold Recommendations: 2
# 
# 🎯 Top Actionable Signals:
# 1. AAPL - BUY (75.2%)
#    Price: $150.25 | Target: $172.79
```

## 📊 **Understanding Output**

### **Signal Fields**
```json
{
  "symbol": "AAPL",           // Stock symbol
  "action": "BUY",            // BUY, SELL, or HOLD
  "confidence": 0.752,        // Confidence level (0.0 to 1.0)
  "current_price": 150.25,    // Current stock price
  "entry_price": 150.25,      // Recommended entry price
  "stop_loss": 142.74,        // Stop loss price
  "target_price": 172.79,     // Take profit target
  "risk_reward_ratio": 2.15,  // Risk/reward ratio
  "sentiment": 0.342,         // Sentiment score (-1 to 1)
  "strategy": "Default Strategy",
  "reasoning": "Technical analysis shows BUY signal..."
}
```

### **Action Types**
- **BUY** - Strong bullish signal, consider long position
- **SELL** - Strong bearish signal, consider short position  
- **HOLD** - No clear signal, maintain current position
- **ERROR** - Analysis failed, check logs for details

### **Confidence Levels**
- **80%+** - Very high confidence, strong signal
- **70-79%** - High confidence, good signal
- **60-69%** - Moderate confidence, proceed with caution
- **<60%** - Low confidence, filtered out by default

## 👤 **User Preferences**

### **Personalized Analysis**
```bash
# Use specific user's preferences
python run_ai_signals.py --symbol AAPL --user conservative@example.com
python run_ai_signals.py --symbol AAPL --user aggressive@example.com
```

### **Preference Impact**
- **Conservative Users**: Higher confidence thresholds, tighter stops
- **Moderate Users**: Balanced approach with standard settings
- **Aggressive Users**: Lower confidence thresholds, wider stops

## 🔧 **Configuration Requirements**

### **Required API Keys**
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your API keys:
OPENAI_API_KEY=your_openai_api_key_here
TWELVE_DATA_API_KEY=your_twelve_data_api_key_here
```

### **Optional API Keys**
```bash
# For enhanced functionality (optional):
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
```

### **Configuration Validation**
```bash
# Check your setup
python run_ai_signals.py --config-check

# Initialize database if needed
python -c "from src.database import init_database; init_database()"
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Missing API Keys**
```bash
# Error: Missing required API keys
# Solution: Configure .env file
cp .env.template .env
# Edit .env with your API keys
```

#### **Database Errors**
```bash
# Error: Database connection failed
# Solution: Initialize database
python -c "from src.database import init_database; init_database()"
```

#### **Network/API Errors**
```bash
# Error: Failed to fetch market data
# Solution: Check internet connection and API key validity
python run_ai_signals.py --config-check
```

#### **Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Run from project root directory
cd SentimentTrade-main
python run_ai_signals.py --demo
```

### **Debug Mode**
```bash
# Enable detailed logging
python run_ai_signals.py --demo --save

# Check log files
tail -f logs/sentimenttrade.log
```

## 💾 **Saving Results**

### **JSON Output**
```bash
# Save results to timestamped file
python run_ai_signals.py --demo --save

# Results saved to: signal_results_20240712_103000.json
```

### **Result File Format**
```json
{
  "single_result": {
    "symbol": "AAPL",
    "action": "BUY",
    "confidence": 0.752,
    // ... full signal data
  },
  "watchlist_results": [
    // Array of signal results
  ],
  "summary": {
    "total_symbols": 5,
    "actionable_signals": 3,
    "success_rate": 1.0
  }
}
```

## 🔗 **Integration**

### **Development Workflow**
```bash
# 1. Test signal generation
python run_ai_signals.py --demo

# 2. Test specific symbols
python run_ai_signals.py --symbol AAPL

# 3. Start API server
python api/main_enhanced.py

# 4. Test API integration
curl -X POST "http://localhost:8000/signal" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}'
```

### **Testing New Strategies**
```bash
# Test default strategy
python run_ai_signals.py --demo

# Test with different user preferences
python run_ai_signals.py --symbol AAPL --user test@example.com
```

### **Performance Analysis**
```bash
# Generate comprehensive results
python run_ai_signals.py --watchlist AAPL MSFT GOOGL AMZN TSLA --save

# Analyze saved JSON results for strategy performance
```

## 🎯 **Best Practices**

### **Before Development**
1. **Configuration Check**: `python run_ai_signals.py --config-check`
2. **Demo Test**: `python run_ai_signals.py --demo`
3. **Single Symbol Test**: `python run_ai_signals.py --symbol AAPL`

### **During Development**
1. **Test Changes**: Run specific symbol tests after code changes
2. **Save Results**: Use `--save` flag to track performance over time
3. **User Testing**: Test with different user preference profiles

### **Before Deployment**
1. **Comprehensive Test**: Run full watchlist analysis
2. **Performance Validation**: Check confidence levels and success rates
3. **API Integration**: Verify API server integration works correctly

The AI Signal Runner provides a comprehensive, independent way to test and validate the SentimentTrade signal generation system! 🚀
