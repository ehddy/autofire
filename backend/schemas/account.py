"""
계좌 및 보유 종목 스키마
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class AccountSnapshotBase(BaseModel):
    """
    계좌 스냅샷 기본 스키마
    """
    total_assets: Decimal
    cash_balance: Decimal
    stock_value: Decimal
    profit_loss: Decimal
    profit_rate: Decimal


class AccountSnapshotCreate(AccountSnapshotBase):
    """
    계좌 스냅샷 생성 스키마
    """
    pass


class AccountSnapshotResponse(AccountSnapshotBase):
    """
    계좌 스냅샷 응답 스키마
    """
    id: int
    snapshot_at: datetime

    class Config:
        from_attributes = True


class HoldingBase(BaseModel):
    """
    보유 종목 기본 스키마
    """
    stock_code: str
    quantity: int
    avg_buy_price: Decimal
    current_price: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = None
    profit_rate: Optional[Decimal] = None


class HoldingCreate(HoldingBase):
    """
    보유 종목 생성 스키마
    """
    pass


class HoldingResponse(HoldingBase):
    """
    보유 종목 응답 스키마
    """
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountSummary(BaseModel):
    """
    계좌 요약 정보
    """
    total_assets: Decimal
    cash_balance: Decimal
    stock_value: Decimal
    profit_loss: Decimal
    profit_rate: Decimal
    holdings_count: int
    holdings: List[HoldingResponse] = []
