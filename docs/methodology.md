## 🧠 Methodology

This AI-powered trading bot uses a multi-timeframe, hybrid strategy that combines **technical indicators** and **AI-driven sentiment analysis** to generate actionable trading signals.

---

### 🔍 1. Data Collection

- Market data is sourced from [Twelve Data](https://twelvedata.com) via their REST API.
- Candlestick data is grouped across the following timeframes:
  - `1-minute`
  - `15-minute`
  - `1-hour`
- Key fields used: `open`, `high`, `low`, `close`, `volume`

---

### 📊 2. Technical Analysis

The bot calculates several indicators across different timeframes:

| Indicator | Timeframe(s) | Purpose |
|----------|--------------|---------|
| **RSI** (Relative Strength Index) | 1m, 15m | Detect overbought/oversold conditions |
| **MACD** (Moving Average Convergence Divergence) | 15m | Identify trend momentum and crossovers |
| **Trendline Slope** | 1h | Confirm long-term directional bias |
| **VWAP** (Volume Weighted Average Price) | 1m | Evaluate entry efficiency and price overextension |

---

### 🤖 3. Sentiment Analysis

- The bot queries OpenAI’s `gpt-3.5-turbo` model to score market sentiment from **-1 (very bearish)** to **+1 (very bullish)**.
- Sample prompt used:
  > “Current price of AAPL is 187.34. Market outlook?”

---

### 🎯 4. Trade Decision Logic

Final recommendations are based on a blend of indicator values and sentiment:
