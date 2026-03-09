"""
계좌 및 보유 종목 모델
"""
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class AccountSnapshot(Base):
    """
    계좌 스냅샷 테이블 (일별/시간별 자산 현황)
    """
    __tablename__ = "account_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_assets = Column(DECIMAL(15, 2))
    cash_balance = Column(DECIMAL(15, 2))
    stock_value = Column(DECIMAL(15, 2))
    profit_loss = Column(DECIMAL(15, 2))
    profit_rate = Column(DECIMAL(5, 2))
    snapshot_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AccountSnapshot(total={self.total_assets}, date={self.snapshot_at})>"


class Holding(Base):
    """
    현재 보유 종목 테이블
    """
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), ForeignKey("stocks.stock_code"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    avg_buy_price = Column(DECIMAL(15, 2))
    current_price = Column(DECIMAL(15, 2))
    profit_loss = Column(DECIMAL(15, 2))
    profit_rate = Column(DECIMAL(5, 2))
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 관계 설정
    stock = relationship("Stock")

    def __repr__(self):
        return f"<Holding(stock={self.stock_code}, qty={self.quantity})>"
