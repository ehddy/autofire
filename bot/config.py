"""
AutoFIRE Trading Bot 환경 변수 설정
CLAUDE.md에 정의된 환경 변수를 로드하고 관리
"""
import os
from typing import List
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Config:
    """환경 변수 중앙 관리 클래스"""

    # ===== KIS API 설정 =====
    APP_KEY: str = os.getenv("APP_KEY", "")
    APP_SECRET: str = os.getenv("APP_SECRET", "")
    ACCOUNT_NO: str = os.getenv("ACCOUNT_NO", "")
    IS_PAPER_TRADING: bool = os.getenv("IS_PAPER_TRADING", "true").lower() == "true"

    # ===== 스케줄 설정 =====
    SELECTION_TIME: str = os.getenv("SELECTION_TIME", "08:30")
    REPORT_TIME: str = os.getenv("REPORT_TIME", "16:00")

    # ===== 전략 설정 =====
    ACTIVE_STRATEGIES: List[str] = [
        s.strip()
        for s in os.getenv("ACTIVE_STRATEGIES", "").split(",")
        if s.strip()
    ]
    SELECTION_POLICIES: List[str] = [
        s.strip()
        for s in os.getenv("SELECTION_POLICIES", "").split(",")
        if s.strip()
    ]

    # ===== 매매 설정 =====
    MAX_BUY_AMOUNT: int = int(os.getenv("MAX_BUY_AMOUNT", "1000000"))
    SLIPPAGE_TOLERANCE: float = float(os.getenv("SLIPPAGE_TOLERANCE", "0.5"))
    STOP_LOSS: float = float(os.getenv("STOP_LOSS", "-2.0"))
    TAKE_PROFIT: float = float(os.getenv("TAKE_PROFIT", "3.0"))
    DAILY_STOP_LOSS: float = float(os.getenv("DAILY_STOP_LOSS", "-3.0"))
    SELECT_COUNT: int = int(os.getenv("SELECT_COUNT", "5"))

    # ===== DB 설정 =====
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "autofire")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # ===== 알림 설정 =====
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")

    # ===== 환경 설정 =====
    ENV: str = os.getenv("ENV", "development")

    @classmethod
    def validate(cls) -> None:
        """필수 환경 변수 검증"""
        required_fields = {
            "APP_KEY": cls.APP_KEY,
            "APP_SECRET": cls.APP_SECRET,
            "ACCOUNT_NO": cls.ACCOUNT_NO,
            "DB_PASSWORD": cls.DB_PASSWORD,
        }

        missing = [key for key, value in required_fields.items() if not value]

        if missing:
            raise ValueError(
                f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing)}\n"
                f".env 파일을 확인하세요."
            )

    @classmethod
    def get_db_url(cls) -> str:
        """PostgreSQL 연결 URL 생성"""
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def print_config(cls) -> None:
        """현재 설정 출력 (민감 정보는 마스킹)"""
        print("\n" + "="*50)
        print("📋 현재 설정")
        print("="*50)
        print(f"🔑 APP_KEY: {cls._mask(cls.APP_KEY)}")
        print(f"🔐 APP_SECRET: {cls._mask(cls.APP_SECRET)}")
        print(f"💳 ACCOUNT_NO: {cls._mask(cls.ACCOUNT_NO)}")
        print(f"🎯 모드: {'모의투자' if cls.IS_PAPER_TRADING else '실전투자'}")
        print(f"⏰ 종목선정: {cls.SELECTION_TIME}")
        print(f"📊 리포트: {cls.REPORT_TIME}")
        print(f"📈 활성 전략: {', '.join(cls.ACTIVE_STRATEGIES) if cls.ACTIVE_STRATEGIES else '없음'}")
        print(f"🎲 선정 정책: {', '.join(cls.SELECTION_POLICIES) if cls.SELECTION_POLICIES else '없음'}")
        print(f"💰 최대 매수금액: {cls.MAX_BUY_AMOUNT:,}원")
        print(f"📉 손절: {cls.STOP_LOSS}%")
        print(f"📈 익절: {cls.TAKE_PROFIT}%")
        print(f"🚨 일일손절: {cls.DAILY_STOP_LOSS}%")
        print(f"🎯 선정 종목 수: {cls.SELECT_COUNT}개")
        print(f"🗄️ DB: {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        print(f"💬 Discord: {'설정됨' if cls.DISCORD_WEBHOOK_URL else '미설정'}")
        print(f"🌍 환경: {cls.ENV}")
        print("="*50 + "\n")

    @staticmethod
    def _mask(value: str, show: int = 4) -> str:
        """민감 정보 마스킹"""
        if not value:
            return "미설정"
        if len(value) <= show:
            return "*" * len(value)
        return value[:show] + "*" * (len(value) - show)


# 싱글톤 인스턴스
config = Config()
