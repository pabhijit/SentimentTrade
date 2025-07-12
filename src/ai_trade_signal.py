"""
Enhanced AI Signal Generation
Uses the new refactored architecture with:
- User preferences integration
- Strategy factory pattern
- Technical indicators utility
- Dynamic trading configuration
"""

import os
import sys
from pathlib import Path
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from functools import wraps

# Import our refactored modules
from config import config
from logger import logger, log_trade_signal, log_api_call, log_error_with_context, log_market_data
from telegram_alerts import send_trade_signal, send_error_alert
from trading_config import get_trading_config, TradingConfig
from technical_indicators import TechnicalIndicators, get_trend_indicators
from strategies.strategy_factory import strategy_factory, analyze_symbol
from database import UserPreferences

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying functions on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator

# Exception classes
class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class DataError(Exception):
    """Custom exception for data-related errors"""
    pass

class TradingSignalGenerator:
    """
    Enhanced trading signal generator using the new architecture
    Integrates user preferences, multiple strategies, and shared technical indicators
    """
    
    def __init__(self, user_preferences: Optional[UserPreferences] = None):
        """
        Initialize the signal generator
        
        Args:
            user_preferences: User's trading preferences (optional)
        """
        self.user_preferences = user_preferences
        self.config = get_trading_config(user_preferences)
        self.strategy_name = user_preferences.strategy if user_preferences else 'default'
        
        # Validate configuration
        self._validate_config()
        
        logger.info(f"TradingSignalGenerator initialized with {self.strategy_name} strategy")
        if user_preferences:
            logger.info(f"User preferences: risk={user_preferences.risk_appetite}, "
                       f"confidence={user_preferences.min_confidence}, "
                       f"max_signals={user_preferences.max_daily_signals}")
    
    def _validate_config(self):
        """Validate configuration and API keys"""
        required_keys = ['TWELVE_DATA_API_KEY', 'OPENAI_API_KEY']
        missing_keys = [key for key in required_keys if not getattr(config, key, None)]
        
        if missing_keys:
            logger.warning(f"Missing API keys for backtesting: {missing_keys}")
            logger.info("Backtesting will use mocked data instead of live API calls")
        
        logger.info("✅ Configuration validated for backtesting")
    
    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    def get_market_data(self, symbol: str, days: int = 60) -> Dict[str, List[float]]:
        """
        Fetch market data for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days of historical data
            
        Returns:
            Dictionary with OHLCV data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # TwelveData API call
            url = "https://api.twelvedata.com/time_series"
            params = {
                'symbol': symbol,
                'interval': '1day',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'apikey': getattr(config, 'TWELVE_DATA_API_KEY', '')
            }
            
            log_api_call("TwelveData", "time_series", params)
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'values' not in data:
                raise DataError(f"No market data available for {symbol}")
            
            # Parse data
            values = data['values']
            if not values:
                raise DataError(f"Empty market data for {symbol}")
            
            # Convert to lists (reverse to get chronological order)
            market_data = {
                'close': [float(item['close']) for item in reversed(values)],
                'high': [float(item['high']) for item in reversed(values)],
                'low': [float(item['low']) for item in reversed(values)],
                'open': [float(item['open']) for item in reversed(values)],
                'volume': [int(item['volume']) for item in reversed(values)]
            }
            
            log_market_data(symbol, len(market_data['close']), market_data['close'][-1])
            logger.info(f"✅ Retrieved {len(market_data['close'])} days of data for {symbol}")
            
            return market_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Market data API error for {symbol}: {e}")
            raise APIError(f"Failed to fetch market data: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Market data parsing error for {symbol}: {e}")
            raise DataError(f"Failed to parse market data: {e}")
    
    @retry_on_failure(max_retries=2, delay=2.0, backoff=1.5)
    def get_sentiment_analysis(self, symbol: str) -> float:
        """
        Get sentiment analysis for a symbol using OpenAI
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Sentiment score (-1 to 1)
        """
        try:
            # Get recent news/context for the symbol
            prompt = f"""
            Analyze the current market sentiment for {symbol} stock.
            Consider recent market trends, news, and overall market conditions.
            
            Provide a sentiment score from -1 (very bearish) to +1 (very bullish).
            
            Return only a single number between -1 and 1.
            """
            
            headers = {
                'Authorization': f"Bearer {getattr(config, 'OPENAI_API_KEY', '')}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'You are a financial sentiment analyst. Return only numerical sentiment scores.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 10,
                'temperature': 0.3
            }
            
            log_api_call("OpenAI", "chat/completions", {"symbol": symbol})
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            sentiment_text = result['choices'][0]['message']['content'].strip()
            
            # Parse sentiment score
            try:
                sentiment_score = float(sentiment_text)
                sentiment_score = max(-1.0, min(1.0, sentiment_score))  # Clamp to [-1, 1]
            except ValueError:
                logger.warning(f"Could not parse sentiment score: {sentiment_text}")
                sentiment_score = 0.0
            
            logger.info(f"✅ Sentiment analysis for {symbol}: {sentiment_score:.3f}")
            return sentiment_score
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Sentiment API error for {symbol}: {e}")
            return 0.0  # Neutral sentiment on error
        except Exception as e:
            logger.error(f"Sentiment analysis error for {symbol}: {e}")
            return 0.0
    
    def generate_signal(self, symbol: str) -> Dict[str, Any]:
        """
        Generate trading signal for a symbol using the configured strategy
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dictionary containing signal analysis
        """
        try:
            logger.info(f"🔍 Generating signal for {symbol} using {self.strategy_name} strategy")
            
            # Get market data
            market_data = self.get_market_data(symbol)
            
            # Get sentiment analysis
            sentiment_score = self.get_sentiment_analysis(symbol)
            
            # Use strategy factory to analyze
            signal_result = analyze_symbol(
                strategy_name=self.strategy_name,
                symbol=symbol,
                market_data=market_data,
                sentiment_score=sentiment_score,
                user_preferences=self.user_preferences,
                logger=logger
            )
            
            # Apply user preference filters
            signal_result = self._apply_user_filters(signal_result)
            
            # Log the signal
            log_trade_signal(
                symbol=signal_result['symbol'],
                action=signal_result['action'],
                confidence=signal_result['confidence'],
                price=signal_result['current_price'],
                reasoning=signal_result['reasoning']
            )
            
            # Send notification if enabled and signal meets threshold
            if (self.user_preferences and 
                self.user_preferences.notification_enabled and
                signal_result['confidence'] >= self.user_preferences.signal_threshold and
                signal_result['action'] != 'HOLD'):
                
                try:
                    send_trade_signal(signal_result)
                except Exception as e:
                    logger.warning(f"Failed to send notification: {e}")
            
            logger.info(f"✅ Signal generated for {symbol}: {signal_result['action']} "
                       f"({signal_result['confidence']:.1%} confidence)")
            
            return signal_result
            
        except Exception as e:
            log_error_with_context("signal_generation", str(e), {"symbol": symbol})
            
            # Send error alert
            try:
                send_error_alert(f"Signal generation failed for {symbol}: {str(e)}")
            except:
                pass
            
            # Return safe default
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'confidence': 0.0,
                'current_price': 0.0,
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'target_price': 0.0,
                'risk_reward_ratio': 0.0,
                'sentiment': 0.0,
                'reasoning': f'Signal generation failed: {str(e)}',
                'strategy': self.strategy_name,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _apply_user_filters(self, signal_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user preference filters to the signal"""
        
        if not self.user_preferences:
            return signal_result
        
        # Check minimum confidence threshold
        if signal_result['confidence'] < self.user_preferences.min_confidence:
            logger.info(f"Signal filtered: confidence {signal_result['confidence']:.1%} "
                       f"below user threshold {self.user_preferences.min_confidence:.1%}")
            signal_result['action'] = 'HOLD'
            signal_result['reasoning'] += f" (Below user confidence threshold of {self.user_preferences.min_confidence:.1%})"
        
        return signal_result
    
    def generate_signals_for_watchlist(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Generate signals for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of signal results
        """
        signals = []
        max_signals = self.user_preferences.max_daily_signals if self.user_preferences else 10
        
        logger.info(f"🔍 Generating signals for {len(symbols)} symbols (max: {max_signals})")
        
        for symbol in symbols:
            if len(signals) >= max_signals:
                logger.info(f"Reached maximum daily signals limit: {max_signals}")
                break
            
            try:
                signal = self.generate_signal(symbol)
                signals.append(signal)
                
                # Add delay between API calls to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to generate signal for {symbol}: {e}")
                continue
        
        # Filter and sort signals
        actionable_signals = [s for s in signals if s['action'] != 'HOLD']
        actionable_signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"✅ Generated {len(signals)} total signals, {len(actionable_signals)} actionable")
        
        return signals
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about the current strategy"""
        return strategy_factory.get_available_strategies().get(self.strategy_name, {})

# Convenience functions for backward compatibility
def generate_signal_for_symbol(symbol: str, user_preferences: Optional[UserPreferences] = None) -> Dict[str, Any]:
    """Generate signal for a single symbol"""
    generator = TradingSignalGenerator(user_preferences)
    return generator.generate_signal(symbol)

def generate_signals_for_watchlist(symbols: List[str], user_preferences: Optional[UserPreferences] = None) -> List[Dict[str, Any]]:
    """Generate signals for multiple symbols"""
    generator = TradingSignalGenerator(user_preferences)
    return generator.generate_signals_for_watchlist(symbols)
