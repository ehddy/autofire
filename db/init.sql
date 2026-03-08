-- AutoFIRE Database Schema
-- 한국투자증권 API 기반 자동 매매 시스템

-- 1. 종목 정보 테이블
CREATE TABLE IF NOT EXISTS stocks (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    market VARCHAR(10),  -- KOSPI, KOSDAQ
    sector VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 거래 이력 테이블
CREATE TABLE IF NOT EXISTS trade_history (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    order_type VARCHAR(10) NOT NULL,  -- BUY, SELL
    order_price DECIMAL(15, 2),
    order_quantity INT,
    executed_price DECIMAL(15, 2),
    executed_quantity INT,
    executed_at TIMESTAMP,
    strategy_name VARCHAR(50),
    profit_loss DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code) ON DELETE CASCADE
);

-- 3. 일별 선정 종목 테이블
CREATE TABLE IF NOT EXISTS daily_selected_stocks (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    selected_date DATE NOT NULL,
    strategy_name VARCHAR(50),
    selection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code) ON DELETE CASCADE,
    UNIQUE(stock_code, selected_date, strategy_name)
);

-- 4. 계좌 스냅샷 테이블
CREATE TABLE IF NOT EXISTS account_snapshots (
    id SERIAL PRIMARY KEY,
    total_assets DECIMAL(15, 2),
    cash_balance DECIMAL(15, 2),
    stock_value DECIMAL(15, 2),
    profit_loss DECIMAL(15, 2),
    profit_rate DECIMAL(5, 2),
    snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 현재 보유 종목 테이블
CREATE TABLE IF NOT EXISTS holdings (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    avg_buy_price DECIMAL(15, 2),
    current_price DECIMAL(15, 2),
    profit_loss DECIMAL(15, 2),
    profit_rate DECIMAL(5, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code) ON DELETE CASCADE
);

-- 6. 시스템 로그 테이블
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(10),  -- INFO, WARNING, ERROR
    message TEXT,
    module VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. API 토큰 관리 테이블
CREATE TABLE IF NOT EXISTS api_tokens (
    id SERIAL PRIMARY KEY,
    token_type VARCHAR(20) NOT NULL,  -- 'access_token'
    token_value TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_virtual BOOLEAN NOT NULL DEFAULT true,  -- 모의투자/실전투자 구분
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_trade_history_stock_code ON trade_history(stock_code);
CREATE INDEX idx_trade_history_executed_at ON trade_history(executed_at);
CREATE INDEX idx_daily_selected_stocks_date ON daily_selected_stocks(selected_date);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_system_logs_level ON system_logs(log_level);
CREATE INDEX idx_api_tokens_type_virtual ON api_tokens(token_type, is_virtual);

-- 종목 정보는 stocks_data.sql에서 자동으로 로드됩니다
-- (3,115개 KOSPI/KOSDAQ 종목)
