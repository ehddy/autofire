"""
종목 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models.stock import Stock
from models.trade import DailySelectedStock
from schemas.stock import StockResponse
from schemas.trade import DailySelectedStockResponse

router = APIRouter()


@router.get("/selected/today", response_model=List[DailySelectedStockResponse])
def get_today_selected_stocks(db: Session = Depends(get_db)):
    """
    금일 선정 종목 조회
    """
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    selected = (
        db.query(DailySelectedStock)
        .filter(DailySelectedStock.selected_date >= today_start)
        .all()
    )

    return selected


@router.get("/selected/history", response_model=List[DailySelectedStockResponse])
def get_selected_stocks_history(
    days: int = Query(7, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    과거 선정 종목 이력 조회

    Args:
        days: 조회 기간 (기본값: 7일)
    """
    start_date = datetime.now() - timedelta(days=days)

    selected = (
        db.query(DailySelectedStock)
        .filter(DailySelectedStock.selected_date >= start_date)
        .order_by(desc(DailySelectedStock.selected_date))
        .all()
    )

    return selected


@router.get("/search", response_model=List[StockResponse])
def search_stocks(
    keyword: str = Query(..., description="종목명 또는 코드"),
    limit: int = Query(20, description="최대 결과 개수"),
    db: Session = Depends(get_db)
):
    """
    종목 검색

    Args:
        keyword: 검색 키워드 (종목명 또는 종목코드)
        limit: 최대 결과 개수
    """
    stocks = (
        db.query(Stock)
        .filter(
            (Stock.stock_name.like(f"%{keyword}%")) |
            (Stock.stock_code.like(f"%{keyword}%"))
        )
        .limit(limit)
        .all()
    )

    return stocks


@router.get("/{stock_code}", response_model=StockResponse)
def get_stock_info(stock_code: str, db: Session = Depends(get_db)):
    """
    특정 종목 정보 조회

    Args:
        stock_code: 종목코드 (6자리)
    """
    stock = db.query(Stock).filter(Stock.stock_code == stock_code).first()

    if not stock:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"종목을 찾을 수 없습니다: {stock_code}")

    return stock
