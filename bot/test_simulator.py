#!/usr/bin/env python3
"""
AutoFIRE Trading Simulator
실제 장 시간 없이 전체 시스템 테스트

사용법:
    python test_simulator.py --date 2024-03-20 --scenario normal
    python test_simulator.py --fast  # 빠른 모드 (시간 압축)
"""
import sys
import time
import importlib
from datetime import datetime, timedelta
from typing import List, Dict
import argparse

# 프로젝트 경로 추가
sys.path.insert(0, '/app')

from config import config
from mock.mock_market_data import MockMarketData
from mock.mock_account import MockAccount
from notifications.discord import DiscordNotifier


class TradingSimulator:
    """
    매매 시뮬레이터

    실제 봇의 로직을 그대로 사용하되, 실제 API 대신 Mock 데이터 사용
    """

    def __init__(self, test_date: str = None, scenario: str = "normal", fast_mode: bool = False, minutes: int = None):
        """
        Args:
            test_date: 테스트 날짜 (YYYY-MM-DD)
            scenario: 시장 시나리오 (normal/volatile/uptrend/downtrend)
            fast_mode: 빠른 모드 (시간 압축)
            minutes: 실행할 분 수 (None이면 전체 장 시간)
        """
        self.test_date = test_date or datetime.now().strftime("%Y-%m-%d")
        self.scenario = scenario
        self.fast_mode = fast_mode
        self.max_minutes = minutes  # 제한 시간

        # Mock 객체
        self.market_data = MockMarketData(scenario=scenario)
        self.account = MockAccount(initial_cash=10000000)  # 1000만원
        self.notifier = DiscordNotifier()

        # 봇 상태
        self.selected_stocks: List[str] = []
        self.portfolio_allocation: Dict[str, float] = {}
        self.selectors = []
        self.portfolio = None
        self.strategies = []

        # 시간
        self.current_time = None

        print(f"\n{'='*50}")
        print(f"🧪 AutoFIRE 시뮬레이터 시작")
        print(f"{'='*50}")
        print(f"📅 날짜: {self.test_date}")
        print(f"🎬 시나리오: {scenario}")
        print(f"⚡ 모드: {'빠른 모드 (압축)' if fast_mode else '실시간 속도'}")
        if self.max_minutes:
            print(f"⏱️ 실행 시간: {self.max_minutes}분")
        print(f"💰 초기 자본: {self.account.initial_cash:,}원")
        print(f"{'='*50}\n")

        # Discord 알림
        self.notifier.send_message(f"""🧪 **시뮬레이터 시작**

📅 날짜: {self.test_date}
🎬 시나리오: {scenario}
💰 초기 자본: {self.account.initial_cash:,}원
""")

    def _load_selectors(self):
        """Selector 로드"""
        if not config.SELECTION_POLICIES:
            print("⚠️ SELECTION_POLICIES가 설정되지 않았습니다.")
            return

        for policy_name in config.SELECTION_POLICIES:
            try:
                # selectors/ 폴더에서 동적 로드
                module = importlib.import_module('selectors.base')
                # 실제 환경에서는 각 파일에서 로드하지만, 테스트에서는 간소화
                print(f"  ℹ️ Selector: {policy_name} (Mock)")
            except Exception as e:
                print(f"  ⚠️ Selector 로드 실패: {policy_name} - {str(e)}")

    def _load_portfolio(self):
        """Portfolio 로드"""
        portfolio_name = config.PORTFOLIO_STRATEGY or "EqualWeightAllocator"
        print(f"  ℹ️ Portfolio: {portfolio_name}")

    def _load_strategies(self):
        """Strategy 로드"""
        if not config.ACTIVE_STRATEGIES:
            print("⚠️ ACTIVE_STRATEGIES가 설정되지 않았습니다.")
            return

        for strategy_name in config.ACTIVE_STRATEGIES:
            print(f"  ℹ️ Strategy: {strategy_name} (Mock)")

    def run_stock_selection(self):
        """
        종목 선정 시뮬레이션

        실제 Selector 대신 가상 종목 선정
        """
        print(f"\n{'='*50}")
        print(f"[{self.current_time.strftime('%H:%M')}] 📋 종목 선정")
        print(f"{'='*50}")

        # Mock: 5개 종목 선정 (실제로는 Selector 사용)
        mock_stocks = ['005930', '000660', '035420', '051910', '068270']
        self.selected_stocks = mock_stocks[:config.SELECT_COUNT]

        print(f"🔀 선정 모드: {config.SELECTION_MODE}")
        print(f"✅ 선정 완료: {len(self.selected_stocks)}개 종목")
        for stock in self.selected_stocks:
            print(f"  - {stock}")

        # Mock 시세 초기화
        self.market_data.initialize_stocks(self.selected_stocks)

        # Discord 알림
        stocks_str = ", ".join(self.selected_stocks)
        self.notifier.send_message(f"""📋 **종목 선정 완료**

🔀 모드: {config.SELECTION_MODE}
✅ 선정: {len(self.selected_stocks)}개
{stocks_str}
""")

    def run_portfolio_allocation(self):
        """
        자산 배분 시뮬레이션
        """
        print(f"\n{'='*50}")
        print(f"[{self.current_time.strftime('%H:%M')}] 💼 자산 배분")
        print(f"{'='*50}")

        total_budget = min(self.account.cash, config.MAX_BUY_AMOUNT * len(self.selected_stocks))

        # EqualWeightAllocator 시뮬레이션
        if len(self.selected_stocks) > 0:
            allocation_per_stock = total_budget / len(self.selected_stocks)
            self.portfolio_allocation = {
                stock: allocation_per_stock
                for stock in self.selected_stocks
            }

            print(f"💼 전략: {config.PORTFOLIO_STRATEGY}")
            print(f"💰 총 예산: {total_budget:,}원")
            print(f"📊 종목당: {allocation_per_stock:,}원")

            allocation_details = "\n".join([
                f"  • {stock}: {amount:,.0f}원"
                for stock, amount in self.portfolio_allocation.items()
            ])

            # Discord 알림
            self.notifier.send_message(f"""💼 **자산 배분 완료**

전략: {config.PORTFOLIO_STRATEGY}
총 예산: {total_budget:,}원

{allocation_details}
""")

    def check_buy_signals(self):
        """
        매수 시그널 체크 및 실행
        """
        for stock_code in self.selected_stocks:
            # One-shot 방식: 이미 거래한 종목은 스킵
            if self.account.has_traded(stock_code):
                continue

            # 배분 금액 확인
            allocated_amount = self.portfolio_allocation.get(stock_code, 0)
            if allocated_amount <= 0:
                continue

            # 현재가 조회
            price_data = self.market_data.get_current_price(stock_code)
            current_price = price_data['current_price']

            # Mock: 랜덤하게 매수 시그널 발생 (실제로는 Strategy 사용)
            # 여기서는 간단히 10% 확률로 매수
            import random
            buy_signal = random.random() < 0.3  # 30% 확률

            if buy_signal:
                # 매수 가능 수량 계산
                quantity = int(allocated_amount / current_price)
                if quantity > 0:
                    print(f"\n  🟢 [{stock_code}] 매수 시그널!")
                    print(f"  ⚡ 모드: {config.STRATEGY_MODE}")

                    # 매수 실행
                    success = self.account.buy(stock_code, current_price, quantity, self.current_time)
                    if success:
                        self.notifier.send_message(f"""🟢 **매수 체결**

종목: {stock_code}
가격: {current_price:,}원
수량: {quantity}주
금액: {current_price * quantity:,}원
""")

    def check_sell_signals(self):
        """
        매도 시그널 체크 및 실행 (익절/손절 포함)
        """
        for stock_code in list(self.account.holdings.keys()):
            holding = self.account.get_holding(stock_code)
            if not holding:
                continue

            # 현재가 조회
            price_data = self.market_data.get_current_price(stock_code)
            current_price = price_data['current_price']

            # 현재가 업데이트
            self.account.update_current_prices({stock_code: current_price})

            # 다시 조회 (업데이트된 정보)
            holding = self.account.get_holding(stock_code)
            profit_rate = holding['profit_rate']

            # 1. 익절/손절 체크 (RiskManagement - 최우선)
            take_profit_rate = config.TAKE_PROFIT
            stop_loss_rate = config.STOP_LOSS

            should_sell = False
            reason = None

            if profit_rate >= take_profit_rate:
                should_sell = True
                reason = f"익절 (+{profit_rate:.2f}%)"
                icon = "💰"
            elif profit_rate <= stop_loss_rate:
                should_sell = True
                reason = f"손절 ({profit_rate:.2f}%)"
                icon = "🔻"
            else:
                # 2. 전략 시그널 체크 (Mock: 랜덤)
                import random
                sell_signal = random.random() < 0.1  # 10% 확률

                if sell_signal:
                    should_sell = True
                    reason = f"전략 시그널 ({profit_rate:+.2f}%)"
                    icon = "🔴"

            # 매도 실행
            if should_sell:
                print(f"\n  {icon} [{stock_code}] 매도 시그널: {reason}")
                success = self.account.sell(stock_code, current_price, timestamp=self.current_time)
                if success:
                    self.notifier.send_message(f"""{icon} **매도 체결**

종목: {stock_code}
사유: {reason}
가격: {current_price:,}원
수익률: {profit_rate:+.2f}%
""")

    def run_minute_loop(self, start_time: datetime, end_time: datetime):
        """
        분봉 루프 실행

        Args:
            start_time: 시작 시간
            end_time: 종료 시간
        """
        self.current_time = start_time
        minutes_elapsed = 0

        while self.current_time <= end_time:
            # 제한 시간 체크
            if self.max_minutes and minutes_elapsed >= self.max_minutes:
                print(f"\n⏱️ 설정된 시간 제한 ({self.max_minutes}분) 도달. 시뮬레이션 종료.")
                break
            time_str = self.current_time.strftime("%H:%M")

            # 09:00~09:10은 관망 구간
            if self.current_time.hour == 9 and self.current_time.minute < 10:
                print(f"\n[{time_str}] 🔶 관망 구간 (매수 제한)")
            else:
                print(f"\n[{time_str}] ⏰ 모니터링...")

                # 분봉 데이터 생성 (모든 종목)
                for stock_code in self.selected_stocks:
                    self.market_data.generate_minute_data(stock_code, self.current_time)

                # 현재가 업데이트
                prices = {}
                for stock_code in self.selected_stocks:
                    price_data = self.market_data.get_current_price(stock_code)
                    prices[stock_code] = price_data['current_price']
                self.account.update_current_prices(prices)

                # 강제 청산 시간 체크 (15:20)
                force_liquidation_time = datetime.strptime(config.MARKET_CLOSE_TIME, "%H:%M").time()
                if self.current_time.time() >= force_liquidation_time:
                    print(f"\n🔴 강제 청산 시간!")
                    self._force_liquidation()
                    break

                # 매도 시그널 체크 (보유 종목)
                self.check_sell_signals()

                # 매수 시그널 체크 (미보유 종목, 관망 구간 제외)
                if not (self.current_time.hour == 9 and self.current_time.minute < 10):
                    self.check_buy_signals()

            # 다음 분으로
            self.current_time += timedelta(minutes=1)
            minutes_elapsed += 1

            # 빠른 모드가 아니면 대기
            if not self.fast_mode:
                time.sleep(0.5)  # 0.5초 대기 (실제 1분을 0.5초로 압축)

    def _force_liquidation(self):
        """강제 청산 (전량 시장가 매도)"""
        print(f"\n{'='*50}")
        print(f"🔴 강제 청산 ({config.MARKET_CLOSE_TIME})")
        print(f"{'='*50}")

        if not self.account.holdings:
            print("  보유 종목 없음")
            return

        for stock_code in list(self.account.holdings.keys()):
            price_data = self.market_data.get_current_price(stock_code)
            current_price = price_data['current_price']

            print(f"  🔴 [{stock_code}] 시장가 강제 매도")
            self.account.sell(stock_code, current_price, timestamp=self.current_time)

        self.notifier.send_message(f"""🔴 **강제 청산 완료**

시간: {config.MARKET_CLOSE_TIME}
매도 종목: {len(self.account.holdings)}개
""")

    def run(self):
        """시뮬레이터 실행"""
        try:
            # 1. 설정 로드
            print(f"\n📦 모듈 로딩...")
            self._load_selectors()
            self._load_portfolio()
            self._load_strategies()

            # 2. 종목 선정 (08:30)
            selection_time = datetime.strptime(f"{self.test_date} {config.SELECTION_TIME}", "%Y-%m-%d %H:%M")
            self.current_time = selection_time
            self.run_stock_selection()

            # 3. 자산 배분
            self.run_portfolio_allocation()

            # 4. 장 시작 (09:00 ~ 15:30)
            market_open = datetime.strptime(f"{self.test_date} {config.MARKET_OPEN_TIME}", "%Y-%m-%d %H:%M")
            market_close = datetime.strptime(f"{self.test_date} {config.MARKET_CLOSE_TIME}", "%Y-%m-%d %H:%M")

            print(f"\n{'='*50}")
            print(f"🚀 장 시작 ({config.MARKET_OPEN_TIME} ~ {config.MARKET_CLOSE_TIME})")
            print(f"{'='*50}")

            # 분봉 루프
            self.run_minute_loop(market_open, market_close)

            # 5. 결과 리포트
            self.print_final_report()

        except KeyboardInterrupt:
            print(f"\n\n👋 사용자에 의해 시뮬레이터 중지")
            self.print_final_report()

        except Exception as e:
            print(f"\n❌ 시뮬레이터 오류: {str(e)}")
            import traceback
            traceback.print_exc()

    def print_final_report(self):
        """최종 리포트 출력"""
        print(f"\n{'='*50}")
        print(f"📊 시뮬레이션 결과")
        print(f"{'='*50}")

        # 계좌 요약
        summary = self.account.get_summary()
        print(summary)

        # 거래 내역
        if self.account.trade_history:
            print(f"\n📝 거래 내역 ({len(self.account.trade_history)}건)")
            print(f"{'-'*50}")
            for trade in self.account.trade_history[-10:]:  # 최근 10건만
                timestamp = trade['timestamp'].strftime("%H:%M")
                trade_type = trade['type']
                icon = "🟢" if trade_type == "BUY" else "🔴"
                stock = trade['stock_code']
                price = trade['price']
                qty = trade['quantity']
                total = trade['total']

                if trade_type == "SELL":
                    profit = trade.get('profit', 0)
                    profit_rate = trade.get('profit_rate', 0)
                    print(f"{icon} [{timestamp}] {trade_type:4s} {stock} {qty:3d}주 @ {price:7,}원 → {profit:+8,}원 ({profit_rate:+.2f}%)")
                else:
                    print(f"{icon} [{timestamp}] {trade_type:4s} {stock} {qty:3d}주 @ {price:7,}원 (총 {total:,}원)")

        # Discord 최종 리포트
        balance = self.account.get_balance()
        self.notifier.send_message(f"""📊 **시뮬레이션 완료**

💰 최종 자산: {balance['total_assets']:,}원
{'🔴' if balance['profit_loss'] < 0 else '🔵'} 손익: {balance['profit_loss']:+,}원 ({balance['profit_rate']:+.2f}%)

📝 거래: {len(self.account.trade_history)}건
📦 보유: {len(self.account.holdings)}개
""")

        print(f"\n{'='*50}")
        print(f"✅ 시뮬레이션 종료")
        print(f"{'='*50}\n")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='AutoFIRE Trading Simulator')
    parser.add_argument('--date', type=str, default=None, help='테스트 날짜 (YYYY-MM-DD)')
    parser.add_argument('--scenario', type=str, default='normal',
                        choices=['normal', 'volatile', 'uptrend', 'downtrend'],
                        help='시장 시나리오')
    parser.add_argument('--fast', action='store_true', help='빠른 모드 (시간 압축)')
    parser.add_argument('--minutes', type=int, default=None,
                        help='실행할 분 수 (기본값: 전체 장 시간 약 390분)')

    args = parser.parse_args()

    simulator = TradingSimulator(
        test_date=args.date,
        scenario=args.scenario,
        fast_mode=args.fast,
        minutes=args.minutes
    )
    simulator.run()


if __name__ == "__main__":
    main()
