# AutoFIRE: Path to Financial Freedom

**한국투자증권 API 기반의 지능형 자동 매매 및 통합 모니터링 시스템**

한국투자증권 API를 활용한 국내 주식 자동 매매 및 실시간 모니터링 시스템입니다. 사용자가 정의한 전략에 따라 종목을 선정하고, 실시간 주가 분석을 통해 매수/매도를 수행하며 웹 대시보드를 통해 현황을 파악할 수 있습니다.

---

## 목차

1. [개요](https://www.notion.so/README-md-31d8970381108076a634c72b66d23bbc?pvs=21)
2. [시작하기](https://www.notion.so/README-md-31d8970381108076a634c72b66d23bbc?pvs=21)
3. [기술 스택](https://www.notion.so/README-md-31d8970381108076a634c72b66d23bbc?pvs=21)
4. [시스템 아키텍처](https://www.notion.so/README-md-31d8970381108076a634c72b66d23bbc?pvs=21)
5. [전략 및 종목 선정 가이드](https://www.notion.so/README-md-31d8970381108076a634c72b66d23bbc?pvs=21)
6. [매매 규칙](https://www.notion.so/README-md-31d8970381108076a634c72b66d23bbc?pvs=21)

---

## 실행 방법

### 1. 레포지토리 클론

```bash
git clone https://github.com/ehddy/autofire.git
cd autofire
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 KIS API 키 및 계좌 정보를 입력합니다.

### 3. 초기 종목 데이터 세팅

한국투자증권 API 가이드에서 `kospi_code.mst`, `kosdaq_code.mst` 파일을 다운로드한 뒤 `api_docs/종목정보/`에 배치합니다.

```bash
cd db && python parse_mst.py  # stocks_data.sql 생성
cd ..
```

### 4. Docker Compose 실행

```bash
docker-compose up -d
```

### 5. 서비스 접속

| 서비스             | 주소                                            |
| ------------------ | ----------------------------------------------- |
| Frontend Dashboard | [http://localhost:3000](http://localhost:3000/) |
| Backend API        | [http://localhost:8000](http://localhost:8000/) |
| API Docs (Swagger) | http://localhost:8000/docs                      |

### 기타 명령어

```bash
# 로그 확인
docker-compose logs -f bot
docker-compose logs -f backend

# 개별 컨테이너 재시작
docker-compose restart bot
docker-compose restart backend

# 전체 중지
docker-compose down

# 데이터 초기화 (볼륨 삭제)
docker-compose down -v && docker-compose up -d
```

---

## Tech Stack

| **Category**       | **Technology**                        |
| ------------------ | ------------------------------------- |
| **Backend**        | Python, FastAPI                       |
| **Frontend**       | Vue.js                                |
| **Database**       | PostgreSQL / MySQL (Docker Container) |
| **Infrastructure** | Docker, Docker Compose                |
| **Notification**   | Discord Webhook                       |
| **API**            | 한국투자증권 Open API                 |

---

## Key Features

### 1. 자동 매매 및 전략 시스템 (Modular Strategy)

- **Daily Selection**: 매일 장 시작 전, 특정 조건에 따라 N개의 대상 종목을 자동 선정합니다.
- **Real-time Monitoring**: 선정된 종목의 주가를 분 단위로 수집하여 상태를 추적합니다.
- **Pluggable Policy**: 매수/매도 로직과 종목 선정 로직이 **인터페이스화(Interface)** 되어 있어, 새로운 전략을 모듈 형태로 손쉽게 추가하거나 교체할 수 있습니다.
- **Smart Asset Allocation:** 선정된 종목들에 대해 가용한 자산을 전략적으로 배분합니다. 동일 비중(Equal Weight) 배분뿐만 아니라, 종목별 확신도나 리스크 지표에 따라 **사용자가 직접 정의한 차등 가중치 배분 정책**을 지원합니다.
- **Multi-Strategy Pipeline**: 하나 이상의 매매 정책을 동시에 활성화할 수 있습니다. 각 전략별로 자산을 배분하거나, 여러 전략의 공통 신호를 포착하는 앙상블 매매가 가능합니다.
- **Configurable Limits**: 사용자 설정을 통해 최대 투자 비율, 익절/손절 기준, 일일 손실 한도 등을 자유롭게 조절합니다.

### 2. 실시간 모니터링 대시보드

- **Direct Market Access**: 백엔드가 공유된 `core` 모듈을 통해 한투 API에 직접 접근하므로, DB 동기화 지연 없이 실시간 계좌 및 시세 정보를 조회합니다.
- **Account Summary**: 내 계좌의 실시간 예수금, 총 자산, 수익률을 한눈에 확인합니다.
- **Trading History**: 과거 매매 이력 및 체결 내역을 시각화하여 제공합니다.

### 3. 알림 서비스

- **Discord Integration**: 종목 선정 완료, 매수/매도 체결 알림, 시스템 오류 등 모든 과정을 실시간으로 디스코드 채널에 전송합니다.

---

## System Architecture (Dockerized)

![image.png](attachment:d4e36251-4981-438b-93ec-6f35a79de3f2:image.png)

```jsx
[ User (Web Browser) ]
                │
                ▼
      [ Frontend (Vue.js) ]
                │
                │ (REST API)
                ▼
      [ Backend (FastAPI) ] ──────┐
                │                 │
                │          ┌──────┴──────┐
                ▼          │ Shared Core │──────▶ [ KIS API ]
      [ Database (Postgres)]│ (bot/core)  │
                ▲          └──────┬──────┘
                │                 │
                │          ┌──────┘
      [ Trading Bot (Python) ] ──────────────────▶ [ Discord ]
```

AutoFIRE는 4개의 독립된 컨테이너가 유기적으로 동작하며, 특히 백엔드와 봇이 핵심 로직을 공유하는 효율적인 구조를 가집니다.

- **Frontend**: Vue.js 기반의 사용자 대시보드 및 설정 인터페이스를 제공합니다.
- **Backend**: FastAPI를 사용하여 DB 데이터를 관리하고, `core` 모듈을 통해 실시간 API 요청을 처리합니다.
- **Bot**: 실시간 시세 수집, 전략 기반 매매 실행 및 디스코드 알림을 담당하는 핵심 엔진입니다.
- **Database**: PostgreSQL을 사용하여 거래 이력, 종목 정보 및 API 접근 토큰을 저장합니다.

| **컨테이너 명** | **기술 스택** | **설명**                                        |
| --------------- | ------------- | ----------------------------------------------- |
| **Frontend**    | Vue.js        | 대시보드 UI 및 사용자 설정 화면                 |
| **Backend**     | FastAPI       | DB 데이터 중계 및 외부 통신 관리 API            |
| **Bot**         | Python        | 실시간 시세 수집, 매매 로직 수행, 디스코드 알림 |
| **DB**          | DB Engine     | 거래 이력, 종목 정보, 계좌 정보 저장            |

---

## Project Structure

전체 프로젝트는 서비스별로 모듈화되어 있으며, 각 컨테이너는 독립적인 `Dockerfile`을 가집니다.

```jsx

├── docker-compose.yaml         # 서비스 전체 오케스트레이션 정의
├── .env                        # API Key, DB 접속 정보 등 환경 변수 (Git 제외)
├── .gitignore                  # Git 추적 제외 설정
├── README.md                   # 프로젝트 메인 설명 문서
│
├── bot/                        # [Container 1] Trading Bot Engine
│   ├── Dockerfile              # Python 기반 봇 이미지 빌드
│   ├── main.py                 # 봇 실행 진입점 (Entry Point)
│   ├── core/                   # 한국투자증권 API 연동 및 공통 모듈 (Shared)
│   ├── selectors/              # 종목 선정 정책 (확장 가능) [Step 1]
│   │   ├── base.py             # 종목 선정 인터페이스 (Abstract Base Class)
│   │   └── custom_selector.py  # 종목 선정 전략 모듈
│   ├── portfolios/             # 자산 배분 정책 [Step 2]
│   │   ├── base.py             # 자산 배분 인터페이스 (ABC)
│   │   ├── equal_allocator.py  # 동일 비중 배분 (1/N)
│   │   └── weight_allocator.py # 가중치 기반 배분 모듈
│   ├── notifications/          # 디스코드 연동
│   ├── policies/               # 매매 실행 전략 (확장 가능)[Step 3]
│   │   ├── base.py             # 매매 전략 인터페이스 (Abstract Base Class)
│   │   └── rsi_strategy.py     # 매수/매도 정책 모듈

│   └── requirements.txt        # 봇 관련 패키지 목록
│
├── backend/                    # [Container 2] FastAPI Server
│   ├── Dockerfile              # FastAPI 이미지 빌드
│   ├── main.py                 # API 서버 실행 진입점 (bot/core 공유 사용)
│   ├── api/                    # 엔드포인트 라우팅 (V1, V2 등)
│   ├── models/                 # SQLAlchemy/Tortoise DB 모델 정의
│   ├── schemas/                # Pydantic 데이터 검증 스키마
│   └── requirements.txt        # 백엔드 관련 패키지 목록
│
├── frontend/                   # [Container 3] Vue.js Web UI
│   ├── Dockerfile              # Nginx 기반 프론트엔드 이미지 빌드
│   ├── package.json            # Node.js 패키지 및 스크립트
│   ├── public/                 # 정적 리소스
│   └── src/                    # Vue 컴포넌트 및 로직
│       ├── views/              # 대시보드, 설정 페이지 등
│       └── components/         # 재사용 가능한 UI 컴포넌트
│
├── db/                         # [Container 4] Database Configuration
│   ├── init.sql                # 초기 테이블 스키마 및 기초 데이터 스크립트
│   └── my.cnf                  # DB 엔진 설정 파일
│
└── api_docs/                   # KIS API 관련 레퍼런스 문서 모음
```

- **`docker-compose.yaml`**: 4개의 서비스(frontend, backend, bot, db) 간의 네트워크 연결 및 볼륨 마운트, 환경 변수 주입을 총괄합니다.
- **`.env`**: `APP_KEY`, `APP_SECRET`, `DB_PASSWORD` 등 보안이 중요한 정보는 이 파일에서 통합 관리하며, **Dockerfile 내부로 직접 하드코딩하지 않습니다.**
- **`bot/selectors/` (Selection Policy)**:
  이 프로젝트의 **종목 유니버스 구성을 담당**하는 폴더입니다. `BaseSelector` 클래스를 상속받아 새로운 `.py` 파일을 만드는 것만으로 당일 거래할 종목을 고르는 알고리즘(예: 거래량 상위, 특정 지표 돌파 등)을 무한히 확장할 수 있습니다.
- **`bot/portfolios/`** **(Portfolio Strategy):**
  이 프로젝트의 **자산 배분(Asset Allocation)**을 담당하는 폴더입니다. `BasePortfolio` 클래스를 상속받아 선정된 종목들에 예산을 어떻게 나눌지 결정하는 로직을 구현합니다. (예: N분의 1로 나누는 동일 비중 배분, 수익률 확신도에 따른 차등 배분 등) 단순히 "무엇을 사느냐"를 넘어 "얼마나 사느냐"를 전략적으로 관리하여 계좌의 리스크를 제어합니다.
- **`bot/policies/` (Trading Strategy)**:
  이 프로젝트의 **실전 매매 타이밍을 담당**하는 폴더입니다. `BaseStrategy` 클래스를 상속받아 실시간 주가 분석을 통한 매수/매도 시그널 결정 로직(예: RSI, 이동평균선 등)을 개별 모듈로 추가하여 운용할 수 있습니다.
- **`db/init.sql`**: 컨테이너가 처음 실행될 때 종목 정보, 거래 이력 테이블을 자동으로 생성하여 초기 세팅 번거로움을 최소화합니다.
- **`bot/core/`**: [Shared Core Module] 한국투자증권 API 연동(인증, 시세, 주문, 계좌)을 담당하는 시스템의 핵심 엔진입니다. `bot`과 `backend` 컨테이너가 이 폴더를 공유함으로써 코드 중복을 방지하고, 웹 대시보드에서 지연 없는 실시간 데이터 조회를 가능하게 합니다.

---

## **포트폴리오 전략(Portfolio) 추가 가이드**

본 시스템은 선정된 종목들에 대해 가용한 자산을 어떻게 배분할지 결정하는 포트폴리오 레이어를 제공합니다.

### **1. 새로운 배분 정책 파일 생성**

`bot/portfolios/` 디렉토리에 파이썬 파일을 생성합니다. (예: `risk_allocator.py`)

### **2. Base 클래스 상속 및 메서드 구현**

`BasePortfolio` 클래스를 상속받아 `allocate` 메서드를 구현합니다.

```python
from .base import BasePortfolio

class CustomWeightAllocator(BasePortfolio):
    def allocate(self, selected_stocks: list, total_budget: float) -> dict:
        """
        [자산 배분 로직]
        - selected_stocks: Selector에 의해 선정된 종목 리스트
        - total_budget: 매수 가능한 총 예산 (예: 1억)
        - Returns: { "종목코드": 배분금액 } 형태의 딕셔너리
        """
        # 예: 종목당 동일하게 배분하거나, 특정 지표에 따라 가중치 부여
        share = total_budget / len(selected_stocks)
        return {code: share for code in selected_stocks}
```

### **3. 정책 활성화**

`.env` 파일에서 사용할 포트폴리오 전략을 지정합니다.

```python
PORTFOLIO_STRATEGY=EqualWeightAllocator
```

---

## 전략(Strategy) 추가 가이드

본 시스템은 전략 패턴(Strategy Pattern)을 기반으로 설계되어, 새로운 종목 선정 및 매매 로직을 손쉽게 확장할 수 있습니다.

본 시스템은 다중 전략 운용을 지원합니다. 사용자는 독립적인 전략들을 생성하고, 이를 조합하여 최적의 매매 타이밍을 잡을 수 있습니다.

### 1. 새로운 정책 파일 생성

`bot/policies/` 디렉토리 내에 새로운 파이썬 파일을 생성합니다. (예: `rsi_strategy.py`)

### 2. Base 클래스 상속 및 메서드 구현

`BaseStrategy` 클래스를 상속받아 아래의 필수 메서드들을 오버라이딩합니다.

```jsx
from .base import BaseStrategy

class RSICustomStrategy(BaseStrategy):
    def check_signal(self, stock_code: str, market_data: dict) -> str:
        """
        [매수/매도 시그널 체크]
        분 단위로 수집되는 데이터를 바탕으로 매매 여부를 결정합니다.
        - Returns: 'BUY', 'SELL', or 'HOLD'
        """
        # 매매 조건 로직 구현 (예: RSI 지표 분석)
        # 선정된 종목(stock_code)에 대한 시그널만 판단합니다.
        return "BUY"
```

### 3. 전략 활성화

작성한 전략을 시스템에 적용하려면 `bot/main.py` 또는 환경 설정(`.env`)에서 활성화할 전략의 클래스명을 지정합니다.

```jsx
# .env 예시
# 활성화할 전략 목록 (쉼표로 구분)
ACTIVE_STRATEGIES=RSI_Strategy,BollingerBand_Strategy
```

### 4. 전략 모드 (STRATEGY_MODE)

여러 개의 매매 전략을 활성화한 경우, BUY 시그널을 조합하는 방식을 선택할 수 있습니다:

```bash
# .env 예시
ACTIVE_STRATEGIES=RSI_Strategy,BollingerBand_Strategy,MACD_Strategy
STRATEGY_MODE=OR  # OR 또는 AND
```

**OR 모드 (기본값, 하나라도 ∪)**
- 하나의 전략이라도 BUY 시그널을 보내면 매수
- 예: RSI → BUY, BollingerBand → HOLD, MACD → HOLD
- 결과: 매수 실행 (1개라도 BUY)
- 용도: 공격적 진입, 기회 확대

**AND 모드 (모두 일치 ∩)**
- 모든 전략이 BUY 시그널을 보내야 매수
- 예: RSI → BUY, BollingerBand → BUY, MACD → HOLD
- 결과: 매수 보류 (3개 중 2개만 BUY)
- 용도: 보수적 진입, 확신도 높은 종목만 매수

**중요: SELL 시그널도 동일하게 적용**
- OR 모드: 하나의 전략이라도 SELL → 매도
- AND 모드: 모든 전략이 SELL → 매도
- 단, **RiskManagement (익절/손절)은 항상 최우선**으로 STRATEGY_MODE와 무관하게 즉시 매도

---

## 종목 선정(Selection) 추가 가이드

본 시스템은 매일 거래할 대상 종목을 추출하는 로직을 매매 전략과 분리하여 관리합니다. `BaseSelector` 클래스를 상속받아 새로운 종목 선정 알고리즘을 손쉽게 추가할 수 있습니다.

### **1. 종목 선정 파일 생성**

`bot/selectors/` 디렉토리 내에 새로운 파이썬 파일을 생성합니다. (예: `volume_selector.py`)

### **2. Base 클래스 상속 및 메서드 구현**

`BaseSelector` 클래스를 상속받아 `select_stocks` 메서드를 오버라이딩합니다.

```jsx
from .base import BaseSelector

class MyCustomSelector(BaseSelector):
    def select_stocks(self) -> list:
        """
        [종목 선정 로직]
        매일 장 시작 전(SELECTION_TIME) 호출되며,
        당일 거래 대상 종목 리스트를 반환합니다.
        """
        # 로직 구현 (예: 거래량 급증 종목 추출)
        selected_codes = ["005930", "000660"]
        return selected_codes
```

### **3. 정책 활성화**

작성한 선정 정책을 적용하려면 .env 파일의 SELECTION_POLICIES 항목에 클래스명을 지정합니다.

### **4. 선정 모드 (SELECTION_MODE)**

여러 개의 Selector를 활성화한 경우, 결과를 조합하는 방식을 선택할 수 있습니다:

```bash
# .env 예시
SELECTION_POLICIES=TechnicalSelector,VolumeSelector
SELECTION_MODE=OR  # OR 또는 AND
```

**OR 모드 (기본값, 합집합 ∪)**
- 하나의 Selector라도 선정한 종목을 포함
- 예: TechnicalSelector가 [A, B, C], VolumeSelector가 [C, D, E] 선정
- 결과: [A, B, C, D, E] (최대 SELECT_COUNT개)
- 용도: 다양한 관점의 종목을 포함하여 기회 확대

**AND 모드 (교집합 ∩)**
- 모든 Selector에서 선정된 종목만 포함
- 예: TechnicalSelector가 [A, B, C], VolumeSelector가 [C, D, E] 선정
- 결과: [C] (공통 종목만)
- 용도: 여러 전략의 확신이 겹치는 종목만 선정하여 리스크 감소

---

## 전략 설계 가이드

본 시스템은 **Selectors(종목 선정)**, **Portfolios(자산 배분)**, **Policies(매매 실행)**의 3단계 레이어가 독립적으로 설계되어, 사용자의 투자 목적에 따라 다양한 전략 조합이 가능합니다.

`selectors/`와 `policies/`는 독립적으로 설계되어 다양한 전략을 자유롭게 조합할 수 있습니다.

전략 구현 방식 중 하나로 **MTF(Multi-Time Frame)** 방식을 활용할 수 있습니다.
일봉으로 종목의 방향성을 먼저 필터링하고, 분봉으로 진입 타이밍을 잡는 방식입니다.

```
selectors/                 portfolios/                policies/
───────────────────        ───────────────────        ───────────────────
[What to Buy]              [How Much to Buy]          [When to Buy]
일봉 기준 종목 필터링  ▶    자산 배분 및 투자 비중  ▶    분봉 기준 실시간 진입
"오늘의 공략 종목군"        "종목별 투입 예산 결정"      "최적의 매매 타이밍"
```

### MTF 전략 예시

아래는 MTF 방식 적용 예시입니다. 실제 구현 전략은 자유롭게 설계할 수 있습니다.

```
RSI 전략 예시
  selector: 일봉 RSI 40~60 사이 종목만 선정
  policy:   분봉 RSI 30 이하 → BUY / 70 이상 → SELL

거래량 전략 예시
  selector: 전일 대비 거래량 상위 N종목 선정
  policy:   분봉 거래량 평균 2배 이상 + 가격 상승 → BUY
```

### Selector / Policy 독립 조합

`selector`와 `policy`는 독립적으로 조합할 수 있습니다.
예를 들어 거래량으로 종목을 선정하고, RSI + MACD 앙상블로 타이밍을 잡을 수 있습니다.

```bash
# .env 예시
SELECTION_POLICIES=VolumeSurgeSelector
ACTIVE_STRATEGIES=RSI_Policy,MACD_Policy
```

복수의 전략이 활성화된 경우 앙상블 조건을 적용합니다.

```
모든 전략이 BUY  → 매수 실행
하나라도 SELL    → 매도 실행
그 외            → HOLD
```

### 파일 구조

```
bot/
├── selectors/
│   ├── base.py                  # 종목 선정 인터페이스 (ABC)
│   └── {strategy}_selector.py  # 전략별 일봉 필터 구현체
│
└── policies/
    ├── base.py                  # 매매 전략 인터페이스 (ABC)
    └── {strategy}_policy.py    # 전략별 분봉 매매 구현체
```

---

## Trading Bot Engine 상세

AutoFIRE의 봇 엔진은 24시간 상주하며 사용자가 설정한 스케줄에 따라 종목 선정, 실시간 매매, 결과 리포팅을 자율적으로 수행합니다.

### 1. 핵심 아키텍처: Shared Core Pattern

봇 내부에 위치한 `core/` 모듈은 시스템의 핵심 엔진으로, 봇과 백엔드가 이를 공유하여 효율성을 극대화합니다.

- **코드 중복 방지**: 인증, 시세 조회, 주문 로직을 하나의 모듈에서 관리합니다.
- **토큰 공유**: `api_tokens` 테이블을 통해 발급받은 OAuth 토큰을 봇과 백엔드가 공유하여 중복 인증 및 API 호출 낭비를 방지합니다.
- **실시간성 보장**: 백엔드 API가 이 모듈을 직접 호출함으로써 DB 지연 없는 실시간 계좌 조회가 가능합니다.

### 2. 자율 운영 라이프사이클 (Sequential Scheduling)

봇은 파이썬 `schedule` 라이브러리를 활용하여 안정적인 순차적 작업 흐름을 유지합니다.

| **단계**          | **시간 (설정 가능)**  | **주요 작업 및 프로세스**                                                                 |
| ----------------- | --------------------- | ----------------------------------------------------------------------------------------- |
| **종목 선정**     | `SELECTION_TIME`      | 활성화된 **Selection Policy**를 구동하여 당일 거래 대상 종목 유니버스 구축 및 DB 저장     |
| **자산 배분**     | `SELECTION_TIME` 직후 | 선정된 종목들에 대해 **Portfolio Strategy**를 적용하여 종목별 투자 비중 및 가용 예산 확정 |
| **실시간 매매**   | 09:00 ~ 15:30         | 1분 단위 루프: 현재가 모니터링 → 전략 신호 체크(`check_signal`) → 주문 실행               |
| **데일리 리포트** | `REPORT_TIME`         | 장 마감 후 당일 매매 결산, 수익률 집계 및 계좌 현황 요약 리포트 전송                      |

### 3. 전략 및 선정 정책의 확장성 (Modular Strategy)

종목 선정과 매매 전략은 모두 모듈화되어 있어 필요에 따라 자유롭게 교체 및 조합이 가능합니다.

- **Modular Selection**: **BaseSelector** 인터페이스를 상속받아 기술적 지표, 재무 지표 등 다양한 종목 선정 로직을 독립적으로 추가할 수 있습니다
- **Multi-Strategy Pipeline**: 하나 이상의 전략을 동시에 활성화하여 전략 간 앙상블 매매나 자산 배분 기능을 수행합니다.
- **State Persistence**: 선정된 종목 정보는 DB(`daily_selected_stocks`)에 보존되어 시스템 재시작 시에도 매매 흐름을 즉시 복구합니다.

### 4. 운영 안정성

- **24/7 상주 프로세스**: 유휴 시간 동안 최소한의 리소스를 사용하며 상시 가동됩니다.
- **순차 실행 방식**: API 호출 제한(Rate Limit)과 데이터 일관성을 고려하여 모든 스케줄된 작업을 안정적으로 순차 처리합니다.
- **실시간 알림**: 모든 핵심 이벤트(선정 완료, 매매 체결, 시스템 에러)는 즉시 디스코드로 전송됩니다.

---

## 매매 규칙 가이드

AutoFIRE의 기본 매매 규칙을 정의합니다.
새로운 전략(`bot/policies/`)을 구현할 때 반드시 이 규칙을 준수해야 합니다.

### 1. 포지션 규칙

- **자산 배분 우선:** 매수 시 시그널뿐만 아니라 `Portfolio Strategy`에서 할당된 종목별 예산을 초과하여 매수하지 않습니다.
- **One-shot 일괄 매수**: BUY 시그널 발생 시 해당 종목 예산 전액을 한 번에 매수합니다.
- **중복 진입 금지**: 이미 보유 중인 종목에 BUY 시그널이 재발생해도 추가 매수하지 않습니다.
- **종목당 투자 한도**: 전체 투자금의 최대 **N%** 를 단일 종목에 배분합니다. (`.env`의 `MAX_POSITION_RATIO`로 설정)

### 2. 매수 규칙

- **주문 방식**: 지정가 매수
- **주문 가격**: 최우선 매도호가 + 1~2틱 (틱 사이즈는 주가 구간에 따라 자동 계산)
- **관망 구간**: 장 시작 직후 09:00 ~ 09:10은 매수하지 않습니다.
- **미체결 타임아웃**: 주문 후 30초 내 미체결 시 주문을 취소하고 해당 루프를 스킵합니다. 재주문은 다음 1분 루프에서 시그널을 재판단하여 결정합니다.

| 주가 구간           | 1틱     |
| ------------------- | ------- |
| 2,000원 미만        | 1원     |
| 2,000 ~ 5,000원     | 5원     |
| 5,000 ~ 20,000원    | 10원    |
| 20,000 ~ 50,000원   | 50원    |
| 50,000 ~ 200,000원  | 100원   |
| 200,000 ~ 500,000원 | 500원   |
| 500,000원 이상      | 1,000원 |

### 3. 매도 규칙

매도는 아래 조건 중 **가장 먼저 충족되는 조건**에 의해 실행됩니다.

| 조건                              | 기준                           | 주문 방식 | 역할          |
| --------------------------------- | ------------------------------ | --------- | ------------- |
| **전략 SELL 시그널**              | `check_signal()` → `SELL` 반환 | 지정가    | 능동적 청산   |
| **익절 (Take Profit)**            | 매수 체결가 대비 +3% 도달      | 지정가    | 수익 확정     |
| **손절 (Stop Loss)**              | 매수 체결가 대비 -2% 도달      | 지정가    | 최소 안전망   |
| **강제 청산 (Force Liquidation)** | 15:20 도달                     | 시장가    | 오버나잇 방지 |

- 전략 SELL 시그널은 익절/손절 구간 도달 전에 먼저 감지될 수 있어 손실을 줄이는 역할을 합니다.
- 익절/손절은 전략 시그널과 무관하게 항상 동작하는 최소 안전망입니다.
- 강제 청산은 위 조건에 걸리지 않은 모든 보유 종목을 대상으로 합니다. 당일 포지션은 반드시 당일 청산합니다.

```
예시:
매수가 10,000원 / 손절 라인 9,800원 (-2%)

→ 9,900원에서 전략 SELL 시그널 발생
→ 9,900원에 청산 (-1% 손실로 마감)   ← 전략 SELL이 손절보다 먼저 동작
```

봇 엔진 루프에서의 처리 순서는 다음과 같습니다.

```python
signal = strategy.check_signal(stock_code, market_data)

if is_holding(stock_code):
    if signal == "SELL" or hit_take_profit() or hit_stop_loss():
        execute_sell()  # 셋 중 하나라도 충족 시 청산
else:
    if signal == "BUY":
        execute_buy()
```

### 4. 리스크 관리

- **일일 최대 손실 한도 (Daily Stop)**: 당일 누적 손실이 전체 투자금의 **3%** 를 초과하면 당일 신규 매수를 중단합니다.

---

## Environment Variables

개인 정보 및 API 키는 절대 코드에 노출되지 않도록 `.env` 파일에서 관리합니다.
`.env.example`을 복사하여 `.env`를 생성한 뒤 값을 채워넣으세요.

```jsx
# KIS API 설정
APP_KEY=your_app_key
APP_SECRET=your_app_secret
ACCOUNT_NO=your_account_no

# 스케줄링 설정 (사용자 정의 시간)
SELECTION_TIME=08:30      # 종목 선정 시간 (HH:MM)
REPORT_TIME=16:00         # 마감 리포트 시간 (HH:MM)

# 전략 및 정책 활성화
ACTIVE_STRATEGIES=RSI_Strategy,BollingerBand_Strategy
STRATEGY_MODE=OR              # OR: 하나라도(∪), AND: 모두 일치(∩)
SELECTION_POLICIES=TechnicalSelectionPolicy,VolumeSelector
SELECTION_MODE=OR             # OR: 합집합(∪), AND: 교집합(∩)
PORTFOLIO_STRATEGY=EqualWeightAllocator  # 자산 배분 전략

# 매매 설정
MAX_POSITION_RATIO=0.2    # 종목당 최대 투자 비율 (전체 자산의 20%)
TAKE_PROFIT=0.03          # 익절 기준 (+3%)
STOP_LOSS=0.02            # 손절 기준 (-2%)
DAILY_STOP_LOSS=0.03      # 일일 최대 손실 한도 (-3%)
ORDER_TIMEOUT=30          # 미체결 타임아웃 (초)
FORCE_LIQUIDATION_TIME=15:20  # 강제 청산 시각
```

---

## 부록. MTF 전략 레퍼런스

MTF(Multi-Time Frame) 방식으로 구현 가능한 전략 예시입니다.
아래 전략들은 참고용이며, `selectors/`와 `policies/`를 자유롭게 조합하여 확장할 수 있습니다.

| 전략            | selector (일봉 필터)                   | policy (분봉 타이밍)                            |
| --------------- | -------------------------------------- | ----------------------------------------------- |
| **RSI**         | 일봉 RSI 40~60 사이 종목               | 분봉 RSI 30 이하 → BUY / 70 이상 → SELL         |
| **볼린저 밴드** | 일봉 밴드 수축 구간 종목               | 분봉 하단 터치 → BUY / 상단 터치 → SELL         |
| **MACD**        | 일봉 MACD 히스토그램 0선 위 종목       | 분봉 골든크로스 → BUY / 데드크로스 → SELL       |
| **거래량 서지** | 전일 대비 거래량 상위 N종목            | 분봉 거래량 평균 2배 이상 + 가격 상승 → BUY     |
| **모멘텀**      | 일봉 5일 연속 상승 or 52주 신고가 근처 | 분봉 전일 종가 대비 +2% 이상 + 거래량 3배 → BUY |
| **ORB**         | 일봉 변동성 높은 종목 (ATR 상위)       | 09:00~09:30 고저가 범위 설정 후 고가 돌파 → BUY |
| **눌림목**      | 일봉 5일선 > 20일선 상승 추세 종목     | 분봉 5일선까지 눌린 후 양봉 반등 → BUY          |
| **갭 + 모멘텀** | 전일 종가 대비 갭업 +2% 이상 종목      | 갭업 후 첫 눌림 반등 확인 → BUY                 |

---

## Disclaimer

- 본 프로그램은 투자 판단을 돕기 위한 보조 도구이며, **모든 투자에 대한 책임은 사용자 본인**에게 있습니다.
- 시스템 오류, 네트워크 장애 등으로 발생한 손실에 대해 제작자는 책임을 지지 않습니다.
