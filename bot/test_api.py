"""
한국투자증권 API 테스트 스크립트 (Discord 알림 연동)
조회 기능만 테스트하며 결과를 Discord로 전송합니다.
"""
import os
from dotenv import load_dotenv
from core.auth import KISAuth
from core.market_data import MarketDataAPI
from core.account import AccountAPI
from notifications.discord import DiscordNotifier # Discord 알림 모듈 추가

# 환경 변수 로드
load_dotenv()

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

    # 환경 변수 확인
    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    account_no = os.getenv("ACCOUNT_NO")
    is_virtual = os.getenv("IS_VIRTUAL", "true").lower() == "true"

    if not all([app_key, app_secret, account_no]):
        error_msg = "❌ 환경 변수 설정이 누락되었습니다 (APP_KEY, APP_SECRET, ACCOUNT_NO)"
        print(error_msg)
        notifier.send_message(error_msg)
        return

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


if __name__ == "__main__":
    test_api()