#!/usr/bin/env python3
"""
SentimentTrade Test Runner
Organized test execution for the entire system
"""

import sys
import os
from pathlib import Path
import subprocess

def run_test_file(test_path: Path, description: str):
    """Run a single test file"""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, str(test_path)], 
                              capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Test failed with return code {result.returncode}")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Run all tests in organized fashion"""
    print("🚀 SentimentTrade Test Suite")
    print("=" * 70)
    
    # Test categories
    test_categories = [
        {
            'name': 'Unit Tests',
            'description': 'Individual component testing',
            'tests': [
                ('tests/unit/test_simple_refactor.py', 'Basic Component Functionality'),
                ('tests/unit/test_preferences.py', 'User Preferences System'),
            ]
        },
        {
            'name': 'Integration Tests', 
            'description': 'Cross-component integration testing',
            'tests': [
                ('tests/integration/test_refactored_architecture.py', 'Complete Architecture Integration'),
            ]
        },
        {
            'name': 'Demonstrations',
            'description': 'Feature demonstrations and examples',
            'tests': [
                ('tests/demos/demo_preferences.py', 'Preferences System Demo'),
                ('tests/demos/demo_enhanced_features.py', 'Enhanced API Features Demo'),
                ('tests/demos/demo_api_features.py', 'API Functionality Demo'),
            ]
        }
    ]
    
    overall_results = []
    
    for category in test_categories:
        print(f"\n📂 {category['name']}")
        print(f"   {category['description']}")
        print("-" * 70)
        
        category_results = []
        
        for test_file, description in category['tests']:
            test_path = Path(test_file)
            if test_path.exists():
                result = run_test_file(test_path, description)
                category_results.append((description, result))
            else:
                print(f"⚠️  Test file not found: {test_file}")
                category_results.append((description, False))
        
        overall_results.extend(category_results)
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in overall_results if result)
    total = len(overall_results)
    
    for description, result in overall_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("🔧 Some tests failed - please review and fix")
        return 1

if __name__ == "__main__":
    sys.exit(main())
