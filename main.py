import os
from dotenv import load_dotenv
from api import get_stock_price
from charts import create_charts
from notifier import send_discord_message

# Carrega variáveis de ambiente
load_dotenv()

def main():
    # Garante que o diretório de execução é o do script
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