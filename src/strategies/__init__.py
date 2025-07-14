#!/usr/bin/env python3
"""
Trading Strategies Package for SentimentTrade Platform

This package contains all trading strategy implementations including momentum,
mean reversion, sentiment-based approaches, and options strategies.

Available Strategies:
- DefaultStrategy: Balanced approach with moderate risk
- MomentumStrategy: Dual moving average crossover for trend following
- MeanReversionStrategy: Bollinger Bands-based contrarian trading
- MechanicalOptionsStrategy: Enhanced mechanical options strategy with 3 scenarios (91-96%+ win rates)

Author: SentimentTrade Development Team
Version: 2.1.0
Last Updated: July 2025
"""

# === Core Strategy Implementations ===
from .default_strategy import DefaultStrategy
from .momentum_strategy import MomentumStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .mechanical_options_strategy import MechanicalOptionsStrategy
from .break_retest_strategy import BreakRetestSwingStrategy

# === Strategy Management ===
from .strategy_factory import (
    StrategyFactory, 
    BaseStrategy,
    strategy_factory, 
    get_available_strategies, 
    create_strategy, 
    analyze_symbol
)

# === Package Exports ===
__all__ = [
    # Strategy Classes
    'DefaultStrategy',
    'MomentumStrategy', 
    'MeanReversionStrategy',
    'MechanicalOptionsStrategy',
    'BaseStrategy',
    'BreakRetestSwingStrategy',
    
    # Factory and Management
    'StrategyFactory', 
    'strategy_factory',
    
    # Convenience Functions
    'get_available_strategies',
    'create_strategy',
    'get_strategy_recommendations',
]

# === Package Metadata ===
__package_name__ = "SentimentTrade Strategies"
__package_version__ = "2.1.0"
__package_description__ = "Comprehensive trading strategy implementations including options"
__package_author__ = "SentimentTrade Development Team"

# === Strategy Summary ===
__available_strategies__ = {
    'default': {
        'class': 'DefaultStrategy',
        'type': 'balanced',
        'risk_level': 'moderate',
        'asset_class': 'stocks',
        'description': 'Balanced approach with moderate risk and steady returns'
    },
    'momentum': {
        'class': 'MomentumStrategy',
        'type': 'trend_following',
        'risk_level': 'medium',
        'asset_class': 'stocks',
        'description': 'Dual moving average crossover for trend following'
    },
    'mean_reversion': {
        'class': 'MeanReversionStrategy',
        'type': 'contrarian',
        'risk_level': 'medium_high',
        'asset_class': 'stocks',
        'description': 'Bollinger Bands-based contrarian trading'
    },
    'mechanical_options': {
        'class': 'MechanicalOptionsStrategy',
        'type': 'options_mechanical',
        'risk_level': 'medium',
        'asset_class': 'options',
        'underlying': 'QQQ',
        'description': 'Enhanced mechanical options strategy with 3 scenarios (91-96%+ win rates)',
        'nickname': 'The Enhanced Pelosi Special',
        'win_rate': '91-96%+',
        'historical_return': '705% over 5 years'
    },
    'break_retest': {
        'class': 'BreakRetestSwingStrategy',
        'type': 'swing_trading',
        'risk_level': 'medium_high',
        'asset_class': 'stocks',
        'description': 'Enhanced support/resistance breakout and retest strategy'
    }
}

# === Quick Access Functions ===
def list_strategies():
    """
    List all available strategies with their descriptions
    
    Returns:
        Dictionary of available strategies with metadata
    """
    return __available_strategies__.copy()

def get_strategy_info(strategy_name: str):
    """
    Get detailed information about a specific strategy
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Dictionary with strategy information or None if not found
    """
    return __available_strategies__.get(strategy_name)

def is_strategy_available(strategy_name: str) -> bool:
    """
    Check if a strategy is available
    
    Args:
        strategy_name: Name of the strategy to check
        
    Returns:
        True if strategy is available, False otherwise
    """
    return strategy_name in __available_strategies__

def get_options_strategies():
    """
    Get list of options-based strategies
    
    Returns:
        List of strategy names that trade options
    """
    return [name for name, info in __available_strategies__.items() 
            if info.get('asset_class') == 'options']

def get_stock_strategies():
    """
    Get list of stock-based strategies
    
    Returns:
        List of strategy names that trade stocks
    """
    return [name for name, info in __available_strategies__.items() 
            if info.get('asset_class') == 'stocks']

# Add convenience functions to exports
__all__.extend(['list_strategies', 'get_strategy_info', 'is_strategy_available', 
                'get_options_strategies', 'get_stock_strategies'])

# === Package Initialization ===
def _initialize_package():
    """Initialize the strategies package"""
    import logging
    logger = logging.getLogger(__name__)
    
    strategy_count = len(__available_strategies__)
    options_count = len(get_options_strategies())
    stock_count = len(get_stock_strategies())
    
    logger.info(f"SentimentTrade Strategies package initialized with {strategy_count} strategies")
    logger.info(f"  - Stock strategies: {stock_count}")
    logger.info(f"  - Options strategies: {options_count}")
    
    for name, info in __available_strategies__.items():
        asset_class = info.get('asset_class', 'unknown')
        risk_level = info.get('risk_level', 'unknown')
        logger.debug(f"  - {name}: {info['description']} ({asset_class}, {risk_level} risk)")
        
        # Special logging for high-performance strategies
        if 'win_rate' in info:
            logger.info(f"    🎯 {name}: {info['win_rate']} win rate, {info.get('historical_return', 'N/A')} return")

# Initialize package on import
_initialize_package()
