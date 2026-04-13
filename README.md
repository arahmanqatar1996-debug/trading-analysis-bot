# Trading Analysis Bot

A Telegram bot for analyzing Binary Options, Crypto, and Forex markets.

## Features

- 📊 **Live Market Data** - Real-time crypto, forex prices
- 💎 **Crypto Analysis** - BTC, ETH, SOL, ADA and more
- 💱 **Forex Rates** - EUR/USD, GBP/USD, USD/JPY
- 🎯 **Binary Options Signals** - CALL/PUT recommendations
- 🔥 **Trending Assets** - Top performers
- 📈 **Price Alerts** - Get notified on price changes

## Setup

1. **Get Telegram Bot Token** from @BotFather
2. **Get your Chat ID** from @userinfobot
3. **Update config.py** with your credentials
4. **Run the bot**

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Help guide |
| `/crypto` | All crypto prices |
| `/crypto BTC` | Specific crypto |
| `/forex` | All forex pairs |
| `/forex EUR/USD` | Specific pair |
| `/binary` | Binary options signals |
| `/signal BTC` | Trading signal |
| `/trending` | Top trending assets |
| `/all` | All markets summary |

## Deploy to Render.com

1. Push code to GitHub
2. Connect GitHub to Render.com
3. Create new Web Service
4. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. Deploy!

## Requirements

- Python 3.8+
- requests
- python-dotenv

## Disclaimer

⚠️ This bot is for educational purposes only. Trading involves risk.
