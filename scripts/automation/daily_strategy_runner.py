#!/usr/bin/env python3
"""
Daily Strategy Runner - SentimentTrade Automation
Runs all strategies on specified stocks every 30 minutes during market hours
Sends alerts to Telegram for actionable signals

Based on backtesting results:
- Break & Retest: Best on AMD (57.1% win rate), MSFT (47.8% win rate)
- Options Strategy: Runs on QQQ for mechanical options trading
- All strategies: Comprehensive coverage across watchlist
"""

import os
import sys
import time
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Import our modules
from config import config
from logger import logger
from telegram_alerts import TelegramNotifier, send_bot_status, send_error_alert
from strategies.break_retest_strategy import BreakRetestSwingStrategy
from strategies.options_break_retest_strategy import OptionsBreakRetestStrategy
from data.data_downloader import download_stock_data
import yfinance as yf

class DailyStrategyRunner:
    """
    Automated strategy runner that executes all strategies on watchlist stocks
    every 30 minutes during market hours and sends Telegram alerts
    """
    
    def __init__(self):
        """Initialize the daily strategy runner"""
        self.telegram = TelegramNotifier()
        self.is_running = False
        self.last_run_time = None
        self.daily_signals = []
        self.run_count = 0
        
        # Import strategy configurations
        from runner_config import get_active_strategies, get_strategy_summary
        
        self.strategies_config = get_active_strategies()
        self.strategy_summary = get_strategy_summary()
        
        # Strategy class mapping
        self.strategy_classes = {
            'enhanced_break_retest': 'BreakRetestSwingStrategy',
            'options_break_retest': 'OptionsBreakRetestStrategy', 
            'default_strategy': 'DefaultStrategy',
            'mean_reversion': 'MeanReversionStrategy',
            'momentum': 'MomentumStrategy'
        }
        
        # Market hours (Eastern Time)
        self.market_open = 9.5  # 9:30 AM
        self.market_close = 16.0  # 4:00 PM
        
        # Results storage
        self.results_dir = project_root / 'results' / 'daily_runs'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 Daily Strategy Runner initialized - ALL STRATEGIES")
        logger.info(f"📊 Active Strategies: {list(self.strategies_config.keys())}")
        logger.info(f"📈 Total symbols: {self.strategy_summary['total_symbols']}")
        logger.info(f"🎯 Strategy breakdown:")
        for name, info in self.strategy_summary['strategies'].items():
            logger.info(f"   • {info['description']}: {info['symbol_count']} symbols")
        logger.info(f"⚠️ Max daily signals: {self.strategy_summary['risk_limits']['max_daily_signals']}")
    
    def is_market_hours(self) -> bool:
        """Check if current time is during market hours (Eastern Time)"""
        try:
            from datetime import datetime
            import pytz
            
            # Get current Eastern Time
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
            
            # Check if it's a weekday
            if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Check if it's during market hours
            current_hour = now_et.hour + now_et.minute / 60.0
            return self.market_open <= current_hour <= self.market_close
            
        except Exception as e:
            logger.warning(f"Could not determine market hours: {e}")
            # Default to running during typical hours
            now = datetime.now()
            if now.weekday() >= 5:
                return False
            current_hour = now.hour + now.minute / 60.0
            return 9.5 <= current_hour <= 16.0
    
    def get_latest_data(self, symbol: str, period: str = '60d') -> Optional[pd.DataFrame]:
        """Get latest market data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
            
            logger.info(f"✅ Retrieved {len(data)} days of data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to get data for {symbol}: {e}")
            return None
    
    def run_strategy(self, strategy_name: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Run a specific strategy on a symbol"""
        try:
            strategy_config = self.strategies_config[strategy_name]
            
            # Get latest market data
            data = self.get_latest_data(symbol)
            if data is None:
                return None
            
            # Initialize strategy based on type
            strategy = self.initialize_strategy(strategy_name, strategy_config)
            if strategy is None:
                return None
            
            # Run strategy analysis
            current_price = data['Close'].iloc[-1]
            
            # Generate signal based on strategy type
            signal_data = self.generate_signal_for_strategy(
                strategy, strategy_name, symbol, data, current_price
            )
            
            if signal_data and signal_data.get('action') != 'HOLD':
                logger.info(f"🎯 {strategy_name} signal for {symbol}: {signal_data['action']} "
                           f"at ${current_price:.2f} (confidence: {signal_data['confidence']:.1%})")
            
            return signal_data
            
        except Exception as e:
            logger.error(f"Error running {strategy_name} on {symbol}: {e}")
            return None
    
    def initialize_strategy(self, strategy_name: str, config: Dict[str, Any]):
        """Initialize strategy based on strategy name"""
        try:
            params = config.get('parameters', {})
            
            if strategy_name == 'enhanced_break_retest':
                from strategies.break_retest_strategy import BreakRetestSwingStrategy
                return BreakRetestSwingStrategy(
                    lookback_period=params.get('lookback_period', 20),
                    min_breakout_strength=params.get('min_breakout_strength', 0.008),
                    position_size=params.get('position_size', 0.03),
                    use_structure_stops=params.get('use_structure_stops', True),
                    use_adaptive_tp=params.get('use_adaptive_tp', True),
                    trade_cooldown_days=params.get('trade_cooldown_days', 2),
                    pattern_confirmation=params.get('pattern_confirmation', True),
                    momentum_confirmation=params.get('momentum_confirmation', True)
                )
            
            elif strategy_name == 'options_break_retest':
                from strategies.options_break_retest_strategy import OptionsBreakRetestStrategy
                from strategies.break_retest_strategy import BreakRetestSwingStrategy
                base_strategy = BreakRetestSwingStrategy()
                return OptionsBreakRetestStrategy(
                    base_strategy=base_strategy,
                    target_delta_range=params.get('target_delta_range', (0.6, 0.8)),
                    days_to_expiry_range=params.get('days_to_expiry_range', (30, 90)),
                    min_option_price=params.get('min_option_price', 1.0),
                    profit_target_pct=params.get('profit_target_pct', 0.5),
                    stop_loss_pct=params.get('stop_loss_pct', 0.3)
                )
            
            elif strategy_name == 'default_strategy':
                return self.create_default_strategy(params)
            
            elif strategy_name == 'mean_reversion':
                return self.create_mean_reversion_strategy(params)
            
            elif strategy_name == 'momentum':
                return self.create_momentum_strategy(params)
            
            else:
                logger.error(f"Unknown strategy: {strategy_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize {strategy_name}: {e}")
            return None
    
    def create_default_strategy(self, params: Dict[str, Any]):
        """Create default strategy with technical and sentiment analysis"""
        class DefaultStrategy:
            def __init__(self, **kwargs):
                self.lookback_period = kwargs.get('lookback_period', 20)
                self.rsi_period = kwargs.get('rsi_period', 14)
                self.rsi_oversold = kwargs.get('rsi_oversold', 30)
                self.rsi_overbought = kwargs.get('rsi_overbought', 70)
                self.ma_short = kwargs.get('ma_short', 10)
                self.ma_long = kwargs.get('ma_long', 20)
                self.volume_threshold = kwargs.get('volume_threshold', 1.2)
                self.min_price_change = kwargs.get('min_price_change', 0.02)
                self.sentiment_weight = kwargs.get('sentiment_weight', 0.3)
                self.technical_weight = kwargs.get('technical_weight', 0.7)
            
            def analyze(self, data):
                """Analyze data and return signal"""
                try:
                    # Calculate technical indicators
                    data['RSI'] = self.calculate_rsi(data['Close'], self.rsi_period)
                    data['MA_Short'] = data['Close'].rolling(self.ma_short).mean()
                    data['MA_Long'] = data['Close'].rolling(self.ma_long).mean()
                    data['Volume_MA'] = data['Volume'].rolling(20).mean()
                    
                    current = data.iloc[-1]
                    prev = data.iloc[-2]
                    
                    # Technical score
                    technical_score = 0
                    
                    # RSI signals
                    if current['RSI'] < self.rsi_oversold:
                        technical_score += 0.3  # Oversold - bullish
                    elif current['RSI'] > self.rsi_overbought:
                        technical_score -= 0.3  # Overbought - bearish
                    
                    # Moving average signals
                    if current['MA_Short'] > current['MA_Long']:
                        technical_score += 0.2  # Uptrend
                    else:
                        technical_score -= 0.2  # Downtrend
                    
                    # Volume confirmation
                    if current['Volume'] > current['Volume_MA'] * self.volume_threshold:
                        technical_score += 0.1  # High volume
                    
                    # Price momentum
                    price_change = (current['Close'] - prev['Close']) / prev['Close']
                    if abs(price_change) > self.min_price_change:
                        technical_score += 0.2 if price_change > 0 else -0.2
                    
                    # Determine action
                    if technical_score > 0.3:
                        action = 'BUY'
                        confidence = min(0.8, 0.5 + technical_score)
                    elif technical_score < -0.3:
                        action = 'SELL'
                        confidence = min(0.8, 0.5 + abs(technical_score))
                    else:
                        action = 'HOLD'
                        confidence = 0.3
                    
                    return {
                        'action': action,
                        'confidence': confidence,
                        'technical_score': technical_score,
                        'rsi': current['RSI'],
                        'ma_signal': 'bullish' if current['MA_Short'] > current['MA_Long'] else 'bearish'
                    }
                    
                except Exception as e:
                    logger.error(f"Default strategy analysis error: {e}")
                    return {'action': 'HOLD', 'confidence': 0.0}
            
            def calculate_rsi(self, prices, period=14):
                """Calculate RSI"""
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                return 100 - (100 / (1 + rs))
        
        return DefaultStrategy(**params)
    
    def create_mean_reversion_strategy(self, params: Dict[str, Any]):
        """Create mean reversion strategy"""
        class MeanReversionStrategy:
            def __init__(self, **kwargs):
                self.lookback_period = kwargs.get('lookback_period', 20)
                self.bollinger_period = kwargs.get('bollinger_period', 20)
                self.bollinger_std = kwargs.get('bollinger_std', 2.0)
                self.rsi_period = kwargs.get('rsi_period', 14)
                self.rsi_oversold = kwargs.get('rsi_oversold', 25)
                self.rsi_overbought = kwargs.get('rsi_overbought', 75)
                self.volume_confirmation = kwargs.get('volume_confirmation', True)
                self.min_volume_ratio = kwargs.get('min_volume_ratio', 1.5)
                self.max_trend_strength = kwargs.get('max_trend_strength', 0.3)
                self.reversion_target = kwargs.get('reversion_target', 0.5)
            
            def analyze(self, data):
                """Analyze for mean reversion opportunities"""
                try:
                    # Calculate indicators
                    data['RSI'] = self.calculate_rsi(data['Close'], self.rsi_period)
                    data['BB_Middle'] = data['Close'].rolling(self.bollinger_period).mean()
                    bb_std = data['Close'].rolling(self.bollinger_period).std()
                    data['BB_Upper'] = data['BB_Middle'] + (bb_std * self.bollinger_std)
                    data['BB_Lower'] = data['BB_Middle'] - (bb_std * self.bollinger_std)
                    data['Volume_MA'] = data['Volume'].rolling(20).mean()
                    
                    current = data.iloc[-1]
                    
                    # Check for mean reversion setup
                    reversion_score = 0
                    
                    # Bollinger Band signals
                    if current['Close'] <= current['BB_Lower']:
                        reversion_score += 0.4  # Oversold
                    elif current['Close'] >= current['BB_Upper']:
                        reversion_score -= 0.4  # Overbought
                    
                    # RSI confirmation
                    if current['RSI'] <= self.rsi_oversold:
                        reversion_score += 0.3
                    elif current['RSI'] >= self.rsi_overbought:
                        reversion_score -= 0.3
                    
                    # Volume confirmation
                    if self.volume_confirmation:
                        if current['Volume'] > current['Volume_MA'] * self.min_volume_ratio:
                            reversion_score += 0.1
                    
                    # Avoid strong trends
                    trend_strength = abs(current['Close'] - current['BB_Middle']) / current['BB_Middle']
                    if trend_strength > self.max_trend_strength:
                        reversion_score *= 0.5  # Reduce signal strength in strong trends
                    
                    # Determine action
                    if reversion_score > 0.4:
                        action = 'BUY'
                        confidence = min(0.8, 0.5 + reversion_score)
                    elif reversion_score < -0.4:
                        action = 'SELL'
                        confidence = min(0.8, 0.5 + abs(reversion_score))
                    else:
                        action = 'HOLD'
                        confidence = 0.3
                    
                    return {
                        'action': action,
                        'confidence': confidence,
                        'reversion_score': reversion_score,
                        'bb_position': (current['Close'] - current['BB_Lower']) / (current['BB_Upper'] - current['BB_Lower']),
                        'rsi': current['RSI']
                    }
                    
                except Exception as e:
                    logger.error(f"Mean reversion strategy analysis error: {e}")
                    return {'action': 'HOLD', 'confidence': 0.0}
            
            def calculate_rsi(self, prices, period=14):
                """Calculate RSI"""
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                return 100 - (100 / (1 + rs))
        
        return MeanReversionStrategy(**params)
    
    def create_momentum_strategy(self, params: Dict[str, Any]):
        """Create momentum strategy"""
        class MomentumStrategy:
            def __init__(self, **kwargs):
                self.lookback_period = kwargs.get('lookback_period', 20)
                self.momentum_period = kwargs.get('momentum_period', 10)
                self.min_momentum_threshold = kwargs.get('min_momentum_threshold', 0.05)
                self.rsi_period = kwargs.get('rsi_period', 14)
                self.rsi_momentum_min = kwargs.get('rsi_momentum_min', 55)
                self.rsi_momentum_max = kwargs.get('rsi_momentum_max', 45)
                self.volume_confirmation = kwargs.get('volume_confirmation', True)
                self.min_volume_ratio = kwargs.get('min_volume_ratio', 1.3)
                self.trend_confirmation = kwargs.get('trend_confirmation', True)
                self.ma_periods = kwargs.get('ma_periods', [10, 20, 50])
                self.breakout_confirmation = kwargs.get('breakout_confirmation', True)
            
            def analyze(self, data):
                """Analyze for momentum opportunities"""
                try:
                    # Calculate indicators
                    data['RSI'] = self.calculate_rsi(data['Close'], self.rsi_period)
                    data['Volume_MA'] = data['Volume'].rolling(20).mean()
                    
                    # Calculate momentum
                    data['Momentum'] = data['Close'].pct_change(self.momentum_period)
                    
                    # Calculate moving averages
                    for period in self.ma_periods:
                        data[f'MA_{period}'] = data['Close'].rolling(period).mean()
                    
                    current = data.iloc[-1]
                    
                    # Momentum score
                    momentum_score = 0
                    
                    # Price momentum
                    if abs(current['Momentum']) > self.min_momentum_threshold:
                        momentum_score += 0.3 if current['Momentum'] > 0 else -0.3
                    
                    # RSI momentum
                    if current['RSI'] > self.rsi_momentum_min:
                        momentum_score += 0.2
                    elif current['RSI'] < self.rsi_momentum_max:
                        momentum_score -= 0.2
                    
                    # Trend confirmation
                    if self.trend_confirmation:
                        ma_alignment = 0
                        for i in range(len(self.ma_periods) - 1):
                            ma1 = current[f'MA_{self.ma_periods[i]}']
                            ma2 = current[f'MA_{self.ma_periods[i+1]}']
                            if ma1 > ma2:
                                ma_alignment += 1
                            else:
                                ma_alignment -= 1
                        
                        momentum_score += 0.2 * (ma_alignment / (len(self.ma_periods) - 1))
                    
                    # Volume confirmation
                    if self.volume_confirmation:
                        if current['Volume'] > current['Volume_MA'] * self.min_volume_ratio:
                            momentum_score += 0.1
                    
                    # Breakout confirmation
                    if self.breakout_confirmation:
                        high_20 = data['High'].rolling(20).max().iloc[-2]  # Previous 20-day high
                        low_20 = data['Low'].rolling(20).min().iloc[-2]    # Previous 20-day low
                        
                        if current['Close'] > high_20:
                            momentum_score += 0.2  # Breakout above resistance
                        elif current['Close'] < low_20:
                            momentum_score -= 0.2  # Breakdown below support
                    
                    # Determine action
                    if momentum_score > 0.4:
                        action = 'BUY'
                        confidence = min(0.8, 0.5 + momentum_score)
                    elif momentum_score < -0.4:
                        action = 'SELL'
                        confidence = min(0.8, 0.5 + abs(momentum_score))
                    else:
                        action = 'HOLD'
                        confidence = 0.3
                    
                    return {
                        'action': action,
                        'confidence': confidence,
                        'momentum_score': momentum_score,
                        'momentum': current['Momentum'],
                        'rsi': current['RSI']
                    }
                    
                except Exception as e:
                    logger.error(f"Momentum strategy analysis error: {e}")
                    return {'action': 'HOLD', 'confidence': 0.0}
            
            def calculate_rsi(self, prices, period=14):
                """Calculate RSI"""
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                return 100 - (100 / (1 + rs))
        
        return MomentumStrategy(**params)
    
    def generate_signal_for_strategy(self, strategy, strategy_name: str, symbol: str, 
                                   data: pd.DataFrame, current_price: float) -> Dict[str, Any]:
        """Generate signal data for any strategy type"""
        try:
            # Run strategy analysis
            if hasattr(strategy, 'check_breakout_setup'):
                # Break & Retest strategies
                setup_result = strategy.check_breakout_setup(data)
                
                if setup_result and setup_result.get('has_setup'):
                    return {
                        'symbol': symbol,
                        'strategy': strategy_name,
                        'action': setup_result.get('direction', 'HOLD').upper(),
                        'current_price': current_price,
                        'entry_price': setup_result.get('entry_price', current_price),
                        'stop_loss': setup_result.get('stop_loss', current_price * 0.95),
                        'target_price': setup_result.get('target_price', current_price * 1.05),
                        'confidence': setup_result.get('confidence', 0.5),
                        'reasoning': setup_result.get('reasoning', f'{strategy_name} setup detected'),
                        'timestamp': datetime.now().isoformat(),
                        'market_regime': setup_result.get('market_regime', 'unknown')
                    }
            
            elif hasattr(strategy, 'analyze'):
                # Other strategies (default, mean reversion, momentum)
                analysis_result = strategy.analyze(data)
                
                if analysis_result:
                    # Calculate stop loss and target based on action
                    if analysis_result['action'] == 'BUY':
                        stop_loss = current_price * 0.95  # 5% stop loss
                        target_price = current_price * 1.08  # 8% target
                    elif analysis_result['action'] == 'SELL':
                        stop_loss = current_price * 1.05  # 5% stop loss (short)
                        target_price = current_price * 0.92  # 8% target (short)
                    else:
                        stop_loss = current_price
                        target_price = current_price
                    
                    return {
                        'symbol': symbol,
                        'strategy': strategy_name,
                        'action': analysis_result['action'],
                        'current_price': current_price,
                        'entry_price': current_price,
                        'stop_loss': stop_loss,
                        'target_price': target_price,
                        'confidence': analysis_result['confidence'],
                        'reasoning': f"{strategy_name} signal: {analysis_result.get('technical_score', analysis_result.get('momentum_score', analysis_result.get('reversion_score', 'N/A')))}",
                        'timestamp': datetime.now().isoformat(),
                        'analysis_details': analysis_result
                    }
            
            # No signal generated
            return {
                'symbol': symbol,
                'strategy': strategy_name,
                'action': 'HOLD',
                'current_price': current_price,
                'confidence': 0.0,
                'reasoning': 'No setup detected',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating signal for {strategy_name}: {e}")
            return {
                'symbol': symbol,
                'strategy': strategy_name,
                'action': 'HOLD',
                'current_price': current_price,
                'confidence': 0.0,
                'reasoning': f'Analysis error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def run_all_strategies(self) -> List[Dict[str, Any]]:
        """Run all strategies on their respective symbols"""
        if not self.is_market_hours():
            logger.info("⏰ Outside market hours - skipping strategy run")
            return []
        
        logger.info("🔄 Starting comprehensive strategy run...")
        all_signals = []
        strategy_counts = {}
        
        # Import configuration
        from runner_config import RISK_CONFIG, get_strategy_alert_threshold
        
        for strategy_name, config in self.strategies_config.items():
            if not config.get('enabled', True):
                logger.info(f"⏭️ Skipping disabled strategy: {strategy_name}")
                continue
                
            logger.info(f"📊 Running {config['description']}...")
            strategy_signals = []
            
            for symbol in config['symbols']:
                try:
                    # Check daily limits
                    if len(all_signals) >= RISK_CONFIG.get('max_daily_signals', 25):
                        logger.info(f"🛑 Reached daily signal limit: {RISK_CONFIG['max_daily_signals']}")
                        break
                    
                    # Check strategy limits
                    strategy_count = strategy_counts.get(strategy_name, 0)
                    if strategy_count >= RISK_CONFIG.get('max_signals_per_strategy', 8):
                        logger.info(f"🛑 Reached strategy limit for {strategy_name}: {RISK_CONFIG['max_signals_per_strategy']}")
                        break
                    
                    # Run strategy
                    signal = self.run_strategy(strategy_name, symbol)
                    if signal:
                        all_signals.append(signal)
                        strategy_signals.append(signal)
                        
                        # Update strategy count
                        if signal['action'] != 'HOLD':
                            strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1
                        
                        # Send Telegram alert for actionable signals
                        alert_threshold = get_strategy_alert_threshold(strategy_name)
                        if (signal['action'] != 'HOLD' and 
                            signal['confidence'] >= alert_threshold):
                            self.send_signal_alert(signal)
                    
                    # Rate limiting between symbols
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Failed to run {strategy_name} on {symbol}: {e}")
                    continue
            
            # Log strategy results
            actionable_strategy_signals = [s for s in strategy_signals if s['action'] != 'HOLD']
            logger.info(f"✅ {strategy_name}: {len(strategy_signals)} total, "
                       f"{len(actionable_strategy_signals)} actionable signals")
            
            # Rate limiting between strategies
            time.sleep(3)
        
        # Save results
        self.save_run_results(all_signals)
        
        # Update counters
        self.run_count += 1
        self.last_run_time = datetime.now()
        self.daily_signals.extend(all_signals)
        
        # Summary
        actionable_signals = [s for s in all_signals if s['action'] != 'HOLD']
        strategy_breakdown = {}
        for signal in actionable_signals:
            strategy = signal['strategy']
            strategy_breakdown[strategy] = strategy_breakdown.get(strategy, 0) + 1
        
        logger.info(f"✅ Strategy run completed: {len(all_signals)} total signals, "
                   f"{len(actionable_signals)} actionable")
        
        if strategy_breakdown:
            logger.info("📊 Actionable signals by strategy:")
            for strategy, count in strategy_breakdown.items():
                logger.info(f"   • {strategy}: {count} signals")
        
        return all_signals
    
    def send_signal_alert(self, signal: Dict[str, Any]):
        """Send Telegram alert for actionable signals with strategy-specific formatting"""
        try:
            from runner_config import get_strategy_alert_threshold
            
            # Check if signal meets strategy-specific threshold
            strategy_threshold = get_strategy_alert_threshold(signal['strategy'])
            if signal['confidence'] < strategy_threshold:
                return
            
            # Format signal for Telegram
            telegram_signal = {
                'symbol': signal['symbol'],
                'recommendation': signal['action'],
                'current_price': signal['current_price'],
                'entry_price': signal.get('entry_price', signal['current_price']),
                'stop_loss': signal.get('stop_loss', 0),
                'target_price': signal.get('target_price', 0),
                'confidence': signal['confidence']
            }
            
            # Enhanced message with strategy-specific info
            strategy_info = f"\n🔧 <b>Strategy:</b> {signal['strategy'].replace('_', ' ').title()}"
            
            # Add strategy-specific details
            if 'market_regime' in signal:
                strategy_info += f"\n📊 <b>Market Regime:</b> {signal['market_regime']}"
            
            if 'analysis_details' in signal:
                details = signal['analysis_details']
                if 'rsi' in details:
                    strategy_info += f"\n📈 <b>RSI:</b> {details['rsi']:.1f}"
                if 'momentum' in details:
                    strategy_info += f"\n🚀 <b>Momentum:</b> {details['momentum']:.1%}"
                if 'bb_position' in details:
                    strategy_info += f"\n📊 <b>BB Position:</b> {details['bb_position']:.1%}"
            
            # Add reasoning
            if signal.get('reasoning'):
                strategy_info += f"\n💭 <b>Reasoning:</b> {signal['reasoning'][:100]}..."
            
            # Create custom message
            emoji = "🟢" if signal['action'] == 'BUY' else "🔴" if signal['action'] == 'SELL' else "🟡"
            action_text = f"{signal['action']} SIGNAL"
            
            custom_message = f"""
{emoji} <b>{action_text}</b> {emoji}

📊 <b>Symbol:</b> {signal['symbol']}
💰 <b>Current Price:</b> ${signal['current_price']:.2f}
🎯 <b>Entry Price:</b> ${telegram_signal['entry_price']:.2f}
🛑 <b>Stop Loss:</b> ${telegram_signal['stop_loss']:.2f}
🚀 <b>Target:</b> ${telegram_signal['target_price']:.2f}
📈 <b>Confidence:</b> {signal['confidence']:.1%}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{strategy_info}

<i>SentimentTrade Multi-Strategy Bot</i>
            """.strip()
            
            # Send custom message
            success = self.telegram.send_message_sync(custom_message)
            
            if success:
                logger.info(f"📱 Telegram alert sent for {signal['symbol']} {signal['action']} ({signal['strategy']})")
            else:
                logger.warning(f"Failed to send Telegram alert for {signal['symbol']}")
                
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
    
    def save_run_results(self, signals: List[Dict[str, Any]]):
        """Save strategy run results to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.results_dir / f'strategy_run_{timestamp}.json'
            
            run_data = {
                'timestamp': datetime.now().isoformat(),
                'run_count': self.run_count,
                'total_signals': len(signals),
                'actionable_signals': len([s for s in signals if s['action'] != 'HOLD']),
                'signals': signals
            }
            
            with open(filename, 'w') as f:
                json.dump(run_data, f, indent=2, default=str)
            
            logger.info(f"💾 Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def send_daily_summary(self):
        """Send comprehensive daily summary via Telegram"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Count today's signals
            total_runs = self.run_count
            total_signals = len(self.daily_signals)
            actionable_signals = len([s for s in self.daily_signals if s['action'] != 'HOLD'])
            
            # Strategy breakdown
            strategy_counts = {}
            strategy_actionable = {}
            for signal in self.daily_signals:
                strategy = signal.get('strategy', 'unknown')
                if strategy not in strategy_counts:
                    strategy_counts[strategy] = 0
                    strategy_actionable[strategy] = 0
                strategy_counts[strategy] += 1
                if signal['action'] != 'HOLD':
                    strategy_actionable[strategy] += 1
            
            # Action breakdown
            buy_signals = len([s for s in self.daily_signals if s['action'] == 'BUY'])
            sell_signals = len([s for s in self.daily_signals if s['action'] == 'SELL'])
            hold_signals = len([s for s in self.daily_signals if s['action'] == 'HOLD'])
            
            # Average confidence
            actionable_confidences = [s['confidence'] for s in self.daily_signals if s['action'] != 'HOLD']
            avg_confidence = sum(actionable_confidences) / len(actionable_confidences) if actionable_confidences else 0
            
            # Create comprehensive summary message
            summary_message = f"""
📊 <b>DAILY MULTI-STRATEGY SUMMARY</b> 📊

📅 <b>Date:</b> {today}
🔄 <b>Strategy Runs:</b> {total_runs}
📈 <b>Total Signals:</b> {total_signals}
🎯 <b>Actionable Signals:</b> {actionable_signals}

<b>📊 SIGNAL BREAKDOWN:</b>
🟢 Buy Signals: {buy_signals}
🔴 Sell Signals: {sell_signals}
🟡 Hold Signals: {hold_signals}
📈 Avg Confidence: {avg_confidence:.1%}

<b>🔧 STRATEGY PERFORMANCE:</b>
            """.strip()
            
            # Add strategy breakdown
            for strategy, total in strategy_counts.items():
                actionable = strategy_actionable.get(strategy, 0)
                strategy_name = strategy.replace('_', ' ').title()
                summary_message += f"\n• {strategy_name}: {actionable}/{total}"
            
            # Add footer
            summary_message += f"""

⏰ <b>Next Run:</b> Every 30 minutes during market hours
🤖 <b>Status:</b> {'Active' if self.is_running else 'Stopped'}

<i>SentimentTrade Multi-Strategy Bot</i>
            """
            
            # Send summary
            success = self.telegram.send_message_sync(summary_message)
            
            if success:
                logger.info(f"📊 Daily summary sent: {total_runs} runs, {actionable_signals} actionable signals")
                logger.info(f"📈 Strategy breakdown: {dict(strategy_actionable)}")
            
            # Reset daily counters
            self.daily_signals = []
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
    
    def start_scheduler(self):
        """Start the scheduled strategy runs"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("🚀 Starting Daily Strategy Runner scheduler...")
        
        # Schedule strategy runs every 30 minutes during market hours
        schedule.every(30).minutes.do(self.run_all_strategies)
        
        # Schedule daily summary at market close
        schedule.every().day.at("16:30").do(self.send_daily_summary)
        
        # Send startup notification
        send_bot_status("STARTED", "Daily Strategy Runner is now active - running every 30 minutes during market hours")
        
        self.is_running = True
        
        # Run scheduler in separate thread
        def run_scheduler():
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    send_error_alert(f"Scheduler error: {str(e)}", "Daily Strategy Runner")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Scheduler started successfully")
        
        # Run initial check if market is open
        if self.is_market_hours():
            logger.info("🎯 Market is open - running initial strategy check...")
            self.run_all_strategies()
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("🛑 Stopping Daily Strategy Runner...")
        
        self.is_running = False
        schedule.clear()
        
        # Send shutdown notification
        send_bot_status("STOPPED", f"Daily Strategy Runner stopped after {self.run_count} runs")
        
        logger.info("✅ Scheduler stopped successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive runner status"""
        from runner_config import get_strategy_summary
        
        strategy_summary = get_strategy_summary()
        
        return {
            'is_running': self.is_running,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'run_count': self.run_count,
            'daily_signals_count': len(self.daily_signals),
            'market_hours': self.is_market_hours(),
            'total_strategies': strategy_summary['total_strategies'],
            'active_strategies': list(self.strategies_config.keys()),
            'total_symbols': strategy_summary['total_symbols'],
            'strategy_details': strategy_summary['strategies'],
            'risk_limits': strategy_summary['risk_limits'],
            'recent_signals': [
                {
                    'symbol': s['symbol'],
                    'strategy': s['strategy'],
                    'action': s['action'],
                    'confidence': s['confidence'],
                    'timestamp': s['timestamp']
                }
                for s in self.daily_signals[-10:] if s['action'] != 'HOLD'
            ]
        }

def main():
    """Main function to run the daily strategy runner"""
    try:
        # Initialize runner
        runner = DailyStrategyRunner()
        
        # Test Telegram connection
        if runner.telegram.test_connection_sync():
            logger.info("✅ Telegram connection successful")
        else:
            logger.warning("⚠️ Telegram connection failed - alerts will be disabled")
        
        # Start scheduler
        runner.start_scheduler()
        
        # Keep running
        logger.info("🔄 Daily Strategy Runner is active. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(10)
                
                # Print status every 10 minutes
                if runner.run_count > 0 and runner.run_count % 20 == 0:
                    status = runner.get_status()
                    logger.info(f"📊 Status: {status['run_count']} runs completed, "
                               f"market_hours={status['market_hours']}")
        
        except KeyboardInterrupt:
            logger.info("👋 Shutdown requested by user")
        
        finally:
            runner.stop_scheduler()
            logger.info("🏁 Daily Strategy Runner stopped")
    
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        send_error_alert(f"Fatal error: {str(e)}", "Daily Strategy Runner")
        raise

if __name__ == "__main__":
    main()
