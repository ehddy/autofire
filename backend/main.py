"""
AutoFIRE Backend API
FastAPI 기반 백엔드 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AutoFIRE API",
    description="한국투자증권 API 기반 자동 매매 시스템 백엔드",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """
    루트 엔드포인트
    """
    return {
        "message": "AutoFIRE API Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "healthy"}

@app.get("/api/v1/account/summary")
def get_account_summary():
    """
    계좌 요약 정보 조회
    """
    # TODO: 실제 DB 조회 로직 구현
    return {
        "total_assets": 10000000,
        "cash_balance": 5000000,
        "stock_value": 5000000,
        "profit_loss": 0,
        "profit_rate": 0.0
    }

@app.get("/api/v1/stocks/selected")
def get_selected_stocks():
    """
    금일 선정 종목 조회
    """
    # TODO: 실제 DB 조회 로직 구현
    return {
        "date": "2026-03-08",
        "stocks": []
    }
