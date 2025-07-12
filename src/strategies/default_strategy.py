"""
Default Trading Strategy
Balanced approach using RSI, MACD, sentiment analysis, and risk management
This is the primary strategy available to all users
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from technical_indicators import TechnicalIndicators, IndicatorResult, get_trend_indicators
from trading_config import TradingConfig
from database import UserPreferences

class DefaultStrategy:
    """
    Default balanced trading strategy
    
    Features:
    - RSI for momentum analysis
    - MACD for trend confirmation
    - Sentiment analysis integration
    - ATR-based stop loss and take profit
    - Risk management based on user preferences
    """
    
    def __init__(self, config: TradingConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.name = "Default Strategy"
        self.description = "Balanced approach with moderate risk and steady returns"
        
    def analyze_symbol(self, symbol: str, market_data: Dict[str, Any], 
                      sentiment_score: float = 0.0) -> Dict[str, Any]:
        """
        Analyze a symbol and generate trading signal
        
        Args:
            symbol: Stock symbol to analyze
            market_data: Dictionary containing OHLCV data
            sentiment_score: Sentiment analysis score (-1 to 1)
            
        Returns:
            Dictionary containing signal analysis
        """
        try:
            # Extract price data
            prices = market_data.get('close', [])
            highs = market_data.get('high', [])
            lows = market_data.get('low', [])
            volumes = market_data.get('volume', [])
            
            if len(prices) < 50:  # Need sufficient data
                return self._create_insufficient_data_response(symbol)
            
            # Calculate technical indicators
            indicators = self._calculate_technical_indicators(prices, highs, lows)
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_sentiment(sentiment_score)
            
            # Generate composite signal
            signal_analysis = self._generate_composite_signal(
                indicators, sentiment_analysis, symbol
            )
            
            # Calculate risk management levels
            risk_levels = self._calculate_risk_levels(prices, highs, lows)
            
            # Create final recommendation
            recommendation = self._create_recommendation(
                signal_analysis, risk_levels, symbol, sentiment_score
            )
            
            self.logger.info(f"Default strategy analysis complete for {symbol}: {recommendation['action']}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol} with default strategy: {e}")
            return self._create_error_response(symbol, str(e))
    
    def _calculate_technical_indicators(self, prices: List[float], 
                                      highs: List[float], lows: List[float]) -> Dict[str, IndicatorResult]:
        """Calculate all technical indicators used by the strategy"""
        
        indicators = {}
        
        # RSI Analysis
        indicators['rsi'] = TechnicalIndicators.calculate_rsi(
            prices, 
            period=self.config.rsi_period,
            oversold=self.config.rsi_oversold,
            overbought=self.config.rsi_overbought
        )
        
        # MACD Analysis
        indicators['macd'] = TechnicalIndicators.calculate_macd(
            prices,
            fast=self.config.macd_fast,
            slow=self.config.macd_slow,
            signal_period=self.config.macd_signal
        )
        
        # Moving Average Crossover
        indicators['ma_crossover'] = TechnicalIndicators.calculate_moving_averages(
            prices, short_period=20, long_period=50
        )
        
        # ATR for volatility
        indicators['atr'] = TechnicalIndicators.calculate_atr(
            highs, lows, prices, period=self.config.atr_period
        )
        
        # Bollinger Bands
        indicators['bollinger'] = TechnicalIndicators.calculate_bollinger_bands(
            prices, period=20, std_dev=2.0
        )
        
        return indicators
    
    def _analyze_sentiment(self, sentiment_score: float) -> Dict[str, Any]:
        """Analyze sentiment score and generate sentiment signal"""
        
        if sentiment_score >= self.config.sentiment_bullish_threshold:
            signal = 'BUY'
            strength = min(1.0, sentiment_score / self.config.sentiment_bullish_threshold)
        elif sentiment_score <= self.config.sentiment_bearish_threshold:
            signal = 'SELL'
            strength = min(1.0, abs(sentiment_score) / abs(self.config.sentiment_bearish_threshold))
        else:
            signal = 'HOLD'
            strength = abs(sentiment_score) / max(
                abs(self.config.sentiment_bullish_threshold),
                abs(self.config.sentiment_bearish_threshold)
            )
        
        return {
            'signal': signal,
            'strength': strength,
            'score': sentiment_score,
            'bullish_threshold': self.config.sentiment_bullish_threshold,
            'bearish_threshold': self.config.sentiment_bearish_threshold
        }
    
    def _generate_composite_signal(self, indicators: Dict[str, IndicatorResult], 
                                  sentiment: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Generate composite signal from technical indicators and sentiment"""
        
        # Define weights for different signals (can be customized per user preferences)
        weights = {
            'rsi': 0.25,
            'macd': 0.25,
            'ma_crossover': 0.20,
            'bollinger': 0.15,
            'sentiment': 0.15
        }
        
        # Calculate weighted scores
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0
        
        # Technical indicators
        for indicator_name, weight in weights.items():
            if indicator_name == 'sentiment':
                continue
                
            indicator = indicators.get(indicator_name)
            if indicator and indicator.signal != 'HOLD':
                total_weight += weight
                if indicator.signal == 'BUY':
                    buy_score += indicator.strength * weight
                elif indicator.signal == 'SELL':
                    sell_score += indicator.strength * weight
        
        # Sentiment
        sentiment_weight = weights['sentiment']
        if sentiment['signal'] != 'HOLD':
            total_weight += sentiment_weight
            if sentiment['signal'] == 'BUY':
                buy_score += sentiment['strength'] * sentiment_weight
            elif sentiment['signal'] == 'SELL':
                sell_score += sentiment['strength'] * sentiment_weight
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine final signal
        net_score = buy_score - sell_score
        
        if buy_score > sell_score and buy_score >= self.config.min_confidence:
            action = 'BUY'
            confidence = buy_score
        elif sell_score > buy_score and sell_score >= self.config.min_confidence:
            action = 'SELL'
            confidence = sell_score
        else:
            action = 'HOLD'
            confidence = max(buy_score, sell_score)
        
        return {
            'action': action,
            'confidence': confidence,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'net_score': net_score,
            'weights': weights,
            'indicators_summary': {
                name: {'signal': ind.signal, 'strength': ind.strength} 
                for name, ind in indicators.items()
            },
            'sentiment_summary': sentiment
        }
    
    def _calculate_risk_levels(self, prices: List[float], highs: List[float], 
                              lows: List[float]) -> Dict[str, float]:
        """Calculate stop loss and take profit levels"""
        
        current_price = prices[-1]
        
        # ATR-based levels
        atr_result = TechnicalIndicators.calculate_atr(highs, lows, prices, self.config.atr_period)
        atr_value = atr_result.value
        
        # Calculate stop loss and take profit using ATR and user preferences
        atr_stop_loss = current_price - (atr_value * self.config.atr_stop_multiplier)
        atr_take_profit = current_price + (atr_value * self.config.atr_target_multiplier)
        
        # Percentage-based levels (from user preferences)
        pct_stop_loss = current_price * (1 - self.config.stop_loss_percentage)
        pct_take_profit = current_price * (1 + self.config.take_profit_percentage)
        
        # Use the more conservative (closer to current price) stop loss
        final_stop_loss = max(atr_stop_loss, pct_stop_loss)
        
        # Use the more conservative (closer to current price) take profit
        final_take_profit = min(atr_take_profit, pct_take_profit)
        
        return {
            'current_price': current_price,
            'stop_loss': final_stop_loss,
            'take_profit': final_take_profit,
            'atr_value': atr_value,
            'risk_reward_ratio': (final_take_profit - current_price) / (current_price - final_stop_loss),
            'stop_loss_pct': ((current_price - final_stop_loss) / current_price) * 100,
            'take_profit_pct': ((final_take_profit - current_price) / current_price) * 100
        }
    
    def _create_recommendation(self, signal_analysis: Dict[str, Any], 
                             risk_levels: Dict[str, float], symbol: str, 
                             sentiment_score: float) -> Dict[str, Any]:
        """Create final trading recommendation"""
        
        current_price = risk_levels['current_price']
        
        # Generate reasoning
        reasoning_parts = []
        
        # Technical analysis reasoning
        if signal_analysis['action'] != 'HOLD':
            top_indicators = sorted(
                signal_analysis['indicators_summary'].items(),
                key=lambda x: x[1]['strength'],
                reverse=True
            )[:2]
            
            action = signal_analysis['action']
            confidence = signal_analysis['confidence']
            indicator_names = ', '.join([f'{name} ({data["signal"]})' for name, data in top_indicators])
            
            reasoning_parts.append(
                f"Technical analysis shows {action} signal "
                f"with {confidence:.1%} confidence. "
                f"Key indicators: {indicator_names}"
            )
        
        # Sentiment reasoning
        if abs(sentiment_score) > 0.2:
            sentiment_direction = "positive" if sentiment_score > 0 else "negative"
            reasoning_parts.append(
                f"Market sentiment is {sentiment_direction} ({sentiment_score:.2f})"
            )
        
        # Risk management reasoning
        risk_reward = risk_levels['risk_reward_ratio']
        stop_loss_pct = risk_levels['stop_loss_pct']
        take_profit_pct = risk_levels['take_profit_pct']
        
        reasoning_parts.append(
            f"Risk/reward ratio: {risk_reward:.2f}, "
            f"Stop loss: {stop_loss_pct:.1f}%, "
            f"Take profit: {take_profit_pct:.1f}%"
        )
        
        reasoning = ". ".join(reasoning_parts)
        
        return {
            'symbol': symbol,
            'action': signal_analysis['action'],
            'confidence': signal_analysis['confidence'],
            'current_price': current_price,
            'entry_price': current_price,
            'stop_loss': risk_levels['stop_loss'],
            'target_price': risk_levels['take_profit'],
            'risk_reward_ratio': risk_levels['risk_reward_ratio'],
            'sentiment': sentiment_score,
            'reasoning': reasoning,
            'strategy': self.name,
            'timestamp': datetime.now().isoformat(),
            'indicators': {
                'rsi': signal_analysis['indicators_summary'].get('rsi', {}),
                'macd': signal_analysis['indicators_summary'].get('macd', {}),
                'ma_crossover': signal_analysis['indicators_summary'].get('ma_crossover', {}),
                'bollinger': signal_analysis['indicators_summary'].get('bollinger', {}),
                'atr': risk_levels['atr_value']
            },
            'signal_breakdown': {
                'buy_score': signal_analysis['buy_score'],
                'sell_score': signal_analysis['sell_score'],
                'net_score': signal_analysis['net_score'],
                'weights': signal_analysis['weights']
            }
        }
    
    def _create_insufficient_data_response(self, symbol: str) -> Dict[str, Any]:
        """Create response for insufficient data"""
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
            'reasoning': 'Insufficient historical data for analysis',
            'strategy': self.name,
            'timestamp': datetime.now().isoformat(),
            'error': 'insufficient_data'
        }
    
    def _create_error_response(self, symbol: str, error_message: str) -> Dict[str, Any]:
        """Create response for analysis errors"""
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
            'reasoning': f'Analysis error: {error_message}',
            'strategy': self.name,
            'timestamp': datetime.now().isoformat(),
            'error': error_message
        }
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about this strategy"""
        return {
            'name': self.name,
            'description': self.description,
            'indicators': ['RSI', 'MACD', 'Moving Averages', 'Bollinger Bands', 'ATR'],
            'risk_level': 'moderate',
            'suitable_for': ['beginners', 'balanced_traders'],
            'min_data_points': 50,
            'signal_weights': {
                'technical': 0.85,
                'sentiment': 0.15
            }
        }
