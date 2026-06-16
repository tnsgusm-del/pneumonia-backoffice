# 🫁 AI Health - 폐렴 환자 관리 백오피스

물리치료사로 10년 넘게 일하다가 의료 AI 분야로 전환하면서 진행한 팀 프로젝트입니다. 병원에서 실제로 느꼈던 불편함들을 떠올리며 기획했습니다. 흉부 X-Ray 이미지를 AI로 분석해 폐렴 여부를 빠르게 확인하고, 환자 정보와 진료기록을 한 곳에서 관리할 수 있는 백오피스 시스템입니다.

---

## 🛠 기술 스택

| 분류 | 기술 |
|------|------|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | MySQL, Docker |
| AI/ML | PyTorch, SimpleCNN |
| Frontend | Vanilla JS, HTML/CSS |
| Auth | JWT (python-jose) |

---

## 👥 팀 구성

3명이서 역할을 나눠 진행했습니다. 팀장을 맡아 전체 흐름을 조율하면서 개발도 함께 담당했습니다.

| 이름 | 담당 |
|------|------|
| 권순현 (팀장) | DB 설계 및 마이그레이션, 환자/진료기록 API, AI 예측 API, 프론트엔드 API 연결 |
| 김영현 | 유저 API |
| nobamti | 유저 API |

---

## 주요 기능

로그인한 사용자의 권한에 따라 접근할 수 있는 기능이 달라집니다. 관리자가 승인한 계정만 환자 정보와 AI 예측 기능을 사용할 수 있습니다.

**사용자 관리**
JWT 기반으로 인증을 처리했으며, PENDING / STAFF / ADMIN 세 가지 역할로 권한을 구분했습니다. 신규 가입자는 관리자 승인을 받아야 서비스를 이용할 수 있습니다.

**환자 관리**
환자 등록부터 조회, 수정, 삭제까지 기본적인 CRUD를 구현했으며, 이름/성별/나이로 필터링 검색도 가능합니다.

**진료기록 관리**
진료기록 등록 시 흉부 X-Ray 이미지를 함께 업로드할 수 있습니다. 이미지는 서버에 저장되며, AI 예측에도 바로 활용됩니다.

**AI 폐렴 예측**
SimpleCNN 모델로 X-Ray 이미지를 분석해 폐렴 여부와 Confidence를 반환합니다. 동일한 진료기록에 대한 중복 분석을 방지하는 로직도 포함했습니다.

---

## 📁 프로젝트 구조

```
├── app/
│   ├── apis/          # API 라우터
│   ├── models/        # SQLAlchemy ORM 모델
│   ├── core/          # DB 연결, 설정
│   └── main.py        # FastAPI 앱 진입점
├── worker/
│   └── model.py       # AI 예측 모델
├── static/            # 프론트엔드 (HTML/CSS/JS)
├── docs/              # API 설계 문서 및 실행화면
├── media/             # X-Ray 이미지 저장소
└── docker-compose.yml
```

---

## ⚙️ 실행 방법

```bash
# 1. 환경변수 설정
cp .env.example .env

# 2. Docker로 MySQL 실행
docker-compose up -d

# 3. 서버 실행
uv run uvicorn app.main:app --reload
```

실행 후 http://0.0.0.0:8000 으로 접속하시면 됩니다. API 문서는 http://0.0.0.0:8000/docs 에서 확인하실 수 있습니다.

---

## 📸 실행 화면

### 환자 목록
![환자목록](docs/환자목록.png)

### 환자 상세 및 진료기록
![진료기록목록](docs/진료기록목록.png)

### AI 폐렴 예측 결과
![진료상세정보_AI예측](docs/진료상세정보_AI예측.png)

---

## 📄 API 문서

- [유저 API 설계](docs/4일차_USER_API_설계.md)
- [환자관리 API 설계](docs/5일차_환자관리_API_설계.md)
- [폐렴예측 API 설계](docs/6일차_폐렴예측_API_설계.md)
- [앱 실행화면](docs/7일차_앱_실행화면.md)

---

## 📋 프로젝트 진행 과정 총정리

### 1. Team Rule 정의
- GitHub Flow 브랜치 전략 채택 (`main` 브랜치 보호, `feat/기능명` 브랜치에서 개발 후 PR 머지)
- 커밋 컨벤션: `feat`, `fix`, `docs`, `refactor` 등 prefix 통일
- PR 머지 전 팀원 코드 리뷰 원칙

### 2. 사용자 요구사항 정의
- 병원 현장에서 실제로 느낀 불편함 기반으로 요구사항 도출
- 주요 요구사항: 환자 정보 관리, 진료기록 등록, X-Ray 이미지 기반 AI 폐렴 예측, 권한별 접근 제어
- PENDING / STAFF / ADMIN 역할 기반 권한 구조 설계

### 3. API 명세서 작성
- RESTful API 설계 원칙 적용
- 유저 API, 환자관리 API, 폐렴예측 API 총 3개 도메인으로 분리 작성
- 각 API별 Request/Response 스키마, 상태코드, 에러 케이스 정의
- [API 문서 보기](docs/)

### 4. Git & Github Branch 전략 구성
- GitHub Flow 기반 운영
- `main`: 배포 가능한 안정 브랜치
- `feat/기능명`: 기능 단위 개발 브랜치
- PR을 통한 코드 리뷰 후 머지

### 5. 프로젝트 세팅
- FastAPI + SQLAlchemy + Alembic 기반 백엔드 구성
- MySQL 데이터베이스 설계 및 ORM 모델 작성 (5개 테이블)
- Alembic 마이그레이션으로 DB 스키마 버전 관리
- `.env` 파일로 환경변수 분리 관리

### 6. API 및 AI 워커 코드 작성 후 Branch 전략을 통한 코드 병합
- 팀원별 도메인 분리: 유저 API(김영혜, 박종현), 환자/진료기록/AI API(권순현)
- 각자 `feat/` 브랜치에서 개발 후 PR을 통해 `main`에 머지
- JWT 인증 미들웨어, 권한 검증 로직 공통 모듈화
- SimpleCNN 모델 통합 및 X-Ray 이미지 업로드/추론 파이프라인 구현

### 7. 아키텍처 설계 및 적용
- 동시성 문제 해결을 위한 Event-Driven Architecture 설계
- FastAPI(Producer) → Redis Queue → AI Worker(Consumer) 구조로 AI 추론 분리
- Redis Pub/Sub으로 추론 결과 비동기 전달
- [아키텍처 설계 문서](docs/9일차_동시성문제_해결을위한_아키텍처설계.md)

### 8. 도커 인프라 관련 파일 작성
- `app/Dockerfile`: FastAPI 이미지 빌드
- `worker/Dockerfile`: AI 워커 이미지 빌드
- `app/.dockerignore`: 보안 및 이미지 경량화
- `docker-compose.yml`: fastapi, ai-worker, mysql, redis 4개 서비스 정의
- MySQL healthcheck 기반 서비스 의존성 관리

### 9. AWS 배포
- 추후 진행 예정

### 10. QA 진행
- Docker 환경에서 전체 서비스 통합 실행 확인
- healthcheck 엔드포인트를 통한 서비스 상태 모니터링
- AI 예측 API 동작 확인 (Redis 큐 → AI 워커 → Pub/Sub 결과 반환)
