import re

with open("backend/main.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Import
import_pattern = re.compile(r'from telegram_bot import send_telegram_message, format_signal_message')
text = import_pattern.sub("from telegram_bot import send_telegram_message, format_signal_message, telegram_polling_loop\nfrom models import Watchlist", text)

# 2. Scanner Logic
scanner_logic = """
async def auto_market_scanner():
    \"\"\"Vòng lặp quét AI liên tục các mã Coin trong Watchlist mỗi giờ.\"\"\"
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

@app.on_event("startup")"""

startup_pattern = re.compile(r'@app\.on_event\("startup"\)')
text = startup_pattern.sub(scanner_logic, text)

# 3. Add to startup event
startup_funcs = """@app.on_event("startup")
async def startup_event():
    asyncio.create_task(telegram_polling_loop())
    asyncio.create_task(check_pending_signals())
    asyncio.create_task(auto_market_scanner())"""

text = re.sub(r'@app\.on_event\("startup"\)\nasync def startup_event\(\):\n    asyncio\.create_task\(check_pending_signals\(\)\)', startup_funcs, text)

with open("backend/main.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Patch applied to main.py")
