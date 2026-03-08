"""
한국투자증권 Open API 기본 클래스
"""
import os
import requests
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KISApiBase:
    """
    한국투자증권 API 기본 클래스
    """

    # API URL
    BASE_URL_REAL = "https://openapi.koreainvestment.com:9443"  # 실전투자
    BASE_URL_VIRTUAL = "https://openapivts.koreainvestment.com:29443"  # 모의투자

    def __init__(self, app_key: str, app_secret: str, account_no: str, is_virtual: bool = True):
        """
        Args:
            app_key: 앱 키
            app_secret: 앱 시크릿
            account_no: 계좌번호 (8자리-2자리 형식)
            is_virtual: 모의투자 여부 (기본값: True)
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.account_no = account_no
        self.is_virtual = is_virtual

        # 계좌번호 파싱 (XXXXXXXX-XX 형식)
        if '-' in account_no:
            self.account_no_prefix = account_no.split('-')[0]
            self.account_no_suffix = account_no.split('-')[1]
        else:
            self.account_no_prefix = account_no[:8]
            self.account_no_suffix = account_no[8:10]

        self.base_url = self.BASE_URL_VIRTUAL if is_virtual else self.BASE_URL_REAL

        # 인증 토큰
        self.access_token: Optional[str] = None

        logger.info(f"KIS API 초기화: {'모의투자' if is_virtual else '실전투자'} 모드")

    def _get_headers(self, tr_id: str = "", custtype: str = "P") -> Dict[str, str]:
        """
        API 요청 헤더 생성

        Args:
            tr_id: 거래ID
            custtype: 고객구분 (P: 개인, B: 법인)

        Returns:
            헤더 딕셔너리
        """
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token}" if self.access_token else "",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
            "custtype": custtype,
        }

        if tr_id:
            headers["tr_id"] = tr_id

        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        tr_id: str = "",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict:
        """
        API 요청 실행

        Args:
            method: HTTP 메서드 (GET, POST 등)
            endpoint: API 엔드포인트
            tr_id: 거래ID
            params: 쿼리 파라미터
            data: 요청 바디

        Returns:
            응답 딕셔너리
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(tr_id=tr_id)

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

            response.raise_for_status()
            result = response.json()

            # API 에러 체크
            if result.get("rt_cd") != "0":
                error_msg = result.get("msg1", "알 수 없는 오류")
                logger.error(f"API 오류: {error_msg}")
                raise Exception(f"API 오류: {error_msg}")

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {str(e)}")
            raise
