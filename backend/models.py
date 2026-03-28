from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone
import uuid

from database import Base

class TradeSignal(Base):
    __tablename__ = "trade_signals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    symbol = Column(String, index=True)
    strategy = Column(String)
    direction = Column(String) # LONG, SHORT, HOLD
    
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    confidence_score = Column(Integer)
    reasoning = Column(Text)
    
    # Auto-tracking fields
    status = Column(String, default="PENDING", index=True) # PENDING, WIN, LOSS, EXPIRED
    highest_price_reached = Column(Float, nullable=True) # Dùng để tính tỉ lệ ăn trượt
    lowest_price_reached = Column(Float, nullable=True)

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    chat_id = Column(String, index=True) # ID của người đăng ký nhận báo cáo
    symbol = Column(String, index=True) # Đồng Coin, ví dụ: BTCUSDT
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
