import requests
import pandas as pd


def get_klines(symbol: str, interval="1h", limit=200) -> pd.DataFrame:
    """Fetch OHLCV candlestick data from Binance Futures public API."""
    url = (
        f"https://fapi.binance.com/fapi/v1/klines"
        f"?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    )
    res = requests.get(url, timeout=10).json()
    if isinstance(res, dict) and "code" in res:
        raise ValueError(f"Binance API error: {res.get('msg', res)}")

    df = pd.DataFrame(res, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_base_vol", "taker_quote_vol", "ignore"
    ])
    for col in ["open", "high", "low", "close", "volume", "taker_base_vol"]:
        df[col] = df[col].astype(float)
    return df


def get_ticker(symbol: str) -> dict:
    """24h price change statistics from Binance Futures."""
    url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol.upper()}"
    data = requests.get(url, timeout=10).json()
    if isinstance(data, dict) and "code" in data:
        raise ValueError(f"Binance API error: {data.get('msg', data)}")
    return data


def get_funding_rate(symbol: str) -> float:
    """Latest funding rate for a Binance Futures symbol."""
    url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol.upper()}&limit=1"
    data = requests.get(url, timeout=10).json()
    if isinstance(data, dict) and "code" in data:
        raise ValueError(f"Binance API error: {data.get('msg', data)}")
    return float(data[0]["fundingRate"])


def get_open_interest(symbol: str) -> float:
    """Latest open interest value (USD) from Binance Futures historical data."""
    url = (
        f"https://fapi.binance.com/futures/data/openInterestHist"
        f"?symbol={symbol.upper()}&period=5m&limit=1"
    )
    data = requests.get(url, timeout=10).json()
    if isinstance(data, dict) and "code" in data:
        raise ValueError(f"Binance API error: {data.get('msg', data)}")
    return float(data[0]["sumOpenInterestValue"])


def get_orderbook_ratio(symbol: str) -> float:
    """Bid/Ask volume ratio from the top 100 levels of the order book."""
    url = f"https://fapi.binance.com/fapi/v1/depth?symbol={symbol.upper()}&limit=100"
    data = requests.get(url, timeout=10).json()
    if isinstance(data, dict) and "code" in data:
        raise ValueError(f"Binance API error: {data.get('msg', data)}")
    bids = sum(float(b[1]) for b in data["bids"])
    asks = sum(float(a[1]) for a in data["asks"])
    if asks == 0:
        return 1.0
    return round(bids / asks, 2)
