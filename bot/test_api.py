"""
한국투자증권 API 테스트 스크립트
조회 기능만 테스트합니다.
"""
import os
from dotenv import load_dotenv
from core.auth import KISAuth
from core.market_data import MarketDataAPI
from core.account import AccountAPI

# 환경 변수 로드
load_dotenv()

def test_api():
    """
    API 조회 기능 테스트
    """
    print("=" * 60)
    print("한국투자증권 API 테스트")
    print("=" * 60)

    # 환경 변수
    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    account_no = os.getenv("ACCOUNT_NO")
    is_virtual = os.getenv("IS_VIRTUAL", "true").lower() == "true"

    if not all([app_key, app_secret, account_no]):
        print("❌ 환경 변수 설정이 필요합니다:")
        print("   APP_KEY, APP_SECRET, ACCOUNT_NO")
        return

    mode = "모의투자" if is_virtual else "실전투자"
    print(f"\n✓ 환경 변수 로드 완료")
    print(f"  - 계좌번호: {account_no}")
    print(f"  - 모드: {mode}")

    # 1. 인증 테스트
    print("\n[1/4] 인증 테스트...")
    try:
        auth = KISAuth(app_key, app_secret, is_virtual=is_virtual)
        token = auth.get_token()
        print(f"  ✓ 토큰 발급 성공")
        print(f"    Token: {token[:20]}...")
    except Exception as e:
        print(f"  ❌ 인증 실패: {str(e)}")
        return

    # 2. 시세 조회 테스트
    print("\n[2/4] 시세 조회 테스트...")
    try:
        market_api = MarketDataAPI(app_key, app_secret, account_no, is_virtual=is_virtual)
        market_api.access_token = token

        # 삼성전자 현재가 조회
        price_info = market_api.get_current_price("005930")
        if price_info:
            print(f"  ✓ 삼성전자 현재가 조회 성공")
            print(f"    현재가: {price_info['current_price']:,}원")
            print(f"    등락률: {price_info['change_rate']}%")
            print(f"    거래량: {price_info['volume']:,}주")
        else:
            print(f"  ⚠️  시세 조회 실패 (API 키 확인 필요)")

    except Exception as e:
        print(f"  ❌ 시세 조회 실패: {str(e)}")

    # 3. 일봉 데이터 조회
    print("\n[3/4] 일봉 데이터 조회 테스트...")
    try:
        daily_data = market_api.get_daily_price("005930", period="D")
        if daily_data:
            print(f"  ✓ 일봉 데이터 조회 성공 ({len(daily_data)}일)")
            print(f"    최근 종가: {daily_data[0]['close']:,}원")
        else:
            print(f"  ⚠️  일봉 조회 실패")
    except Exception as e:
        print(f"  ❌ 일봉 조회 실패: {str(e)}")

    # 4. 계좌 조회 테스트
    print("\n[4/4] 계좌 조회 테스트...")
    try:
        account_api = AccountAPI(app_key, app_secret, account_no, is_virtual=is_virtual)
        account_api.access_token = token

        balance = account_api.get_balance()
        if balance:
            print(f"  ✓ 계좌 조회 성공")
            print(f"    총 자산: {balance.get('total_assets', 0):,}원")
            print(f"    예수금: {balance.get('cash_balance', 0):,}원")
            print(f"    보유 종목: {len(balance.get('holdings', []))}개")

            if balance.get('holdings'):
                print(f"\n  [보유 종목]")
                for holding in balance['holdings'][:3]:  # 상위 3개만
                    print(f"    - {holding['stock_name']}: {holding['quantity']}주 ({holding['profit_rate']:+.2f}%)")
        else:
            print(f"  ⚠️  계좌 조회 실패 (계좌번호 확인 필요)")

    except Exception as e:
        print(f"  ❌ 계좌 조회 실패: {str(e)}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    test_api()
