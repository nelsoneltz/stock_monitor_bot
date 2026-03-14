import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def create_charts():
    # Carregar configuração
    with open('stock_thresholds.json', 'r') as f:
        config = json.load(f)
    
    # Carregar dados
    df = pd.read_csv('stock_data.csv')
    
    # Converter coluna de data
    df['regularMarketTime'] = pd.to_datetime(df['regularMarketTime'])
    
    # Filtrar últimos 2 dias
    cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=2)
    df = df[df['regularMarketTime'] >= cutoff_date]
    
    tickers = list(config.keys())
    
    for ticker in tickers:
        ticker_data = df[df['symbol'] == ticker].copy()
        
        if ticker_data.empty:
            print(f"No data found for {ticker}")
            continue

        # Tratamento de datas: Converter para UTC-3 (horário de Brasília)
        ticker_data['regularMarketTime'] = ticker_data['regularMarketTime'] - pd.Timedelta(hours=3)
        
        # Ordenar por tempo para garantir que o gráfico flua corretamente
        ticker_data = ticker_data.sort_values('regularMarketTime')

        plt.figure(figsize=(12, 6))
        
        # 1. Área: Preenche entre o Mínimo (DayLow) e o Máximo (DayHigh)
        plt.fill_between(
            ticker_data['regularMarketTime'], 
            ticker_data['regularMarketDayLow'], 
            ticker_data['regularMarketDayHigh'], 
            color='skyblue', 
            alpha=0.3, 
            label='Variação do Dia (Mín/Máx)'
        )

        # 2. Linha: Valor Atual (Price)
        plt.plot(
            ticker_data['regularMarketTime'], 
            ticker_data['regularMarketPrice'], 
            color='navy', 
            linewidth=2, 
            label='Preço Atual'
        )

        # 3. Anotações para valores no eixo X
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
        # 4. Linha de Threshold (Limite de Alerta)
        ticker_threshold = config.get(ticker) # Busca o valor no dicionário carregado do JSON
        
        if ticker_threshold:
            plt.axhline(
                y=ticker_threshold, 
                color='red', 
                linestyle='--', 
                linewidth=1.5, 
                label=f'Threshold (R$ {ticker_threshold:.2f})',
                alpha=0.8
            )
            
            # Opcional: Adicionar um texto pequeno acima da linha no canto esquerdo
            plt.text(
                ticker_data['regularMarketTime'].min(), 
                ticker_threshold, 
                f' Limite: R$ {ticker_threshold:.2f}', 
                color='red', 
                va='bottom', 
                fontsize=9,
                fontweight='bold'
            )
        # Estilização
        plt.title(f'Análise de Preço: {ticker}', fontsize=14, fontweight='bold')
        plt.xlabel('Hora/Data')
        plt.ylabel('Preço (Moeda Local)')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        plt.tight_layout()
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M')) # Ex: 13/03 15:00
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        # Salvar
        output_dir = Path('charts')
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / f'{ticker}_chart.png')
        plt.close()
        
        print(f"Chart created for {ticker} with area range.")