import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def get_week_stats():
    df = pd.read_csv("stock_data.csv")
    df["regularMarketTime"] = pd.to_datetime(df["regularMarketTime"], utc=True)

    now = datetime.now(timezone.utc)
    days_since_monday = now.weekday()
    monday = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    week_df = df[df["regularMarketTime"] >= monday]

    stats = {}
    for ticker in week_df["symbol"].unique():
        t = week_df[week_df["symbol"] == ticker].sort_values("regularMarketTime")
        if t.empty:
            continue

        open_price = t.iloc[0]["regularMarketPrice"]
        close_price = t.iloc[-1]["regularMarketPrice"]
        week_high = t["regularMarketDayHigh"].max()
        week_low = t["regularMarketDayLow"].min()
        change_pct = ((close_price - open_price) / open_price) * 100
        avg_price = t["regularMarketPrice"].mean()
        readings = len(t)

        stats[ticker] = {
            "open": open_price,
            "close": close_price,
            "high": week_high,
            "low": week_low,
            "change_pct": change_pct,
            "avg": avg_price,
            "readings": readings,
        }

    return stats, monday


def send_weekly_report():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    stats, monday = get_week_stats()
    if not stats:
        print("No data for the week, skipping report.")
        return

    monday_brt = monday - timedelta(hours=3)
    friday_brt = monday_brt + timedelta(days=4)
    week_range = f"{monday_brt.strftime('%d/%m')} – {friday_brt.strftime('%d/%m/%Y')}"

    lines = [f"📊 **Relatório Semanal** | {week_range}\n"]

    for ticker, s in sorted(stats.items()):
        emoji = "📈" if s["change_pct"] >= 0 else "📉"
        sign = "+" if s["change_pct"] >= 0 else ""
        lines.append(
            f"{emoji} **{ticker}**\n"
            f"Abertura: R${s['open']:.2f}  →  Fechamento: R${s['close']:.2f}\n"
            f"Máxima: R${s['high']:.2f}  |  Mínima: R${s['low']:.2f}\n"
            f"Variação semanal: {sign}{s['change_pct']:.2f}%  |  Média: R${s['avg']:.2f}\n"
        )

    content = "\n".join(lines)
    response = requests.post(WEBHOOK_URL, json={"content": content}, timeout=10)
    if response.status_code in (200, 204):
        print("Weekly report sent successfully.")
    else:
        print(f"Failed to send weekly report: {response.status_code} {response.text}")


if __name__ == "__main__":
    send_weekly_report()
