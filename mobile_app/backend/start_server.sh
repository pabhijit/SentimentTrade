#!/bin/bash

echo "🚀 Starting SentimentTrade Backtesting API Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

echo "📊 Available Features:"
echo "  • AI Sentiment Strategy (Momentum/Contrarian modes)"
echo "  • Break & Retest Strategy (Swing trading focus)"
echo "  • 7 Assets: SPY, QQQ, NVDA, AAPL, AMZN, MSFT, GOOGL"
echo "  • 4 Preset Configurations: Conservative, Balanced, Aggressive, High Frequency"
echo "  • Real-time backtesting with progress tracking"
echo "  • Performance metrics and comparison tools"
echo ""
echo "🌐 API Endpoints:"
echo "  • GET  /api/strategies - List available strategies"
echo "  • GET  /api/assets - List available assets"
echo "  • POST /api/backtest - Run backtest"
echo "  • GET  /api/backtest/results/<job_id> - Get results"
echo ""
echo "🔗 Server will be available at: http://localhost:8000"
echo "📱 Flutter app should connect to this URL"
echo ""

# Start the Flask server
python app.py
