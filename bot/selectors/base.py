"""
Base Selector Interface
모든 종목 선정 정책의 기본 클래스

CLAUDE.md 규칙:
- select_stocks()는 종목 코드 리스트만 반환한다
- 선정 로직과 DB 저장 로직을 분리한다
- MTF 방식 적용 시 일봉 데이터 기반으로 필터링한다
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseSelector(ABC):
    """
    종목 선정 정책 기본 인터페이스

    책임:
    - 거래할 종목 선정 (일봉 기반 필터링)
    - 종목 코드 리스트만 반환
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: 선정 정책별 설정 (선택사항)
        """
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def select_stocks(self, select_count: int = 5) -> List[str]:
        """
        종목 선정 로직 (일봉 기반)

        Args:
            select_count: 선정할 종목 수

        Returns:
            선정된 종목 코드 리스트 (예: ['005930', '000660', ...])

        주의사항:
        - 종목 코드만 반환한다 (DB 저장은 호출자가 처리)
        - MTF 방식 사용 시 일봉 데이터로만 필터링한다
        - policy와 독립적으로 동작해야 한다
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.name}>"
