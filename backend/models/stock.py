"""
종목 정보 모델
"""
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class Stock(Base):
    """
    종목 정보 테이블
    """
    __tablename__ = "stocks"

    stock_code = Column(String(10), primary_key=True, index=True)
    stock_name = Column(String(100), nullable=False)
    market = Column(String(10))  # KOSPI, KOSDAQ
    sector = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<Stock(code={self.stock_code}, name={self.stock_name})>"
