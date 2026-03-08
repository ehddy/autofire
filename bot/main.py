"""
AutoFIRE Trading Bot
한국투자증권 API 기반 자동 매매 봇
"""
import os
import time
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def main():
    """
    봇 메인 실행 함수
    """
    print("=" * 50)
    print("AutoFIRE Trading Bot Started")
    print("=" * 50)

    # 환경 변수 확인
    env = os.getenv('ENV', 'development')
    print(f"Environment: {env}")

    # TODO: 실제 로직 구현
    # - KIS API 인증
    # - 전략 로드
    # - 스케줄러 시작

    print("Bot is running... (Press Ctrl+C to stop)")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nBot stopped by user")

if __name__ == "__main__":
    main()
