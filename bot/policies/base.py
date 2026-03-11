"""
Base Strategy Interface
모든 매매 전략의 기본 클래스

CLAUDE.md 규칙:
- check_signal()은 반드시 'BUY' | 'SELL' | 'HOLD' 중 하나만 반환
- 전략 내부에서 주문을 직접 실행하지 않음 (시그널만 반환)
- MTF 방식 사용 시 분봉 데이터만 담당
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Literal


SignalType = Literal['BUY', 'SELL', 'HOLD']


class BaseStrategy(ABC):
    """
    매매 전략 기본 인터페이스

    책임:
    - 매수/매도 시그널 판단 (분봉 기반)
    - 시그널만 반환 (주문 실행은 봇 엔진이 처리)
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: 전략별 설정 (선택사항)
        """
        self.config = config or {}
        self.name = self.__class__.__name__

    @abstractmethod
    def check_signal(
        self,
        stock_code: str,
        current_data: Dict,
        historical_data: Optional[List[Dict]] = None,
        holding_info: Optional[Dict] = None
    ) -> SignalType:
        """
        매매 시그널 체크 (분봉 기반)

        Args:
            stock_code: 종목 코드
            current_data: 현재 시세 정보
            historical_data: 과거 시세 데이터 (선택사항)
            holding_info: 보유 정보 (선택사항, 매도 시그널 체크 시 전달)
                {'avg_buy_price': float, 'profit_rate': float, 'quantity': int, ...}

        Returns:
            'BUY' | 'SELL' | 'HOLD'

        주의사항:
        - 반드시 'BUY', 'SELL', 'HOLD' 중 하나만 반환
        - 주문 실행은 하지 않음 (봇 엔진이 처리)
        - MTF 방식 사용 시 분봉 데이터만 사용
        - holding_info는 매도 시그널 체크 시에만 전달됨 (매수 시에는 None)
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.name}>"
