from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.db.databases import Base  # 프로젝트 템플릿의 Base 경로

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    image_path = Column(String(500), nullable=False)         # X-Ray 이미지 경로
    prediction_probability = Column(Float, nullable=True)     # AI 판독 확률
    result = Column(String(50), nullable=True)               # Normal / Pneumonia
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())