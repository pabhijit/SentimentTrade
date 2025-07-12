#!/usr/bin/env python3
"""
Updated Strategy Factory for SentimentTrade Platform

Enhanced factory including the new QQQ LEAPS options strategy alongside
existing momentum, mean reversion, and sentiment-based approaches.

Author: SentimentTrade Development Team
Version: 2.1.0
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
from .mechanical_options_strategy import MechanicalOptionsStrategy


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
    """Enhanced Factory class for creating and managing trading strategies"""
    
    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register all available strategy implementations"""
        
        # Core strategies
        self._strategies['default'] = DefaultStrategy
        self._strategies['momentum'] = MomentumStrategy
        self._strategies['mean_reversion'] = MeanReversionStrategy
        self._strategies['mechanical_options'] = MechanicalOptionsStrategy
        
        # Future strategies (to be implemented)
        # self._strategies['aggressive'] = AggressiveStrategy
        # self._strategies['conservative'] = ConservativeStrategy
        # self._strategies['breakout'] = BreakoutStrategy
        # self._strategies['pairs_trading'] = PairsTradingStrategy
    
    def get_available_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available strategies"""
        
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
            'typical_holding_period': '1-5 days',
            'asset_class': 'stocks'
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
            'asset_class': 'stocks',
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
            'asset_class': 'stocks',
            'parameters': {
                'period': {'default': 20, 'range': '10-30', 'description': 'Bollinger Bands period'},
                'devfactor': {'default': 2.0, 'range': '1.5-3.0', 'description': 'Standard deviation multiplier'}
            }
        }
        
        # === Mechanical Options Strategy ===
        strategies_info['mechanical_options'] = {
            'name': 'Mechanical Options Strategy',
            'description': 'Enhanced mechanical options strategy with 3 scenarios: Basic (91%), Gap+Trend (96%), Pullback+Trend (96%+)',
            'risk_level': 'medium',
            'available': True,
            'indicators': ['Daily Returns', 'Gap Analysis', 'SMA Trend', 'ATH Pullback'],
            'suitable_for': ['options_traders', 'long_term_investors', 'mechanical_traders'],
            'market_conditions': ['bull_markets', 'corrections', 'recovery'],
            'win_rate_range': '91-96%+',
            'typical_holding_period': '3-4 months',
            'asset_class': 'options',
            'underlying_asset': 'QQQ',
            'historical_performance': {
                'scenario_1_win_rate': '91%',
                'scenario_2_win_rate': '96%',
                'scenario_3_win_rate': '96%+',
                'total_return': '705% over 5 years',
                'max_drawdown': '18%',
                'avg_winner': '$2,560',
                'avg_loser': '$3,348'
            },
            'parameters': {
                'scenario': {'default': 1, 'range': '1-3', 'description': 'Trading scenario (1=Basic, 2=Gap+Trend, 3=Pullback+Trend)'},
                'min_drop_pct': {'default': 1.0, 'range': '0.5-2.0', 'description': 'Minimum daily drop to trigger entry'},
                'target_profit_pct': {'default': 50.0, 'range': '30-100', 'description': 'Target profit percentage'},
                'target_delta': {'default': 65, 'range': '60-80', 'description': 'Target option delta'},
                'expiry_months': {'default': 12, 'range': '9-18', 'description': 'LEAPS expiry in months'}
            },
            'special_features': [
                'Three distinct trading scenarios',
                'Optimized entry criteria for higher win rates',
                'Gap analysis and trend confirmation',
                'ATH pullback detection',
                'No technical analysis required',
                'Set and forget monthly management',
                'Mechanical entry/exit rules'
            ]
        }
        
        # === Future Strategies (Coming Soon) ===
        strategies_info['aggressive'] = {
            'name': 'Aggressive Growth',
            'description': 'Higher risk strategy targeting maximum returns with momentum focus',
            'risk_level': 'high',
            'available': False,
            'indicators': ['RSI', 'MACD', 'Momentum', 'Volume', 'Breakout Patterns'],
            'suitable_for': ['experienced_traders', 'high_risk_tolerance'],
            'market_conditions': ['trending', 'volatile'],
            'win_rate_range': '35-55%',
            'typical_holding_period': '1-7 days',
            'asset_class': 'stocks'
        }
        
        strategies_info['conservative'] = {
            'name': 'Conservative',
            'description': 'Lower risk strategy focusing on capital preservation',
            'risk_level': 'low',
            'available': False,
            'indicators': ['RSI', 'SMA', 'Bollinger Bands', 'Support/Resistance'],
            'suitable_for': ['risk_averse', 'income_focused'],
            'market_conditions': ['trending', 'stable'],
            'win_rate_range': '55-70%',
            'typical_holding_period': '3-14 days',
            'asset_class': 'stocks'
        }
        
        return strategies_info
    
    def create_strategy(self, strategy_name: str, user_preferences: Optional[UserPreferences] = None,
                       logger: Optional[logging.Logger] = None) -> BaseStrategy:
        """Create a strategy instance"""
        
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
    
    def get_strategy_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy recommendations based on user profile"""
        
        recommendations = {}
        
        # Extract user characteristics
        risk_tolerance = user_profile.get('risk_tolerance', 'medium').lower()
        experience_level = user_profile.get('experience_level', 'beginner').lower()
        trading_style = user_profile.get('trading_style', 'balanced').lower()
        market_preference = user_profile.get('market_preference', 'any').lower()
        options_experience = user_profile.get('options_experience', False)
        
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
        
        # Mechanical Options - good for options traders and long-term investors
        if options_experience and trading_style in ['long_term', 'mechanical', 'set_forget']:
            strategy_scores['mechanical_options'] = 0.9
        elif options_experience and risk_tolerance in ['medium', 'high']:
            strategy_scores['mechanical_options'] = 0.8
        elif experience_level in ['intermediate', 'advanced'] and risk_tolerance != 'low':
            strategy_scores['mechanical_options'] = 0.6
        else:
            strategy_scores['mechanical_options'] = 0.2  # Requires options knowledge
        
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
        """Generate reasoning for strategy recommendation"""
        
        risk_tolerance = user_profile.get('risk_tolerance', 'medium')
        experience_level = user_profile.get('experience_level', 'beginner')
        options_experience = user_profile.get('options_experience', False)
        
        reasoning_map = {
            'default': f"Recommended for {experience_level} traders with {risk_tolerance} risk tolerance. "
                      "Provides balanced approach with moderate risk and steady returns.",
            
            'momentum': f"Suitable for traders who prefer trend-following strategies. "
                       f"Works well with {risk_tolerance} risk tolerance and trending markets.",
            
            'mean_reversion': f"Ideal for contrarian traders with {risk_tolerance} risk tolerance. "
                             "Effective in range-bound and volatile market conditions.",
            
            'mechanical_options': f"Perfect for {'experienced' if options_experience else 'learning'} options traders. "
                        f"Mechanical strategy with 91-96%+ win rate, ideal for {risk_tolerance} risk tolerance. "
                        "Requires options trading knowledge but offers exceptional risk-adjusted returns."
        }
        
        return reasoning_map.get(recommended_strategy, 
                               f"Strategy selected based on {risk_tolerance} risk profile.")


# === Global Strategy Factory Instance ===
strategy_factory = StrategyFactory()


# === Convenience Functions ===
def get_available_strategies() -> Dict[str, Dict[str, Any]]:
    """Get information about all available strategies"""
    return strategy_factory.get_available_strategies()


def create_strategy(strategy_name: str, user_preferences: Optional[UserPreferences] = None,
                   logger: Optional[logging.Logger] = None) -> BaseStrategy:
    """Create a strategy instance"""
    return strategy_factory.create_strategy(strategy_name, user_preferences, logger)


def get_strategy_recommendations(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Get strategy recommendations based on user profile"""
    return strategy_factory.get_strategy_recommendations(user_profile)


# === Strategy Metadata ===
__module_name__ = "Enhanced Strategy Factory"
__module_version__ = "2.1.0"
__module_description__ = "Centralized strategy management including options strategies"
__module_author__ = "SentimentTrade Development Team"
__supported_strategies__ = ["default", "momentum", "mean_reversion", "mechanical_options"]
__future_strategies__ = ["aggressive", "conservative", "breakout", "pairs_trading"]
__new_features__ = ["Mechanical Options Strategy", "Options Trading Support", "Enhanced Recommendations"]
