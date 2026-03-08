"""
한국투자증권 계좌 조회 API 모듈
"""
import logging
from typing import Dict, List
from .kis_api import KISApiBase

logger = logging.getLogger(__name__)


class AccountAPI(KISApiBase):
    """
    계좌 조회 API
    """

    def get_balance(self) -> Dict:
        """
        계좌 잔고 조회 (예수금 + 보유 종목)

        Returns:
            계좌 잔고 정보 딕셔너리
        """
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-balance"
        tr_id = "VTTC8434R" if self.is_virtual else "TTTC8434R"  # 모의/실전 구분

        params = {
            "CANO": self.account_no_prefix,  # 종합계좌번호
            "ACNT_PRDT_CD": self.account_no_suffix,  # 계좌상품코드
            "AFHR_FLPR_YN": "N",  # 시간외단일가여부
            "OFL_YN": "",  # 오프라인여부
            "INQR_DVSN": "02",  # 조회구분 (01: 대출일별, 02: 종목별)
            "UNPR_DVSN": "01",  # 단가구분
            "FUND_STTL_ICLD_YN": "N",  # 펀드결제분포함여부
            "FNCG_AMT_AUTO_RDPT_YN": "N",  # 융자금액자동상환여부
            "PRCS_DVSN": "00",  # 처리구분
            "CTX_AREA_FK100": "",  # 연속조회검색조건100
            "CTX_AREA_NK100": "",  # 연속조회키100
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)

            output1 = result.get("output1", [])  # 보유 종목 리스트
            output2 = result.get("output2", [{}])[0]  # 계좌 요약

            # 보유 종목 파싱
            holdings = []
            for item in output1:
                if int(item.get("hldg_qty", 0)) > 0:  # 보유 수량이 있는 종목만
                    holdings.append({
                        "stock_code": item.get("pdno"),
                        "stock_name": item.get("prdt_name"),
                        "quantity": int(item.get("hldg_qty", 0)),
                        "avg_price": float(item.get("pchs_avg_pric", 0)),
                        "current_price": int(item.get("prpr", 0)),
                        "eval_amount": int(item.get("evlu_amt", 0)),  # 평가금액
                        "profit_loss": int(item.get("evlu_pfls_amt", 0)),  # 평가손익
                        "profit_rate": float(item.get("evlu_pfls_rt", 0)),  # 평가손익률
                    })

            # 계좌 요약 파싱
            summary = {
                "total_assets": int(output2.get("tot_evlu_amt", 0)),  # 총 평가금액
                "cash_balance": int(output2.get("dnca_tot_amt", 0)),  # 예수금 총액
                "stock_value": int(output2.get("scts_evlu_amt", 0)),  # 유가증권 평가금액
                "profit_loss": int(output2.get("evlu_pfls_smtl_amt", 0)),  # 평가손익합계
                "profit_rate": float(output2.get("tot_evlu_pfls_rt", 0)),  # 총 평가손익률
                "holdings": holdings,
            }

            logger.info(f"계좌 조회 성공: 보유 종목 {len(holdings)}개")
            return summary

        except Exception as e:
            logger.error(f"계좌 조회 실패: {str(e)}")
            return {}

    def get_buy_available_cash(self) -> int:
        """
        매수 가능 금액 조회

        Returns:
            매수 가능 금액
        """
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        tr_id = "VTTC8908R" if self.is_virtual else "TTTC8908R"

        params = {
            "CANO": self.account_no_prefix,
            "ACNT_PRDT_CD": self.account_no_suffix,
            "PDNO": "005930",  # 삼성전자 (더미)
            "ORD_UNPR": "0",  # 주문단가
            "ORD_DVSN": "01",  # 주문구분 (01: 시장가)
            "CMA_EVLU_AMT_ICLD_YN": "Y",  # CMA평가금액포함여부
            "OVRS_ICLD_YN": "N",  # 해외포함여부
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output", {})

            available_cash = int(output.get("ord_psbl_cash", 0))  # 주문가능현금
            logger.info(f"매수 가능 금액: {available_cash:,}원")
            return available_cash

        except Exception as e:
            logger.error(f"매수 가능 금액 조회 실패: {str(e)}")
            return 0

    def get_order_history(self) -> List[Dict]:
        """
        당일 주문 내역 조회

        Returns:
            주문 내역 리스트
        """
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
        tr_id = "VTTC8001R" if self.is_virtual else "TTTC8001R"

        params = {
            "CANO": self.account_no_prefix,
            "ACNT_PRDT_CD": self.account_no_suffix,
            "INQR_STRT_DT": "",  # 조회시작일자 (공백: 당일)
            "INQR_END_DT": "",  # 조회종료일자
            "SLL_BUY_DVSN_CD": "00",  # 매도매수구분 (00: 전체)
            "INQR_DVSN": "00",  # 조회구분
            "PDNO": "",  # 종목코드 (공백: 전체)
            "CCLD_DVSN": "00",  # 체결구분 (00: 전체)
            "ORD_GNO_BRNO": "",  # 주문채번지점번호
            "ODNO": "",  # 주문번호
            "INQR_DVSN_3": "00",  # 조회구분3
            "INQR_DVSN_1": "",  # 조회구분1
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output1", [])

            orders = []
            for item in output:
                orders.append({
                    "order_no": item.get("odno"),  # 주문번호
                    "stock_code": item.get("pdno"),
                    "stock_name": item.get("prdt_name"),
                    "order_type": "매수" if item.get("sll_buy_dvsn_cd") == "02" else "매도",
                    "order_quantity": int(item.get("ord_qty", 0)),
                    "order_price": int(item.get("ord_unpr", 0)),
                    "executed_quantity": int(item.get("tot_ccld_qty", 0)),  # 총 체결수량
                    "executed_price": int(item.get("avg_prvs", 0)),  # 평균가
                    "order_time": item.get("ord_tmd"),
                })

            logger.info(f"주문 내역 조회: {len(orders)}건")
            return orders

        except Exception as e:
            logger.error(f"주문 내역 조회 실패: {str(e)}")
            return []
