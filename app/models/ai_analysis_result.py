from datetime import datetime
from sqlalchemy import Column, BigInteger, Boolean, Numeric, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db.databases import Base

class AIAnalysisResult(Base):
    __tablename__ = "ai_analysis_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id = Column(BigInteger, ForeignKey("medical_records.id", ondelete="CASCADE"), nullable=False, comment="진료 기록 id")
    is_pneumonia = Column(Boolean, nullable=False, comment="폐렴 진단 여부")
    confidence = Column(Numeric(5, 2), nullable=False, comment="AI 예측 신뢰도")
    heatmap_url = Column(String(255), nullable=False, comment="AI가 판별한 병변 표시 이미지 url")
    ai_model = Column(String(50), nullable=False, comment="AI 예측에 사용된 모델명 혹은 모델파일")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="AI 폐렴 예측 결과 생성일시")
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="수정 일시")

    # 관계 정의
    medical_record = relationship("MedicalRecord", back_populates="ai_analysis_results")