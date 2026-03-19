"""
Equal Weight Allocator
동일 비중 자산 배분 정책

전략 설명:
- 선정된 모든 종목에 동일한 금액 배분 (1/N)
- 가장 단순하고 직관적인 배분 방식
"""
from typing import List, Dict, Optional
from portfolios.base import BasePortfolio


class EqualWeightAllocator(BasePortfolio):
    """
    동일 비중 배분 정책

    배분 기준:
    - 총 예산을 종목 수로 나눔
    - 각 종목에 동일한 금액 할당
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)

    def allocate(self, selected_stocks: List[str], total_budget: float) -> Dict[str, float]:
        """
        동일 비중 자산 배분

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

        # 동일 비중 계산
        num_stocks = len(selected_stocks)
        allocation_per_stock = total_budget / num_stocks

        # 배분 결과 생성
        allocation = {
            stock_code: allocation_per_stock
            for stock_code in selected_stocks
        }

        print(f"[{self.name}] 자산 배분 완료")
        print(f"  - 총 예산: {total_budget:,}원")
        print(f"  - 종목 수: {num_stocks}개")
        print(f"  - 종목당 배분: {allocation_per_stock:,}원")

        return allocation
