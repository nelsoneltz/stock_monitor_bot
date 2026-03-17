import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def create_charts():
    # Load configuration
    try:
        with open('stock_thresholds.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Arquivo stock_thresholds.json não encontrado.")
        return

    # Load data
    df = pd.read_csv('stock_data.csv')
    
    # Convert date column
    df['regularMarketTime'] = pd.to_datetime(df['regularMarketTime'])
    
    # Filter last 2 days (Ajustado para garantir que pegamos dados recentes)
    cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=2)
    df = df[df['regularMarketTime'] >= cutoff_date]
    
    tickers = list(config.keys())
    
    for ticker in tickers:
        ticker_data = df[df['symbol'] == ticker].copy()
        
        if ticker_data.empty:
            print(f"No data found for {ticker}")
            continue

        # Date handling: Convert to UTC-3 (Brazil time)
        ticker_data['regularMarketTime'] = ticker_data['regularMarketTime'] - pd.Timedelta(hours=3)
        
        # Sort by time
        ticker_data = ticker_data.sort_values('regularMarketTime')

        # --- O SEGREDO ESTÁ AQUI ---
        # Criamos uma coluna de string para os labels e usamos o range (índice) para o eixo X
        ticker_data['time_label'] = ticker_data['regularMarketTime'].dt.strftime('%d/%m %H:%M')
        x_axis = range(len(ticker_data)) 
        # ---------------------------

        plt.figure(figsize=(14, 7))
        
        # 1. Area: Fill entre Min e Max usando o x_axis sequencial
        plt.fill_between(
            x_axis, 
            ticker_data['regularMarketDayLow'], 
            ticker_data['regularMarketDayHigh'], 
            color='skyblue', 
            alpha=0.2, 
            label='Day Range (Min/Max)'
        )

        # 2. Line: Preço Atual
        plt.plot(
            x_axis, 
            ticker_data['regularMarketPrice'], 
            color='navy', 
            linewidth=2, 
            marker='o', # Adicionei um marcador pequeno para ver os pontos
            markersize=3,
            label='Current Price'
        )

        # 3. Annotations (Otimizadas para não poluir tanto)
        # Vamos anotar apenas 1 a cada 3 pontos para evitar sobreposição excessiva
        for i, (idx, row) in enumerate(ticker_data.iterrows()):
            if i % 2 == 0: # Anota a cada 2 pontos (ajuste conforme necessário)
                plt.annotate(
                    f'{row["regularMarketPrice"]:.2f}',
                    xy=(i, row['regularMarketPrice']),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=8,
                    color='darkblue',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='gray', alpha=0.6)
                )

        # 4. Threshold Line
        ticker_threshold = config.get(ticker)
        if ticker_threshold:
            plt.axhline(
                y=ticker_threshold, 
                color='red', 
                linestyle='--', 
                linewidth=1.5, 
                label=f'Threshold (R$ {ticker_threshold:.2f})',
                alpha=0.8
            )
            
            plt.text(
                0, 
                ticker_threshold, 
                f' Limit: R$ {ticker_threshold:.2f}', 
                color='red', 
                va='bottom', 
                fontsize=9,
                fontweight='bold'
            )

        # Styling
        plt.title(f'Price Analysis: {ticker}', fontsize=14, fontweight='bold')
        plt.xlabel('Time/Date (Trading Sessions Only)')
        plt.ylabel('Price (Local Currency)')
        
        # Ajuste das marcações do eixo X para não ficarem amontoadas
        max_ticks = 12
        step = max(1, len(ticker_data) // max_ticks)
        plt.xticks(
            ticks=list(x_axis)[::step], 
            labels=ticker_data['time_label'].iloc[::step], 
            rotation=45
        )

        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend(loc='upper left')
        
        plt.tight_layout()
        
        # Save
        output_dir = Path('charts')
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / f'{ticker}_chart.png', dpi=150)
        plt.close()
        print(f"Gráfico para {ticker} gerado com sucesso.")

