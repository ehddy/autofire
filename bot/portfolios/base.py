"""
Base Portfolio Interface
모든 자산 배분 정책의 기본 클래스

CLAUDE.md 규칙:
- allocate()는 선정된 종목 리스트와 총 예산을 입력받아 {종목코드: 배분금액}을 반환한다
- 사용자가 직접 배분 로직을 커스텀화하여 여러 전략을 구현하고, 그중 하나를 선택하여 사용한다
- 활성화는 .env의 PORTFOLIO_STRATEGY에 클래스명을 지정하는 것으로만 한다
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BasePortfolio(ABC):
    """
    자산 배분 정책 기본 인터페이스

    책임:
    - 선정된 종목들에 대해 가용 자산을 배분
    - 종목별 투자 금액 결정
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: 배분 정책별 설정 (선택사항)
        """
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def allocate(self, selected_stocks: List[str], total_budget: float) -> Dict[str, float]:
        """
        자산 배분 로직

        Args:
            selected_stocks: Selector에 의해 선정된 종목 코드 리스트
            total_budget: 매수 가능한 총 예산 (원)

        Returns:
            종목별 배분 금액 딕셔너리
            예: {
                '005930': 10000000,  # 삼성전자에 1000만원
                '000660': 5000000,   # SK하이닉스에 500만원
            }

        주의사항:
        - 반환된 배분 금액의 합은 total_budget을 초과하면 안됨
        - 각 종목의 배분 금액은 0보다 커야 함
        - 배분되지 않은 종목은 딕셔너리에 포함하지 않음
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.name}>"
