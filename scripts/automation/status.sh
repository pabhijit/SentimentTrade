#!/bin/bash
# Check the status of the SentimentTrade service

if command -v systemctl >/dev/null 2>&1; then
    # Use systemd if available
    systemctl --user status sentimenttrade.service
else
    # Fall back to process checking
    PID=$(pgrep -f "python launcher.py --start")
    if [ -n "$PID" ]; then
        echo "SentimentTrade is running with PID: $PID"
        echo "Process info:"
        ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
    else
        echo "SentimentTrade is not running."
    fi
fi
