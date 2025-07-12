# SentimentTrade Flutter App - Setup & Run Guide

## 🚀 Complete Setup Instructions

### **Step 1: Install Flutter**

#### Option A: Using Homebrew (Recommended)
```bash
# Install Flutter using Homebrew
brew install --cask flutter

# Add Flutter to your PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="$PATH:/usr/local/Caskroom/flutter/bin"

# Reload your shell
source ~/.zshrc
```

#### Option B: Manual Installation
```bash
# Download Flutter SDK
cd ~/development
git clone https://github.com/flutter/flutter.git -b stable

# Add to PATH
export PATH="$PATH:$HOME/development/flutter/bin"
```

### **Step 2: Verify Flutter Installation**
```bash
# Check Flutter installation
flutter doctor

# Accept Android licenses (if needed)
flutter doctor --android-licenses
```

### **Step 3: Install Dependencies**
```bash
# Navigate to the mobile app directory
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app

# Get Flutter dependencies
flutter pub get
```

### **Step 4: Set Up Simulators**

#### iOS Simulator (macOS only)
```bash
# Install Xcode from App Store (if not already installed)
# Open Xcode and install additional components

# List available iOS simulators
xcrun simctl list devices

# Open iOS Simulator
open -a Simulator
```

#### Android Emulator
```bash
# Install Android Studio from https://developer.android.com/studio
# Open Android Studio and install SDK components
# Create an Android Virtual Device (AVD) through AVD Manager
```

### **Step 5: Run the App**

#### Check Available Devices
```bash
flutter devices
```

#### Run on iOS Simulator
```bash
# Start iOS Simulator first, then:
flutter run -d "iPhone 15 Pro"

# Or let Flutter choose the device:
flutter run
```

#### Run on Android Emulator
```bash
# Start Android emulator first, then:
flutter run -d android

# Or specify emulator name:
flutter run -d "Pixel_7_API_33"
```

## 📱 **Quick Start Commands**

### **One-Command Setup** (after Flutter is installed)
```bash
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app
flutter pub get
flutter run
```

### **Start Backend Server** (in separate terminal)
```bash
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app/backend
./start_server.sh
```

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### 1. Flutter Not Found
```bash
# Check if Flutter is in PATH
echo $PATH | grep flutter

# If not found, add to ~/.zshrc:
export PATH="$PATH:/path/to/flutter/bin"
source ~/.zshrc
```

#### 2. iOS Simulator Issues
```bash
# Reset iOS Simulator
xcrun simctl erase all

# Open Simulator manually
open -a Simulator
```

#### 3. Android Emulator Issues
```bash
# List available emulators
emulator -list-avds

# Start specific emulator
emulator -avd Pixel_7_API_33
```

#### 4. Dependencies Issues
```bash
# Clean and reinstall dependencies
flutter clean
flutter pub get

# Update dependencies
flutter pub upgrade
```

#### 5. Build Issues
```bash
# Clean build cache
flutter clean

# Rebuild
flutter run --debug
```

## 📊 **App Features to Test**

### **1. Login Screen**
- Test email/password input
- Try "Continue with Google" button
- Check "Forgot Password" link

### **2. Dashboard**
- View portfolio performance (+2,847%)
- Check top strategies list
- Test "Run Backtest" and "View Analytics" buttons

### **3. Interactive Backtesting**
- Select AI Sentiment strategy
- Choose NVDA asset
- Adjust parameter sliders
- Apply different presets (Conservative, Balanced, Aggressive)
- Run backtest and view progress

### **4. Results Screen**
- View performance metrics (+5,928% NVDA)
- Check trade statistics
- Analyze risk metrics (Sharpe ratio, drawdown)

### **5. Trading Signals**
- View real-time signals
- Filter by Buy/Sell/Hold
- Check confidence levels

### **6. Profile Screen**
- View user information
- Check trading statistics
- Access settings menu

## 🌐 **Backend Integration**

### **Start Backend Server**
```bash
# Terminal 1: Start Flask API
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app/backend
./start_server.sh

# Terminal 2: Run Flutter app
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app
flutter run
```

### **API Endpoints Available**
- `GET /api/strategies` - Available trading strategies
- `GET /api/assets` - Supported assets
- `POST /api/backtest` - Run backtesting
- `GET /api/backtest/results/{id}` - Get results
- `GET /api/performance/{asset}/{strategy}` - Historical data

## 🎯 **Development Workflow**

### **Hot Reload**
- Press `r` in terminal to hot reload
- Press `R` to hot restart
- Press `q` to quit

### **Debug Mode**
```bash
# Run in debug mode with verbose output
flutter run --debug --verbose
```

### **Release Mode**
```bash
# Build for release (testing performance)
flutter run --release
```

## 📱 **Simulator Controls**

### **iOS Simulator**
- **Rotate**: `Cmd + Left/Right Arrow`
- **Home**: `Cmd + Shift + H`
- **Lock Screen**: `Cmd + L`
- **Screenshot**: `Cmd + S`

### **Android Emulator**
- **Back**: `Esc`
- **Home**: `Cmd + H`
- **Menu**: `F2`
- **Volume**: `Cmd + Up/Down`

## 🎨 **UI Testing**

### **Screen Navigation**
1. **Bottom Navigation**: Tap between Watchlist, Dashboard, Backtest, Signals, Profile
2. **Forms**: Test input fields, sliders, dropdowns
3. **Buttons**: Verify all CTAs work correctly
4. **Cards**: Check tap interactions and data display

### **Performance Testing**
1. **Backtesting Flow**: Complete end-to-end backtest
2. **Data Loading**: Check API response times
3. **Smooth Animations**: Verify transitions and interactions
4. **Memory Usage**: Monitor app performance

## 🚀 **Next Steps**

### **After Successful Run**
1. **Test All Features**: Navigate through every screen
2. **Backend Integration**: Verify API calls work
3. **Performance Validation**: Check +5,928% NVDA results display
4. **User Experience**: Test complete trading workflow

### **Development Enhancements**
1. **Add Real Charts**: Implement FL Chart for equity curves
2. **Enhanced Animations**: Smooth transitions between screens
3. **Offline Support**: Cache data for offline viewing
4. **Push Notifications**: Real-time trading alerts

## 📞 **Support**

### **If You Encounter Issues**
1. **Check Flutter Doctor**: `flutter doctor -v`
2. **Verify Dependencies**: `flutter pub deps`
3. **Clean and Rebuild**: `flutter clean && flutter pub get`
4. **Check Logs**: Look for error messages in terminal

### **Useful Commands**
```bash
# Check Flutter version
flutter --version

# List connected devices
flutter devices

# Analyze code
flutter analyze

# Run tests
flutter test
```

## 🎉 **Success Indicators**

### **App Successfully Running When:**
- ✅ Login screen displays with SentimentTrade branding
- ✅ Navigation works between all 5 tabs
- ✅ Backtesting screen shows strategy and asset selection
- ✅ Performance data displays correctly (+5,928% NVDA)
- ✅ Backend API responds to requests
- ✅ No error messages in terminal

**Your revolutionary mobile trading platform is ready to run!** 🚀📱
