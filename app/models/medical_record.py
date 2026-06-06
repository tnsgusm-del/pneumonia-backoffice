from datetime import datetime
from sqlalchemy import String, DateTime, BigInteger, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.databases import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, comment="환자 정보 테이블 FK")
    chart_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="환자 진료 차트 번호")
    symptoms: Mapped[str] = mapped_column(Text, nullable=False, comment="환자 증상 기록")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), comment="진료 정보 등록 일시")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=func.now(), comment="진료 정보 수정 일시")

    # 관계 설정
    patient = relationship("Patient", back_populates="medical_records")
    xray_images = relationship("XrayImage", back_populates="medical_record", cascade="all, delete-orphan")
    ai_analysis_results = relationship("AiAnalysisResult", back_populates="medical_record", cascade="all, delete-orphan")