from datetime import datetime
from sqlalchemy import Column, BigInteger, SmallInteger, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.db.databases import Base
from app.models.user import GenderEnum  # user.py에 정의된 gender 재사용

class Patient(Base):
    __tablename__ = "patients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, comment="환자 성명")
    age = Column(SmallInteger, nullable=False, comment="smallint")
    gender = Column(SQLEnum(GenderEnum), nullable=True, comment="환자 성별")
    phone = Column(String(11), nullable=False, comment="환자 연락처, 국내 전화번호로 한정")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="환자 정보 등록 일시")
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="환자 정보 수정 일시")

    # 관계 정의 (진료 기록 테이블과의 연관 관계, cascade 설정)
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")