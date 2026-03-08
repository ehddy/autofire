import requests
import os
import pytz
from datetime import datetime

class DiscordNotifier:
    def __init__(self):
        # .env 파일에 정의된 WEBHOOK URL을 가져옵니다.
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.korea_timezone = pytz.timezone("Asia/Seoul")

    def send_message(self, msg: str):
        """디스코드 메세지 전송"""
        if not self.webhook_url:
            print(f"⚠️ Discord Webhook URL이 설정되지 않았습니다: {msg}")
            return

        korea_time = datetime.now(self.korea_timezone)
        formatted_time = korea_time.strftime('%Y-%m-%d %H:%M:%S')
        
        payload = {
            "content": f"🚀 **[AutoFIRE]** `{formatted_time}`\n{str(msg)}"
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print(f"📢 Discord 알림 전송 완료: {msg}")
        except Exception as e:
            print(f"❌ Discord 알림 전송 실패: {str(e)}")

