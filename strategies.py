"""
Advanced Trading Strategies & Technical Analysis Engine
Complete collection of trading indicators and patterns
"""

import requests
import json
import math
from datetime import datetime, timedelta
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

class TimeFrame(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"

@dataclass
class OHLCV:
    """OHLCV Candlestick Data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class IndicatorResult:
    """Technical Indicator Result"""
    name: str
    value: float
    signal: SignalType
    description: str

@dataclass
class TradingSignal:
    """Complete Trading Signal"""
    symbol: str
    timestamp: datetime
    direction: str  # UP / DOWN / NEUTRAL
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
    """Complete Technical Analysis Engine"""

    def __init__(self):
        self.indicators_cache = {}

    # ==================== DATA FETCHING ====================

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 200) -> List[OHLCV]:
        """Fetch OHLCV data from CoinGecko or Yahoo Finance"""
        candles = []

        try:
            # CoinGecko for crypto
            if symbol.upper() in ["BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "DOT", "AVAX", "LINK", "MATIC"]:
                coin_ids = {
                    "BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "SOL": "solana",
                    "ADA": "cardano", "DOGE": "dogecoin", "DOT": "polkadot", "AVAX": "avalanche-2",
                    "LINK": "chainlink", "MATIC": "matic-network"
                }
                coin_id = coin_ids.get(symbol.upper(), symbol.lower())

                # Map timeframe
                days_map = {"1m": "1", "5m": "1", "15m": "1", "30m": "1", "1h": "7", "4h": "30", "1d": "90", "1w": "365"}
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

            # Yahoo Finance for forex/stocks
            else:
                pair = symbol.replace("/", "") + "=X"
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}"
                params = {"interval": timeframe, "range": "1y"}
                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if "chart" in data and data["chart"]["result"]:
                    result = data["chart"]["result"][0]
                    timestamps = result["timestamp"]
                    quotes = result["indicators"]["quote"][0]

                    for i, ts in enumerate(timestamps):
                        if quotes["open"][i] and quotes["close"][i]:
                            candles.append(OHLCV(
                                timestamp=datetime.fromtimestamp(ts),
                                open=quotes["open"][i],
                                high=quotes["high"][i],
                                low=quotes["low"][i],
                                close=quotes["close"][i],
                                volume=quotes.get("volume", [0])[i] or 0
                            ))

        except Exception as e:
            print(f"Error fetching OHLCV: {e}")

        return candles[-limit:]  # Return last 'limit' candles

    # ==================== MOVING AVERAGES ====================

    def sma(self, candles: List[OHLCV], period: int) -> float:
        """Simple Moving Average"""
        if len(candles) < period:
            return 0
        closes = [c.close for c in candles[-period:]]
        return sum(closes) / period

    def ema(self, candles: List[OHLCV], period: int) -> float:
        """Exponential Moving Average"""
        if len(candles) < period:
            return 0

        closes = [c.close for c in candles]
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period

        for price in closes[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def wma(self, candles: List[OHLCV], period: int) -> float:
        """Weighted Moving Average"""
        if len(candles) < period:
            return 0

        closes = [c.close for c in candles[-period:]]
        weight_sum = sum(closes[i] * (i + 1) for i in range(period))
        divisor = period * (period + 1) / 2
        return weight_sum / divisor

    def hull_ma(self, candles: List[OHLCV], period: int) -> float:
        """Hull Moving Average - smoother and faster"""
        if len(candles) < period:
            return 0

        # Calculate WMA for different periods
        half_period = period // 2
        sqrt_period = int(math.sqrt(period))

        def wma_val(data, period):
            if len(data) < period:
                return 0
            weights = list(range(1, period + 1))
            return sum(d * w for d, w in zip(data, weights)) / sum(weights)

        closes = [c.close for c in candles]

        # Hull formula: HMA = WMA(2*WMA(n/2) - WMA(n)), sqrt(n))
        wma_n2 = [wma_val(closes[i-half_period+1:i+1], half_period) if i >= half_period-1 else 0 for i in range(len(closes))]
        wma_n = [wma_val(closes[i-period+1:i+1], period) if i >= period-1 else 0 for i in range(len(closes))]

        hull = []
        for i in range(len(closes)):
            if i >= period-1 and wma_n2[i] and wma_n[i]:
                diff = 2 * wma_n2[i] - wma_n[i]
                hull.append(wma_val(closes[i-sqrt_period+1:i+1], sqrt_period))

        return hull[-1] if hull else 0

    def analyze_ma_crossover(self, candles: List[OHLCV]) -> IndicatorResult:
        """Golden Cross / Death Cross Analysis"""
        if len(candles) < 200:
            return IndicatorResult("MA_Crossover", 0, SignalType.NEUTRAL, "Not enough data")

        ema_9 = self.ema(candles, 9)
        ema_21 = self.ema(candles, 21)
        ema_50 = self.ema(candles, 50)
        ema_100 = self.ema(candles, 100)
        ema_200 = self.ema(candles, 200)

        current = candles[-1].close
        signal = SignalType.NEUTRAL
        description = ""

        # Short-term crossovers
        if ema_9 > ema_21 and candles[-2].close < self.ema(candles[:-1], 9):
            signal = SignalType.BUY
            description = "EMA 9/21 Golden Cross ✅"
        elif ema_9 < ema_21 and candles[-2].close > self.ema(candles[:-1], 9):
            signal = SignalType.SELL
            description = "EMA 9/21 Death Cross 🔴"

        # Long-term crossovers
        if ema_50 > ema_200:
            signal = SignalType.STRONG_BUY
            description = "Golden Cross (50/200 EMA) 🟢🟢"
        elif ema_50 < ema_200:
            signal = SignalType.STRONG_SELL
            description = "Death Cross (50/200 EMA) 🔴🔴"

        return IndicatorResult(
            name="MA_Crossover",
            value=ema_50 - ema_200,
            signal=signal,
            description=description
        )

    # ==================== MOMENTUM INDICATORS ====================

    def rsi(self, candles: List[OHLCV], period: int = 14) -> float:
        """Relative Strength Index"""
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
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def stochastic(self, candles: List[OHLCV], k_period: int = 14, d_period: int = 3) -> Tuple[float, float]:
        """Stochastic Oscillator %K and %D"""
        if len(candles) < k_period:
            return 50, 50

        highs = [c.high for c in candles[-k_period:]]
        lows = [c.low for c in candles[-k_period:]]
        current = candles[-1].close

        highest_high = max(highs)
        lowest_low = min(lows)

        if highest_high == lowest_low:
            return 50, 50

        k_percent = ((current - lowest_low) / (highest_high - lowest_low)) * 100

        # Calculate D% as SMA of K%
        if len(candles) >= k_period + d_period:
            k_values = []
            for i in range(d_period):
                sub_candles = candles[-(k_period + d_period - i):-i if i > 0 else None]
                sub_highs = [c.high for c in sub_candles]
                sub_lows = [c.low for c in sub_candles]
                sub_current = sub_candles[-1].close
                k_values.append(((sub_current - min(sub_lows)) / (max(sub_highs) - min(sub_lows))) * 100)
            d_percent = sum(k_values) / d_period
        else:
            d_percent = k_percent

        return k_percent, d_percent

    def macd(self, candles: List[OHLCV], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """MACD - Moving Average Convergence Divergence"""
        if len(candles) < slow:
            return 0, 0, 0

        closes = [c.close for c in candles]

        # Calculate EMAs
        multiplier_fast = 2 / (fast + 1)
        multiplier_slow = 2 / (slow + 1)
        multiplier_signal = 2 / (signal + 1)

        ema_fast = sum(closes[:fast]) / fast
        ema_slow = sum(closes[:slow]) / slow

        for price in closes[fast:slow]:
            ema_fast = (price - ema_fast) * multiplier_fast + ema_fast

        for price in closes[slow:]:
            ema_slow = (price - ema_slow) * multiplier_slow + ema_slow

        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line
        for i in range(signal):
            idx = -(signal - i)
            if len(closes) > slow + i:
                temp_fast = sum(closes[slow:slow+fast]) / fast
                temp_slow = sum(closes[:slow]) / slow
                for price in closes[slow+fast:slow+i]:
                    temp_fast = (price - temp_fast) * multiplier_fast + temp_fast
                for price in closes[:slow]:
                    temp_slow = (price - temp_slow) * multiplier_slow + temp_slow
                signal_line = (temp_fast - temp_slow) - signal_line

        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def cci(self, candles: List[OHLCV], period: int = 20) -> float:
        """Commodity Channel Index"""
        if len(candles) < period:
            return 0

        typical_prices = [(c.high + c.low + c.close) / 3 for c in candles[-period:]]
        sma_tp = sum(typical_prices) / period

        mean_deviation = sum(abs(tp - sma_tp) for tp in typical_prices) / period

        if mean_deviation == 0:
            return 0

        current_tp = (candles[-1].high + candles[-1].low + candles[-1].close) / 3
        cci = (current_tp - sma_tp) / (0.015 * mean_deviation)

        return cci

    def roc(self, candles: List[OHLCV], period: int = 12) -> float:
        """Rate of Change"""
        if len(candles) < period:
            return 0

        current = candles[-1].close
        past = candles[-period].close

        if past == 0:
            return 0

        roc = ((current - past) / past) * 100
        return roc

    def momentum(self, candles: List[OHLCV], period: int = 10) -> float:
        """Momentum Indicator"""
        if len(candles) < period:
            return 0

        return candles[-1].close - candles[-period].close

    def mfi(self, candles: List[OHLCV], period: int = 14) -> float:
        """Money Flow Index"""
        if len(candles) < period + 1:
            return 50

        typical_prices = [(c.high + c.low + c.close) / 3 for c in candles[-period:]]
        raw_money = [tp * c.volume for tp, c in zip(typical_prices, candles[-period:])]

        positive_flow = 0
        negative_flow = 0

        for i in range(1, period):
            tp_current = typical_prices[i]
            tp_prev = typical_prices[i-1]

            if tp_current > tp_prev:
                positive_flow += raw_money[i]
            else:
                negative_flow += raw_money[i]

        if negative_flow == 0:
            return 100

        money_ratio = positive_flow / negative_flow
        mfi = 100 - (100 / (1 + money_ratio))

        return mfi

    # ==================== VOLATILITY INDICATORS ====================

    def bollinger_bands(self, candles: List[OHLCV], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Bollinger Bands - Upper, Middle, Lower"""
        if len(candles) < period:
            return 0, 0, 0

        closes = [c.close for c in candles[-period:]]
        sma = sum(closes) / period

        # Standard deviation
        variance = sum((c - sma) ** 2 for c in closes) / period
        std = math.sqrt(variance)

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return upper_band, sma, lower_band

    def atr(self, candles: List[OHLCV], period: int = 14) -> float:
        """Average True Range"""
        if len(candles) < period + 1:
            return 0

        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i-1].close

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)

        return sum(true_ranges[-period:]) / period

    def keltner_channels(self, candles: List[OHLCV], period: int = 20, multiplier: float = 2.0) -> Tuple[float, float, float]:
        """Keltner Channels"""
        if len(candles) < period:
            return 0, 0, 0

        closes = [c.close for c in candles[-period:]]
        typical_prices = [(c.high + c.low + c.close) / 3 for c in candles[-period:]]

        middle = sum(typical_prices) / period
        atr_val = self.atr(candles, period)

        upper = middle + (multiplier * atr_val)
        lower = middle - (multiplier * atr_val)

        return upper, middle, lower

    def donchian_channel(self, candles: List[OHLCV], period: int = 20) -> Tuple[float, float, float]:
        """Donchian Channel"""
        if len(candles) < period:
            return 0, 0, 0

        highs = [c.high for c in candles[-period:]]
        lows = [c.low for c in candles[-period:]]

        upper = max(highs)
        lower = min(lows)
        middle = (upper + lower) / 2

        return upper, middle, lower

    def standard_deviation(self, candles: List[OHLCV], period: int = 20) -> float:
        """Standard Deviation"""
        if len(candles) < period:
            return 0

        closes = [c.close for c in candles[-period:]]
        mean = sum(closes) / period
        variance = sum((c - mean) ** 2 for c in closes) / period
        return math.sqrt(variance)

    # ==================== TREND INDICATORS ====================

    def adx(self, candles: List[OHLCV], period: int = 14) -> Tuple[float, float, float]:
        """Average Directional Index - Trend Strength"""
        if len(candles) < period + 1:
            return 0, 0, 0

        # Calculate True Range and Directional Movement
        tr_list = []
        plus_dm = []
        minus_dm = []

        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_high = candles[i-1].high
            prev_low = candles[i-1].low
            prev_close = candles[i-1].close

            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)

            up_move = high - prev_high
            down_move = prev_low - low

            if up_move > down_move and up_move > 0:
                plus_dm.append(up_move)
            else:
                plus_dm.append(0)

            if down_move > up_move and down_move > 0:
                minus_dm.append(down_move)
            else:
                minus_dm.append(0)

        # Smooth values
        atr = sum(tr_list[-period:]) / period
        plus_dm_smooth = sum(plus_dm[-period:]) / period
        minus_dm_smooth = sum(minus_dm[-period:]) / period

        if atr == 0:
            return 0, 0, 0

        plus_di = (plus_dm_smooth / atr) * 100
        minus_di = (minus_dm_smooth / atr) * 100

        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0

        # ADX (simplified)
        adx = dx  # In production, smooth this over multiple periods

        return adx, plus_di, minus_di

    def supertrend(self, candles: List[OHLCV], period: int = 10, multiplier: float = 3.0) -> Tuple[float, bool]:
        """Supertrend Indicator"""
        if len(candles) < period:
            return 0, False

        atr_val = self.atr(candles, period)

        hl2 = (candles[-1].high + candles[-1].low) / 2
        upper_band = hl2 + (multiplier * atr_val)
        lower_band = hl2 - (multiplier * atr_val)

        current = candles[-1].close

        # Check trend direction
        if current > upper_band:
            return upper_band, True  # Uptrend
        elif current < lower_band:
            return lower_band, False  # Downtrend
        else:
            return lower_band, True  # Continue previous trend

    def ichimoku(self, candles: List[OHLCV]) -> Dict[str, float]:
        """Ichimoku Cloud"""
        if len(candles) < 52:
            return {}

        # Tenkan-sen (Conversion Line)
        high_9 = max(c.high for c in candles[-9:])
        low_9 = min(c.low for c in candles[-9:])
        tenkan_sen = (high_9 + low_9) / 2

        # Kijun-sen (Base Line)
        high_26 = max(c.high for c in candles[-26:])
        low_26 = min(c.low for c in candles[-26:])
        kijun_sen = (high_26 + low_26) / 2

        # Senkou Span A (Leading Span A)
        senkou_a = (tenkan_sen + kijun_sen) / 2

        # Senkou Span B (Leading Span B)
        high_52 = max(c.high for c in candles[-52:])
        low_52 = min(c.low for c in candles[-52:])
        senkou_b = (high_52 + low_52) / 2

        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b
        }

    def parabolic_sar(self, candles: List[OHLCV], af: float = 0.02, max_af: float = 0.2) -> float:
        """Parabolic SAR"""
        if len(candles) < 3:
            return 0

        trend = candles[-1].close > candles[-2].close  # Start with uptrend
        sar = candles[0].low
        ep = candles[0].high
        af_current = af

        for i in range(1, len(candles)):
            if trend:
                sar = sar + af_current * (ep - sar)
                if candles[i].low < sar:
                    trend = False
                    sar = ep
                    ep = candles[i].low
                    af_current = af
                else:
                    ep = max(ep, candles[i].high)
                    af_current = min(af_current + af, max_af)
            else:
                sar = sar + af_current * (ep - sar)
                if candles[i].high > sar:
                    trend = True
                    sar = ep
                    ep = candles[i].high
                    af_current = af
                else:
                    ep = min(ep, candles[i].low)
                    af_current = min(af_current + af, max_af)

        return sar

    # ==================== VOLUME INDICATORS ====================

    def obv(self, candles: List[OHLCV]) -> float:
        """On Balance Volume"""
        if len(candles) < 2:
            return 0

        obv = 0
        for i in range(1, len(candles)):
            if candles[i].close > candles[i-1].close:
                obv += candles[i].volume
            elif candles[i].close < candles[i-1].close:
                obv -= candles[i].volume

        return obv

    def vwap(self, candles: List[OHLCV]) -> float:
        """Volume Weighted Average Price"""
        if len(candles) < 2:
            return 0

        volume_sum = 0
        price_volume_sum = 0

        for candle in candles:
            price_volume_sum += candle.close * candle.volume
            volume_sum += candle.volume

        return price_volume_sum / volume_sum if volume_sum > 0 else 0

    def mfi_analyze(self, candles: List[OHLCV]) -> IndicatorResult:
        """Analyze Money Flow Index"""
        mfi_val = self.mfi(candles)

        if mfi_val > 80:
            signal = SignalType.STRONG_SELL
            description = f"MFI Overbought: {mfi_val:.1f}"
        elif mfi_val > 60:
            signal = SignalType.SELL
            description = f"MFI: {mfi_val:.1f} - Bearish pressure"
        elif mfi_val < 20:
            signal = SignalType.STRONG_BUY
            description = f"MFI Oversold: {mfi_val:.1f}"
        elif mfi_val < 40:
            signal = SignalType.BUY
            description = f"MFI: {mfi_val:.1f} - Bullish pressure"
        else:
            signal = SignalType.NEUTRAL
            description = f"MFI: {mfi_val:.1f}"

        return IndicatorResult("MFI", mfi_val, signal, description)

    def volume_profile(self, candles: List[OHLCV]) -> Dict[str, float]:
        """Volume Profile Analysis"""
        if len(candles) < 20:
            return {}

        price_ranges = {}
        for candle in candles[-20:]:
            price = round(candle.close, -1)  # Round to nearest 10
            if price not in price_ranges:
                price_ranges[price] = 0
            price_ranges[price] += candle.volume

        if price_ranges:
            max_volume_price = max(price_ranges, key=price_ranges.get)
        else:
            max_volume_price = 0

        return {
            "max_volume_price": max_volume_price,
            "total_volume": sum(price_ranges.values())
        }

    # ==================== CANDLESTICK PATTERNS ====================

    def detect_candlestick_patterns(self, candles: List[OHLCV]) -> List[Tuple[str, SignalType]]:
        """Detect candlestick patterns"""
        patterns = []

        if len(candles) < 3:
            return patterns

        # Latest candles
        c1 = candles[-3] if len(candles) >= 3 else None
        c2 = candles[-2] if len(candles) >= 2 else None
        c3 = candles[-1]

        body3 = abs(c3.close - c3.open)
        upper_shadow3 = c3.high - max(c3.open, c3.close)
        lower_shadow3 = min(c3.open, c3.close) - c3.low

        if c1 and c2:
            body1 = abs(c1.close - c1.open)
            body2 = abs(c2.close - c2.open)

            # Doji
            if body3 < (c3.high - c3.low) * 0.1:
                patterns.append(("DOJI - Uncertainty", SignalType.NEUTRAL))

            # Hammer (bullish)
            if lower_shadow3 > body3 * 2 and upper_shadow3 < body3 * 0.3:
                if c3.close > c3.open:  # Bullish
                    patterns.append(("HAMMER - Bullish reversal", SignalType.BUY))

            # Inverted Hammer
            if upper_shadow3 > body3 * 2 and lower_shadow3 < body3 * 0.3:
                patterns.append(("INVERTED HAMMER - Bullish reversal", SignalType.BUY))

            # Shooting Star (bearish)
            if upper_shadow3 > body3 * 2 and lower_shadow3 < body3 * 0.3:
                if c3.close < c3.open:  # Bearish
                    patterns.append(("SHOOTING STAR - Bearish reversal", SignalType.SELL))

            # Engulfing Pattern
            if body2 > body1:
                # Bullish Engulfing
                if c2.close < c2.open and c3.close > c3.open:  # c2 is bearish, c3 is bullish
                    if c3.open < c2.close and c3.close > c2.open:
                        patterns.append(("BULLISH ENGULFING 🟢🟢", SignalType.STRONG_BUY))

                # Bearish Engulfing
                elif c2.close > c2.open and c3.close < c3.open:  # c2 is bullish, c3 is bearish
                    if c3.open > c2.close and c3.close < c2.open:
                        patterns.append(("BEARISH ENGULFING 🔴🔴", SignalType.STRONG_SELL))

            # Morning Star (bullish reversal)
            if c1.close < c1.open and body1 > body2 and c3.close > c3.open:
                if c3.close > (c1.open + c1.close) / 2:
                    patterns.append(("MORNING STAR - Bullish reversal", SignalType.STRONG_BUY))

            # Evening Star (bearish reversal)
            if c1.close > c1.open and body1 > body2 and c3.close < c3.open:
                if c3.close < (c1.open + c1.close) / 2:
                    patterns.append(("EVENING STAR - Bearish reversal", SignalType.STRONG_SELL))

            # Three White Soldiers (bullish)
            if (c1.close > c1.open and c2.close > c2.open and c3.close > c3.open):
                if (c2.close > c1.close and c3.close > c2.close):
                    patterns.append(("THREE WHITE SOLDIERS 🟢🟢🟢", SignalType.STRONG_BUY))

            # Three Black Crows (bearish)
            if (c1.close < c1.open and c2.close < c2.open and c3.close < c3.open):
                if (c2.close < c1.close and c3.close < c2.close):
                    patterns.append(("THREE BLACK CROWS 🔴🔴🔴", SignalType.STRONG_SELL))

        # Marubozu
        if upper_shadow3 < body3 * 0.1 and lower_shadow3 < body3 * 0.1:
            if c3.close > c3.open:
                patterns.append(("MARUBOZU BULLISH", SignalType.BUY))
            else:
                patterns.append(("MARUBOZU BEARISH", SignalType.SELL))

        return patterns

    # ==================== SUPPORT/RESISTANCE ====================

    def find_support_resistance(self, candles: List[OHLCV], lookback: int = 50) -> Dict[str, List[float]]:
        """Find support and resistance levels"""
        if len(candles) < lookback:
            return {"support": [], "resistance": [], "pivot": []}

        highs = [c.high for c in candles[-lookback:]]
        lows = [c.low for c in candles[-lookback:]]
        closes = [c.close for c in candles[-lookback:]]

        # Simple pivot points
        pivot = (max(highs) + min(lows) + closes[-1]) / 3
        r1 = 2 * pivot - min(lows)
        s1 = 2 * pivot - max(highs)
        r2 = pivot + (max(highs) - min(lows))
        s2 = pivot - (max(highs) - min(lows))

        return {
            "support": [min(lows), s1, s2],
            "resistance": [max(highs), r1, r2],
            "pivot": [pivot, r1, s1]
        }

    def analyze_price_action(self, candles: List[OHLCV]) -> IndicatorResult:
        """Analyze price action and market structure"""
        if len(candles) < 50:
            return IndicatorResult("Price Action", 0, SignalType.NEUTRAL, "Not enough data")

        current = candles[-1].close
        high_20 = max(c.high for c in candles[-20:])
        low_20 = min(c.low for c in candles[-20:])
        high_50 = max(c.high for c in candles[-50:])
        low_50 = min(c.low for c in candles[-50:])

        # Determine market structure
        if current > high_20:
            structure = "Strong Uptrend"
            signal = SignalType.STRONG_BUY
        elif current > high_50:
            structure = "Uptrend"
            signal = SignalType.BUY
        elif current < low_20:
            structure = "Strong Downtrend"
            signal = SignalType.STRONG_SELL
        elif current < low_50:
            structure = "Downtrend"
            signal = SignalType.SELL
        else:
            structure = "Ranging"
            signal = SignalType.NEUTRAL

        return IndicatorResult(
            "Price Action",
            current,
            signal,
            f"{structure} | 20H: {high_20:.2f} | 50H: {high_50:.2f}"
        )

    # ==================== FIBONACCI ====================

    def fibonacci_retracement(self, candles: List[OHLCV]) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        if len(candles) < 50:
            return {}

        high = max(c.high for c in candles[-50:])
        low = min(c.low for c in candles[-50:])
        diff = high - low

        levels = {
            "0% (Low)": low,
            "23.6%": high - 0.236 * diff,
            "38.2%": high - 0.382 * diff,
            "50%": high - 0.5 * diff,
            "61.8%": high - 0.618 * diff,
            "78.6%": high - 0.786 * diff,
            "100% (High)": high
        }

        return levels

    # ==================== COMPLETE SIGNAL ANALYSIS ====================

    def generate_complete_signal(self, symbol: str, candles: List[OHLCV]) -> TradingSignal:
        """Generate complete trading signal with all indicators"""

        signal = TradingSignal(
            symbol=symbol,
            timestamp=datetime.now(),
            direction="NEUTRAL",
            signal_type=SignalType.NEUTRAL,
            confidence=0,
            entry_price=candles[-1].close if candles else 0,
            stop_loss=0,
            take_profit=0,
            indicators={},
            recommendation="WAIT ⏰",
            expiry="5 min",
            analysis_summary=""
        )

        if len(candles) < 50:
            signal.analysis_summary = "Not enough data for analysis"
            return signal

        current_price = candles[-1].close
        signal.entry_price = current_price

        # Calculate all indicators
        all_signals = []
        indicator_values = {}

        # 1. MA Crossover
        ma_result = self.analyze_ma_crossover(candles)
        signal.indicators["MA_Crossover"] = ma_result
        all_signals.append(ma_result.signal)
        indicator_values["EMA_50"] = self.ema(candles, 50)
        indicator_values["EMA_200"] = self.ema(candles, 200)

        # 2. RSI
        rsi_val = self.rsi(candles)
        signal.indicators["RSI"] = IndicatorResult(
            "RSI", rsi_val,
            SignalType.STRONG_BUY if rsi_val < 30 else SignalType.STRONG_SELL if rsi_val > 70 else SignalType.NEUTRAL,
            f"RSI(14): {rsi_val:.1f}"
        )
        all_signals.append(signal.indicators["RSI"].signal)
        indicator_values["RSI"] = rsi_val

        # 3. Stochastic
        stoch_k, stoch_d = self.stochastic(candles)
        signal.indicators["Stochastic"] = IndicatorResult(
            "Stochastic", stoch_k,
            SignalType.BUY if stoch_k < 20 else SignalType.SELL if stoch_k > 80 else SignalType.NEUTRAL,
            f"Stoch K: {stoch_k:.1f}, D: {stoch_d:.1f}"
        )
        all_signals.append(signal.indicators["Stochastic"].signal)
        indicator_values["Stochastic_K"] = stoch_k

        # 4. MACD
        macd_line, signal_line, histogram = self.macd(candles)
        macd_signal = SignalType.BUY if histogram > 0 else SignalType.SELL if histogram < 0 else SignalType.NEUTRAL
        signal.indicators["MACD"] = IndicatorResult(
            "MACD", histogram,
            macd_signal,
            f"MACD: {macd_line:.4f} | Signal: {signal_line:.4f} | Hist: {histogram:.4f}"
        )
        all_signals.append(macd_signal)
        indicator_values["MACD_Hist"] = histogram

        # 5. Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.bollinger_bands(candles)
        bb_position = "Middle" if bb_middle - 0.001 < current_price < bb_middle + 0.001 else "Upper" if current_price > bb_upper else "Lower" if current_price < bb_lower else "Near Upper" if current_price > bb_middle else "Near Lower"
        signal.indicators["Bollinger"] = IndicatorResult(
            "Bollinger", current_price,
            SignalType.SELL if current_price > bb_upper else SignalType.BUY if current_price < bb_lower else SignalType.NEUTRAL,
            f"BB: {bb_lower:.2f} - {bb_middle:.2f} - {bb_upper:.2f} | Price: {bb_position}"
        )
        all_signals.append(signal.indicators["Bollinger"].signal)
        indicator_values["BB_Upper"] = bb_upper
        indicator_values["BB_Lower"] = bb_lower

        # 6. CCI
        cci_val = self.cci(candles)
        signal.indicators["CCI"] = IndicatorResult(
            "CCI", cci_val,
            SignalType.STRONG_BUY if cci_val < -100 else SignalType.STRONG_SELL if cci_val > 100 else SignalType.NEUTRAL,
            f"CCI(20): {cci_val:.1f}"
        )
        all_signals.append(signal.indicators["CCI"].signal)

        # 7. ATR (Volatility)
        atr_val = self.atr(candles)
        signal.indicators["ATR"] = IndicatorResult(
            "ATR", atr_val,
            SignalType.NEUTRAL,
            f"ATR(14): {atr_val:.4f} | Volatility: {'High' if atr_val > current_price * 0.02 else 'Normal'}"
        )
        indicator_values["ATR"] = atr_val

        # 8. ADX (Trend Strength)
        adx_val, plus_di, minus_di = self.adx(candles)
        trend_strength = "Strong" if adx_val > 25 else "Weak" if adx_val < 20 else "Moderate"
        signal.indicators["ADX"] = IndicatorResult(
            "ADX", adx_val,
            SignalType.BUY if plus_di > minus_di else SignalType.SELL if minus_di > plus_di else SignalType.NEUTRAL,
            f"ADX: {adx_val:.1f} ({trend_strength}) | +DI: {plus_di:.1f} | -DI: {minus_di:.1f}"
        )
        all_signals.append(signal.indicators["ADX"].signal)

        # 9. Supertrend
        supert_value, supert_uptrend = self.supertrend(candles)
        signal.indicators["Supertrend"] = IndicatorResult(
            "Supertrend", supert_value,
            SignalType.BUY if supert_uptrend else SignalType.SELL,
            f"Supertrend: {supert_value:.2f} | {'Uptrend' if supert_uptrend else 'Downtrend'}"
        )
        all_signals.append(signal.indicators["Supertrend"].signal)

        # 10. OBV
        obv_val = self.obv(candles)
        signal.indicators["OBV"] = IndicatorResult(
            "OBV", obv_val,
            SignalType.BUY if obv_val > 0 else SignalType.SELL,
            f"OBV: {obv_val:,.0f}"
        )

        # 11. VWAP
        vwap_val = self.vwap(candles[-20:])
        signal.indicators["VWAP"] = IndicatorResult(
            "VWAP", vwap_val,
            SignalType.BUY if current_price > vwap_val else SignalType.SELL,
            f"VWAP: {vwap_val:.4f} | {'Above' if current_price > vwap_val else 'Below'} price"
        )
        all_signals.append(signal.indicators["VWAP"].signal)

        # 12. MFI
        mfi_result = self.mfi_analyze(candles)
        signal.indicators["MFI"] = mfi_result
        all_signals.append(mfi_result.signal)

        # 13. Price Action
        pa_result = self.analyze_price_action(candles)
        signal.indicators["Price_Action"] = pa_result
        all_signals.append(pa_result.signal)

        # 14. Candlestick Patterns
        patterns = self.detect_candlestick_patterns(candles)
        pattern_signals = [p[1] for p in patterns]
        signal.indicators["Patterns"] = IndicatorResult(
            "Patterns",
            len(patterns),
            max(pattern_signals, key=lambda x: x.value if hasattr(x, 'value') else 0) if pattern_signals else SignalType.NEUTRAL,
            " | ".join([p[0] for p in patterns]) if patterns else "No clear pattern"
        )
        all_signals.extend(pattern_signals)

        # 15. Fibonacci
        fib_levels = self.fibonacci_retracement(candles)
        fib_desc = f"Support: {fib_levels.get('61.8%', 0):.2f} | Resistance: {fib_levels.get('38.2%', 0):.2f}" if fib_levels else "N/A"
        signal.indicators["Fibonacci"] = IndicatorResult("Fibonacci", 0, SignalType.NEUTRAL, fib_desc)

        # 16. Support/Resistance
        sr_levels = self.find_support_resistance(candles)
        signal.indicators["SR_Levels"] = IndicatorResult(
            "Support/Resistance", 0, SignalType.NEUTRAL,
            f"R: {sr_levels.get('resistance', [0])[0]:.2f} | S: {sr_levels.get('support', [0])[0]:.2f}"
        )

        # ==================== FINAL SIGNAL DETERMINATION ====================

        # Count signals
        buy_signals = all_signals.count(SignalType.STRONG_BUY) + all_signals.count(SignalType.BUY)
        sell_signals = all_signals.count(SignalType.STRONG_SELL) + all_signals.count(SignalType.SELL)
        total_signals = len(all_signals)

        # Calculate confidence
        if buy_signals > sell_signals:
            signal.direction = "UP 📈"
            diff = buy_signals - sell_signals
            if diff >= total_signals * 0.6:
                signal.signal_type = SignalType.STRONG_BUY
                signal.recommendation = "STRONG BUY 🟢🟢"
            else:
                signal.signal_type = SignalType.BUY
                signal.recommendation = "BUY 🟢"
        elif sell_signals > buy_signals:
            signal.direction = "DOWN 📉"
            diff = sell_signals - buy_signals
            if diff >= total_signals * 0.6:
                signal.signal_type = SignalType.STRONG_SELL
                signal.recommendation = "STRONG SELL 🔴🔴"
            else:
                signal.signal_type = SignalType.SELL
                signal.recommendation = "SELL 🔴"
        else:
            signal.direction = "NEUTRAL ⏰"
            signal.signal_type = SignalType.NEUTRAL
            signal.recommendation = "WAIT ⏰"

        signal.confidence = (max(buy_signals, sell_signals) / total_signals * 100) if total_signals > 0 else 50

        # Calculate stop loss and take profit
        atr_multiplier = 1.5
        if signal.direction == "UP 📈":
            signal.stop_loss = current_price - (atr_val * atr_multiplier)
            signal.take_profit = current_price + (atr_val * atr_multiplier * 2)
        else:
            signal.stop_loss = current_price + (atr_val * atr_multiplier)
            signal.take_profit = current_price - (atr_val * atr_multiplier * 2)

        # Generate summary
        signal.analysis_summary = (
            f"Buy Signals: {buy_signals}/{total_signals} ✅\n"
            f"Sell Signals: {sell_signals}/{total_signals} ❌\n"
            f"Confidence: {signal.confidence:.0f}%\n"
            f"Entry: {current_price:.4f}\n"
            f"SL: {signal.stop_loss:.4f} | TP: {signal.take_profit:.4f}"
        )

        return signal

    def format_signal_message(self, signal: TradingSignal) -> str:
        """Format trading signal for Telegram"""
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

        # Add each indicator
        indicator_list = list(signal.indicators.items())
        for i, (name, indicator) in enumerate(indicator_list[:10]):  # Top 10 indicators
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


# Global instance
analysis = TechnicalAnalysis()
