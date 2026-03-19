"""
Mock Market Data
가상 시세 데이터 생성

실제 시장 패턴을 시뮬레이션하여 테스트용 시세 데이터 제공
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List


class MockMarketData:
    """
    가상 시세 데이터 생성기

    실제 시장의 변동성을 모방한 시세 데이터를 생성합니다.
    """

    def __init__(self, scenario: str = "normal"):
        """
        Args:
            scenario: 시나리오 종류
                - normal: 정상 변동 (±3% 이내)
                - volatile: 고변동성 (±5% 이내)
                - uptrend: 상승 추세 (+5% 목표)
                - downtrend: 하락 추세 (-5% 목표)
        """
        self.scenario = scenario
        self.stocks_data = {}  # {종목코드: {시간: 가격}}
        self.current_time = None

    def initialize_stocks(self, stock_codes: List[str], base_price: int = 50000):
        """
        종목 데이터 초기화

        Args:
            stock_codes: 종목 코드 리스트
            base_price: 기준 가격
        """
        for code in stock_codes:
            # 종목별로 약간 다른 기준가
            price = base_price + random.randint(-10000, 10000)
            self.stocks_data[code] = {
                'base_price': price,
                'current_price': price,
                'open_price': price,
                'high_price': price,
                'low_price': price,
                'volume': random.randint(500000, 2000000),
                'history': []  # 분봉 데이터
            }

    def generate_minute_data(self, stock_code: str, current_time: datetime) -> Dict:
        """
        1분봉 데이터 생성

        Args:
            stock_code: 종목 코드
            current_time: 현재 시간

        Returns:
            시세 데이터 딕셔너리
        """
        if stock_code not in self.stocks_data:
            return None

        stock = self.stocks_data[stock_code]
        prev_price = stock['current_price']

        # 시나리오별 변동률
        if self.scenario == "normal":
            change_rate = random.uniform(-0.005, 0.005)  # ±0.5%
        elif self.scenario == "volatile":
            change_rate = random.uniform(-0.01, 0.01)  # ±1%
        elif self.scenario == "uptrend":
            change_rate = random.uniform(-0.003, 0.008)  # 상승 편향
        elif self.scenario == "downtrend":
            change_rate = random.uniform(-0.008, 0.003)  # 하락 편향
        else:
            change_rate = random.uniform(-0.005, 0.005)

        # 새 가격 계산
        new_price = int(prev_price * (1 + change_rate))
        new_price = max(1000, new_price)  # 최소 1000원

        # 고가/저가 업데이트
        stock['high_price'] = max(stock['high_price'], new_price)
        stock['low_price'] = min(stock['low_price'], new_price)
        stock['current_price'] = new_price

        # 거래량 (랜덤)
        minute_volume = random.randint(1000, 10000)
        stock['volume'] += minute_volume

        # 분봉 기록
        candle = {
            'time': current_time.strftime("%H:%M"),
            'open': prev_price,
            'high': max(prev_price, new_price),
            'low': min(prev_price, new_price),
            'close': new_price,
            'volume': minute_volume
        }
        stock['history'].append(candle)

        return {
            'stock_code': stock_code,
            'current_price': new_price,
            'open_price': stock['open_price'],
            'high_price': stock['high_price'],
            'low_price': stock['low_price'],
            'volume': stock['volume'],
            'change_rate': ((new_price - stock['open_price']) / stock['open_price']) * 100,
            'prev_close': stock['base_price']
        }

    def get_current_price(self, stock_code: str) -> Dict:
        """
        현재가 조회 (실제 MarketDataAPI 호환)

        Args:
            stock_code: 종목 코드

        Returns:
            현재가 정보
        """
        if stock_code not in self.stocks_data:
            return None

        stock = self.stocks_data[stock_code]
        return {
            'stock_code': stock_code,
            'current_price': stock['current_price'],
            'open_price': stock['open_price'],
            'high_price': stock['high_price'],
            'low_price': stock['low_price'],
            'volume': stock['volume'],
            'change_rate': ((stock['current_price'] - stock['open_price']) / stock['open_price']) * 100
        }

    def get_minute_price(self, stock_code: str, count: int = 100) -> List[Dict]:
        """
        분봉 데이터 조회 (실제 MarketDataAPI 호환)

        Args:
            stock_code: 종목 코드
            count: 조회할 분봉 개수

        Returns:
            분봉 데이터 리스트
        """
        if stock_code not in self.stocks_data:
            return []

        history = self.stocks_data[stock_code]['history']
        return history[-count:] if len(history) > count else history

    def get_stock_info(self, stock_code: str) -> Dict:
        """
        종목 정보 조회

        Args:
            stock_code: 종목 코드

        Returns:
            종목 정보
        """
        if stock_code not in self.stocks_data:
            return None

        stock = self.stocks_data[stock_code]
        return {
            'stock_code': stock_code,
            'current_price': stock['current_price'],
            'base_price': stock['base_price'],
            'profit_rate': ((stock['current_price'] - stock['base_price']) / stock['base_price']) * 100
        }
