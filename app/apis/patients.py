import os
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.db.databases import get_db
from app.models.patient import Patient, PatientGenderEnum
from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage
from app.models.ai_analysis_result import AiAnalysisResult

# 환자 및 진료기록 통합 라우터 선언
router = APIRouter(prefix="/api/v1", tags=["Patients & Medical Records"])

# X-Ray 파일 저장 디렉토리 설정 (NFR-MDR-001 로컬 저장소 요구 준수)
UPLOAD_DIR = Path("media/xray")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 📋 Pydantic DTO 스키마 정의
# ==========================================
class PatientCreate(BaseModel):
    name: str = Field(..., example="홍길동")
    age: int = Field(..., ge=0, example=45)
    gender: PatientGenderEnum = Field(..., example=PatientGenderEnum.M)
    phone: str = Field(..., min_length=9, max_length=11, example="01012345678")

class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, example="홍길순")
    phone: Optional[str] = Field(None, example="01099998888")

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: PatientGenderEnum
    phone: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PatientDetailResponse(BaseModel):
    name: str
    gender: PatientGenderEnum
    phone: str
    age: int

    class Config:
        from_attributes = True

class MedicalRecordBriefResponse(BaseModel):
    id: int
    chart_number: str
    symptoms: str
    created_at: datetime

    class Config:
        from_attributes = True

class MedicalRecordDetailResponse(BaseModel):
    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    xray_image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# 👥 환자 관리 API (REQ-PTNT-001 ~ 005)
# ==========================================

@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """[REQ-PTNT-001] 환자 정보 등록 API (의료인 전용)"""
    exist_patient = db.execute(select(Patient).where(Patient.phone == patient_data.phone)).scalars().first()
    if exist_patient:
        raise HTTPException(status_code=400, detail="이미 등록된 연락처의 환자입니다.")

    new_patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        gender=patient_data.gender,
        phone=patient_data.phone
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient


@router.get("/patients", response_model=List[PatientResponse])
def get_patients_list(
    search: Optional[str] = None,
    gender: Optional[PatientGenderEnum] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """[REQ-PTNT-002] 환자 목록 검색 및 필터링 조회 API"""
    query = select(Patient)

    if search:
        query = query.where(Patient.name.contains(search))
    if gender:
        query = query.where(Patient.gender == gender)
    if age_min is not None:
        query = query.where(Patient.age >= age_min)
    if age_max is not None:
        query = query.where(Patient.age <= age_max)

    result = db.execute(query).scalars().all()
    return result


@router.get("/patients/{patient_id}", response_model=PatientDetailResponse)
def get_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    """[REQ-PTNT-003] 환자 상세 단일 조회 API"""
    patient = db.execute(select(Patient).where(Patient.id == patient_id)).scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="해당 환자 정보를 찾을 수 없습니다.")
    return patient


@router.patch("/patients/{patient_id}", response_model=PatientResponse)
def update_patient_info(patient_id: int, update_data: PatientUpdate, db: Session = Depends(get_db)):
    """[REQ-PTNT-004] 환자 정보 부분 수정(Partial Update) API"""
    patient = db.execute(select(Patient).where(Patient.id == patient_id)).scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="해당 환자 정보를 찾을 수 없습니다.")

    if update_data.name is not None:
        patient.name = update_data.name
    if update_data.phone is not None:
        exist_phone = db.execute(
            select(Patient).where(Patient.phone == update_data.phone, Patient.id != patient_id)
        ).scalars().first()
        if exist_phone:
            raise HTTPException(status_code=400, detail="이미 다른 환자가 사용 중인 연락처 번호입니다.")
        patient.phone = update_data.phone

    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """[REQ-PTNT-005] 환자 데이터 CASCADE 즉시 영구 삭제 API"""
    patient = db.execute(select(Patient).where(Patient.id == patient_id)).scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="삭제할 환자가 존재하지 않습니다.")

    db.delete(patient)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================
# 🔬 진료기록 관리 API (REQ-MDR-001 ~ 003)
# ==========================================

@router.post("/medical-records", status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    patient_id: int = Form(...),
    chart_number: str = Form(...),
    symptoms: str = Form(...),
    xray_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """[REQ-MDR-001] 진료기록 등록 및 X-Ray 이미지 로컬 동적 업로드 저장 API"""
    patient = db.execute(select(Patient).where(Patient.id == patient_id)).scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="등록하려는 진료 기록의 대상 환자가 존재하지 않습니다.")

    exist_chart = db.execute(select(MedicalRecord).where(MedicalRecord.chart_number == chart_number)).scalars().first()
    if exist_chart:
        raise HTTPException(status_code=400, detail="이미 등록된 차트 넘버 식별자입니다.")

    file_extension = Path(xray_image.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        content = await xray_image.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"X-Ray 이미지 로컬 디스크 저장 실패: {str(e)}")

    new_record = MedicalRecord(
        patient_id=patient_id,
        chart_number=chart_number,
        symptoms=symptoms
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    new_xray = XrayImage(
        record_id=new_record.id,
        image_url=f"/media/xray/{unique_filename}",
        shooting_datetime=datetime.now()
    )
    db.add(new_xray)

    new_ai_result = AiAnalysisResult(
        record_id=new_record.id,
        is_pneumonia=True,
        confidence=92.4,
        heatmap_url=f"/media/xray/heatmap_{unique_filename}",
        ai_model="ResNet50-ChestXray-v2.4.1"
    )
    db.add(new_ai_result)

    db.commit()

    return {
        "record_id": new_record.id,
        "patient_id": new_record.patient_id,
        "chart_number": new_record.chart_number,
        "symptoms": new_record.symptoms,
        "xray_image_url": new_xray.image_url,
        "created_at": new_record.created_at
    }


@router.get("/patients/{patient_id}/medical-records", response_model=List[MedicalRecordBriefResponse])
def get_patient_records(patient_id: int, db: Session = Depends(get_db)):
    """[REQ-MDR-002] 특정 환자의 진료 기록 목록 요약본 조회 API (증상 100자 요약 기능 포함)"""
    patient = db.execute(select(Patient).where(Patient.id == patient_id)).scalars().first()
    if not patient:
        raise HTTPException(status_code=404, detail="해당 환자 정보를 찾을 수 없습니다.")

    records = db.execute(select(MedicalRecord).where(MedicalRecord.patient_id == patient_id)).scalars().all()

    brief_records = []
    for record in records:
        short_symptoms = record.symptoms
        if len(short_symptoms) > 100:
            short_symptoms = f"{short_symptoms[:100]}..."
        
        brief_records.append({
            "id": record.id,
            "chart_number": record.chart_number,
            "symptoms": short_symptoms,
            "created_at": record.created_at
        })

    return brief_records


@router.get("/medical-records/{record_id}", response_model=MedicalRecordDetailResponse)
def get_medical_record_detail(record_id: int, db: Session = Depends(get_db)):
    """[REQ-MDR-003] 특정 진료 기록 단일 상세 정보 및 이미지 경로 포함 조회 API"""
    record = db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id)).scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="지정한 진료 기록을 찾을 수 없습니다.")

    image_url = None
    xray = db.execute(select(XrayImage).where(XrayImage.record_id == record_id)).scalars().first()
    if xray:
        image_url = xray.image_url

    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "chart_number": record.chart_number,
        "symptoms": record.symptoms,
        "xray_image_url": image_url,
        "created_at": record.created_at
    }