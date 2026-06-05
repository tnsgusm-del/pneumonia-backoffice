
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
# 데이터베이스 연결을 위한 Base 객체를 가져옵니다 (프로젝트 세팅에 맞게 경로 확인)
from app.core.db.databases import Base

class GenderEnum(str, enum.Enum):
    M = "male"
    F = "female"

class RoleEnum(str, enum.Enum):
    PENDING = "권한 부여 대기"
    STAFF = "폐렴 추적 관련 데이터 CRUD 허용"
    ADMIN = "전체데이터 CRUD 허용"

class DepartmentEnum(str, enum.Enum):
    MEDICAL = "의료진"
    DEV = "개발팀"
    RESEARCH = "연구진"

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.db.databases import Base  # 과제 템플릿의 Base 경로 확인

class User(Base):
    __tablename__ = "users"


    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False, comment="평문 저장 x -> 해쉬화 된 비밀번호 저장")
    name = Column(String(20), nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True, comment="유저 휴대폰 번호")
    gender = Column(SQLEnum(GenderEnum), nullable=False, comment="성별 선택")
    department = Column(SQLEnum(DepartmentEnum), nullable=False, comment="부서 선택")
    role = Column(SQLEnum(RoleEnum), nullable=False, comment="부여된 역할 권한")
    is_active = Column(Boolean, nullable=False, default=True, comment="계정 활성화 여부")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="유저 생성 일시")
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="유저 정보 수정 일시")

    # 관계 정의 (xray_images 테이블과의 연관 관계)
    xray_images = relationship("XrayImage", back_populates="uploader")

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
