import os
from dotenv import load_dotenv
from api import get_stock_price
from charts import create_charts
from notifier import send_discord_message

# Load environment variables
load_dotenv()

def main():
    # Ensure the working directory is the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tickers = ["AURA33", "PETR4", "VALE3"]
    stock_results = []

    print("Starting data collection...")
    for ticker in tickers:
        try:
            price, change, time, res = get_stock_price(ticker)
            stock_results.append({
                'ticker': ticker, 'price': price, 
                'change': change, 'time': time, 'stock_data': res
            })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    print("Generating charts...")
    create_charts() 

    print("Sending notifications...")
    for stock in stock_results:
        send_discord_message(
            stock['price'], stock['change'], 
            stock['time'], stock['ticker'], stock['stock_data']
        )

if __name__ == "__main__":
    main()