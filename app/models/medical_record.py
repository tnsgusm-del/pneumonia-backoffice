from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db.databases import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, comment="환자 정보 테이블 FK")
    chart_number = Column(String(50), unique=True, nullable=False, comment="환자 진료 차트 번호")
    symptoms = Column(Text, nullable=False, comment="환자 증상 기록")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="진료 정보 등록 일시")
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="진료 정보 수정 일시")

    # 관계 정의
    patient = relationship("Patient", back_populates="medical_records")
    xray_images = relationship("XrayImage", back_populates="medical_record", cascade="all, delete-orphan")
    ai_analysis_results = relationship("AIAnalysisResult", back_populates="medical_record", cascade="all, delete-orphan")