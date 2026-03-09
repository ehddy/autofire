"""
Technical Selector
기술적 지표 기반 종목 선정 정책

전략 설명:
- 거래대금 상위 종목 중에서
- 기술적 지표(RSI, 이동평균)로 필터링
- 상승 추세 + 과매도 구간 진입 종목 선정
"""
from typing import List, Dict, Optional
from selectors.base import BaseSelector


class TechnicalSelector(BaseSelector):
    """
    기술적 지표 기반 종목 선정

    선정 기준:
    1. 거래대금 상위 100개 종목
    2. RSI 30~50 구간 (과매도 진입)
    3. 20일 이평선 > 60일 이평선 (상승 추세)
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.min_volume = self.config.get('min_volume', 100_000_000)  # 최소 거래대금 1억
        self.rsi_lower = self.config.get('rsi_lower', 30)
        self.rsi_upper = self.config.get('rsi_upper', 50)

    def select_stocks(self, select_count: int = 5) -> List[str]:
        """
        종목 선정 로직 (일봉 기반)

        Args:
            select_count: 선정할 종목 수

        Returns:
            선정된 종목 코드 리스트

        TODO: 실제 구현 시
        1. MarketDataAPI를 사용하여 전체 종목 조회
        2. 거래대금 필터링
        3. 일봉 데이터로 RSI 계산
        4. 이동평균선 계산 및 필터링
        5. 상위 N개 종목 반환
        """
        # 현재는 더미 데이터 반환
        # 실제 구현 시 MarketDataAPI 연동 필요
        print(f"[{self.name}] 종목 선정 시작...")
        print(f"  - 최소 거래대금: {self.min_volume:,}원")
        print(f"  - RSI 범위: {self.rsi_lower}~{self.rsi_upper}")
        print(f"  - 선정 목표: {select_count}개")

        # TODO: 실제 종목 선정 로직 구현
        selected = []

        # 임시 예제 (삼성전자, SK하이닉스 등)
        # 실제로는 API를 통해 동적으로 선정
        dummy_stocks = ['005930', '000660', '035720', '005380', '051910']
        selected = dummy_stocks[:select_count]

        print(f"  ✅ {len(selected)}개 종목 선정 완료")
        return selected

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        RSI (Relative Strength Index) 계산

        Args:
            prices: 가격 리스트 (최신 순)
            period: RSI 기간 (기본 14일)

        Returns:
            RSI 값 (0~100)
        """
        if len(prices) < period + 1:
            return 50.0  # 데이터 부족 시 중립 값

        deltas = [prices[i] - prices[i + 1] for i in range(len(prices) - 1)]
        gains = [d if d > 0 else 0 for d in deltas[:period]]
        losses = [-d if d < 0 else 0 for d in deltas[:period]]

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_ma(self, prices: List[float], period: int) -> float:
        """
        이동평균 계산

        Args:
            prices: 가격 리스트 (최신 순)
            period: 이평 기간

        Returns:
            이동평균 값
        """
        if len(prices) < period:
            return prices[0] if prices else 0

        return sum(prices[:period]) / period
