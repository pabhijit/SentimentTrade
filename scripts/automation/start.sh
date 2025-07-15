#!/bin/bash
# Start the SentimentTrade service

if command -v systemctl >/dev/null 2>&1; then
    # Use systemd if available
    systemctl --user start sentimenttrade.service
    echo "SentimentTrade service started."
    echo "Check status with: ./status.sh"
else
    # Fall back to direct execution
    echo "Starting SentimentTrade in the background..."
    nohup python launcher.py --start > /dev/null 2>&1 &
    echo "SentimentTrade started with PID: $!"
    echo "To stop, use: ./stop.sh"
fi
