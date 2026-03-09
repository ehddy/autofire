"""
거래 이력 모델
"""
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class TradeHistory(Base):
    """
    거래 이력 테이블
    """
    __tablename__ = "trade_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    order_type = Column(String(10), nullable=False)  # BUY, SELL
    order_price = Column(DECIMAL(15, 2))
    order_quantity = Column(Integer)
    executed_price = Column(DECIMAL(15, 2))
    executed_quantity = Column(Integer)
    executed_at = Column(TIMESTAMP)
    strategy_name = Column(String(50))
    profit_loss = Column(DECIMAL(15, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 관계 설정
    stock = relationship("Stock")

    def __repr__(self):
        return f"<TradeHistory(id={self.id}, stock={self.stock_code}, type={self.order_type})>"


class DailySelectedStock(Base):
    """
    일별 선정 종목 테이블
    """
    __tablename__ = "daily_selected_stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False)
    selected_date = Column(TIMESTAMP, nullable=False, index=True)
    strategy_name = Column(String(50))
    selection_reason = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 관계 설정
    stock = relationship("Stock")

    def __repr__(self):
        return f"<DailySelectedStock(stock={self.stock_code}, date={self.selected_date})>"
