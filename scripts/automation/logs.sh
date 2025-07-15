#!/bin/bash
# View SentimentTrade logs

PROJECT_ROOT=$(dirname "$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")")
LOG_FILE="$PROJECT_ROOT/logs/sentimenttrade.log"

if command -v systemctl >/dev/null 2>&1; then
    # Use journalctl if systemd is available
    journalctl --user -u sentimenttrade.service -f
else
    # Fall back to direct log file viewing
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "Log file not found at: $LOG_FILE"
        
        # Check if logs directory exists in current directory
        if [ -f "logs/sentimenttrade.log" ]; then
            tail -f "logs/sentimenttrade.log"
        else
            echo "No log files found."
        fi
    fi
fi
