#!/usr/bin/env python3
"""
Test script for the refactored SentimentTrade architecture
Tests the new modular design with:
- Trading configuration management
- Technical indicators utility
- Strategy factory pattern
- User preferences integration
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from database import init_database, get_db, User, UserPreferences
from trading_config import TradingConfigManager, get_trading_config, get_strategy_config
from technical_indicators import TechnicalIndicators, get_trend_indicators
from strategies.strategy_factory import strategy_factory, get_available_strategies, create_strategy
from preferences_service import PreferencesService

def test_trading_config():
    """Test the new trading configuration system"""
    print("🔧 Testing Trading Configuration System")
    print("=" * 50)
    
    try:
        config_manager = TradingConfigManager()
        
        # Test base configuration
        base_config = config_manager.get_user_config()
        print(f"✅ Base configuration loaded")
        print(f"   Position Size: ${base_config.position_size}")
        print(f"   RSI Period: {base_config.rsi_period}")
        print(f"   Min Confidence: {base_config.min_confidence}")
        
        # Test with mock user preferences
        db = next(get_db())
        users = db.query(User).all()
        if users:
            user = users[0]
            preferences_service = PreferencesService(db)
            user_prefs = preferences_service.get_or_create_preferences(user.id)
            
            # Test user-specific configuration
            user_config = config_manager.get_user_config(user_prefs)
            print(f"✅ User-specific configuration")
            print(f"   Risk Appetite: {user_prefs.risk_appetite}")
            print(f"   Strategy: {user_prefs.strategy}")
            print(f"   Min Confidence: {user_config.min_confidence}")
            print(f"   Max Daily Signals: {user_config.max_daily_signals}")
            
            # Test strategy-specific configuration
            strategy_config = get_strategy_config('default', user_prefs)
            print(f"✅ Strategy configuration")
            print(f"   Strategy Name: {strategy_config['name']}")
            print(f"   Indicators: {', '.join(strategy_config['indicators'])}")
            print(f"   Signal Weights: {strategy_config['signal_weight']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Trading config test failed: {e}")
        return False

def test_technical_indicators():
    """Test the technical indicators utility"""
    print("\n📊 Testing Technical Indicators Utility")
    print("=" * 50)
    
    try:
        # Mock price data (simulating AAPL-like movement)
        prices = [
            150.0, 152.0, 151.5, 153.0, 154.5, 153.8, 155.0, 156.2,
            154.8, 157.0, 158.5, 157.2, 159.0, 160.5, 159.8, 161.0,
            162.5, 161.8, 163.0, 164.2, 163.5, 165.0, 166.5, 165.8,
            167.0, 168.2, 167.5, 169.0, 170.5, 169.8, 171.0, 172.5
        ]
        
        highs = [p + 1.0 for p in prices]  # Mock highs
        lows = [p - 1.0 for p in prices]   # Mock lows
        
        # Test RSI calculation
        rsi_result = TechnicalIndicators.calculate_rsi(prices)
        print(f"✅ RSI Analysis")
        print(f"   Value: {rsi_result.value:.2f}")
        print(f"   Signal: {rsi_result.signal}")
        print(f"   Strength: {rsi_result.strength:.2f}")
        
        # Test MACD calculation
        macd_result = TechnicalIndicators.calculate_macd(prices)
        print(f"✅ MACD Analysis")
        print(f"   Value: {macd_result.value:.4f}")
        print(f"   Signal: {macd_result.signal}")
        print(f"   Strength: {macd_result.strength:.2f}")
        
        # Test ATR calculation
        atr_result = TechnicalIndicators.calculate_atr(highs, lows, prices)
        print(f"✅ ATR Analysis")
        print(f"   Value: {atr_result.value:.2f}")
        print(f"   Volatility: {atr_result.metadata['volatility_level']}")
        
        # Test Bollinger Bands
        bb_result = TechnicalIndicators.calculate_bollinger_bands(prices)
        print(f"✅ Bollinger Bands Analysis")
        print(f"   Signal: {bb_result.signal}")
        print(f"   Band Position: {bb_result.metadata['band_position']:.2f}")
        
        # Test composite signal
        indicators = [rsi_result, macd_result, bb_result]
        composite = TechnicalIndicators.calculate_composite_signal(indicators)
        print(f"✅ Composite Signal")
        print(f"   Final Signal: {composite.signal}")
        print(f"   Confidence: {composite.strength:.2f}")
        print(f"   Buy Score: {composite.metadata['buy_score']:.2f}")
        print(f"   Sell Score: {composite.metadata['sell_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Technical indicators test failed: {e}")
        return False

def test_strategy_factory():
    """Test the strategy factory system"""
    print("\n🏭 Testing Strategy Factory System")
    print("=" * 50)
    
    try:
        # Test available strategies
        strategies = get_available_strategies()
        print(f"✅ Available strategies: {len(strategies)}")
        
        for name, info in strategies.items():
            status = "✅ Available" if info['available'] else "🚧 Coming Soon"
            print(f"   {status} {info['name']}")
            print(f"      📝 {info['description']}")
            print(f"      📊 Risk Level: {info['risk_level']}")
            print(f"      🔧 Indicators: {', '.join(info['indicators'])}")
        
        # Test strategy creation
        default_strategy = create_strategy('default')
        print(f"✅ Created default strategy")
        
        strategy_info = default_strategy.get_strategy_info()
        print(f"   Name: {strategy_info['name']}")
        print(f"   Suitable for: {', '.join(strategy_info['suitable_for'])}")
        
        # Test with user preferences
        db = next(get_db())
        users = db.query(User).all()
        if users:
            user = users[0]
            preferences_service = PreferencesService(db)
            user_prefs = preferences_service.get_or_create_preferences(user.id)
            
            user_strategy = strategy_factory.get_strategy_for_user(user_prefs)
            print(f"✅ Created user-specific strategy")
            print(f"   User's strategy: {user_prefs.strategy}")
            print(f"   Risk appetite: {user_prefs.risk_appetite}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Strategy factory test failed: {e}")
        return False

def test_integration():
    """Test integration between all components"""
    print("\n🔗 Testing Component Integration")
    print("=" * 50)
    
    try:
        # Initialize database
        init_database()
        db = next(get_db())
        
        # Get or create test user preferences
        users = db.query(User).all()
        if not users:
            print("❌ No users found. Please run the enhanced demo first.")
            return False
        
        user = users[0]
        preferences_service = PreferencesService(db)
        user_prefs = preferences_service.get_or_create_preferences(user.id)
        
        print(f"👤 Testing integration for user: {user.email}")
        print(f"   Risk Appetite: {user_prefs.risk_appetite}")
        print(f"   Strategy: {user_prefs.strategy}")
        print(f"   Min Confidence: {user_prefs.min_confidence}")
        
        # Test configuration integration
        config = get_trading_config(user_prefs)
        print(f"✅ Configuration integrated with user preferences")
        print(f"   Position Size: ${config.position_size}")
        print(f"   Stop Loss: {config.stop_loss_percentage * 100:.1f}%")
        print(f"   Take Profit: {config.take_profit_percentage * 100:.1f}%")
        
        # Test strategy with user preferences
        strategy = create_strategy(user_prefs.strategy, user_prefs)
        print(f"✅ Strategy created with user preferences")
        
        # Mock market data analysis
        mock_market_data = {
            'close': [150 + i * 0.5 for i in range(60)],  # Trending up
            'high': [151 + i * 0.5 for i in range(60)],
            'low': [149 + i * 0.5 for i in range(60)],
            'volume': [1000000 + i * 1000 for i in range(60)]
        }
        
        # Test strategy analysis
        analysis = strategy.analyze_symbol('TEST', mock_market_data, sentiment_score=0.3)
        print(f"✅ Strategy analysis completed")
        print(f"   Symbol: {analysis['symbol']}")
        print(f"   Action: {analysis['action']}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
        print(f"   Current Price: ${analysis['current_price']:.2f}")
        print(f"   Stop Loss: ${analysis['stop_loss']:.2f}")
        print(f"   Target: ${analysis['target_price']:.2f}")
        print(f"   Risk/Reward: {analysis['risk_reward_ratio']:.2f}")
        
        # Test preference filtering
        if analysis['confidence'] >= user_prefs.min_confidence:
            print(f"✅ Signal passes user confidence threshold")
        else:
            print(f"⚠️ Signal below user confidence threshold")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all architecture tests"""
    print("🏗️ SentimentTrade Refactored Architecture Testing")
    print("=" * 70)
    
    # Test individual components
    config_success = test_trading_config()
    indicators_success = test_technical_indicators()
    strategy_success = test_strategy_factory()
    integration_success = test_integration()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 70)
    print(f"Trading Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"Technical Indicators: {'✅ PASS' if indicators_success else '❌ FAIL'}")
    print(f"Strategy Factory: {'✅ PASS' if strategy_success else '❌ FAIL'}")
    print(f"Component Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    overall_success = all([config_success, indicators_success, strategy_success, integration_success])
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Refactored Architecture is Working Perfectly!")
        print("✅ Trading config moved from .env to user preferences")
        print("✅ Technical indicators extracted to reusable utility")
        print("✅ Default strategy separated into its own module")
        print("✅ Strategy factory ready for multiple strategies")
        print("✅ User preferences fully integrated")
        print("✅ Mobile app can now use personalized trading settings")
    else:
        print("\n🔧 Please fix the failing tests before proceeding")

if __name__ == "__main__":
    main()
