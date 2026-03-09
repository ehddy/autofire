"""
AutoFIRE Backend API
FastAPI 기반 백엔드 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# API 라우터 import
from api.v1 import account, trading, stocks, live

app = FastAPI(
    title="AutoFIRE API",
    description="한국투자증권 API 기반 자동 매매 시스템 백엔드",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(account.router, prefix="/api/v1/account", tags=["계좌 (DB)"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["거래 (DB)"])
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["종목 (DB)"])
app.include_router(live.router, prefix="/api/v1/live", tags=["실시간 (KIS API)"])


@app.get("/", tags=["기본"])
def root():
    """
    루트 엔드포인트
    """
    return {
        "message": "AutoFIRE API Server",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["기본"])
def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행
    """
    print("🚀 AutoFIRE Backend API 시작...")
    print("📚 API 문서: http://localhost:8000/docs")
    print("💡 Bot의 core 모듈을 공유하여 실시간 데이터 제공")


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행
    """
    print("👋 AutoFIRE Backend API 종료...")
