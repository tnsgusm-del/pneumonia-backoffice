from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, BigInteger, SmallInteger, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.databases import Base

class PatientGenderEnum(str, Enum):
    M = 'M'
    F = 'F'

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, comment="환자 성명")
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="smallint")
    gender: Mapped[PatientGenderEnum] = mapped_column(SQLAlchemyEnum(PatientGenderEnum), nullable=True, comment="환자 성별")
    phone: Mapped[str] = mapped_column(String(11), nullable=False, comment="환자 연락처, 국내 전화번호로 한정")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), comment="환자 정보 등록 일시")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now(), comment="환자 정보 수정 일시")

    # 관계 설정 (환자가 가진 진료 기록들)
<<<<<<< HEAD
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
=======
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
>>>>>>> main
