"""
Logging configuration for SentimentTrade bot
Provides structured logging with file rotation and different log levels
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from config import config

class SentimentTradeLogger:
    """Custom logger for SentimentTrade bot"""
    
    def __init__(self, name: str = "SentimentTrade"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path("../logs")
        log_dir.mkdir(exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set base level
        self.logger.setLevel(logging.DEBUG)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler (INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all logs (DEBUG and above)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "sentimenttrade.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler (ERROR and above)
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "sentimenttrade_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # Trading activity handler (custom level)
        trading_handler = logging.handlers.RotatingFileHandler(
            log_dir / "trading_activity.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        trading_handler.setLevel(logging.INFO)
        trading_handler.setFormatter(detailed_formatter)
        
        # Add filter to only log trading-related messages
        trading_handler.addFilter(lambda record: 'TRADE' in record.getMessage().upper())
        self.logger.addHandler(trading_handler)
    
    def get_logger(self):
        """Get the configured logger"""
        return self.logger
    
    def log_trade_signal(self, symbol: str, recommendation: str, price: float, 
                        confidence: float, indicators: dict = None):
        """Log trade signal with structured format"""
        indicators_str = ""
        if indicators:
            indicators_str = " | ".join([f"{k}:{v}" for k, v in indicators.items()])
        
        message = f"TRADE SIGNAL - {symbol} | {recommendation} | ${price:.2f} | Confidence: {confidence:.2%}"
        if indicators_str:
            message += f" | Indicators: {indicators_str}"
        
        self.logger.info(message)
    
    def log_trade_execution(self, symbol: str, action: str, quantity: float, 
                           price: float, order_id: str = None, status: str = "PENDING"):
        """Log trade execution"""
        message = f"TRADE EXECUTION - {symbol} | {action} | Qty: {quantity} | ${price:.2f} | Status: {status}"
        if order_id:
            message += f" | Order ID: {order_id}"
        
        self.logger.info(message)
    
    def log_api_call(self, api_name: str, endpoint: str, status: str, 
                     response_time: float = None, error: str = None):
        """Log API calls"""
        message = f"API CALL - {api_name} | {endpoint} | {status}"
        if response_time:
            message += f" | {response_time:.3f}s"
        if error:
            message += f" | Error: {error}"
        
        if status == "SUCCESS":
            self.logger.debug(message)
        else:
            self.logger.warning(message)
    
    def log_market_data(self, symbol: str, price: float, volume: int = None, 
                       indicators: dict = None):
        """Log market data updates"""
        message = f"MARKET DATA - {symbol} | ${price:.2f}"
        if volume:
            message += f" | Vol: {volume:,}"
        if indicators:
            indicators_str = " | ".join([f"{k}:{v}" for k, v in indicators.items()])
            message += f" | {indicators_str}"
        
        self.logger.debug(message)
    
    def log_error_with_context(self, error: Exception, context: str, 
                              additional_data: dict = None):
        """Log error with full context"""
        message = f"ERROR - {context} | {type(error).__name__}: {str(error)}"
        if additional_data:
            data_str = " | ".join([f"{k}:{v}" for k, v in additional_data.items()])
            message += f" | Data: {data_str}"
        
        self.logger.error(message, exc_info=True)
    
    def log_performance_metric(self, metric_name: str, value: float, 
                              symbol: str = None, timeframe: str = None):
        """Log performance metrics"""
        message = f"PERFORMANCE - {metric_name}: {value}"
        if symbol:
            message += f" | Symbol: {symbol}"
        if timeframe:
            message += f" | Timeframe: {timeframe}"
        
        self.logger.info(message)

# Create global logger instance
sentiment_logger = SentimentTradeLogger()
logger = sentiment_logger.get_logger()

# Convenience functions
def log_trade_signal(symbol: str, recommendation: str, price: float, 
                    confidence: float, indicators: dict = None):
    """Log trade signal"""
    sentiment_logger.log_trade_signal(symbol, recommendation, price, confidence, indicators)

def log_trade_execution(symbol: str, action: str, quantity: float, 
                       price: float, order_id: str = None, status: str = "PENDING"):
    """Log trade execution"""
    sentiment_logger.log_trade_execution(symbol, action, quantity, price, order_id, status)

def log_api_call(api_name: str, endpoint: str, status: str, 
                response_time: float = None, error: str = None):
    """Log API call"""
    sentiment_logger.log_api_call(api_name, endpoint, status, response_time, error)

def log_market_data(symbol: str, price: float, volume: int = None, 
                   indicators: dict = None):
    """Log market data"""
    sentiment_logger.log_market_data(symbol, price, volume, indicators)

def log_error_with_context(error: Exception, context: str, 
                          additional_data: dict = None):
    """Log error with context"""
    sentiment_logger.log_error_with_context(error, context, additional_data)

def log_performance_metric(metric_name: str, value: float, 
                          symbol: str = None, timeframe: str = None):
    """Log performance metric"""
    sentiment_logger.log_performance_metric(metric_name, value, symbol, timeframe)

if __name__ == "__main__":
    # Test logging functionality
    logger.info("Testing SentimentTrade logging system")
    
    # Test different log types
    log_trade_signal("AAPL", "BUY", 150.25, 0.75, {"RSI": 25, "MACD": "Bullish"})
    log_trade_execution("AAPL", "BUY", 10, 150.25, "ORDER123", "FILLED")
    log_api_call("TwelveData", "/time_series", "SUCCESS", 0.245)
    log_market_data("AAPL", 150.30, 1000000, {"RSI": 25.5, "VWAP": 149.80})
    log_performance_metric("Daily P&L", 125.50, "AAPL", "1D")
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        log_error_with_context(e, "Testing error logging", {"symbol": "AAPL", "price": 150.25})
    
    logger.info("Logging test completed")
