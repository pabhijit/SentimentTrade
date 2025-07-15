#!/usr/bin/env python3
"""
Unified Configuration for SentimentTrade Automation
Consolidates settings from runner_config.py and embedded configurations
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Strategy watchlists
BREAK_RETEST_WATCHLIST = [
    'AMD',    # 57.1% win rate
    'MSFT',   # 47.8% win rate  
    'BAC',    # 13.4% return
    'AAPL', 'NVDA', 'GOOGL', 'AMZN',
    'SPY', 'QQQ', 'JPM', 'XLF'
]

OPTIONS_WATCHLIST = [
    'QQQ',    # Primary focus - excellent options liquidity
    'SPY'     # Secondary focus
]

DEFAULT_WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'AMD', 'SPY', 'QQQ'
]

MOMENTUM_WATCHLIST = [
    'TSLA', 'NVDA', 'AMD', 'SHOP', 'AMZN', 'QQQ', 'ARKK'
]

MEAN_REVERSION_WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'SPY', 'QQQ'
]

# Strategy configurations
STRATEGY_CONFIGS = {
    'enhanced_break_retest': {
        'enabled': True,
        'description': 'Enhanced Break & Retest Strategy',
        'symbols': BREAK_RETEST_WATCHLIST,
        'alert_threshold': 0.65,
        'parameters': {
            'lookback_period': 20,
            'min_breakout_strength': 0.008,  # 0.8% optimized
            'position_size': 0.03,           # 3% risk per trade
            'trade_cooldown_days': 2,
            'regime_detection': True,        # Market adaptation
            'volatility_sizing': True,       # Dynamic sizing
            'max_portfolio_risk': 0.06,      # 6% max risk
        }
    },
    'options_break_retest': {
        'enabled': True,
        'description': 'Options Break & Retest Strategy',
        'symbols': OPTIONS_WATCHLIST,
        'alert_threshold': 0.70,
        'parameters': {
            'lookback_period': 20,
            'min_breakout_strength': 0.01,   # 1.0% for options
            'option_delta': 0.70,            # Target 0.7 delta
            'days_to_expiry': 45,            # 45 DTE
            'profit_target_pct': 0.50,       # 50% profit target
            'stop_loss_pct': 0.30,           # 30% stop loss
        }
    },
    'default': {
        'enabled': True,
        'description': 'Default Multi-Factor Strategy',
        'symbols': DEFAULT_WATCHLIST,
        'alert_threshold': 0.60,
        'parameters': {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'ma_short': 20,
            'ma_long': 50
        }
    },
    'momentum': {
        'enabled': True,
        'description': 'Momentum Strategy',
        'symbols': MOMENTUM_WATCHLIST,
        'alert_threshold': 0.60,
        'parameters': {
            'lookback_period': 20,
            'momentum_period': 10,
            'volume_factor': 1.5,
            'breakout_threshold': 0.02,
        }
    },
    'mean_reversion': {
        'enabled': True,
        'description': 'Mean Reversion Strategy',
        'symbols': MEAN_REVERSION_WATCHLIST,
        'alert_threshold': 0.65,
        'parameters': {
            'bb_period': 20,
            'bb_std': 2.0,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
        }
    }
}

# Timing configuration
TIMING_CONFIG = {
    'run_interval_minutes': 30,
    'market_open': '09:30',
    'market_close': '16:00',
    'timezone': 'America/New_York',
    'weekend_enabled': False,
    'holiday_enabled': False,
}

# Alert configuration
ALERT_CONFIG = {
    'telegram_enabled': True,
    'min_confidence_for_alert': 0.60,
    'max_alerts_per_hour': 10,
    'max_alerts_per_day': 30,
    'send_daily_summary': True,
    'include_market_regime': True,
}

# Risk configuration
RISK_CONFIG = {
    'max_concurrent_signals': 8,
    'max_daily_signals': 15,
    'max_portfolio_risk': 0.10,      # 10% max portfolio risk
    'daily_loss_limit': 0.05,        # Stop if daily loss > 5%
    'consecutive_loss_limit': 3,     # Stop after 3 losses
}

# Data configuration
DATA_CONFIG = {
    'default_period': '60d',
    'default_interval': '1d',
    'premarket_data': False,
    'cache_data': True,
    'cache_expiry_minutes': 30,
}

# Helper functions
def get_active_strategies() -> Dict[str, Any]:
    """Get all active strategies with their configurations"""
    return {name: config for name, config in STRATEGY_CONFIGS.items() 
            if config.get('enabled', True)}

def get_all_symbols() -> List[str]:
    """Get all unique symbols across all active strategies"""
    all_symbols = set()
    for strategy_name, config in get_active_strategies().items():
        all_symbols.update(config.get('symbols', []))
    return sorted(list(all_symbols))

def get_strategy_parameters(strategy_name: str) -> Dict[str, Any]:
    """Get parameters for a specific strategy"""
    if strategy_name in STRATEGY_CONFIGS:
        return STRATEGY_CONFIGS[strategy_name].get('parameters', {})
    return {}

def get_alert_threshold(strategy_name: str) -> float:
    """Get alert threshold for a specific strategy"""
    if strategy_name in STRATEGY_CONFIGS:
        return STRATEGY_CONFIGS[strategy_name].get('alert_threshold', 
                                                 ALERT_CONFIG['min_confidence_for_alert'])
    return ALERT_CONFIG['min_confidence_for_alert']

# Export constants for compatibility with both systems
RUN_INTERVAL_MINUTES = TIMING_CONFIG['run_interval_minutes']
MARKET_OPEN = TIMING_CONFIG['market_open']
MARKET_CLOSE = TIMING_CONFIG['market_close']
TIMEZONE = TIMING_CONFIG['timezone']
MAX_DAILY_SIGNALS = RISK_CONFIG['max_daily_signals']
MAX_SIGNALS_PER_STRATEGY = RISK_CONFIG['max_concurrent_signals']
