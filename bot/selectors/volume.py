"""
Volume Selector
거래량 급증 종목 선정 정책

전략 설명:
- 당일 거래량이 20일 평균 대비 N배 이상
- 가격 상승 중인 종목만
- 거래대금 필터링
"""
import sys
sys.path.insert(0, '/app')

from typing import List, Dict, Optional
from selectors.base import BaseSelector
from selectors.config import selector_config
from core.market_data import MarketDataAPI
from core.db_helper import DBHelper
from config import config

import time


class VolumeSelector(BaseSelector):
    """
    거래량 급증 종목 선정

    선정 기준:
    1. 당일 거래량이 20일 평균 대비 N배 이상
    2. 가격 상승 중 (전일 대비 +1% 이상)
    3. 거래대금 필터링
    """

    def __init__(self, config_dict: Optional[Dict] = None):
        super().__init__(config_dict)

        # Selector 환경 변수에서 설정 로드
        self.volume_ratio = selector_config.VOLUME_RATIO
        self.min_price_change = selector_config.VOLUME_MIN_PRICE_CHANGE
        self.min_trade_amount = selector_config.VOLUME_MIN_TRADE_AMOUNT
        self.ma_period = selector_config.VOLUME_MA_PERIOD
        self.lookback_days = selector_config.VOLUME_LOOKBACK_DAYS

        # API 초기화
        self.market_api = MarketDataAPI(
            config.APP_KEY,
            config.APP_SECRET,
            config.ACCOUNT_NO,
            config.IS_PAPER_TRADING
        )
        self.db = DBHelper()

    def select_stocks(self, select_count: int = 5) -> List[str]:
        """
        거래량 급증 종목 선정 (일봉 기반)

        Args:
            select_count: 선정할 종목 수

        Returns:
            선정된 종목 코드 리스트
        """
        print(f"[{self.name}] 종목 선정 시작...")
        print(f"  - 거래량 배수: {self.volume_ratio}배")
        print(f"  - 최소 상승률: +{self.min_price_change}%")
        print(f"  - 최소 거래대금: {self.min_trade_amount:,}원")
        print(f"  - 평균 기간: {self.ma_period}일")

        try:
            # 1. DB에서 전체 종목 목록 조회 (코스피, 코스닥)
            stock_list = self._get_stock_list()
            print(f"  - 전체 종목 수: {len(stock_list)}개")

            # 2. 각 종목의 거래량 분석
            candidates = []
            for i, stock_code in enumerate(stock_list):
                if i % 10 == 0:  # 10개마다 진행상황 출력
                    print(f"  - 진행: {i}/{len(stock_list)} ({i/len(stock_list)*100:.1f}%)")

                result = self._analyze_volume(stock_code)
                time.sleep(0.2)
                if result:
                    candidates.append(result)

            # 3. 거래량 증가율로 정렬
            candidates.sort(key=lambda x: x['volume_ratio'], reverse=True)

            # 4. 상위 N개 선정
            selected = [c['stock_code'] for c in candidates[:select_count]]

            # 선정 결과 출력
            print(f"\n  ✅ {len(selected)}개 종목 선정 완료")
            for i, candidate in enumerate(candidates[:select_count], 1):
                print(f"    {i}. {candidate['stock_code']}: "
                      f"거래량 {candidate['volume_ratio']:.1f}배, "
                      f"가격 변동 {candidate['price_change']:+.2f}%")

            return selected

        except Exception as e:
            print(f"  ❌ 종목 선정 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            # 에러 발생 시 더미 데이터 반환
            return ['005930', '000660', '035720'][:select_count]

    def _get_stock_list(self) -> List[str]:
        """
        DB에서 거래 가능한 종목 목록 조회

        Returns:
            종목 코드 리스트
        """
        try:
            # stocks 테이블에서 코스피/코스닥 종목 조회
            query = """
                SELECT stock_code
                FROM stocks
                WHERE market IN ('KOSPI', 'KOSDAQ')
                AND stock_code NOT LIKE '%%ETF%%'
                ORDER BY RANDOM()
                LIMIT 300
            """
            result = self.db.execute_query(query)

            return [row['stock_code'] for row in result] if result else []
        except Exception as e:
            print(f"  ⚠️ 종목 목록 조회 실패: {str(e)}")
            # 에러 시 주요 종목 반환
            return ['005930', '000660']

    def _analyze_volume(self, stock_code: str) -> Optional[Dict]:
        """
        종목의 거래량 분석

        Args:
            stock_code: 종목 코드

        Returns:
            분석 결과 딕셔너리 또는 None (조건 미충족 시)
        """
        try:
            # 일봉 데이터 조회 (최근 N일)
            daily_data = self.market_api.get_daily_price(stock_code, period="D")

            if not daily_data or len(daily_data) < self.ma_period + 1:
                return None

            # 최신 데이터 (당일)
            today = daily_data[0]
            today_volume = today['volume']
            today_close = today['close']

            # 전일 종가
            yesterday_close = daily_data[1]['close']

            # 가격 변동률 계산
            price_change = ((today_close - yesterday_close) / yesterday_close) * 100

            # 가격 상승 필터링
            if price_change < self.min_price_change:
                return None

            # 평균 거래량 계산 (최근 N일, 당일 제외)
            avg_volume = sum(d['volume'] for d in daily_data[1:self.ma_period+1]) / self.ma_period

            if avg_volume == 0:
                return None

            # 거래량 배수 계산
            volume_ratio = today_volume / avg_volume

            # 거래량 배수 필터링
            if volume_ratio < self.volume_ratio:
                return None

            # 거래대금 계산 (당일 거래량 * 종가)
            trade_amount = today_volume * today_close

            # 거래대금 필터링
            if trade_amount < self.min_trade_amount:
                return None

            return {
                'stock_code': stock_code,
                'volume_ratio': volume_ratio,
                'price_change': price_change,
                'trade_amount': trade_amount,
                'today_volume': today_volume,
                'avg_volume': avg_volume
            }

        except Exception as e:
            # 개별 종목 조회 실패는 무시
            return None
