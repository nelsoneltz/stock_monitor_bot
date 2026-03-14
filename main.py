import requests
from datetime import datetime, timedelta
import pandas as pd
from config import Config
import os
from charts import create_charts
from dotenv import load_dotenv
load_dotenv()
# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Busca os dados das variáveis de ambiente definidas no GitHub Secrets
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TOKEN = os.environ.get("BRAPI_TOKEN")
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
API_URL = "https://brapi.dev/api/quote/"

config = Config()

def save_data(data):
    # Verifica se o arquivo existe para definir o header
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

def send_discord_message(price, change, time, ticker, stock_data=None):
    threshold = config.get_threshold(ticker)
    image_path = f"charts/{ticker}_chart.png"
    
    content = f"📈 **Cotação {ticker}**\nPreço: R$ {price:.2f}\nVariação: {change:.2f}%\nHora: {time}"
    
    if price <= threshold:
        content += f"\n⚠️ **Abaixo do limite!** <@{DISCORD_USER_ID}>"

    payload = {"content": content}
    abs_change = abs(stock_data['regularMarketChangePercent']) if stock_data else abs(change)
    
    # Envio com imagem ou apenas texto
    if abs_change > 5.0 and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            files = {"file": (f"{ticker}_chart.png", f, "image/png")}
            requests.post(WEBHOOK_URL, data=payload, files=files)
    else:
        requests.post(WEBHOOK_URL, json=payload)

def main():
    # Define o diretório de trabalho como a pasta do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tickers = ["AURA33", "PETR4", "VALE3"]
    stock_results = []

    print("Iniciando coleta de dados...")
    for ticker in tickers:
        try:
            price, change, time, res = get_stock_price(ticker)
            stock_results.append({
                'ticker': ticker, 'price': price, 
                'change': change, 'time': time, 'stock_data': res
            })
        except Exception as e:
            print(f"Erro ao processar {ticker}: {e}")
    
    print("Gerando gráficos...")
    create_charts() 

    print("Enviando notificações...")
    for stock in stock_results:
        send_discord_message(
            stock['price'], stock['change'], 
            stock['time'], stock['ticker'], stock['stock_data']
        )

if __name__ == "__main__":
    main()