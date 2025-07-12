# 📱 SentimentTrade Mobile App Integration Guide

This guide shows you how to build a mobile application that uses your SentimentTrade script to generate buy/sell signals.

## 🏗️ Architecture Overview

```
📱 Mobile App (Flutter/React Native)
    ↓ HTTP REST API
🖥️  Backend API Server (FastAPI)
    ↓ Function Calls  
🧠 SentimentTrade Engine (Your Enhanced Script)
    ↓ External APIs
🌐 Market Data & AI Services (TwelveData, OpenAI)
```

## 🚀 Quick Start

### 1. Install API Dependencies

```bash
cd /Users/abpattan/Downloads/SentimentTrade-main
pip install -r api/requirements.txt
```

### 2. Start the API Server

```bash
cd api
python main.py
```

The API will be available at: `http://localhost:8000`
- 📚 API Documentation: `http://localhost:8000/docs`
- 🔍 Alternative docs: `http://localhost:8000/redoc`

### 3. Test the API

```bash
python tests/test_api.py
```

### 4. Set Up Mobile App (Flutter)

```bash
cd mobile_app
flutter pub get
flutter run
```

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | API info | Basic API information |
| `/health` | GET | Health check | API status and config validation |
| `/signal` | POST | Get single signal | `{"symbol": "AAPL"}` |
| `/signals` | POST | Get multiple signals | `{"symbols": ["AAPL", "MSFT"]}` |
| `/config` | GET | Get configuration | Current API settings |
| `/symbols/popular` | GET | Popular symbols | List of common stock symbols |

### Example API Usage

#### Get Single Signal
```bash
curl -X POST "http://localhost:8000/signal" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL", "include_indicators": true}'
```

#### Response Format
```json
{
  "symbol": "AAPL",
  "timestamp": "2024-01-15T10:30:00",
  "recommendation": "BUY",
  "confidence": 0.75,
  "current_price": 150.25,
  "entry_price": 150.25,
  "stop_loss": 147.50,
  "target_price": 155.00,
  "sentiment": 0.6,
  "risk_reward_ratio": 2.0,
  "indicators": {
    "rsi_1m": 25.5,
    "macd": 1.2,
    "vwap": 149.80
  }
}
```

## 📱 Mobile App Features

### Current Features
- ✅ **Symbol Search**: Enter any stock symbol
- ✅ **Trading Signals**: Get BUY/SELL/HOLD recommendations
- ✅ **Confidence Scores**: AI confidence in recommendations
- ✅ **Risk Management**: Stop loss and target prices
- ✅ **Popular Symbols**: Quick access to common stocks
- ✅ **Recent History**: View recent signal requests
- ✅ **Error Handling**: Graceful error messages
- ✅ **Offline Detection**: API connection status

### Mobile App Screenshots (Conceptual)

```
┌─────────────────────┐
│   SentimentTrade    │
├─────────────────────┤
│ [AAPL____________]🔍│
│                     │
│ Popular: AAPL MSFT  │
│         GOOGL AMZN  │
├─────────────────────┤
│ 📊 AAPL            │
│ 🟢 BUY (75%)       │
│                     │
│ Price: $150.25      │
│ Entry: $150.25      │
│ Stop:  $147.50      │
│ Target: $155.00     │
│                     │
│ Sentiment: Bullish  │
│ R/R Ratio: 2.0      │
└─────────────────────┘
```

## 🛠️ Development Setup

### Backend API Setup

1. **Environment Variables** (Optional but recommended):
```bash
# Create .env file
cp .env.template .env

# Add your API keys
OPENAI_API_KEY=your_openai_key
TWELVE_DATA_API_KEY=your_twelve_data_key
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

2. **Start Development Server**:
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Flutter Mobile App Setup

1. **Install Flutter**: Follow [Flutter installation guide](https://flutter.dev/docs/get-started/install)

2. **Install Dependencies**:
```bash
cd mobile_app
flutter pub get
```

3. **Run on Device/Emulator**:
```bash
# iOS Simulator
flutter run -d ios

# Android Emulator  
flutter run -d android

# Chrome (for testing)
flutter run -d chrome
```

### React Native Alternative

If you prefer React Native, here's the equivalent setup:

```bash
# Create React Native app
npx react-native init SentimentTradeApp
cd SentimentTradeApp

# Install dependencies
npm install axios react-native-vector-icons
```

## 🔧 Configuration

### API Configuration

The API can be configured through environment variables or the config file:

```python
# Key settings
STOCK_SYMBOL = "AAPL"           # Default symbol
POSITION_SIZE = 1000.0          # USD per trade
RSI_OVERSOLD = 30               # RSI buy threshold
RSI_OVERBOUGHT = 70             # RSI sell threshold
SENTIMENT_BULLISH_THRESHOLD = 0.4   # Sentiment buy threshold
SENTIMENT_BEARISH_THRESHOLD = -0.4  # Sentiment sell threshold
```

### Mobile App Configuration

Update the API URL in your mobile app:

```dart
// Flutter - lib/main.dart
class ApiService {
  static const String baseUrl = 'http://YOUR_SERVER_IP:8000';
  // For local development: 'http://localhost:8000'
  // For production: 'https://your-domain.com'
}
```

## 🚀 Deployment Options

### Option 1: Local Development
- API runs on your computer
- Mobile app connects to `localhost:8000`
- Good for: Testing and development

### Option 2: Cloud Deployment
- Deploy API to cloud (AWS, Google Cloud, Heroku)
- Mobile app connects to cloud URL
- Good for: Production use

### Option 3: Docker Deployment
```bash
# Create Dockerfile for API
docker build -t sentiment-trade-api .
docker run -p 8000:8000 sentiment-trade-api
```

## 📊 Performance Considerations

### API Performance
- **Caching**: Market data cached for 60 seconds
- **Retry Logic**: 3 retries with exponential backoff
- **Rate Limiting**: Consider adding rate limits for production
- **Async Processing**: API uses async/await for better performance

### Mobile App Performance
- **Offline Support**: Cache recent signals
- **Loading States**: Show progress indicators
- **Error Handling**: Graceful degradation
- **Background Updates**: Refresh signals periodically

## 🔒 Security Considerations

### API Security
- **API Keys**: Store in environment variables, not code
- **CORS**: Configure allowed origins for production
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Validate all inputs
- **HTTPS**: Use HTTPS in production

### Mobile App Security
- **API URL**: Don't hardcode sensitive URLs
- **Local Storage**: Encrypt sensitive data
- **Network Security**: Use certificate pinning
- **User Data**: Don't store API keys on device

## 🧪 Testing

### API Testing
```bash
# Run API tests
python tests/test_api.py

# Run unit tests
python -m pytest tests/ -v

# Run comprehensive test suite
python tests/run_tests.py

# Test API components without server
python tests/test_api_simple.py

# Load testing (optional)
pip install locust
locust -f load_test.py
```

### Mobile App Testing
```bash
# Flutter tests
flutter test

# Integration tests
flutter drive --target=test_driver/app.dart
```

## 📈 Monitoring & Analytics

### API Monitoring
- **Logs**: Check `logs/` directory for detailed logs
- **Health Endpoint**: Monitor `/health` for API status
- **Metrics**: Track response times and error rates

### Mobile App Analytics
- **Usage Tracking**: Track which symbols are requested most
- **Performance**: Monitor app startup and API response times
- **Crashes**: Implement crash reporting

## 🔄 Updates & Maintenance

### API Updates
1. Update SentimentTrade engine
2. Test with `python test_api.py`
3. Deploy new API version
4. Update API documentation

### Mobile App Updates
1. Update API integration if needed
2. Test on multiple devices
3. Submit to app stores
4. Monitor user feedback

## 🆘 Troubleshooting

### Common Issues

**API won't start:**
```bash
# Check if port is in use
lsof -i :8000

# Install missing dependencies
pip install -r api/requirements.txt
```

**Mobile app can't connect:**
- Check API server is running
- Verify API URL in mobile app
- Check firewall settings
- Test with `curl` or browser

**Signals not working:**
- Check API keys in `.env` file
- Verify internet connection
- Check API logs for errors
- Test individual components

**Performance issues:**
- Check API response times
- Monitor memory usage
- Optimize database queries
- Add caching where needed

## 📞 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Run the test suite: `python tests/run_tests.py`
3. Test API components: `python tests/test_api_simple.py`
4. Check API documentation: `http://localhost:8000/docs`
5. Review this guide for common solutions

## 🎯 Next Steps

1. **✅ Set up the API server**
2. **✅ Test all endpoints**
3. **✅ Build the mobile app**
4. **🔄 Add your API keys for full functionality**
5. **🚀 Deploy to production when ready**

Your SentimentTrade mobile app is now ready to provide AI-powered trading signals on the go! 📱📈
