from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.db.databases import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(String(50), nullable=False)  # YYYY-MM-DD
    gender = Column(String(10), nullable=False)      # Male / Female
    created_at = Column(DateTime(timezone=True), server_default=func.now())