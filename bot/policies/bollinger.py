"""
Bollinger Band Strategy
볼린저 밴드 기반 매매 전략

전략 설명:
- 매수: 가격이 하단 밴드 돌파
- 매도: 가격이 상단 밴드 돌파
"""
from typing import List, Dict, Optional
from policies.base import BaseStrategy, SignalType


class BollingerBand_Strategy(BaseStrategy):
    """
    볼린저 밴드 기반 매매 전략

    매매 규칙:
    - 매수 시그널: 가격이 하단 밴드 돌파
    - 매도 시그널: 가격이 상단 밴드 돌파
    - 분봉 데이터로 실시간 밴드 계산
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.bb_period = self.config.get('bb_period', 20)
        self.bb_std = self.config.get('bb_std', 2)  # 표준편차 배수

    def check_signal(
        self,
        stock_code: str,
        current_data: Dict,
        historical_data: Optional[List[Dict]] = None,
        holding_info: Optional[Dict] = None
    ) -> SignalType:
        """
        볼린저 밴드 기반 시그널 체크

        Args:
            stock_code: 종목 코드
            current_data: 현재 시세 정보
            historical_data: 과거 분봉 데이터
            holding_info: 보유 정보 (사용하지 않음)

        Returns:
            'BUY' | 'SELL' | 'HOLD'
        """
        if not historical_data or len(historical_data) < self.bb_period:
            return 'HOLD'

        # 현재가
        current_price = current_data.get('current_price', 0)
        if not current_price:
            return 'HOLD'

        # 분봉 종가 리스트
        prices = [candle.get('close', 0) for candle in historical_data[:self.bb_period]]

        # 볼린저 밴드 계산
        middle, upper, lower = self._calculate_bollinger_bands(prices, self.bb_period, self.bb_std)

        # 시그널 판단
        if current_price <= lower:
            return 'BUY'
        elif current_price >= upper:
            return 'SELL'
        else:
            return 'HOLD'

    def _calculate_bollinger_bands(
        self,
        prices: List[float],
        period: int,
        std_dev: float
    ) -> tuple[float, float, float]:
        """
        볼린저 밴드 계산

        Args:
            prices: 가격 리스트
            period: 기간
            std_dev: 표준편차 배수

        Returns:
            (중심선, 상단밴드, 하단밴드)
        """
        if len(prices) < period:
            avg = prices[0] if prices else 0
            return (avg, avg, avg)

        # 중심선 (이동평균)
        middle = sum(prices[:period]) / period

        # 표준편차
        variance = sum((p - middle) ** 2 for p in prices[:period]) / period
        std = variance ** 0.5

        # 상단/하단 밴드
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return (middle, upper, lower)
