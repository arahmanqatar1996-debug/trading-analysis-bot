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

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TradingBot:
    """Advanced Telegram Bot for Trading Analysis"""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, text: str, parse_mode: str = "MarkdownV2") -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data, timeout=30)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def get_updates(self) -> List[Dict]:
        """Get updates from Telegram"""
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
        """Start command"""
        return (
            "*Trading Analysis Bot* - স্বাগতম!\n\n"
            "আমি সম্পূর্ণ Technical Analysis করি।\n\n"
            "*Commands:*\n"
            "/crypto - ক্রিপ্টো দাম\n"
            "/forex - ফরেক্স দাম\n"
            "/signal BTC - সম্পূর্ণ সিগন্যাল\n"
            "/binary EUR/USD - বাইনারি সিগন্যাল\n"
            "/trending - ট্রেন্ডিং ক্রিপ্টো\n"
            "/all - সব মার্কেট\n"
            "/help - সাহায্য\n\n"
            "*Indicators:* RSI, MACD, Bollinger, Stochastic, MA Crossover, ADX, Supertrend, VWAP, CCI, MFI, OBV, Fibonacci, Support/Resistance, Candlestick Patterns"
        )

    def cmd_help(self) -> str:
        """Help command"""
        return (
            "*সাহায্য Guide*\n\n"
            "/crypto [SYMBOL] - Crypto দাম (সব / নির্দিষ্ট)\n"
            "/forex [PAIR] - Forex দাম\n"
            "/signal [SYMBOL] - সম্পূর্ণ Technical Analysis\n"
            "/binary [PAIR] - Binary Options সিগন্যাল\n"
            "/trending - Top Cryptocurrencies\n"
            "/all - All Markets Summary\n\n"
            "*Technical Indicators যোগ করা হয়েছে:*\n"
            "- RSI (14)\n"
            "- MACD (12, 26, 9)\n"
            "- Bollinger Bands (20, 2)\n"
            "- Stochastic (14, 3)\n"
            "- MA Crossover (9, 21, 50, 200)\n"
            "- ADX (14)\n"
            "- Supertrend (10, 3)\n"
            "- VWAP\n"
            "- CCI (20)\n"
            "- MFI (14)\n"
            "- OBV\n"
            "- Fibonacci Retracement\n"
            "- Support/Resistance\n"
            "- Candlestick Patterns"
        )

    def cmd_crypto(self, args: str) -> str:
        """Crypto prices command"""
        if args:
            data = market_data.get_crypto_price(args.upper())
            if data:
                emoji = "🟢" if data.get("change_24h", 0) > 0 else "🔴"
                return (
                    f"{emoji} *{data['symbol']}*\n"
                    f"Price: ${data['price']:,.2f}\n"
                    f"24h Change: {data.get('change_24h', 0):+.2f}%\n"
                    f"Volume: ${data.get('volume_24h', 0):,.0f}"
                )
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
        """Forex prices command"""
        if args:
            data = market_data.get_forex_price(args.upper())
            if data:
                emoji = "🟢" if data.get("change_percent", 0) > 0 else "🔴"
                return (
                    f"{emoji} *{data['symbol']}*\n"
                    f"Price: {data['price']:.5f}\n"
                    f"Change: {data.get('change_percent', 0):+.2f}%"
                )
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
        """Complete technical analysis signal"""
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
        """Binary options signal"""
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
        """Trending cryptos"""
        cryptos = market_data.get_top_cryptos(10)
        if not cryptos:
            return "Error loading trending data."

        message = "*Trending Cryptocurrencies:*\n\n"
        for coin in cryptos:
            emoji = "🟢" if coin.get("change_24h", 0) > 0 else "🔴"
            message += f"{emoji} #{coin['rank']} *{coin['symbol']}*\n   ${coin['price']:,.2f} ({coin.get('change_24h', 0):+.2f}%)\n"
        return message

    def cmd_all_markets(self) -> str:
        """All markets summary"""
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
        """Handle bot commands"""
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
        """Process incoming updates"""
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
    """Main function"""
    logger.info("Starting Advanced Trading Analysis Bot...")

    bot = TradingBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    bot.send_message(
        "Advanced Trading Bot Activated!\n\n"
        "All Technical Indicators Ready.\n"
        "Type /help for commands."
    )

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
