import requests
import os
import pandas as pd
from datetime import datetime, timedelta

TOKEN = os.environ.get("BRAPI_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
API_URL = "https://brapi.dev/api/quote/"

def purge_old_data(csv_path='stock_data.csv', months=2):
    if not os.path.isfile(csv_path):
        return
    df = pd.read_csv(csv_path)
    if 'regularMarketTime' not in df.columns:
        return
    df['regularMarketTime'] = pd.to_datetime(df['regularMarketTime'], utc=True, errors='coerce')
    cutoff = datetime.now(tz=df['regularMarketTime'].dt.tz) - timedelta(days=months * 30)
    before = len(df)
    df = df[df['regularMarketTime'] >= cutoff]
    after = len(df)
    if before != after:
        df.to_csv(csv_path, index=False)
        print(f"Purged {before - after} rows older than {months} months from {csv_path}")

def save_data(data):
    file_exists = os.path.isfile('stock_data.csv')
    df = pd.DataFrame(data['results']).drop(columns=['logourl'], errors='ignore')
    df.to_csv('stock_data.csv', mode='a', header=not file_exists, index=False)

def get_stock_price(ticker):
    response = requests.get(f"{API_URL}{ticker}", headers=HEADERS, timeout=10)
    data = response.json()
    save_data(data)
    
    res = data["results"][0]
    price = res["regularMarketPrice"]
    change = res["regularMarketChangePercent"]
    time_utc = res["regularMarketTime"]
    
    # Convert UTC to Brazil time (UTC-3)
    time_obj = datetime.fromisoformat(time_utc.replace('Z', '+00:00'))
    time_utc3 = time_obj - timedelta(hours=3)
    time = time_utc3.strftime("%Y-%m-%d %H:%M:%S")
    
    return price, change, time, res