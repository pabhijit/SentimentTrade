#!/bin/bash
# Stop the SentimentTrade service

if command -v systemctl >/dev/null 2>&1; then
    # Use systemd if available
    systemctl --user stop sentimenttrade.service
    echo "SentimentTrade service stopped."
else
    # Fall back to direct process killing
    PID=$(pgrep -f "python launcher.py --start")
    if [ -n "$PID" ]; then
        kill $PID
        echo "SentimentTrade stopped (PID: $PID)"
    else
        echo "SentimentTrade is not running."
    fi
fi
