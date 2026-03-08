"""
한국투자증권 주문 실행 API 모듈
"""
import logging
from typing import Dict, Optional
from .kis_api import KISApiBase

logger = logging.getLogger(__name__)


class OrderAPI(KISApiBase):
    """
    주문 실행 API
    """

    def buy_market_order(self, stock_code: str, quantity: int) -> Dict:
        """
        시장가 매수

        Args:
            stock_code: 종목코드
            quantity: 매수 수량

        Returns:
            주문 결과 딕셔너리
        """
        return self._execute_order(
            stock_code=stock_code,
            quantity=quantity,
            order_type="01",  # 시장가
            side="buy"
        )

    def buy_limit_order(self, stock_code: str, quantity: int, price: int) -> Dict:
        """
        지정가 매수

        Args:
            stock_code: 종목코드
            quantity: 매수 수량
            price: 지정 가격

        Returns:
            주문 결과 딕셔너리
        """
        return self._execute_order(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            order_type="00",  # 지정가
            side="buy"
        )

    def sell_market_order(self, stock_code: str, quantity: int) -> Dict:
        """
        시장가 매도

        Args:
            stock_code: 종목코드
            quantity: 매도 수량

        Returns:
            주문 결과 딕셔너리
        """
        return self._execute_order(
            stock_code=stock_code,
            quantity=quantity,
            order_type="01",  # 시장가
            side="sell"
        )

    def sell_limit_order(self, stock_code: str, quantity: int, price: int) -> Dict:
        """
        지정가 매도

        Args:
            stock_code: 종목코드
            quantity: 매도 수량
            price: 지정 가격

        Returns:
            주문 결과 딕셔너리
        """
        return self._execute_order(
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            order_type="00",  # 지정가
            side="sell"
        )

    def _execute_order(
        self,
        stock_code: str,
        quantity: int,
        order_type: str,
        side: str,
        price: int = 0
    ) -> Dict:
        """
        주문 실행 (내부 함수)

        Args:
            stock_code: 종목코드
            quantity: 수량
            order_type: 주문 구분 (00: 지정가, 01: 시장가)
            side: 매수/매도 구분 (buy, sell)
            price: 가격 (시장가는 0)

        Returns:
            주문 결과
        """
        endpoint = "/uapi/domestic-stock/v1/trading/order-cash"

        # 실전/모의 구분
        if side == "buy":
            tr_id = "VTTC0802U" if self.is_virtual else "TTTC0802U"  # 매수
        else:
            tr_id = "VTTC0801U" if self.is_virtual else "TTTC0801U"  # 매도

        data = {
            "CANO": self.account_no_prefix,  # 종합계좌번호
            "ACNT_PRDT_CD": self.account_no_suffix,  # 계좌상품코드
            "PDNO": stock_code,  # 종목코드
            "ORD_DVSN": order_type,  # 주문구분
            "ORD_QTY": str(quantity),  # 주문수량
            "ORD_UNPR": str(price),  # 주문단가 (시장가는 0)
        }

        try:
            result = self._request("POST", endpoint, tr_id=tr_id, data=data)
            output = result.get("output", {})

            order_result = {
                "success": True,
                "order_no": output.get("ODNO"),  # 주문번호
                "order_time": output.get("ORD_TMD"),  # 주문시각
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price if price > 0 else "시장가",
                "side": "매수" if side == "buy" else "매도",
                "message": result.get("msg1", "주문 성공")
            }

            logger.info(f"주문 성공: {order_result['side']} {stock_code} {quantity}주")
            return order_result

        except Exception as e:
            logger.error(f"주문 실패 ({side} {stock_code}): {str(e)}")
            return {
                "success": False,
                "stock_code": stock_code,
                "quantity": quantity,
                "side": "매수" if side == "buy" else "매도",
                "error": str(e)
            }

    def cancel_order(self, order_no: str, stock_code: str, quantity: int, order_type: str = "00") -> Dict:
        """
        주문 취소

        Args:
            order_no: 원주문번호
            stock_code: 종목코드
            quantity: 취소 수량
            order_type: 주문구분

        Returns:
            취소 결과
        """
        endpoint = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
        tr_id = "VTTC0803U" if self.is_virtual else "TTTC0803U"

        data = {
            "CANO": self.account_no_prefix,
            "ACNT_PRDT_CD": self.account_no_suffix,
            "KRX_FWDG_ORD_ORGNO": "",  # 한국거래소전송주문조직번호 (공백)
            "ORGN_ODNO": order_no,  # 원주문번호
            "ORD_DVSN": order_type,  # 주문구분
            "RVSE_CNCL_DVSN_CD": "02",  # 정정취소구분코드 (02: 취소)
            "ORD_QTY": "0",  # 주문수량 (취소는 0)
            "ORD_UNPR": "0",  # 주문단가 (취소는 0)
            "QTY_ALL_ORD_YN": "Y",  # 잔량전부주문여부 (Y: 전량취소)
        }

        try:
            result = self._request("POST", endpoint, tr_id=tr_id, data=data)
            output = result.get("output", {})

            cancel_result = {
                "success": True,
                "order_no": order_no,
                "stock_code": stock_code,
                "message": result.get("msg1", "취소 성공")
            }

            logger.info(f"주문 취소 성공: {order_no}")
            return cancel_result

        except Exception as e:
            logger.error(f"주문 취소 실패 ({order_no}): {str(e)}")
            return {
                "success": False,
                "order_no": order_no,
                "error": str(e)
            }

    def modify_order(
        self,
        order_no: str,
        stock_code: str,
        quantity: int,
        price: int,
        order_type: str = "00"
    ) -> Dict:
        """
        주문 정정

        Args:
            order_no: 원주문번호
            stock_code: 종목코드
            quantity: 정정 수량
            price: 정정 가격
            order_type: 주문구분

        Returns:
            정정 결과
        """
        endpoint = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
        tr_id = "VTTC0803U" if self.is_virtual else "TTTC0803U"

        data = {
            "CANO": self.account_no_prefix,
            "ACNT_PRDT_CD": self.account_no_suffix,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": order_no,
            "ORD_DVSN": order_type,
            "RVSE_CNCL_DVSN_CD": "01",  # 01: 정정
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "QTY_ALL_ORD_YN": "N",
        }

        try:
            result = self._request("POST", endpoint, tr_id=tr_id, data=data)
            output = result.get("output", {})

            modify_result = {
                "success": True,
                "order_no": order_no,
                "new_quantity": quantity,
                "new_price": price,
                "message": result.get("msg1", "정정 성공")
            }

            logger.info(f"주문 정정 성공: {order_no} -> {quantity}주 @ {price}원")
            return modify_result

        except Exception as e:
            logger.error(f"주문 정정 실패 ({order_no}): {str(e)}")
            return {
                "success": False,
                "order_no": order_no,
                "error": str(e)
            }

    def get_order_status(self, order_no: str) -> Dict:
        """
        주문 체결 조회

        Args:
            order_no: 주문번호

        Returns:
            체결 정보
        """
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-ccnl"
        tr_id = "VTTC8001R" if self.is_virtual else "TTTC8001R"

        params = {
            "CANO": self.account_no_prefix,
            "ACNT_PRDT_CD": self.account_no_suffix,
            "INQR_STRT_DT": "",  # 조회시작일자 (당일)
            "INQR_END_DT": "",  # 조회종료일자
            "SLL_BUY_DVSN_CD": "00",  # 매도매수구분 (00: 전체)
            "INQR_DVSN": "00",
            "PDNO": "",
            "CCLD_DVSN": "00",
            "ORD_GNO_BRNO": "",
            "ODNO": order_no,  # 주문번호
            "INQR_DVSN_3": "00",
            "INQR_DVSN_1": "",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }

        try:
            result = self._request("GET", endpoint, tr_id=tr_id, params=params)
            output = result.get("output1", [])

            if output:
                item = output[0]
                return {
                    "order_no": order_no,
                    "stock_code": item.get("pdno"),
                    "stock_name": item.get("prdt_name"),
                    "order_quantity": int(item.get("ord_qty", 0)),
                    "executed_quantity": int(item.get("tot_ccld_qty", 0)),
                    "executed_price": int(item.get("avg_prvs", 0)),
                    "order_status": item.get("ord_qty") == item.get("tot_ccld_qty") and "완료" or "진행중",
                }
            else:
                return {"order_no": order_no, "status": "조회 결과 없음"}

        except Exception as e:
            logger.error(f"체결 조회 실패 ({order_no}): {str(e)}")
            return {"order_no": order_no, "error": str(e)}
