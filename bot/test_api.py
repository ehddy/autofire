"""
한국투자증권 API 종합 테스트 스크립트

모든 조회 기능 및 주문 API를 테스트하며 결과를 Discord로 전송합니다.
- 기본 조회 API (인증, 현재가, 일봉, 계좌 잔고 등)
- 신규 조회 API (호가, 거래량/거래대금 순위, 당일 손익, 미체결 주문 등)
- 주문 API (선택적)

주의: 실제 주문 테스트는 매우 신중하게 수행해야 합니다.
     기본적으로 모의투자 모드에서만 테스트합니다.
"""
from config import config
from core.auth import KISAuth
from core.market_data import MarketDataAPI
from core.account import AccountAPI
from core.order import OrderAPI
from notifications.discord import DiscordNotifier


def test_basic_apis():
    """
    기본 API 조회 기능 테스트 (인증, 시세, 계좌)
    """
    notifier = DiscordNotifier()

    header = "=" * 70 + "\n📊 [1단계] 기본 API 테스트\n" + "=" * 70
    print(header)
    notifier.send_message("📊 **[1단계] 기본 API 테스트 시작**")

    # 환경 변수 검증
    try:
        config.validate()
    except ValueError as e:
        error_msg = f"❌ {e}"
        print(error_msg)
        notifier.send_message(error_msg)
        return None, None, None

    # config에서 값 가져오기
    app_key = config.APP_KEY
    app_secret = config.APP_SECRET
    account_no = config.ACCOUNT_NO
    is_virtual = config.IS_PAPER_TRADING

    mode = "모의투자" if is_virtual else "실전투자"
    setup_info = f"✓ 환경 변수 로드 완료\n- 계좌번호: {account_no}\n- 모드: {mode}"
    print(setup_info)
    notifier.send_message(setup_info)

    # 1. 인증 테스트
    msg = "[1/4] 인증 테스트..."
    print(f"\n{msg}")
    notifier.send_message(msg)
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
        return None, None, None

    # 2. 시세 조회 테스트
    msg = "[2/4] 시세 조회 테스트..."
    print(f"\n{msg}")
    notifier.send_message(msg)
    market_api = None
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
    msg = "[3/4] 일봉 데이터 조회 테스트..."
    print(f"\n{msg}")
    notifier.send_message(msg)
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
    msg = "[4/4] 계좌 조회 테스트..."
    print(f"\n{msg}")
    notifier.send_message(msg)
    account_api = None
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

    msg = "✅ [1단계] 기본 API 테스트 완료"
    print(f"\n{msg}")
    notifier.send_message(msg)
    return market_api, account_api, notifier


def test_advanced_market_apis(market_api, notifier):
    """
    신규 추가된 시세 조회 API 테스트 (호가, 순위 등)
    """
    header = "\n" + "=" * 70 + "\n📈 [2단계] 신규 시세 조회 API 테스트\n" + "=" * 70
    print(header)
    notifier.send_message("📈 **[2단계] 신규 시세 조회 API 테스트 시작**")

    try:
        # 1. 호가 조회
        msg = "[1/3] 호가 정보 조회 (삼성전자)"
        print(f"\n{msg}")
        notifier.send_message(msg)

        orderbook = market_api.get_orderbook("005930")
        if orderbook:
            msg = (f"✅ [호가] 조회 성공\n"
                   f"- 현재가: {orderbook['current_price']:,}원\n"
                   f"- 최우선 매도호가: {orderbook['best_ask_price']:,}원\n"
                   f"- 최우선 매수호가: {orderbook['best_bid_price']:,}원\n"
                   f"- 총 매도잔량: {orderbook['total_ask_quantity']:,}주\n"
                   f"- 총 매수잔량: {orderbook['total_bid_quantity']:,}주")
            print(msg)
            notifier.send_message(msg)
        else:
            msg = "❌ 호가 조회 실패"
            print(msg)
            notifier.send_message(msg)

        # 2. 거래량 순위
        msg = "[2/3] 거래량 순위 (코스피 상위 10개)"
        print(f"\n{msg}")
        notifier.send_message(msg)
        volume_rank = market_api.get_volume_rank(market="1")
        if volume_rank:
            rank_msg = [f"✅ [거래량 순위] 조회 성공 ({len(volume_rank)}개)\n"]
            rank_msg.append("[코스피 거래량 TOP 10]")
            for i, item in enumerate(volume_rank[:10], 1):
                rank_msg.append(
                    f"{i}. {item['stock_name']}({item['stock_code']}) - "
                    f"거래량: {item['volume']:,}, 등락률: {item['change_rate']:+.2f}%"
                )
            msg = "\n".join(rank_msg)
            print(msg)
            notifier.send_message(msg[:1990])  # Discord 2000자 제한
        else:
            msg = "❌ 거래량 순위 조회 실패"
            print(msg)
            notifier.send_message(msg)

        # 3. 거래대금 순위
        msg = "[3/3] 거래대금 순위 (전체 상위 10개)"
        print(f"\n{msg}")
        notifier.send_message(msg)
        amount_rank = market_api.get_trade_amount_rank(market="0")
        if amount_rank:
            rank_msg = [f"✅ [거래대금 순위] 조회 성공 ({len(amount_rank)}개)\n"]
            rank_msg.append("[전체 거래대금 TOP 10]")
            for i, item in enumerate(amount_rank[:10], 1):
                rank_msg.append(
                    f"{i}. {item['stock_name']}({item['stock_code']}) - "
                    f"거래대금: {item['trade_amount']:,}원"
                )
            msg = "\n".join(rank_msg)
            print(msg)
            notifier.send_message(msg[:1990])
        else:
            msg = "❌ 거래대금 순위 조회 실패"
            print(msg)
            notifier.send_message(msg)

        msg = "✅ [2단계] 신규 시세 조회 API 테스트 완료"
        print(f"\n{msg}")
        notifier.send_message(msg)

    except Exception as e:
        error = f"❌ 신규 시세 조회 API 테스트 실패: {str(e)}"
        print(error)
        notifier.send_message(error)
        import traceback
        traceback.print_exc()


def test_advanced_account_apis(account_api, notifier):
    """
    신규 추가된 계좌 조회 API 테스트 (당일 손익, 미체결 주문 등)
    """
    header = "\n" + "=" * 70 + "\n💰 [3단계] 신규 계좌 조회 API 테스트\n" + "=" * 70
    print(header)
    notifier.send_message("💰 **[3단계] 신규 계좌 조회 API 테스트 시작**")

    try:
        # 1. 당일 손익 조회
        msg = "[1/2] 당일 손익 조회"
        print(f"\n{msg}")
        notifier.send_message(msg)
        daily_pl = account_api.get_daily_profit_loss()
        if daily_pl:
            msg = (f"✅ [당일 손익] 조회 성공\n"
                   f"- 매수 금액: {daily_pl['total_buy_amount']:,}원 ({daily_pl['buy_count']}건)\n"
                   f"- 매도 금액: {daily_pl['total_sell_amount']:,}원 ({daily_pl['sell_count']}건)\n"
                   f"- 당일 손익: {daily_pl['profit_loss']:,}원")
            print(msg)
            notifier.send_message(msg)
        else:
            msg = "❌ 당일 손익 조회 실패"
            print(msg)
            notifier.send_message(msg)

        # 2. 미체결 주문 조회
        msg = "[2/2] 미체결 주문 조회"
        print(f"\n{msg}")
        notifier.send_message(msg)
        pending = account_api.get_pending_orders()
        if pending is not None:
            msg = f"✅ [미체결 주문] 조회 성공 ({len(pending)}건)"
            if pending:
                msg += "\n[미체결 주문 목록]"
                for order in pending[:5]:  # 최대 5건만
                    msg += (f"\n• [{order['order_type']}] {order['stock_name']}({order['stock_code']})\n"
                            f"  주문: {order['order_quantity']}주 @ {order['order_price']:,}원\n"
                            f"  미체결: {order['pending_quantity']}주")
            else:
                msg += "\n(미체결 주문 없음)"

            print(msg)
            notifier.send_message(msg[:1990])
        else:
            msg = "❌ 미체결 주문 조회 실패"
            print(msg)
            notifier.send_message(msg)

        msg = "✅ [3단계] 신규 계좌 조회 API 테스트 완료"
        print(f"\n{msg}")
        notifier.send_message(msg)

    except Exception as e:
        error = f"❌ 신규 계좌 조회 API 테스트 실패: {str(e)}"
        print(error)
        notifier.send_message(error)
        import traceback
        traceback.print_exc()


def test_order_api(test_real_order: bool = False):
    """
    주문 API 테스트 (매수/매도)

    Args:
        test_real_order: 실제 주문 실행 여부 (기본값: False, 모의 주문만)

    주의: 실제 주문은 매우 위험합니다. 모의투자 모드에서만 테스트하세요!
    """
    notifier = DiscordNotifier()

    header = "\n" + "=" * 70 + "\n🔧 [4단계] 주문 API 테스트\n" + "=" * 70
    print(header)
    notifier.send_message("🔧 **[4단계] 주문 API 테스트 시작**")

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
    msg = f"✓ 모드: {mode}"
    print(msg)
    notifier.send_message(msg)

    try:
        # OrderAPI 초기화
        order_api = OrderAPI(app_key, app_secret, account_no, is_virtual=is_virtual)

        msg = "✅ 주문 API 초기화 완료"
        print(f"\n{msg}")
        notifier.send_message(msg)

        if not test_real_order:
            info_msg = "ℹ️ 실제 주문은 실행하지 않습니다. test_real_order=True로 설정하면 모의투자에서 실제 주문을 테스트할 수 있습니다."
            print(info_msg)
            notifier.send_message(info_msg)
            return

        # 실제 주문 테스트 (모의투자에서만)
        if is_virtual:
            msg = "[1] 시장가 매수 테스트..."
            print(f"\n{msg}")
            notifier.send_message(msg)

            # 소액으로 테스트 (삼성전자 1주)
            buy_result = order_api.buy_market_order("005930", 1)

            if buy_result.get("success"):
                msg = f"✅ 매수 주문 성공\n- 주문번호: {buy_result.get('order_no')}\n- 종목: {buy_result.get('stock_code')}\n- 수량: {buy_result.get('quantity')}주"
                print(msg)
                notifier.send_message(msg)

                # 주문 상태 조회
                msg = "[2] 주문 상태 조회..."
                print(f"\n{msg}")
                notifier.send_message(msg)

                order_no = buy_result.get('order_no')
                status = order_api.get_order_status(order_no)

                status_msg = f"📊 주문 상태\n- 주문번호: {order_no}\n- 체결수량: {status.get('executed_quantity', 0)}주\n- 체결가: {status.get('executed_price', 0):,}원"
                print(status_msg)
                notifier.send_message(status_msg)
            else:
                error = f"❌ 매수 주문 실패: {buy_result.get('error', '알 수 없는 오류')}"
                print(error)
                notifier.send_message(error)

        msg = "✅ [4단계] 주문 API 테스트 완료"
        print(f"\n{msg}")
        notifier.send_message(msg)

    except Exception as e:
        error = f"❌ 주문 API 테스트 중 오류 발생: {str(e)}"
        print(error)
        notifier.send_message(error)


if __name__ == "__main__":
    mode = "모의투자" if config.IS_PAPER_TRADING else "실전투자"
    header = "\n" + "=" * 70 + f"\n🚀 한국투자증권 API 종합 테스트\n모드: {mode}\n" + "=" * 70
    print(header)

    notifier = DiscordNotifier()
    notifier.send_message(f"🚀 **한국투자증권 API 종합 테스트 시작**\n모드: {mode}")

    # 1단계: 기본 API 테스트 (인증, 현재가, 일봉, 계좌 잔고)
    market_api, account_api, notifier = test_basic_apis()

    if market_api and account_api:
        # 2단계: 신규 시세 조회 API 테스트 (호가, 순위)
        test_advanced_market_apis(market_api, notifier)

        # 3단계: 신규 계좌 조회 API 테스트 (당일 손익, 미체결 주문)
        test_advanced_account_apis(account_api, notifier)

    # 4단계: 주문 API 테스트 (선택적)
    test_order_api(test_real_order=False)  # False: 초기화만, True: 실제 주문 테스트

    footer = "\n" + "=" * 70 + "\n🏁 전체 테스트 완료\n" + "=" * 70
    print(footer)

    if notifier:
        notifier.send_message("🏁 **한국투자증권 API 종합 테스트가 모두 완료되었습니다.**")
