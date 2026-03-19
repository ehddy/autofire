"""
Mock Account
가상 계좌 관리

실제 매매 없이 가상으로 계좌를 관리하여 시뮬레이션
"""
from typing import Dict, List
from datetime import datetime


class MockAccount:
    """
    가상 계좌

    실제 증권 계좌처럼 동작하는 가상 계좌
    - 예수금 관리
    - 보유 종목 관리
    - 거래 내역 기록
    """

    def __init__(self, initial_cash: int = 10000000):
        """
        Args:
            initial_cash: 초기 예수금 (기본 1000만원)
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash  # 현재 예수금
        self.holdings = {}  # 보유 종목 {종목코드: {quantity, avg_price, ...}}
        self.trade_history = []  # 거래 내역
        self.daily_trades = 0  # 당일 거래 횟수
        self.traded_stocks = set()  # 거래한 종목 추적 (One-shot 방식)

    def get_balance(self) -> Dict:
        """
        계좌 잔고 조회 (실제 AccountAPI 호환)

        Returns:
            계좌 정보 딕셔너리
        """
        total_stock_value = sum(
            h['quantity'] * h['current_price']
            for h in self.holdings.values()
        )
        total_assets = self.cash + total_stock_value
        profit_loss = total_assets - self.initial_cash
        profit_rate = (profit_loss / self.initial_cash) * 100 if self.initial_cash > 0 else 0

        holdings_list = [
            {
                'stock_code': code,
                'quantity': info['quantity'],
                'avg_buy_price': info['avg_price'],
                'current_price': info['current_price'],
                'profit_rate': ((info['current_price'] - info['avg_price']) / info['avg_price']) * 100
            }
            for code, info in self.holdings.items()
        ]

        return {
            'total_assets': total_assets,
            'cash_balance': self.cash,
            'stock_value': total_stock_value,
            'profit_loss': profit_loss,
            'profit_rate': profit_rate,
            'holdings': holdings_list
        }

    def buy(self, stock_code: str, price: int, quantity: int, timestamp: datetime = None) -> bool:
        """
        매수 주문

        Args:
            stock_code: 종목 코드
            price: 매수 가격
            quantity: 수량
            timestamp: 거래 시간

        Returns:
            성공 여부
        """
        total_cost = price * quantity

        # 예수금 부족 체크
        if total_cost > self.cash:
            print(f"  ❌ 예수금 부족: 필요 {total_cost:,}원 / 보유 {self.cash:,}원")
            return False

        # 예수금 차감
        self.cash -= total_cost

        # 보유 종목 업데이트
        if stock_code in self.holdings:
            # 기존 보유 종목 → 평균 단가 재계산
            holding = self.holdings[stock_code]
            total_qty = holding['quantity'] + quantity
            total_value = (holding['avg_price'] * holding['quantity']) + (price * quantity)
            holding['avg_price'] = int(total_value / total_qty)
            holding['quantity'] = total_qty
            holding['current_price'] = price
        else:
            # 신규 매수
            self.holdings[stock_code] = {
                'quantity': quantity,
                'avg_price': price,
                'current_price': price
            }

        # 거래 내역 기록
        self.trade_history.append({
            'type': 'BUY',
            'stock_code': stock_code,
            'price': price,
            'quantity': quantity,
            'total': total_cost,
            'timestamp': timestamp or datetime.now()
        })
        self.daily_trades += 1
        self.traded_stocks.add(stock_code)  # 거래 종목 추가

        print(f"  ✅ 매수 체결: {stock_code} {quantity}주 @ {price:,}원 (총 {total_cost:,}원)")
        return True

    def sell(self, stock_code: str, price: int, quantity: int = None, timestamp: datetime = None) -> bool:
        """
        매도 주문

        Args:
            stock_code: 종목 코드
            price: 매도 가격
            quantity: 수량 (None이면 전량 매도)
            timestamp: 거래 시간

        Returns:
            성공 여부
        """
        # 보유 여부 체크
        if stock_code not in self.holdings:
            print(f"  ❌ 미보유 종목: {stock_code}")
            return False

        holding = self.holdings[stock_code]

        # 수량 결정 (None이면 전량)
        if quantity is None:
            quantity = holding['quantity']
        elif quantity > holding['quantity']:
            print(f"  ❌ 수량 부족: 요청 {quantity}주 / 보유 {holding['quantity']}주")
            return False

        # 매도 금액 계산
        total_revenue = price * quantity
        profit = (price - holding['avg_price']) * quantity
        profit_rate = ((price - holding['avg_price']) / holding['avg_price']) * 100

        # 예수금 증가
        self.cash += total_revenue

        # 보유 종목 업데이트
        holding['quantity'] -= quantity
        if holding['quantity'] == 0:
            del self.holdings[stock_code]

        # 거래 내역 기록
        self.trade_history.append({
            'type': 'SELL',
            'stock_code': stock_code,
            'price': price,
            'quantity': quantity,
            'total': total_revenue,
            'profit': profit,
            'profit_rate': profit_rate,
            'timestamp': timestamp or datetime.now()
        })
        self.daily_trades += 1

        icon = "💰" if profit > 0 else "🔻"
        print(f"  {icon} 매도 체결: {stock_code} {quantity}주 @ {price:,}원 (손익: {profit:+,}원 / {profit_rate:+.2f}%)")
        return True

    def update_current_prices(self, prices: Dict[str, int]):
        """
        보유 종목 현재가 업데이트

        Args:
            prices: {종목코드: 현재가}
        """
        for stock_code, price in prices.items():
            if stock_code in self.holdings:
                self.holdings[stock_code]['current_price'] = price

    def get_holding(self, stock_code: str) -> Dict:
        """
        특정 종목 보유 정보 조회

        Args:
            stock_code: 종목 코드

        Returns:
            보유 정보 (없으면 None)
        """
        if stock_code not in self.holdings:
            return None

        holding = self.holdings[stock_code]
        profit_rate = ((holding['current_price'] - holding['avg_price']) / holding['avg_price']) * 100

        return {
            'stock_code': stock_code,
            'quantity': holding['quantity'],
            'avg_buy_price': holding['avg_price'],
            'current_price': holding['current_price'],
            'profit_rate': profit_rate
        }

    def has_traded(self, stock_code: str) -> bool:
        """
        특정 종목 거래 이력 확인 (One-shot 방식)

        Args:
            stock_code: 종목 코드

        Returns:
            거래한 적 있으면 True
        """
        return stock_code in self.traded_stocks

    def get_summary(self) -> str:
        """
        계좌 요약 문자열 생성

        Returns:
            요약 문자열
        """
        balance = self.get_balance()
        win_count = sum(1 for t in self.trade_history if t['type'] == 'SELL' and t.get('profit', 0) > 0)
        total_sell = sum(1 for t in self.trade_history if t['type'] == 'SELL')
        win_rate = (win_count / total_sell * 100) if total_sell > 0 else 0

        summary = f"""
==================================================
📊 계좌 요약
==================================================
💰 총 자산: {balance['total_assets']:,}원
💵 예수금: {balance['cash_balance']:,}원
📈 평가금액: {balance['stock_value']:,}원
{'🔴' if balance['profit_loss'] < 0 else '🔵'} 손익: {balance['profit_loss']:+,}원 ({balance['profit_rate']:+.2f}%)

📦 보유 종목: {len(self.holdings)}개
📝 거래 횟수: {len(self.trade_history)}회
✅ 승률: {win_rate:.1f}% ({win_count}/{total_sell})
==================================================
"""
        return summary.strip()
