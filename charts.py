import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def create_charts():
    # Load configuration
    with open('stock_thresholds.json', 'r') as f:
        config = json.load(f)
    
    # Load data
    df = pd.read_csv('stock_data.csv')
    
    # Convert date column
    df['regularMarketTime'] = pd.to_datetime(df['regularMarketTime'])
    
    # Filter last 2 days
    cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=2)
    df = df[df['regularMarketTime'] >= cutoff_date]
    
    tickers = list(config.keys())
    
    for ticker in tickers:
        ticker_data = df[df['symbol'] == ticker].copy()
        
        if ticker_data.empty:
            print(f"No data found for {ticker}")
            continue

        # Date handling: Convert to UTC-3 (Brazil time)
        ticker_data['regularMarketTime'] = ticker_data['regularMarketTime'] - pd.Timedelta(hours=3)
        
        # Sort by time to ensure the chart flows correctly
        ticker_data = ticker_data.sort_values('regularMarketTime')

        plt.figure(figsize=(12, 6))
        
        # 1. Area: Fill between Minimum (DayLow) and Maximum (DayHigh)
        plt.fill_between(
            ticker_data['regularMarketTime'], 
            ticker_data['regularMarketDayLow'], 
            ticker_data['regularMarketDayHigh'], 
            color='skyblue', 
            alpha=0.3, 
            label='Day Range (Min/Max)'
        )

        # 2. Line: Current Value (Price)
        plt.plot(
            ticker_data['regularMarketTime'], 
            ticker_data['regularMarketPrice'], 
            color='navy', 
            linewidth=2, 
            label='Current Price'
        )

        # 3. Annotations for values on X axis
        for idx, row in ticker_data.iterrows():
            plt.annotate(
            f'{row["regularMarketPrice"]:.2f}',
            xy=(row['regularMarketTime'], row['regularMarketPrice']),
            xytext=(0, 10),
            textcoords='offset points',
            ha='center',
            fontsize=8,
            color='darkblue',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='gray', alpha=0.7)
            )
        # 4. Threshold Line (Alert Limit)
        ticker_threshold = config.get(ticker) # Fetch value from loaded JSON dictionary
        
        if ticker_threshold:
            plt.axhline(
                y=ticker_threshold, 
                color='red', 
                linestyle='--', 
                linewidth=1.5, 
                label=f'Threshold (R$ {ticker_threshold:.2f})',
                alpha=0.8
            )
            
            # Optional: Add small text above the line in the left corner
            plt.text(
                ticker_data['regularMarketTime'].min(), 
                ticker_threshold, 
                f' Limit: R$ {ticker_threshold:.2f}', 
                color='red', 
                va='bottom', 
                fontsize=9,
                fontweight='bold'
            )
        # Styling
        plt.title(f'Price Analysis: {ticker}', fontsize=14, fontweight='bold')
        plt.xlabel('Time/Date')
        plt.ylabel('Price (Local Currency)')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        plt.tight_layout()
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M')) # Ex: 13/03 15:00
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        # Save
        output_dir = Path('charts')
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / f'{ticker}_chart.png')
        plt.close()
        
        print(f"Chart created for {ticker} with area range.")