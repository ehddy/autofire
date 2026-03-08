"""
한국투자증권 API 인증 모듈 (DB 저장 방식)
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional
from .db_helper import DBHelper

logger = logging.getLogger(__name__)


class KISAuth:
    """
    한국투자증권 OAuth 인증 관리 (DB 저장)
    """

    def __init__(self, app_key: str, app_secret: str, is_virtual: bool = True):
        """
        Args:
            app_key: 앱 키
            app_secret: 앱 시크릿
            is_virtual: 모의투자 여부
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.is_virtual = is_virtual

        self.base_url = (
            "https://openapivts.koreainvestment.com:29443"
            if is_virtual
            else "https://openapi.koreainvestment.com:9443"
        )

        self.db = DBHelper()

    def get_token(self) -> str:
        """
        액세스 토큰 발급/갱신 (DB에서 먼저 확인)

        Returns:
            액세스 토큰
        """
        # 1. DB에서 유효한 토큰 확인
        token = self._get_token_from_db()
        if token:
            logger.info("DB에서 토큰 재사용")
            return token

        # 2. 유효한 토큰이 없으면 새로 발급
        logger.info("새 토큰 발급 시도")
        token = self._issue_new_token()

        # 3. DB에 저장
        self._save_token_to_db(token)

        return token

    def _get_token_from_db(self) -> Optional[str]:
        """
        DB에서 유효한 토큰 가져오기

        Returns:
            유효한 토큰 또는 None
        """
        query = """
            SELECT token_value, expires_at
            FROM api_tokens
            WHERE token_type = 'access_token'
              AND is_virtual = %s
              AND expires_at > NOW() + INTERVAL '10 minutes'
            ORDER BY created_at DESC
            LIMIT 1
        """

        try:
            results = self.db.execute_query(query, (self.is_virtual,))
            if results and len(results) > 0:
                token_value = results[0]['token_value']
                expires_at = results[0]['expires_at']
                logger.info(f"DB 토큰 발견 (만료: {expires_at})")
                return token_value
        except Exception as e:
            logger.error(f"DB 토큰 조회 실패: {str(e)}")

        return None

    def _issue_new_token(self) -> str:
        """
        API를 통해 새 토큰 발급

        Returns:
            액세스 토큰
        """
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            access_token = result.get("access_token")
            expires_in = int(result.get("expires_in", 86400))  # 기본 24시간

            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info(f"토큰 발급 성공 (만료: {self.token_expires_at})")
            return access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"토큰 발급 실패: {str(e)}")
            raise

    def _save_token_to_db(self, token: str):
        """
        토큰을 DB에 저장

        Args:
            token: 액세스 토큰
        """
        # 기존 토큰 삭제 (같은 타입)
        delete_query = """
            DELETE FROM api_tokens
            WHERE token_type = 'access_token'
              AND is_virtual = %s
        """

        # 새 토큰 삽입
        insert_query = """
            INSERT INTO api_tokens (token_type, token_value, expires_at, is_virtual)
            VALUES ('access_token', %s, %s, %s)
        """

        try:
            self.db.execute_update(delete_query, (self.is_virtual,))
            self.db.execute_update(
                insert_query,
                (token, self.token_expires_at, self.is_virtual)
            )
            logger.info("토큰 DB 저장 완료")
        except Exception as e:
            logger.error(f"토큰 DB 저장 실패: {str(e)}")

    def is_token_valid(self) -> bool:
        """
        DB에서 토큰 유효성 검사

        Returns:
            토큰 유효 여부
        """
        token = self._get_token_from_db()
        return token is not None
