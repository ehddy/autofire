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
        self.user = os.getenv("DB_USER", "postgres")
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
