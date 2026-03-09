# AutoFIRE: Path to Financial Freedom

**한국투자증권 API 기반의 지능형 자동 매매 및 통합 모니터링 시스템**

---

## 빠른 시작

### 1. 환경 설정

`.env` 파일을 수정하여 한국투자증권 API 키를 입력하세요:

```bash
# .env 파일 편집
APP_KEY=your_app_key_here
APP_SECRET=your_app_secret_here
ACCOUNT_NO=your_account_number_here
```

### 2. Docker Compose 실행

```bash
# 모든 컨테이너 빌드 및 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f bot
docker-compose logs -f backend
```

### 3. 서비스 접속

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### 4. 중지 및 삭제

```bash
# 컨테이너 중지
docker-compose stop

# 컨테이너 삭제
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v
```

---

## 프로젝트 구조

```
.
├── docker-compose.yaml         # 서비스 오케스트레이션
├── .env                        # 환경 변수 (Git 제외)
├── .env.example               # 환경 변수 템플릿
├── CLAUDE.md                  # 프로젝트 개요
├── ARCHITECTURE_DECISION.md    # 아키텍처 결정 문서
├── SETUP_GUIDE.md              # 설치 가이드
│
├── bot/                       # Trading Bot
│   ├── Dockerfile
│   ├── main.py
│   ├── test_api.py            # API 테스트
│   ├── requirements.txt
│   ├── core/                  # KIS API 연동 (backend와 공유)
│   │   ├── auth.py
│   │   ├── kis_api.py
│   │   ├── account.py
│   │   ├── market_data.py
│   │   ├── order.py
│   │   └── db_helper.py
│   ├── policies/              # 매매 전략
│   │   └── base.py
│   └── notifications/         # Discord 알림
│       └── discord.py
│
├── backend/                   # FastAPI Backend
│   ├── Dockerfile
│   ├── main.py
│   ├── database.py            # DB 연결 설정
│   ├── requirements.txt
│   ├── core/                  # KIS API 연동 (bot과 공유)
│   ├── api/v1/                # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── live.py
│   │   ├── stocks.py
│   │   ├── trading.py
│   │   └── orders.py
│   ├── services/              # 비즈니스 로직
│   │   └── kis_service.py
│   ├── models/                # DB 모델
│   │   ├── account.py
│   │   ├── stock.py
│   │   └── trade.py
│   └── schemas/               # Pydantic 스키마
│       ├── account.py
│       ├── stock.py
│       └── trade.py
│
├── frontend/                  # Vue.js Frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── router/            # Vue Router
│       ├── stores/            # Pinia 상태 관리
│       ├── services/          # API 클라이언트
│       ├── views/             # 페이지 컴포넌트
│       └── components/        # 재사용 컴포넌트
│
└── db/                        # Database
    └── init.sql               # 초기 스키마
```

---

## 개발 가이드

### 로컬 개발 모드

각 서비스를 개별적으로 실행할 수 있습니다:

```bash
# Backend만 재시작
docker-compose restart backend

# Bot만 재시작
docker-compose restart bot

# Frontend 개발 모드 (hot reload)
cd frontend
npm install
npm run dev
```

### 전략 추가하기

새로운 매매 전략을 추가하려면:

1. `bot/policies/` 폴더에 새 파일 생성 (예: `my_strategy.py`)
2. `BaseStrategy` 클래스를 상속받아 구현
3. `.env` 파일의 `ACTIVE_STRATEGIES`에 추가

자세한 내용은 [CLAUDE.md](CLAUDE.md)를 참고하세요.

---

## 문서

- [CLAUDE.md](CLAUDE.md) - 프로젝트 전체 개요 및 아키텍처
- [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md) - 아키텍처 설계 결정 사항
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 상세 설치 및 설정 가이드

---

## 트러블슈팅

### Database 연결 오류

```bash
# DB 컨테이너 상태 확인
docker-compose ps db

# DB 재시작
docker-compose restart db
```

### Frontend 빌드 오류

```bash
# 빌드 캐시 삭제 후 재빌드
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 라이선스

이 프로젝트는 개인 투자 보조 도구입니다. 모든 투자 책임은 사용자 본인에게 있습니다.

---

## 기여

이슈 및 PR은 언제나 환영합니다!
