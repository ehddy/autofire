"""
실시간 데이터 API 엔드포인트 (KIS API 직접 호출)
"""
from fastapi import APIRouter, HTTPException
from typing import Dict

from services.kis_service import get_kis_service

router = APIRouter()


@router.get("/account/summary")
async def get_live_account_summary() -> Dict:
    """
    실시간 계좌 요약 조회

    **데이터 소스**: 한국투자증권 API (실시간)

    Returns:
        - total_assets: 총 자산
        - cash_balance: 예수금
        - stock_value: 보유 종목 가치
        - profit_loss: 평가 손익
        - profit_rate: 수익률
        - holdings_count: 보유 종목 개수
        - holdings: 보유 종목 상세
    """
    try:
        kis = get_kis_service()
        return kis.get_live_account_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 계좌 조회 실패: {str(e)}")


@router.get("/account/holdings")
async def get_live_holdings():
    """
    실시간 보유 종목 조회

    **데이터 소스**: 한국투자증권 API (실시간)

    Returns:
        보유 종목 리스트 (실시간 평가 금액 포함)
    """
    try:
        kis = get_kis_service()
        return kis.get_live_holdings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"실시간 보유 종목 조회 실패: {str(e)}")


@router.get("/account/buy-power")
async def get_live_buy_power() -> Dict:
    """
    실시간 매수 가능 금액 조회

    **데이터 소스**: 한국투자증권 API (실시간)

    Returns:
        매수 가능 금액
    """
    try:
        kis = get_kis_service()
        available_cash = kis.get_live_buy_power()
        return {"available_cash": available_cash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"매수 가능 금액 조회 실패: {str(e)}")


@router.get("/stocks/{stock_code}/price")
async def get_live_stock_price(stock_code: str) -> Dict:
    """
    실시간 종목 현재가 조회

    **데이터 소스**: 한국투자증권 API (실시간)

    Args:
        stock_code: 종목코드 (6자리)

    Returns:
        현재가 정보 (가격, 등락률, 거래량 등)
    """
    try:
        kis = get_kis_service()
        return kis.get_current_price(stock_code)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"실시간 현재가 조회 실패 ({stock_code}): {str(e)}"
        )
