"""
MACD Strategy
MACD 기반 매매 전략

전략 설명:
- 매수: MACD선이 시그널선을 상향 돌파 (골든크로스)
- 매도: MACD선이 시그널선을 하향 돌파 (데드크로스)
"""
from typing import List, Dict, Optional
from policies.base import BaseStrategy, SignalType


class MACD_Strategy(BaseStrategy):
    """
    MACD 기반 매매 전략

    매매 규칙:
    - 매수 시그널: MACD선이 시그널선을 상향 돌파 (골든크로스)
    - 매도 시그널: MACD선이 시그널선을 하향 돌파 (데드크로스)
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.fast_period = self.config.get('fast_period', 12)
        self.slow_period = self.config.get('slow_period', 26)
        self.signal_period = self.config.get('signal_period', 9)

    def check_signal(
        self,
        stock_code: str,
        current_data: Dict,
        historical_data: Optional[List[Dict]] = None
    ) -> SignalType:
        """
        MACD 기반 시그널 체크

        TODO: MACD 계산 로직 구현 필요
        """
        # 간단한 구현 예시
        return 'HOLD'

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """
        EMA (Exponential Moving Average) 계산

        Args:
            prices: 가격 리스트 (최신 순)
            period: 기간

        Returns:
            EMA 값
        """
        if len(prices) < period:
            return prices[0] if prices else 0

        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # 초기 SMA

        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema
