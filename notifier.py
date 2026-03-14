import requests
import os
from config import Config

# Load Discord webhook URL from environment variables
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
# Load Discord user ID for mentions when price alerts are triggered
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID")
# Initialize configuration to access stock price thresholds
config = Config()

def send_discord_message(price, change, time, ticker, stock_data=None):
    """
    Send a formatted stock price notification to Discord.
    
    Args:
        price (float): Current stock price
        change (float): Percentage change in stock price
        time (str): Timestamp of the stock data
        ticker (str): Stock ticker symbol
        stock_data (dict, optional): Complete stock data from API
    """
    # Get the configured price threshold for this ticker
    threshold = config.get_threshold(ticker)
    # Construct path to the chart image for this ticker
    image_path = f"charts/{ticker}_chart.png"
    
    # Build the base message content with stock information
    content = f"📈 **Cotação {ticker}**\nPreço: R$ {price:.2f}\nVariação: {change:.2f}%\nHora: {time}"
    
    # Add alert mention if price drops below the configured threshold
    if price <= threshold:
        content += f"\n⚠️ **Abaixo do limite!** <@{DISCORD_USER_ID}>"

    # Prepare the Discord webhook payload
    payload = {"content": content}
    
    # Calculate absolute percentage change (for comparison)
    abs_change = abs(stock_data['regularMarketChangePercent']) if stock_data else abs(change)
    
    # Send message with chart attachment if change exceeds 5% and chart exists
    if abs_change > 5.0 and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            files = {"file": (f"{ticker}_chart.png", f, "image/png")}
            requests.post(WEBHOOK_URL, data=payload, files=files)
    else:
        # Send text-only message if change is small or chart doesn't exist
        requests.post(WEBHOOK_URL, json=payload)