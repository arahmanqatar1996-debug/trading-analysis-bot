"""
Market Data Fetcher with Advanced Technical Analysis
Fetches real-time data for Crypto, Forex, and Binary Options
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from strategies import analysis, TradingSignal, SignalType

logger = logging.getLogger(__name__)

class MarketData:
    """Market data fetcher for various asset classes"""

    def __init__(self):
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.yahoo_url = "https://query1.finance.yahoo.com/v8/finance"

    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """Get current crypto price from CoinGecko"""
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
        """Get current forex price from Yahoo Finance"""
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
        """Get top cryptocurrencies by market cap"""
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
        """Generate comprehensive trading signal using all strategies"""
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

    def analyze_signal(self, symbol: str, market_type: str) -> TradingSignal:
        """Generate trading signal (uses advanced analysis)"""
        return self.analyze_with_strategies(symbol)

    def get_binary_signal(self, pair: str) -> TradingSignal:
        """Generate binary options signal with full analysis"""
        return self.analyze_with_strategies(pair)

# Global instance
market_data = MarketData()
