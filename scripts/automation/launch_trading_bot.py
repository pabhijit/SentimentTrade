#!/usr/bin/env python3
"""
SentimentTrade Bot Launcher
Easy-to-use launcher for the daily trading strategy runner
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("🚀 SENTIMENTTRADE AUTOMATED TRADING BOT")
    print("=" * 70)
    print("📊 Strategies: Break & Retest + Options Trading")
    print("⏰ Schedule: Every 30 minutes during market hours")
    print("📱 Alerts: Telegram notifications enabled")
    print("=" * 70)
    print()

def check_requirements():
    """Check if system is properly configured"""
    issues = []
    
    # Check .env file
    env_file = project_root / '.env'
    if not env_file.exists():
        issues.append("❌ .env file not found. Run setup_telegram.py first.")
    else:
        # Check for required variables
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
        for var in required_vars:
            if f'{var}=' not in content:
                issues.append(f"❌ {var} not found in .env file")
    
    # Check Python packages
    try:
        import schedule
        import yfinance
        import pandas
        import numpy
    except ImportError as e:
        issues.append(f"❌ Missing Python package: {e}")
    
    # Check data directory
    data_dir = project_root / 'data'
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print("📁 Created data directory")
    
    # Check results directory
    results_dir = project_root / 'results' / 'daily_runs'
    if not results_dir.exists():
        results_dir.mkdir(parents=True, exist_ok=True)
        print("📁 Created results directory")
    
    return issues

def show_configuration():
    """Show current configuration"""
    try:
        from runner_config import (
            get_active_strategies, 
            get_all_symbols, 
            TIMING_CONFIG, 
            ALERT_CONFIG
        )
        
        print("📋 CURRENT CONFIGURATION:")
        print("-" * 30)
        
        # Strategies
        strategies = get_active_strategies()
        print(f"🎯 Active Strategies: {len(strategies)}")
        for name, config in strategies.items():
            print(f"   • {config['description']}: {len(config['symbols'])} symbols")
        
        # Symbols
        all_symbols = get_all_symbols()
        print(f"📈 Total Symbols: {len(all_symbols)}")
        print(f"   {', '.join(all_symbols[:10])}" + ("..." if len(all_symbols) > 10 else ""))
        
        # Timing
        print(f"⏰ Run Interval: Every {TIMING_CONFIG['run_interval_minutes']} minutes")
        print(f"🕘 Market Hours: {TIMING_CONFIG['market_open']} - {TIMING_CONFIG['market_close']} ET")
        
        # Alerts
        print(f"📱 Telegram Alerts: {'Enabled' if ALERT_CONFIG['telegram_enabled'] else 'Disabled'}")
        print(f"🎯 Alert Threshold: {ALERT_CONFIG['min_confidence_for_alert']:.0%}")
        
        print()
        
    except Exception as e:
        print(f"⚠️ Could not load configuration: {e}")

def test_telegram():
    """Test Telegram connection"""
    try:
        from telegram_alerts import test_telegram
        
        print("📱 Testing Telegram connection...")
        if test_telegram():
            print("✅ Telegram connection successful!")
            return True
        else:
            print("❌ Telegram connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Telegram test error: {e}")
        return False

def start_bot():
    """Start the trading bot"""
    print("🚀 Starting SentimentTrade Bot...")
    print("📊 The bot will run every 30 minutes during market hours")
    print("📱 You'll receive Telegram alerts for trading signals")
    print()
    print("Press Ctrl+C to stop the bot")
    print("=" * 50)
    print()
    
    try:
        # Import and run the daily runner
        from daily_strategy_runner import main as run_daily_runner
        run_daily_runner()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        raise

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n🤖 SENTIMENTTRADE BOT MENU")
        print("-" * 30)
        print("1. 🚀 Start Trading Bot")
        print("2. 📋 Show Configuration")
        print("3. 📱 Test Telegram")
        print("4. ⚙️ Setup Telegram Bot")
        print("5. 📊 View Recent Results")
        print("6. 🔧 Install Requirements")
        print("0. 👋 Exit")
        print()
        
        choice = input("Select option (0-6): ").strip()
        
        if choice == '1':
            start_bot()
        elif choice == '2':
            show_configuration()
        elif choice == '3':
            test_telegram()
        elif choice == '4':
            print("🔧 Running Telegram setup...")
            try:
                subprocess.run([sys.executable, 'setup_telegram.py'], check=True)
            except subprocess.CalledProcessError:
                print("❌ Setup failed")
        elif choice == '5':
            show_recent_results()
        elif choice == '6':
            install_requirements()
        elif choice == '0':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

def show_recent_results():
    """Show recent trading results"""
    try:
        results_dir = project_root / 'results' / 'daily_runs'
        
        if not results_dir.exists():
            print("📊 No results found yet. Run the bot first!")
            return
        
        # Get recent result files
        result_files = sorted(results_dir.glob('strategy_run_*.json'), reverse=True)[:5]
        
        if not result_files:
            print("📊 No results found yet. Run the bot first!")
            return
        
        print("📊 RECENT TRADING RESULTS:")
        print("-" * 40)
        
        for file in result_files:
            try:
                import json
                with open(file, 'r') as f:
                    data = json.load(f)
                
                timestamp = data.get('timestamp', 'Unknown')
                total_signals = data.get('total_signals', 0)
                actionable = data.get('actionable_signals', 0)
                
                print(f"📅 {timestamp[:19]}: {total_signals} signals ({actionable} actionable)")
                
            except Exception as e:
                print(f"❌ Error reading {file.name}: {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error showing results: {e}")

def install_requirements():
    """Install required Python packages"""
    print("🔧 Installing required packages...")
    
    requirements = [
        'schedule',
        'yfinance',
        'pandas',
        'numpy',
        'python-telegram-bot',
        'requests',
        'pytz'
    ]
    
    for package in requirements:
        try:
            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check system requirements
    issues = check_requirements()
    
    if issues:
        print("⚠️ CONFIGURATION ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print()
        print("Please fix these issues before starting the bot.")
        print("Run option 4 to setup Telegram or option 6 to install requirements.")
        print()
    else:
        print("✅ System configuration looks good!")
        print()
    
    # Show current configuration
    show_configuration()
    
    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--start':
        # Direct start mode
        if issues:
            print("❌ Cannot start bot due to configuration issues.")
            sys.exit(1)
        start_bot()
    else:
        # Interactive menu mode
        show_menu()

if __name__ == "__main__":
    main()
