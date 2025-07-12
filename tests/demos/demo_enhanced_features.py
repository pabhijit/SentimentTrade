#!/usr/bin/env python3
"""
Demo script for Enhanced SentimentTrade API
Demonstrates the new features that match your product specification
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def demo_user_registration():
    """Demo user registration"""
    print("👤 User Registration Demo")
    print("-" * 30)
    
    user_data = {
        "email": "demo@sentimenttrade.com",
        "password": "DemoPassword123",
        "full_name": "Demo User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User registered successfully!")
            print(f"   Email: {result['user']['email']}")
            print(f"   Name: {result['user']['full_name']}")
            print(f"   Token: {result['tokens']['access_token'][:20]}...")
            return result['tokens']['access_token']
        else:
            print(f"⚠️  Registration response: {response.status_code}")
            if "already registered" in response.text:
                print("   User already exists, trying login...")
                return demo_user_login()
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Please start the server: cd api && python main_enhanced.py")
        return None
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return None

def demo_user_login():
    """Demo user login"""
    print("\n🔐 User Login Demo")
    print("-" * 30)
    
    login_data = {
        "email": "demo@sentimenttrade.com",
        "password": "DemoPassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User logged in successfully!")
            print(f"   Welcome back: {result['user']['full_name']}")
            return result['tokens']['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def demo_watchlist_management(token):
    """Demo watchlist management"""
    print("\n📋 Watchlist Management Demo")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add symbols to watchlist
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in symbols:
        watchlist_data = {
            "symbol": symbol,
            "signal_preferences": {
                "rsi_threshold": 30,
                "confidence_min": 0.7
            },
            "notes": f"Watching {symbol} for swing trading opportunities"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/watchlist", json=watchlist_data, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Added {symbol} to watchlist")
            elif response.status_code == 400 and "already in watchlist" in response.text:
                print(f"⚠️  {symbol} already in watchlist")
            else:
                print(f"❌ Failed to add {symbol}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error adding {symbol}: {e}")
    
    # Get watchlist
    try:
        response = requests.get(f"{BASE_URL}/watchlist", headers=headers)
        
        if response.status_code == 200:
            watchlist = response.json()
            print(f"\n📊 Current Watchlist ({len(watchlist)} symbols):")
            for item in watchlist:
                print(f"   • {item['symbol']} - {item['notes'][:50]}...")
        else:
            print(f"❌ Failed to get watchlist: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting watchlist: {e}")

def demo_signal_generation(token):
    """Demo enhanced signal generation"""
    print("\n📈 Enhanced Signal Generation Demo")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Generate signals for watchlist symbols
    symbols = ["AAPL", "MSFT"]
    signals = []
    
    for symbol in symbols:
        signal_data = {
            "symbol": symbol,
            "include_indicators": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/signal", json=signal_data, headers=headers)
            
            if response.status_code == 200:
                signal = response.json()
                signals.append(signal)
                
                print(f"✅ Signal for {symbol}:")
                print(f"   Recommendation: {signal['recommendation']}")
                print(f"   Confidence: {signal['confidence']:.1%}")
                print(f"   Current Price: ${signal['current_price']:.2f}")
                
                if signal.get('error'):
                    print(f"   ⚠️  Note: {signal['error']}")
                    
            else:
                print(f"❌ Failed to get signal for {symbol}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting signal for {symbol}: {e}")
    
    return signals

def demo_trade_confirmation(token, signals):
    """Demo trade confirmation tracking"""
    print("\n✅ Trade Confirmation Demo")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Confirm trades for generated signals
    for signal in signals:
        if not signal.get('id'):
            continue
            
        # Simulate trade execution decision
        executed = signal['recommendation'] != 'HOLD'
        
        confirmation_data = {
            "signal_id": signal['id'],
            "executed": executed,
            "execution_price": signal['current_price'] * (1.001 if executed else 1),  # Slight slippage
            "quantity": 10 if executed else None,
            "notes": f"{'Executed' if executed else 'Skipped'} {signal['recommendation']} signal for {signal['symbol']}",
            "user_rating": 4 if executed else 3
        }
        
        try:
            response = requests.post(f"{BASE_URL}/trade-confirmation", json=confirmation_data, headers=headers)
            
            if response.status_code == 200:
                confirmation = response.json()
                print(f"✅ Trade confirmation for {signal['symbol']}:")
                print(f"   Executed: {confirmation['executed']}")
                if confirmation['executed']:
                    print(f"   Execution Price: ${confirmation['execution_price']:.2f}")
                    print(f"   Quantity: {confirmation['quantity']}")
                    if confirmation['pnl']:
                        print(f"   P&L: ${confirmation['pnl']:.2f}")
            else:
                print(f"❌ Failed to confirm trade for {signal['symbol']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error confirming trade for {signal['symbol']}: {e}")

def demo_dashboard(token):
    """Demo performance dashboard"""
    print("\n📊 Performance Dashboard Demo")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            
            print("✅ Dashboard Statistics:")
            print(f"   Total Signals: {stats['total_signals']}")
            print(f"   Executed Trades: {stats['executed_trades']}")
            print(f"   Win Rate: {stats['win_rate']:.1f}%")
            print(f"   Total P&L: ${stats['total_pnl']:.2f}")
            print(f"   Avg Confidence: {stats['avg_confidence']:.1%}")
            
            if stats['best_performing_symbol']:
                print(f"   Best Symbol: {stats['best_performing_symbol']}")
            
            if stats['recent_activity']:
                print(f"\n📈 Recent Activity:")
                for activity in stats['recent_activity'][:3]:
                    print(f"   • {activity['symbol']} - {activity['recommendation']} ({'Executed' if activity['executed'] else 'Skipped'})")
                    
        else:
            print(f"❌ Failed to get dashboard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting dashboard: {e}")

def demo_api_health():
    """Demo API health check"""
    print("\n🏥 API Health Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Status: {health['status']}")
            print(f"   Version: {health['version']}")
            print(f"   Features: {', '.join([k for k, v in health['features'].items() if v])}")
            
            if not health['config_valid']:
                print(f"   ⚠️  Missing API keys: {', '.join(health['missing_keys'])}")
            else:
                print("   ✅ All API keys configured")
                
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Please start the server: cd api && python main_enhanced.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    return True

def main():
    """Run complete enhanced API demo"""
    print("🚀 SentimentTrade Enhanced API Demo")
    print("Showcasing features from your product specification")
    print("=" * 60)
    
    # Check API health first
    if not demo_api_health():
        print("\n❌ API server is not running. Please start it first:")
        print("   cd api && python main_enhanced.py")
        return
    
    # Demo user authentication
    token = demo_user_registration()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Demo all features
    demo_watchlist_management(token)
    signals = demo_signal_generation(token)
    demo_trade_confirmation(token, signals)
    demo_dashboard(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED!")
    print("=" * 60)
    print("✅ Features Demonstrated:")
    print("   • User Registration & Authentication")
    print("   • Watchlist Management (CRUD)")
    print("   • Enhanced Signal Generation")
    print("   • Trade Confirmation & Tracking")
    print("   • Performance Dashboard")
    print("   • Real-time API Health Monitoring")
    
    print(f"\n📱 Your Product Spec Implementation Status:")
    print("   ✅ AI-powered trading signals")
    print("   ✅ User authentication (JWT)")
    print("   ✅ Watchlist CRUD operations")
    print("   ✅ Real-time signal polling")
    print("   ✅ Trade confirmation tracking")
    print("   ✅ Performance dashboard")
    print("   ✅ FastAPI backend")
    print("   ✅ Database integration")
    
    print(f"\n🔗 Next Steps:")
    print("   • Add Telegram integration")
    print("   • Build web/mobile frontend")
    print("   • Add more AI sentiment sources")
    print("   • Implement trading journal")
    print("   • Add admin tools")
    
    print(f"\n📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
