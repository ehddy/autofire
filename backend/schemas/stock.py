"""
종목 정보 스키마
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StockBase(BaseModel):
    """
    종목 기본 스키마
    """
    stock_code: str
    stock_name: str
    market: Optional[str] = None
    sector: Optional[str] = None


class StockCreate(StockBase):
    """
    종목 생성 스키마
    """
    pass


class StockResponse(StockBase):
    """
    종목 응답 스키마
    """
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
