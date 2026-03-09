"""
거래 이력 스키마
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class TradeHistoryBase(BaseModel):
    """
    거래 이력 기본 스키마
    """
    stock_code: str
    order_type: str  # BUY, SELL
    order_price: Optional[Decimal] = None
    order_quantity: Optional[int] = None
    executed_price: Optional[Decimal] = None
    executed_quantity: Optional[int] = None
    strategy_name: Optional[str] = None
    profit_loss: Optional[Decimal] = None


class TradeHistoryCreate(TradeHistoryBase):
    """
    거래 이력 생성 스키마
    """
    executed_at: Optional[datetime] = None


class TradeHistoryResponse(TradeHistoryBase):
    """
    거래 이력 응답 스키마
    """
    id: int
    executed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DailySelectedStockBase(BaseModel):
    """
    일별 선정 종목 기본 스키마
    """
    stock_code: str
    strategy_name: Optional[str] = None
    selection_reason: Optional[str] = None


class DailySelectedStockCreate(DailySelectedStockBase):
    """
    일별 선정 종목 생성 스키마
    """
    selected_date: datetime


class DailySelectedStockResponse(DailySelectedStockBase):
    """
    일별 선정 종목 응답 스키마
    """
    id: int
    selected_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
