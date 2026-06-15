import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt, JWTError

# 데이터베이스 연결 의존성 및 관련 모델 임포트
from app.core.db.databases import get_db
from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage
from app.models.ai_analysis_result import AiAnalysisResult
from app.models.user import User, RoleEnum  # 🔒 사용자 및 역할 이넘 추가

# 💡 [핵심 연동] Step 1에서 작성하고 메모리에 안전하게 상주시킨 AI 예측 핵심 기능 임포트
from worker.model import predict_pneumonia

router = APIRouter(prefix="/api/v1", tags=["AI Pneumonia Analysis"])

# 프로젝트 루트 경로 (미디어 상대 경로 변환용)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 현재 사용 중인 AI 분석 모델 고유 식별자 선언
AI_MODEL_NAME = "SimpleCNN_v1"

# ==========================================
# 🔒 [Step 3 핵심] JWT 기반 사용자 권한 인가 의존성 (Security Guard)
# ==========================================
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"

def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰 내 식별 정보가 올바르지 않습니다."
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었거나 올바르지 않은 서명입니다."
        )

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="시스템에 등록되지 않은 세션입니다."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다. 로그인할 수 없습니다."
        )

    if user.role == RoleEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="요청 권한이 없습니다. 사내 승인(STAFF 또는 ADMIN)이 완료된 후 다시 시도해 주세요."
        )
        
    return user


# ==========================================
# 📋 Pydantic DTO 정의
# ==========================================
class AiAnalysisResponse(BaseModel):
    id: int
    record_id: int
    is_pneumonia: bool
    confidence: float
    heatmap_url: str
    ai_model: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# 🚀 권한이 보장된 AI 분석 및 결과 적재 API 구현체 (REQ-PRED-001 ~ 002)
# ==========================================

@router.post("/medical-records/{record_id}/predict", response_model=AiAnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_ai_analysis(
    record_id: int, 
    response: Response, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    record = db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id)).scalars().first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"지정한 진료기록(ID: {record_id})이 존재하지 않습니다."
        )

    existing_result = db.execute(
        select(AiAnalysisResult)
        .where(
            AiAnalysisResult.record_id == record_id,
            AiAnalysisResult.ai_model == AI_MODEL_NAME
        )
    ).scalars().first()

    if existing_result:
        response.status_code = status.HTTP_200_OK
        return existing_result

    xray = db.execute(select(XrayImage).where(XrayImage.record_id == record_id)).scalars().first()
    if not xray or not xray.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 진료기록에 첨부된 흉부 X-ray 이미지 파일이 존재하지 않아 분석을 진행할 수 없습니다."
        )

    relative_image_path = xray.image_url.lstrip("/")
    full_local_image_path = BASE_DIR / relative_image_path

    if not full_local_image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드된 X-ray 파일이 물리적 디렉토리 내에 존재하지 않습니다."
        )

    prediction = predict_pneumonia(str(full_local_image_path))

    if "error" in prediction:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 분석 엔진 구동 실패: {prediction['error']}"
        )

    ai_result = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=prediction["is_pneumonia"],
        confidence=prediction["confidence"],
        heatmap_url=f"/media/xray/heatmap_{full_local_image_path.name}",
        ai_model=AI_MODEL_NAME
    )
    
    db.add(ai_result)
    db.commit()
    db.refresh(ai_result)

    return ai_result


@router.get("/medical-records/{record_id}/analyses", response_model=list[AiAnalysisResponse])
def get_ai_analysis_result(
    record_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    results = db.execute(select(AiAnalysisResult).where(AiAnalysisResult.record_id == record_id)).scalars().all()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 진료기록에 대해 가동된 AI 판독 이력이 존재하지 않습니다."
        )
    return results