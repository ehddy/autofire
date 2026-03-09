"""
한국투자증권 시세 조회 API 모듈
"""
import logging
from typing import Dict, List, Optional
from .kis_api import KISApiBase
from .auth import KISAuth

logger = logging.getLogger(__name__)


class MarketDataAPI(KISApiBase):
    """
    시세 조회 API
    """

    def __init__(self, app_key: str, app_secret: str, account_no: str, is_virtual: bool = True):
        """
        Args:
            app_key: 앱 키
            app_secret: 앱 시크릿
            account_no: 계좌번호
            is_virtual: 모의투자 여부
        """
        super().__init__(app_key, app_secret, account_no, is_virtual)

        # 인증 모듈 초기화
        self.auth = KISAuth(app_key, app_secret, is_virtual)

        # 액세스 토큰 발급
        self.access_token = self.auth.get_token()
        logger.info("MarketDataAPI 초기화 완료 - 토큰 발급됨")

    def get_current_price(self, stock_code: str) -> Dict:
        """
        현재가 조회

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            현재가 정보 딕셔너리
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
        tr_id = "FHKST01010100"  # 주식현재가 시세

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # 시장 구분 (J: 주식)
            "FID_INPUT_ISCD": stock_code,  # 종목코드
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output", {})

            return {
                "stock_code": stock_code,
                "current_price": int(output.get("stck_prpr", 0)),  # 현재가
                "change_rate": float(output.get("prdy_ctrt", 0)),  # 전일대비율
                "volume": int(output.get("acml_vol", 0)),  # 누적거래량
                "high_price": int(output.get("stck_hgpr", 0)),  # 최고가
                "low_price": int(output.get("stck_lwpr", 0)),  # 최저가
                "open_price": int(output.get("stck_oprc", 0)),  # 시가
            }

        except Exception as e:
            logger.error(f"현재가 조회 실패 ({stock_code}): {str(e)}")
            return {}

    def get_daily_price(self, stock_code: str, period: str = "D") -> List[Dict]:
        """
        일봉/주봉/월봉 조회

        Args:
            stock_code: 종목코드
            period: 기간 구분 (D: 일봉, W: 주봉, M: 월봉)

        Returns:
            가격 정보 리스트
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        tr_id = "FHKST01010400"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "0",  # 수정주가 구분 (0: 미반영)
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output_list = result.get("output", [])

            price_list = []
            for item in output_list[:100]:  # 최근 100일
                price_list.append({
                    "date": item.get("stck_bsop_date"),  # 영업일자
                    "open": int(item.get("stck_oprc", 0)),
                    "high": int(item.get("stck_hgpr", 0)),
                    "low": int(item.get("stck_lwpr", 0)),
                    "close": int(item.get("stck_clpr", 0)),
                    "volume": int(item.get("acml_vol", 0)),
                })

            return price_list

        except Exception as e:
            logger.error(f"일봉 조회 실패 ({stock_code}): {str(e)}")
            return []

    def get_minute_price(self, stock_code: str, time_unit: str = "1") -> List[Dict]:
        """
        분봉 조회

        Args:
            stock_code: 종목코드
            time_unit: 시간 단위 (1, 3, 5, 10, 30, 60)

        Returns:
            분봉 데이터 리스트
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        tr_id = "FHKST01010600"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_HOUR_1": time_unit,  # 시간 단위
            "FID_PW_DATA_INCU_YN": "Y",  # 과거 데이터 포함 여부
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output_list = result.get("output2", [])

            minute_list = []
            for item in output_list[:100]:  # 최근 100개
                minute_list.append({
                    "datetime": item.get("stck_bsop_date") + item.get("stck_cntg_hour"),  # 일시
                    "price": int(item.get("stck_prpr", 0)),  # 현재가
                    "open": int(item.get("stck_oprc", 0)),
                    "high": int(item.get("stck_hgpr", 0)),
                    "low": int(item.get("stck_lwpr", 0)),
                    "volume": int(item.get("cntg_vol", 0)),
                })

            return minute_list

        except Exception as e:
            logger.error(f"분봉 조회 실패 ({stock_code}): {str(e)}")
            return []

    def get_stock_info(self, stock_code: str) -> Dict:
        """
        종목 기본 정보 조회

        Args:
            stock_code: 종목코드

        Returns:
            종목 정보 딕셔너리
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/search-stock-info"
        tr_id = "CTPF1002R"

        params = {
            "PDNO": stock_code,
            "PRDT_TYPE_CD": "300",  # 상품 유형 (300: 주식)
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output", {})

            return {
                "stock_code": stock_code,
                "stock_name": output.get("prdt_name", ""),  # 종목명
                "market_type": output.get("std_pdno_short_pdno_prsn", ""),  # 시장구분
                "listing_date": output.get("lstg_dt", ""),  # 상장일
            }

        except Exception as e:
            logger.error(f"종목 정보 조회 실패 ({stock_code}): {str(e)}")
            return {}
