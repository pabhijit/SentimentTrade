#!/usr/bin/env python3
"""
Clean Strategy Factory for SentimentTrade Platform
Unified factory for all trading strategies with automation support

Author: SentimentTrade Development Team
Version: 3.0.0 - Clean Architecture
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional, List, Union
import logging
import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime

# Import configurations
from trading_config import TradingConfig, get_trading_config
from database import UserPreferences

class TradingSignal:
    """Standardized trading signal format"""
    
    def __init__(self, symbol: str, action: str, confidence: float, 
                 current_price: float, strategy_name: str, **kwargs):
        self.symbol = symbol
        self.action = action.upper()  # BUY, SELL, HOLD
        self.confidence = confidence  # 0.0 to 1.0
        self.current_price = current_price
        self.strategy_name = strategy_name
        self.timestamp = datetime.now()
        
        # Optional fields
        self.entry_price = kwargs.get('entry_price', current_price)
        self.stop_loss = kwargs.get('stop_loss', 0.0)
        self.target_price = kwargs.get('target_price', 0.0)
        self.reasoning = kwargs.get('reasoning', '')
        self.indicators = kwargs.get('indicators', {})
        self.risk_reward_ratio = kwargs.get('risk_reward_ratio', 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary format"""
        return {
            'symbol': self.symbol,
            'action': self.action,
            'confidence': self.confidence,
            'current_price': self.current_price,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'target_price': self.target_price,
            'strategy': self.strategy_name,
            'reasoning': self.reasoning,
            'indicators': self.indicators,
            'risk_reward_ratio': self.risk_reward_ratio,
            'timestamp': self.timestamp.isoformat()
        }
    
    def is_actionable(self, min_confidence: float = 0.6) -> bool:
        """Check if signal is actionable based on confidence threshold"""
        return self.action != 'HOLD' and self.confidence >= min_confidence

class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.logger = logging.getLogger(f"strategy.{name}")
    
    @abstractmethod
    def analyze(self, symbol: str, data: pd.DataFrame, **kwargs) -> TradingSignal:
        """
        Analyze market data and generate trading signal
        
        Args:
            symbol: Stock symbol
            data: OHLCV DataFrame
            **kwargs: Additional parameters (sentiment, etc.)
            
        Returns:
            TradingSignal object
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get strategy information"""
        return {
            'name': self.name,
            'description': self.description,
            'config': self.config
        }

class DefaultStrategy(BaseStrategy):
    """Default balanced trading strategy"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Default Strategy",
            description="Balanced RSI + MA + Volume analysis",
            config=config
        )
        
        # Strategy parameters
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_oversold = self.config.get('rsi_oversold', 30)
        self.rsi_overbought = self.config.get('rsi_overbought', 70)
        self.ma_short = self.config.get('ma_short', 20)
        self.ma_long = self.config.get('ma_long', 50)
        self.volume_threshold = self.config.get('volume_threshold', 1.2)
    
    def analyze(self, symbol: str, data: pd.DataFrame, **kwargs) -> TradingSignal:
        """Analyze using RSI, MA, and volume"""
        try:
            # Calculate indicators
            data = data.copy()
            data['RSI'] = self._calculate_rsi(data['Close'], self.rsi_period)
            data['MA_Short'] = data['Close'].rolling(self.ma_short).mean()
            data['MA_Long'] = data['Close'].rolling(self.ma_long).mean()
            data['Volume_MA'] = data['Volume'].rolling(20).mean()
            
            current = data.iloc[-1]
            current_price = current['Close']
            
            # Signal generation
            signal_score = 0
            reasoning = []
            
            # RSI analysis
            if current['RSI'] < self.rsi_oversold:
                signal_score += 0.4
                reasoning.append(f"RSI oversold ({current['RSI']:.1f})")
            elif current['RSI'] > self.rsi_overbought:
                signal_score -= 0.4
                reasoning.append(f"RSI overbought ({current['RSI']:.1f})")
            
            # Moving average analysis
            if current['MA_Short'] > current['MA_Long']:
                signal_score += 0.3
                reasoning.append("Bullish MA alignment")
            else:
                signal_score -= 0.3
                reasoning.append("Bearish MA alignment")
            
            # Volume confirmation
            if current['Volume'] > current['Volume_MA'] * self.volume_threshold:
                signal_score += 0.2
                reasoning.append("High volume confirmation")
            
            # Determine action and confidence
            if signal_score > 0.5:
                action = 'BUY'
                confidence = min(0.85, 0.5 + signal_score)
                stop_loss = current_price * 0.95
                target_price = current_price * 1.08
            elif signal_score < -0.5:
                action = 'SELL'
                confidence = min(0.85, 0.5 + abs(signal_score))
                stop_loss = current_price * 1.05
                target_price = current_price * 0.92
            else:
                action = 'HOLD'
                confidence = 0.3
                stop_loss = current_price
                target_price = current_price
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                strategy_name=self.name,
                stop_loss=stop_loss,
                target_price=target_price,
                reasoning='; '.join(reasoning),
                indicators={
                    'rsi': current['RSI'],
                    'ma_short': current['MA_Short'],
                    'ma_long': current['MA_Long'],
                    'signal_score': signal_score
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return TradingSignal(
                symbol=symbol,
                action='HOLD',
                confidence=0.0,
                current_price=data['Close'].iloc[-1] if not data.empty else 0,
                strategy_name=self.name,
                reasoning=f"Analysis error: {str(e)}"
            )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Momentum Strategy",
            description="MACD + RSI momentum analysis",
            config=config
        )
        
        self.macd_fast = self.config.get('macd_fast', 12)
        self.macd_slow = self.config.get('macd_slow', 26)
        self.macd_signal = self.config.get('macd_signal', 9)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.momentum_threshold = self.config.get('momentum_threshold', 0.02)
    
    def analyze(self, symbol: str, data: pd.DataFrame, **kwargs) -> TradingSignal:
        """Analyze using MACD and momentum"""
        try:
            data = data.copy()
            
            # Calculate indicators
            data['MACD'], data['MACD_Signal'] = self._calculate_macd(data['Close'])
            data['RSI'] = self._calculate_rsi(data['Close'])
            data['Momentum'] = data['Close'].pct_change(10)  # 10-day momentum
            
            current = data.iloc[-1]
            current_price = current['Close']
            
            signal_score = 0
            reasoning = []
            
            # MACD analysis
            if current['MACD'] > current['MACD_Signal']:
                signal_score += 0.4
                reasoning.append("MACD bullish crossover")
            else:
                signal_score -= 0.4
                reasoning.append("MACD bearish crossover")
            
            # RSI momentum
            if current['RSI'] > 55:
                signal_score += 0.2
                reasoning.append("RSI showing momentum")
            elif current['RSI'] < 45:
                signal_score -= 0.2
                reasoning.append("RSI showing weakness")
            
            # Price momentum
            if abs(current['Momentum']) > self.momentum_threshold:
                momentum_signal = 0.3 if current['Momentum'] > 0 else -0.3
                signal_score += momentum_signal
                direction = "positive" if current['Momentum'] > 0 else "negative"
                reasoning.append(f"Strong {direction} momentum ({current['Momentum']:.1%})")
            
            # Determine action
            if signal_score > 0.5:
                action = 'BUY'
                confidence = min(0.8, 0.5 + signal_score)
                stop_loss = current_price * 0.94
                target_price = current_price * 1.12
            elif signal_score < -0.5:
                action = 'SELL'
                confidence = min(0.8, 0.5 + abs(signal_score))
                stop_loss = current_price * 1.06
                target_price = current_price * 0.88
            else:
                action = 'HOLD'
                confidence = 0.3
                stop_loss = current_price
                target_price = current_price
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                strategy_name=self.name,
                stop_loss=stop_loss,
                target_price=target_price,
                reasoning='; '.join(reasoning),
                indicators={
                    'macd': current['MACD'],
                    'macd_signal': current['MACD_Signal'],
                    'rsi': current['RSI'],
                    'momentum': current['Momentum'],
                    'signal_score': signal_score
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return TradingSignal(
                symbol=symbol,
                action='HOLD',
                confidence=0.0,
                current_price=data['Close'].iloc[-1] if not data.empty else 0,
                strategy_name=self.name,
                reasoning=f"Analysis error: {str(e)}"
            )
    
    def _calculate_macd(self, prices: pd.Series):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=self.macd_fast).mean()
        ema_slow = prices.ewm(span=self.macd_slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=self.macd_signal).mean()
        return macd, macd_signal
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using Bollinger Bands"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Mean Reversion Strategy",
            description="Bollinger Bands mean reversion",
            config=config
        )
        
        self.bb_period = self.config.get('bb_period', 20)
        self.bb_std = self.config.get('bb_std', 2.0)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_oversold = self.config.get('rsi_oversold', 25)
        self.rsi_overbought = self.config.get('rsi_overbought', 75)
    
    def analyze(self, symbol: str, data: pd.DataFrame, **kwargs) -> TradingSignal:
        """Analyze using Bollinger Bands for mean reversion"""
        try:
            data = data.copy()
            
            # Calculate indicators
            data['BB_Middle'] = data['Close'].rolling(self.bb_period).mean()
            bb_std = data['Close'].rolling(self.bb_period).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * self.bb_std)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * self.bb_std)
            data['RSI'] = self._calculate_rsi(data['Close'])
            
            current = data.iloc[-1]
            current_price = current['Close']
            
            signal_score = 0
            reasoning = []
            
            # Bollinger Band position
            bb_position = (current_price - current['BB_Lower']) / (current['BB_Upper'] - current['BB_Lower'])
            
            if current_price <= current['BB_Lower']:
                signal_score += 0.5
                reasoning.append("Price at lower Bollinger Band")
            elif current_price >= current['BB_Upper']:
                signal_score -= 0.5
                reasoning.append("Price at upper Bollinger Band")
            
            # RSI confirmation
            if current['RSI'] <= self.rsi_oversold:
                signal_score += 0.3
                reasoning.append(f"RSI oversold ({current['RSI']:.1f})")
            elif current['RSI'] >= self.rsi_overbought:
                signal_score -= 0.3
                reasoning.append(f"RSI overbought ({current['RSI']:.1f})")
            
            # Determine action
            if signal_score > 0.6:
                action = 'BUY'
                confidence = min(0.85, 0.5 + signal_score)
                stop_loss = current_price * 0.96
                target_price = current['BB_Middle']
            elif signal_score < -0.6:
                action = 'SELL'
                confidence = min(0.85, 0.5 + abs(signal_score))
                stop_loss = current_price * 1.04
                target_price = current['BB_Middle']
            else:
                action = 'HOLD'
                confidence = 0.3
                stop_loss = current_price
                target_price = current_price
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                strategy_name=self.name,
                stop_loss=stop_loss,
                target_price=target_price,
                reasoning='; '.join(reasoning),
                indicators={
                    'bb_position': bb_position,
                    'bb_upper': current['BB_Upper'],
                    'bb_middle': current['BB_Middle'],
                    'bb_lower': current['BB_Lower'],
                    'rsi': current['RSI'],
                    'signal_score': signal_score
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return TradingSignal(
                symbol=symbol,
                action='HOLD',
                confidence=0.0,
                current_price=data['Close'].iloc[-1] if not data.empty else 0,
                strategy_name=self.name,
                reasoning=f"Analysis error: {str(e)}"
            )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class BreakRetestStrategy(BaseStrategy):
    """Break & Retest strategy adapted for clean architecture"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Break & Retest Strategy",
            description="Support/Resistance breakout and retest analysis",
            config=config
        )
        
        # Strategy parameters from backtesting optimization
        self.lookback_period = self.config.get('lookback_period', 20)
        self.min_breakout_strength = self.config.get('min_breakout_strength', 0.008)  # 0.8%
        self.retest_tolerance = self.config.get('retest_tolerance', 0.007)  # 0.7%
        self.volume_factor = self.config.get('volume_factor', 1.3)
        self.rsi_period = self.config.get('rsi_period', 14)
    
    def analyze(self, symbol: str, data: pd.DataFrame, **kwargs) -> TradingSignal:
        """Analyze for break & retest opportunities"""
        try:
            data = data.copy()
            
            # Calculate indicators
            data['RSI'] = self._calculate_rsi(data['Close'])
            data['Volume_MA'] = data['Volume'].rolling(20).mean()
            
            # Find support/resistance levels
            highs = data['High'].rolling(self.lookback_period, center=True).max()
            lows = data['Low'].rolling(self.lookback_period, center=True).min()
            
            # Identify swing points
            data['Swing_High'] = (data['High'] == highs)
            data['Swing_Low'] = (data['Low'] == lows)
            
            current = data.iloc[-1]
            current_price = current['Close']
            
            signal_score = 0
            reasoning = []
            
            # Look for recent breakouts
            recent_data = data.tail(10)  # Last 10 days
            
            # Check for resistance breakout
            resistance_levels = data[data['Swing_High']]['High'].tail(5)
            if not resistance_levels.empty:
                nearest_resistance = resistance_levels.iloc[-1]
                breakout_strength = (current_price - nearest_resistance) / nearest_resistance
                
                if breakout_strength > self.min_breakout_strength:
                    signal_score += 0.4
                    reasoning.append(f"Resistance breakout ({breakout_strength:.1%})")
                    
                    # Check for retest
                    if abs(current_price - nearest_resistance) / nearest_resistance < self.retest_tolerance:
                        signal_score += 0.3
                        reasoning.append("Price retesting broken resistance")
            
            # Check for support breakout (bearish)
            support_levels = data[data['Swing_Low']]['Low'].tail(5)
            if not support_levels.empty:
                nearest_support = support_levels.iloc[-1]
                breakdown_strength = (nearest_support - current_price) / nearest_support
                
                if breakdown_strength > self.min_breakout_strength:
                    signal_score -= 0.4
                    reasoning.append(f"Support breakdown ({breakdown_strength:.1%})")
                    
                    # Check for retest
                    if abs(current_price - nearest_support) / nearest_support < self.retest_tolerance:
                        signal_score -= 0.3
                        reasoning.append("Price retesting broken support")
            
            # Volume confirmation
            if current['Volume'] > current['Volume_MA'] * self.volume_factor:
                signal_score += 0.2 if signal_score > 0 else -0.2
                reasoning.append("Volume confirmation")
            
            # RSI confirmation
            if signal_score > 0 and current['RSI'] < 70:  # Bullish but not overbought
                signal_score += 0.1
                reasoning.append("RSI not overbought")
            elif signal_score < 0 and current['RSI'] > 30:  # Bearish but not oversold
                signal_score -= 0.1
                reasoning.append("RSI not oversold")
            
            # Determine action
            if signal_score > 0.6:
                action = 'BUY'
                confidence = min(0.85, 0.5 + signal_score)
                stop_loss = current_price * 0.94  # 6% stop loss
                target_price = current_price * 1.12  # 12% target
            elif signal_score < -0.6:
                action = 'SELL'
                confidence = min(0.85, 0.5 + abs(signal_score))
                stop_loss = current_price * 1.06  # 6% stop loss
                target_price = current_price * 0.88  # 12% target
            else:
                action = 'HOLD'
                confidence = 0.3
                stop_loss = current_price
                target_price = current_price
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                strategy_name=self.name,
                stop_loss=stop_loss,
                target_price=target_price,
                reasoning='; '.join(reasoning) if reasoning else 'No clear setup',
                indicators={
                    'rsi': current['RSI'],
                    'volume_ratio': current['Volume'] / current['Volume_MA'],
                    'signal_score': signal_score
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return TradingSignal(
                symbol=symbol,
                action='HOLD',
                confidence=0.0,
                current_price=data['Close'].iloc[-1] if not data.empty else 0,
                strategy_name=self.name,
                reasoning=f"Analysis error: {str(e)}"
            )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class MechanicalOptionsStrategy(BaseStrategy):
    """Mechanical Options strategy for QQQ"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="Mechanical Options Strategy",
            description="QQQ mechanical options trading (91-96% win rate)",
            config=config
        )
        
        # Strategy parameters
        self.scenario = self.config.get('scenario', 1)  # 1, 2, or 3
        self.min_drop_pct = self.config.get('min_drop_pct', 0.01)  # 1% minimum drop
        self.sma_period = self.config.get('sma_period', 100)  # 100-day SMA
        self.ath_lookback = self.config.get('ath_lookback', 90)  # 3 months for ATH
        self.pullback_threshold = self.config.get('pullback_threshold', 0.03)  # 3% pullback
    
    def analyze(self, symbol: str, data: pd.DataFrame, **kwargs) -> TradingSignal:
        """Analyze for mechanical options opportunities (QQQ only)"""
        try:
            # This strategy is specifically for QQQ
            if symbol != 'QQQ':
                return TradingSignal(
                    symbol=symbol,
                    action='HOLD',
                    confidence=0.0,
                    current_price=data['Close'].iloc[-1] if not data.empty else 0,
                    strategy_name=self.name,
                    reasoning='Strategy only applies to QQQ'
                )
            
            data = data.copy()
            
            # Calculate indicators
            data['SMA_100'] = data['Close'].rolling(self.sma_period).mean()
            data['Daily_Return'] = data['Close'].pct_change()
            data['ATH'] = data['High'].rolling(self.ath_lookback).max()
            
            current = data.iloc[-1]
            prev = data.iloc[-2]
            current_price = current['Close']
            
            signal_score = 0
            reasoning = []
            scenario_met = False
            
            # Scenario 1: Basic - Any 1% down day
            if self.scenario == 1:
                if current['Daily_Return'] <= -self.min_drop_pct:
                    signal_score = 0.7  # High confidence based on 91% win rate
                    reasoning.append(f"QQQ down {abs(current['Daily_Return']):.1%} (Scenario 1)")
                    scenario_met = True
            
            # Scenario 2: Gap Down + Trend Filter
            elif self.scenario == 2:
                gap_down = (current['Open'] - prev['Close']) / prev['Close'] <= -self.min_drop_pct
                above_sma = current['Close'] > current['SMA_100']
                
                if gap_down and above_sma:
                    signal_score = 0.8  # Higher confidence based on 96% win rate
                    reasoning.append(f"Gap down {abs((current['Open'] - prev['Close']) / prev['Close']):.1%} + above SMA (Scenario 2)")
                    scenario_met = True
            
            # Scenario 3: Pullback + Trend Filter
            elif self.scenario == 3:
                pullback_from_ath = (current['ATH'] - current['Close']) / current['ATH']
                above_sma = current['Close'] > current['SMA_100']
                
                if pullback_from_ath >= self.pullback_threshold and above_sma:
                    signal_score = 0.85  # Highest confidence based on 96%+ win rate
                    reasoning.append(f"Pullback {pullback_from_ath:.1%} from ATH + above SMA (Scenario 3)")
                    scenario_met = True
            
            # Determine action (this is a call options strategy)
            if scenario_met and signal_score > 0.6:
                action = 'BUY'  # Buy call options
                confidence = signal_score
                # Options-specific targets (these would be for the underlying)
                stop_loss = current_price * 0.92  # 8% stop loss
                target_price = current_price * 1.15  # 15% target (options would be much higher)
                
                reasoning.append("Mechanical options entry signal")
            else:
                action = 'HOLD'
                confidence = 0.3
                stop_loss = current_price
                target_price = current_price
                if not reasoning:
                    reasoning.append("No mechanical setup detected")
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                current_price=current_price,
                strategy_name=self.name,
                stop_loss=stop_loss,
                target_price=target_price,
                reasoning='; '.join(reasoning),
                indicators={
                    'daily_return': current['Daily_Return'],
                    'sma_100': current['SMA_100'],
                    'above_sma': current['Close'] > current['SMA_100'],
                    'scenario': self.scenario,
                    'signal_score': signal_score
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return TradingSignal(
                symbol=symbol,
                action='HOLD',
                confidence=0.0,
                current_price=data['Close'].iloc[-1] if not data.empty else 0,
                strategy_name=self.name,
                reasoning=f"Analysis error: {str(e)}"
            )

class StrategyFactory:
    
    def __init__(self):
        self._strategies = {
            'default': DefaultStrategy,
            'momentum': MomentumStrategy,
            'mean_reversion': MeanReversionStrategy,
            'break_retest': BreakRetestStrategy,
            'mechanical_options': MechanicalOptionsStrategy
        }
        self.logger = logging.getLogger(__name__)
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names"""
        return list(self._strategies.keys())
    
    def create_strategy(self, strategy_name: str, config: Optional[Dict[str, Any]] = None) -> BaseStrategy:
        """Create a strategy instance"""
        if strategy_name not in self._strategies:
            available = ', '.join(self.get_available_strategies())
            raise ValueError(f"Unknown strategy '{strategy_name}'. Available: {available}")
        
        strategy_class = self._strategies[strategy_name]
        return strategy_class(config)
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """Get information about a strategy"""
        if strategy_name not in self._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Create temporary instance to get info
        strategy = self.create_strategy(strategy_name)
        return strategy.get_info()
    
    def analyze_symbol(self, strategy_name: str, symbol: str, data: pd.DataFrame, 
                      config: Optional[Dict[str, Any]] = None, **kwargs) -> TradingSignal:
        """Analyze a symbol using specified strategy"""
        strategy = self.create_strategy(strategy_name, config)
        return strategy.analyze(symbol, data, **kwargs)

# Global factory instance
strategy_factory = StrategyFactory()

# Convenience functions
def get_available_strategies() -> List[str]:
    """Get available strategies"""
    return strategy_factory.get_available_strategies()

def analyze_symbol(strategy_name: str, symbol: str, data: pd.DataFrame, 
                  config: Optional[Dict[str, Any]] = None, **kwargs) -> TradingSignal:
    """Analyze symbol with specified strategy"""
    return strategy_factory.analyze_symbol(strategy_name, symbol, data, config, **kwargs)

def create_strategy(strategy_name: str, config: Optional[Dict[str, Any]] = None) -> BaseStrategy:
    """Create strategy instance"""
    return strategy_factory.create_strategy(strategy_name, config)
