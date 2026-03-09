"""
한국투자증권 API 테스트 스크립트 (Discord 알림 연동)
조회 기능 및 주문 API를 테스트하며 결과를 Discord로 전송합니다.

주의: 실제 주문 테스트는 매우 신중하게 수행해야 합니다.
     기본적으로 모의투자 모드에서만 테스트합니다.
"""
from config import config
from core.auth import KISAuth
from core.market_data import MarketDataAPI
from core.account import AccountAPI
from core.order import OrderAPI
from notifications.discord import DiscordNotifier

def test_api():
    """
    API 조회 기능 테스트 및 Discord 전송
    """
    notifier = DiscordNotifier()
    report = [] # 메시지 요약을 위한 리스트

    print("=" * 60)
    print("한국투자증권 API 테스트 시작")
    print("=" * 60)
    notifier.send_message("🔍 **한국투자증권 API 연결 테스트를 시작합니다.**")

    # 환경 변수 검증
    try:
        config.validate()
    except ValueError as e:
        error_msg = f"❌ {e}"
        print(error_msg)
        notifier.send_message(error_msg)
        return

    # config에서 값 가져오기
    app_key = config.APP_KEY
    app_secret = config.APP_SECRET
    account_no = config.ACCOUNT_NO
    is_virtual = config.IS_PAPER_TRADING

    mode = "모의투자" if is_virtual else "실전투자"
    setup_info = f"✓ 환경 변수 로드 완료\n- 계좌번호: {account_no}\n- 모드: {mode}"
    print(setup_info)

    # 1. 인증 테스트
    print("\n[1/4] 인증 테스트...")
    try:
        auth = KISAuth(app_key, app_secret, is_virtual=is_virtual)
        token = auth.get_token()
        auth_res = "✅ [인증] 토큰 발급 성공"
        print(auth_res)
        notifier.send_message(auth_res)
    except Exception as e:
        auth_err = f"❌ [인증] 실패: {str(e)}"
        print(auth_err)
        notifier.send_message(auth_err)
        return

    # 2. 시세 조회 테스트
    print("\n[2/4] 시세 조회 테스트...")
    try:
        market_api = MarketDataAPI(app_key, app_secret, account_no, is_virtual=is_virtual)
        market_api.access_token = token

        # 삼성전자 현재가 조회
        price_info = market_api.get_current_price("005930")
        if price_info:
            res = (f"✅ [시세] 삼성전자(005930) 조회 성공\n"
                   f"- 현재가: {price_info['current_price']:,}원\n"
                   f"- 등락률: {price_info['change_rate']}%\n"
                   f"- 거래량: {price_info['volume']:,}주")
            print(res)
            notifier.send_message(res)
        else:
            notifier.send_message("⚠️ [시세] 삼성전자 조회 결과가 없습니다.")

    except Exception as e:
        print(f"  ❌ 시세 조회 실패: {str(e)}")
        notifier.send_message(f"❌ [시세] 조회 에러: {str(e)}")

    # 3. 일봉 데이터 조회
    print("\n[3/4] 일봉 데이터 조회 테스트...")
    try:
        daily_data = market_api.get_daily_price("005930", period="D")
        if daily_data:
            res = f"✅ [차트] 일봉 데이터 조회 성공 ({len(daily_data)}일 데이터 수신)"
            print(res)
            notifier.send_message(res)
        else:
            notifier.send_message("⚠️ [차트] 일봉 조회 결과가 없습니다.")
    except Exception as e:
        notifier.send_message(f"❌ [차트] 데이터 에러: {str(e)}")

    # 4. 계좌 조회 테스트
    print("\n[4/4] 계좌 조회 테스트...")
    try:
        account_api = AccountAPI(app_key, app_secret, account_no, is_virtual=is_virtual)
        account_api.access_token = token

        balance = account_api.get_balance()
        if balance:
            acc_res = [
                "✅ [계좌] 잔고 조회 성공",
                f"- 총 자산: {balance.get('total_assets', 0):,}원",
                f"- 예수금: {balance.get('cash_balance', 0):,}원",
                f"- 보유 종목: {len(balance.get('holdings', []))}개"
            ]
            
            if balance.get('holdings'):
                acc_res.append("\n[보유 종목 상위]")
                for holding in balance['holdings'][:3]:
                    acc_res.append(f"• {holding['stock_name']}: {holding['quantity']}주 ({holding['profit_rate']:+.2f}%)")
            
            msg = "\n".join(acc_res)
            print(msg)
            notifier.send_message(msg)
        else:
            notifier.send_message("⚠️ [계좌] 잔고 조회 결과가 없습니다.")

    except Exception as e:
        notifier.send_message(f"❌ [계좌] 조회 에러: {str(e)}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)
    notifier.send_message("🏁 **모든 API 테스트가 완료되었습니다.**")


def test_order_api(test_real_order: bool = False):
    """
    주문 API 테스트 (매수/매도)

    Args:
        test_real_order: 실제 주문 실행 여부 (기본값: False, 모의 주문만)

    주의: 실제 주문은 매우 위험합니다. 모의투자 모드에서만 테스트하세요!
    """
    notifier = DiscordNotifier()

    print("=" * 60)
    print("한국투자증권 주문 API 테스트 시작")
    print("=" * 60)

    # 환경 변수 검증
    try:
        config.validate()
    except ValueError as e:
        error_msg = f"❌ {e}"
        print(error_msg)
        notifier.send_message(error_msg)
        return

    # config에서 값 가져오기
    app_key = config.APP_KEY
    app_secret = config.APP_SECRET
    account_no = config.ACCOUNT_NO
    is_virtual = config.IS_PAPER_TRADING

    # 실전투자 모드에서 실제 주문 방지
    if not is_virtual and test_real_order:
        warning = "⚠️ 경고: 실전투자 모드에서는 주문 테스트를 수행하지 않습니다!"
        print(warning)
        notifier.send_message(warning)
        return

    mode = "모의투자" if is_virtual else "실전투자"
    print(f"✓ 모드: {mode}")
    notifier.send_message(f"🔧 **주문 API 테스트 시작** (모드: {mode})")

    try:
        # OrderAPI 초기화
        order_api = OrderAPI(app_key, app_secret, account_no, is_virtual=is_virtual)

        print("\n[주문 API 초기화 완료]")
        notifier.send_message("✅ 주문 API 초기화 완료")

        if not test_real_order:
            info_msg = "ℹ️ 실제 주문은 실행하지 않습니다. test_real_order=True로 설정하면 모의투자에서 실제 주문을 테스트할 수 있습니다."
            print(info_msg)
            notifier.send_message(info_msg)
            return

        # 실제 주문 테스트 (모의투자에서만)
        if is_virtual:
            print("\n[1] 시장가 매수 테스트...")
            # 소액으로 테스트 (삼성전자 1주)
            buy_result = order_api.buy_market_order("005930", 1)

            if buy_result.get("success"):
                msg = f"✅ 매수 주문 성공\n- 주문번호: {buy_result.get('order_no')}\n- 종목: {buy_result.get('stock_code')}\n- 수량: {buy_result.get('quantity')}주"
                print(msg)
                notifier.send_message(msg)

                # 주문 상태 조회
                print("\n[2] 주문 상태 조회...")
                order_no = buy_result.get('order_no')
                status = order_api.get_order_status(order_no)

                status_msg = f"📊 주문 상태\n- 주문번호: {order_no}\n- 체결수량: {status.get('executed_quantity', 0)}주\n- 체결가: {status.get('executed_price', 0):,}원"
                print(status_msg)
                notifier.send_message(status_msg)
            else:
                error = f"❌ 매수 주문 실패: {buy_result.get('error', '알 수 없는 오류')}"
                print(error)
                notifier.send_message(error)

        print("\n" + "=" * 60)
        print("주문 API 테스트 완료")
        print("=" * 60)
        notifier.send_message("🏁 **주문 API 테스트 완료**")

    except Exception as e:
        error = f"❌ 주문 API 테스트 중 오류 발생: {str(e)}"
        print(error)
        notifier.send_message(error)


if __name__ == "__main__":
    # 기본 조회 API 테스트
    test_api()

    # 주문 API 테스트를 원하면 주석 해제 (모의투자에서만!)
    test_order_api(test_real_order=False)  # False: 초기화만, True: 실제 주문 테스트