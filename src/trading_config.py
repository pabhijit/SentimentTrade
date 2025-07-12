"""
Trading Configuration Manager
Handles trading parameters that can be customized per user preferences
Replaces static .env trading config with dynamic user-based settings
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from database import UserPreferences
import os

@dataclass
class TradingConfig:
    """Trading configuration with user-customizable parameters"""
    
    # Position Management
    position_size: float = 1000.0  # USD per trade
    max_positions: int = 3
    max_daily_loss: float = 500.0
    max_drawdown: float = 0.05  # 5%
    
    # Technical Indicators
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    atr_period: int = 14
    atr_stop_multiplier: float = 1.5
    atr_target_multiplier: float = 2.0
    
    # Sentiment Analysis
    sentiment_bullish_threshold: float = 0.4
    sentiment_bearish_threshold: float = -0.4
    
    # Signal Filtering (from user preferences)
    min_confidence: float = 0.7
    max_daily_signals: int = 10
    
    # Risk Management (from user preferences)
    stop_loss_percentage: float = 0.05  # 5%
    take_profit_percentage: float = 0.15  # 15%
    
    # Trading Hours
    trading_start_hour: int = 9
    trading_end_hour: int = 16

class TradingConfigManager:
    """Manages trading configuration with user preference integration"""
    
    def __init__(self):
        self.base_config = self._load_base_config()
    
    def _load_base_config(self) -> TradingConfig:
        """Load base configuration from environment variables"""
        return TradingConfig(
            # Position Management
            position_size=float(os.getenv('POSITION_SIZE', 1000.0)),
            max_positions=int(os.getenv('MAX_POSITIONS', 3)),
            max_daily_loss=float(os.getenv('MAX_DAILY_LOSS', 500.0)),
            max_drawdown=float(os.getenv('MAX_DRAWDOWN', 0.05)),
            
            # Technical Indicators
            rsi_period=int(os.getenv('RSI_PERIOD', 14)),
            rsi_oversold=float(os.getenv('RSI_OVERSOLD', 30.0)),
            rsi_overbought=float(os.getenv('RSI_OVERBOUGHT', 70.0)),
            macd_fast=int(os.getenv('MACD_FAST', 12)),
            macd_slow=int(os.getenv('MACD_SLOW', 26)),
            macd_signal=int(os.getenv('MACD_SIGNAL', 9)),
            atr_period=int(os.getenv('ATR_PERIOD', 14)),
            atr_stop_multiplier=float(os.getenv('ATR_STOP_MULTIPLIER', 1.5)),
            atr_target_multiplier=float(os.getenv('ATR_TARGET_MULTIPLIER', 2.0)),
            
            # Sentiment Analysis
            sentiment_bullish_threshold=float(os.getenv('SENTIMENT_BULLISH_THRESHOLD', 0.4)),
            sentiment_bearish_threshold=float(os.getenv('SENTIMENT_BEARISH_THRESHOLD', -0.4)),
            
            # Trading Hours
            trading_start_hour=int(os.getenv('TRADING_START_HOUR', 9)),
            trading_end_hour=int(os.getenv('TRADING_END_HOUR', 16))
        )
    
    def get_user_config(self, user_preferences: Optional[UserPreferences] = None) -> TradingConfig:
        """Get trading configuration customized for user preferences"""
        config = TradingConfig(
            # Copy base configuration
            position_size=self.base_config.position_size,
            max_positions=self.base_config.max_positions,
            max_daily_loss=self.base_config.max_daily_loss,
            max_drawdown=self.base_config.max_drawdown,
            rsi_period=self.base_config.rsi_period,
            rsi_oversold=self.base_config.rsi_oversold,
            rsi_overbought=self.base_config.rsi_overbought,
            macd_fast=self.base_config.macd_fast,
            macd_slow=self.base_config.macd_slow,
            macd_signal=self.base_config.macd_signal,
            atr_period=self.base_config.atr_period,
            atr_stop_multiplier=self.base_config.atr_stop_multiplier,
            atr_target_multiplier=self.base_config.atr_target_multiplier,
            sentiment_bullish_threshold=self.base_config.sentiment_bullish_threshold,
            sentiment_bearish_threshold=self.base_config.sentiment_bearish_threshold,
            trading_start_hour=self.base_config.trading_start_hour,
            trading_end_hour=self.base_config.trading_end_hour
        )
        
        # Apply user preferences if provided
        if user_preferences:
            config.min_confidence = user_preferences.min_confidence
            config.max_daily_signals = user_preferences.max_daily_signals
            config.stop_loss_percentage = user_preferences.stop_loss_percentage
            config.take_profit_percentage = user_preferences.take_profit_percentage
            config.position_size = user_preferences.max_position_size
            
            # Adjust risk parameters based on risk appetite
            config = self._apply_risk_adjustments(config, user_preferences.risk_appetite)
        
        return config
    
    def _apply_risk_adjustments(self, config: TradingConfig, risk_appetite: str) -> TradingConfig:
        """Apply risk-based adjustments to trading configuration"""
        
        if risk_appetite == "low":  # Conservative
            # More conservative indicator settings
            config.rsi_oversold = 25.0  # More oversold before buying
            config.rsi_overbought = 75.0  # More overbought before selling
            config.atr_stop_multiplier = 1.0  # Tighter stops
            config.atr_target_multiplier = 1.5  # Lower targets
            config.sentiment_bullish_threshold = 0.6  # Higher sentiment required
            config.sentiment_bearish_threshold = -0.6
            config.max_daily_loss = config.max_daily_loss * 0.5  # Lower loss limit
            
        elif risk_appetite == "high":  # Aggressive
            # More aggressive indicator settings
            config.rsi_oversold = 35.0  # Less oversold before buying
            config.rsi_overbought = 65.0  # Less overbought before selling
            config.atr_stop_multiplier = 2.0  # Wider stops
            config.atr_target_multiplier = 3.0  # Higher targets
            config.sentiment_bullish_threshold = 0.2  # Lower sentiment required
            config.sentiment_bearish_threshold = -0.2
            config.max_daily_loss = config.max_daily_loss * 2.0  # Higher loss limit
            config.max_positions = min(config.max_positions + 2, 10)  # More positions
        
        # Moderate uses base settings
        return config
    
    def get_strategy_config(self, strategy: str, user_preferences: Optional[UserPreferences] = None) -> Dict[str, Any]:
        """Get configuration specific to a trading strategy"""
        base_config = self.get_user_config(user_preferences)
        
        strategy_configs = {
            "default": {
                "name": "Default Balanced Strategy",
                "description": "Balanced approach using RSI, MACD, and sentiment",
                "config": base_config,
                "indicators": ["rsi", "macd", "atr", "sentiment"],
                "signal_weight": {
                    "technical": 0.6,
                    "sentiment": 0.4
                }
            },
            "aggressive": {
                "name": "Aggressive Growth Strategy",
                "description": "Higher risk, momentum-focused approach",
                "config": base_config,
                "indicators": ["rsi", "macd", "momentum", "volume"],
                "signal_weight": {
                    "technical": 0.8,
                    "sentiment": 0.2
                }
            },
            "conservative": {
                "name": "Conservative Strategy",
                "description": "Risk-averse approach with strong confirmations",
                "config": base_config,
                "indicators": ["rsi", "sma", "bollinger", "sentiment"],
                "signal_weight": {
                    "technical": 0.4,
                    "sentiment": 0.6
                }
            },
            "momentum": {
                "name": "Momentum Strategy",
                "description": "Trend-following with momentum indicators",
                "config": base_config,
                "indicators": ["macd", "momentum", "volume", "trend"],
                "signal_weight": {
                    "technical": 0.9,
                    "sentiment": 0.1
                }
            }
        }
        
        return strategy_configs.get(strategy, strategy_configs["default"])

# Global instance
trading_config_manager = TradingConfigManager()

def get_trading_config(user_preferences: Optional[UserPreferences] = None) -> TradingConfig:
    """Convenience function to get trading configuration"""
    return trading_config_manager.get_user_config(user_preferences)

def get_strategy_config(strategy: str, user_preferences: Optional[UserPreferences] = None) -> Dict[str, Any]:
    """Convenience function to get strategy-specific configuration"""
    return trading_config_manager.get_strategy_config(strategy, user_preferences)
