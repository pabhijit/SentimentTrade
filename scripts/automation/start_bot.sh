#!/bin/bash
# SentimentTrade Bot Startup Script
# Simple launcher for macOS/Linux

echo "🚀 Starting SentimentTrade Automated Trading Bot..."
echo "📊 Strategies: Break & Retest + Options Trading"
echo "⏰ Schedule: Every 30 minutes during market hours"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3."
    exit 1
fi

echo "🐍 Using Python: $PYTHON_CMD"

# Check if .env file exists
if [ ! -f "../../.env" ]; then
    echo "⚠️  .env file not found. Running Telegram setup..."
    $PYTHON_CMD setup_telegram.py
    echo ""
fi

# Install requirements if needed
echo "📦 Checking requirements..."
$PYTHON_CMD -c "import schedule, yfinance, pandas" 2>/dev/null || {
    echo "📦 Installing required packages..."
    pip3 install -r requirements.txt
}

echo "✅ Requirements satisfied"
echo ""

# Start the bot
echo "🤖 Launching trading bot..."
echo "Press Ctrl+C to stop"
echo "=" * 50

$PYTHON_CMD launch_trading_bot.py --start
