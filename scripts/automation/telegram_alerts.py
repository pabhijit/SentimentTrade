"""
Simplified Telegram alerts for SentimentTrade automation
"""

import os
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_alerts")

class TelegramNotifier:
    """Telegram notification handler"""
    
    def __init__(self):
        """Initialize Telegram notifier"""
        # Load environment variables
        self.token = os.environ.get('TELEGRAM_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        # Check if Telegram is configured
        self.enabled = bool(self.token and self.chat_id)
        
        if not self.enabled:
            logger.warning("Telegram notifier disabled - missing token or chat_id")
    
    def send_message(self, message: str) -> bool:
        """Send a message to Telegram"""
        if not self.enabled:
            logger.debug(f"Telegram disabled, not sending: {message[:50]}...")
            return False
        
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            data = response.json()
            if data.get('ok'):
                logger.debug(f"Telegram message sent: {message[:50]}...")
                return True
            else:
                logger.error(f"Telegram error: {data.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_trading_signal(self, signal) -> bool:
        """Send a trading signal alert"""
        if not self.enabled:
            return False
        
        try:
            # Create message
            if signal.action == "BUY":
                emoji = "🟢"
            elif signal.action == "SELL":
                emoji = "🔴"
            else:
                emoji = "⚪"
            
            message = f"{emoji} {signal.action} SIGNAL {emoji}\n\n"
            message += f"📊 Symbol: {signal.symbol}\n"
            message += f"💰 Current Price: ${signal.current_price:.2f}\n"
            message += f"🎯 Entry Price: ${signal.entry_price:.2f}\n"
            
            if signal.stop_loss:
                message += f"🛑 Stop Loss: ${signal.stop_loss:.2f}\n"
            
            if signal.target_price:
                message += f"🚀 Target: ${signal.target_price:.2f}\n"
            
            message += f"📈 Confidence: {signal.confidence:.1%}\n\n"
            
            # Add timestamp
            message += f"⏰ Time: {signal.timestamp[:19]}\n"
            
            # Add strategy
            if signal.strategy:
                message += f"🔧 Strategy: {signal.strategy}\n"
            
            # Add reasoning if available
            if signal.reasoning:
                message += f"💭 Reasoning: {signal.reasoning}\n\n"
            
            message += "SentimentTrade Multi-Strategy Bot"
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error creating signal message: {e}")
            return False

def send_bot_status(message: str) -> bool:
    """Send bot status message"""
    notifier = TelegramNotifier()
    return notifier.send_message(message)

def send_error_alert(error_message: str) -> bool:
    """Send error alert"""
    notifier = TelegramNotifier()
    message = f"⚠️ ERROR ALERT ⚠️\n\n{error_message}\n\nSentimentTrade Bot"
    return notifier.send_message(message)

def test_telegram() -> bool:
    """Test Telegram connection"""
    notifier = TelegramNotifier()
    
    if not notifier.enabled:
        logger.warning("Telegram not configured - test skipped")
        return False
    
    message = "🚀 SentimentTrade Bot Test\n\n"
    message += "If you're seeing this message, your Telegram notifications are working correctly!"
    
    return notifier.send_message(message)

if __name__ == "__main__":
    # Test Telegram connection
    if test_telegram():
        print("✅ Telegram test successful!")
    else:
        print("❌ Telegram test failed!")
