import os
import time
from dotenv import load_dotenv
from notifications.discord import DiscordNotifier # 생성한 모듈 임포트

# 환경 변수 로드
load_dotenv()

def main():
    # 디스코드 알림 객체 생성
    notifier = DiscordNotifier()

    notifier.send_message("AutoFIRE Trading Bot이 시작되었습니다!")

    env = os.getenv('ENV', 'development')
    notifier.send_message(f"현재 실행 환경: {env}")

    try:
        # 예시: 특정 로직 성공 시 알림
        notifier.send_message("KIS API 인증 성공. 매매 전략을 가동합니다.")
        
        while True:
            # 봇 로직 수행...
            time.sleep(60)
            
    except KeyboardInterrupt:
        notifier.send_message("사용자에 의해 봇이 중지되었습니다. 🛑")
    except Exception as e:
        notifier.send_message(f"🧨 시스템 에러 발생: {str(e)}")

if __name__ == "__main__":
    main()