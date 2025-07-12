#!/usr/bin/env python3
"""
Test script for user preferences functionality
Tests the new preferences endpoints and database models
"""

import sys
import os
from pathlib import Path
import requests
import json
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from database import init_database, get_db, User, UserPreferences
from auth import AuthService
from preferences_service import PreferencesService

def test_database_setup():
    """Test database setup with preferences table"""
    print("🗄️ Testing Database Setup with Preferences")
    print("=" * 50)
    
    try:
        # Initialize database (creates tables)
        init_database()
        
        # Test database connection
        db = next(get_db())
        
        # Check if preferences table exists
        user_count = db.query(User).count()
        preferences_count = db.query(UserPreferences).count()
        
        print(f"✅ Users: {user_count}")
        print(f"✅ User Preferences: {preferences_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_preferences_service():
    """Test preferences service functionality"""
    print("\n🔧 Testing Preferences Service")
    print("=" * 50)
    
    try:
        db = next(get_db())
        preferences_service = PreferencesService(db)
        
        # Test creating default preferences for a mock user
        test_user_id = 999  # Mock user ID
        
        # Test get_or_create_preferences
        preferences = preferences_service.get_or_create_preferences(test_user_id)
        print(f"✅ Created default preferences for user {test_user_id}")
        print(f"   Strategy: {preferences.strategy}")
        print(f"   Risk Appetite: {preferences.risk_appetite}")
        print(f"   Min Confidence: {preferences.min_confidence}")
        
        # Test available strategies
        strategies = preferences_service.get_available_strategies()
        print(f"✅ Available strategies: {len(strategies)}")
        for strategy in strategies:
            status = "✅" if strategy.available else "🚧"
            print(f"   {status} {strategy.display_name} ({strategy.name})")
        
        # Test risk profiles
        risk_profiles = preferences_service.get_risk_profiles()
        print(f"✅ Risk profiles: {len(risk_profiles)}")
        for profile in risk_profiles:
            print(f"   📊 {profile.display_name}: {profile.recommended_confidence*100:.0f}% confidence")
        
        # Test preferences summary
        summary = preferences_service.get_preferences_summary(test_user_id)
        print(f"✅ Preferences summary generated")
        print(f"   Current Strategy: {summary['current_strategy'].display_name if summary['current_strategy'] else 'None'}")
        print(f"   Current Risk Profile: {summary['current_risk_profile'].display_name if summary['current_risk_profile'] else 'None'}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Preferences service test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data['status']}")
            print(f"   Preferences feature: {health_data['features'].get('preferences', False)}")
        else:
            print("❌ Health check failed")
            return False
        
        # Test registration and login to get token
        test_email = f"test_preferences_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        test_password = "testpassword123"
        
        # Register test user
        register_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data["access_token"]
            print(f"✅ Test user registered: {test_email}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
        
        # Set up headers with token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test get preferences (should create default)
        response = requests.get(f"{base_url}/user/preferences", headers=headers)
        if response.status_code == 200:
            preferences = response.json()
            print(f"✅ Retrieved preferences")
            print(f"   Strategy: {preferences['strategy']}")
            print(f"   Risk Appetite: {preferences['risk_appetite']}")
            print(f"   Min Confidence: {preferences['min_confidence']}")
        else:
            print(f"❌ Get preferences failed: {response.text}")
            return False
        
        # Test update preferences
        update_data = {
            "risk_appetite": "high",
            "min_confidence": 0.6,
            "max_daily_signals": 20
        }
        
        response = requests.put(f"{base_url}/user/preferences", json=update_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Updated preferences: {result['message']}")
            updated_prefs = result['preferences']
            print(f"   New Risk Appetite: {updated_prefs['risk_appetite']}")
            print(f"   New Min Confidence: {updated_prefs['min_confidence']}")
        else:
            print(f"❌ Update preferences failed: {response.text}")
            return False
        
        # Test get available strategies
        response = requests.get(f"{base_url}/user/preferences/strategies", headers=headers)
        if response.status_code == 200:
            strategies_data = response.json()
            print(f"✅ Retrieved strategies")
            print(f"   Current: {strategies_data['current_strategy']}")
            print(f"   Available: {len(strategies_data['strategies'])} strategies")
        else:
            print(f"❌ Get strategies failed: {response.text}")
            return False
        
        # Test get risk profiles
        response = requests.get(f"{base_url}/user/preferences/risk-profiles", headers=headers)
        if response.status_code == 200:
            risk_data = response.json()
            print(f"✅ Retrieved risk profiles")
            print(f"   Current: {risk_data['current_risk_appetite']}")
            print(f"   Available: {len(risk_data['risk_profiles'])} profiles")
        else:
            print(f"❌ Get risk profiles failed: {response.text}")
            return False
        
        # Test preferences summary
        response = requests.get(f"{base_url}/user/preferences/summary", headers=headers)
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Retrieved preferences summary")
            print(f"   Strategy: {summary['current_strategy']['display_name'] if summary['current_strategy'] else 'None'}")
            print(f"   Risk Profile: {summary['current_risk_profile']['display_name'] if summary['current_risk_profile'] else 'None'}")
        else:
            print(f"❌ Get preferences summary failed: {response.text}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   Make sure the server is running: python api/main_enhanced.py")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all preference tests"""
    print("🧪 SentimentTrade Preferences Testing")
    print("=" * 60)
    
    # Test database setup
    db_success = test_database_setup()
    
    # Test preferences service
    service_success = test_preferences_service()
    
    # Test API endpoints (optional - requires running server)
    print("\n⚠️  API endpoint tests require the server to be running")
    print("   Start server with: python api/main_enhanced.py")
    
    try_api = input("\nTest API endpoints? (y/n): ").lower().strip() == 'y'
    api_success = True
    
    if try_api:
        api_success = test_api_endpoints()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    print(f"Database Setup: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"Preferences Service: {'✅ PASS' if service_success else '❌ FAIL'}")
    if try_api:
        print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    overall_success = db_success and service_success and api_success
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 User preferences functionality is ready!")
        print("📱 Mobile app can now use the preferences endpoints")
    else:
        print("\n🔧 Please fix the failing tests before proceeding")

if __name__ == "__main__":
    main()
