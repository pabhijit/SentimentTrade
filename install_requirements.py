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
    
    # Check Python version first
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8+ is required. Please upgrade Python.")
        return False
    
    if python_version >= (3, 12):
        print("⚠️ Python 3.12+ detected. Some packages may have compatibility issues.")
        print("   Consider using Python 3.8-3.11 for best compatibility.")
    
    # Determine requirements file
    if level == "full":
        req_file = "requirements-fixed.txt"
        description = "Full SentimentTrade suite (fixed versions)"
    elif level == "minimal":
        req_file = "requirements-minimal.txt"
        description = "Essential components only (guaranteed compatible)"
    else:
        print(f"❌ Unknown installation level: {level}")
        return False
    
    print(f"🎯 Installing: {description}")
    print(f"📄 Requirements file: {req_file}")
    print()
    
    # Check if requirements file exists
    if not Path(req_file).exists():
        print(f"❌ Requirements file not found: {req_file}")
        print("Available files:")
        for f in Path(".").glob("requirements*.txt"):
            print(f"   - {f}")
        return False
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️ Pip upgrade failed, continuing anyway...")
    
    # Install requirements with better error handling
    install_cmd = f"{sys.executable} -m pip install -r {req_file}"
    print(f"🔧 Running: {install_cmd}")
    
    try:
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Requirements installed successfully!")
            return True
        else:
            print("❌ Installation failed with errors:")
            print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
            print("STDERR:", result.stderr[-1000:])  # Last 1000 chars
            
            # Suggest fallback
            if level == "full":
                print("\n💡 Suggestion: Try minimal installation instead:")
                print("   python install_requirements.py --level minimal")
            else:
                print("\n💡 Try installing packages individually:")
                print("   pip install yfinance pandas numpy schedule python-telegram-bot")
            
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out (10 minutes)")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
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

def install_core_packages_manually():
    """Install core packages one by one for maximum compatibility"""
    print("🔧 Installing core packages individually...")
    
    core_packages = [
        "yfinance>=0.2.18",
        "pandas>=1.5.0", 
        "numpy>=1.21.0",
        "requests>=2.28.0",
        "python-dotenv>=1.0.0",
        "schedule>=1.2.0",
        "python-telegram-bot>=20.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "ta>=0.10.2",
        "matplotlib>=3.5.0",
        "colorlog>=6.7.0"
    ]
    
    successful = []
    failed = []
    
    for package in core_packages:
        print(f"📦 Installing {package}...")
        try:
            result = subprocess.run(
                f"{sys.executable} -m pip install '{package}'", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
                successful.append(package)
            else:
                print(f"❌ {package} failed: {result.stderr[:200]}")
                failed.append(package)
                
        except Exception as e:
            print(f"❌ {package} error: {e}")
            failed.append(package)
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print(f"\n⚠️ Failed packages:")
        for pkg in failed:
            print(f"   - {pkg}")
        print("\nYou can try installing these manually later.")
    
    return len(successful) >= 8  # Need at least 8 core packages

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(description="Install SentimentTrade requirements")
    parser.add_argument(
        "--level",
        choices=["minimal", "full", "manual"],
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
    if args.level == "manual":
        success = install_core_packages_manually()
    else:
        success = install_requirements(args.level)
    
    if not success:
        print("\n❌ Installation failed!")
        if args.level != "manual":
            print("\n💡 Try manual installation:")
            print("   python install_requirements.py --level manual")
        sys.exit(1)
    
    # Verify if requested
    if args.verify:
        verify_installation()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Installation completed successfully!")

if __name__ == "__main__":
    main()
