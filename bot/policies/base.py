"""
Base Strategy Interface
모든 매매 전략의 기본 클래스
"""
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseStrategy(ABC):
    """
    매매 전략 기본 인터페이스
    """

    def __init__(self, config: Dict):
        """
        Args:
            config: 전략별 설정
        """
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def select_stocks(self, market_data: Dict) -> List[str]:
        """
        종목 선정 로직

        Args:
            market_data: 전체 시장 데이터

        Returns:
            선정된 종목 코드 리스트
        """
        pass

    @abstractmethod
    def check_signal(self, stock_code: str, current_data: Dict, historical_data: List[Dict]) -> str:
        """
        매매 시그널 체크

        Args:
            stock_code: 종목 코드
            current_data: 현재 시세 정보
            historical_data: 과거 시세 데이터

        Returns:
            'BUY', 'SELL', 'HOLD' 중 하나
        """
        pass
