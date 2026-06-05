from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db.databases import Base

class XrayImage(Base):
    __tablename__ = "xray_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id = Column(BigInteger, ForeignKey("medical_records.id", ondelete="CASCADE"), nullable=False, comment="진료 기록 id")
    uploader_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="X-ray 이미지를 업로드한 유저의 id")
    image_url = Column(String(2048), nullable=False, comment="이미지 url")
    shooting_datetime = Column(DateTime, nullable=False, comment="X-ray 촬영일시")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="X-ray 이미지 등록 일시")

    # 관계 정의
    medical_record = relationship("MedicalRecord", back_populates="xray_images")
    uploader = relationship("User", back_populates="xray_images")