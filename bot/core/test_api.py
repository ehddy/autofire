"""
한국투자증권 API 종합 테스트 스크립트

실전/모의 환경에서 모든 조회 API를 테스트합니다.
주의: 실전 환경에서는 조회만 수행하며, 실제 주문은 실행하지 않습니다.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env 파일 로드
env_path = project_root / '.env'
load_dotenv(env_path)

from core.market_data import MarketDataAPI
from core.account import AccountAPI
from core.order import OrderAPI


class KISAPITester:
    """KIS API 테스터"""

    def __init__(self, is_virtual: bool = True):
        """
        Args:
            is_virtual: True면 모의투자, False면 실전투자
        """
        self.is_virtual = is_virtual
        self.mode_name = "모의투자" if is_virtual else "실전투자"

        # 환경 변수 로드
        self.app_key = os.getenv("APP_KEY")
        self.app_secret = os.getenv("APP_SECRET")
        self.account_no = os.getenv("ACCOUNT_NO")

        if not all([self.app_key, self.app_secret, self.account_no]):
            raise ValueError("환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")

        # API 초기화
        print(f"\n{'='*60}")
        print(f"🚀 한국투자증권 API 테스트 시작 ({self.mode_name})")
        print(f"{'='*60}\n")

        self.market_api = MarketDataAPI(
            self.app_key, self.app_secret, self.account_no, is_virtual
        )
        self.account_api = AccountAPI(
            self.app_key, self.app_secret, self.account_no, is_virtual
        )
        self.order_api = OrderAPI(
            self.app_key, self.app_secret, self.account_no, is_virtual
        )

    def test_market_data_apis(self):
        """시세 조회 API 테스트"""
        print(f"\n{'='*60}")
        print("📊 [1] 시세 조회 API 테스트")
        print(f"{'='*60}\n")

        test_stock = "005930"  # 삼성전자

        # 1-1. 현재가 조회
        print(f"[1-1] 현재가 조회 ({test_stock})")
        current_price = self.market_api.get_current_price(test_stock)
        if current_price:
            print(f"  ✅ 성공")
            print(f"     종목코드: {current_price['stock_code']}")
            print(f"     현재가: {current_price['current_price']:,}원")
            print(f"     등락률: {current_price['change_rate']}%")
            print(f"     거래량: {current_price['volume']:,}")
        else:
            print(f"  ❌ 실패")

        # 1-2. 일봉 조회
        print(f"\n[1-2] 일봉 데이터 조회 ({test_stock})")
        daily_data = self.market_api.get_daily_price(test_stock, period="D")
        if daily_data:
            print(f"  ✅ 성공 (최근 {len(daily_data)}일 데이터)")
            print(f"     최근일: {daily_data[0]['date']}")
            print(f"     종가: {daily_data[0]['close']:,}원")
            print(f"     거래량: {daily_data[0]['volume']:,}")
        else:
            print(f"  ❌ 실패")

        # 1-3. 분봉 조회
        print(f"\n[1-3] 분봉 데이터 조회 ({test_stock}, 1분봉)")
        minute_data = self.market_api.get_minute_price(test_stock, time_unit="1")
        if minute_data:
            print(f"  ✅ 성공 (최근 {len(minute_data)}개 데이터)")
            if minute_data:
                print(f"     최근시간: {minute_data[0]['datetime']}")
                print(f"     가격: {minute_data[0]['price']:,}원")
        else:
            print(f"  ❌ 실패")

        # 1-4. 호가 조회
        print(f"\n[1-4] 호가 정보 조회 ({test_stock})")
        orderbook = self.market_api.get_orderbook(test_stock)
        if orderbook:
            print(f"  ✅ 성공")
            print(f"     현재가: {orderbook['current_price']:,}원")
            print(f"     최우선 매도호가: {orderbook['best_ask_price']:,}원")
            print(f"     최우선 매수호가: {orderbook['best_bid_price']:,}원")
            print(f"     총 매도잔량: {orderbook['total_ask_quantity']:,}주")
            print(f"     총 매수잔량: {orderbook['total_bid_quantity']:,}주")
        else:
            print(f"  ❌ 실패")

        # 1-5. 거래량 순위
        print(f"\n[1-5] 거래량 순위 조회 (코스피 상위 10개)")
        volume_rank = self.market_api.get_volume_rank(market="1")  # 1: 코스피
        if volume_rank:
            print(f"  ✅ 성공 ({len(volume_rank)}개)")
            for i, item in enumerate(volume_rank[:10], 1):
                print(f"     {i}. {item['stock_name']}({item['stock_code']}) - "
                      f"거래량: {item['volume']:,}, "
                      f"등락률: {item['change_rate']:+.2f}%")
        else:
            print(f"  ❌ 실패")

        # 1-6. 거래대금 순위
        print(f"\n[1-6] 거래대금 순위 조회 (전체 상위 10개)")
        amount_rank = self.market_api.get_trade_amount_rank(market="0")  # 0: 전체
        if amount_rank:
            print(f"  ✅ 성공 ({len(amount_rank)}개)")
            for i, item in enumerate(amount_rank[:10], 1):
                print(f"     {i}. {item['stock_name']}({item['stock_code']}) - "
                      f"거래대금: {item['trade_amount']:,}원")
        else:
            print(f"  ❌ 실패")

        # 1-7. 상승률 순위
        print(f"\n[1-7] 상승률 순위 조회 (코스닥 상위 10개)")
        rise_rank = self.market_api.get_fluctuation_rank(market="2", sort="1")  # 2: 코스닥, 1: 상승률
        if rise_rank:
            print(f"  ✅ 성공 ({len(rise_rank)}개)")
            for i, item in enumerate(rise_rank[:10], 1):
                print(f"     {i}. {item['stock_name']}({item['stock_code']}) - "
                      f"상승률: {item['change_rate']:+.2f}%")
        else:
            print(f"  ❌ 실패")

    def test_account_apis(self):
        """계좌 조회 API 테스트"""
        print(f"\n{'='*60}")
        print("💰 [2] 계좌 조회 API 테스트")
        print(f"{'='*60}\n")

        # 2-1. 계좌 잔고 조회
        print(f"[2-1] 계좌 잔고 조회")
        balance = self.account_api.get_balance()
        if balance:
            print(f"  ✅ 성공")
            print(f"     총 자산: {balance['total_assets']:,}원")
            print(f"     예수금: {balance['cash_balance']:,}원")
            print(f"     주식 평가금액: {balance['stock_value']:,}원")
            print(f"     평가손익: {balance['profit_loss']:,}원 ({balance['profit_rate']:+.2f}%)")
            print(f"     보유 종목 수: {len(balance.get('holdings', []))}개")

            if balance.get('holdings'):
                print(f"\n     [보유 종목]")
                for h in balance['holdings']:
                    print(f"       • {h['stock_name']}({h['stock_code']})")
                    print(f"         수량: {h['quantity']}주, 평단가: {h['avg_price']:,.0f}원")
                    print(f"         현재가: {h['current_price']:,}원, "
                          f"수익률: {h['profit_rate']:+.2f}%")
        else:
            print(f"  ❌ 실패")

        # 2-2. 매수 가능 금액 조회
        print(f"\n[2-2] 매수 가능 금액 조회")
        available_cash = self.account_api.get_buy_available_cash()
        if available_cash > 0:
            print(f"  ✅ 성공")
            print(f"     매수 가능 금액: {available_cash:,}원")
        else:
            print(f"  ❌ 실패 또는 잔액 없음")

        # 2-3. 당일 주문 내역 조회
        print(f"\n[2-3] 당일 주문 내역 조회")
        orders = self.account_api.get_order_history()
        if orders is not None:
            print(f"  ✅ 성공 (총 {len(orders)}건)")
            if orders:
                for order in orders[:5]:  # 최근 5건만 출력
                    print(f"     • [{order['order_type']}] {order['stock_name']}({order['stock_code']})")
                    print(f"       주문: {order['order_quantity']}주 @ {order['order_price']:,}원")
                    print(f"       체결: {order['executed_quantity']}주 @ {order['executed_price']:,}원")
            else:
                print(f"     (당일 주문 내역 없음)")
        else:
            print(f"  ❌ 실패")

        # 2-4. 당일 손익 조회
        print(f"\n[2-4] 당일 손익 조회")
        daily_pl = self.account_api.get_daily_profit_loss()
        if daily_pl:
            print(f"  ✅ 성공")
            print(f"     매수 금액: {daily_pl['total_buy_amount']:,}원 ({daily_pl['buy_count']}건)")
            print(f"     매도 금액: {daily_pl['total_sell_amount']:,}원 ({daily_pl['sell_count']}건)")
            print(f"     당일 손익: {daily_pl['profit_loss']:,}원")
        else:
            print(f"  ❌ 실패")

        # 2-5. 미체결 주문 조회
        print(f"\n[2-5] 미체결 주문 조회")
        pending = self.account_api.get_pending_orders()
        if pending is not None:
            print(f"  ✅ 성공 (총 {len(pending)}건)")
            if pending:
                for order in pending:
                    print(f"     • [{order['order_type']}] {order['stock_name']}({order['stock_code']})")
                    print(f"       주문: {order['order_quantity']}주 @ {order['order_price']:,}원")
                    print(f"       미체결: {order['pending_quantity']}주")
            else:
                print(f"     (미체결 주문 없음)")
        else:
            print(f"  ❌ 실패")

    def test_order_apis_info_only(self):
        """주문 API 정보 출력 (실제 주문 실행하지 않음)"""
        print(f"\n{'='*60}")
        print("📝 [3] 주문 API 정보")
        print(f"{'='*60}\n")

        print("[3-1] 사용 가능한 주문 메서드")
        print("  • buy_market_order(stock_code, quantity)")
        print("    - 시장가 매수 주문")
        print()
        print("  • buy_limit_order(stock_code, quantity, price)")
        print("    - 지정가 매수 주문")
        print()
        print("  • sell_market_order(stock_code, quantity)")
        print("    - 시장가 매도 주문")
        print()
        print("  • sell_limit_order(stock_code, quantity, price)")
        print("    - 지정가 매도 주문")
        print()
        print("  • cancel_order(order_no, stock_code, quantity)")
        print("    - 주문 취소")
        print()
        print("  • modify_order(order_no, stock_code, quantity, price)")
        print("    - 주문 정정")
        print()
        print("  • get_order_status(order_no)")
        print("    - 주문 체결 조회")
        print()
        print("⚠️  주의: 실제 주문은 신중하게 테스트하세요!")
        print(f"    현재 모드: {self.mode_name}")

    def run_all_tests(self):
        """모든 테스트 실행"""
        try:
            # 1. 시세 조회 API 테스트
            self.test_market_data_apis()

            # 2. 계좌 조회 API 테스트
            self.test_account_apis()

            # 3. 주문 API 정보 출력 (실제 주문 실행 안 함)
            self.test_order_apis_info_only()

            # 결과 요약
            print(f"\n{'='*60}")
            print(f"✅ 모든 테스트 완료 ({self.mode_name})")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """메인 함수"""
    print("\n한국투자증권 API 테스트 프로그램")
    print("="*60)
    print("1. 모의투자 환경 테스트")
    print("2. 실전투자 환경 테스트")
    print("3. 둘 다 테스트")
    print("="*60)

    choice = input("\n선택하세요 (1/2/3): ").strip()

    if choice == "1":
        # 모의투자만
        tester = KISAPITester(is_virtual=True)
        tester.run_all_tests()

    elif choice == "2":
        # 실전투자만
        confirm = input("\n⚠️  실전투자 환경에서 테스트합니다. 계속하시겠습니까? (yes/no): ").strip().lower()
        if confirm == "yes":
            tester = KISAPITester(is_virtual=False)
            tester.run_all_tests()
        else:
            print("테스트를 취소했습니다.")

    elif choice == "3":
        # 둘 다 테스트
        print("\n먼저 모의투자 환경을 테스트합니다.")
        input("Enter를 눌러 계속...")
        tester_virtual = KISAPITester(is_virtual=True)
        tester_virtual.run_all_tests()

        print("\n\n다음으로 실전투자 환경을 테스트합니다.")
        confirm = input("⚠️  실전투자 환경에서 테스트합니다. 계속하시겠습니까? (yes/no): ").strip().lower()
        if confirm == "yes":
            tester_real = KISAPITester(is_virtual=False)
            tester_real.run_all_tests()
        else:
            print("실전투자 테스트를 건너뛰었습니다.")

    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
