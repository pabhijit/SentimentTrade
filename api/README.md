# 🔌 SentimentTrade API Server

FastAPI REST API server that exposes SentimentTrade functionality for mobile and web applications.

## 🚀 Quick Start

For complete setup instructions, see the main [**QUICKSTART Guide**](../QUICKSTART.md).

### **Start API Server**
```bash
# From project root
python api/main_enhanced.py

# Visit: http://localhost:8000/docs
```

### **Basic Setup**
```bash
pip install -r requirements.txt
python main.py
```

The API will be available at:
- **API Base**: `http://localhost:8000`
- **Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/` | API information | Basic API details |
| GET | `/health` | Health check | API status and configuration |
| POST | `/signal` | Get single trading signal | `{"symbol": "AAPL"}` |
| POST | `/signals` | Get multiple signals | `{"symbols": ["AAPL", "MSFT"]}` |
| GET | `/config` | Get configuration | Current API settings |
| GET | `/symbols/popular` | Popular symbols | List of common stocks |

### Example Requests

#### Get Trading Signal
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

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Required for full functionality
OPENAI_API_KEY=your_openai_key_here
TWELVE_DATA_API_KEY=your_twelve_data_key_here

# Optional
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
```

### Trading Parameters
```python
STOCK_SYMBOL = "AAPL"              # Default symbol
POSITION_SIZE = 1000.0             # USD per trade
RSI_OVERSOLD = 30                  # RSI buy threshold
RSI_OVERBOUGHT = 70                # RSI sell threshold
SENTIMENT_BULLISH_THRESHOLD = 0.4  # Sentiment threshold
```

## 🧪 Testing

### Test API Components (No Server Required)
```bash
cd ..
python tests/test_api_simple.py
```

### Test Full API (Server Required)
```bash
# Terminal 1: Start server
python main.py

# Terminal 2: Run tests
cd ..
python tests/test_api.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Get popular symbols
curl http://localhost:8000/symbols/popular

# Get trading signal
curl -X POST http://localhost:8000/signal \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL"}'
```

## 🏗️ Architecture

### Components
- **FastAPI Server** - HTTP request handling
- **Pydantic Models** - Request/response validation
- **SentimentTrade Engine** - Core trading logic
- **Error Handling** - Comprehensive exception management
- **CORS Support** - Cross-origin requests for mobile apps

### Data Flow
```
Mobile App → HTTP Request → FastAPI → SentimentTrade Engine → External APIs
                                   ↓
Mobile App ← HTTP Response ← FastAPI ← Trading Signal ← Market Data
```

## 📊 Performance Features

- **Caching** - Market data cached for 60 seconds
- **Retry Logic** - 3 retries with exponential backoff
- **Async Processing** - Non-blocking request handling
- **Connection Pooling** - Efficient HTTP connections
- **Request Validation** - Input sanitization and validation

## 🛡️ Security Features

- **Input Validation** - All inputs validated with Pydantic
- **Error Sanitization** - No sensitive data in error responses
- **CORS Configuration** - Configurable cross-origin policies
- **Rate Limiting** - (Future feature)
- **API Key Management** - Environment variable storage

## 🚀 Deployment Options

### Development
```bash
# Basic development server
python main.py

# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Production server with Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker deployment
docker build -t sentiment-trade-api .
docker run -p 8000:8000 sentiment-trade-api
```

### Cloud Deployment
- **Heroku**: `git push heroku main`
- **AWS Lambda**: Use Mangum adapter
- **Google Cloud Run**: Deploy container
- **DigitalOcean App Platform**: Connect GitHub repo

## 📁 File Structure

```
api/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔍 Monitoring & Debugging

### Logs
- Server logs printed to console
- Application logs in `../logs/` directory
- Error tracking with full stack traces

### Health Monitoring
```bash
# Check API health
curl http://localhost:8000/health

# Response includes:
# - API status
# - Configuration validation
# - Missing API keys
# - Warnings
```

### Performance Monitoring
- Response times logged
- API call success/failure rates
- Cache hit/miss statistics

## 🚨 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :8000

# Kill process using port
kill -9 $(lsof -t -i:8000)

# Install missing dependencies
pip install -r requirements.txt
```

**Import errors:**
```bash
# Add parent directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# Or run from project root
cd .. && python api/main.py
```

**API keys not working:**
- Check `.env` file exists in project root
- Verify API key format and validity
- Check logs for specific error messages

**CORS errors:**
- Update `allow_origins` in `main.py`
- For development: `["*"]`
- For production: `["https://yourdomain.com"]`

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug
uvicorn main:app --reload --log-level debug
```

## 📈 API Usage Examples

### Python Client
```python
import requests

# Get trading signal
response = requests.post(
    "http://localhost:8000/signal",
    json={"symbol": "AAPL", "include_indicators": True}
)
signal = response.json()
print(f"Recommendation: {signal['recommendation']}")
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/signal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: 'AAPL' })
});
const signal = await response.json();
console.log(`Recommendation: ${signal.recommendation}`);
```

### Flutter/Dart
```dart
final response = await http.post(
  Uri.parse('http://localhost:8000/signal'),
  headers: {'Content-Type': 'application/json'},
  body: json.encode({'symbol': 'AAPL'}),
);
final signal = json.decode(response.body);
```

## 🔗 Related

- **Main Project**: [../README.md](../README.md)
- **Mobile App**: [../mobile_app/](../mobile_app/)
- **Complete Guide**: [../docs/MOBILE_APP_GUIDE.md](../docs/MOBILE_APP_GUIDE.md)
- **Tests**: [../tests/](../tests/)

---

**🎯 Ready to serve?** Start the API server and begin building amazing trading applications!
