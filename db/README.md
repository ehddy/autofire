# 🗄️ AutoFIRE Database Guide

AutoFIRE 시스템의 데이터 구조 명세와 초기 종목 데이터 세팅을 위한 가이드입니다. 본 시스템은 **PostgreSQL 15**를 기반으로 설계되었습니다.

## 1. 데이터베이스 테이블 명세 (Schema)

`db/init.sql`에 정의된 주요 테이블들의 상세 구조입니다.

### 1.1 종목 정보 (`stocks`)

한국 시장의 상장 종목 기본 정보를 관리합니다.
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `stock_code` | VARCHAR(10) | PRIMARY KEY | 종목코드 (6자리) |
| `stock_name` | VARCHAR(100) | NOT NULL | 종목명 |
| `market` | VARCHAR(10) | - | 시장 구분 (KOSPI, KOSDAQ) |
| `sector` | VARCHAR(50) | - | 업종 정보 |
| `created_at` | TIMESTAMP | DEFAULT NOW() | 데이터 생성 일시 |

### 1.2 거래 이력 (`trade_history`)

봇에 의해 수행된 모든 매매 내역을 기록합니다.
| 컬럼명 | 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | SERIAL | PRIMARY KEY | 기록 고유 ID |
| `stock_code` | VARCHAR(10) | FK (stocks) | 종목코드 |
| `order_type` | VARCHAR(10) | NOT NULL | 주문 유형 (BUY, SELL) |
| `executed_price` | DECIMAL(15,2) | - | 실제 체결 가격 |
| `executed_quantity`| INT | - | 체결 수량 |
| `profit_loss` | DECIMAL(15,2) | - | 매매 손익액 |
| `strategy_name` | VARCHAR(50) | - | 적용된 전략 명칭 |
| `executed_at` | TIMESTAMP | - | 체결 시각 |

### 1.3 계좌 및 보유 현황 (`holdings`, `account_snapshots`)

실시간 잔고와 자산 변동 추이를 추적합니다.
| 테이블명 | 주요 컬럼 | 설명 |
| :--- | :--- | :--- |
| `holdings` | `quantity`, `avg_buy_price`, `profit_rate` | 현재 계좌 내 보유 종목 현황 |
| `account_snapshots` | `total_assets`, `cash_balance`, `profit_loss` | 일별/시간별 전체 자산 상태 기록 |

### 1.4 시스템 관리 (`api_tokens`, `system_logs`)

| 테이블명      | 주요 컬럼                                 | 설명                                  |
| :------------ | :---------------------------------------- | :------------------------------------ |
| `api_tokens`  | `token_value`, `expires_at`, `is_virtual` | KIS API OAuth 토큰 관리 (자동 갱신용) |
| `system_logs` | `log_level`, `message`, `module`          | 봇 동작 상태 및 에러 로그 기록        |

---

## 2. 초기 데이터 세팅 가이드 (MST 파싱)

시스템 가동 전, 한국투자증권에서 제공하는 마스터(`.mst`) 파일을 파싱하여 전체 종목 정보를 DB에 먼저 입력해야 합니다.

### 2.1 사전 준비

1.  한국투자증권 API 가이드에서 `kospi_code.mst`와 `kosdaq_code.mst` 파일을 다운로드합니다.
2.  파일을 `api_docs/종목정보/` 폴더 내에 배치합니다.

### 2.2 파싱 스크립트 실행

`db` 폴더 내에서 파싱 스크립트를 실행하여 SQL 데이터를 생성합니다.

```bash
# db 폴더로 이동
cd db

# MST 파일 파싱 및 stocks_data.sql 생성
python parse_mst.py
```

### 2.3 데이터 로드 원리

- `parse_mst.py` 실행 시 `db/stocks_data.sql` 파일이 생성됩니다.
- `docker-compose.yaml` 설정에 따라, 컨테이너 최초 실행 시 `init.sql`과 `stocks_data.sql`이 순차적으로 실행되어 DB가 초기화됩니다.

---

## 3. 관리 명령어

- **데이터 완전 초기화**: 볼륨을 삭제하고 다시 빌드합니다.
  ```bash
  docker-compose down -v
  docker-compose up -d
  ```
