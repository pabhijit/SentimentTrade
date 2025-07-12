"""
Telegram Bot Notification Logic for SentimentTrade
Handles sending trading alerts, signals, and status updates via Telegram
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Handles Telegram notifications for trading bot"""
    
    def __init__(self, token: str = None, chat_id: str = None):
        """Initialize Telegram notifier"""
        self.token = token or config.TELEGRAM_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.bot = None
        self.enabled = bool(self.token and self.chat_id)
        
        if self.enabled:
            self.bot = Bot(token=self.token)
            logger.info("Telegram notifier initialized successfully")
        else:
            logger.warning("Telegram notifier disabled - missing token or chat_id")
    
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send a message via Telegram"""
        if not self.enabled:
            logger.debug(f"Telegram disabled - would send: {message}")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("Telegram message sent successfully")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def send_message_sync(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Synchronous wrapper for sending messages"""
        try:
            return asyncio.run(self.send_message(message, parse_mode))
        except Exception as e:
            logger.error(f"Error in sync message send: {e}")
            return False
    
    async def send_trade_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Send a formatted trading signal alert"""
        try:
            symbol = signal_data.get('symbol', 'Unknown')
            recommendation = signal_data.get('recommendation', 'HOLD')
            current_price = signal_data.get('current_price', 0)
            entry_price = signal_data.get('entry_price', current_price)
            stop_loss = signal_data.get('stop_loss', 0)
            target_price = signal_data.get('target_price', 0)
            confidence = signal_data.get('confidence', 0)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Format the message
            if recommendation == 'BUY':
                emoji = "🟢"
                action = "BUY SIGNAL"
            elif recommendation == 'SELL':
                emoji = "🔴"
                action = "SELL SIGNAL"
            else:
                emoji = "🟡"
                action = "HOLD SIGNAL"
            
            message = f"""
{emoji} <b>{action}</b> {emoji}

📊 <b>Symbol:</b> {symbol}
💰 <b>Current Price:</b> ${current_price:.2f}
🎯 <b>Entry Price:</b> ${entry_price:.2f}
🛑 <b>Stop Loss:</b> ${stop_loss:.2f}
🚀 <b>Target:</b> ${target_price:.2f}
📈 <b>Confidence:</b> {confidence:.1%}

⏰ <b>Time:</b> {timestamp}

<i>SentimentTrade Bot Alert</i>
            """.strip()
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error formatting trade signal: {e}")
            return False
    
    def send_trade_signal_sync(self, signal_data: Dict[str, Any]) -> bool:
        """Synchronous wrapper for trade signal"""
        try:
            return asyncio.run(self.send_trade_signal(signal_data))
        except Exception as e:
            logger.error(f"Error in sync trade signal send: {e}")
            return False
    
    async def send_trade_execution(self, execution_data: Dict[str, Any]) -> bool:
        """Send trade execution confirmation"""
        try:
            symbol = execution_data.get('symbol', 'Unknown')
            action = execution_data.get('action', 'Unknown')
            quantity = execution_data.get('quantity', 0)
            price = execution_data.get('price', 0)
            order_id = execution_data.get('order_id', 'N/A')
            status = execution_data.get('status', 'Unknown')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if status.lower() == 'filled':
                emoji = "✅"
                status_text = "EXECUTED"
            elif status.lower() == 'rejected':
                emoji = "❌"
                status_text = "REJECTED"
            else:
                emoji = "⏳"
                status_text = "PENDING"
            
            message = f"""
{emoji} <b>TRADE {status_text}</b> {emoji}

📊 <b>Symbol:</b> {symbol}
🔄 <b>Action:</b> {action.upper()}
📦 <b>Quantity:</b> {quantity}
💰 <b>Price:</b> ${price:.2f}
🆔 <b>Order ID:</b> {order_id}
📋 <b>Status:</b> {status.upper()}

⏰ <b>Time:</b> {timestamp}

<i>SentimentTrade Bot Execution</i>
            """.strip()
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error formatting trade execution: {e}")
            return False
    
    def send_trade_execution_sync(self, execution_data: Dict[str, Any]) -> bool:
        """Synchronous wrapper for trade execution"""
        try:
            return asyncio.run(self.send_trade_execution(execution_data))
        except Exception as e:
            logger.error(f"Error in sync trade execution send: {e}")
            return False
    
    async def send_error_alert(self, error_message: str, context: str = "") -> bool:
        """Send error alert"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            message = f"""
🚨 <b>ERROR ALERT</b> 🚨

❌ <b>Error:</b> {error_message}
📍 <b>Context:</b> {context or 'General'}
⏰ <b>Time:</b> {timestamp}

<i>SentimentTrade Bot Error</i>
            """.strip()
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending error alert: {e}")
            return False
    
    def send_error_alert_sync(self, error_message: str, context: str = "") -> bool:
        """Synchronous wrapper for error alert"""
        try:
            return asyncio.run(self.send_error_alert(error_message, context))
        except Exception as e:
            logger.error(f"Error in sync error alert send: {e}")
            return False
    
    async def send_daily_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Send daily trading summary"""
        try:
            date = summary_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            total_trades = summary_data.get('total_trades', 0)
            profitable_trades = summary_data.get('profitable_trades', 0)
            total_pnl = summary_data.get('total_pnl', 0)
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            pnl_emoji = "📈" if total_pnl >= 0 else "📉"
            pnl_color = "green" if total_pnl >= 0 else "red"
            
            message = f"""
📊 <b>DAILY SUMMARY</b> 📊

📅 <b>Date:</b> {date}
🔢 <b>Total Trades:</b> {total_trades}
✅ <b>Profitable:</b> {profitable_trades}
📊 <b>Win Rate:</b> {win_rate:.1f}%
{pnl_emoji} <b>P&L:</b> ${total_pnl:.2f}

<i>SentimentTrade Bot Summary</i>
            """.strip()
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    def send_daily_summary_sync(self, summary_data: Dict[str, Any]) -> bool:
        """Synchronous wrapper for daily summary"""
        try:
            return asyncio.run(self.send_daily_summary(summary_data))
        except Exception as e:
            logger.error(f"Error in sync daily summary send: {e}")
            return False
    
    async def send_bot_status(self, status: str, details: str = "") -> bool:
        """Send bot status update"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if status.lower() == 'started':
                emoji = "🟢"
            elif status.lower() == 'stopped':
                emoji = "🔴"
            elif status.lower() == 'error':
                emoji = "🚨"
            else:
                emoji = "ℹ️"
            
            message = f"""
{emoji} <b>BOT STATUS: {status.upper()}</b> {emoji}

📝 <b>Details:</b> {details or 'No additional details'}
⏰ <b>Time:</b> {timestamp}

<i>SentimentTrade Bot Status</i>
            """.strip()
            
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending bot status: {e}")
            return False
    
    def send_bot_status_sync(self, status: str, details: str = "") -> bool:
        """Synchronous wrapper for bot status"""
        try:
            return asyncio.run(self.send_bot_status(status, details))
        except Exception as e:
            logger.error(f"Error in sync bot status send: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Telegram connection"""
        if not self.enabled:
            logger.info("Telegram is disabled")
            return False
        
        try:
            await self.bot.get_me()
            test_message = "🤖 SentimentTrade Bot - Connection Test Successful!"
            return await self.send_message(test_message)
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def test_connection_sync(self) -> bool:
        """Synchronous wrapper for connection test"""
        try:
            return asyncio.run(self.test_connection())
        except Exception as e:
            logger.error(f"Error in sync connection test: {e}")
            return False

# Global notifier instance
notifier = TelegramNotifier()

# Convenience functions for easy import
def send_trade_signal(signal_data: Dict[str, Any]) -> bool:
    """Send trade signal notification"""
    return notifier.send_trade_signal_sync(signal_data)

def send_trade_execution(execution_data: Dict[str, Any]) -> bool:
    """Send trade execution notification"""
    return notifier.send_trade_execution_sync(execution_data)

def send_error_alert(error_message: str, context: str = "") -> bool:
    """Send error alert notification"""
    return notifier.send_error_alert_sync(error_message, context)

def send_daily_summary(summary_data: Dict[str, Any]) -> bool:
    """Send daily summary notification"""
    return notifier.send_daily_summary_sync(summary_data)

def send_bot_status(status: str, details: str = "") -> bool:
    """Send bot status notification"""
    return notifier.send_bot_status_sync(status, details)

def test_telegram() -> bool:
    """Test Telegram connection"""
    return notifier.test_connection_sync()

if __name__ == "__main__":
    # Test the Telegram functionality
    print("Testing Telegram Notifier...")
    
    # Test connection
    if test_telegram():
        print("✅ Telegram connection successful!")
        
        # Test trade signal
        test_signal = {
            'symbol': 'AAPL',
            'recommendation': 'BUY',
            'current_price': 150.25,
            'entry_price': 150.25,
            'stop_loss': 147.50,
            'target_price': 155.00,
            'confidence': 0.75
        }
        
        if send_trade_signal(test_signal):
            print("✅ Trade signal test successful!")
        else:
            print("❌ Trade signal test failed")
            
    else:
        print("❌ Telegram connection failed or disabled")
        print("Make sure TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set in your .env file")
