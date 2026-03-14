# 📈 Discord Stock Bot

A Python automation bot that monitors Brazilian stock market prices using the Brapi API and sends real-time updates to Discord with interactive price charts.

## 🎯 Overview

This bot automatically collects stock market data, stores historical prices, generates visual charts, and sends formatted notifications to Discord. It's designed to help investors track their portfolio and receive alerts when stocks reach critical price levels.

## ✨ Features

- **Multi-Stock Monitoring**: Tracks multiple Brazilian stocks simultaneously (AURA33, PETR4, VALE3)
- **Automated Data Collection**: Fetches real-time prices from Brapi API
- **Historical Data Storage**: Maintains CSV records for trend analysis
- **Smart Chart Generation**: Creates visual price charts for stocks with significant changes (>5%)
- **Price Alert System**: Sends user mentions when stocks fall below configured thresholds
- **Timezone Intelligence**: Automatically converts UTC timestamps to Brazilian time (UTC-3)
- **Secure Configuration**: Uses environment variables for sensitive credentials

## 🏗️ Project Structure

```
discord_acao_bot/
├── main.py              # Core bot logic and orchestration
├── charts.py            # Chart generation using matplotlib
├── config.py            # Configuration and threshold management
├── stock_data.csv       # Historical price data storage
├── .env                 # Environment variables (not in repo)
├── .gitignore          # Git ignore rules
└── charts/             # Generated chart images
    ├── AURA33_chart.png
    ├── PETR4_chart.png
    └── VALE3_chart.png
```

## 🔧 How It Works

### 1. **Environment Setup**
```python
# Loads credentials from .env file
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TOKEN = os.environ.get("BRAPI_TOKEN")
```

### 2. **Data Collection Pipeline**

**`get_stock_price(ticker)`**
- Makes API request to Brapi: `https://brapi.dev/api/quote/{ticker}`
- Extracts price, percentage change, and timestamp
- Converts UTC time to Brazilian timezone (UTC-3)
- Returns formatted data for processing

**`save_data(data)`**
- Converts API response to pandas DataFrame
- Removes unnecessary columns (like `logourl`)
- Appends data to `stock_data.csv` with proper headers
- Ensures data consistency across runs

### 3. **Chart Generation**

**`create_charts()`** (in `charts.py`)
- Reads historical data from CSV
- Generates price trend visualizations
- Saves charts as PNG images in `charts/` directory
- Used for stocks with significant daily changes

### 4. **Discord Notification System**

**`send_discord_message(price, change, time, ticker, stock_data)`**
- Formats message with stock information
- Checks price against configured thresholds
- Sends user mention (`<@185166993236688897>`) if price drops below limit
- Attaches chart image if variation exceeds 5%
- Posts to Discord webhook

**Message Format:**
```
📈 **Cotação PETR4**
Preço: R$ 38.45
Variação: -2.34%
Hora: 2026-03-13 15:30:00
⚠️ **Abaixo do limite!** @user
```

### 5. **Main Execution Flow**

```python
def main():
    1. Set working directory to script location
    2. Iterate through ticker list ["AURA33", "PETR4", "VALE3"]
    3. Fetch current prices for each stock
    4. Store results in temporary list
    5. Generate charts for all stocks
    6. Send Discord notifications with charts
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Discord webhook URL
- Brapi API token (free at https://brapi.dev)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd discord_acao_bot
```

2. **Install dependencies**
```bash
pip install requests pandas matplotlib python-dotenv
```

3. **Configure environment variables**

Create a `.env` file:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
BRAPI_TOKEN=your_brapi_token_here
```

4. **Run the bot**
```bash
python main.py
```

## 📊 Configuration

### Adding New Stocks

Edit `main.py`, line 68:
```python
tickers = ["AURA33", "PETR4", "VALE3", "BBAS3"]  # Add more tickers
```

### Setting Price Thresholds

Edit `config.py` to define alert levels:
```python
def get_threshold(self, ticker):
    thresholds = {
        "AURA33": 10.50,
        "PETR4": 35.00,
        "VALE3": 60.00
    }
    return thresholds.get(ticker, 0)
```

### Chart Sensitivity

Modify the variation threshold in `main.py`, line 58:
```python
if abs_change > 5.0 and os.path.exists(image_path):  # Change 5.0 to desired percentage
```

## 🤖 Automation

### GitHub Actions (Recommended)

Create `.github/workflows/stock_bot.yml`:
```yaml
name: Stock Price Monitor

on:
  schedule:
    - cron: '0 13-20 * * 1-5'  # Mon-Fri, 10am-5pm BRT

jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
          BRAPI_TOKEN: ${{ secrets.BRAPI_TOKEN }}
```

### Cron (Local/Server)

```bash
# Edit crontab
crontab -e

# Run every hour during market hours (10am-5pm BRT, Mon-Fri)
0 10-17 * * 1-5 cd /path/to/discord_acao_bot && /usr/bin/python3 main.py
```

## 📁 Data Storage

### CSV Format (`stock_data.csv`)
```csv
symbol,shortName,longName,currency,regularMarketPrice,regularMarketChange,regularMarketChangePercent,...
PETR4,Petrobras PN,Petróleo Brasileiro S.A.,BRL,38.45,-0.92,-2.34,...
```

**Columns include:**
- Basic info: symbol, shortName, longName, currency
- Price data: regularMarketPrice, regularMarketChange, regularMarketChangePercent
- Market metrics: marketCap, regularMarketVolume, regularMarketDayHigh, regularMarketDayLow
- Historical: fiftyTwoWeekLow, fiftyTwoWeekHigh, twoHundredDayAverage

## 🔒 Security Best Practices

1. **Never commit credentials** - Use `.env` file (added to `.gitignore`)
2. **Use GitHub Secrets** for automation workflows
3. **Rotate tokens** periodically
4. **Limit webhook permissions** to posting messages only

## 🐛 Troubleshooting

### "ParserError: Expected X fields, saw Y"
- **Cause**: CSV file has inconsistent column structure
- **Fix**: Delete `stock_data.csv` and run again for fresh data

### Charts not appearing
- **Check**: `charts/` directory exists
- **Check**: Variation exceeds 5% threshold
- **Fix**: Create directory: `mkdir -p charts`

### Discord messages not sending
- **Verify**: Webhook URL is correct and active
- **Check**: Webhook has proper permissions in Discord channel

## 📝 Output Examples

**Console Output:**
```
Iniciando coleta de dados...
Gerando gráficos...
Enviando notificações...
```

**Discord Message (High Variation):**
```
📈 **Cotação PETR4**
Preço: R$ 38.45
Variação: -6.34%
Hora: 2026-03-13 15:30:00
⚠️ **Abaixo do limite!** @user
[Chart Image Attached]
```

**Discord Message (Low Variation):**
```
📈 **Cotação VALE3**
Preço: R$ 65.20
Variação: 1.23%
Hora: 2026-03-13 15:30:00
```

## 🛠️ Technical Stack

- **Python 3.13** - Core language
- **requests** - HTTP API calls
- **pandas** - Data manipulation and CSV handling
- **matplotlib** - Chart generation
- **python-dotenv** - Environment variable management
- **Brapi API** - Stock market data source
- **Discord Webhooks** - Notification delivery

## 📈 Future Enhancements

- [ ] Add support for more stock exchanges (US, Europe)
- [ ] Implement moving average indicators
- [ ] Create web dashboard for historical data
- [ ] Add email notifications as backup
- [ ] Support for cryptocurrency tracking
- [ ] Machine learning price predictions
- [ ] Portfolio performance summaries

## 📄 License

MIT License - Feel free to use and modify for personal or commercial use.

## 👤 Author

Created for automated stock market monitoring and portfolio management.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Note**: This bot is for informational purposes only. Always do your own research before making investment decisions.