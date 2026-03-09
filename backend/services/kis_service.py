"""
한국투자증권 API 서비스 (Backend용)
Backend의 core 모듈을 사용하여 실시간 데이터 제공
"""
import os
from typing import Dict, List, Optional
from decimal import Decimal

# Backend의 KIS API 모듈 import
from core.account import AccountAPI
from core.market_data import MarketDataAPI
from core.order import OrderAPI


class KISService:
    """
    한국투자증권 API 서비스
    Backend에서 실시간 데이터를 제공하기 위한 래퍼
    """

    def __init__(self):
        """KIS API 초기화"""
        self.app_key = os.getenv("APP_KEY")
        self.app_secret = os.getenv("APP_SECRET")
        self.account_no = os.getenv("ACCOUNT_NO")
        self.is_virtual = os.getenv("IS_VIRTUAL", "true").lower() == "true"

        if not all([self.app_key, self.app_secret, self.account_no]):
            print("⚠️ KIS API 환경 변수가 설정되지 않았습니다. 실시간 API를 사용할 수 없습니다.")
            self.enabled = False
            return

        self.enabled = True

        # API 클라이언트 초기화
        try:
            self.account_api = AccountAPI(
                self.app_key,
                self.app_secret,
                self.account_no,
                self.is_virtual
            )
            self.market_api = MarketDataAPI(
                self.app_key,
                self.app_secret,
                self.account_no,
                self.is_virtual
            )
            self.order_api = OrderAPI(
                self.app_key,
                self.app_secret,
                self.account_no,
                self.is_virtual
            )
            print(f"✅ KIS API 초기화 완료 (모드: {'모의투자' if self.is_virtual else '실전투자'})")
        except Exception as e:
            print(f"❌ KIS API 초기화 실패: {str(e)}")
            self.enabled = False

    # ===== 계좌 조회 =====
    def get_live_account_summary(self) -> Dict:
        """
        실시간 계좌 요약 조회 (KIS API 직접 호출)

        Returns:
            계좌 요약 정보
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        balance = self.account_api.get_balance()

        return {
            "total_assets": Decimal(str(balance.get("total_assets", 0))),
            "cash_balance": Decimal(str(balance.get("cash_balance", 0))),
            "stock_value": Decimal(str(balance.get("stock_value", 0))),
            "profit_loss": Decimal(str(balance.get("profit_loss", 0))),
            "profit_rate": Decimal(str(balance.get("profit_rate", 0))),
            "holdings_count": len(balance.get("holdings", [])),
            "holdings": self._convert_holdings(balance.get("holdings", []))
        }

    def get_live_holdings(self) -> List[Dict]:
        """
        실시간 보유 종목 조회

        Returns:
            보유 종목 리스트
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        balance = self.account_api.get_balance()
        return self._convert_holdings(balance.get("holdings", []))

    def get_live_buy_power(self) -> int:
        """
        실시간 매수 가능 금액 조회

        Returns:
            매수 가능 금액
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        return self.account_api.get_buy_available_cash()

    # ===== 시세 조회 =====
    def get_current_price(self, stock_code: str) -> Dict:
        """
        실시간 현재가 조회

        Args:
            stock_code: 종목코드

        Returns:
            현재가 정보
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        return self.market_api.get_current_price(stock_code)

    # ===== 주문 실행 =====
    def execute_buy_order(self, stock_code: str, quantity: int, price: Optional[int] = None) -> Dict:
        """
        매수 주문 실행

        Args:
            stock_code: 종목코드
            quantity: 수량
            price: 가격 (None이면 시장가)

        Returns:
            주문 결과
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        if price is None:
            # 시장가 매수
            return self.order_api.buy_market_order(stock_code, quantity)
        else:
            # 지정가 매수
            return self.order_api.buy_limit_order(stock_code, quantity, price)

    def execute_sell_order(self, stock_code: str, quantity: int, price: Optional[int] = None) -> Dict:
        """
        매도 주문 실행

        Args:
            stock_code: 종목코드
            quantity: 수량
            price: 가격 (None이면 시장가)

        Returns:
            주문 결과
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        if price is None:
            # 시장가 매도
            return self.order_api.sell_market_order(stock_code, quantity)
        else:
            # 지정가 매도
            return self.order_api.sell_limit_order(stock_code, quantity, price)

    def get_order_status(self, order_no: str) -> Dict:
        """
        주문 상태 조회

        Args:
            order_no: 주문번호

        Returns:
            주문 상태 정보
        """
        if not self.enabled:
            raise Exception("KIS API가 초기화되지 않았습니다.")

        return self.order_api.get_order_status(order_no)

    # ===== 헬퍼 메서드 =====
    def _convert_holdings(self, holdings: List[Dict]) -> List[Dict]:
        """
        보유 종목 데이터 변환 (Decimal 타입으로)

        Args:
            holdings: 원본 보유 종목 리스트

        Returns:
            변환된 보유 종목 리스트
        """
        converted = []
        for h in holdings:
            converted.append({
                "stock_code": h.get("stock_code"),
                "stock_name": h.get("stock_name"),
                "quantity": h.get("quantity"),
                "avg_buy_price": Decimal(str(h.get("avg_price", 0))),
                "current_price": Decimal(str(h.get("current_price", 0))),
                "profit_loss": Decimal(str(h.get("profit_loss", 0))),
                "profit_rate": Decimal(str(h.get("profit_rate", 0)))
            })
        return converted


# 싱글톤 인스턴스
_kis_service = None


def get_kis_service() -> KISService:
    """
    KIS 서비스 싱글톤 인스턴스 반환

    Returns:
        KISService 인스턴스
    """
    global _kis_service
    if _kis_service is None:
        _kis_service = KISService()
    return _kis_service
