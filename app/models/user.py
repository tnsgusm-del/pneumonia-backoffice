from datetime import datetime
from enum import Enum
from sqlalchemy import BigInteger, String, Boolean, DateTime, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.databases import Base


# ※ Base는 프로젝트 환경에 맞게 임포트 경로를 맞춰주세요. (예: app.core.db.databases)
from app.core.db.databases import Base 

class GenderEnum(str, Enum):
    M = 'M'
    F = 'F'

class DepartmentEnum(str, Enum):
    MEDICAL = 'MEDICAL'
    DEV = 'DEV'
    RESEARCH = 'RESEARCH'

class RoleEnum(str, Enum):
    PENDING = 'PENDING'
    STAFF = 'STAFF'
    ADMIN = 'ADMIN'

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="평문 저장 x -> 해쉬화 된 비밀번호 저장")
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=True, comment="유저 휴대폰 번호")
    gender: Mapped[GenderEnum] = mapped_column(SQLAlchemyEnum(GenderEnum), nullable=False, comment="성별 선택")
    department: Mapped[DepartmentEnum] = mapped_column(SQLAlchemyEnum(DepartmentEnum), nullable=False, comment="부서 선택")
    role: Mapped[RoleEnum] = mapped_column(SQLAlchemyEnum(RoleEnum), nullable=False, comment="부여된 역할 권한")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="계정 활성화 여부")
    
    # 🔥 [중요 수정]: default=func.now()를 추가하여, DB 제약 조건과 상관없이 SQLAlchemy가 직접 'now()' 함수를 쿼리에 담아 보내도록 보완했습니다.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=func.now(), 
        server_default=func.now(), 
        comment="유저 생성 일시"
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now(), comment="유저 정보 수정 일시")

    # 관계 설정 (X-ray 이미지를 올린 사람)
    xray_images = relationship("XrayImage", back_populates="uploader")