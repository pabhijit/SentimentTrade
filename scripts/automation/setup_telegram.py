#!/usr/bin/env python3
"""
Telegram Bot Setup for SentimentTrade Daily Runner
Helps you create and configure a Telegram bot for trading alerts
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🤖 TELEGRAM BOT SETUP - SENTIMENTTRADE")
    print("=" * 60)
    print()

def print_step(step_num: int, title: str):
    """Print step header"""
    print(f"\n📋 STEP {step_num}: {title}")
    print("-" * 40)

def create_telegram_bot_guide():
    """Show guide for creating Telegram bot"""
    print_step(1, "CREATE TELEGRAM BOT")
    
    print("To create a Telegram bot, follow these steps:")
    print()
    print("1. Open Telegram and search for '@BotFather'")
    print("2. Start a chat with BotFather")
    print("3. Send the command: /newbot")
    print("4. Choose a name for your bot (e.g., 'SentimentTrade Alerts')")
    print("5. Choose a username for your bot (must end with 'bot', e.g., 'sentimenttrade_alerts_bot')")
    print("6. BotFather will give you a TOKEN - copy this!")
    print()
    print("Example token format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    print()
    
    token = input("📝 Enter your bot TOKEN: ").strip()
    
    if not token or ':' not in token:
        print("❌ Invalid token format. Please try again.")
        return None
    
    return token

def get_chat_id(token: str) -> Optional[str]:
    """Get chat ID by having user send a message"""
    print_step(2, "GET CHAT ID")
    
    print("Now we need to get your Chat ID:")
    print()
    print("1. Search for your bot in Telegram using the username you created")
    print("2. Start a chat with your bot")
    print("3. Send any message to your bot (e.g., 'Hello')")
    print("4. Press Enter here after sending the message")
    
    input("Press Enter after sending a message to your bot...")
    
    try:
        # Get updates from Telegram
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Telegram API error: {data.get('description', 'Unknown error')}")
            return None
        
        updates = data.get('result', [])
        
        if not updates:
            print("❌ No messages found. Please send a message to your bot and try again.")
            return None
        
        # Get the most recent chat ID
        latest_update = updates[-1]
        chat_id = str(latest_update['message']['chat']['id'])
        
        print(f"✅ Found Chat ID: {chat_id}")
        return chat_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return None

def test_telegram_connection(token: str, chat_id: str) -> bool:
    """Test the Telegram bot connection"""
    print_step(3, "TEST CONNECTION")
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': '🎉 SentimentTrade Bot Setup Complete!\n\nYour trading alerts are now configured.',
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ok'):
            print("✅ Test message sent successfully!")
            print("Check your Telegram to see the test message.")
            return True
        else:
            print(f"❌ Failed to send test message: {data.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_env_file(token: str, chat_id: str):
    """Create or update .env file with Telegram credentials"""
    print_step(4, "SAVE CONFIGURATION")
    
    env_file = project_root / '.env'
    env_template = project_root / '.env.template'
    
    # Read existing .env or template
    env_content = {}
    
    if env_file.exists():
        print("📝 Updating existing .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
    elif env_template.exists():
        print("📝 Creating .env file from template...")
        with open(env_template, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()
    
    # Update Telegram settings
    env_content['TELEGRAM_TOKEN'] = token
    env_content['TELEGRAM_CHAT_ID'] = chat_id
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write("# SentimentTrade Environment Configuration\n")
        f.write("# Generated by setup_telegram.py\n\n")
        
        # Telegram settings first
        f.write("# Telegram Bot Configuration\n")
        f.write(f"TELEGRAM_TOKEN={token}\n")
        f.write(f"TELEGRAM_CHAT_ID={chat_id}\n\n")
        
        # Other settings
        f.write("# API Keys (add your own)\n")
        for key, value in env_content.items():
            if key not in ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']:
                f.write(f"{key}={value}\n")
    
    print(f"✅ Configuration saved to {env_file}")
    print()
    print("🔐 IMPORTANT: Keep your .env file secure and never commit it to version control!")

def show_next_steps():
    """Show what to do next"""
    print_step(5, "NEXT STEPS")
    
    print("Your Telegram bot is now configured! Here's what to do next:")
    print()
    print("1. 🔑 Add your API keys to the .env file:")
    print("   - TWELVE_DATA_API_KEY (for market data)")
    print("   - OPENAI_API_KEY (for sentiment analysis)")
    print()
    print("2. 🚀 Start the daily runner:")
    print("   cd scripts/automation")
    print("   python daily_strategy_runner.py")
    print()
    print("3. 📱 You'll receive alerts for:")
    print("   - Break & Retest signals on your watchlist")
    print("   - Options signals on QQQ")
    print("   - Daily summaries")
    print("   - System status updates")
    print()
    print("4. 📊 Monitor results in the results/daily_runs/ folder")
    print()
    print("5. ⚙️ Customize settings in runner_config.py")
    print()
    print("🎯 The system will run every 30 minutes during market hours!")

def main():
    """Main setup function"""
    print_header()
    
    print("This script will help you set up Telegram alerts for your trading bot.")
    print("You'll need to create a Telegram bot and get your chat ID.")
    print()
    
    # Check if already configured
    env_file = project_root / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'TELEGRAM_TOKEN=' in content and 'TELEGRAM_CHAT_ID=' in content:
                print("⚠️  Telegram appears to already be configured.")
                reconfigure = input("Do you want to reconfigure? (y/N): ").strip().lower()
                if reconfigure != 'y':
                    print("👋 Setup cancelled.")
                    return
    
    try:
        # Step 1: Create bot and get token
        token = create_telegram_bot_guide()
        if not token:
            return
        
        # Step 2: Get chat ID
        chat_id = get_chat_id(token)
        if not chat_id:
            return
        
        # Step 3: Test connection
        if not test_telegram_connection(token, chat_id):
            print("❌ Setup failed. Please check your token and chat ID.")
            return
        
        # Step 4: Save configuration
        create_env_file(token, chat_id)
        
        # Step 5: Show next steps
        show_next_steps()
        
        print("\n🎉 Telegram bot setup completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")

if __name__ == "__main__":
    main()
