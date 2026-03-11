"""
AutoFIRE Trading Bot
한국투자증권 API를 활용한 자동 매매 봇

아키텍처:
- Selectors: 종목 선정 (일봉 기반)
- Policies: 매매 시그널 판단 (분봉 기반)
- 봇 엔진: 주문 실행 및 스케줄링
"""
import time
import schedule
import importlib
from datetime import datetime
from typing import List, Dict

# 환경 변수 설정
from config import config

# Core 모듈 import
from core.account import AccountAPI
from core.market_data import MarketDataAPI
from core.order import OrderAPI
from core.db_helper import DBHelper

# 알림 모듈
from notifications.discord import DiscordNotifier

# Base 클래스
from selectors.base import BaseSelector
from policies.base import BaseStrategy

class TradingBot:
    """
    자동 매매 봇 메인 클래스
    """

    def __init__(self):
        """봇 초기화"""
        # 환경 변수 검증
        try:
            config.validate()
        except ValueError as e:
            print(f"❌ {e}")
            raise

        # 현재 설정 출력
        config.print_config()

        # API 클라이언트 초기화
        self.account_api = AccountAPI(
            config.APP_KEY,
            config.APP_SECRET,
            config.ACCOUNT_NO,
            config.IS_PAPER_TRADING
        )
        self.market_api = MarketDataAPI(
            config.APP_KEY,
            config.APP_SECRET,
            config.ACCOUNT_NO,
            config.IS_PAPER_TRADING
        )
        self.order_api = OrderAPI(
            config.APP_KEY,
            config.APP_SECRET,
            config.ACCOUNT_NO,
            config.IS_PAPER_TRADING
        )

        # DB 헬퍼
        self.db = DBHelper()

        # Discord 알림
        self.notifier = DiscordNotifier()

        # 봇 상태
        self.selected_stocks: List[str] = []  # 금일 선정된 종목
        self.holdings: Dict = {}  # 현재 보유 종목 {종목코드: 보유정보}

        # Selectors 로드 (종목 선정 정책)
        self.selectors: List[BaseSelector] = self._load_selectors()

        # Policies 로드 (매매 전략)
        self.strategies: List[BaseStrategy] = self._load_strategies()

        print("✅ AutoFIRE Trading Bot 초기화 완료")
        print(f"📊 모드: {'모의투자' if config.IS_PAPER_TRADING else '실전투자'}")
        print(f"🎲 활성화된 Selectors: {len(self.selectors)}개")
        print(f"📈 활성화된 Strategies: {len(self.strategies)}개")

    def _load_selectors(self) -> List[BaseSelector]:
        """
        환경 변수에서 Selector 클래스들을 동적으로 로드

        자동 탐색 방식:
        1. selectors/ 폴더의 모든 .py 파일 스캔
        2. 환경 변수의 클래스명과 일치하는 클래스 찾기
        3. 인스턴스 생성

        Returns:
            로드된 Selector 인스턴스 리스트
        """
        selectors = []

        if not config.SELECTION_POLICIES:
            print("⚠️ SELECTION_POLICIES가 설정되지 않았습니다.")
            return selectors

        for policy_name in config.SELECTION_POLICIES:
            try:
                # selectors/ 폴더에서 클래스 찾기
                selector = self._find_and_load_class(
                    package='selectors',
                    class_name=policy_name,
                    base_class=BaseSelector
                )

                if selector:
                    selectors.append(selector)
                    print(f"  ✅ Selector 로드: {policy_name}")
                else:
                    print(f"  ⚠️ Selector 로드 실패: {policy_name} - 클래스를 찾을 수 없습니다.")

            except Exception as e:
                print(f"  ⚠️ Selector 로드 실패: {policy_name} - {str(e)}")

        return selectors

    def _load_strategies(self) -> List[BaseStrategy]:
        """
        환경 변수에서 Strategy 클래스들을 동적으로 로드

        자동 탐색 방식:
        1. policies/ 폴더의 모든 .py 파일 스캔
        2. 환경 변수의 클래스명과 일치하는 클래스 찾기
        3. 인스턴스 생성

        Returns:
            로드된 Strategy 인스턴스 리스트
        """
        strategies = []

        if not config.ACTIVE_STRATEGIES:
            print("⚠️ ACTIVE_STRATEGIES가 설정되지 않았습니다.")
            return strategies

        for strategy_name in config.ACTIVE_STRATEGIES:
            try:
                # policies/ 폴더에서 클래스 찾기
                strategy = self._find_and_load_class(
                    package='policies',
                    class_name=strategy_name,
                    base_class=BaseStrategy
                )

                if strategy:
                    strategies.append(strategy)
                    print(f"  ✅ Strategy 로드: {strategy_name}")
                else:
                    print(f"  ⚠️ Strategy 로드 실패: {strategy_name} - 클래스를 찾을 수 없습니다.")

            except Exception as e:
                print(f"  ⚠️ Strategy 로드 실패: {strategy_name} - {str(e)}")

        return strategies

    def _find_and_load_class(self, package: str, class_name: str, base_class):
        """
        패키지 폴더에서 클래스를 자동으로 찾아 로드

        Args:
            package: 패키지명 (예: 'selectors', 'policies')
            class_name: 찾을 클래스명
            base_class: 기본 클래스 (검증용)

        Returns:
            로드된 클래스 인스턴스 또는 None
        """
        import pkgutil

        # 패키지 경로 찾기
        package_module = importlib.import_module(package)
        package_path = package_module.__path__[0]

        # 패키지 내 모든 모듈 스캔
        for _, module_name, _ in pkgutil.iter_modules([package_path]):
            # __init__, base 등은 스킵
            if module_name in ['__init__', 'base']:
                continue

            try:
                # 모듈 로드
                full_module_name = f"{package}.{module_name}"
                module = importlib.import_module(full_module_name)

                # 클래스가 모듈에 있는지 확인
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)

                    # base_class를 상속했는지 확인
                    if isinstance(cls, type) and issubclass(cls, base_class) and cls != base_class:
                        return cls()

            except Exception:
                # 이 모듈에서 찾지 못하면 다음 모듈 시도
                continue

        return None

    def daily_stock_selection(self):
        """
        매일 장 시작 전 종목 선정

        Selectors를 사용하여 거래할 종목을 선정합니다.
        - 일봉 데이터 기반
        - 여러 Selector 결과를 통합
        """
        print("\n" + "="*50)
        print("📋 종목 선정 시작...")
        print("="*50)

        try:
            all_selected = []

            # 각 Selector로 종목 선정
            if not self.selectors:
                print("⚠️ 활성화된 Selector가 없습니다.")
                self.notifier.send_message("⚠️ Selector가 설정되지 않았습니다.")
                return

            for selector in self.selectors:
                print(f"\n🔍 {selector.name} 실행 중...")
                try:
                    selected = selector.select_stocks(select_count=config.SELECT_COUNT)
                    all_selected.extend(selected)
                    print(f"  ✅ {len(selected)}개 종목 선정")
                except Exception as e:
                    print(f"  ❌ 선정 실패: {str(e)}")

            # 중복 제거 및 최종 선정
            self.selected_stocks = list(set(all_selected))[:config.SELECT_COUNT]

            # DB에 선정 종목 저장
            if self.selected_stocks:
                self.db.save_selected_stocks(self.selected_stocks)

                # Discord 알림
                stocks_str = ", ".join(self.selected_stocks)
                self.notifier.send_message(
                    f"📋 금일 선정 종목 ({len(self.selected_stocks)}개)\n{stocks_str}"
                )
                print(f"\n✅ 최종 선정: {len(self.selected_stocks)}개 종목")
            else:
                print("⚠️ 선정된 종목이 없습니다.")
                self.notifier.send_message("⚠️ 금일 선정된 종목이 없습니다.")

        except Exception as e:
            error_msg = f"종목 선정 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            self.notifier.send_message(f"🚨 {error_msg}")

    def monitor_and_trade(self):
        """
        실시간 모니터링 및 매매 실행

        매매 규칙:
        1. 전략 시그널: 모든 Strategy의 시그널 체크 (ACTIVE_STRATEGIES 순서대로)
           - RiskManagement_Strategy: 익절/손절 체크
           - 기타 전략: 매매 시그널 생성
        2. 강제 청산: 15:20에 전량 시장가 매도
        3. Daily Stop: 당일 누적 손실 -3% 초과 시 신규 매수 중단

        주의: RiskManagement_Strategy를 ACTIVE_STRATEGIES의 첫 번째로 배치하여
              익절/손절이 다른 전략보다 우선 실행되도록 해야 합니다.
        """
        try:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M:%S")
            print(f"\n⏰ [{current_time_str}] 모니터링 시작...")

            if not self.strategies:
                print("⚠️ 활성화된 Strategy가 없습니다.")
                return

            # Daily Stop 체크 (당일 누적 손실 -3% 초과 시 매수 중단)
            balance = self.account_api.get_balance()
            daily_profit_rate = balance.get('profit_rate', 0)

            if daily_profit_rate <= config.DAILY_STOP_LOSS:
                print(f"🚨 Daily Stop 발동! 당일 손실: {daily_profit_rate:.2f}%")
                print("  ⛔ 신규 매수 중단")
                self.notifier.send_message(
                    f"🚨 Daily Stop 발동!\n당일 손실: {daily_profit_rate:.2f}%\n신규 매수 중단"
                )
                # 매도만 수행 (매수는 스킵)
                can_buy = False
            else:
                can_buy = True

            # 보유 종목 조회
            self.holdings = {
                h['stock_code']: h
                for h in balance.get('holdings', [])
            }

            print(f"💼 현재 보유 종목: {len(self.holdings)}개")
            print(f"📊 선정 종목: {len(self.selected_stocks)}개")
            print(f"💰 당일 손익률: {daily_profit_rate:+.2f}%")

            # 강제 청산 체크 (config.MARKET_CLOSE_TIME)
            force_liquidation_time = datetime.strptime(config.MARKET_CLOSE_TIME, "%H:%M").time()
            if current_time.time() >= force_liquidation_time:
                print(f"🔴 {config.MARKET_CLOSE_TIME} 강제 청산 시간!")
                self._force_liquidation()
                return

            # 1. 보유 종목 매도 시그널 체크 (익절/손절/전략 시그널)
            for stock_code, holding in self.holdings.items():
                self._check_sell_conditions(stock_code, holding)

            # 2. 선정 종목 매수 시그널 체크 (Daily Stop 미발동 시에만)
            if can_buy:
                for stock_code in self.selected_stocks:
                    if stock_code not in self.holdings:  # 미보유 종목만
                        self._check_buy_signal(stock_code)

        except Exception as e:
            print(f"❌ 모니터링 중 오류: {str(e)}")

    def _check_buy_signal(self, stock_code: str):
        """
        매수 시그널 체크

        Args:
            stock_code: 종목 코드
        """
        try:
            # 현재 시세 조회
            current_data = self.market_api.get_current_price(stock_code)
            if not current_data:
                return

            # 분봉 데이터 조회 (최근 100개)
            historical_data = self.market_api.get_minute_price(stock_code, count=100)

            # 각 전략으로 시그널 체크
            for strategy in self.strategies:
                signal = strategy.check_signal(stock_code, current_data, historical_data)

                if signal == 'BUY':
                    print(f"  🟢 [{strategy.name}] {stock_code} 매수 시그널!")
                    # TODO: 실제 매수 주문 실행
                    # self._execute_buy_order(stock_code, current_data)
                    break  # 하나의 전략에서라도 매수 시그널이 나오면 실행

        except Exception as e:
            print(f"  ⚠️ {stock_code} 매수 시그널 체크 실패: {str(e)}")

    def _check_sell_conditions(self, stock_code: str, holding: Dict):
        """
        매도 조건 체크 (전략 기반)

        모든 전략(RiskManagement 포함)의 시그널을 체크합니다.
        RiskManagement_Strategy가 ACTIVE_STRATEGIES의 첫 번째에 있어야
        익절/손절 우선순위가 보장됩니다.

        Args:
            stock_code: 종목 코드
            holding: 보유 정보 {'avg_buy_price': float, 'profit_rate': float, ...}
        """
        try:
            # 현재 시세 조회
            current_data = self.market_api.get_current_price(stock_code)
            if not current_data:
                return

            profit_rate = holding.get('profit_rate', 0)

            # 분봉 데이터 조회 (전략이 필요로 할 경우를 위해)
            historical_data = self.market_api.get_minute_price(stock_code, count=100)

            # 모든 전략 시그널 체크 (순서대로 실행)
            for strategy in self.strategies:
                # RiskManagement_Strategy는 holding_info를 필요로 함
                signal = strategy.check_signal(
                    stock_code,
                    current_data,
                    historical_data,
                    holding_info=holding  # RiskManagement를 위한 보유 정보 전달
                )

                if signal == 'SELL':
                    # 매도 사유 판별
                    if strategy.name == "RiskManagement_Strategy":
                        # RiskManagement의 get_sell_reason 메서드 사용
                        if hasattr(strategy, 'get_sell_reason'):
                            reason = strategy.get_sell_reason(profit_rate)
                            icon = "💰" if profit_rate > 0 else "🔻"
                            print(f"  {icon} [{stock_code}] {reason}")
                            self.notifier.send_message(
                                f"{icon} 리스크 관리 매도\n종목: {stock_code}\n{reason}"
                            )
                        else:
                            print(f"  🔴 [{stock_code}] 리스크 관리 매도! {profit_rate:+.2f}%")
                            self.notifier.send_message(
                                f"🔴 리스크 관리 매도\n종목: {stock_code}\n수익률: {profit_rate:+.2f}%"
                            )
                    else:
                        # 다른 전략의 시그널
                        print(f"  🔴 [{strategy.name}] {stock_code} 매도 시그널!")
                        self.notifier.send_message(
                            f"🔴 전략 매도\n종목: {stock_code}\n전략: {strategy.name}"
                        )

                    # TODO: 지정가 매도 주문 실행
                    # self._execute_sell_order(stock_code, current_price, reason=strategy.name)
                    break  # 첫 번째 SELL 시그널에서 매도 실행 후 종료

        except Exception as e:
            print(f"  ⚠️ {stock_code} 매도 조건 체크 실패: {str(e)}")

    def _force_liquidation(self):
        """
        강제 청산 (전량 시장가 매도)
        .env의 MARKET_CLOSE_TIME에 실행

        오버나잇 방지를 위해 모든 보유 종목을 시장가로 매도
        """
        print("\n" + "="*50)
        print(f"🔴 강제 청산 시작 ({config.MARKET_CLOSE_TIME})")
        print("="*50)

        if not self.holdings:
            print("  보유 종목 없음")
            return

        for stock_code in self.holdings.keys():
            try:
                print(f"  🔴 [{stock_code}] 시장가 강제 매도")
                # TODO: 시장가 매도 주문 실행
                # self._execute_market_sell(stock_code, reason='강제청산')

            except Exception as e:
                print(f"  ❌ [{stock_code}] 강제 청산 실패: {str(e)}")

        self.notifier.send_message(
            f"🔴 강제 청산 완료\n매도 종목 수: {len(self.holdings)}개"
        )
        print("="*50)

    def daily_report(self, is_startup: bool = False):
        """
        계좌 상태 리포트 생성

        Args:
            is_startup: True이면 봇 시작 시 리포트, False이면 정기 일일 리포트

        - 계좌 정보 조회
        - 수익률 계산
        - Discord로 리포트 전송
        - DB에 스냅샷 저장 (정기 리포트만)
        """
        report_type = "초기 계좌 상태" if is_startup else "일일 매매 리포트"
        print("\n" + "="*50)
        print(f"📊 {report_type} 생성 중...")
        print("="*50)

        try:
            # 계좌 정보 조회
            balance = self.account_api.get_balance()

            # 계좌 스냅샷 DB 저장 (정기 리포트만)
            if not is_startup:
                snapshot = {
                    'total_assets': balance.get('total_assets', 0),
                    'cash_balance': balance.get('cash_balance', 0),
                    'stock_value': balance.get('stock_value', 0),
                    'profit_loss': balance.get('profit_loss', 0),
                    'profit_rate': balance.get('profit_rate', 0)
                }
                self.db.save_account_snapshot(snapshot)

            # Discord 리포트 전송
            title = "📊 **초기 계좌 상태**" if is_startup else "📊 **일일 매매 리포트**"
            report = f"""
{title}

💰 총 자산: {balance.get('total_assets', 0):,}원
💵 예수금: {balance.get('cash_balance', 0):,}원
📈 평가금액: {balance.get('stock_value', 0):,}원
{'🔴' if balance.get('profit_loss', 0) < 0 else '🔵'} 평가손익: {balance.get('profit_loss', 0):,}원 ({balance.get('profit_rate', 0):.2f}%)

📦 보유 종목: {len(balance.get('holdings', []))}개
            """
            self.notifier.send_message(report.strip())

            print(f"✅ {report_type} 생성 완료")

        except Exception as e:
            error_msg = f"리포트 생성 중 오류: {str(e)}"
            print(f"❌ {error_msg}")
            self.notifier.send_message(f"🚨 {error_msg}")

    def setup_schedule(self):
        """
        스케줄러 설정 (.env 기반)

        - SELECTION_TIME: 종목 선정
        - MARKET_OPEN_TIME ~ MARKET_CLOSE_TIME: MONITOR_INTERVAL 분마다 모니터링
        - REPORT_TIME: 일일 리포트
        """
        # 종목 선정 (장 시작 전)
        schedule.every().day.at(config.SELECTION_TIME).do(self.daily_stock_selection)

        # 일일 리포트 (장 마감 후)
        schedule.every().day.at(config.REPORT_TIME).do(self.daily_report)

        # 장 시간 중 모니터링 (config.MONITOR_INTERVAL 분마다)
        schedule.every(config.MONITOR_INTERVAL).minutes.do(self._scheduled_monitor_and_trade)

        print("⏰ 스케줄러 설정 완료")
        print(f"  - {config.SELECTION_TIME}: 종목 선정")
        print(f"  - {config.MARKET_OPEN_TIME}~{config.MARKET_CLOSE_TIME}: {config.MONITOR_INTERVAL}분마다 모니터링")
        print(f"  - {config.REPORT_TIME}: 일일 리포트")

    def _scheduled_monitor_and_trade(self):
        """
        스케줄러용 모니터링 래퍼
        .env의 MARKET_OPEN_TIME ~ MARKET_CLOSE_TIME에만 실행
        """
        now = datetime.now()
        current_time = now.time()

        # 장 시작/마감 시간 (config에서 가져오기)
        market_open = datetime.strptime(config.MARKET_OPEN_TIME, "%H:%M").time()
        market_close = datetime.strptime(config.MARKET_CLOSE_TIME, "%H:%M").time()

        # 장 시간 체크
        if market_open <= current_time <= market_close:
            # 평일만 (월~금)
            if now.weekday() < 5:
                self.monitor_and_trade()
        else:
            # 장 시간 외에는 스킵
            pass

    def run(self):
        """봇 실행"""
        print("\n" + "="*50)
        print("🚀 AutoFIRE Trading Bot 시작")
        print("="*50)

        # Discord 상세 시작 알림 (.env 기반 동적 생성)
        selectors_str = ', '.join(config.SELECTION_POLICIES) if config.SELECTION_POLICIES else '없음'
        strategies_str = ', '.join(config.ACTIVE_STRATEGIES) if config.ACTIVE_STRATEGIES else '없음'

        startup_message = f"""🚀 **AutoFIRE Trading Bot 시작**

📊 **모드**: {'모의투자' if config.IS_PAPER_TRADING else '실전투자'}

🎲 **종목 선택 전략** ({len(self.selectors)}개)
{selectors_str}

📈 **매매 전략** ({len(self.strategies)}개)
{strategies_str}

⏰ **스케줄**
• {config.SELECTION_TIME}: 종목 선정
• {config.MARKET_OPEN_TIME}~{config.MARKET_CLOSE_TIME}: {config.MONITOR_INTERVAL}분마다 모니터링
• {config.REPORT_TIME}: 일일 리포트

💰 **매매 설정**
• 최대 매수금액: {config.MAX_BUY_AMOUNT:,}원
• 익절: +{config.TAKE_PROFIT}%
• 손절: {config.STOP_LOSS}%
• Daily Stop: {config.DAILY_STOP_LOSS}%
• 선정 종목 수: {config.SELECT_COUNT}개
"""
        self.notifier.send_message(startup_message.strip())

        # 현재 계좌 상태 리포트 전송 (시작 시)
        self.daily_report(is_startup=True)

        # 스케줄러 설정
        self.setup_schedule()

        try:
            # 메인 루프
            while True:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n👋 사용자에 의해 봇 중지")
            self.notifier.send_message("👋 AutoFIRE Bot 종료")
        except Exception as e:
            error_msg = f"시스템 에러: {str(e)}"
            print(f"\n❌ {error_msg}")
            self.notifier.send_message(f"🚨 {error_msg}")


def main():
    """메인 함수"""
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()
