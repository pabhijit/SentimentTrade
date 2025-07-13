"""
Configuration for Daily Strategy Runner - ALL STRATEGIES
Comprehensive automation covering all SentimentTrade strategies:
- Enhanced Break & Retest Strategy
- Options Break & Retest Strategy  
- Default Strategy
- Mean Reversion Strategy
- Momentum Strategy
"""

from typing import Dict, List, Any

# =============================================================================
# WATCHLIST CONFIGURATION BY STRATEGY
# Optimized based on backtesting results and strategy characteristics
# =============================================================================

# Break & Retest Strategy Watchlist - Top performers from backtesting
BREAK_RETEST_WATCHLIST = [
    # Top performers from backtesting
    'AMD',    # 57.1% win rate - semiconductor leader
    'MSFT',   # 47.8% win rate - tech giant
    'BAC',    # 13.4% return - financial sector
    
    # Major tech stocks - good for breakouts
    'AAPL',   # Apple - high volume, clear levels
    'NVDA',   # NVIDIA - volatile, strong trends
    'GOOGL',  # Google - consistent patterns
    'AMZN',   # Amazon - e-commerce leader
    
    # Market ETFs - broad market exposure
    'SPY',    # S&P 500 - market benchmark
    'QQQ',    # NASDAQ 100 - tech-heavy
    
    # Financial sector - showed good performance
    'JPM',    # JPMorgan Chase
    'XLF',    # Financial sector ETF
]

# Options Strategy Watchlist - High liquidity for options
OPTIONS_WATCHLIST = [
    'QQQ',    # Primary focus - excellent options liquidity
    'SPY',    # Backup - also excellent liquidity
]

# Default Strategy Watchlist - Broad market coverage
DEFAULT_STRATEGY_WATCHLIST = [
    # Large cap tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    
    # Market leaders
    'TSLA', 'NVDA', 'AMD', 'NFLX', 'CRM',
    
    # ETFs for diversification
    'SPY', 'QQQ', 'IWM', 'VTI',
    
    # Financial sector
    'JPM', 'BAC', 'WFC', 'GS',
    
    # Healthcare
    'JNJ', 'PFE', 'UNH', 'ABBV',
]

# Mean Reversion Strategy Watchlist - Stocks that tend to revert to mean
MEAN_REVERSION_WATCHLIST = [
    # High volatility stocks good for mean reversion
    'TSLA',   # Tesla - high volatility, mean reversion opportunities
    'NVDA',   # NVIDIA - volatile, cyclical
    'AMD',    # AMD - semiconductor cycles
    'NFLX',   # Netflix - streaming cycles
    'ROKU',   # Roku - high volatility
    
    # ETFs with mean reversion characteristics
    'QQQ',    # Tech ETF - cyclical
    'XLF',    # Financial ETF - cyclical sector
    'XLE',    # Energy ETF - commodity cycles
    'GDX',    # Gold miners - commodity cycles
    
    # Biotech - high volatility sector
    'IBB',    # Biotech ETF
    'GILD',   # Gilead Sciences
    'BIIB',   # Biogen
]

# Momentum Strategy Watchlist - Trending stocks
MOMENTUM_WATCHLIST = [
    # Strong trending stocks
    'AAPL',   # Apple - consistent uptrends
    'MSFT',   # Microsoft - steady growth
    'GOOGL',  # Google - long-term trends
    'AMZN',   # Amazon - growth trends
    'META',   # Meta - recovery trends
    
    # Growth sectors
    'NVDA',   # AI/GPU growth
    'CRM',    # Cloud computing
    'ADBE',   # Software growth
    'NOW',    # ServiceNow - enterprise software
    
    # Momentum ETFs
    'MTUM',   # Momentum factor ETF
    'QQQ',    # Tech momentum
    'ARKK',   # Innovation momentum
    'SPYG',   # Growth momentum
    
    # Emerging trends
    'PLTR',   # Palantir - data analytics
    'SNOW',   # Snowflake - cloud data
]

# =============================================================================
# STRATEGY CONFIGURATIONS
# =============================================================================

STRATEGY_CONFIGS = {
    'enhanced_break_retest': {
        'enabled': True,
        'symbols': BREAK_RETEST_WATCHLIST,
        'description': 'Enhanced Break & Retest Strategy',
        'parameters': {
            'lookback_period': 20,
            'min_breakout_strength': 0.008,  # 0.8% from optimization
            'position_size': 0.03,           # 3% risk per trade
            'use_structure_stops': True,
            'use_adaptive_tp': True,
            'trade_cooldown_days': 2,
            'pattern_confirmation': True,
            'momentum_confirmation': True,
            # Market regime adaptation
            'regime_detection': True,
            'adaptive_confirmation': True,
            # Enhanced risk management
            'volatility_sizing': True,
            'max_portfolio_risk': 0.06,      # 6% max portfolio risk
            'drawdown_protection': True
        },
        'alert_threshold': 0.65,  # Send alerts for signals > 65% confidence
        'priority': 1
    },
    
    'options_break_retest': {
        'enabled': True,
        'symbols': OPTIONS_WATCHLIST,
        'description': 'Options Break & Retest Strategy',
        'parameters': {
            'target_delta_range': (0.6, 0.8),    # ITM options
            'days_to_expiry_range': (30, 90),    # 1-3 months
            'min_option_price': 1.0,             # Minimum $1 option price
            'profit_target_pct': 0.5,            # 50% profit target
            'stop_loss_pct': 0.3,                # 30% stop loss
            'max_trades_per_day': 2,             # Limit options trades
        },
        'alert_threshold': 0.70,  # Higher threshold for options
        'priority': 2
    }
}

# =============================================================================
# TIMING CONFIGURATION
# =============================================================================

TIMING_CONFIG = {
    # Market hours (Eastern Time)
    'market_open': 9.5,   # 9:30 AM ET
    'market_close': 16.0, # 4:00 PM ET
    
    # Strategy run frequency
    'run_interval_minutes': 30,  # Run every 30 minutes
    
    # Daily summary time
    'daily_summary_time': "16:30",  # 4:30 PM ET (after market close)
    
    # Rate limiting
    'delay_between_symbols': 2,  # 2 seconds between symbol analysis
    'delay_between_strategies': 5,  # 5 seconds between different strategies
}

# =============================================================================
# ALERT CONFIGURATION
# =============================================================================

ALERT_CONFIG = {
    # Telegram settings
    'telegram_enabled': True,
    'send_startup_alert': True,
    'send_shutdown_alert': True,
    'send_error_alerts': True,
    'send_daily_summary': True,
    
    # Alert thresholds
    'min_confidence_for_alert': 0.60,  # 60% minimum confidence
    'max_alerts_per_hour': 10,         # Rate limit alerts
    
    # Alert formatting
    'include_chart_analysis': True,
    'include_risk_metrics': True,
    'include_market_regime': True,
    
    # Error handling
    'max_consecutive_errors': 5,       # Stop after 5 consecutive errors
    'error_cooldown_minutes': 15,      # Wait 15 minutes after errors
}

# =============================================================================
# DATA CONFIGURATION
# =============================================================================

DATA_CONFIG = {
    # Historical data settings
    'lookback_days': 60,              # Days of historical data to fetch
    'data_source': 'yfinance',        # Primary data source
    'backup_data_source': 'twelvedata', # Backup if primary fails
    
    # Data quality checks
    'min_data_points': 30,            # Minimum data points required
    'max_missing_days': 5,            # Maximum missing days allowed
    
    # Caching
    'cache_data': True,               # Cache data to reduce API calls
    'cache_duration_minutes': 15,     # Cache for 15 minutes
}

# =============================================================================
# RISK MANAGEMENT
# =============================================================================

RISK_CONFIG = {
    # Portfolio limits
    'max_concurrent_signals': 8,      # Maximum active signals
    'max_daily_signals': 15,          # Maximum signals per day
    'max_signals_per_symbol': 1,      # One signal per symbol at a time
    
    # Risk thresholds
    'max_portfolio_risk': 0.10,       # 10% maximum portfolio risk
    'max_single_position_risk': 0.03, # 3% maximum single position risk
    
    # Stop conditions
    'daily_loss_limit': 0.05,         # Stop if daily loss > 5%
    'consecutive_loss_limit': 3,      # Stop after 3 consecutive losses
    
    # Market conditions
    'volatility_threshold': 0.30,     # Reduce position size if VIX > 30
    'market_stress_indicators': ['VIX', 'DXY', 'TNX'],  # Monitor these for market stress
}

# =============================================================================
# LOGGING AND MONITORING
# =============================================================================

LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_to_file': True,
    'log_file_path': 'logs/daily_runner.log',
    'max_log_file_size_mb': 50,
    'backup_log_files': 5,
    
    # Performance monitoring
    'track_execution_time': True,
    'track_api_calls': True,
    'track_memory_usage': True,
    
    # Results storage
    'save_all_results': True,
    'results_retention_days': 90,     # Keep results for 90 days
    'compress_old_results': True,
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_active_strategies() -> Dict[str, Any]:
    """Get only enabled strategies"""
    return {name: config for name, config in STRATEGY_CONFIGS.items() 
            if config.get('enabled', True)}

def get_all_symbols() -> List[str]:
    """Get all unique symbols across all strategies"""
    all_symbols = set()
    for config in get_active_strategies().values():
        all_symbols.update(config['symbols'])
    return sorted(list(all_symbols))

def get_high_priority_symbols() -> List[str]:
    """Get symbols from high-priority strategies"""
    high_priority = []
    for config in get_active_strategies().values():
        if config.get('priority', 999) <= 2:
            high_priority.extend(config['symbols'])
    return list(set(high_priority))

def validate_config() -> List[str]:
    """Validate configuration and return any issues"""
    issues = []
    
    # Check if we have symbols
    if not get_all_symbols():
        issues.append("No symbols configured for any strategy")
    
    # Check timing
    if TIMING_CONFIG['market_open'] >= TIMING_CONFIG['market_close']:
        issues.append("Market open time must be before market close time")
    
    # Check risk limits
    if RISK_CONFIG['max_single_position_risk'] > RISK_CONFIG['max_portfolio_risk']:
        issues.append("Single position risk cannot exceed portfolio risk")
    
    return issues

# =============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# =============================================================================

# You can override any settings based on environment
import os

# Development environment - more conservative settings
if os.getenv('ENVIRONMENT') == 'development':
    ALERT_CONFIG['max_alerts_per_hour'] = 5
    RISK_CONFIG['max_daily_signals'] = 8
    TIMING_CONFIG['run_interval_minutes'] = 60  # Less frequent in dev

# Production environment - full settings
elif os.getenv('ENVIRONMENT') == 'production':
    # Use default settings
    pass

# Paper trading environment
elif os.getenv('ENVIRONMENT') == 'paper':
    ALERT_CONFIG['telegram_enabled'] = False  # No alerts for paper trading
    RISK_CONFIG['max_daily_signals'] = 20     # More signals for testing
