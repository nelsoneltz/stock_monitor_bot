import requests
import os
from config import Config

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID")
config = Config()

def send_discord_message(price, change, time, ticker, stock_data=None):
    threshold = config.get_threshold(ticker)
    image_path = f"charts/{ticker}_chart.png"
    
    content = f"📈 **Cotação {ticker}**\nPreço: R$ {price:.2f}\nVariação: {change:.2f}%\nHora: {time}"
    
    if price <= threshold:
        content += f"\n⚠️ **Abaixo do limite!** <@{DISCORD_USER_ID}>"

    payload = {"content": content}
    abs_change = abs(stock_data['regularMarketChangePercent']) if stock_data else abs(change)
    
    if abs_change > 5.0 and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            files = {"file": (f"{ticker}_chart.png", f, "image/png")}
            requests.post(WEBHOOK_URL, data=payload, files=files)
    else:
        requests.post(WEBHOOK_URL, json=payload)