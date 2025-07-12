# AI Signal Generation Logic with ATR-based Stop-Loss and Target

import os
import requests
from datetime import datetime
import numpy as np
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
STOCK_SYMBOL = os.getenv("STOCK_SYMBOL", "AAPL")

def fetch_candles(symbol, interval, outputsize=50):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVE_DATA_API_KEY}&outputsize={outputsize}"
    response = requests.get(url).json()
    if "values" in response:
        return list(reversed(response["values"]))
    return []

def rsi(values, period=14):
    deltas = np.diff(values)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period if any(seed < 0) else 0.001
    rs = up / down
    rsi_vals = [100 - 100 / (1 + rs)]
    for delta in deltas[period:]:
        up_val = max(delta, 0)
        down_val = -min(delta, 0)
        up = (up * (period - 1) + up_val) / period
        down = (down * (period - 1) + down_val) / period
        rs = up / (down if down != 0 else 0.001)
        rsi_vals.append(100 - 100 / (1 + rs))
    return rsi_vals[-1]

def macd(values):
    ema12 = exponential_moving_average(values, 12)
    ema26 = exponential_moving_average(values, 26)
    return ema12[-1] - ema26[-1]

def exponential_moving_average(values, period):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:period] = a[period]
    return a

def trend_slope(prices):
    x = np.arange(len(prices))
    slope, _ = np.polyfit(x, prices, 1)
    return slope

def vwap_from_candles(candles):
    try:
        tp_vol = 0
        total_vol = 0
        for c in candles:
            high = float(c["high"])
            low = float(c["low"])
            close = float(c["close"])
            vol = float(c["volume"])
            tp = (high + low + close) / 3
            tp_vol += tp * vol
            total_vol += vol
        return tp_vol / total_vol if total_vol else None
    except Exception as e:
        print(f"[ERROR] VWAP calc failed: {e}")
        return None

def calculate_atr(candles, period=14):
    trs = []
    for i in range(1, len(candles)):
        high = float(candles[i]["high"])
        low = float(candles[i]["low"])
        prev_close = float(candles[i-1]["close"])
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
    if len(trs) >= period:
        return np.mean(trs[-period:])
    else:
        return None

def get_sentiment(text):
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Rate the sentiment for this stock message from -1 (very bearish) to 1 (very bullish). Only respond with a number."},
                    {"role": "user", "content": text}
                ]
            }
        )
        return float(response.json()['choices'][0]['message']['content'].strip())
    except:
        return 0

def run_agent(symbol):
    data_1m = fetch_candles(symbol, "1min", 30)
    data_15m = fetch_candles(symbol, "15min", 50)
    data_1h = fetch_candles(symbol, "1h", 20)
    if not data_1m or not data_15m or not data_1h:
        print("Insufficient data.")
        return
    prices_1m = [float(v["close"]) for v in data_1m]
    prices_15m = [float(v["close"]) for v in data_15m]
    prices_1h = [float(v["close"]) for v in data_1h]
    rsi_1m = rsi(prices_1m)
    rsi_15m = rsi(prices_15m)
    macd_15m = macd(prices_15m)
    slope_1h = trend_slope(prices_1h)
    current_price = prices_1m[-1]
    vwap_1m = vwap_from_candles(data_1m)
    atr = calculate_atr(data_1m)
    sentiment = get_sentiment(f"Current price of {symbol} is {current_price}. Market outlook?")
    # Decision logic
    recommendation = "HOLD"
    if rsi_1m < 30 and rsi_15m < 35 and macd_15m > 0 and slope_1h > 0 and sentiment > 0.4 and current_price < vwap_1m:
        recommendation = "BUY"
    elif rsi_1m > 70 and rsi_15m > 65 and macd_15m < 0 and slope_1h < 0 and sentiment < -0.4 and current_price > vwap_1m:
        recommendation = "SELL"
    # ATR-based stop loss and target
    if atr:
        stop_loss = round(current_price - 1.5 * atr, 2)
        target_price = round(current_price + 2 * atr, 2)
    else:
        stop_loss = round(current_price * 0.98, 2)
        target_price = round(current_price * 1.03, 2)
    print(f"Technical Recommendation: {recommendation}")
    print(f"Entry Price: {current_price:.2f}")
    print(f"Stop-Loss: {stop_loss}")
    print(f"Target/Exit Price: {target_price}")

if __name__ == "__main__":
    run_agent(STOCK_SYMBOL)
