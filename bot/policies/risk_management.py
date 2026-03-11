"""
리스크 관리 전략

익절, 손절, Daily Stop 로직을 담당하는 필수 전략입니다.
이 전략은 다른 전략보다 우선적으로 실행되어야 합니다.

작동 방식:
- 매수 시그널: 항상 'HOLD' (매수는 다른 전략이 담당)
- 매도 시그널:
  1. 익절: 수익률이 TAKE_PROFIT 이상일 때 'SELL'
  2. 손절: 손실률이 STOP_LOSS 이하일 때 'SELL'
  3. 그 외: 'HOLD'
"""

from typing import Dict, List, Optional
from policies.base import BaseStrategy, SignalType
from config import config


class RiskManagement_Strategy(BaseStrategy):
    """
    리스크 관리 전략 (익절/손절)

    이 전략은 .env의 다음 설정을 사용합니다:
    - TAKE_PROFIT: 익절 기준 (기본값: 3.0%)
    - STOP_LOSS: 손절 기준 (기본값: -2.0%)
    - DAILY_STOP_LOSS: 일일 손절 기준 (기본값: -3.0%) - main.py에서 처리
    """

    def __init__(self):
        self.name = "RiskManagement_Strategy"
        self.take_profit = config.TAKE_PROFIT
        self.stop_loss = config.STOP_LOSS
        print(f"✅ {self.name} 초기화 완료")
        print(f"  익절: +{self.take_profit}%, 손절: {self.stop_loss}%")

    def check_signal(
        self,
        stock_code: str,
        current_data: Dict,
        historical_data: Optional[List[Dict]] = None,
        holding_info: Optional[Dict] = None
    ) -> SignalType:
        """
        리스크 관리 시그널 체크

        Args:
            stock_code: 종목 코드
            current_data: 현재 시세 데이터
            historical_data: 과거 데이터 (사용하지 않음)
            holding_info: 보유 정보 (avg_buy_price, profit_rate 필수)
                예: {'avg_buy_price': 50000, 'profit_rate': 3.5, 'quantity': 10}

        Returns:
            'SELL': 익절 또는 손절 조건 충족
            'HOLD': 조건 미충족 또는 매수 시그널 요청
        """
        # 보유 정보가 없으면 매수/미보유 상황 -> 리스크 관리 불필요
        if not holding_info:
            return 'HOLD'

        profit_rate = holding_info.get('profit_rate', 0)

        # 1. 익절 체크
        if profit_rate >= self.take_profit:
            return 'SELL'  # 익절

        # 2. 손절 체크
        if profit_rate <= self.stop_loss:
            return 'SELL'  # 손절

        # 3. 익절/손절 범위 내에 있음
        return 'HOLD'

    def get_sell_reason(self, profit_rate: float) -> str:
        """
        매도 사유 반환 (로깅용)

        Args:
            profit_rate: 수익률

        Returns:
            매도 사유 문자열
        """
        if profit_rate >= self.take_profit:
            return f"익절 (목표: +{self.take_profit}%, 현재: {profit_rate:+.2f}%)"
        elif profit_rate <= self.stop_loss:
            return f"손절 (기준: {self.stop_loss}%, 현재: {profit_rate:+.2f}%)"
        else:
            return "리스크 관리 범위 내"
