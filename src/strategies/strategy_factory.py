"""
Strategy Factory
Manages different trading strategies and provides a unified interface
Allows easy extension for new strategies (aggressive, conservative, momentum)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional, Type
import logging
from abc import ABC, abstractmethod

from trading_config import TradingConfig, get_strategy_config
from database import UserPreferences
from .default_strategy import DefaultStrategy

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, config: TradingConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    @abstractmethod
    def analyze_symbol(self, symbol: str, market_data: Dict[str, Any], 
                      sentiment_score: float = 0.0) -> Dict[str, Any]:
        """Analyze a symbol and generate trading signal"""
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy"""
        pass

class StrategyFactory:
    """Factory class for creating and managing trading strategies"""
    
    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register built-in strategies"""
        self._strategies['default'] = DefaultStrategy
        # Future strategies will be registered here
        # self._strategies['aggressive'] = AggressiveStrategy
        # self._strategies['conservative'] = ConservativeStrategy
        # self._strategies['momentum'] = MomentumStrategy
    
    def register_strategy(self, name: str, strategy_class: Type[BaseStrategy]):
        """Register a new strategy"""
        self._strategies[name] = strategy_class
    
    def get_available_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available strategies"""
        strategies_info = {}
        
        # Default strategy (always available)
        strategies_info['default'] = {
            'name': 'Default Strategy',
            'description': 'Balanced approach with moderate risk and steady returns',
            'risk_level': 'moderate',
            'available': True,
            'indicators': ['RSI', 'MACD', 'Moving Averages', 'Bollinger Bands', 'ATR'],
            'suitable_for': ['beginners', 'balanced_traders']
        }
        
        # Future strategies (coming soon)
        strategies_info['aggressive'] = {
            'name': 'Aggressive Growth',
            'description': 'Higher risk strategy targeting maximum returns with momentum focus',
            'risk_level': 'high',
            'available': False,  # Coming soon
            'indicators': ['RSI', 'MACD', 'Momentum', 'Volume', 'Breakout Patterns'],
            'suitable_for': ['experienced_traders', 'high_risk_tolerance']
        }
        
        strategies_info['conservative'] = {
            'name': 'Conservative',
            'description': 'Lower risk strategy focusing on capital preservation',
            'risk_level': 'low',
            'available': False,  # Coming soon
            'indicators': ['RSI', 'SMA', 'Bollinger Bands', 'Support/Resistance'],
            'suitable_for': ['risk_averse', 'income_focused']
        }
        
        strategies_info['momentum'] = {
            'name': 'Momentum Trading',
            'description': 'Trend-following strategy with momentum indicators',
            'risk_level': 'moderate',
            'available': False,  # Coming soon
            'indicators': ['MACD', 'Momentum', 'Volume', 'Trend Lines'],
            'suitable_for': ['trend_followers', 'active_traders']
        }
        
        return strategies_info
    
    def create_strategy(self, strategy_name: str, user_preferences: Optional[UserPreferences] = None,
                       logger: Optional[logging.Logger] = None) -> BaseStrategy:
        """
        Create a strategy instance
        
        Args:
            strategy_name: Name of the strategy to create
            user_preferences: User preferences for configuration
            logger: Optional logger instance
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy is not available
        """
        
        # Validate strategy availability
        available_strategies = self.get_available_strategies()
        if strategy_name not in available_strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        if not available_strategies[strategy_name]['available']:
            # For now, fall back to default strategy
            logger = logger or logging.getLogger(__name__)
            logger.warning(f"Strategy '{strategy_name}' not yet available, using default strategy")
            strategy_name = 'default'
        
        # Get strategy configuration
        strategy_config = get_strategy_config(strategy_name, user_preferences)
        config = strategy_config['config']
        
        # Create strategy instance
        strategy_class = self._strategies.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"Strategy implementation not found: {strategy_name}")
        
        return strategy_class(config, logger)
    
    def get_strategy_for_user(self, user_preferences: UserPreferences,
                             logger: Optional[logging.Logger] = None) -> BaseStrategy:
        """
        Get the appropriate strategy for a user based on their preferences
        
        Args:
            user_preferences: User's trading preferences
            logger: Optional logger instance
            
        Returns:
            Strategy instance configured for the user
        """
        strategy_name = user_preferences.strategy
        return self.create_strategy(strategy_name, user_preferences, logger)
    
    def analyze_with_strategy(self, strategy_name: str, symbol: str, 
                            market_data: Dict[str, Any], sentiment_score: float = 0.0,
                            user_preferences: Optional[UserPreferences] = None,
                            logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
        """
        Analyze a symbol using a specific strategy
        
        Args:
            strategy_name: Name of the strategy to use
            symbol: Stock symbol to analyze
            market_data: Market data for analysis
            sentiment_score: Sentiment analysis score
            user_preferences: User preferences for configuration
            logger: Optional logger instance
            
        Returns:
            Analysis results
        """
        try:
            strategy = self.create_strategy(strategy_name, user_preferences, logger)
            return strategy.analyze_symbol(symbol, market_data, sentiment_score)
        except Exception as e:
            logger = logger or logging.getLogger(__name__)
            logger.error(f"Error analyzing {symbol} with {strategy_name} strategy: {e}")
            
            # Return error response
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'confidence': 0.0,
                'current_price': 0.0,
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'target_price': 0.0,
                'risk_reward_ratio': 0.0,
                'sentiment': sentiment_score,
                'reasoning': f'Strategy analysis failed: {str(e)}',
                'strategy': strategy_name,
                'error': str(e)
            }

# Global strategy factory instance
strategy_factory = StrategyFactory()

# Convenience functions
def get_available_strategies() -> Dict[str, Dict[str, Any]]:
    """Get information about all available strategies"""
    return strategy_factory.get_available_strategies()

def create_strategy(strategy_name: str, user_preferences: Optional[UserPreferences] = None,
                   logger: Optional[logging.Logger] = None) -> BaseStrategy:
    """Create a strategy instance"""
    return strategy_factory.create_strategy(strategy_name, user_preferences, logger)

def analyze_symbol(strategy_name: str, symbol: str, market_data: Dict[str, Any],
                  sentiment_score: float = 0.0, user_preferences: Optional[UserPreferences] = None,
                  logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Analyze a symbol using a specific strategy"""
    return strategy_factory.analyze_with_strategy(
        strategy_name, symbol, market_data, sentiment_score, user_preferences, logger
    )
