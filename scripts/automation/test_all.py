#!/usr/bin/env python3
"""
Test script to verify all components of the SentimentTrade automation system
"""

import os
import sys
import importlib
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_module(module_name):
    """Test importing a module"""
    try:
        module = importlib.import_module(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"❌ {module_name} import failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("🧪 TESTING SENTIMENTTRADE AUTOMATION COMPONENTS")
    print("=" * 50)
    print()
    
    # Test core modules
    modules = [
        "automation_system",
        "launcher",
        "config",
        "setup_telegram",
        "logger",
        "telegram_alerts"
    ]
    
    success_count = 0
    for module in modules:
        if test_module(module):
            success_count += 1
    
    print()
    print(f"Results: {success_count}/{len(modules)} modules imported successfully")
    
    # Test automation_system functionality
    try:
        from automation_system import UnifiedRunner
        runner = UnifiedRunner()
        result = runner.run_all_strategies()
        print(f"✅ UnifiedRunner.run_all_strategies() returned: {result}")
    except Exception as e:
        print(f"❌ UnifiedRunner test failed: {e}")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()
