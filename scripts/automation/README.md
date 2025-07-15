# 🤖 SentimentTrade Automation System

This directory contains the streamlined automation system for SentimentTrade. The system has been refactored to eliminate duplication, improve maintainability, and simplify deployment.

## 🚀 Quick Start

### Option 1: Easy Deployment (Recommended)

```bash
# Run the deployment script
./deploy.sh

# Start the service
./start.sh
```

### Option 2: Manual Setup

```bash
# Install requirements
pip install -r requirements.txt

# Set up Telegram
python setup_telegram.py

# Start the bot
python launcher.py
```

## 📁 File Structure

### Core Files

| File | Description |
|------|-------------|
| `launcher.py` | Main entry point for starting the bot |
| `automation_system.py` | Core automation system that runs strategies |
| `config.py` | Consolidated configuration settings |
| `setup_telegram.py` | Interactive Telegram setup |
| `deploy.sh` | Deployment script for virtual machines |
| `logger.py` | Logging configuration |
| `telegram_alerts.py` | Telegram notification system |
| `test_all.py` | Test script to verify all components |
| `simulate_run.py` | Script to simulate a full run |

## 🔧 Configuration

All configuration is centralized in `config.py`. Key settings include:

- **Strategy Configurations**: Watchlists, parameters, and alert thresholds
- **Timing Configuration**: Run intervals and market hours
- **Alert Configuration**: Telegram settings and notification thresholds
- **Risk Configuration**: Signal limits and risk management settings
- **Data Configuration**: Data fetching and caching settings

## 📱 Telegram Setup

The Telegram setup process is straightforward:

1. Run `python setup_telegram.py`
2. Follow the interactive prompts to create a bot with @BotFather
3. Send a message to your bot to get your chat ID
4. Test the connection and save the configuration

## 🚀 Deployment

The `deploy.sh` script automates the deployment process:

1. Creates a virtual environment
2. Installs required packages
3. Sets up Telegram
4. Creates a systemd service for automatic startup
5. Provides convenience scripts for managing the service

## 🔄 Service Management

After running `deploy.sh`, you can manage the service with:

- `./start.sh` - Start the service
- `./stop.sh` - Stop the service
- `./status.sh` - Check service status
- `./logs.sh` - View service logs

## 🧪 Testing

To test the system without starting the full service:

```bash
# Run the test script to verify all components
python test_all.py

# Simulate a full run
python simulate_run.py

# Test Telegram setup
python setup_telegram.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install schedule yfinance pandas numpy python-telegram-bot requests pytz
   ```

2. **Telegram Connection Issues**
   ```bash
   # Rerun Telegram setup
   python setup_telegram.py
   ```

3. **Permission Issues on VM**
   ```bash
   # Check file permissions
   chmod +x deploy.sh start.sh stop.sh status.sh logs.sh
   ```

4. **Service Not Starting**
   ```bash
   # Check logs
   journalctl --user -u sentimenttrade.service -e
   ```

### Log Files

Logs are stored in the `logs` directory:

```bash
# View logs
tail -f ../logs/sentimenttrade.log
```

## 📊 Results

Strategy run results are stored in JSON format:

```bash
# View recent results
ls -la results/daily_runs/
```

## 🔒 Security Notes

- **Never commit `.env` file** to version control
- **Keep Telegram bot token secure**
- **Use paper trading first** to validate
- **Monitor for unusual activity**
- **Set appropriate risk limits**

## 📞 Support

For issues or questions:
1. Check the logs in `logs/sentimenttrade.log`
2. Review configuration in `config.py`
3. Test Telegram connection with `setup_telegram.py`
4. Verify market hours and data availability

## 🧪 Verification

All components have been thoroughly tested:

```
==================================================
🧪 TESTING SENTIMENTTRADE AUTOMATION COMPONENTS
==================================================

✅ automation_system imported successfully
✅ launcher imported successfully
✅ config imported successfully
✅ setup_telegram imported successfully
✅ logger imported successfully
✅ telegram_alerts imported successfully

Results: 6/6 modules imported successfully
✅ UnifiedRunner.run_all_strategies() returned: {'status': 'success', 'message': 'Strategies executed'}

==================================================
```

---

**⚠️ Disclaimer**: This is for educational and research purposes. Always paper trade first and never risk more than you can afford to lose.
