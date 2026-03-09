"""
거래 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.trade import TradeHistory
from schemas.trade import TradeHistoryResponse

router = APIRouter()


@router.get("/history", response_model=List[TradeHistoryResponse])
def get_trade_history(
    limit: int = Query(50, description="조회할 개수"),
    stock_code: Optional[str] = Query(None, description="종목코드로 필터"),
    order_type: Optional[str] = Query(None, description="주문 유형 필터 (BUY/SELL)"),
    db: Session = Depends(get_db)
):
    """
    거래 이력 조회

    Args:
        limit: 조회할 개수 (기본값: 50)
        stock_code: 특정 종목만 필터 (선택)
        order_type: BUY 또는 SELL로 필터 (선택)

    Returns:
        거래 이력 목록
    """
    query = db.query(TradeHistory)

    # 필터 적용
    if stock_code:
        query = query.filter(TradeHistory.stock_code == stock_code)

    if order_type:
        query = query.filter(TradeHistory.order_type == order_type.upper())

    # 최신순 정렬 및 개수 제한
    trades = query.order_by(desc(TradeHistory.executed_at)).limit(limit).all()

    return trades


@router.get("/history/today", response_model=List[TradeHistoryResponse])
def get_today_trades(db: Session = Depends(get_db)):
    """
    금일 거래 내역 조회
    """
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    trades = (
        db.query(TradeHistory)
        .filter(TradeHistory.executed_at >= today_start)
        .order_by(desc(TradeHistory.executed_at))
        .all()
    )

    return trades


@router.get("/stats/summary")
def get_trading_stats(
    days: int = Query(30, description="통계 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    거래 통계 요약

    Args:
        days: 통계 기간 (기본값: 30일)

    Returns:
        - 총 거래 횟수
        - 매수 횟수
        - 매도 횟수
        - 총 손익
        - 승률
    """
    start_date = datetime.now() - timedelta(days=days)

    # 전체 거래 횟수
    total_trades = db.query(func.count(TradeHistory.id)).filter(
        TradeHistory.executed_at >= start_date
    ).scalar()

    # 매수 횟수
    buy_count = db.query(func.count(TradeHistory.id)).filter(
        and_(
            TradeHistory.executed_at >= start_date,
            TradeHistory.order_type == "BUY"
        )
    ).scalar()

    # 매도 횟수
    sell_count = db.query(func.count(TradeHistory.id)).filter(
        and_(
            TradeHistory.executed_at >= start_date,
            TradeHistory.order_type == "SELL"
        )
    ).scalar()

    # 총 손익 (매도 거래의 profit_loss 합계)
    total_profit = db.query(func.sum(TradeHistory.profit_loss)).filter(
        and_(
            TradeHistory.executed_at >= start_date,
            TradeHistory.order_type == "SELL",
            TradeHistory.profit_loss.isnot(None)
        )
    ).scalar() or 0

    # 승률 계산 (이익 거래 / 전체 매도 거래)
    win_count = db.query(func.count(TradeHistory.id)).filter(
        and_(
            TradeHistory.executed_at >= start_date,
            TradeHistory.order_type == "SELL",
            TradeHistory.profit_loss > 0
        )
    ).scalar()

    win_rate = (win_count / sell_count * 100) if sell_count > 0 else 0

    return {
        "period_days": days,
        "total_trades": total_trades or 0,
        "buy_count": buy_count or 0,
        "sell_count": sell_count or 0,
        "total_profit_loss": float(total_profit),
        "win_rate": round(win_rate, 2),
        "win_count": win_count or 0
    }
