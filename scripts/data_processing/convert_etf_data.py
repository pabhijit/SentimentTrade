#!/usr/bin/env python3
"""
ETF Data Converter for SPY and QQQ
Convert ETF CSV data to backtesting format
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def convert_etf_data():
    """Convert SPY and QQQ data to backtesting format"""
    
    print("🔄 Converting ETF Data for Backtesting")
    print("=" * 50)
    
    # Input files
    spy_file = "/Users/abpattan/Downloads/archive (1)/SPY.csv"
    qqq_file = "/Users/abpattan/Downloads/archive (1)/QQQ_raw.csv"
    
    # Output directory
    output_dir = "data/real_data"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Convert SPY
    print("📊 Converting SPY data...")
    try:
        spy_df = pd.read_csv(spy_file)
        print(f"   Loaded {len(spy_df)} rows of SPY data")
        print(f"   Date range: {spy_df['date'].iloc[0]} to {spy_df['date'].iloc[-1]}")
        
        # Convert to our format
        spy_converted = pd.DataFrame({
            'datetime': pd.to_datetime(spy_df['date']).dt.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'open': spy_df['open'],
            'high': spy_df['high'],
            'low': spy_df['low'],
            'close': spy_df['close'],
            'volume': spy_df['volume']
        })
        
        # Remove any NaN values
        spy_converted = spy_converted.dropna()
        
        # Save
        spy_output = f"{output_dir}/SPY_historical.csv"
        spy_converted.to_csv(spy_output, index=False)
        
        # Calculate stats
        spy_return = ((spy_df['close'].iloc[-1] / spy_df['close'].iloc[0]) - 1) * 100
        spy_years = (pd.to_datetime(spy_df['date'].iloc[-1]) - pd.to_datetime(spy_df['date'].iloc[0])).days / 365.25
        spy_annual = ((spy_df['close'].iloc[-1] / spy_df['close'].iloc[0]) ** (1/spy_years) - 1) * 100
        
        print(f"   ✅ Saved {len(spy_converted)} rows to {spy_output}")
        print(f"   📈 SPY Performance: {spy_return:+.1f}% total ({spy_annual:+.1f}% annual over {spy_years:.1f} years)")
        
    except Exception as e:
        print(f"   ❌ Error converting SPY: {e}")
        return False
    
    # Convert QQQ
    print("\n📊 Converting QQQ data...")
    try:
        qqq_df = pd.read_csv(qqq_file)
        print(f"   Loaded {len(qqq_df)} rows of QQQ data")
        print(f"   Date range: {qqq_df['date'].iloc[0]} to {qqq_df['date'].iloc[-1]}")
        
        # Convert to our format
        qqq_converted = pd.DataFrame({
            'datetime': pd.to_datetime(qqq_df['date']).dt.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'open': qqq_df['open'],
            'high': qqq_df['high'],
            'low': qqq_df['low'],
            'close': qqq_df['close'],
            'volume': qqq_df['volume']
        })
        
        # Remove any NaN values
        qqq_converted = qqq_converted.dropna()
        
        # Save
        qqq_output = f"{output_dir}/QQQ_historical.csv"
        qqq_converted.to_csv(qqq_output, index=False)
        
        # Calculate stats
        qqq_return = ((qqq_df['close'].iloc[-1] / qqq_df['close'].iloc[0]) - 1) * 100
        qqq_years = (pd.to_datetime(qqq_df['date'].iloc[-1]) - pd.to_datetime(qqq_df['date'].iloc[0])).days / 365.25
        qqq_annual = ((qqq_df['close'].iloc[-1] / qqq_df['close'].iloc[0]) ** (1/qqq_years) - 1) * 100
        
        print(f"   ✅ Saved {len(qqq_converted)} rows to {qqq_output}")
        print(f"   📈 QQQ Performance: {qqq_return:+.1f}% total ({qqq_annual:+.1f}% annual over {qqq_years:.1f} years)")
        
    except Exception as e:
        print(f"   ❌ Error converting QQQ: {e}")
        return False
    
    print(f"\n✅ ETF data conversion completed!")
    print(f"   Ready for backtesting with SPY and QQQ data")
    
    return True

if __name__ == "__main__":
    convert_etf_data()
