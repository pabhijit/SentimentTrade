#!/usr/bin/env python3
"""
Data Downloader for SentimentTrade
Downloads and caches stock data from various sources
"""

import os
import sys
import time
import json
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def download_stock_data(symbol: str, period: str = '60d', interval: str = '1d',
                       use_cache: bool = True, cache_expiry: int = 3600) -> pd.DataFrame:
    """
    Download stock data with caching support

    Args:
        symbol: Stock symbol
        period: Data period (e.g., '60d', '1y')
        interval: Data interval ('1d', '1h', etc.)
        use_cache: Whether to use cached data
        cache_expiry: Cache expiry in seconds (default 1 hour)

    Returns:
        DataFrame with OHLCV data
    """
    try:
        # Setup cache directory
        cache_dir = project_root / 'data' / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"{symbol}_{period}_{interval}.json"

        # Check cache
        if use_cache and cache_file.exists():
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < cache_expiry:
                try:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)

                    # Convert to DataFrame
                    df = pd.DataFrame(cached_data)
                    df.index = pd.to_datetime(df.index)
                    return df
                except Exception as e:
                    print(f"Cache read error for {symbol}: {e}")

        # Download fresh data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)

        if data.empty:
            print(f"No data available for {symbol}")
            return pd.DataFrame()

        # Cache the data
        try:
            # Convert to JSON-serializable format
            json_data = data.reset_index().to_json(date_format='iso')
            with open(cache_file, 'w') as f:
                f.write(json_data)
        except Exception as e:
            print(f"Cache write error for {symbol}: {e}")

        return data

    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")
        return pd.DataFrame()

def download_multiple_stocks(symbols: list, period: str = '60d',
                           interval: str = '1d', use_cache: bool = True) -> dict:
    """
    Download data for multiple stocks

    Args:
        symbols: List of stock symbols
        period: Data period
        interval: Data interval
        use_cache: Whether to use cached data

    Returns:
        Dict of symbol -> DataFrame
    """
    data = {}
    for symbol in symbols:
        try:
            df = download_stock_data(symbol, period, interval, use_cache)
            if not df.empty:
                data[symbol] = df
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"Error downloading {symbol}: {e}")
    return data

def update_stock_data(symbols: list, force: bool = False):
    """
    Update cached stock data for a list of symbols

    Args:
        symbols: List of stock symbols
        force: Force update even if cache is fresh
    """
    print(f"Updating data for {len(symbols)} symbols...")

    updated = 0
    errors = 0

    for symbol in symbols:
        try:
            df = download_stock_data(symbol, use_cache=not force)
            if not df.empty:
                updated += 1
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"Error updating {symbol}: {e}")
            errors += 1

    print(f"Update complete: {updated} updated, {errors} errors")

def get_latest_prices(symbols: list) -> dict:
    """
    Get latest prices for a list of symbols

    Args:
        symbols: List of stock symbols

    Returns:
        Dict of symbol -> latest price
    """
    prices = {}
    for symbol in symbols:
        try:
            df = download_stock_data(symbol, period='1d', interval='1m', use_cache=False)
            if not df.empty:
                prices[symbol] = df['Close'].iloc[-1]
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
    return prices

if __name__ == "__main__":
    # Example usage
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT']

    # Download data
    data = download_multiple_stocks(symbols)
    print(f"Downloaded data for {len(data)} symbols")

    # Get latest prices
    prices = get_latest_prices(symbols)
    for symbol, price in prices.items():
        print(f"{symbol}: ${price:.2f}")
