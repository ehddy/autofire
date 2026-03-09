"""
주문 실행 API 엔드포인트 (Bot용)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime

from services.kis_service import get_kis_service
from models.trade import TradeHistory

router = APIRouter()


class BuyOrderRequest(BaseModel):
    """매수 주문 요청"""
    stock_code: str
    quantity: int
    price: Optional[int] = None  # None이면 시장가
    strategy_name: Optional[str] = None


class SellOrderRequest(BaseModel):
    """매도 주문 요청"""
    stock_code: str
    quantity: int
    price: Optional[int] = None  # None이면 시장가
    strategy_name: Optional[str] = None


@router.post("/buy")
async def execute_buy(request: BuyOrderRequest, db: Session = Depends(get_db)) -> Dict:
    """
    매수 주문 실행 + DB 기록

    **사용자**: Bot

    Args:
        request: 매수 주문 정보

    Returns:
        주문 결과 + DB 기록 ID
    """
    try:
        kis = get_kis_service()

        # 1. KIS API로 주문 실행
        result = kis.execute_buy_order(
            request.stock_code,
            request.quantity,
            request.price
        )

        # 2. 성공한 경우 DB에 기록
        if result.get("success"):
            trade = TradeHistory(
                stock_code=request.stock_code,
                order_type="BUY",
                order_price=request.price,
                order_quantity=request.quantity,
                executed_price=result.get("price") if isinstance(result.get("price"), (int, float)) else None,
                executed_quantity=request.quantity,
                executed_at=datetime.now(),
                strategy_name=request.strategy_name,
                profit_loss=None  # 매수 시에는 아직 손익 없음
            )
            db.add(trade)
            db.commit()
            db.refresh(trade)

            result["db_id"] = trade.id
            result["message"] = f"✅ 매수 주문 성공 및 DB 기록 (ID: {trade.id})"

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매수 주문 실패: {str(e)}")


@router.post("/sell")
async def execute_sell(request: SellOrderRequest, db: Session = Depends(get_db)) -> Dict:
    """
    매도 주문 실행 + DB 기록

    **사용자**: Bot

    Args:
        request: 매도 주문 정보

    Returns:
        주문 결과 + DB 기록 ID
    """
    try:
        kis = get_kis_service()

        # 1. KIS API로 주문 실행
        result = kis.execute_sell_order(
            request.stock_code,
            request.quantity,
            request.price
        )

        # 2. 성공한 경우 DB에 기록
        if result.get("success"):
            # TODO: 매도 시 손익 계산 (매수가 대비)
            trade = TradeHistory(
                stock_code=request.stock_code,
                order_type="SELL",
                order_price=request.price,
                order_quantity=request.quantity,
                executed_price=result.get("price") if isinstance(result.get("price"), (int, float)) else None,
                executed_quantity=request.quantity,
                executed_at=datetime.now(),
                strategy_name=request.strategy_name,
                profit_loss=None  # TODO: 계산 필요
            )
            db.add(trade)
            db.commit()
            db.refresh(trade)

            result["db_id"] = trade.id
            result["message"] = f"✅ 매도 주문 성공 및 DB 기록 (ID: {trade.id})"

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매도 주문 실패: {str(e)}")


@router.get("/status/{order_no}")
async def get_order_status(order_no: str) -> Dict:
    """
    주문 상태 조회

    Args:
        order_no: 주문번호

    Returns:
        주문 상태 정보
    """
    try:
        kis = get_kis_service()
        return kis.get_order_status(order_no)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주문 상태 조회 실패: {str(e)}")
