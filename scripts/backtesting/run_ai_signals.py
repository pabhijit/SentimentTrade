#!/usr/bin/env python3
"""
SentimentTrade AI Signal Generator Runner
Independent runner for testing and executing the AI trading signal generator
"""

import sys
import os
from pathlib import Path
import argparse
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import our modules
from ai_trade_signal import TradingSignalGenerator, generate_signal_for_symbol, generate_signals_for_watchlist
from database import init_database, get_db, User, UserPreferences
from preferences_service import PreferencesService
from config import config
from logger import logger

class AISignalRunner:
    """Runner class for the AI signal generator"""
    
    def __init__(self):
        self.generator = None
        self.user_preferences = None
        
    def setup_database(self):
        """Initialize database if needed"""
        try:
            init_database()
            logger.info("✅ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    def load_user_preferences(self, user_email: Optional[str] = None):
        """Load user preferences for personalized signals"""
        try:
            if not user_email:
                # Use default preferences
                self.user_preferences = None
                logger.info("📊 Using default trading configuration")
                return True
            
            db = next(get_db())
            user = db.query(User).filter(User.email == user_email).first()
            
            if not user:
                logger.warning(f"⚠️ User {user_email} not found, using default preferences")
                self.user_preferences = None
                db.close()
                return True
            
            preferences_service = PreferencesService(db)
            self.user_preferences = preferences_service.get_or_create_preferences(user.id)
            
            logger.info(f"✅ Loaded preferences for {user_email}")
            logger.info(f"   Risk Appetite: {self.user_preferences.risk_appetite}")
            logger.info(f"   Strategy: {self.user_preferences.strategy}")
            logger.info(f"   Min Confidence: {self.user_preferences.min_confidence}")
            
            db.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load user preferences: {e}")
            return False
    
    def initialize_generator(self):
        """Initialize the trading signal generator"""
        try:
            self.generator = TradingSignalGenerator(self.user_preferences)
            logger.info("✅ AI Signal Generator initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize signal generator: {e}")
            return False
    
    def test_single_symbol(self, symbol: str) -> Dict[str, Any]:
        """Test signal generation for a single symbol"""
        logger.info(f"🔍 Generating signal for {symbol}")
        
        try:
            signal = self.generator.generate_signal(symbol)
            
            # Display results
            print(f"\n📊 Signal Results for {symbol}")
            print("=" * 50)
            print(f"Action: {signal['action']}")
            print(f"Confidence: {signal['confidence']:.1%}")
            print(f"Current Price: ${signal['current_price']:.2f}")
            print(f"Entry Price: ${signal['entry_price']:.2f}")
            print(f"Stop Loss: ${signal['stop_loss']:.2f}")
            print(f"Target Price: ${signal['target_price']:.2f}")
            print(f"Risk/Reward Ratio: {signal['risk_reward_ratio']:.2f}")
            print(f"Sentiment Score: {signal['sentiment']:.3f}")
            print(f"Strategy: {signal['strategy']}")
            print(f"Reasoning: {signal['reasoning']}")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Failed to generate signal for {symbol}: {e}")
            return {
                'symbol': symbol,
                'action': 'ERROR',
                'error': str(e)
            }
    
    def test_watchlist(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Test signal generation for multiple symbols"""
        logger.info(f"🔍 Generating signals for watchlist: {', '.join(symbols)}")
        
        try:
            signals = self.generator.generate_signals_for_watchlist(symbols)
            
            # Display results
            print(f"\n📊 Watchlist Signal Results")
            print("=" * 60)
            
            actionable_signals = [s for s in signals if s['action'] != 'HOLD']
            
            print(f"Total Symbols Analyzed: {len(signals)}")
            print(f"Actionable Signals: {len(actionable_signals)}")
            print(f"Hold Recommendations: {len(signals) - len(actionable_signals)}")
            
            if actionable_signals:
                print(f"\n🎯 Top Actionable Signals:")
                print("-" * 40)
                
                # Sort by confidence
                sorted_signals = sorted(actionable_signals, key=lambda x: x['confidence'], reverse=True)
                
                for i, signal in enumerate(sorted_signals[:5], 1):
                    print(f"{i}. {signal['symbol']} - {signal['action']} ({signal['confidence']:.1%})")
                    print(f"   Price: ${signal['current_price']:.2f} | Target: ${signal['target_price']:.2f}")
                    print(f"   Risk/Reward: {signal['risk_reward_ratio']:.2f}")
                    print()
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ Failed to generate watchlist signals: {e}")
            return []
    
    def run_demo_mode(self):
        """Run demonstration with popular stocks"""
        logger.info("🎬 Running AI Signal Generator Demo")
        
        demo_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        
        print(f"\n🎬 SentimentTrade AI Signal Generator Demo")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.user_preferences:
            print(f"👤 User Preferences:")
            print(f"   Risk Appetite: {self.user_preferences.risk_appetite}")
            print(f"   Strategy: {self.user_preferences.strategy}")
            print(f"   Min Confidence: {self.user_preferences.min_confidence:.1%}")
        else:
            print(f"⚙️ Using default configuration")
        
        # Test single symbol first
        print(f"\n🔍 Single Symbol Test: {demo_symbols[0]}")
        single_result = self.test_single_symbol(demo_symbols[0])
        
        # Test watchlist
        print(f"\n📋 Watchlist Test: {len(demo_symbols)} symbols")
        watchlist_results = self.test_watchlist(demo_symbols)
        
        # Summary
        print(f"\n📊 Demo Summary")
        print("=" * 60)
        print(f"✅ Single symbol test: {'SUCCESS' if single_result.get('action') != 'ERROR' else 'FAILED'}")
        print(f"✅ Watchlist test: {len(watchlist_results)} signals generated")
        
        actionable = [s for s in watchlist_results if s['action'] not in ['HOLD', 'ERROR']]
        if actionable:
            avg_confidence = sum(s['confidence'] for s in actionable) / len(actionable)
            print(f"📈 Average confidence: {avg_confidence:.1%}")
            print(f"🎯 Actionable signals: {len(actionable)}/{len(watchlist_results)}")
        
        print(f"\n🎉 Demo completed successfully!")
        
        return {
            'single_result': single_result,
            'watchlist_results': watchlist_results,
            'summary': {
                'total_symbols': len(demo_symbols),
                'actionable_signals': len(actionable),
                'success_rate': len([s for s in watchlist_results if s.get('action') != 'ERROR']) / len(watchlist_results)
            }
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"signal_results_{timestamp}.json"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=json_serializer)
            
            logger.info(f"💾 Results saved to {filename}")
            print(f"💾 Results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")

def main():
    """Main runner function"""
    parser = argparse.ArgumentParser(description='SentimentTrade AI Signal Generator Runner')
    
    parser.add_argument('--symbol', '-s', type=str, help='Single symbol to analyze (e.g., AAPL)')
    parser.add_argument('--watchlist', '-w', nargs='+', help='Multiple symbols to analyze (e.g., AAPL MSFT GOOGL)')
    parser.add_argument('--user', '-u', type=str, help='User email for personalized preferences')
    parser.add_argument('--demo', '-d', action='store_true', help='Run demonstration mode')
    parser.add_argument('--save', action='store_true', help='Save results to JSON file')
    parser.add_argument('--config-check', action='store_true', help='Check configuration and exit')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = AISignalRunner()
    
    print("🤖 SentimentTrade AI Signal Generator Runner")
    print("=" * 60)
    
    # Configuration check mode
    if args.config_check:
        print("⚙️ Configuration Check")
        print("-" * 30)
        
        validation = config.validate_config()
        print(f"Configuration Valid: {'✅ YES' if validation['valid'] else '❌ NO'}")
        
        if validation['missing_keys']:
            print(f"Missing API Keys: {', '.join(validation['missing_keys'])}")
        
        if validation['warnings']:
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  ⚠️ {warning}")
        
        return 0 if validation['valid'] else 1
    
    # Setup database
    if not runner.setup_database():
        print("❌ Database setup failed")
        return 1
    
    # Load user preferences
    if not runner.load_user_preferences(args.user):
        print("❌ Failed to load user preferences")
        return 1
    
    # Initialize generator
    if not runner.initialize_generator():
        print("❌ Failed to initialize signal generator")
        return 1
    
    results = None
    
    try:
        # Execute based on arguments
        if args.demo or (not args.symbol and not args.watchlist):
            # Demo mode (default if no specific arguments)
            results = runner.run_demo_mode()
            
        elif args.symbol:
            # Single symbol mode
            print(f"🔍 Single Symbol Analysis: {args.symbol}")
            result = runner.test_single_symbol(args.symbol)
            results = {'single_result': result}
            
        elif args.watchlist:
            # Watchlist mode
            print(f"📋 Watchlist Analysis: {', '.join(args.watchlist)}")
            watchlist_results = runner.test_watchlist(args.watchlist)
            results = {'watchlist_results': watchlist_results}
        
        # Save results if requested
        if args.save and results:
            runner.save_results(results)
        
        print(f"\n✅ AI Signal Generator completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
