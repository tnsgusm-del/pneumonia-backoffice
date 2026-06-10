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

router = APIRouter(prefix="/api/v1/ai-analysis", tags=["AI Pneumonia Analysis"])

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
    """
    이전 과제(사용 권한 가드)에서 작성한 보안 필터 로직을 완벽하게 재활용합니다.
    Header의 Bearer Token을 추출/복호화하여 현재 로그인한 유저를 검증하고, 
    승인 대기자(PENDING) 등 권한이 없는 접근에 대해 403 예외를 반환합니다.
    """
    token = credentials.credentials
    try:
        # 1. JWT 복호화 및 페이로드 무결성 검증
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

    # 2. 데이터베이스에서 실존 유저인지 2차 확인
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

    # 3. 🚨 [사용 권한 없음 방어] 사내 승인을 받지 못한 PENDING 유저의 접근을 무조건 차단
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

@router.post("/{record_id}", response_model=AiAnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_ai_analysis(
    record_id: int, 
    response: Response, 
    current_user: User = Depends(get_current_active_user),  # 🔒 [Step 3 반영] 의료인/개발자/연구자 권한 확인 의존성 주입
    db: Session = Depends(get_db)
):
    """
    [REQ-PRED-001] 특정 진료 기록에 대해 실시간 AI 폐렴 예측 모델을 구동하고 결과를 저장합니다.
    - 🔒 **보안 요건**: 정식 승인된 계정(`STAFF`, `ADMIN`)만 사용이 허가됩니다.
    - 💡 **중복 분석 방지**: 이미 동일 모델명으로 저장된 결과가 존재한다면 즉시 기존 분석 결과를 반환(200 OK)합니다.
    """
    # 1. 진료 기록이 존재하는지 먼저 체크합니다.
    record = db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id)).scalars().first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"지정한 진료기록(ID: {record_id})이 존재하지 않습니다."
        )

    # 2. [중복 연산 차단 규칙] 이미 해당 진료기록으로 같은 모델을 사용하여 저장된 예측 결과가 있는지 우선 탐색
    existing_result = db.execute(
        select(AiAnalysisResult)
        .where(
            AiAnalysisResult.record_id == record_id,
            AiAnalysisResult.ai_model == AI_MODEL_NAME
        )
    ).scalars().first()

    if existing_result:
        # 중복 연산 방지 가동 시, 응답 상태코드를 200 OK로 정밀 조정하여 클라이언트에 인지시킵니다.
        response.status_code = status.HTTP_200_OK
        return existing_result

    # 3. 해당 진료 기록에 촬영된 X-ray 원본 이미지가 첨부되어 있는지 체크합니다.
    xray = db.execute(select(XrayImage).where(XrayImage.record_id == record_id)).scalars().first()
    if not xray or not xray.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 진료기록에 첨부된 흉부 X-ray 이미지 파일이 존재하지 않아 분석을 진행할 수 없습니다."
        )

    # 4. 로컬 디스크 파일 경로 조립 (예: "/media/xray/some.jpg" -> "media/xray/some.jpg")
    relative_image_path = xray.image_url.lstrip("/")
    full_local_image_path = BASE_DIR / relative_image_path

    # 5. 이미지 물리적 존재 여부 안전 검증
    if not full_local_image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드된 X-ray 파일이 물리적 디렉토리 내에 존재하지 않습니다."
        )

    # 6. 상주 중인 PyTorch AI 모델로 실시간 추론 연산 실행 (NFR-PRED-002 성능 한계 보장)
    prediction = predict_pneumonia(str(full_local_image_path))

    if "error" in prediction:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 분석 엔진 구동 실패: {prediction['error']}"
        )

    # 7. 추론 결과 데이터를 AiAnalysisResult 테이블에 최종 영구 적재합니다.
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


@router.get("/records/{record_id}", response_model=AiAnalysisResponse)
def get_ai_analysis_result(
    record_id: int, 
    current_user: User = Depends(get_current_active_user),  # 🔒 [Step 3 반영] 의료인/개발자/연구자 권한 확인 의존성 주입
    db: Session = Depends(get_db)
):
    """
    [REQ-PRED-002] 특정 진료 기록에 등록되어 있는 AI 분석 판독 최종 결과 상세 정보를 조회합니다.
    - 🔒 **보안 요건**: 정식 승인된 계정(`STAFF`, `ADMIN`)만 사용이 허가됩니다.
    """
    result = db.execute(select(AiAnalysisResult).where(AiAnalysisResult.record_id == record_id)).scalars().first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 진료기록에 대해 가동된 AI 판독 이력이 존재하지 않습니다."
        )
    return result