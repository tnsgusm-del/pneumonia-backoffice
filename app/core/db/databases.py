import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from app.core.config import settings

# 🔥 핵심: 특수문자(@, !) 충돌을 완벽하게 방어하기 위해 설정된 비밀번호를 quote_plus로 인코딩 처리
encoded_password = quote_plus(settings.DB_PASSWORD)

# ==========================================
# 1. 비동기(Async) DB 설정 (기존 팀원 코드 유지 및 특수문자 에러 해결)
# ==========================================
DATABASE_PREFIX_ASYNC = "mysql+asyncmy://"
DATABASE_URI_ASYNC = f"{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
DATABASE_URL_ASYNC = f"{DATABASE_PREFIX_ASYNC}{DATABASE_URI_ASYNC}"

# 비동기 엔진 생성
async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=False, future=True)
# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)

<<<<<<< HEAD
# 비동기 세션 생성 함수
=======
from app.models.user import User
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage
from app.models.ai_analysis_result import AiAnalysisResult

# 세션 생성 함수
>>>>>>> main
async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


# ==========================================
# 2. 동기(Sync) DB 설정 (추가: 4일차 사용자 API 및 Alembic 마이그레이션 호환용)
# ==========================================
DATABASE_PREFIX_SYNC = "mysql+pymysql://"
DATABASE_URL_SYNC = f"{DATABASE_PREFIX_SYNC}{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# 동기 엔진 생성
engine = create_engine(
    DATABASE_URL_SYNC,
    pool_pre_ping=True,  # 수시로 연결 유효성 자동 체크
    pool_recycle=3600    # 일정 시간 미사용 연결 자동 정리
)
# 동기 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 동기 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 3. 공통 모델 베이스 정의
# ==========================================
Base = declarative_base()