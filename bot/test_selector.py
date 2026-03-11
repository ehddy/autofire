#!/usr/bin/env python3
"""
Selector 테스트 스크립트

.env에서 설정한 SELECTION_POLICIES를 로드하여
각 selector의 종목 선정 결과를 테스트하고 Discord로 전송
"""
import sys
import os
from datetime import datetime

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from notifications.discord import DiscordNotifier
from selectors.technical import TechnicalSelector
from selectors.volume import VolumeSelector


def load_selectors():
    """
    .env에서 설정한 SELECTION_POLICIES를 동적으로 로드

    Returns:
        선정 정책 인스턴스 리스트
    """
    selectors = []
    policy_classes = {
        'TechnicalSelector': TechnicalSelector,
        'VolumeSelector': VolumeSelector,
    }

    for policy_name in Config.SELECTION_POLICIES:
        if policy_name in policy_classes:
            selector_class = policy_classes[policy_name]
            selectors.append(selector_class())
            print(f"✓ {policy_name} 로드 완료")
        else:
            print(f"⚠️ {policy_name} 클래스를 찾을 수 없습니다.")

    return selectors


def format_stock_info(stock_codes):
    """
    종목 코드 리스트를 읽기 쉬운 형태로 포맷팅

    Args:
        stock_codes: 종목 코드 리스트

    Returns:
        포맷팅된 문자열
    """
    # TODO: 실제로는 DB에서 종목명을 조회해야 함
    stock_names = {
        '005930': '삼성전자',
        '000660': 'SK하이닉스',
        '035720': '카카오',
        '005380': '현대차',
        '051910': 'LG화학',
    }

    result = []
    for i, code in enumerate(stock_codes, 1):
        name = stock_names.get(code, '알 수 없음')
        result.append(f"{i}. {name}({code})")

    return "\n".join(result)


def test_selectors():
    """
    .env에 설정된 selector 전략들을 테스트
    """
    print("\n" + "="*70)
    print("📊 Selector 종목 선정 테스트")
    print("="*70)

    # Discord 알림 초기화
    notifier = DiscordNotifier()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"🚀 **[AutoFIRE] Selector 테스트**\n"
        f"시간: {timestamp}\n"
        f"모드: {'모의투자' if Config.IS_PAPER_TRADING else '실전투자'}"
    )
    print(header)
    notifier.send_message(header)

    # 설정 정보 출력
    msg = (
        f"\n📋 **설정 정보**\n"
        f"- 활성 Selector: {', '.join(Config.SELECTION_POLICIES)}\n"
        f"- 선정 목표 수: {Config.SELECT_COUNT}개"
    )
    print(msg)
    notifier.send_message(msg)

    # Selector 로드
    print("\n" + "-"*70)
    print("🔧 Selector 로드 중...")
    print("-"*70)
    selectors = load_selectors()

    if not selectors:
        error = "❌ 활성화된 selector가 없습니다. .env의 SELECTION_POLICIES를 확인하세요."
        print(error)
        notifier.send_message(error)
        return

    msg = f"✅ {len(selectors)}개 Selector 로드 완료"
    print(f"\n{msg}")
    notifier.send_message(msg)

    # 각 selector 테스트
    all_selected_stocks = {}

    for i, selector in enumerate(selectors, 1):
        print("\n" + "-"*70)
        print(f"[{i}/{len(selectors)}] {selector.name} 테스트")
        print("-"*70)

        msg = f"📈 **[{i}/{len(selectors)}] {selector.name} 종목 선정 시작**"
        notifier.send_message(msg)

        try:
            # 종목 선정 실행
            selected = selector.select_stocks(select_count=Config.SELECT_COUNT)

            if selected:
                stock_list = format_stock_info(selected)
                result_msg = (
                    f"✅ **{selector.name} 선정 완료**\n"
                    f"선정 종목: {len(selected)}개\n\n"
                    f"{stock_list}"
                )
                print(f"\n{result_msg}")
                notifier.send_message(result_msg)

                # 선정 결과 저장
                all_selected_stocks[selector.name] = selected
            else:
                error_msg = f"⚠️ {selector.name}에서 종목을 선정하지 못했습니다."
                print(f"\n{error_msg}")
                notifier.send_message(error_msg)

        except Exception as e:
            error_msg = f"❌ {selector.name} 실행 중 오류 발생: {str(e)}"
            print(f"\n{error_msg}")
            notifier.send_message(error_msg)
            import traceback
            traceback.print_exc()

    # 최종 요약
    print("\n" + "="*70)
    print("📊 선정 결과 요약")
    print("="*70)

    if all_selected_stocks:
        # 전체 선정 종목 수 계산
        all_codes = set()
        for codes in all_selected_stocks.values():
            all_codes.update(codes)

        summary = (
            f"\n🎯 **최종 선정 결과**\n"
            f"- 실행된 Selector: {len(all_selected_stocks)}개\n"
            f"- 중복 제거 총 종목 수: {len(all_codes)}개\n\n"
        )

        # Selector별 선정 종목 리스트
        for selector_name, codes in all_selected_stocks.items():
            summary += f"**{selector_name}**: {', '.join(codes)}\n"

        print(summary)
        notifier.send_message(summary)
    else:
        error = "⚠️ 선정된 종목이 없습니다."
        print(error)
        notifier.send_message(error)

    # 테스트 완료
    final_msg = "✅ **Selector 테스트 완료**"
    print(f"\n{final_msg}")
    print("="*70 + "\n")
    notifier.send_message(final_msg)


if __name__ == "__main__":
    try:
        # 환경 변수 검증
        Config.validate()

        # Selector 테스트 실행
        test_selectors()

    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
