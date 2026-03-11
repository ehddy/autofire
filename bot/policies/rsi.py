"""
RSI Strategy
RSI 지표 기반 매매 전략 (분봉 데이터 사용)

전략 설명:
- 매수: RSI < 30 (과매도)
- 매도: RSI > 70 (과매수)
- 보유: 30 <= RSI <= 70 (중립)
"""
from typing import List, Dict, Optional
from policies.base import BaseStrategy, SignalType


class RSI_Strategy(BaseStrategy):
    """
    RSI 기반 매매 전략

    매매 규칙:
    - 매수 시그널: RSI가 30 이하로 떨어질 때 (과매도)
    - 매도 시그널: RSI가 70 이상으로 올라갈 때 (과매수)
    - 분봉 데이터로 실시간 RSI 계산
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.rsi_period = self.config.get('rsi_period', 14)
        self.rsi_oversold = self.config.get('rsi_oversold', 30)
        self.rsi_overbought = self.config.get('rsi_overbought', 70)

    def check_signal(
        self,
        stock_code: str,
        current_data: Dict,
        historical_data: Optional[List[Dict]] = None,
        holding_info: Optional[Dict] = None
    ) -> SignalType:
        """
        RSI 기반 매매 시그널 체크

        Args:
            stock_code: 종목 코드
            current_data: 현재 시세 정보
                {
                    'current_price': int,
                    'change_rate': float,
                    'volume': int,
                    ...
                }
            historical_data: 과거 분봉 데이터 (최신 순)
                [
                    {'close': int, 'volume': int, 'timestamp': str},
                    ...
                ]
            holding_info: 보유 정보 (사용하지 않음)

        Returns:
            'BUY' | 'SELL' | 'HOLD'
        """
        if not historical_data or len(historical_data) < self.rsi_period + 1:
            # 데이터 부족 시 HOLD
            return 'HOLD'

        # 분봉 종가 리스트 추출 (최신 순)
        prices = [candle.get('close', 0) for candle in historical_data]

        # RSI 계산
        rsi = self._calculate_rsi(prices, self.rsi_period)

        # 시그널 판단
        if rsi <= self.rsi_oversold:
            return 'BUY'
        elif rsi >= self.rsi_overbought:
            return 'SELL'
        else:
            return 'HOLD'

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        RSI (Relative Strength Index) 계산

        Args:
            prices: 가격 리스트 (최신 순)
            period: RSI 기간

        Returns:
            RSI 값 (0~100)
        """
        if len(prices) < period + 1:
            return 50.0

        # 가격 변화량 계산
        deltas = [prices[i] - prices[i + 1] for i in range(len(prices) - 1)]

        # 상승/하락 분리
        gains = [d if d > 0 else 0 for d in deltas[:period]]
        losses = [-d if d < 0 else 0 for d in deltas[:period]]

        # 평균 상승/하락
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi
