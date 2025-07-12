# iOS Simulator Setup for SentimentTrade Mobile App

## 📱 Complete iOS Simulator Setup Guide

### **Current Status: ✅ Xcode 15.0.1 Installed**

You already have Xcode installed! Now let's set up the iOS Simulator properly.

---

## 🚀 **Quick Setup (5 Minutes)**

### **Step 1: Accept Xcode License**
```bash
sudo xcodebuild -license accept
```

### **Step 2: Set Developer Tools Path**
```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

### **Step 3: Open Xcode to Install Components**
```bash
# Open Xcode app
open /Applications/Xcode.app

# Or from terminal
open -a Xcode
```

**In Xcode:**
1. **Accept any license agreements**
2. **Install additional components** (if prompted)
3. **Wait for installation to complete**

### **Step 4: Verify Simulator Installation**
```bash
# List available iOS simulators
xcrun simctl list devices

# Check for iPhone simulators specifically
xcrun simctl list devices | grep iPhone
```

### **Step 5: Open iOS Simulator**
```bash
# Open Simulator app
open -a Simulator

# Or open specific iPhone model
xcrun simctl boot "iPhone 15 Pro"
open -a Simulator
```

---

## 📱 **Alternative Setup Methods**

### **Method 1: Through Xcode Interface**
1. **Open Xcode**
2. **Go to:** Xcode → Preferences → Components
3. **Download iOS Simulators** you want
4. **Wait for download to complete**

### **Method 2: Command Line Installation**
```bash
# Install iOS 17.0 simulators (latest)
xcodebuild -downloadPlatform iOS

# Install specific simulator runtime
xcrun simctl runtime install "iOS 17.0"
```

---

## 🎯 **Recommended iPhone Simulators**

### **For SentimentTrade Testing:**
1. **iPhone 15 Pro** - Latest flagship model
2. **iPhone 14** - Popular current model  
3. **iPhone SE (3rd generation)** - Smaller screen testing
4. **iPhone 13 mini** - Compact screen testing

### **Create Simulators:**
```bash
# Create iPhone 15 Pro simulator
xcrun simctl create "iPhone 15 Pro Test" "iPhone 15 Pro" "iOS-17-0"

# Create iPhone 14 simulator  
xcrun simctl create "iPhone 14 Test" "iPhone 14" "iOS-17-0"

# List created simulators
xcrun simctl list devices
```

---

## 🚀 **Running SentimentTrade on iOS Simulator**

### **Step 1: Start iOS Simulator**
```bash
# Open Simulator app
open -a Simulator

# Or boot specific device
xcrun simctl boot "iPhone 15 Pro"
open -a Simulator
```

### **Step 2: Run Flutter App**
```bash
# Navigate to your app
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app

# Check available devices
flutter devices

# Run on iOS Simulator
flutter run -d "iPhone 15 Pro"

# Or let Flutter auto-select
flutter run
```

### **Step 3: Start Backend (Optional)**
```bash
# In separate terminal
cd /Users/abpattan/Downloads/SentimentTrade-main/mobile_app/backend
./start_server.sh
```

---

## 🔧 **Troubleshooting Common Issues**

### **Issue 1: "simctl not found"**
```bash
# Fix developer tools path
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# Verify path
xcode-select --print-path
```

### **Issue 2: "No iOS simulators available"**
```bash
# Open Xcode and install components
open -a Xcode

# Or install via command line
xcodebuild -downloadAllPlatforms
```

### **Issue 3: "License not accepted"**
```bash
# Accept Xcode license
sudo xcodebuild -license accept

# Verify license status
xcodebuild -checkFirstLaunchStatus
```

### **Issue 4: Simulator won't start**
```bash
# Reset all simulators
xcrun simctl erase all

# Restart Simulator app
killall Simulator
open -a Simulator
```

### **Issue 5: Flutter can't find iOS devices**
```bash
# Check Flutter iOS setup
flutter doctor

# Install iOS deployment tools
flutter doctor --android-licenses
```

---

## 📱 **iOS Simulator Controls**

### **Essential Shortcuts:**
- **Home Button**: `Cmd + Shift + H`
- **Lock Screen**: `Cmd + L`
- **Rotate Left**: `Cmd + Left Arrow`
- **Rotate Right**: `Cmd + Right Arrow`
- **Screenshot**: `Cmd + S`
- **Shake Gesture**: `Device → Shake`

### **Hardware Menu:**
- **Volume Up/Down**: `Device → Volume Up/Down`
- **Touch ID**: `Device → Touch ID → Matching Touch`
- **Face ID**: `Device → Face ID → Matching Face`

---

## 🎯 **Testing SentimentTrade Features**

### **What to Test on iOS Simulator:**

#### **1. Login Screen**
- ✅ Email/password input fields
- ✅ "Sign In" button functionality
- ✅ "Continue with Google" button
- ✅ "Forgot Password" link

#### **2. Dashboard Screen**
- ✅ Portfolio performance display (+2,847%)
- ✅ Top strategies list with returns
- ✅ Quick action buttons
- ✅ Navigation between tabs

#### **3. Interactive Backtesting**
- ✅ Strategy dropdown (AI Sentiment)
- ✅ Asset selection (NVDA, SPY, etc.)
- ✅ Parameter sliders (confidence, position size)
- ✅ Preset chips (Conservative, Balanced, etc.)
- ✅ "Run Backtest" button

#### **4. Results Display**
- ✅ Performance metrics (+5,928% NVDA)
- ✅ Trade statistics (win rate, drawdown)
- ✅ Risk metrics (Sharpe ratio)
- ✅ Strategy information

#### **5. Trading Signals**
- ✅ Signal cards with buy/sell/hold
- ✅ Confidence levels
- ✅ Price changes and timestamps
- ✅ Filter tabs

#### **6. Profile Screen**
- ✅ User information display
- ✅ Trading performance stats
- ✅ Settings menu items
- ✅ Account management options

---

## 🚀 **Expected Performance**

### **SentimentTrade on iOS Simulator:**
- **Smooth Navigation**: 60 FPS between screens
- **Responsive UI**: Immediate feedback on taps
- **Fast Loading**: Quick data display and updates
- **Professional Look**: Matches your mockups exactly

### **Key Features Working:**
- ✅ **Material Design 3** theme and colors
- ✅ **Real performance data** display
- ✅ **Interactive controls** (sliders, dropdowns)
- ✅ **Bottom navigation** between 5 tabs
- ✅ **Professional layout** matching mockups

---

## 📞 **Quick Help Commands**

### **Check Status:**
```bash
# Flutter doctor (check iOS setup)
flutter doctor

# List available devices
flutter devices

# Check Xcode installation
xcodebuild -version

# List iOS simulators
xcrun simctl list devices
```

### **Start Fresh:**
```bash
# Clean Flutter project
flutter clean
flutter pub get

# Reset iOS simulators
xcrun simctl erase all

# Restart everything
flutter run
```

---

## 🎉 **Success Indicators**

### **iOS Simulator Setup Complete When:**
- ✅ `xcrun simctl list devices` shows iPhone simulators
- ✅ `flutter devices` shows iOS simulators
- ✅ Simulator app opens iPhone interface
- ✅ `flutter run` successfully launches your app

### **SentimentTrade App Running Successfully When:**
- ✅ Login screen displays with branding
- ✅ Navigation works between all 5 tabs
- ✅ Backtesting screen shows strategy selection
- ✅ Performance data displays (+5,928% NVDA)
- ✅ All interactive elements respond to touch
- ✅ Professional design matches mockups

---

## 🚀 **Next Steps After Setup**

1. **Run the app**: `flutter run`
2. **Test all features**: Navigate through every screen
3. **Verify performance data**: Check +5,928% NVDA results
4. **Test interactions**: Try sliders, buttons, navigation
5. **Start backend**: For full API functionality

**Your revolutionary mobile trading platform is ready for iOS! 📱🚀**
