"""
Weight-based Allocator
가중치 기반 자산 배분 정책

전략 설명:
- 종목별로 차등 가중치를 부여하여 배분
- 확신도, 리스크 지표 등에 따라 가중치 조정 가능
"""
from typing import List, Dict, Optional
from portfolios.base import BasePortfolio


class WeightAllocator(BasePortfolio):
    """
    가중치 기반 배분 정책

    배분 기준:
    - 종목별 가중치를 계산 (예: 기술적 지표, 확신도 등)
    - 가중치에 비례하여 자산 배분
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        # 사용자 정의 가중치 (종목코드: 가중치)
        # 예: {'005930': 2.0, '000660': 1.5}  # 삼성전자 2배, SK하이닉스 1.5배
        self.custom_weights = self.config.get('weights', {})

    def allocate(self, selected_stocks: List[str], total_budget: float) -> Dict[str, float]:
        """
        가중치 기반 자산 배분

        Args:
            selected_stocks: 선정된 종목 코드 리스트
            total_budget: 총 예산 (원)

        Returns:
            종목별 배분 금액 딕셔너리
        """
        if not selected_stocks:
            print(f"[{self.name}] 선정된 종목이 없습니다.")
            return {}

        if total_budget <= 0:
            print(f"[{self.name}] 가용 예산이 없습니다: {total_budget:,}원")
            return {}

        # 가중치 계산
        weights = self._calculate_weights(selected_stocks)

        # 가중치 합계
        total_weight = sum(weights.values())

        if total_weight == 0:
            print(f"[{self.name}] 가중치 합계가 0입니다. 동일 비중으로 배분합니다.")
            # Fallback: 동일 비중
            equal_amount = total_budget / len(selected_stocks)
            return {stock: equal_amount for stock in selected_stocks}

        # 가중치에 비례하여 배분
        allocation = {
            stock_code: (weights[stock_code] / total_weight) * total_budget
            for stock_code in selected_stocks
        }

        print(f"[{self.name}] 자산 배분 완료")
        print(f"  - 총 예산: {total_budget:,}원")
        print(f"  - 종목 수: {len(selected_stocks)}개")
        for stock_code, amount in allocation.items():
            weight = weights[stock_code]
            ratio = (amount / total_budget) * 100
            print(f"  - {stock_code}: {amount:,}원 (가중치: {weight:.2f}, 비중: {ratio:.1f}%)")

        return allocation

    def _calculate_weights(self, selected_stocks: List[str]) -> Dict[str, float]:
        """
        종목별 가중치 계산

        Args:
            selected_stocks: 선정된 종목 코드 리스트

        Returns:
            종목별 가중치 딕셔너리

        Note:
            현재는 custom_weights에서 가져오고, 없으면 기본값 1.0 사용
            실제 구현 시 기술적 지표, 확신도 등으로 동적 계산 가능
        """
        weights = {}

        for stock_code in selected_stocks:
            # 커스텀 가중치가 있으면 사용, 없으면 기본값 1.0
            weights[stock_code] = self.custom_weights.get(stock_code, 1.0)

        return weights
