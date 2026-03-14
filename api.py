import requests
import os
import pandas as pd
from datetime import datetime, timedelta

TOKEN = os.environ.get("BRAPI_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
API_URL = "https://brapi.dev/api/quote/"

def save_data(data):
    file_exists = os.path.isfile('stock_data.csv')
    df = pd.DataFrame(data['results']).drop(columns=['logourl'], errors='ignore')
    df.to_csv('stock_data.csv', mode='a', header=not file_exists, index=False)

def get_stock_price(ticker):
    response = requests.get(f"{API_URL}{ticker}", headers=HEADERS)
    data = response.json()
    save_data(data)
    
    res = data["results"][0]
    price = res["regularMarketPrice"]
    change = res["regularMarketChangePercent"]
    time_utc = res["regularMarketTime"]
    
    # Converter UTC para Brasília (UTC-3)
    time_obj = datetime.fromisoformat(time_utc.replace('Z', '+00:00'))
    time_utc3 = time_obj - timedelta(hours=3)
    time = time_utc3.strftime("%Y-%m-%d %H:%M:%S")
    
    return price, change, time, res