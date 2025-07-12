#!/usr/bin/env python3
"""
Simple test for refactored architecture components
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

def test_basic_functionality():
    """Test basic functionality of refactored components"""
    print("🧪 Testing Refactored Architecture Components")
    print("=" * 60)
    
    try:
        # Test trading config
        from trading_config import get_trading_config
        config = get_trading_config()
        print(f"✅ Trading config: Position size ${config.position_size}")
        
        # Test technical indicators with simple data
        from technical_indicators import TechnicalIndicators
        prices = [100, 101, 102, 101, 103, 104, 103, 105]
        
        rsi = TechnicalIndicators.calculate_rsi(prices, period=5)
        print(f"✅ RSI calculation: {rsi.value:.2f} ({rsi.signal})")
        
        # Test strategy factory
        from strategies.strategy_factory import get_available_strategies
        strategies = get_available_strategies()
        print(f"✅ Available strategies: {len(strategies)}")
        
        # Test user preferences integration
        from database import init_database, get_db, User
        from preferences_service import PreferencesService
        
        init_database()
        db = next(get_db())
        users = db.query(User).all()
        
        if users:
            user = users[0]
            prefs_service = PreferencesService(db)
            prefs = prefs_service.get_or_create_preferences(user.id)
            print(f"✅ User preferences: {prefs.risk_appetite} risk, {prefs.strategy} strategy")
        
        db.close()
        
        print("\n🎉 All basic components working!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_functionality()
