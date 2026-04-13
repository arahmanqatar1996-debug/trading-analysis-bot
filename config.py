"""
Trading Analysis Bot Configuration
Advanced Technical Analysis Edition
"""

import os

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8269257402:AAEb2RMKL3r2CJQC10H4YBRhFI-rx-PhVhg"
TELEGRAM_CHAT_ID = "-1002986335453"

# Market Data APIs
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance"

# Crypto Pairs
CRYPTO_PAIRS = [
    "BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "DOT", "AVAX",
    "LINK", "MATIC", "BNB", "LTC", "UNI", "ATOM", "XLM", "NEAR"
]

# Forex Pairs
FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "NZD/USD", "USD/CHF",
    "EUR/AUD", "EUR/CAD", "GBP/AUD", "USD/SGD", "USD/HKD"
]

# Binary Options Pairs
BINARY_SIGNAL_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "NZD/USD", "USD/CHF",
    "EUR/AUD", "EUR/CAD", "GBP/AUD", "USD/SGD", "USD/HKD"
]

# Timeframes
TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]

# Analysis Settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2.0

STOCH_K = 14
STOCH_D = 3

CCI_PERIOD = 20

ADX_PERIOD = 14

SUPERTREND_PERIOD = 10
SUPERTREND_MULTIPLIER = 3.0

# Supported Analysis Symbols (for auto-detection)
SUPPORTED_SYMBOLS = CRYPTO_PAIRS + [
    pair.replace("/", "") for pair in FOREX_PAIRS
]

# Bot Commands
BOT_COMMANDS = """
/start - Welcome message
/help - Help guide
/crypto [SYMBOL] - Crypto prices
/forex [PAIR] - Forex prices
/signal [SYMBOL] - Full technical analysis
/binary [PAIR] - Binary options signal
/trending - Trending cryptocurrencies
/all - All markets summary
"""
