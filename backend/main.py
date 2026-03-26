import sys
import os

# Add backend directory to path so imports work when run from any location
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from data_fetcher import (
    get_klines, get_ticker, get_funding_rate,
    get_open_interest, get_orderbook_ratio
)
from indicators import compute_indicators
from groq_client import get_trading_signal

app = FastAPI(title="Binance Future Advisor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

TIMEFRAMES = ["15m", "1h", "4h", "1d"]


class AnalyzeRequest(BaseModel):
    symbol: str


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    symbol = req.symbol.upper().strip().replace("/", "").replace("-", "")

    try:
        # --- Global market metrics ---
        ticker = get_ticker(symbol)
        funding_rate  = get_funding_rate(symbol)
        open_interest = get_open_interest(symbol)
        bid_ask_ratio = get_orderbook_ratio(symbol)

        change_24h = round(float(ticker.get("priceChangePercent", 0)), 2)
        volume_24h = round(float(ticker.get("volume", 0)), 2)

        # --- Per-timeframe indicators ---
        timeframe_data = {}
        for tf in TIMEFRAMES:
            df = get_klines(symbol, interval=tf, limit=200)
            ind = compute_indicators(df)
            ind["change_24h"] = change_24h
            ind["volume_24h"] = volume_24h
            timeframe_data[tf] = ind

        # --- Build payload for Gemini ---
        market_data = {
            "asset":         symbol,
            "funding_rate":  round(funding_rate, 6),
            "open_interest": round(open_interest, 2),
            "bid_ask_ratio": bid_ask_ratio,
            "timeframes":    timeframe_data,
        }

        # --- Call Gemini ---
        signal = get_trading_signal(market_data)

        # Return both signal and raw market data for the frontend to display
        signal["market_data"] = market_data
        return signal

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
