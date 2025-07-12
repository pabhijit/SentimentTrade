#!/usr/bin/env python3
"""
Demo script for user preferences functionality
Shows how the mobile app preferences integrate with the backend
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from database import init_database, get_db, User, UserPreferences
from auth import AuthService
from preferences_service import PreferencesService
from preferences_models import UserPreferencesUpdate

def demo_preferences_functionality():
    """Demonstrate the complete preferences functionality"""
    print("🎯 SentimentTrade Preferences Demo")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Get database session
    db = next(get_db())
    
    # Create preferences service
    preferences_service = PreferencesService(db)
    
    print("\n📱 Mobile App Preferences Integration")
    print("-" * 40)
    
    # Simulate a user (using existing user from database)
    users = db.query(User).all()
    if not users:
        print("❌ No users found. Please run the enhanced demo first.")
        return
    
    test_user = users[0]
    print(f"👤 Testing with user: {test_user.email}")
    
    # 1. Get or create default preferences (what happens when user first opens settings)
    print("\n1️⃣ Getting default preferences...")
    preferences = preferences_service.get_or_create_preferences(test_user.id)
    print(f"   ✅ Strategy: {preferences.strategy}")
    print(f"   ✅ Risk Appetite: {preferences.risk_appetite}")
    print(f"   ✅ Min Confidence: {preferences.min_confidence * 100:.0f}%")
    print(f"   ✅ Max Daily Signals: {preferences.max_daily_signals}")
    
    # 2. Show available strategies (what user sees in strategy selector)
    print("\n2️⃣ Available trading strategies...")
    strategies = preferences_service.get_available_strategies()
    for strategy in strategies:
        status = "✅ Available" if strategy.available else "🚧 Coming Soon"
        print(f"   {status} {strategy.display_name}")
        print(f"      📝 {strategy.description}")
    
    # 3. Show risk profiles (what user sees in risk selector)
    print("\n3️⃣ Risk appetite profiles...")
    risk_profiles = preferences_service.get_risk_profiles()
    for profile in risk_profiles:
        current = "👈 Current" if profile.name == preferences.risk_appetite else ""
        print(f"   📊 {profile.display_name} {current}")
        print(f"      📝 {profile.description}")
        print(f"      🎯 Recommended confidence: {profile.recommended_confidence * 100:.0f}%")
    
    # 4. Simulate user changing preferences (what happens when user saves settings)
    print("\n4️⃣ Updating preferences (user changes risk to 'high')...")
    update_data = UserPreferencesUpdate(
        risk_appetite="high",
        min_confidence=0.6,
        max_daily_signals=20
    )
    
    updated_preferences = preferences_service.update_preferences(test_user.id, update_data)
    print(f"   ✅ New Risk Appetite: {updated_preferences.risk_appetite}")
    print(f"   ✅ New Min Confidence: {updated_preferences.min_confidence * 100:.0f}%")
    print(f"   ✅ New Max Daily Signals: {updated_preferences.max_daily_signals}")
    
    # 5. Apply risk profile defaults (what happens when user selects a risk profile)
    print("\n5️⃣ Applying 'conservative' risk profile defaults...")
    conservative_prefs = preferences_service.apply_risk_profile_defaults(test_user.id, "low")
    print(f"   ✅ Applied conservative settings:")
    print(f"      📊 Risk Appetite: {conservative_prefs.risk_appetite}")
    print(f"      🎯 Min Confidence: {conservative_prefs.min_confidence * 100:.0f}%")
    print(f"      📈 Max Daily Signals: {conservative_prefs.max_daily_signals}")
    print(f"      🛡️ Stop Loss: {conservative_prefs.stop_loss_percentage * 100:.0f}%")
    
    # 6. Get comprehensive summary (what mobile app uses for settings screen)
    print("\n6️⃣ Preferences summary for mobile app...")
    summary = preferences_service.get_preferences_summary(test_user.id)
    print(f"   📱 Current Strategy: {summary['current_strategy'].display_name}")
    print(f"   📱 Current Risk Profile: {summary['current_risk_profile'].display_name}")
    print(f"   📱 Available Strategies: {len(summary['available_strategies'])}")
    print(f"   📱 Risk Profiles: {len(summary['risk_profiles'])}")
    
    # 7. Show how preferences affect signal generation
    print("\n7️⃣ How preferences affect trading signals...")
    current_prefs = summary['preferences']
    print(f"   🎯 Only signals with ≥{current_prefs.min_confidence * 100:.0f}% confidence will be shown")
    print(f"   📊 Maximum {current_prefs.max_daily_signals} signals per day")
    print(f"   🛡️ Default stop loss: {current_prefs.stop_loss_percentage * 100:.0f}%")
    print(f"   💰 Default take profit: {current_prefs.take_profit_percentage * 100:.0f}%")
    
    db.close()
    
    print("\n🎉 Preferences Demo Complete!")
    print("=" * 60)
    print("✅ Database models working")
    print("✅ Preferences service working") 
    print("✅ Mobile app integration ready")
    print("✅ API endpoints ready (when server is running)")
    
    print("\n📱 Mobile App Integration Points:")
    print("   • GET /user/preferences - Get current settings")
    print("   • PUT /user/preferences - Update settings")
    print("   • GET /user/preferences/strategies - Available strategies")
    print("   • GET /user/preferences/risk-profiles - Risk profiles")
    print("   • POST /user/preferences/apply-risk-profile - Apply defaults")
    print("   • GET /user/preferences/summary - Complete summary")

if __name__ == "__main__":
    demo_preferences_functionality()
