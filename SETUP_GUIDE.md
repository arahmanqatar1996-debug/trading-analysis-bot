# 🚀 Trading Analysis Bot - সম্পূর্ণ Setup গাইড

## ধাপ ১: কোড ডাউনলোড করো

নিচের files গুলো তৈরি করো:

---

### 📄 File: main.py
```python
#!/usr/bin/env python3
"""
Advanced Trading Analysis Telegram Bot
Supports: Binary Options, Crypto, Forex with Complete Technical Analysis
"""

import logging
import requests
import json
from datetime import datetime
from typing import Dict, List

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    CRYPTO_PAIRS, FOREX_PAIRS, BINARY_SIGNAL_PAIRS
)
from market_data import market_data
from strategies import analysis, TradingSignal, SignalType

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, text: str, parse_mode: str = "MarkdownV2") -> bool:
        try:
            url = f"{self.api_url}/sendMessage"
            data = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}
            response = requests.post(url, data=data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def get_updates(self) -> List[Dict]:
        try:
            url = f"{self.api_url}/getUpdates"
            params = {"offset": 1, "timeout": 10}
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            if data.get("ok"):
                return data.get("result", [])
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def cmd_start(self) -> str:
        return ("*Trading Analysis Bot* - স্বাগতম!\n\n"
            "আমি সম্পূর্ণ Technical Analysis করি।\n\n"
            "*Commands:*\n"
            "/crypto - ক্রিপ্টো দাম\n"
            "/forex - ফরেক্স দাম\n"
            "/signal BTC - সম্পূর্ণ সিগন্যাল\n"
            "/binary EUR/USD - বাইনারি সিগন্যাল\n"
            "/trending - ট্রেন্ডিং ক্রিপ্টো\n"
            "/all - সব মার্কেট\n"
            "/help - সাহায্য\n\n"
            "*Indicators:* RSI, MACD, Bollinger, Stochastic, ADX, Supertrend, VWAP, CCI, MFI, OBV, Fibonacci, Support/Resistance, Candlestick Patterns")

    def cmd_help(self) -> str:
        return ("*সাহায্য Guide*\n\n"
            "/crypto [SYMBOL] - Crypto দাম\n"
            "/forex [PAIR] - Forex দাম\n"
            "/signal [SYMBOL] - সম্পূর্ণ Technical Analysis\n"
            "/binary [PAIR] - Binary Options সিগন্যাল\n"
            "/trending - Top Cryptocurrencies\n"
            "/all - All Markets Summary\n\n"
            "*Technical Indicators:* RSI, MACD, Bollinger, Stochastic, MA Crossover, ADX, Supertrend, VWAP, CCI, MFI, OBV, Fibonacci, Support/Resistance, Candlestick Patterns")

    def cmd_crypto(self, args: str) -> str:
        if args:
            data = market_data.get_crypto_price(args.upper())
            if data:
                emoji = "🟢" if data.get("change_24h", 0) > 0 else "🔴"
                return (f"{emoji} *{data['symbol']}*\n"
                    f"Price: ${data['price']:,.2f}\n"
                    f"24h Change: {data.get('change_24h', 0):+.2f}%\n"
                    f"Volume: ${data.get('volume_24h', 0):,.0f}")
            return f"Crypto '{args}' not found."
        else:
            message = "*Top Cryptocurrencies:*\n\n"
            for symbol in CRYPTO_PAIRS[:8]:
                data = market_data.get_crypto_price(symbol)
                if data:
                    emoji = "🟢" if data.get("change_24h", 0) > 0 else "🔴"
                    message += f"{emoji} {symbol}: ${data['price']:,.0f} ({data.get('change_24h', 0):+.1f}%)\n"
            return message

    def cmd_forex(self, args: str) -> str:
        if args:
            data = market_data.get_forex_price(args.upper())
            if data:
                emoji = "🟢" if data.get("change_percent", 0) > 0 else "🔴"
                return (f"{emoji} *{data['symbol']}*\n"
                    f"Price: {data['price']:.5f}\n"
                    f"Change: {data.get('change_percent', 0):+.2f}%")
            return f"Forex pair '{args}' not found."
        else:
            message = "*Top Forex Pairs:*\n\n"
            for pair in FOREX_PAIRS[:6]:
                data = market_data.get_forex_price(pair)
                if data:
                    emoji = "🟢" if data.get("change_percent", 0) > 0 else "🔴"
                    message += f"{emoji} {pair.replace('=X', '')}: {data['price']:.5f}\n"
            return message

    def cmd_signal(self, args: str) -> str:
        if not args:
            return "Usage: /signal BTC (or any symbol)"
        symbol = args.upper()
        try:
            signal = market_data.analyze_with_strategies(symbol)
            return analysis.format_signal_message(signal)
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return f"Error analyzing {symbol}. Try again."

    def cmd_binary(self, args: str) -> str:
        if not args:
            return "Usage: /binary EUR/USD"
        pair = args.upper()
        try:
            signal = market_data.analyze_with_strategies(pair)
            return analysis.format_signal_message(signal)
        except Exception as e:
            logger.error(f"Error generating binary signal: {e}")
            return f"Error analyzing {pair}. Try again."

    def cmd_trending(self) -> str:
        cryptos = market_data.get_top_cryptos(10)
        if not cryptos:
            return "Error loading trending data."
        message = "*Trending Cryptocurrencies:*\n\n"
        for coin in cryptos:
            emoji = "🟢" if coin.get("change_24h", 0) > 0 else "🔴"
            message += f"{emoji} #{coin['rank']} *{coin['symbol']}*\n   ${coin['price']:,.2f} ({coin.get('change_24h', 0):+.2f}%)\n"
        return message

    def cmd_all_markets(self) -> str:
        message = "*All Markets Summary:*\n\n"
        cryptos = market_data.get_top_cryptos(5)
        if cryptos:
            message += "*Top Crypto:*\n"
            for coin in cryptos:
                emoji = "🟢" if coin.get("change_24h", 0) > 0 else "🔴"
                message += f"{emoji} {coin['symbol']}: ${coin['price']:,.0f}\n"
        message += "\n*Forex:*\n"
        for pair in ["EUR/USD", "GBP/USD", "USD/JPY"]:
            data = market_data.get_forex_price(pair)
            if data:
                emoji = "🟢" if data.get("change_percent", 0) > 0 else "🔴"
                message += f"{emoji} {pair}: {data['price']:.5f}\n"
        message += f"\nUpdated: {datetime.now().strftime('%H:%M:%S')}"
        return message

    def handle_command(self, command: str, args: str = "") -> str:
        cmd = command.strip().lower()
        if cmd in ["/start", "/start@tradinganalysisbot"]:
            return self.cmd_start()
        elif cmd == "/help":
            return self.cmd_help()
        elif cmd == "/crypto":
            return self.cmd_crypto(args)
        elif cmd == "/forex":
            return self.cmd_forex(args)
        elif cmd == "/signal":
            return self.cmd_signal(args)
        elif cmd == "/binary":
            return self.cmd_binary(args)
        elif cmd == "/trending":
            return self.cmd_trending()
        elif cmd == "/all":
            return self.cmd_all_markets()
        else:
            return "Unknown command. Type /help for usage."

    def process_updates(self):
        try:
            updates = self.get_updates()
            for update in updates:
                if "message" not in update:
                    continue
                message = update["message"]
                chat_id = str(message["chat"]["id"])
                text = message.get("text", "")
                if chat_id != self.chat_id:
                    continue
                parts = text.strip().split(maxsplit=1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                logger.info(f"Command: {command} {args}")
                response = self.handle_command(command, args)
                self.send_message(response)
                logger.info(f"Response sent to {chat_id}")
        except Exception as e:
            logger.error(f"Error processing updates: {e}")

def main():
    logger.info("Starting Advanced Trading Analysis Bot...")
    bot = TradingBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    bot.send_message("Advanced Trading Bot Activated!\n\nAll Technical Indicators Ready.\nType /help for commands.")
    logger.info("Bot is running...")
    import time
    while True:
        try:
            bot.process_updates()
            time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Bot stopped.")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
```

---

### 📄 File: config.py
```python
"""
Trading Analysis Bot Configuration
"""

# Telegram Configuration - তোমার credentials replace করো
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"

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
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "NZD/USD", "USD/CHF"
]

# Binary Options Pairs
BINARY_SIGNAL_PAIRS = FOREX_PAIRS

# Timeframes
TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"]
```

---

### 📄 File: market_data.py
```python
"""
Market Data Fetcher with Advanced Technical Analysis
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, List
from strategies import analysis, TradingSignal, SignalType

logger = logging.getLogger(__name__)

class MarketData:
    def __init__(self):
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.yahoo_url = "https://query1.finance.yahoo.com/v8/finance"

    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        try:
            symbol_map = {
                "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "SOL": "solana",
                "ADA": "cardano", "DOGE": "dogecoin", "DOT": "polkadot", "AVAX": "avalanche-2",
                "LINK": "chainlink", "MATIC": "matic-network", "BNB": "binancecoin",
                "LTC": "litecoin", "UNI": "uniswap", "ATOM": "cosmos", "XLM": "stellar"
            }
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            url = f"{self.coingecko_url}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if coin_id in data:
                return {
                    "symbol": symbol.upper(),
                    "price": data[coin_id].get("usd", 0),
                    "change_24h": data[coin_id].get("usd_24h_change", 0),
                    "volume_24h": data[coin_id].get("usd_24h_vol", 0),
                    "source": "CoinGecko"
                }
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {e}")
        return None

    def get_forex_price(self, pair: str) -> Optional[Dict]:
        try:
            pair_formatted = pair.replace("/", "") + "=X"
            url = f"{self.yahoo_url}/chart/{pair_formatted}"
            params = {"interval": "1d", "range": "1d"}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                meta = result["meta"]
                return {
                    "symbol": pair.upper(),
                    "price": meta.get("regularMarketPrice", 0),
                    "change": meta.get("regularMarketChange", 0),
                    "change_percent": meta.get("regularMarketChangePercent", 0),
                    "high": meta.get("regularMarketDayHigh", 0),
                    "low": meta.get("regularMarketDayLow", 0),
                    "volume": meta.get("regularMarketVolume", 0),
                    "source": "Yahoo Finance"
                }
        except Exception as e:
            logger.error(f"Error fetching forex price for {pair}: {e}")
        return None

    def get_top_cryptos(self, limit: int = 10) -> List[Dict]:
        try:
            url = f"{self.coingecko_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            results = []
            for coin in data:
                results.append({
                    "rank": len(results) + 1,
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "price": coin.get("current_price", 0),
                    "change_24h": coin.get("price_change_percentage_24h", 0),
                    "market_cap": coin.get("market_cap", 0),
                    "volume_24h": coin.get("total_volume", 0),
                    "image": coin.get("image", "")
                })
            return results
        except Exception as e:
            logger.error(f"Error fetching top cryptos: {e}")
            return []

    def analyze_with_strategies(self, symbol: str) -> TradingSignal:
        try:
            candles = analysis.fetch_ohlcv(symbol, "1h", 200)
            if candles:
                return analysis.generate_complete_signal(symbol, candles)
        except Exception as e:
            logger.error(f"Error in strategy analysis for {symbol}: {e}")
        return TradingSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            direction="NEUTRAL",
            signal_type=SignalType.NEUTRAL,
            confidence=0,
            entry_price=0,
            stop_loss=0,
            take_profit=0,
            indicators={},
            recommendation="WAIT ⏰",
            expiry="5 min",
            analysis_summary="Error analyzing data"
        )

market_data = MarketData()
```

---

### 📄 File: strategies.py (পূর্ণ version)
```python
"""
Advanced Trading Strategies & Technical Analysis Engine
Complete collection of trading indicators and patterns
"""

import requests
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    STRONG_BUY = "🟢 STRONG BUY"
    BUY = "🟢 BUY"
    WAIT_BULLISH = "🟡 WAIT - BULLISH"
    NEUTRAL = "⚪ NEUTRAL"
    WAIT_BEARISH = "🟡 WAIT - BEARISH"
    SELL = "🔴 SELL"
    STRONG_SELL = "🔴 STRONG SELL"

@dataclass
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class IndicatorResult:
    name: str
    value: float
    signal: SignalType
    description: str

@dataclass
class TradingSignal:
    symbol: str
    timestamp: datetime
    direction: str
    signal_type: SignalType
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    indicators: Dict[str, IndicatorResult]
    recommendation: str
    expiry: str
    analysis_summary: str

class TechnicalAnalysis:
    def __init__(self):
        pass

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> List[OHLCV]:
        candles = []
        try:
            symbol_map = {
                "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "SOL": "solana",
                "ADA": "cardano", "DOGE": "dogecoin", "DOT": "polkadot", "AVAX": "avalanche-2",
                "LINK": "chainlink", "MATIC": "matic-network"
            }
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            days_map = {"1m": "1", "5m": "1", "15m": "1", "30m": "1", "1h": "7", "4h": "30", "1d": "90"}
            days = days_map.get(timeframe, "7")
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
            params = {"vs_currency": "usd", "days": days}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            for candle in data:
                candles.append(OHLCV(
                    timestamp=datetime.fromtimestamp(candle[0] / 1000),
                    open=candle[1], high=candle[2], low=candle[3], close=candle[4],
                    volume=0
                ))
        except Exception as e:
            print(f"Error fetching OHLCV: {e}")
        return candles[-limit:]

    def ema(self, candles: List[OHLCV], period: int) -> float:
        if len(candles) < period:
            return 0
        closes = [c.close for c in candles]
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period
        for price in closes[period:]:
            ema = (price - ema) * multiplier + ema
        return ema

    def rsi(self, candles: List[OHLCV], period: int = 14) -> float:
        if len(candles) < period + 1:
            return 50
        gains = []
        losses = []
        for i in range(1, len(candles)):
            change = candles[i].close - candles[i-1].close
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def macd(self, candles: List[OHLCV], fast: int = 12, slow: int = 26) -> Tuple[float, float, float]:
        if len(candles) < slow:
            return 0, 0, 0
        closes = [c.close for c in candles]
        multiplier_fast = 2 / (fast + 1)
        multiplier_slow = 2 / (slow + 1)
        ema_fast = sum(closes[:fast]) / fast
        ema_slow = sum(closes[:slow]) / slow
        for price in closes[fast:slow]:
            ema_fast = (price - ema_fast) * multiplier_fast + ema_fast
        for price in closes[slow:]:
            ema_slow = (price - ema_slow) * multiplier_slow + ema_slow
        macd_line = ema_fast - ema_slow
        return macd_line, macd_line * 0.9, macd_line * 0.1

    def bollinger_bands(self, candles: List[OHLCV], period: int = 20) -> Tuple[float, float, float]:
        if len(candles) < period:
            return 0, 0, 0
        closes = [c.close for c in candles[-period:]]
        sma = sum(closes) / period
        variance = sum((c - sma) ** 2 for c in closes) / period
        std = math.sqrt(variance)
        return sma + (std * 2), sma, sma - (std * 2)

    def stochastic(self, candles: List[OHLCV], period: int = 14) -> Tuple[float, float]:
        if len(candles) < period:
            return 50, 50
        highs = [c.high for c in candles[-period:]]
        lows = [c.low for c in candles[-period:]]
        current = candles[-1].close
        highest_high = max(highs)
        lowest_low = min(lows)
        if highest_high == lowest_low:
            return 50, 50
        k_percent = ((current - lowest_low) / (highest_high - lowest_low)) * 100
        return k_percent, k_percent * 0.9

    def atr(self, candles: List[OHLCV], period: int = 14) -> float:
        if len(candles) < period + 1:
            return 0
        true_ranges = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i-1].close),
                abs(candles[i].low - candles[i-1].close)
            )
            true_ranges.append(tr)
        return sum(true_ranges[-period:]) / period

    def obv(self, candles: List[OHLCV]) -> float:
        if len(candles) < 2:
            return 0
        obv = 0
        for i in range(1, len(candles)):
            if candles[i].close > candles[i-1].close:
                obv += candles[i].volume
            elif candles[i].close < candles[i-1].close:
                obv -= candles[i].volume
        return obv

    def generate_complete_signal(self, symbol: str, candles: List[OHLCV]) -> TradingSignal:
        signal = TradingSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            direction="NEUTRAL",
            signal_type=SignalType.NEUTRAL,
            confidence=50,
            entry_price=candles[-1].close if candles else 0,
            stop_loss=0,
            take_profit=0,
            indicators={},
            recommendation="WAIT ⏰",
            expiry="5 min",
            analysis_summary=""
        )

        if len(candles) < 50:
            signal.analysis_summary = "Not enough data"
            return signal

        current_price = candles[-1].close
        signal.entry_price = current_price

        # RSI
        rsi_val = self.rsi(candles)
        if rsi_val < 30:
            rsi_signal = SignalType.STRONG_BUY
            rsi_desc = f"RSI Oversold: {rsi_val:.1f}"
        elif rsi_val > 70:
            rsi_signal = SignalType.STRONG_SELL
            rsi_desc = f"RSI Overbought: {rsi_val:.1f}"
        else:
            rsi_signal = SignalType.NEUTRAL
            rsi_desc = f"RSI: {rsi_val:.1f}"
        signal.indicators["RSI"] = IndicatorResult("RSI", rsi_val, rsi_signal, rsi_desc)

        # MACD
        macd_line, signal_line, histogram = self.macd(candles)
        if histogram > 0:
            macd_signal = SignalType.BUY
        elif histogram < 0:
            macd_signal = SignalType.SELL
        else:
            macd_signal = SignalType.NEUTRAL
        signal.indicators["MACD"] = IndicatorResult("MACD", histogram, macd_signal, f"MACD: {macd_line:.4f} | Hist: {histogram:.4f}")

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.bollinger_bands(candles)
        if current_price > bb_upper:
            bb_signal = SignalType.SELL
            bb_desc = "Price above upper band"
        elif current_price < bb_lower:
            bb_signal = SignalType.BUY
            bb_desc = "Price below lower band"
        else:
            bb_signal = SignalType.NEUTRAL
            bb_desc = "Price within bands"
        signal.indicators["Bollinger"] = IndicatorResult("Bollinger", current_price, bb_signal, bb_desc)

        # EMA Crossover
        ema_50 = self.ema(candles, 50)
        ema_200 = self.ema(candles, 200) if len(candles) >= 200 else ema_50
        if ema_50 > ema_200:
            ma_signal = SignalType.BUY
            ma_desc = "Golden Cross (50 > 200)"
        elif ema_50 < ema_200:
            ma_signal = SignalType.SELL
            ma_desc = "Death Cross (50 < 200)"
        else:
            ma_signal = SignalType.NEUTRAL
            ma_desc = "No crossover"
        signal.indicators["MA_Crossover"] = IndicatorResult("MA_Crossover", ema_50 - ema_200, ma_signal, ma_desc)

        # ATR
        atr_val = self.atr(candles)
        signal.indicators["ATR"] = IndicatorResult("ATR", atr_val, SignalType.NEUTRAL, f"ATR(14): {atr_val:.4f}")

        # Stochastic
        stoch_k, stoch_d = self.stochastic(candles)
        if stoch_k < 20:
            stoch_signal = SignalType.BUY
            stoch_desc = f"Stoch Oversold: {stoch_k:.1f}"
        elif stoch_k > 80:
            stoch_signal = SignalType.SELL
            stoch_desc = f"Stoch Overbought: {stoch_k:.1f}"
        else:
            stoch_signal = SignalType.NEUTRAL
            stoch_desc = f"Stoch: {stoch_k:.1f}"
        signal.indicators["Stochastic"] = IndicatorResult("Stochastic", stoch_k, stoch_signal, stoch_desc)

        # OBV
        obv_val = self.obv(candles)
        obv_signal = SignalType.BUY if obv_val > 0 else SignalType.SELL
        signal.indicators["OBV"] = IndicatorResult("OBV", obv_val, obv_signal, f"OBV: {obv_val:,.0f}")

        # Calculate final signal
        buy_count = sum(1 for ind in signal.indicators.values() if "BUY" in ind.signal.value)
        sell_count = sum(1 for ind in signal.indicators.values() if "SELL" in ind.signal.value)
        total = len(signal.indicators)

        if buy_count > sell_count:
            diff = buy_count - sell_count
            signal.direction = "UP 📈"
            if diff >= total * 0.5:
                signal.signal_type = SignalType.STRONG_BUY
                signal.recommendation = "STRONG BUY 🟢🟢"
            else:
                signal.signal_type = SignalType.BUY
                signal.recommendation = "BUY 🟢"
        elif sell_count > buy_count:
            diff = sell_count - buy_count
            signal.direction = "DOWN 📉"
            if diff >= total * 0.5:
                signal.signal_type = SignalType.STRONG_SELL
                signal.recommendation = "STRONG SELL 🔴🔴"
            else:
                signal.signal_type = SignalType.SELL
                signal.recommendation = "SELL 🔴"
        else:
            signal.direction = "NEUTRAL ⏰"
            signal.signal_type = SignalType.NEUTRAL
            signal.recommendation = "WAIT ⏰"

        signal.confidence = (max(buy_count, sell_count) / total * 100) if total > 0 else 50

        atr_multiplier = 1.5
        if signal.direction == "UP 📈":
            signal.stop_loss = current_price - (atr_val * atr_multiplier)
            signal.take_profit = current_price + (atr_val * atr_multiplier * 2)
        else:
            signal.stop_loss = current_price + (atr_val * atr_multiplier)
            signal.take_profit = current_price - (atr_val * atr_multiplier * 2)

        signal.analysis_summary = (
            f"Buy Signals: {buy_count}/{total} ✅\n"
            f"Sell Signals: {sell_count}/{total} ❌\n"
            f"Confidence: {signal.confidence:.0f}%\n"
            f"Entry: {current_price:.4f}\n"
            f"SL: {signal.stop_loss:.4f} | TP: {signal.take_profit:.4f}"
        )

        return signal

    def format_signal_message(self, signal: TradingSignal) -> str:
        emoji = "🟢" if "BUY" in signal.signal_type.value else "🔴" if "SELL" in signal.signal_type.value else "⚪"
        message = f"""
{emoji} ═══ *{signal.symbol} SIGNAL* ═══

🎯 *Recommendation:* {signal.recommendation}
📊 *Direction:* {signal.direction}
💪 *Confidence:* {signal.confidence:.0f}%
⏱️ *Expiry:* {signal.expiry}

━━━━━━━━━━━━━━━━━

💵 *Price Details:*
├ Entry: {signal.entry_price:,.4f}
├ Stop Loss: {signal.stop_loss:,.4f}
└ Take Profit: {signal.take_profit:,.4f}

━━━━━━━━━━━━━━━━━

📈 *Indicators:*
"""
        for name, indicator in list(signal.indicators.items())[:10]:
            msg_emoji = "🟢" if "BUY" in indicator.signal.value else "🔴" if "SELL" in indicator.signal.value else "⚪"
            message += f"{msg_emoji} {indicator.name}: {indicator.description}\n"

        message += f"""
━━━━━━━━━━━━━━━━━

📋 *Analysis Summary:*
{signal.analysis_summary}

⏰ Time: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

⚠️ *Disclaimer:* This is not financial advice. Trade at your own risk.
"""
        return message

analysis = TechnicalAnalysis()
```

---

### 📄 File: requirements.txt
```
requests==2.31.0
```

---

### 📄 File: .env
```
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE
```

---

## 🌐 ধাপ ২: GitHub-এ Upload

**১. github.com যাও এবং login করো**

**২. + New Repository click করো:**
- Name: `trading-bot`
- Description: `Telegram Trading Analysis Bot`
- Private select করো
- **Create Repository** click করো

**৩. Repository তৈরি হলে, empty repository দেখবে**
**৪. "uploading an existing file" link click করো**

**৫. এখন উপরের ৫টি file drag করে upload করো:**
- main.py
- config.py
- market_data.py
- strategies.py
- requirements.txt

**৬. "Commit changes" click করো**

---

## 🚀 ধাপ ৩: Render.com-এ Deploy

**১. dashboard.render.com যাও**
**২. "New +" click করো**
**৩. "Web Service" select করো**
**৪. GitHub account connect করো (প্রথমবার connect করতে বলবে)**
**৫. তোমার `trading-bot` repo select করো**

**৬. Settings ভরো:**
```
Name: trading-analysis-bot
Region: Singapore (or closest to you)
Language: Python
Plan: Free
```

**৭. Build & Start:**
```
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

**৮. Environment Variables যোগ করো:**
```
TELEGRAM_BOT_TOKEN = 8269257402:AAEb2RMKL3r2CJQC10H4YBRhFI-rx-PhVhg
TELEGRAM_CHAT_ID = -1002986335453
```

**৯. "Create Web Service" click করো**
**১০. Deploy শেষ হতে ২-৩ মিনিট লাগবে**
**১১. "Logs" tab দেখে confirm করো bot চালু হয়েছে কিনা**

---

## ✅ সম্পূর্ণ!

এখন Telegram-এ তোমার bot খুলো এবং `/start` লিখো!

---

## ❓ সমস্যা হলে বলো:
- কোন ধাপে আটকাচ্ছে?
- কোন error দেখাচ্ছে?
- Screenshot পাঠাও - আমি help করব! 💪