"""
Database Helper 모듈
PostgreSQL 연결 및 쿼리 헬퍼
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class DBHelper:
    """
    PostgreSQL Database 헬퍼 클래스
    """

    def __init__(self):
        """
        환경 변수에서 DB 연결 정보 로드
        """
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", 5432))
        self.database = os.getenv("DB_NAME", "autofire")
        self.user = os.getenv("DB_USER", "autofire")
        self.password = os.getenv("DB_PASSWORD", "postgres")

        self.conn = None

    def connect(self):
        """
        데이터베이스 연결
        """
        try:
            if not self.conn or self.conn.closed:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                )
                logger.info(f"DB 연결 성공: {self.database}")
        except Exception as e:
            logger.error(f"DB 연결 실패: {str(e)}")
            raise

    def close(self):
        """
        데이터베이스 연결 종료
        """
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("DB 연결 종료")

    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """
        SELECT 쿼리 실행

        Args:
            query: SQL 쿼리
            params: 파라미터 튜플

        Returns:
            결과 리스트 (딕셔너리 형태)
        """
        self.connect()
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"쿼리 실행 실패: {str(e)}")
            logger.error(f"Query: {query}")
            return None

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        INSERT/UPDATE/DELETE 쿼리 실행

        Args:
            query: SQL 쿼리
            params: 파라미터 튜플

        Returns:
            영향받은 행 수
        """
        self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"쿼리 실행 실패: {str(e)}")
            logger.error(f"Query: {query}")
            return 0

    def __enter__(self):
        """
        Context manager 진입
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager 종료
        """
        self.close()

    # ===== 비즈니스 로직 메서드 =====

    def save_selected_stocks(
        self,
        stock_codes: List[str],
        strategy_name: str = "DefaultSelector",
        selection_reason: str = None
    ) -> bool:
        """
        금일 선정된 종목을 DB에 저장

        Args:
            stock_codes: 종목 코드 리스트
            strategy_name: 선정 전략명
            selection_reason: 선정 사유 (선택)

        Returns:
            성공 여부
        """
        if not stock_codes:
            logger.warning("저장할 종목이 없습니다.")
            return False

        self.connect()

        try:
            from datetime import date
            today = date.today()

            success_count = 0
            for stock_code in stock_codes:
                query = """
                    INSERT INTO daily_selected_stocks
                    (stock_code, selected_date, strategy_name, selection_reason)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (stock_code, selected_date, strategy_name)
                    DO UPDATE SET
                        selection_reason = EXCLUDED.selection_reason,
                        created_at = CURRENT_TIMESTAMP
                """
                params = (stock_code, today, strategy_name, selection_reason)

                affected = self.execute_update(query, params)
                if affected > 0:
                    success_count += 1

            logger.info(f"선정 종목 저장 완료: {success_count}/{len(stock_codes)}개")
            return success_count > 0

        except Exception as e:
            logger.error(f"선정 종목 저장 실패: {str(e)}")
            return False

    def save_account_snapshot(self, snapshot: Dict) -> bool:
        """
        계좌 스냅샷 저장

        Args:
            snapshot: 계좌 정보
                {
                    'total_assets': float,
                    'cash_balance': float,
                    'stock_value': float,
                    'profit_loss': float,
                    'profit_rate': float
                }

        Returns:
            성공 여부
        """
        self.connect()

        try:
            query = """
                INSERT INTO account_snapshots
                (total_assets, cash_balance, stock_value, profit_loss, profit_rate)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                snapshot.get('total_assets', 0),
                snapshot.get('cash_balance', 0),
                snapshot.get('stock_value', 0),
                snapshot.get('profit_loss', 0),
                snapshot.get('profit_rate', 0)
            )

            affected = self.execute_update(query, params)
            if affected > 0:
                logger.info("계좌 스냅샷 저장 완료")
                return True
            return False

        except Exception as e:
            logger.error(f"계좌 스냅샷 저장 실패: {str(e)}")
            return False

    def get_today_selected_stocks(self) -> List[Dict]:
        """
        금일 선정된 종목 조회

        Returns:
            선정 종목 리스트
        """
        from datetime import date
        today = date.today()

        query = """
            SELECT
                dss.stock_code,
                s.stock_name,
                dss.strategy_name,
                dss.selection_reason,
                dss.created_at
            FROM daily_selected_stocks dss
            LEFT JOIN stocks s ON dss.stock_code = s.stock_code
            WHERE dss.selected_date = %s
            ORDER BY dss.created_at DESC
        """

        return self.execute_query(query, (today,)) or []

    def save_trade(self, trade_data: Dict) -> bool:
        """
        거래 이력 저장

        Args:
            trade_data: 거래 정보
                {
                    'stock_code': str,
                    'order_type': str,  # 'BUY' or 'SELL'
                    'order_price': float,
                    'order_quantity': int,
                    'executed_price': float,
                    'executed_quantity': int,
                    'executed_at': datetime,
                    'strategy_name': str,
                    'profit_loss': float
                }

        Returns:
            성공 여부
        """
        self.connect()

        try:
            query = """
                INSERT INTO trade_history
                (stock_code, order_type, order_price, order_quantity,
                 executed_price, executed_quantity, executed_at,
                 strategy_name, profit_loss)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                trade_data.get('stock_code'),
                trade_data.get('order_type'),
                trade_data.get('order_price'),
                trade_data.get('order_quantity'),
                trade_data.get('executed_price'),
                trade_data.get('executed_quantity'),
                trade_data.get('executed_at'),
                trade_data.get('strategy_name'),
                trade_data.get('profit_loss', 0)
            )

            affected = self.execute_update(query, params)
            if affected > 0:
                logger.info(f"거래 이력 저장 완료: {trade_data.get('order_type')} {trade_data.get('stock_code')}")
                return True
            return False

        except Exception as e:
            logger.error(f"거래 이력 저장 실패: {str(e)}")
            return False

    def get_recent_trades(self, limit: int = 10) -> List[Dict]:
        """
        최근 거래 이력 조회

        Args:
            limit: 조회할 개수

        Returns:
            거래 이력 리스트
        """
        query = """
            SELECT
                th.*,
                s.stock_name
            FROM trade_history th
            LEFT JOIN stocks s ON th.stock_code = s.stock_code
            ORDER BY th.executed_at DESC
            LIMIT %s
        """

        return self.execute_query(query, (limit,)) or []

    def log_system_event(self, level: str, message: str, module: str = None) -> bool:
        """
        시스템 로그 저장

        Args:
            level: 로그 레벨 (INFO, WARNING, ERROR)
            message: 로그 메시지
            module: 모듈명

        Returns:
            성공 여부
        """
        self.connect()

        try:
            query = """
                INSERT INTO system_logs (log_level, message, module)
                VALUES (%s, %s, %s)
            """
            params = (level, message, module)

            affected = self.execute_update(query, params)
            return affected > 0

        except Exception as e:
            logger.error(f"시스템 로그 저장 실패: {str(e)}")
            return False
