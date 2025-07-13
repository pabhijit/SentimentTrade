#!/usr/bin/env python3
"""
SentimentTrade Requirements Installation Script
Handles installation of different requirement levels based on use case
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("=" * 70)
    print("🚀 SENTIMENTTRADE REQUIREMENTS INSTALLER")
    print("=" * 70)
    print()

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def install_requirements(level="minimal"):
    """Install requirements based on level"""
    print_banner()
    
    # Determine requirements file
    if level == "full":
        req_file = "requirements.txt"
        description = "Full SentimentTrade suite with all features"
    elif level == "minimal":
        req_file = "requirements-minimal.txt"
        description = "Essential components for automated trading"
    else:
        print(f"❌ Unknown installation level: {level}")
        return False
    
    print(f"🎯 Installing: {description}")
    print(f"📄 Requirements file: {req_file}")
    print()
    
    # Check if requirements file exists
    if not Path(req_file).exists():
        print(f"❌ Requirements file not found: {req_file}")
        return False
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️ Pip upgrade failed, continuing anyway...")
    
    # Install requirements
    install_cmd = f"{sys.executable} -m pip install -r {req_file}"
    if not run_command(install_cmd, f"Installing {req_file}"):
        return False
    
    # Install optional system dependencies
    print("\n🔧 OPTIONAL SYSTEM DEPENDENCIES:")
    print("For enhanced technical analysis, you may want to install TA-Lib:")
    print()
    if sys.platform == "darwin":  # macOS
        print("macOS:")
        print("  brew install ta-lib")
        print("  pip install TA-Lib")
    elif sys.platform.startswith("linux"):  # Linux
        print("Linux (Ubuntu/Debian):")
        print("  sudo apt-get install libta-lib-dev")
        print("  pip install TA-Lib")
    elif sys.platform == "win32":  # Windows
        print("Windows:")
        print("  Download TA-Lib wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib")
        print("  pip install <downloaded-wheel-file>")
    
    print("\n✅ Requirements installation completed!")
    return True

def verify_installation():
    """Verify that key packages are installed"""
    print("\n🔍 VERIFYING INSTALLATION:")
    print("-" * 40)
    
    key_packages = [
        ("yfinance", "Market data"),
        ("pandas", "Data analysis"),
        ("numpy", "Numerical computing"),
        ("telegram", "Telegram alerts"),
        ("schedule", "Task scheduling"),
        ("fastapi", "Web API"),
        ("sqlalchemy", "Database"),
    ]
    
    all_good = True
    for package, description in key_packages:
        try:
            __import__(package)
            print(f"✅ {package:<15} - {description}")
        except ImportError:
            print(f"❌ {package:<15} - {description} (MISSING)")
            all_good = False
    
    print("-" * 40)
    if all_good:
        print("🎉 All key packages installed successfully!")
    else:
        print("⚠️ Some packages are missing. Try running the installer again.")
    
    return all_good

def show_next_steps():
    """Show what to do after installation"""
    print("\n🎯 NEXT STEPS:")
    print("-" * 30)
    print("1. 🤖 Set up Telegram bot:")
    print("   cd scripts/automation")
    print("   python setup_telegram.py")
    print()
    print("2. 🚀 Launch the trading bot:")
    print("   cd scripts/automation")
    print("   python launch_trading_bot.py")
    print()
    print("3. 📊 Or run backtesting:")
    print("   cd scripts/backtesting")
    print("   python comprehensive_backtest.py")
    print()
    print("4. 🌐 Or start the API server:")
    print("   cd api")
    print("   python main.py")

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(description="Install SentimentTrade requirements")
    parser.add_argument(
        "--level",
        choices=["minimal", "full"],
        default="minimal",
        help="Installation level (default: minimal)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify installation after installing"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify current installation, don't install"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        print_banner()
        verify_installation()
        return
    
    # Install requirements
    success = install_requirements(args.level)
    
    if not success:
        print("\n❌ Installation failed!")
        sys.exit(1)
    
    # Verify if requested
    if args.verify:
        verify_installation()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Installation completed successfully!")

if __name__ == "__main__":
    main()
