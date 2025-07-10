import pandas as pd
from utils import rsi, macd, vwap, mock_sentiment

# Load mock 1m OHLCV data
df = pd.read_csv("test_data.csv")

entry_price = None
results = []

for i in range(30, len(df)):
    window = df.iloc[i-30:i]
    close_prices = window['close']
    trend = close_prices.iloc[-1] - close_prices.iloc[0]
    rsi_val = rsi(close_prices.values)
    macd_val = macd(close_prices)
    vwap_val = vwap(window)
    sentiment = mock_sentiment()

    price = close_prices.iloc[-1]
    recommendation = "HOLD"

    if (rsi_val < 35 and macd_val > 0 and trend > 0 and sentiment > 0.4 and price < vwap_val):
        recommendation = "BUY"
        entry_price = price
        target_price = round(price * 1.02, 2)
        stop_loss = round(price * 0.98, 2)
    elif (rsi_val > 65 and macd_val < 0 and sentiment < -0.3 and price > vwap_val):
        recommendation = "SELL"
        entry_price = price
        target_price = round(price * 0.98, 2)
        stop_loss = round(price * 1.02, 2)

    if recommendation != "HOLD":
        results.append({
            "timestamp": df.iloc[i]["datetime"],
            "action": recommendation,
            "entry": round(price, 2),
            "stop": stop_loss,
            "target": target_price,
            "sentiment": round(sentiment, 2),
            "vwap": round(vwap_val, 2)
        })

results_df = pd.DataFrame(results)
results_df.to_csv("backtest_results.csv", index=False)
print("Backtest complete. Results saved to backtest_results.csv.")
