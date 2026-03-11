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
            # 자릿수를 10자리로 맞추어 전달 (0: 미반영, 1: 반영)
            "FID_ORG_ADJ_PRC": "0000000000" 
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

    def get_orderbook(self, stock_code: str) -> Dict:
        """
        호가 정보 조회 (매수/매도 10호가)

        Args:
            stock_code: 종목코드

        Returns:
            호가 정보 딕셔너리
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
        tr_id = "FHKST01010200"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output1 = result.get("output1", {})
            output2 = result.get("output2", [])

            # 10호가 데이터 파싱
            bid_prices = []  # 매수호가
            ask_prices = []  # 매도호가

            for i in range(1, 11):
                # 매도호가 (역순으로 저장 - 10호가부터)
                ask_prices.append({
                    "price": int(output1.get(f"askp{i}", 0)),
                    "quantity": int(output1.get(f"askp_rsqn{i}", 0)),
                })

                # 매수호가
                bid_prices.append({
                    "price": int(output1.get(f"bidp{i}", 0)),
                    "quantity": int(output1.get(f"bidp_rsqn{i}", 0)),
                })

            return {
                "stock_code": stock_code,
                "current_price": int(output1.get("stck_prpr", 0)),  # 현재가
                "best_ask_price": int(output1.get("askp1", 0)),  # 최우선 매도호가
                "best_bid_price": int(output1.get("bidp1", 0)),  # 최우선 매수호가
                "total_ask_quantity": int(output1.get("total_askp_rsqn", 0)),  # 총 매도잔량
                "total_bid_quantity": int(output1.get("total_bidp_rsqn", 0)),  # 총 매수잔량
                "ask_prices": ask_prices,  # 매도호가 리스트
                "bid_prices": bid_prices,  # 매수호가 리스트
            }

        except Exception as e:
            logger.error(f"호가 조회 실패 ({stock_code}): {str(e)}")
            return {}

    def get_volume_rank(self, market: str = "0", condition: str = "0") -> List[Dict]:
        """
        거래량 순위 조회

        Args:
            market: 시장구분 (0: 전체, 1: 코스피, 2: 코스닥)
            condition: 조건 (0: 전체, 1: 관리종목제외, 5: 증권사추천종목제외 등)

        Returns:
            거래량 순위 리스트 (상위 30개)
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/volume-rank"
        tr_id = "FHPST01710000"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20171",  # 거래량 순위
            "FID_INPUT_ISCD": "0000",  # 전체
            "FID_DIV_CLS_CODE": market,  # 시장구분
            "FID_BLNG_CLS_CODE": condition,  # 조건
            "FID_TRGT_CLS_CODE": "111111111",  # 대상 (전체)
            "FID_TRGT_EXLS_CLS_CODE": "0000000000",  # 제외 대상
            "FID_INPUT_PRICE_1": "",  # 입력가격1
            "FID_INPUT_PRICE_2": "",  # 입력가격2
            "FID_VOL_CNT": "",  # 거래량 수
            "FID_INPUT_DATE_1": "",  # 입력일자1
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output", [])

            rank_list = []
            for item in output[:30]:  # 상위 30개만
                rank_list.append({
                    "rank": int(item.get("data_rank", 0)),  # 순위
                    "stock_code": item.get("mksc_shrn_iscd"),  # 종목코드
                    "stock_name": item.get("hts_kor_isnm"),  # 종목명
                    "current_price": int(item.get("stck_prpr", 0)),  # 현재가
                    "change_rate": float(item.get("prdy_ctrt", 0)),  # 전일대비율
                    "volume": int(item.get("acml_vol", 0)),  # 누적거래량
                    "trade_amount": int(item.get("acml_tr_pbmn", 0)),  # 누적거래대금
                })

            logger.info(f"거래량 순위 조회 성공: {len(rank_list)}개")
            return rank_list

        except Exception as e:
            logger.error(f"거래량 순위 조회 실패: {str(e)}")
            return []

    def get_trade_amount_rank(self, market: str = "0") -> List[Dict]:
        """
        거래대금 순위 조회

        Args:
            market: 시장구분 (0: 전체, 1: 코스피, 2: 코스닥)

        Returns:
            거래대금 순위 리스트 (상위 30개)
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/volume-rank"
        tr_id = "FHPST01710000"

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20170",  # 거래대금 순위
            "FID_INPUT_ISCD": "0000",
            "FID_DIV_CLS_CODE": market,
            "FID_BLNG_CLS_CODE": "0",
            "FID_TRGT_CLS_CODE": "111111111",
            "FID_TRGT_EXLS_CLS_CODE": "0000000000",
            "FID_INPUT_PRICE_1": "",
            "FID_INPUT_PRICE_2": "",
            "FID_VOL_CNT": "",
            "FID_INPUT_DATE_1": "",
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output", [])

            rank_list = []
            for item in output[:30]:
                rank_list.append({
                    "rank": int(item.get("data_rank", 0)),
                    "stock_code": item.get("mksc_shrn_iscd"),
                    "stock_name": item.get("hts_kor_isnm"),
                    "current_price": int(item.get("stck_prpr", 0)),
                    "change_rate": float(item.get("prdy_ctrt", 0)),
                    "volume": int(item.get("acml_vol", 0)),
                    "trade_amount": int(item.get("acml_tr_pbmn", 0)),
                })

            logger.info(f"거래대금 순위 조회 성공: {len(rank_list)}개")
            return rank_list

        except Exception as e:
            logger.error(f"거래대금 순위 조회 실패: {str(e)}")
            return []

