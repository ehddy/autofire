"""
Selector 환경 변수 설정
selectors/.env 파일에서 Selector별 설정을 로드합니다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# selectors/.env 파일 로드
selector_env_path = Path(__file__).parent / '.env'
load_dotenv(selector_env_path)


class SelectorConfig:
    """Selector별 환경 변수 관리 클래스"""

    # ===== 공통 설정 =====
    MIN_MARKET_CAP: int = int(os.getenv("MIN_MARKET_CAP", "1000000000"))
    MIN_TRADE_AMOUNT: int = int(os.getenv("MIN_TRADE_AMOUNT", "100000000"))
    EXCLUDE_MANAGEMENT_STOCKS: bool = os.getenv("EXCLUDE_MANAGEMENT_STOCKS", "true").lower() == "true"

    # ===== TechnicalSelector 설정 =====
    TECHNICAL_MIN_VOLUME: int = int(os.getenv("TECHNICAL_MIN_VOLUME", "100000000"))
    TECHNICAL_RSI_LOWER: int = int(os.getenv("TECHNICAL_RSI_LOWER", "30"))
    TECHNICAL_RSI_UPPER: int = int(os.getenv("TECHNICAL_RSI_UPPER", "50"))
    TECHNICAL_MA_SHORT: int = int(os.getenv("TECHNICAL_MA_SHORT", "20"))
    TECHNICAL_MA_LONG: int = int(os.getenv("TECHNICAL_MA_LONG", "60"))
    TECHNICAL_LOOKBACK_DAYS: int = int(os.getenv("TECHNICAL_LOOKBACK_DAYS", "60"))

    # ===== VolumeSelector 설정 =====
    VOLUME_RATIO: float = float(os.getenv("VOLUME_RATIO", "2.0"))
    VOLUME_MIN_PRICE_CHANGE: float = float(os.getenv("VOLUME_MIN_PRICE_CHANGE", "1.0"))
    VOLUME_MIN_TRADE_AMOUNT: int = int(os.getenv("VOLUME_MIN_TRADE_AMOUNT", "100000000"))
    VOLUME_MA_PERIOD: int = int(os.getenv("VOLUME_MA_PERIOD", "20"))
    VOLUME_LOOKBACK_DAYS: int = int(os.getenv("VOLUME_LOOKBACK_DAYS", "30"))

    @classmethod
    def print_config(cls) -> None:
        """현재 Selector 설정 출력"""
        print("\n" + "="*50)
        print("📊 Selector 설정")
        print("="*50)
        print(f"💰 최소 시가총액: {cls.MIN_MARKET_CAP:,}원")
        print(f"💵 최소 거래대금: {cls.MIN_TRADE_AMOUNT:,}원")
        print(f"⚠️ 관리종목 제외: {cls.EXCLUDE_MANAGEMENT_STOCKS}")
        print("\n[TechnicalSelector]")
        print(f"  - RSI 범위: {cls.TECHNICAL_RSI_LOWER}~{cls.TECHNICAL_RSI_UPPER}")
        print(f"  - 이동평균: {cls.TECHNICAL_MA_SHORT}일 / {cls.TECHNICAL_MA_LONG}일")
        print(f"  - 데이터 기간: {cls.TECHNICAL_LOOKBACK_DAYS}일")
        print("\n[VolumeSelector]")
        print(f"  - 거래량 배수: {cls.VOLUME_RATIO}배")
        print(f"  - 최소 상승률: +{cls.VOLUME_MIN_PRICE_CHANGE}%")
        print(f"  - 평균 기간: {cls.VOLUME_MA_PERIOD}일")
        print(f"  - 데이터 기간: {cls.VOLUME_LOOKBACK_DAYS}일")
        print("="*50 + "\n")


# 싱글톤 인스턴스
selector_config = SelectorConfig()
