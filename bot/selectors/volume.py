"""
Volume Selector
거래량 급증 종목 선정 정책

전략 설명:
- 당일 거래량이 20일 평균 대비 N배 이상
- 가격 상승 중인 종목만
- 거래대금 필터링
"""
from typing import List, Dict, Optional
from selectors.base import BaseSelector


class VolumeSelector(BaseSelector):
    """
    거래량 급증 종목 선정

    선정 기준:
    1. 당일 거래량이 20일 평균 대비 2배 이상
    2. 가격 상승 중 (전일 대비 +1% 이상)
    3. 거래대금 1억 이상
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.volume_ratio = self.config.get('volume_ratio', 2.0)  # 평균 대비 배수
        self.min_price_change = self.config.get('min_price_change', 1.0)  # 최소 상승률 %

    def select_stocks(self, select_count: int = 5) -> List[str]:
        """
        거래량 급증 종목 선정 (일봉 기반)

        Args:
            select_count: 선정할 종목 수

        Returns:
            선정된 종목 코드 리스트
        """
        print(f"[{self.name}] 종목 선정 시작...")
        print(f"  - 거래량 배수: {self.volume_ratio}배")
        print(f"  - 최소 상승률: +{self.min_price_change}%")

        # TODO: 실제 구현
        # 1. 전체 종목의 당일 거래량 조회
        # 2. 20일 평균 거래량과 비교
        # 3. 조건 충족 종목 필터링
        # 4. 상위 N개 선정

        selected = ['005930', '000660', '035720'][:select_count]
        print(f"  ✅ {len(selected)}개 종목 선정 완료")
        return selected
