import os
import httpx
import logging
import html
import asyncio
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Chat ID trung tâm để nhận các thông báo hệ thống tự động
GLOBAL_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(message: str, target_chat_id: str = None):
    chat_id = target_chat_id or GLOBAL_CHAT_ID
    if not TELEGRAM_BOT_TOKEN or not chat_id or "Điền_" in TELEGRAM_BOT_TOKEN:
        logging.warning("Telegram Bot is not properly configured. Skipping alert.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code != 200:
                logging.error(f"Telegram API Error: {response.text}")
            response.raise_for_status()
            return True
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {str(e)}")
        return False

def format_signal_message(signal_data: dict) -> str:
    direction = signal_data.get("direction", "HOLD").upper()
    asset = signal_data.get("asset", "Unknown")
    
    emoji = "🟢" if direction == "LONG" else "🔴" if direction == "SHORT" else "⚪"
    reasoning_text = html.escape(str(signal_data.get('reasoning', "")))
    
    msg = f"<b>{emoji} ALPHA TRADER ALERT: {asset} {direction}</b>\n\n"
    msg += f"🎯 <b>Entry:</b> {signal_data.get('entry_price')}\n"
    msg += f"🛑 <b>Stop Loss:</b> {signal_data.get('stop_loss')}\n"
    msg += f"✅ <b>Take Profit:</b> {signal_data.get('take_profit')}\n"
    msg += f"⚖️ <b>Leverage:</b> {signal_data.get('leverage')}x\n"
    msg += f"🛒 <b>Pos Size:</b> {signal_data.get('position_size_percent')}%\n"
    msg += f"🧠 <b>Confidence:</b> {signal_data.get('confidence_score')}%\n\n"
    msg += f"📝 <i>{reasoning_text}</i>"
    return msg

async def telegram_polling_loop():
    from database import get_db
    from models import Watchlist
    
    if not TELEGRAM_BOT_TOKEN or "Điền_" in TELEGRAM_BOT_TOKEN:
        logging.warning("No Telegram Token, skipping polling loop.")
        return

    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    while True:
        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                res = await client.get(f"{url}?offset={offset}&timeout=30")
                if res.status_code == 200:
                    data = res.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        msg = update.get("message", {})
                        text = msg.get("text", "").strip()
                        chat_id = str(msg.get("chat", {}).get("id", ""))
                        
                        if text and chat_id:
                            db = next(get_db())
                            parts = text.split(" ")
                            cmd = parts[0].upper()
                            
                            if cmd == "/START":
                                await send_telegram_message("🤖 <b>Chào mừng bạn tới AlphaTrader!</b>\n\nGõ <code>/add BTCUSDT</code> để thêm coin vào danh sách Auto-Scanner hằng giờ.\nGõ <code>/remove BTCUSDT</code> để xóa.\nGõ <code>/list</code> để xem các coin đang soi.", target_chat_id=chat_id)
                            
                            elif cmd == "/ADD" and len(parts) >= 2:
                                symbol = parts[1].upper().replace("/", "").replace("-", "")
                                exist = db.query(Watchlist).filter_by(chat_id=chat_id, symbol=symbol).first()
                                if exist:
                                    await send_telegram_message(f"⚠️ Cặp <b>{symbol}</b> đã nằm trong dánh sách của bạn rồi!", target_chat_id=chat_id)
                                else:
                                    wl = Watchlist(chat_id=chat_id, symbol=symbol)
                                    db.add(wl)
                                    db.commit()
                                    await send_telegram_message(f"✅ Đã đưa <b>{symbol}</b> vào tầm ngắm Auto-Scanner!\n⚙️ Xin chờ 1 chút, BOT đang khởi động máy phân tích khẩn cấp lấy thông tin hiện tại...", target_chat_id=chat_id)
                                    
                                    try:
                                        # Gọi local API để kích hoạt luồng analyze tức thì
                                        async with httpx.AsyncClient(timeout=60.0) as local_client:
                                            res = await local_client.post("http://127.0.0.1:8000/api/analyze", json={"symbol": symbol, "style": "Swing"})
                                            if res.status_code == 200:
                                                data = res.json()
                                                conf = data.get("confidence_score", 0)
                                                dir = data.get("direction", "HOLD").upper()
                                                
                                                if dir == "HOLD" or conf < 75:
                                                    reason = html.escape(str(data.get('reasoning', '')))
                                                    await send_telegram_message(f"📉 Tín hiệu hiện tại của <b>{symbol}</b> đang là {dir} với điểm tin cậy: <b>{conf}%</b> (Chưa đạt mốc 75%).\n\n📝 AI Báo Cáo: <i>{reason}</i>\n\n👉 Do chưa đạt chuẩn nên Bot không hô lệnh. Bot sẽ tiếp tục theo dõi hằng giờ giúp bạn!", target_chat_id=chat_id)
                                                # Nếu conf >= 75 và dir != HOLD thì endpoint API kia đã TỰ ĐỘNG bắn lệnh sang Telegram rồi!
                                            else:
                                                await send_telegram_message(f"⚠️ Lỗi phân tích khẩn cấp, mã lỗi: {res.status_code}", target_chat_id=chat_id)
                                    except Exception as ex:
                                        await send_telegram_message(f"⚠️ Máy chủ cục bộ đang bận rộn: {ex}", target_chat_id=chat_id)
                                        
                            elif cmd == "/REMOVE" and len(parts) >= 2:
                                symbol = parts[1].upper().replace("/", "").replace("-", "")
                                exist = db.query(Watchlist).filter_by(chat_id=chat_id, symbol=symbol).first()
                                if exist:
                                    db.delete(exist)
                                    db.commit()
                                    await send_telegram_message(f"❌ Đã gỡ <b>{symbol}</b> khỏi danh sách.", target_chat_id=chat_id)
                                else:
                                    await send_telegram_message(f"Không tìm ra <b>{symbol}</b> trong danh sách của bạn.", target_chat_id=chat_id)
                                    
                            elif cmd == "/LIST":
                                items = db.query(Watchlist).filter_by(chat_id=chat_id).all()
                                if not items:
                                    await send_telegram_message("Giỏ đồ của bạn trống không. Xài lệnh <code>/add</code> nhé!", target_chat_id=chat_id)
                                else:
                                    ans = "📜 <b>Danh sách Auto-Scan của bạn:</b>\n"
                                    for i, it in enumerate(items):
                                        ans += f"{i+1}. {it.symbol}\n"
                                    await send_telegram_message(ans, target_chat_id=chat_id)
                                    
                            db.close()
        except Exception as e:
            await asyncio.sleep(5)
            
        await asyncio.sleep(1)
