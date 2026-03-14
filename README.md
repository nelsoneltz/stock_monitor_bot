# 📈 Discord Stock Bot

Automated Brazilian stock market monitor that sends price alerts and charts to Discord via webhooks.

## Features

- **Real-time monitoring** - Tracks AURA33, PETR4, VALE3 stocks via Brapi API
- **Price alerts** - Mentions users when stocks fall below configured thresholds
- **Smart charts** - Generates visual trends for stocks with >5% daily change
- **Historical data** - Stores all price data in CSV format
- **Auto-scheduling** - Runs every 30min during market hours (GitHub Actions)

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment** (create `.env` file)
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
BRAPI_TOKEN=your_brapi_token
DISCORD_USER_ID=your_discord_user_id
```

3. **Set price thresholds** (edit `stock_thresholds.json`)
```json
{
    "AURA33": 130.0,
    "PETR4": 29.0,
    "VALE3": 70.0
}
```

4. **Run**
```bash
python main.py
```

## How It Works

```
1. Fetch prices → 2. Save to CSV → 3. Generate charts → 4. Send to Discord
```

### Architecture

- **`main.py`** - Orchestrates workflow: data collection → charting → notifications
- **`api.py`** - Fetches stock prices from Brapi API, saves to CSV
- **`charts.py`** - Creates matplotlib charts (2-day history with thresholds)
- **`notifier.py`** - Sends Discord messages with optional chart attachments
- **`config.py`** - Manages stock price thresholds from JSON

### Discord Output

**Normal message:**
```
📈 Cotação PETR4
Preço: R$ 38.45
Variação: -2.34%
Hora: 2026-03-13 15:30:00
```

**Alert message (below threshold):**
```
📈 Cotação PETR4
Preço: R$ 28.50
Variação: -6.34%
Hora: 2026-03-13 15:30:00
⚠️ Abaixo do limite! @user
[Chart attached if variation > 5%]
```

## Configuration

**Add stocks** - Edit `main.py`:
```python
tickers = ["AURA33", "PETR4", "VALE3", "BBAS3"]
```

**Change alert thresholds** - Edit `stock_thresholds.json` or use config API:
```python
from config import Config
config = Config()
config.set_threshold("PETR4", 30.0)
```

**Chart sensitivity** - Edit `notifier.py`:
```python
if abs_change > 5.0:  # Change to desired %
```

## Automation

The bot runs automatically via GitHub Actions every 30min during Brazilian market hours (10am-5pm BRT, Mon-Fri).

**Manual trigger:** Go to Actions tab → Run workflow

**Required secrets:**
- `BRAPI_TOKEN`
- `DISCORD_WEBHOOK_URL`
- `DISCORD_USER_ID`

## Data Storage

- **`stock_data.csv`** - Historical price records (all columns from Brapi API)
- **`charts/*.png`** - Generated price visualizations
- **`stock_thresholds.json`** - Alert threshold configuration

## Tech Stack

- Python 3.13
- pandas, matplotlib, requests
- Brapi API (Brazilian stocks)
- Discord Webhooks

## Troubleshooting

**CSV parsing error:** Delete `stock_data.csv` to rebuild from scratch

**Charts not generating:** Ensure `charts/` folder exists or set different threshold

**No Discord messages:** Verify webhook URL and permissions

---

*For educational purposes only. Not financial advice.*