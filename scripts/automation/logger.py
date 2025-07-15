"""
Simplified logging configuration for SentimentTrade automation
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

class SentimentTradeLogger:
    """Custom logger for SentimentTrade bot"""
    
    def __init__(self, name: str = "SentimentTrade"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
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
    
    def get_logger(self):
        """Get the configured logger"""
        return self.logger

# Create global logger instance
sentiment_logger = SentimentTradeLogger()
logger = sentiment_logger.get_logger()

if __name__ == "__main__":
    # Test logging functionality
    logger.info("Testing SentimentTrade logging system")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.info("Logging test completed")
