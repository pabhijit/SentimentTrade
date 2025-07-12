# 🚀 SentimentTrade Quick Start Guide

Get SentimentTrade up and running in minutes with this comprehensive setup guide.

## 📋 **Prerequisites**

### **System Requirements**
- **Python 3.8+** (for backend and AI engine)
- **Node.js 16+** (for any web components)
- **Flutter 3.0+** (for mobile app development)
- **Git** (for version control)

### **API Keys (Optional but Recommended)**
- **OpenAI API Key** - For sentiment analysis
- **TwelveData API Key** - For market data
- **Telegram Bot Token** - For notifications (optional)
- **Alpaca API Keys** - For paper/live trading (optional)

## ⚡ **Quick Setup (5 Minutes)**

### **1. Clone and Setup**
```bash
# Clone the repository
git clone <repository-url>
cd SentimentTrade-main

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_database; init_database()"
```

### **2. Configure Environment (Optional)**
```bash
# Copy environment template
cp .env.template .env

# Edit with your API keys (optional for basic testing)
nano .env  # or use your preferred editor
```

### **3. Test the AI Signal Generator**
```bash
# Run AI signal generator with demo mode
python run_ai_signals.py --demo

# Test specific symbol
python run_ai_signals.py --symbol AAPL

# Test multiple symbols
python run_ai_signals.py --watchlist AAPL MSFT GOOGL

# Check configuration
python run_ai_signals.py --config-check
```

### **4. Run AI Backtesting**
```bash
# Test your AI strategy against historical data
python run_backtest.py --save --plot

# Quick backtest with different sentiment styles
python run_backtest.py --sentiment realistic
python run_backtest.py --sentiment contrarian
python run_backtest.py --sentiment momentum

# Expected output:
# 🚀 Starting AI Backtest
# Starting Portfolio Value: $100,000.00
# Final Portfolio Value: $102,450.00
# Total Return: 2.45%
```
```bash
# Start enhanced API server
python api/main_enhanced.py

# Visit: http://localhost:8000/docs for API documentation
```

### **5. Run Mobile App (Optional)**
```bash
# In a new terminal
cd mobile_app
flutter pub get
flutter run

# Or for web testing
flutter run -d chrome
```

## 📊 **AI Strategy Backtesting**

### **Validate Your Strategy with Historical Data**

Before deploying your AI trading strategy, validate its performance using historical backtesting.

#### **Quick Backtest**
```bash
# Run backtest with default settings
python run_backtest.py

# Expected output:
# 🚀 Setting up AI Backtest
#    Data File: data/test_data/random_gen.csv
#    Initial Cash: $100,000.00
#    Sentiment Style: realistic
# 
# 📊 AI Backtest Results
# ============================================================
# 💰 Performance Summary:
#    Initial Value: $100,000.00
#    Final Portfolio Value: $102,450.00
#    Total Return: 2.45%
#    Win Rate: 60.0%
```

#### **Advanced Backtesting**
```bash
# Test different sentiment styles
python run_backtest.py --sentiment realistic --save
python run_backtest.py --sentiment contrarian --save
python run_backtest.py --sentiment momentum --save

# Test with user preferences
python run_backtest.py --user john@example.com --save

# Generate comprehensive analysis
python run_backtest.py --save --plot --cerebro-plot
```

#### **Backtest Parameters**
```bash
python run_backtest.py [OPTIONS]

Key Options:
  -d, --data FILE       CSV data file (default: test data)
  -c, --cash AMOUNT     Initial capital (default: $100,000)
  -s, --sentiment STYLE Sentiment style (realistic/contrarian/momentum/random/neutral)
  --confidence LEVEL    Min confidence threshold (default: 0.7)
  -u, --user EMAIL      User email for personalized preferences
  --save               Save results to JSON
  --plot               Generate performance plots
  --cerebro-plot       Show candlestick chart with trades
```

#### **Understanding Backtest Results**

**Performance Metrics:**
- **Total Return** - Overall strategy profitability
- **Win Rate** - Percentage of profitable trades
- **Sharpe Ratio** - Risk-adjusted returns (>1.0 is good, >2.0 is excellent)
- **Max Drawdown** - Largest peak-to-trough decline
- **SQN Score** - System Quality Number (>2.0 is good, >3.0 is excellent)

**Sentiment Styles:**
- **realistic** - Combines price momentum, volume, and technical indicators
- **contrarian** - Opposite to price momentum (buy when falling, sell when rising)
- **momentum** - Aligned with price momentum (buy when rising, sell when falling)
- **random** - Random sentiment for baseline comparison
- **neutral** - No sentiment influence (pure technical analysis)

#### **Strategy Validation Workflow**
```bash
# 1. Test baseline performance
python run_backtest.py --sentiment neutral --save

# 2. Test with realistic sentiment
python run_backtest.py --sentiment realistic --save

# 3. Compare different confidence thresholds
python run_backtest.py --confidence 0.6 --save
python run_backtest.py --confidence 0.8 --save

# 4. Test with user preferences
python run_backtest.py --user conservative@example.com --save
python run_backtest.py --user aggressive@example.com --save

# 5. Generate comprehensive analysis
python run_backtest.py --sentiment realistic --plot --save
```

For detailed backtesting guide, see **[Backtesting Documentation](docs/BACKTESTING_GUIDE.md)**.

## 🤖 **AI Signal Generator Testing**

### **Independent Signal Testing**

The AI signal generator can be run and tested independently using the dedicated runner script.

#### **Basic Usage**
```bash
# Demo mode (recommended for first test)
python run_ai_signals.py --demo

# Expected output:
# 🎬 SentimentTrade AI Signal Generator Demo
# ============================================================
# 📅 Date: 2024-07-12 10:30:00
# ⚙️ Using default configuration
# 
# 🔍 Single Symbol Test: AAPL
# ==================================================
# Action: BUY
# Confidence: 75.2%
# Current Price: $150.25
# Entry Price: $150.25
# Stop Loss: $142.74
# Target Price: $172.79
# Risk/Reward Ratio: 2.15
# Sentiment Score: 0.342
# Strategy: Default Strategy
```

#### **Single Symbol Analysis**
```bash
# Analyze specific stock
python run_ai_signals.py --symbol AAPL
python run_ai_signals.py --symbol MSFT
python run_ai_signals.py --symbol GOOGL

# With user preferences (if user exists)
python run_ai_signals.py --symbol AAPL --user test@example.com
```

#### **Watchlist Analysis**
```bash
# Analyze multiple symbols
python run_ai_signals.py --watchlist AAPL MSFT GOOGL AMZN TSLA

# Save results to JSON file
python run_ai_signals.py --watchlist AAPL MSFT GOOGL --save

# Expected output:
# 📊 Watchlist Signal Results
# ============================================================
# Total Symbols Analyzed: 5
# Actionable Signals: 3
# Hold Recommendations: 2
# 
# 🎯 Top Actionable Signals:
# ----------------------------------------
# 1. AAPL - BUY (75.2%)
#    Price: $150.25 | Target: $172.79
#    Risk/Reward: 2.15
```

#### **Configuration Check**
```bash
# Verify API keys and configuration
python run_ai_signals.py --config-check

# Expected output:
# ⚙️ Configuration Check
# ------------------------------
# Configuration Valid: ✅ YES
# 
# Or if missing keys:
# Configuration Valid: ❌ NO
# Missing API Keys: OPENAI_API_KEY, TWELVE_DATA_API_KEY
```

### **Runner Command Options**

#### **Available Arguments**
```bash
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

#### **Usage Examples**
```bash
# Demo with all features
python run_ai_signals.py --demo --save

# Quick single symbol test
python run_ai_signals.py -s AAPL

# Comprehensive watchlist analysis
python run_ai_signals.py -w AAPL MSFT GOOGL AMZN TSLA NVDA META --save

# Personalized analysis for specific user
python run_ai_signals.py -s AAPL -u john@example.com

# Configuration validation
python run_ai_signals.py --config-check
```

### **Understanding Signal Output**

#### **Signal Fields Explained**
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

#### **Action Types**
- **BUY** - Strong bullish signal, consider long position
- **SELL** - Strong bearish signal, consider short position  
- **HOLD** - No clear signal, maintain current position
- **ERROR** - Analysis failed, check logs for details

#### **Confidence Levels**
- **80%+** - Very high confidence, strong signal
- **70-79%** - High confidence, good signal
- **60-69%** - Moderate confidence, proceed with caution
- **<60%** - Low confidence, filtered out by default

### **Personalized Analysis**

#### **Using User Preferences**
```bash
# First, create a user account via API or mobile app
# Then use their email for personalized analysis

python run_ai_signals.py --symbol AAPL --user conservative@example.com
# Uses conservative risk settings

python run_ai_signals.py --symbol AAPL --user aggressive@example.com  
# Uses aggressive risk settings
```

#### **Preference Impact**
- **Conservative Users**: Higher confidence thresholds, tighter stops
- **Moderate Users**: Balanced approach with standard settings
- **Aggressive Users**: Lower confidence thresholds, wider stops

### **Troubleshooting Signal Generation**

#### **Common Issues**

**No API Keys Configured:**
```bash
# Error: Missing required API keys
# Solution: Configure .env file or use demo mode
cp .env.template .env
# Edit .env with your API keys
```

**Network/API Errors:**
```bash
# Error: Failed to fetch market data
# Solution: Check internet connection and API key validity
python run_ai_signals.py --config-check
```

**Database Errors:**
```bash
# Error: Database connection failed
# Solution: Initialize database
python -c "from src.database import init_database; init_database()"
```

#### **Debug Mode**
```bash
# Enable detailed logging
export PYTHONPATH=./src
python run_ai_signals.py --demo --save

# Check log files
tail -f logs/sentimenttrade.log
```

### **Integration with Development Workflow**

#### **Testing New Strategies**
```bash
# Test default strategy
python run_ai_signals.py --demo

# After implementing new strategy, test it
python run_ai_signals.py --symbol AAPL --user strategy_test@example.com
```

#### **Performance Validation**
```bash
# Generate signals and save for analysis
python run_ai_signals.py --watchlist AAPL MSFT GOOGL AMZN TSLA --save

# Results saved to: signal_results_20240712_103000.json
# Analyze results for strategy performance
```

#### **API Integration Testing**
```bash
# Test signal generation before API integration
python run_ai_signals.py --demo

# Start API server
python api/main_enhanced.py

# Test API endpoints
curl -X POST "http://localhost:8000/signal" -H "Content-Type: application/json" -d '{"symbol":"AAPL"}'
```

## 🔧 **Detailed Development Setup**

### **Python Environment Setup**

#### **Option 1: Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **Option 2: Conda Environment**
```bash
# Create conda environment
conda create -n sentimenttrade python=3.9
conda activate sentimenttrade

# Install dependencies
pip install -r requirements.txt
```

### **Database Setup**

#### **SQLite (Default - No Setup Required)**
```bash
# Database is created automatically
python -c "from src.database import init_database; init_database()"

# Verify database creation
ls -la sentimenttrade.db
```

#### **PostgreSQL (Production)**
```bash
# Install PostgreSQL
# Ubuntu: sudo apt install postgresql
# Mac: brew install postgresql

# Create database
createdb sentimenttrade

# Update .env file
echo "DATABASE_URL=postgresql://user:password@localhost/sentimenttrade" >> .env
```

### **API Keys Configuration**

#### **Required for Full Functionality**
```bash
# Edit .env file
nano .env

# Add your API keys:
OPENAI_API_KEY=your_openai_api_key_here
TWELVE_DATA_API_KEY=your_twelve_data_api_key_here
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

#### **Getting API Keys**

**OpenAI API Key:**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create account and navigate to API Keys
3. Generate new secret key
4. Add to `.env` file

**TwelveData API Key:**
1. Visit [TwelveData](https://twelvedata.com/)
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env` file

**Telegram Bot (Optional):**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot with `/newbot`
3. Get bot token and chat ID
4. Add to `.env` file

## 🧪 **Testing & Validation**

### **Run All Tests**
```bash
# Comprehensive test suite
python run_tests.py

# Expected output:
# 🚀 SentimentTrade Test Suite
# ======================================================================
# 📂 Unit Tests - Individual component testing
# ✅ PASS Basic Component Functionality
# ✅ PASS User Preferences System
# 📂 Integration Tests - Cross-component integration testing  
# ✅ PASS Complete Architecture Integration
# 📂 Demonstrations - Feature demonstrations and examples
# ✅ PASS Preferences System Demo
# Overall: 6/6 tests passed
# 🎉 All tests passed!
```

### **Individual Test Categories**

#### **Unit Tests**
```bash
# Test individual components
python tests/unit/test_simple_refactor.py
python tests/unit/test_preferences.py

# Expected: Component functionality validation
```

#### **Integration Tests**
```bash
# Test system integration
python tests/integration/test_refactored_architecture.py

# Expected: Full architecture validation
```

#### **Feature Demonstrations**
```bash
# See feature showcases
python tests/demos/demo_preferences.py
python tests/demos/demo_enhanced_features.py

# Expected: Complete feature walkthroughs
```

### **API Testing**

#### **Start API Server**
```bash
# Terminal 1: Start server
python api/main_enhanced.py

# Expected output:
# 🚀 Starting SentimentTrade Enhanced API...
# 📱 Features: User Auth, Watchlist, Trade Tracking, Dashboard
# 📚 API Documentation: http://localhost:8000/docs
```

#### **Test API Endpoints**
```bash
# Terminal 2: Test health check
curl http://localhost:8000/health

# Expected: {"status":"healthy","features":{"preferences":true}}

# Test API documentation
open http://localhost:8000/docs
```

#### **Test User Registration**
```bash
# Register test user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Expected: {"access_token":"...","user":{"email":"test@example.com"}}
```

## 📱 **Mobile App Development**

### **Flutter Setup**

#### **Install Flutter**
```bash
# Download Flutter SDK
# Visit: https://flutter.dev/docs/get-started/install

# Verify installation
flutter doctor

# Expected: All checkmarks or minor warnings only
```

#### **Setup Mobile App**
```bash
# Navigate to mobile app
cd mobile_app

# Get dependencies
flutter pub get

# Verify setup
flutter doctor

# Run on device/simulator
flutter run

# Or run on web for testing
flutter run -d chrome
```

### **Mobile App Configuration**

#### **Update API Endpoint**
```dart
// Edit: mobile_app/lib/services/auth_service.dart
// Edit: mobile_app/lib/services/api_service.dart

// Change baseUrl to your server:
static const String baseUrl = 'http://localhost:8000';

// For device testing, use your computer's IP:
static const String baseUrl = 'http://192.168.1.100:8000';
```

#### **Test Mobile App Features**
```bash
# Start API server first
python api/main_enhanced.py

# In another terminal, run mobile app
cd mobile_app
flutter run

# Test features:
# 1. User registration/login
# 2. Trading preferences
# 3. Signal generation
# 4. Portfolio dashboard
```

## 🔧 **Development Workflow**

### **Code Organization**

#### **Project Structure**
```
SentimentTrade-main/
├── 📂 src/                          # Core application code
│   ├── 📂 strategies/               # Trading strategy implementations
│   ├── 🐍 ai_trade_signal.py    # Latest signal generator
│   ├── 🐍 technical_indicators.py  # Shared indicator calculations
│   ├── 🐍 trading_config.py        # Dynamic configuration system
│   ├── 🐍 preferences_service.py   # User preferences business logic
│   └── 🐍 database.py              # Database models and utilities
├── 📂 api/                          # FastAPI REST API
├── 📂 mobile_app/                  # Flutter mobile application
├── 📂 tests/                       # Organized test suite
└── 📂 docs/                        # Comprehensive documentation
```

#### **Development Commands**
```bash
# Run AI signal generator
python run_ai_signals.py --demo

# Run signal generator for specific symbol
python run_ai_signals.py --symbol AAPL

# Start API server
python api/main_enhanced.py

# Run tests
python run_tests.py

# Run mobile app
cd mobile_app && flutter run
```

### **Adding New Features**

#### **1. Create New Strategy**
```python
# Create: src/strategies/my_strategy.py
from .strategy_factory import BaseStrategy

class MyStrategy(BaseStrategy):
    def analyze_symbol(self, symbol, market_data, sentiment_score):
        # Your strategy logic here
        pass

# Register in: src/strategies/strategy_factory.py
self._strategies['my_strategy'] = MyStrategy
```

#### **2. Add API Endpoint**
```python
# Edit: api/main_enhanced.py
@app.get("/my-endpoint")
async def my_endpoint(current_user: User = Depends(get_current_user)):
    # Your endpoint logic here
    return {"message": "Hello from my endpoint"}
```

#### **3. Update Mobile App**
```dart
// Edit: mobile_app/lib/services/api_service.dart
Future<Map<String, dynamic>> callMyEndpoint() async {
  final headers = await _authService.getAuthHeaders();
  final response = await http.get(
    Uri.parse('$baseUrl/my-endpoint'),
    headers: headers,
  );
  return json.decode(response.body);
}
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'src'
# Solution: Run from project root directory
cd SentimentTrade-main
python run_tests.py
```

#### **Database Errors**
```bash
# Error: Database connection failed
# Solution: Initialize database
python -c "from src.database import init_database; init_database()"
```

#### **API Connection Errors**
```bash
# Error: Connection refused
# Solution: Start API server first
python api/main_enhanced.py

# Then test in another terminal
curl http://localhost:8000/health
```

#### **Mobile App Build Errors**
```bash
# Error: Flutter build failed
# Solution: Clean and rebuild
cd mobile_app
flutter clean
flutter pub get
flutter run
```

### **Debugging Tips**

#### **Enable Debug Logging**
```python
# Edit: src/logger.py
# Change log level to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

#### **Check API Logs**
```bash
# API server logs appear in terminal
# Look for error messages and stack traces

# Check log files
ls -la logs/
tail -f logs/sentimenttrade.log
```

#### **Test Individual Components**
```bash
# Test specific functionality
python tests/unit/test_simple_refactor.py
python tests/demos/demo_preferences.py

# Test API endpoints
curl -X GET http://localhost:8000/health
```

## 📊 **Performance & Monitoring**

### **System Health Checks**

#### **API Health**
```bash
# Check API status
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "features": {
    "user_auth": true,
    "watchlist": true,
    "trade_tracking": true,
    "dashboard": true,
    "preferences": true
  }
}
```

#### **Database Health**
```bash
# Check database
python -c "
from src.database import get_db
db = next(get_db())
print(f'Database connection: OK')
print(f'Tables created: {len(db.get_bind().table_names())}')
"
```

#### **Test Coverage**
```bash
# Run comprehensive tests
python run_tests.py

# Expected: All tests passing
# 📊 Test Results Summary
# ✅ PASS Basic Component Functionality
# ✅ PASS User Preferences System
# ✅ PASS Complete Architecture Integration
```

### **Performance Optimization**

#### **API Performance**
```bash
# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Optimize database queries
# Enable query logging in database.py
```

#### **Mobile App Performance**
```bash
# Profile Flutter app
flutter run --profile

# Build optimized release
flutter build apk --release
flutter build ios --release
```

## 🎯 **Next Steps**

### **Development Roadmap**

#### **Phase 1: Core Features** ✅
- [x] AI signal generation
- [x] User authentication
- [x] Mobile app interface
- [x] Preferences system

#### **Phase 2: Advanced Features** 🚧
- [ ] Multiple trading strategies
- [ ] Real-time notifications
- [ ] Advanced analytics
- [ ] Social trading features

#### **Phase 3: Production** 🔮
- [ ] Cloud deployment
- [ ] Scalability optimization
- [ ] Advanced security
- [ ] Enterprise features

### **Contributing**

#### **Development Setup**
```bash
# Fork repository
# Clone your fork
git clone <your-fork-url>

# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
python run_tests.py

# Commit and push
git commit -m "Add my feature"
git push origin feature/my-feature

# Create pull request
```

#### **Code Standards**
- **Python**: Follow PEP 8 style guide
- **Flutter**: Follow Dart style guide
- **Testing**: Add tests for new features
- **Documentation**: Update relevant docs

## 🎉 **Success!**

If you've followed this guide, you should now have:

- ✅ **Working API server** at `http://localhost:8000`
- ✅ **Mobile app** running on device/simulator
- ✅ **All tests passing** with `python run_tests.py`
- ✅ **User registration/login** working
- ✅ **Trading preferences** functional
- ✅ **Signal generation** operational

**🚀 You're ready to start trading with AI-powered signals!**

---

## 📞 **Need Help?**

- **📖 Documentation**: Check the `docs/` directory for detailed guides
- **🧪 Testing**: Run `python run_tests.py` to verify your setup
- **🔧 API Docs**: Visit `http://localhost:8000/docs` for interactive API documentation
- **📱 Mobile Guide**: See `docs/MOBILE_APP_GUIDE.md` for mobile-specific setup

**Happy Trading! 📈**

---

## ⚠️ **Important Legal Disclaimer**

### **🚨 Trading Risk Warning**
**TRADING INVOLVES SUBSTANTIAL RISK OF LOSS. USE THIS SOFTWARE AT YOUR OWN RISK.**

- **💰 Financial Risk**: You may lose some or all of your invested capital
- **📊 No Guarantees**: This software does not guarantee profits or prevent losses
- **🎯 Educational Purpose**: This software is for educational and informational purposes only
- **👨‍💼 Not Investment Advice**: Always consult qualified financial advisors before trading
- **📈 Past Performance**: Historical results do not guarantee future performance

### **🔧 Software Disclaimer**
**THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.**

- **🐛 No Warranty**: No guarantees regarding accuracy, reliability, or performance
- **📡 Data Dependencies**: Relies on third-party APIs which may be inaccurate or unavailable
- **⚡ System Failures**: Technical issues may affect signal generation
- **🔄 Development Software**: Features and algorithms subject to change

### **📜 Regulatory Compliance**
- **🏛️ Local Laws**: Ensure compliance with financial regulations in your jurisdiction
- **💼 Commercial Use**: Additional licenses may be required for commercial deployment
- **🌍 International Use**: Regulations vary by country and jurisdiction

**⚠️ By using this software, you acknowledge that you understand these risks and disclaimers.**

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
