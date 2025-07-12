"""
Sentiment Mocker for Backtesting
Generates realistic sentiment signals for historical data backtesting
since we can't call OpenAI API for past dates
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import random
from datetime import datetime, timedelta

class BacktestSentimentMocker:
    """
    Generates realistic sentiment signals for backtesting
    Uses technical indicators and price action to simulate news sentiment
    """
    
    def __init__(self, sentiment_style: str = 'realistic', seed: Optional[int] = None):
        """
        Initialize sentiment mocker
        
        Args:
            sentiment_style: Style of sentiment generation
                - 'realistic': Combines multiple factors for realistic sentiment
                - 'contrarian': Contrarian sentiment (opposite to price momentum)
                - 'momentum': Momentum-following sentiment
                - 'random': Pure random sentiment for baseline testing
                - 'neutral': Always neutral sentiment (0.0)
            seed: Random seed for reproducible results
        """
        self.style = sentiment_style
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        # Sentiment generation parameters
        self.momentum_weight = 0.4
        self.volume_weight = 0.3
        self.technical_weight = 0.3
        self.noise_level = 0.15
        
        # Market regime detection
        self.bull_threshold = 0.02  # 2% price increase for bull signal
        self.bear_threshold = -0.02  # 2% price decrease for bear signal
        
        # Sentiment persistence (sentiment tends to continue)
        self.persistence_factor = 0.3
        self.previous_sentiment = 0.0
    
    def generate_sentiment(self, market_data: Dict, technical_indicators: Dict = None, 
                          timestamp: datetime = None) -> float:
        """
        Generate sentiment score for given market conditions
        
        Args:
            market_data: Dictionary with OHLCV data
            technical_indicators: Optional technical indicator values
            timestamp: Optional timestamp for time-based patterns
            
        Returns:
            Sentiment score between -1.0 and 1.0
        """
        
        if self.style == 'neutral':
            return 0.0
        elif self.style == 'random':
            return self._random_sentiment()
        elif self.style == 'realistic':
            return self._realistic_sentiment(market_data, technical_indicators, timestamp)
        elif self.style == 'contrarian':
            return self._contrarian_sentiment(market_data, technical_indicators)
        elif self.style == 'momentum':
            return self._momentum_sentiment(market_data)
        else:
            return self._realistic_sentiment(market_data, technical_indicators, timestamp)
    
    def _realistic_sentiment(self, market_data: Dict, technical_indicators: Dict = None, 
                           timestamp: datetime = None) -> float:
        """Generate realistic sentiment combining multiple factors"""
        
        # Price momentum component
        price_momentum = self._calculate_price_momentum(market_data)
        
        # Volume analysis component
        volume_signal = self._analyze_volume_pattern(market_data)
        
        # Technical indicator bias
        technical_bias = 0.0
        if technical_indicators:
            technical_bias = self._technical_sentiment_bias(technical_indicators)
        
        # Time-based patterns (optional)
        time_bias = 0.0
        if timestamp:
            time_bias = self._time_based_sentiment(timestamp)
        
        # Combine factors
        base_sentiment = (
            price_momentum * self.momentum_weight +
            volume_signal * self.volume_weight +
            technical_bias * self.technical_weight +
            time_bias * 0.1
        )
        
        # Add persistence (sentiment tends to continue)
        persistent_sentiment = (
            base_sentiment * (1 - self.persistence_factor) +
            self.previous_sentiment * self.persistence_factor
        )
        
        # Add realistic noise
        noise = np.random.uniform(-self.noise_level, self.noise_level)
        final_sentiment = persistent_sentiment + noise
        
        # Clamp to valid range
        final_sentiment = np.clip(final_sentiment, -1.0, 1.0)
        
        # Store for next iteration
        self.previous_sentiment = final_sentiment
        
        return final_sentiment
    
    def _calculate_price_momentum(self, market_data: Dict) -> float:
        """Calculate price momentum component of sentiment"""
        
        current_price = market_data.get('close', 0)
        open_price = market_data.get('open', current_price)
        high_price = market_data.get('high', current_price)
        low_price = market_data.get('low', current_price)
        
        # Intraday momentum
        if open_price > 0:
            intraday_change = (current_price - open_price) / open_price
        else:
            intraday_change = 0
        
        # Range analysis (where price closed within the day's range)
        if high_price != low_price:
            range_position = (current_price - low_price) / (high_price - low_price)
            range_sentiment = (range_position - 0.5) * 2  # Convert to -1 to 1 scale
        else:
            range_sentiment = 0
        
        # Combine momentum factors
        momentum_sentiment = (intraday_change * 10 + range_sentiment) / 2
        
        return np.clip(momentum_sentiment, -1.0, 1.0)
    
    def _analyze_volume_pattern(self, market_data: Dict) -> float:
        """Analyze volume patterns for sentiment signals"""
        
        volume = market_data.get('volume', 0)
        
        # Simulate average volume (in real backtest, this would be calculated from history)
        avg_volume = volume * np.random.uniform(0.8, 1.2)  # Mock average
        
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            
            # High volume with price increase = positive sentiment
            # High volume with price decrease = negative sentiment
            price_change = self._get_price_change(market_data)
            
            if volume_ratio > 1.5:  # High volume
                volume_sentiment = price_change * 0.5
            elif volume_ratio < 0.5:  # Low volume
                volume_sentiment = price_change * 0.2  # Weaker signal
            else:  # Normal volume
                volume_sentiment = price_change * 0.3
        else:
            volume_sentiment = 0
        
        return np.clip(volume_sentiment, -1.0, 1.0)
    
    def _technical_sentiment_bias(self, technical_indicators: Dict) -> float:
        """Generate sentiment bias from technical indicators"""
        
        sentiment_components = []
        
        # RSI-based sentiment
        rsi = technical_indicators.get('rsi', 50)
        if rsi < 30:  # Oversold - contrarian positive
            sentiment_components.append(0.3)
        elif rsi > 70:  # Overbought - contrarian negative
            sentiment_components.append(-0.3)
        else:
            sentiment_components.append((rsi - 50) / 100)  # Normalized RSI
        
        # MACD-based sentiment
        macd = technical_indicators.get('macd', 0)
        macd_signal = technical_indicators.get('macd_signal', 0)
        if macd > macd_signal:
            sentiment_components.append(0.2)
        else:
            sentiment_components.append(-0.2)
        
        # Moving average sentiment
        ma_short = technical_indicators.get('ma_short', 0)
        ma_long = technical_indicators.get('ma_long', 0)
        current_price = technical_indicators.get('price', 0)
        
        if current_price > ma_short > ma_long:
            sentiment_components.append(0.3)  # Strong uptrend
        elif current_price < ma_short < ma_long:
            sentiment_components.append(-0.3)  # Strong downtrend
        else:
            sentiment_components.append(0.0)  # Neutral
        
        # Average the components
        if sentiment_components:
            avg_sentiment = np.mean(sentiment_components)
        else:
            avg_sentiment = 0.0
        
        return np.clip(avg_sentiment, -1.0, 1.0)
    
    def _time_based_sentiment(self, timestamp: datetime) -> float:
        """Generate time-based sentiment patterns"""
        
        # Market opening/closing effects
        hour = timestamp.hour
        if 9 <= hour <= 10:  # Market open - higher volatility
            return np.random.uniform(-0.2, 0.2)
        elif 15 <= hour <= 16:  # Market close - position adjustments
            return np.random.uniform(-0.1, 0.1)
        else:
            return 0.0
    
    def _contrarian_sentiment(self, market_data: Dict, technical_indicators: Dict = None) -> float:
        """Generate contrarian sentiment (opposite to price momentum)"""
        
        price_change = self._get_price_change(market_data)
        
        # Contrarian approach - negative sentiment when price goes up
        contrarian_sentiment = -price_change * 2
        
        # Add some noise
        noise = np.random.uniform(-0.1, 0.1)
        
        return np.clip(contrarian_sentiment + noise, -1.0, 1.0)
    
    def _momentum_sentiment(self, market_data: Dict) -> float:
        """Generate momentum-following sentiment"""
        
        price_change = self._get_price_change(market_data)
        
        # Momentum approach - positive sentiment when price goes up
        momentum_sentiment = price_change * 3
        
        # Add some noise
        noise = np.random.uniform(-0.1, 0.1)
        
        return np.clip(momentum_sentiment + noise, -1.0, 1.0)
    
    def _random_sentiment(self) -> float:
        """Generate pure random sentiment for baseline testing"""
        return np.random.uniform(-1.0, 1.0)
    
    def _get_price_change(self, market_data: Dict) -> float:
        """Calculate normalized price change"""
        
        current_price = market_data.get('close', 0)
        open_price = market_data.get('open', current_price)
        
        if open_price > 0:
            return (current_price - open_price) / open_price
        else:
            return 0.0
    
    def generate_sentiment_series(self, market_data_series: List[Dict], 
                                 technical_series: List[Dict] = None,
                                 timestamps: List[datetime] = None) -> List[float]:
        """
        Generate sentiment series for entire backtest period
        
        Args:
            market_data_series: List of market data dictionaries
            technical_series: Optional list of technical indicator dictionaries
            timestamps: Optional list of timestamps
            
        Returns:
            List of sentiment scores
        """
        
        sentiment_series = []
        
        for i, market_data in enumerate(market_data_series):
            technical_data = technical_series[i] if technical_series else None
            timestamp = timestamps[i] if timestamps else None
            
            sentiment = self.generate_sentiment(market_data, technical_data, timestamp)
            sentiment_series.append(sentiment)
        
        return sentiment_series
    
    def get_sentiment_statistics(self, sentiment_series: List[float]) -> Dict[str, float]:
        """Calculate statistics for generated sentiment series"""
        
        if not sentiment_series:
            return {}
        
        sentiment_array = np.array(sentiment_series)
        
        return {
            'mean': np.mean(sentiment_array),
            'std': np.std(sentiment_array),
            'min': np.min(sentiment_array),
            'max': np.max(sentiment_array),
            'positive_ratio': np.sum(sentiment_array > 0.1) / len(sentiment_array),
            'negative_ratio': np.sum(sentiment_array < -0.1) / len(sentiment_array),
            'neutral_ratio': np.sum(np.abs(sentiment_array) <= 0.1) / len(sentiment_array)
        }

# Convenience functions
def create_sentiment_mocker(style: str = 'realistic', seed: int = None) -> BacktestSentimentMocker:
    """Create a sentiment mocker with specified style"""
    return BacktestSentimentMocker(sentiment_style=style, seed=seed)

def mock_sentiment_for_backtest(market_data: Dict, style: str = 'realistic') -> float:
    """Quick function to generate single sentiment value"""
    mocker = BacktestSentimentMocker(sentiment_style=style)
    return mocker.generate_sentiment(market_data)
