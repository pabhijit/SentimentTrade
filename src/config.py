"""
Configuration module for SentimentTrade bot
Handles API keys, trading parameters, and environment settings
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for SentimentTrade bot"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    TWELVE_DATA_API_KEY: str = os.getenv("TWELVE_DATA_API_KEY", "")
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Trading Configuration
    STOCK_SYMBOL: str = os.getenv("STOCK_SYMBOL", "AAPL")
    POSITION_SIZE: float = float(os.getenv("POSITION_SIZE", "1000"))  # USD amount per trade
    MAX_POSITIONS: int = int(os.getenv("MAX_POSITIONS", "3"))
    
    # Technical Indicator Parameters
    RSI_PERIOD: int = int(os.getenv("RSI_PERIOD", "14"))
    RSI_OVERSOLD: float = float(os.getenv("RSI_OVERSOLD", "30"))
    RSI_OVERBOUGHT: float = float(os.getenv("RSI_OVERBOUGHT", "70"))
    
    MACD_FAST: int = int(os.getenv("MACD_FAST", "12"))
    MACD_SLOW: int = int(os.getenv("MACD_SLOW", "26"))
    MACD_SIGNAL: int = int(os.getenv("MACD_SIGNAL", "9"))
    
    ATR_PERIOD: int = int(os.getenv("ATR_PERIOD", "14"))
    ATR_STOP_MULTIPLIER: float = float(os.getenv("ATR_STOP_MULTIPLIER", "1.5"))
    ATR_TARGET_MULTIPLIER: float = float(os.getenv("ATR_TARGET_MULTIPLIER", "2.0"))
    
    # Sentiment Thresholds
    SENTIMENT_BULLISH_THRESHOLD: float = float(os.getenv("SENTIMENT_BULLISH_THRESHOLD", "0.4"))
    SENTIMENT_BEARISH_THRESHOLD: float = float(os.getenv("SENTIMENT_BEARISH_THRESHOLD", "-0.4"))
    
    # Risk Management
    MAX_DAILY_LOSS: float = float(os.getenv("MAX_DAILY_LOSS", "500"))  # USD
    MAX_DRAWDOWN: float = float(os.getenv("MAX_DRAWDOWN", "0.05"))  # 5%
    
    # Trading Hours (24-hour format)
    TRADING_START_HOUR: int = int(os.getenv("TRADING_START_HOUR", "9"))
    TRADING_END_HOUR: int = int(os.getenv("TRADING_END_HOUR", "16"))
    
    # Alpaca Environment
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")  # Paper trading by default
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        missing_keys = []
        warnings = []
        
        # Check required API keys
        required_keys = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "TWELVE_DATA_API_KEY": cls.TWELVE_DATA_API_KEY,
        }
        
        for key, value in required_keys.items():
            if not value:
                missing_keys.append(key)
        
        # Check optional but recommended keys
        optional_keys = {
            "ALPACA_API_KEY": cls.ALPACA_API_KEY,
            "ALPACA_SECRET_KEY": cls.ALPACA_SECRET_KEY,
            "TELEGRAM_TOKEN": cls.TELEGRAM_TOKEN,
            "TELEGRAM_CHAT_ID": cls.TELEGRAM_CHAT_ID,
        }
        
        for key, value in optional_keys.items():
            if not value:
                warnings.append(f"{key} not set - related functionality will be disabled")
        
        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys,
            "warnings": warnings
        }
    
    @classmethod
    def get_trading_symbols(cls) -> list:
        """Get list of symbols to trade"""
        symbols_str = os.getenv("TRADING_SYMBOLS", cls.STOCK_SYMBOL)
        return [symbol.strip().upper() for symbol in symbols_str.split(",")]
    
    @classmethod
    def is_trading_hours(cls) -> bool:
        """Check if current time is within trading hours"""
        from datetime import datetime
        current_hour = datetime.now().hour
        return cls.TRADING_START_HOUR <= current_hour < cls.TRADING_END_HOUR
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("=== SentimentTrade Configuration ===")
        print(f"Stock Symbol: {cls.STOCK_SYMBOL}")
        print(f"Position Size: ${cls.POSITION_SIZE}")
        print(f"Max Positions: {cls.MAX_POSITIONS}")
        print(f"RSI Period: {cls.RSI_PERIOD} (Oversold: {cls.RSI_OVERSOLD}, Overbought: {cls.RSI_OVERBOUGHT})")
        print(f"MACD: {cls.MACD_FAST}/{cls.MACD_SLOW}/{cls.MACD_SIGNAL}")
        print(f"ATR Period: {cls.ATR_PERIOD} (Stop: {cls.ATR_STOP_MULTIPLIER}x, Target: {cls.ATR_TARGET_MULTIPLIER}x)")
        print(f"Sentiment Thresholds: Bullish > {cls.SENTIMENT_BULLISH_THRESHOLD}, Bearish < {cls.SENTIMENT_BEARISH_THRESHOLD}")
        print(f"Trading Hours: {cls.TRADING_START_HOUR}:00 - {cls.TRADING_END_HOUR}:00")
        print(f"Max Daily Loss: ${cls.MAX_DAILY_LOSS}")
        print(f"Alpaca Environment: {cls.ALPACA_BASE_URL}")
        
        # Show API key status
        validation = cls.validate_config()
        if validation["valid"]:
            print("✅ All required API keys configured")
        else:
            print(f"❌ Missing required keys: {', '.join(validation['missing_keys'])}")
        
        if validation["warnings"]:
            print("⚠️  Warnings:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")

# Create global config instance
config = Config()

if __name__ == "__main__":
    # Test configuration
    config.print_config()
    validation = config.validate_config()
    print(f"\nConfiguration valid: {validation['valid']}")
