import pandas as pd
import ta


def compute_indicators(df: pd.DataFrame) -> dict:
    """
    Compute technical indicators from a klines DataFrame.
    Requires at least 200 rows for EMA200 to be valid.
    Returns a dict of the latest indicator values.
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

    # MACD
    macd_obj = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    macd_line   = macd_obj.macd().iloc[-1]
    macd_signal = macd_obj.macd_signal().iloc[-1]
    macd_hist   = macd_obj.macd_diff().iloc[-1]

    # EMA
    ema50  = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]
    ema200 = ta.trend.EMAIndicator(close, window=200).ema_indicator().iloc[-1]

    def safe_round(val, decimals=6):
        """Round only if the value is a finite float."""
        try:
            f = float(val)
            import math
            if math.isnan(f) or math.isinf(f):
                return None
            return round(f, decimals)
        except Exception:
            return None

    return {
        "price":          safe_round(close.iloc[-1], 6),
        "RSI_14":         safe_round(rsi, 2),
        "MACD_line":      safe_round(macd_line, 6),
        "MACD_signal":    safe_round(macd_signal, 6),
        "MACD_histogram": safe_round(macd_hist, 6),
        "EMA50":          safe_round(ema50, 6),
        "EMA200":         safe_round(ema200, 6),
    }
