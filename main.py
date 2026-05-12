import os
import json
from datetime import date
from dotenv import load_dotenv
import holidays
from api import get_stock_price, purge_old_data
from charts import create_charts
from notifier import send_discord_message

load_dotenv()

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
    br_holidays = holidays.country_holidays("BR")
    if today in br_holidays:
        print(f"Today ({today}) is a Brazilian holiday ({br_holidays[today]}). Market closed, skipping.")
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

        send_discord_message(
            price,
            stock["change"],
            stock["time"],
            ticker,
            stock["stock_data"],
        )
        last_sent[ticker] = price

    save_last_sent(last_sent)


if __name__ == "__main__":
    main()

