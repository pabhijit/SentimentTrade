"""
Technical Indicators Utility (Clean Version)
Shared calculations for RSI, MACD, ATR, and other technical indicators
No external dependencies - pure Python implementation
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class IndicatorResult:
    """Container for indicator calculation results"""
    value: float
    signal: str  # 'BUY', 'SELL', 'HOLD'
    strength: float  # 0.0 to 1.0
    metadata: Dict = None

class TechnicalIndicators:
    """Technical indicators calculation utility class"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14, 
                     oversold: float = 30, overbought: float = 70) -> IndicatorResult:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return IndicatorResult(50.0, 'HOLD', 0.0, {'error': 'Insufficient data'})
        
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [max(delta, 0) for delta in deltas]
        losses = [abs(min(delta, 0)) for delta in deltas]
        
        # Calculate initial averages
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate RSI for remaining periods
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Calculate RSI
        if avg_loss == 0:
            current_rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            current_rsi = 100 - (100 / (1 + rs))
        
        # Determine signal
        if current_rsi <= oversold:
            signal = 'BUY'
            strength = min(1.0, (oversold - current_rsi) / oversold)
        elif current_rsi >= overbought:
            signal = 'SELL'
            strength = min(1.0, (current_rsi - overbought) / (100 - overbought))
        else:
            signal = 'HOLD'
            distance_from_neutral = abs(current_rsi - 50)
            strength = distance_from_neutral / 50.0
        
        return IndicatorResult(
            value=current_rsi,
            signal=signal,
            strength=strength,
            metadata={'period': period, 'oversold': oversold, 'overbought': overbought}
        )
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma_values = []
        for i in range(period - 1, len(prices)):
            sma = sum(prices[i - period + 1:i + 1]) / period
            sma_values.append(sma)
        
        return sma_values
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = []
        
        # Start with SMA for first value
        sma = sum(prices[:period]) / period
        ema_values.append(sma)
        
        # Calculate EMA for remaining values
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, 
                      signal_period: int = 9) -> IndicatorResult:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow + signal_period:
            return IndicatorResult(0.0, 'HOLD', 0.0, {'error': 'Insufficient data'})
        
        # Calculate EMAs
        fast_ema = TechnicalIndicators.calculate_ema(prices, fast)
        slow_ema = TechnicalIndicators.calculate_ema(prices, slow)
        
        # Calculate MACD line
        macd_line = []
        start_idx = slow - fast
        for i in range(len(slow_ema)):
            macd_value = fast_ema[i + start_idx] - slow_ema[i]
            macd_line.append(macd_value)
        
        # Calculate signal line (EMA of MACD line)
        signal_line = TechnicalIndicators.calculate_ema(macd_line, signal_period)
        
        if not signal_line:
            return IndicatorResult(0.0, 'HOLD', 0.0, {'error': 'Insufficient data for signal line'})
        
        # Calculate histogram
        histogram = []
        signal_start = len(macd_line) - len(signal_line)
        for i in range(len(signal_line)):
            hist_value = macd_line[i + signal_start] - signal_line[i]
            histogram.append(hist_value)
        
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        current_histogram = histogram[-1]
        previous_histogram = histogram[-2] if len(histogram) > 1 else 0
        
        # Determine signal
        if current_macd > current_signal and current_histogram > previous_histogram:
            signal = 'BUY'
            strength = min(1.0, abs(current_histogram) / (abs(current_macd) + 0.001))
        elif current_macd < current_signal and current_histogram < previous_histogram:
            signal = 'SELL'
            strength = min(1.0, abs(current_histogram) / (abs(current_macd) + 0.001))
        else:
            signal = 'HOLD'
            strength = abs(current_histogram) / (abs(current_macd) + 0.001)
        
        return IndicatorResult(
            value=current_macd,
            signal=signal,
            strength=strength,
            metadata={
                'macd_line': current_macd,
                'signal_line': current_signal,
                'histogram': current_histogram,
                'crossover': current_macd > current_signal
            }
        )
    
    @staticmethod
    def calculate_composite_signal(indicators: List[IndicatorResult]) -> IndicatorResult:
        """Calculate composite signal from multiple indicators"""
        if not indicators:
            return IndicatorResult(0.0, 'HOLD', 0.0, {'error': 'No indicators provided'})
        
        buy_score = 0.0
        sell_score = 0.0
        total_weight = len(indicators)
        
        for indicator in indicators:
            if indicator.signal == 'BUY':
                buy_score += indicator.strength
            elif indicator.signal == 'SELL':
                sell_score += indicator.strength
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Determine composite signal
        if buy_score > sell_score and buy_score > 0.5:
            signal = 'BUY'
            strength = buy_score
        elif sell_score > buy_score and sell_score > 0.5:
            signal = 'SELL'
            strength = sell_score
        else:
            signal = 'HOLD'
            strength = max(buy_score, sell_score)
        
        return IndicatorResult(
            value=buy_score - sell_score,
            signal=signal,
            strength=strength,
            metadata={'buy_score': buy_score, 'sell_score': sell_score}
        )

# Convenience functions
def get_trend_indicators(prices: List[float]) -> Dict[str, IndicatorResult]:
    """Get common trend-following indicators"""
    return {
        'rsi': TechnicalIndicators.calculate_rsi(prices),
        'macd': TechnicalIndicators.calculate_macd(prices)
    }
