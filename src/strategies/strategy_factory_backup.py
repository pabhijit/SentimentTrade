#!/usr/bin/env python3
"""
Strategy Factory for SentimentTrade Platform

Manages different trading strategies and provides a unified interface for strategy
creation, registration, and execution. Supports multiple strategy types including
momentum, mean reversion, and sentiment-based approaches.

This factory pattern allows easy extension for new strategies while maintaining
a consistent interface for strategy analysis and execution.

Author: SentimentTrade Development Team
Version: 2.0.0
Last Updated: July 2025
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
from .momentum_strategy import MomentumStrategy
from .mean_reversion_strategy import MeanReversionStrategy


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    
    Defines the interface that all trading strategies must implement,
    ensuring consistency across different strategy types.
    """
    
    def __init__(self, config: TradingConfig, logger: Optional[logging.Logger] = None):
        """
        Initialize base strategy
        
        Args:
            config: Trading configuration object
            logger: Optional logger for strategy events
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
    
    @abstractmethod
    def analyze_symbol(self, symbol: str, market_data: Dict[str, Any], 
                      sentiment_score: float = 0.0) -> Dict[str, Any]:
        """
        Analyze a symbol and generate trading signal
        
        Args:
            symbol: Stock symbol to analyze
            market_data: Historical and current market data
            sentiment_score: Sentiment analysis score (-1 to 1)
            
        Returns:
            Dictionary containing trading signal and analysis
        """
        pass
    
    @abstractmethod
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about this strategy
        
        Returns:
            Dictionary containing strategy metadata and characteristics
        """
        pass


class StrategyFactory:
    """
    Factory class for creating and managing trading strategies
    
    Provides centralized strategy management with registration, creation,
    and analysis capabilities. Supports both built-in and custom strategies.
    """
    
    def __init__(self):
        """Initialize the strategy factory with built-in strategies"""
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """
        Register built-in strategies
        
        Registers all available strategy implementations with the factory.
        New strategies should be added here when implemented.
        """
        # Core strategies
        self._strategies['default'] = DefaultStrategy
        self._strategies['momentum'] = MomentumStrategy
        self._strategies['mean_reversion'] = MeanReversionStrategy
        
        # Future strategies (to be implemented)
        # self._strategies['aggressive'] = AggressiveStrategy
        # self._strategies['conservative'] = ConservativeStrategy
        # self._strategies['breakout'] = BreakoutStrategy
        # self._strategies['pairs_trading'] = PairsTradingStrategy
    
    def register_strategy(self, name: str, strategy_class: Type[BaseStrategy]):
        """
        Register a new custom strategy
        
        Args:
            name: Unique name for the strategy
            strategy_class: Strategy class implementing BaseStrategy
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"Strategy class must inherit from BaseStrategy")
        
        self._strategies[name] = strategy_class
        self.logger.info(f"Registered custom strategy: {name}")
    
    def get_available_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available strategies
        
        Returns:
            Dictionary mapping strategy names to their metadata and availability
        """
        strategies_info = {}
        
        # === Default Strategy ===
        strategies_info['default'] = {
            'name': 'Default Strategy',
            'description': 'Balanced approach with moderate risk and steady returns',
            'risk_level': 'moderate',
            'available': True,
            'indicators': ['RSI', 'MACD', 'Moving Averages', 'Bollinger Bands', 'ATR'],
            'suitable_for': ['beginners', 'balanced_traders'],
            'market_conditions': ['trending', 'sideways'],
            'win_rate_range': '45-65%',
            'typical_holding_period': '1-5 days'
        }
        
        # === Momentum Strategy ===
        strategies_info['momentum'] = {
            'name': 'Momentum Trading',
            'description': 'Dual moving average crossover strategy for trend following',
            'risk_level': 'medium',
            'available': True,
            'indicators': ['Fast MA', 'Slow MA', 'Crossover Signals'],
            'suitable_for': ['trend_followers', 'active_traders'],
            'market_conditions': ['trending'],
            'win_rate_range': '40-60%',
            'typical_holding_period': '2-10 days',
            'parameters': {
                'fast_ma': {'default': 10, 'range': '5-20', 'description': 'Fast moving average period'},
                'slow_ma': {'default': 30, 'range': '20-50', 'description': 'Slow moving average period'}
            }
        }
        
        # === Mean Reversion Strategy ===
        strategies_info['mean_reversion'] = {
            'name': 'Mean Reversion',
            'description': 'Bollinger Bands-based contrarian strategy for range-bound markets',
            'risk_level': 'medium-high',
            'available': True,
            'indicators': ['Bollinger Bands', 'Band Width', 'Band Position'],
            'suitable_for': ['contrarian_traders', 'range_traders'],
            'market_conditions': ['sideways', 'volatile'],
            'win_rate_range': '60-75%',
            'typical_holding_period': '1-3 days',
            'parameters': {
                'period': {'default': 20, 'range': '10-30', 'description': 'Bollinger Bands period'},
                'devfactor': {'default': 2.0, 'range': '1.5-3.0', 'description': 'Standard deviation multiplier'}
            }
        }
        
        # === Future Strategies (Coming Soon) ===
        strategies_info['aggressive'] = {
            'name': 'Aggressive Growth',
            'description': 'Higher risk strategy targeting maximum returns with momentum focus',
            'risk_level': 'high',
            'available': False,  # Coming soon
            'indicators': ['RSI', 'MACD', 'Momentum', 'Volume', 'Breakout Patterns'],
            'suitable_for': ['experienced_traders', 'high_risk_tolerance'],
            'market_conditions': ['trending', 'volatile'],
            'win_rate_range': '35-55%',
            'typical_holding_period': '1-7 days'
        }
        
        strategies_info['conservative'] = {
            'name': 'Conservative',
            'description': 'Lower risk strategy focusing on capital preservation',
            'risk_level': 'low',
            'available': False,  # Coming soon
            'indicators': ['RSI', 'SMA', 'Bollinger Bands', 'Support/Resistance'],
            'suitable_for': ['risk_averse', 'income_focused'],
            'market_conditions': ['trending', 'stable'],
            'win_rate_range': '55-70%',
            'typical_holding_period': '3-14 days'
        }
        
        strategies_info['breakout'] = {
            'name': 'Breakout Trading',
            'description': 'Identifies and trades significant price breakouts from consolidation',
            'risk_level': 'medium-high',
            'available': False,  # Coming soon
            'indicators': ['Support/Resistance', 'Volume', 'ATR', 'Consolidation Patterns'],
            'suitable_for': ['breakout_traders', 'momentum_traders'],
            'market_conditions': ['consolidating', 'pre_breakout'],
            'win_rate_range': '40-60%',
            'typical_holding_period': '1-5 days'
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
            Strategy instance configured according to preferences
            
        Raises:
            ValueError: If strategy is not available or unknown
        """
        
        # Validate strategy availability
        available_strategies = self.get_available_strategies()
        if strategy_name not in available_strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(available_strategies.keys())}")
        
        # Check if strategy is implemented
        if not available_strategies[strategy_name]['available']:
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
        
        # Log strategy creation
        logger = logger or logging.getLogger(__name__)
        logger.info(f"Created {strategy_name} strategy with config: {config}")
        
        return strategy_class(config, logger)
    
    def get_strategy_for_user(self, user_preferences: UserPreferences,
                             logger: Optional[logging.Logger] = None) -> BaseStrategy:
        """
        Get the appropriate strategy for a user based on their preferences
        
        Args:
            user_preferences: User's trading preferences and risk profile
            logger: Optional logger instance
            
        Returns:
            Strategy instance configured for the user's preferences
        """
        strategy_name = user_preferences.strategy
        
        # Log user strategy selection
        logger = logger or logging.getLogger(__name__)
        logger.info(f"Creating strategy for user: {user_preferences.user_id}, "
                   f"strategy: {strategy_name}, risk_tolerance: {user_preferences.risk_tolerance}")
        
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
            sentiment_score: Sentiment analysis score (-1 to 1)
            user_preferences: User preferences for configuration
            logger: Optional logger instance
            
        Returns:
            Analysis results with trading signals and reasoning
        """
        logger = logger or logging.getLogger(__name__)
        
        try:
            # Create strategy instance
            strategy = self.create_strategy(strategy_name, user_preferences, logger)
            
            # Log analysis start
            logger.info(f"Analyzing {symbol} with {strategy_name} strategy, "
                       f"sentiment: {sentiment_score:.3f}")
            
            # Perform analysis
            result = strategy.analyze_symbol(symbol, market_data, sentiment_score)
            
            # Add strategy metadata to result
            result['strategy_used'] = strategy_name
            result['analysis_timestamp'] = market_data.get('timestamp', 'unknown')
            
            # Log analysis result
            logger.info(f"Analysis complete for {symbol}: {result.get('action', 'UNKNOWN')} "
                       f"with confidence {result.get('confidence', 0.0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol} with {strategy_name} strategy: {e}")
            
            # Return error response with fallback analysis
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'confidence': 0.0,
                'current_price': market_data.get('current_price', 0.0),
                'entry_price': market_data.get('current_price', 0.0),
                'stop_loss': 0.0,
                'target_price': 0.0,
                'risk_reward_ratio': 0.0,
                'sentiment': sentiment_score,
                'reasoning': f'Strategy analysis failed: {str(e)}. Defaulting to HOLD.',
                'strategy_used': strategy_name,
                'error': str(e),
                'fallback_applied': True
            }
    
    def get_strategy_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get strategy recommendations based on user profile
        
        Args:
            user_profile: User's trading profile and preferences
            
        Returns:
            Dictionary with recommended strategies and reasoning
        """
        recommendations = {}
        
        # Extract user characteristics
        risk_tolerance = user_profile.get('risk_tolerance', 'medium').lower()
        experience_level = user_profile.get('experience_level', 'beginner').lower()
        trading_style = user_profile.get('trading_style', 'balanced').lower()
        market_preference = user_profile.get('market_preference', 'any').lower()
        
        # Strategy scoring based on user profile
        strategy_scores = {}
        
        # Default strategy - good for beginners
        if experience_level in ['beginner', 'novice']:
            strategy_scores['default'] = 0.9
        else:
            strategy_scores['default'] = 0.6
        
        # Momentum strategy - good for trend followers
        if trading_style in ['momentum', 'trend_following'] or market_preference == 'trending':
            strategy_scores['momentum'] = 0.8
        elif risk_tolerance in ['medium', 'high']:
            strategy_scores['momentum'] = 0.7
        else:
            strategy_scores['momentum'] = 0.4
        
        # Mean reversion - good for contrarian traders
        if trading_style in ['contrarian', 'mean_reversion'] or market_preference == 'sideways':
            strategy_scores['mean_reversion'] = 0.8
        elif risk_tolerance in ['medium', 'high'] and experience_level != 'beginner':
            strategy_scores['mean_reversion'] = 0.6
        else:
            strategy_scores['mean_reversion'] = 0.3
        
        # Sort strategies by score
        sorted_strategies = sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations['primary'] = sorted_strategies[0][0]
        recommendations['alternatives'] = [s[0] for s in sorted_strategies[1:3]]
        recommendations['scores'] = strategy_scores
        recommendations['reasoning'] = self._generate_recommendation_reasoning(
            user_profile, sorted_strategies[0][0]
        )
        
        return recommendations
    
    def _generate_recommendation_reasoning(self, user_profile: Dict[str, Any], 
                                        recommended_strategy: str) -> str:
        """
        Generate reasoning for strategy recommendation
        
        Args:
            user_profile: User's profile information
            recommended_strategy: The recommended strategy name
            
        Returns:
            String explaining why this strategy was recommended
        """
        risk_tolerance = user_profile.get('risk_tolerance', 'medium')
        experience_level = user_profile.get('experience_level', 'beginner')
        
        reasoning_map = {
            'default': f"Recommended for {experience_level} traders with {risk_tolerance} risk tolerance. "
                      "Provides balanced approach with moderate risk and steady returns.",
            
            'momentum': f"Suitable for traders who prefer trend-following strategies. "
                       f"Works well with {risk_tolerance} risk tolerance and trending markets.",
            
            'mean_reversion': f"Ideal for contrarian traders with {risk_tolerance} risk tolerance. "
                             "Effective in range-bound and volatile market conditions."
        }
        
        return reasoning_map.get(recommended_strategy, 
                               f"Strategy selected based on {risk_tolerance} risk profile.")


# === Global Strategy Factory Instance ===
strategy_factory = StrategyFactory()


# === Convenience Functions ===
def get_available_strategies() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all available strategies
    
    Returns:
        Dictionary mapping strategy names to their metadata
    """
    return strategy_factory.get_available_strategies()


def create_strategy(strategy_name: str, user_preferences: Optional[UserPreferences] = None,
                   logger: Optional[logging.Logger] = None) -> BaseStrategy:
    """
    Create a strategy instance
    
    Args:
        strategy_name: Name of the strategy to create
        user_preferences: Optional user preferences
        logger: Optional logger instance
        
    Returns:
        Configured strategy instance
    """
    return strategy_factory.create_strategy(strategy_name, user_preferences, logger)


def analyze_symbol(strategy_name: str, symbol: str, market_data: Dict[str, Any],
                  sentiment_score: float = 0.0, user_preferences: Optional[UserPreferences] = None,
                  logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Analyze a symbol using a specific strategy
    
    Args:
        strategy_name: Name of the strategy to use
        symbol: Stock symbol to analyze
        market_data: Market data for analysis
        sentiment_score: Sentiment analysis score
        user_preferences: Optional user preferences
        logger: Optional logger instance
        
    Returns:
        Analysis results with trading signals
    """
    return strategy_factory.analyze_with_strategy(
        strategy_name, symbol, market_data, sentiment_score, user_preferences, logger
    )


def get_strategy_recommendations(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get strategy recommendations based on user profile
    
    Args:
        user_profile: User's trading profile and preferences
        
    Returns:
        Dictionary with recommended strategies and reasoning
    """
    return strategy_factory.get_strategy_recommendations(user_profile)


# === Strategy Metadata ===
__module_name__ = "Strategy Factory"
__module_version__ = "2.0.0"
__module_description__ = "Centralized strategy management and creation system"
__module_author__ = "SentimentTrade Development Team"
__supported_strategies__ = ["default", "momentum", "mean_reversion"]
__future_strategies__ = ["aggressive", "conservative", "breakout", "pairs_trading"]
