#!/bin/bash
#
# SentimentTrade Deployment Script
# Sets up the SentimentTrade automation system on a virtual machine
#

# Print banner
echo "=================================================="
echo "🚀 SENTIMENTTRADE DEPLOYMENT SCRIPT"
echo "=================================================="
echo "This script will set up the SentimentTrade"
echo "automation system on your virtual machine."
echo "=================================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo "⚠️  Please do not run this script as root"
  exit 1
fi

# Set up colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to print success
print_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to print error
print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Function to print warning
print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
if command -v python3 &>/dev/null; then
  PYTHON_VERSION=$(python3 --version)
  print_success "Found $PYTHON_VERSION"
  PYTHON="python3"
elif command -v python &>/dev/null; then
  PYTHON_VERSION=$(python --version)
  print_success "Found $PYTHON_VERSION"
  PYTHON="python"
else
  print_error "Python not found. Please install Python 3.8 or higher."
  exit 1
fi

# Check pip
print_status "Checking pip..."
if command -v pip3 &>/dev/null; then
  PIP="pip3"
elif command -v pip &>/dev/null; then
  PIP="pip"
else
  print_error "pip not found. Please install pip."
  exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

print_status "Project root: $PROJECT_ROOT"

# Create virtual environment
print_status "Creating virtual environment..."
cd "$PROJECT_ROOT" || exit 1

if [ -d "venv" ]; then
  print_warning "Virtual environment already exists. Skipping creation."
else
  $PYTHON -m venv venv
  if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment."
    exit 1
  fi
  print_success "Virtual environment created."
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
  print_error "Failed to activate virtual environment."
  exit 1
fi
print_success "Virtual environment activated."

# Install requirements
print_status "Installing requirements..."
if [ -f "$PROJECT_ROOT/requirements-clean.txt" ]; then
  $PIP install -r "$PROJECT_ROOT/requirements-clean.txt"
else
  $PIP install -r "$PROJECT_ROOT/requirements.txt"
fi

if [ $? -ne 0 ]; then
  print_error "Failed to install requirements."
  exit 1
fi
print_success "Requirements installed."

# Install specific packages needed for automation
print_status "Installing specific packages for automation..."
$PIP install schedule yfinance pandas numpy python-telegram-bot requests pytz
if [ $? -ne 0 ]; then
  print_warning "Some packages may not have installed correctly."
else
  print_success "Specific packages installed."
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/results/daily_runs"
mkdir -p "$PROJECT_ROOT/logs"
print_success "Directories created."

# Set up Telegram
print_status "Setting up Telegram..."
if [ -f "$PROJECT_ROOT/.env" ]; then
  print_warning "Telegram configuration already exists. Skipping setup."
else
  print_status "Running Telegram setup..."
  cd "$SCRIPT_DIR" || exit 1
  $PYTHON setup_telegram.py
  if [ $? -ne 0 ]; then
    print_warning "Telegram setup may not have completed successfully."
  else
    print_success "Telegram setup completed."
  fi
fi

# Create systemd service file
print_status "Creating systemd service file..."
SERVICE_FILE="$HOME/.config/systemd/user/sentimenttrade.service"
mkdir -p "$HOME/.config/systemd/user"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=SentimentTrade Automated Trading Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/venv/bin/python $SCRIPT_DIR/launcher.py --start
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

print_success "Systemd service file created at $SERVICE_FILE"

# Enable and start service
print_status "Enabling systemd service..."
systemctl --user daemon-reload
systemctl --user enable sentimenttrade.service
print_success "Service enabled."

# Create convenience scripts
print_status "Creating convenience scripts..."

# Start script
cat > "$SCRIPT_DIR/start.sh" << EOF
#!/bin/bash
systemctl --user start sentimenttrade.service
echo "SentimentTrade service started."
echo "Check status with: systemctl --user status sentimenttrade.service"
EOF
chmod +x "$SCRIPT_DIR/start.sh"

# Stop script
cat > "$SCRIPT_DIR/stop.sh" << EOF
#!/bin/bash
systemctl --user stop sentimenttrade.service
echo "SentimentTrade service stopped."
EOF
chmod +x "$SCRIPT_DIR/stop.sh"

# Status script
cat > "$SCRIPT_DIR/status.sh" << EOF
#!/bin/bash
systemctl --user status sentimenttrade.service
EOF
chmod +x "$SCRIPT_DIR/status.sh"

# Logs script
cat > "$SCRIPT_DIR/logs.sh" << EOF
#!/bin/bash
journalctl --user -u sentimenttrade.service -f
EOF
chmod +x "$SCRIPT_DIR/logs.sh"

print_success "Convenience scripts created."

# Final instructions
echo
echo "=================================================="
echo "🎉 SENTIMENTTRADE DEPLOYMENT COMPLETE!"
echo "=================================================="
echo
echo "To manage the service:"
echo "  - Start:  ./start.sh"
echo "  - Stop:   ./stop.sh"
echo "  - Status: ./status.sh"
echo "  - Logs:   ./logs.sh"
echo
echo "To start the service now, run:"
echo "  ./start.sh"
echo
echo "To run the bot interactively:"
echo "  cd $PROJECT_ROOT"
echo "  source venv/bin/activate"
echo "  python $SCRIPT_DIR/launcher.py"
echo
echo "=================================================="
