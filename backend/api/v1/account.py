"""
계좌 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from decimal import Decimal

from database import get_db
from models.account import AccountSnapshot, Holding
from schemas.account import AccountSnapshotResponse, HoldingResponse, AccountSummary

router = APIRouter()


@router.get("/summary", response_model=AccountSummary)
def get_account_summary(db: Session = Depends(get_db)):
    """
    계좌 요약 정보 조회

    Returns:
        - 총 자산
        - 예수금
        - 보유 종목 가치
        - 손익
        - 수익률
        - 보유 종목 목록
    """
    # 최신 스냅샷 조회
    latest_snapshot = db.query(AccountSnapshot).order_by(desc(AccountSnapshot.snapshot_at)).first()

    # 현재 보유 종목 조회
    holdings = db.query(Holding).all()

    if not latest_snapshot:
        # 스냅샷이 없으면 기본값 반환
        return AccountSummary(
            total_assets=Decimal("0"),
            cash_balance=Decimal("0"),
            stock_value=Decimal("0"),
            profit_loss=Decimal("0"),
            profit_rate=Decimal("0"),
            holdings_count=0,
            holdings=[]
        )

    return AccountSummary(
        total_assets=latest_snapshot.total_assets,
        cash_balance=latest_snapshot.cash_balance,
        stock_value=latest_snapshot.stock_value,
        profit_loss=latest_snapshot.profit_loss,
        profit_rate=latest_snapshot.profit_rate,
        holdings_count=len(holdings),
        holdings=[HoldingResponse.from_orm(h) for h in holdings]
    )


@router.get("/holdings", response_model=List[HoldingResponse])
def get_holdings(db: Session = Depends(get_db)):
    """
    현재 보유 종목 목록 조회
    """
    holdings = db.query(Holding).all()
    return holdings


@router.get("/snapshots", response_model=List[AccountSnapshotResponse])
def get_account_snapshots(limit: int = 30, db: Session = Depends(get_db)):
    """
    계좌 스냅샷 이력 조회

    Args:
        limit: 조회할 개수 (기본값: 30일)
    """
    snapshots = (
        db.query(AccountSnapshot)
        .order_by(desc(AccountSnapshot.snapshot_at))
        .limit(limit)
        .all()
    )
    return snapshots
