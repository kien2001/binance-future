import sys
import os
import asyncio
from datetime import datetime, timezone

# Add backend directory to path so imports work when run from any location
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from data_fetcher import (
    get_klines, get_ticker, get_funding_rate,
    get_open_interest, get_orderbook_ratio
)
from indicators import compute_indicators
from groq_client import get_trading_signal

# --- Phase 3 Additions ---
from database import engine, Base, get_db
from models import TradeSignal
from telegram_bot import send_telegram_message, format_signal_message, telegram_polling_loop
from models import Watchlist

# Create DB Tables
Base.metadata.create_all(bind=engine)

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
    style: str = "Swing"


async def check_pending_signals():
    """Background task to check TP/SL against current ticker every 5 minutes."""
    while True:
        try:
            db = next(get_db())
            pending_signals = db.query(TradeSignal).filter(TradeSignal.status == "PENDING").all()
            for sig in pending_signals:
                try:
                    ticker = get_ticker(sig.symbol)
                    current_price = float(ticker.get("lastPrice", 0))
                    
                    if current_price <= 0:
                        continue
                        
                    # LONG Case
                    if sig.direction == "LONG":
                        if sig.take_profit and current_price >= sig.take_profit:
                            sig.status = "WIN"
                        elif sig.stop_loss and current_price <= sig.stop_loss:
                            sig.status = "LOSS"
                            
                    # SHORT Case
                    elif sig.direction == "SHORT":
                        if sig.take_profit and current_price <= sig.take_profit:
                            sig.status = "WIN"
                        elif sig.stop_loss and current_price >= sig.stop_loss:
                            sig.status = "LOSS"
                            
                except Exception as e:
                    print(f"Error checking signal {sig.symbol}: {e}")
                    
            db.commit()
            db.close()
        except Exception as e:
            print(f"Background Task Error: {e}")
            
        await asyncio.sleep(300) # 5 minutes


async def auto_market_scanner():
    """Vòng lặp quét AI liên tục các mã Coin trong Watchlist mỗi giờ."""
    await asyncio.sleep(15) # Chờ server load xong
    
    while True:
        try:
            db = next(get_db())
            watchlists = db.query(Watchlist).all()
            
            # Gộp Symbol lại để tránh gọi API nhiều lần cho cùng 1 coin
            symbol_to_users = {}
            for item in watchlists:
                if item.symbol not in symbol_to_users:
                    symbol_to_users[item.symbol] = set()
                symbol_to_users[item.symbol].add(item.chat_id)
                
            for symbol, chat_ids in symbol_to_users.items():
                print(f"[SCANNER] Bắt đầu soi kèo tự động cho {symbol}...")
                try:
                    # Lấy dữ liệu
                    ticker = get_ticker(symbol)
                    funding_rate = get_funding_rate(symbol)
                    open_interest = get_open_interest(symbol)
                    bid_ask_ratio = get_orderbook_ratio(symbol)
                    
                    change_24h = round(float(ticker.get("priceChangePercent", 0)), 2)
                    volume_24h = round(float(ticker.get("volume", 0)), 2)
                    
                    timeframe_data = {}
                    for tf in TIMEFRAMES:
                        df = get_klines(symbol, interval=tf, limit=200)
                        ind = compute_indicators(df)
                        ind["change_24h"] = change_24h
                        ind["volume_24h"] = volume_24h
                        timeframe_data[tf] = ind
                        
                    market_data = {
                        "asset": symbol, "funding_rate": round(funding_rate, 6),
                        "open_interest": round(open_interest, 2), "bid_ask_ratio": bid_ask_ratio,
                        "timeframes": timeframe_data,
                    }
                    
                    # Gọi AI Phân tích
                    signal = get_trading_signal(market_data, "Swing")
                    direction = signal.get("direction", "HOLD").upper()
                    confidence = signal.get("confidence_score", 0)
                    
                    # Cổng Lọc (Filter)
                    if direction != "HOLD" and confidence >= 75:
                        # Chống Spam: Xem đã có lệnh PENDING cùng chiều chưa
                        exist = db.query(TradeSignal).filter_by(
                            symbol=symbol, direction=direction, status="PENDING"
                        ).first()
                        
                        if not exist:
                            # Lưu Lịch sử 
                            db_signal = TradeSignal(
                                symbol=symbol, strategy="Auto-Scan (Swing)",
                                direction=direction, entry_price=signal.get("entry_price"),
                                stop_loss=signal.get("stop_loss"), take_profit=signal.get("take_profit"),
                                confidence_score=confidence, reasoning=signal.get("reasoning", "")
                            )
                            db.add(db_signal)
                            db.commit()
                            
                            # Bắn Tin Nhắn cho toàn bộ user đang theo dõi mã này
                            telegram_msg = format_signal_message(signal)
                            telegram_msg = f"🔥 <b>[HỆ THỐNG QUÉT TỰ ĐỘNG]</b>\\n\\n{telegram_msg}"
                            
                            for cid in chat_ids:
                                asyncio.create_task(send_telegram_message(telegram_msg, target_chat_id=cid))
                        else:
                            print(f"[SCANNER] Kèo {symbol} {direction} đã tồn tại PENDING. Bỏ qua tránh spam.")
                            
                except Exception as ex:
                    print(f"[SCANNER ERROR] Lỗi soi kèo {symbol}: {ex}")
                    
                # Chống Rate Limit API Groq
                await asyncio.sleep(15)
                
            db.close()
        except Exception as e:
            print(f"Background Scanner Error: {e}")
            
        # Lặp lại mỗi 1 Tiếng (3600s)
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(telegram_polling_loop())
    asyncio.create_task(check_pending_signals())
    asyncio.create_task(auto_market_scanner())

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/journal")
def get_journal(db: Session = Depends(get_db)):
    """Fetch all historical signals for the Trade Journal UI."""
    signals = db.query(TradeSignal).order_by(TradeSignal.timestamp.desc()).limit(50).all()
    
    total_closed = len([s for s in signals if s.status in ["WIN", "LOSS"]])
    wins = len([s for s in signals if s.status == "WIN"])
    win_rate = (wins / total_closed * 100) if total_closed > 0 else 0
    
    return {
        "win_rate": round(win_rate, 2),
        "total_closed": total_closed,
        "signals": [
            {
                "id": s.id,
                "timestamp": s.timestamp.isoformat(),
                "symbol": s.symbol,
                "strategy": s.strategy,
                "direction": s.direction,
                "entry_price": s.entry_price,
                "status": s.status,
                "confidence_score": s.confidence_score
            } for s in signals
        ]
    }


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    symbol = req.symbol.upper().strip().replace("/", "").replace("-", "")
    style  = req.style

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
            df = get_klines(req.symbol, interval=tf, limit=200)
            # Chỉ đính kèm Chart Series dữ liệu EMA cho khung 1h (Mặc định của Frontend)
            include_s = True if tf == "1h" else False
            ind = compute_indicators(df, include_series=include_s)
            
            ind["change_24h"] = change_24h
            ind["volume_24h"] = volume_24h
            timeframe_data[tf] = ind

        # --- Build payload for Gemini/Groq ---
        market_data = {
            "asset":         symbol,
            "funding_rate":  round(funding_rate, 6),
            "open_interest": round(open_interest, 2),
            "bid_ask_ratio": bid_ask_ratio,
            "timeframes":    timeframe_data,
        }

        # --- Call AI ---
        signal = get_trading_signal(market_data, style)
        signal["market_data"] = market_data
        
        # --- Phase 3: Save to Database ---
        db_signal = TradeSignal(
            symbol=symbol,
            strategy=style,
            direction=signal.get("direction", "HOLD").upper(),
            entry_price=signal.get("entry_price"),
            stop_loss=signal.get("stop_loss"),
            take_profit=signal.get("take_profit"),
            confidence_score=signal.get("confidence_score", 0),
            reasoning=signal.get("reasoning", "")
        )
        db.add(db_signal)
        db.commit()
        db.refresh(db_signal)
        
        # --- Phase 3: Async Telegram Alert ---
        if db_signal.direction != "HOLD" and db_signal.confidence_score >= 75:
            telegram_msg = format_signal_message(signal)
            background_tasks.add_task(send_telegram_message, telegram_msg)
            
        return signal

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Server Error in /analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))
