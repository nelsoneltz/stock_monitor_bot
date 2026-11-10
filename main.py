import os
import json
from datetime import date
from dotenv import load_dotenv

# Load .env before importing modules that read environment variables at import time
load_dotenv()

import holidays
from api import get_stock_price, purge_old_data
from charts import create_charts
from notifier import send_discord_message

LAST_SENT_FILE = "last_sent.json"


def load_last_sent():
    if os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE) as f:
            return json.load(f)
    return {}


def save_last_sent(data):
    with open(LAST_SENT_FILE, "w") as f:
        json.dump(data, f)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    today = date.today()
    # B3 trading calendar; B3 also has no trading session on Dec 24 and Dec 31
    b3_holidays = holidays.financial_holidays("BVMF")
    if today in b3_holidays:
        print(f"Today ({today}) is a B3 holiday ({b3_holidays[today]}). Market closed, skipping.")
        return
    if (today.month, today.day) in ((12, 24), (12, 31)):
        print(f"Today ({today}) has no B3 trading session. Market closed, skipping.")
        return

    purge_old_data()

    with open("stock_thresholds.json", "r") as f:
        thresholds = json.load(f)
    tickers = list(thresholds.keys())

    stock_results = []

    print("Starting data collection...")
    for ticker in tickers:
        try:
            price, change, time, res = get_stock_price(ticker)
            stock_results.append(
                {
                    "ticker": ticker,
                    "price": price,
                    "change": change,
                    "time": time,
                    "stock_data": res,
                }
            )
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    print("Generating charts...")
    create_charts()

    print("Sending notifications...")
    last_sent = load_last_sent()

    for stock in stock_results:
        ticker = stock["ticker"]
        price = stock["price"]

        if last_sent.get(ticker) == price:
            print(f"Price unchanged for {ticker} (R${price:.2f}), skipping notification")
            continue

        sent = send_discord_message(
            price,
            stock["change"],
            stock["time"],
            ticker,
            stock["stock_data"],
        )
        if sent:
            last_sent[ticker] = price

    save_last_sent(last_sent)


if __name__ == "__main__":
    main()

