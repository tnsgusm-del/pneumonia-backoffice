import os
import uuid
import json
import asyncio
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt, JWTError

from app.core.db.databases import get_db
from app.core.redis_client import get_redis
from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage
from app.models.ai_analysis_result import AiAnalysisResult
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/api/v1", tags=["AI Pneumonia Analysis"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AI_MODEL_NAME = "SimpleCNN_v1"
TASK_QUEUE = "ai_task_queue"

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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 토큰 내 식별 정보가 올바르지 않습니다.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었거나 올바르지 않은 서명입니다.")

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="시스템에 등록되지 않은 세션입니다.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비활성화된 계정입니다.")
    if user.role == RoleEnum.PENDING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="요청 권한이 없습니다.")
    return user


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


@router.post("/medical-records/{record_id}/predict", response_model=AiAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def run_ai_analysis(
    record_id: int,
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    record = db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id)).scalars().first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"진료기록(ID: {record_id})이 존재하지 않습니다.")

    # 같은 이미지+모델로 이미 분석한 결과가 있으면 DB에서 바로 반환
    existing_result = db.execute(
        select(AiAnalysisResult).where(
            AiAnalysisResult.record_id == record_id,
            AiAnalysisResult.ai_model == AI_MODEL_NAME
        )
    ).scalars().first()
    if existing_result:
        response.status_code = status.HTTP_200_OK
        return existing_result

    xray = db.execute(select(XrayImage).where(XrayImage.record_id == record_id)).scalars().first()
    if not xray or not xray.image_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-ray 이미지가 존재하지 않습니다.")

    full_local_image_path = BASE_DIR / xray.image_url.lstrip("/")
    if not full_local_image_path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-ray 파일이 디렉토리에 존재하지 않습니다.")

    # Redis 큐에 작업 등록
    task_id = str(uuid.uuid4())
    channel = f"ai_result:{task_id}"
    redis = await get_redis()

    task = {
        "task_id": task_id,
        "image_path": str(full_local_image_path),
        "channel": channel
    }
    await redis.rpush(TASK_QUEUE, json.dumps(task))

    # Pub/Sub으로 결과 구독 (최대 30초 대기)
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    prediction = None
    try:
        for _ in range(60):  # 0.5초 * 60 = 30초
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
            if message and message["type"] == "message":
                prediction = json.loads(message["data"])
                break
            await asyncio.sleep(0.5)
    finally:
        await pubsub.unsubscribe(channel)

    if prediction is None or "error" in prediction:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AI 분석 타임아웃 또는 실패")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI 판독 이력이 존재하지 않습니다.")
    return results
