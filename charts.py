import json
from datetime import date
from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def create_charts():
    # Load configuration
    try:
        with open("stock_thresholds.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Arquivo stock_thresholds.json não encontrado.")
        return

    # Load data
    df = pd.read_csv("stock_data.csv")

    # Convert date column
    df["regularMarketTime"] = pd.to_datetime(df["regularMarketTime"])

    # Filter last 2 days
    cutoff_date = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=5)
    df = df[df["regularMarketTime"] >= cutoff_date]

    tickers = list(config.keys())

    for ticker in tickers:
        ticker_data = cast(pd.DataFrame, df[df["symbol"] == ticker].copy())
        if len(ticker_data) == 0:
            print(f"No data found for {ticker}")
            continue

        # Date handling: UTC-3
        ticker_data["regularMarketTime"] = ticker_data[
            "regularMarketTime"
        ] - pd.Timedelta(hours=3)
        ticker_data = ticker_data.sort_values(by="regularMarketTime")

        # Criar labels e o eixo X sequencial
        ticker_data["time_label"] = ticker_data["regularMarketTime"].dt.strftime(
            "%d/%m %H:%M"
        )
        ticker_data["date_only"] = ticker_data[
            "regularMarketTime"
        ].dt.date  # Para agrupamento
        x_axis = np.arange(len(ticker_data))
        ticker_data["x_idx"] = x_axis

        plt.figure(figsize=(14, 7))

        # 1. Area: Min/Max
        plt.fill_between(
            x_axis,
            ticker_data["regularMarketDayLow"],
            ticker_data["regularMarketDayHigh"],
            color="skyblue",
            alpha=0.15,
            label="Day Range (Min/Max)",
        )

        # 2. Line: Preço Atual
        plt.plot(
            x_axis,
            ticker_data["regularMarketPrice"],
            color="navy",
            linewidth=2,
            marker="o",
            markersize=3,
            label="Current Price",
        )

        for date_val, group in ticker_data.groupby("date_only"):
            date_val = cast(date, date_val)
            if len(group) > 1:
                # Calculando a regressão linear: y = ax + b
                x = group["x_idx"]
                y = group["regularMarketPrice"]

                # np.polyfit retorna [inclinação, intercepto]
                slope, intercept = np.polyfit(x, y, 1)
                line_y = slope * x + intercept

                # Plota a linha para o intervalo deste dia específico
                plt.plot(
                    x,
                    line_y,
                    color="darkorange",
                    linestyle="-",
                    linewidth=2,
                    alpha=0.8,
                    label=f'Trend {date_val.strftime("%d/%m")}',
                )
        # ----------------------------------------
        # 3. Annotations
        for i, (_, row) in enumerate(ticker_data.iterrows()):
            if i % 2 == 0:
                # Extraímos o preço e garantimos que é um float para o linter
                price = float(row["regularMarketPrice"])

                plt.annotate(
                    f"{price:.2f}",
                    xy=(float(i), price),  # Forçamos a tupla como (float, float)
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    color="darkblue",
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        edgecolor="gray",
                        alpha=0.6,
                    ),
                )

        # 4. Threshold Line
        ticker_threshold = config.get(ticker)
        if ticker_threshold:
            plt.axhline(
                y=ticker_threshold,
                color="red",
                linestyle="--",
                linewidth=1.5,
                label=f"Threshold (R$ {ticker_threshold:.2f})",
                alpha=0.7,
            )
            plt.text(
                0,
                ticker_threshold,
                f" Limit: R$ {ticker_threshold:.2f}",
                color="red",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

        # Styling
        plt.title(
            f"Price Analysis with Daily Trend: {ticker}", fontsize=14, fontweight="bold"
        )
        plt.xlabel("Time/Date (Trading Sessions Only)")
        plt.ylabel("Price (Local Currency)")

        max_ticks = 12
        step = max(1, len(ticker_data) // max_ticks)
        plt.xticks(
            ticks=x_axis[::step],
            labels=ticker_data["time_label"].iloc[::step],
            rotation=45,
        )

        plt.grid(True, linestyle="--", alpha=0.3)
        # Ajuste da legenda para não repetir "Trend" várias vezes se houver muitos dias
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(
            by_label.values(), by_label.keys(), loc="upper left", fontsize="small"
        )

        plt.tight_layout()

        output_dir = Path("charts")
        output_dir.mkdir(exist_ok=True)
        plt.savefig(output_dir / f"{ticker}_chart.png", dpi=150)
        plt.close()
        print(f"Gráfico para {ticker} gerado com sucesso.")
