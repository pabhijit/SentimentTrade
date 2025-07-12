# Scripts

This directory contains utility scripts for backtesting, data processing, and system operations.

## Directory Structure

### `backtesting/`
Contains scripts for running various backtesting scenarios:

- **`run_backtest.py`** - Main backtesting script for AI sentiment strategies
- **`run_real_backtest.py`** - Real market data backtesting with comprehensive analysis
- **`final_real_backtest.py`** - Final optimized backtesting implementation
- **`run_break_retest_backtest.py`** - Break and retest strategy backtesting
- **`backtest_etfs.py`** - ETF-specific backtesting with parameter optimization
- **`run_ai_signals.py`** - AI signal generation and analysis

### `data_processing/`
Contains scripts for data manipulation and preparation:

- **`convert_etf_data.py`** - ETF data conversion and formatting utilities

## Usage Examples

### Running ETF Backtests
```bash
cd scripts/backtesting
python backtest_etfs.py
```

### Running Individual Stock Analysis
```bash
cd scripts/backtesting
python run_real_backtest.py
```

### Break and Retest Strategy
```bash
cd scripts/backtesting
python run_break_retest_backtest.py
```

### Data Processing
```bash
cd scripts/data_processing
python convert_etf_data.py
```

## Key Features

### Backtesting Scripts
- **Comprehensive Analysis**: 15-31 years of historical data
- **Multiple Strategies**: AI Sentiment, Break & Retest, and more
- **Parameter Optimization**: Automated parameter tuning
- **Performance Metrics**: Risk-adjusted returns, Sharpe ratios, drawdowns
- **Visualization**: Automatic chart generation

### Data Processing
- **Format Conversion**: Convert between different data formats
- **Data Validation**: Ensure data quality and consistency
- **Historical Data**: Process decades of market data

## Integration

These scripts form the foundation of the mobile app's backtesting capabilities. The mobile app's backend API uses similar logic and methodologies to provide real-time backtesting functionality to users.

## Performance Results

The scripts in this directory have generated the proven results integrated into the mobile app:
- **NVDA**: +5,928% (AI Sentiment Contrarian)
- **SPY**: +383.8% (AI Sentiment)
- **QQQ**: +126.1% (AI Sentiment)
- **AAPL**: +545% (AI Sentiment Momentum)
- **AMZN**: +449% (AI Sentiment Momentum)
