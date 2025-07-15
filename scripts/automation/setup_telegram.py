#!/usr/bin/env python3
"""
Unified Telegram Setup for SentimentTrade
Interactive setup for Telegram bot configuration
"""

import os
import sys
import time
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("📱 SENTIMENTTRADE TELEGRAM SETUP")
    print("=" * 70)
    print("This script will help you set up Telegram notifications")
    print("for your SentimentTrade automated trading system.")
    print("=" * 70)
    print()

def check_existing_config() -> Tuple[bool, Dict[str, str]]:
    """Check for existing Telegram configuration"""
    env_file = project_root / '.env'
    config = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        config[key] = value
                    except ValueError:
                        pass
    
    has_telegram = 'TELEGRAM_TOKEN' in config and 'TELEGRAM_CHAT_ID' in config
    return has_telegram, config

def get_bot_token() -> str:
    """Get Telegram bot token from user"""
    print("📝 TELEGRAM BOT TOKEN")
    print("-" * 30)
    print("To get a bot token, you need to create a bot with @BotFather on Telegram:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Start a chat and send /newbot")
    print("3. Follow the instructions to create a bot")
    print("4. Copy the API token provided by BotFather")
    print()
    
    token = input("Enter your Telegram bot token: ").strip()
    
    while not token or not token.count(':') == 1:
        print("❌ Invalid token format. It should look like: 123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ")
        token = input("Enter your Telegram bot token: ").strip()
    
    return token

def get_chat_id(token: str) -> str:
    """Get chat ID interactively"""
    print("\n📝 TELEGRAM CHAT ID")
    print("-" * 30)
    print("To get your chat ID, you need to send a message to your bot:")
    print("1. Open Telegram and search for your bot")
    print("2. Start a chat and send any message (e.g., /start)")
    print()
    
    input("Press Enter after you've sent a message to your bot...")
    
    # Try to get updates from the bot
    try:
        print("\n🔍 Checking for messages...")
        response = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Error from Telegram API: {data.get('description', 'Unknown error')}")
            return manual_chat_id()
        
        updates = data.get('result', [])
        if not updates:
            print("❌ No messages found. Make sure you've sent a message to your bot.")
            return manual_chat_id()
        
        # Get the most recent chat ID
        chat_id = str(updates[-1]['message']['chat']['id'])
        print(f"✅ Found chat ID: {chat_id}")
        return chat_id
        
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return manual_chat_id()

def manual_chat_id() -> str:
    """Get chat ID manually from user"""
    print("\n📝 MANUAL CHAT ID ENTRY")
    print("-" * 30)
    print("You'll need to enter your chat ID manually.")
    print("If you don't know your chat ID, you can use @userinfobot on Telegram.")
    print()
    
    chat_id = input("Enter your Telegram chat ID: ").strip()
    
    while not chat_id or not chat_id.lstrip('-').isdigit():
        print("❌ Invalid chat ID format. It should be a number like 123456789.")
        chat_id = input("Enter your Telegram chat ID: ").strip()
    
    return chat_id

def test_telegram_connection(token: str, chat_id: str) -> bool:
    """Test Telegram connection by sending a test message"""
    print("\n🧪 TESTING TELEGRAM CONNECTION")
    print("-" * 30)
    print("Sending a test message to your Telegram...")
    
    try:
        message = "🚀 SentimentTrade Bot Test\n\nIf you're seeing this message, your Telegram notifications are working correctly!"
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
        )
        
        data = response.json()
        if data.get('ok'):
            print("✅ Test message sent successfully!")
            return True
        else:
            print(f"❌ Error sending test message: {data.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Telegram connection: {e}")
        return False

def save_config(config: Dict[str, str]) -> bool:
    """Save configuration to .env file"""
    print("\n💾 SAVING CONFIGURATION")
    print("-" * 30)
    
    env_file = project_root / '.env'
    
    try:
        # Read existing content if file exists
        existing_content = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            existing_content[key] = value
                        except ValueError:
                            pass
        
        # Update with new config
        existing_content.update(config)
        
        # Write back to file
        with open(env_file, 'w') as f:
            for key, value in existing_content.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Configuration saved to {env_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def setup_telegram() -> bool:
    """Run the Telegram setup process"""
    print_banner()
    
    # Check for existing configuration
    has_telegram, existing_config = check_existing_config()
    
    if has_telegram:
        print("📱 EXISTING TELEGRAM CONFIGURATION FOUND")
        print("-" * 40)
        print(f"Bot Token: {'*' * 10}{existing_config['TELEGRAM_TOKEN'][-5:]}")
        print(f"Chat ID: {existing_config['TELEGRAM_CHAT_ID']}")
        print()
        
        choice = input("Do you want to keep this configuration? (y/n): ").strip().lower()
        if choice == 'y':
            # Test existing configuration
            print("\nTesting existing configuration...")
            if test_telegram_connection(
                existing_config['TELEGRAM_TOKEN'],
                existing_config['TELEGRAM_CHAT_ID']
            ):
                print("\n✅ Existing configuration is working correctly!")
                return True
            else:
                print("\n⚠️ Existing configuration is not working. Let's set it up again.")
        else:
            print("\nLet's set up a new configuration.")
    
    # Get bot token
    token = get_bot_token()
    
    # Get chat ID
    chat_id = get_chat_id(token)
    
    # Test connection
    if not test_telegram_connection(token, chat_id):
        print("\n⚠️ Telegram test failed. Let's try again.")
        retry = input("Do you want to retry setup? (y/n): ").strip().lower()
        if retry == 'y':
            return setup_telegram()
        return False
    
    # Save configuration
    config = {
        'TELEGRAM_TOKEN': token,
        'TELEGRAM_CHAT_ID': chat_id
    }
    
    if save_config(config):
        print("\n🎉 TELEGRAM SETUP COMPLETE!")
        print("-" * 30)
        print("Your SentimentTrade bot is now configured to send")
        print("Telegram notifications for trading signals.")
        print()
        print("You can start the bot with:")
        print("python unified_launcher.py")
        return True
    else:
        print("\n❌ Failed to save configuration.")
        return False

def main():
    """Main entry point"""
    try:
        setup_telegram()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")

if __name__ == "__main__":
    main()
