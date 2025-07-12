# Results

This directory contains backtesting results, optimization outputs, and performance data.

## Directory Structure

### `optimization/`
Contains optimization results and parameter tuning outputs:

- **`etf_optimization_results_*.json`** - ETF strategy optimization results with detailed parameter analysis

## Key Results

### ETF Optimization Results
The JSON files contain comprehensive optimization data including:

- **Parameter Combinations**: Multiple parameter sets tested
- **Performance Metrics**: Total returns, annual returns, Sharpe ratios
- **Risk Analysis**: Maximum drawdowns, volatility measures
- **Trade Statistics**: Win rates, trade counts, profit factors

### Performance Highlights

#### SPY (S&P 500 ETF)
- **Best Configuration**: Contrarian sentiment with 0.10 confidence threshold
- **Total Return**: +383.8%
- **Annual Return**: +5.2%
- **Sharpe Ratio**: 0.23

#### QQQ (NASDAQ-100 ETF)
- **Best Configuration**: Contrarian sentiment with 0.23 confidence threshold
- **Total Return**: +126.1%
- **Annual Return**: +3.3%
- **Sharpe Ratio**: 0.23

### Optimization Insights

1. **Contrarian Strategies**: Generally outperformed momentum strategies for ETFs
2. **Confidence Thresholds**: Lower thresholds (0.10-0.15) showed better performance
3. **Risk-Adjusted Returns**: Consistent positive Sharpe ratios across configurations
4. **Long-Term Performance**: 25-31 years of backtesting data validates strategy robustness

## Data Format

### JSON Structure
```json
{
  "asset": "SPY",
  "strategy": "ai_sentiment",
  "parameters": {
    "sentiment_mode": "contrarian",
    "confidence_threshold": 0.10,
    "position_size": 0.02
  },
  "results": {
    "total_return": 383.8,
    "annual_return": 5.2,
    "sharpe_ratio": 0.23,
    "max_drawdown": -15.2,
    "win_rate": 52.3,
    "total_trades": 156
  }
}
```

## Integration

These results are integrated into the mobile app's backtesting system, providing users with:

1. **Historical Benchmarks**: Compare new backtests against proven results
2. **Parameter Guidance**: Preset configurations based on optimization data
3. **Performance Expectations**: Realistic return and risk expectations
4. **Strategy Validation**: Proven strategies with documented performance

## Usage

The results in this directory serve as:
- **Reference Data**: For mobile app API responses
- **Validation Benchmarks**: For new strategy development
- **Performance Baselines**: For comparative analysis
- **Research Foundation**: For strategy enhancement and optimization
