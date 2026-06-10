import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# 1. DB 연결 (비동기 함수명 async_get_db 적용!)
from app.core.db.databases import async_get_db
from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage
from app.models.ai_analysis_result import AiAnalysisResult

# 2. AI 추론 모델 Import
from worker.model import predict_pneumonia

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------------------------------------------------------------------
# 🔒 [임시 인증 함수]
# ------------------------------------------------------------------
async def get_current_user_placeholder():
    return {"id": 1, "email": "staff@hospital.com", "role": "STAFF"}


@router.post("/medical-records/{record_id}/predict")
async def predict_pneumonia_api(
    record_id: int,
    db: AsyncSession = Depends(async_get_db), # <-- async_get_db 적용 완료!
    current_user: dict = Depends(get_current_user_placeholder)
):
    # 1. 권한 체크
    if current_user.get("role") not in ["STAFF", "ADMIN"]:
        raise HTTPException(status_code=403, detail="AI 예측 결과를 확인할 권한이 없습니다.")

    # 2. 진료기록 기본 조회 (비동기 방식 조회 문법 적용)
    record_result = await db.execute(select(MedicalRecord).filter(MedicalRecord.id == record_id))
    record = record_result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="진료기록을 찾을 수 없습니다.")

    # 3. [캐싱 로직] 이미 해당 진료기록으로 저장된 AI 예측 결과가 있는지 비동기 조회
    existing_res = await db.execute(select(AiAnalysisResult).filter(AiAnalysisResult.record_id == record_id))
    existing_result = existing_res.scalars().first()
    
    if existing_result:
        return {
            "record_id": record_id,
            "is_pneumonia": existing_result.is_pneumonia,
            "confidence": float(existing_result.confidence),
            "heatmap_url": existing_result.heatmap_url,
            "message": "이미 조회된 과거의 AI 예측 결과(캐시)를 반환합니다."
        }

    # 4. 진료기록에 연결된 X-ray 이미지 찾기 (비동기 조회)
    xray_res = await db.execute(select(XrayImage).filter(XrayImage.record_id == record_id))
    xray = xray_res.scalars().first()
    if not xray:
        raise HTTPException(status_code=400, detail="해당 진료기록에 등록된 흉부 X-Ray 이미지가 없습니다.")

    file_path = os.path.join(BASE_DIR, xray.image_url.lstrip("/"))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="서버에서 이미지 파일을 찾을 수 없습니다.")

    # 5. AI 추론 실행
    try:
        with open(file_path, "rb") as f:
            image_bytes = f.read()
            
        probability = predict_pneumonia(image_bytes)
        is_pneumonia_bool = bool(probability > 0.5)
        confidence_val = round(probability, 4)

        # 6. 추론 결과를 DB에 새로 저장 (비동기 커밋)
        new_analysis = AiAnalysisResult(
            record_id=record_id,
            is_pneumonia=is_pneumonia_bool,
            confidence=confidence_val,
            heatmap_url="", 
            ai_model="SimpleCNN_v1" 
        )
        db.add(new_analysis)
        await db.commit() # <-- 비동기 방식이므로 await가 붙습니다.

        return {
            "record_id": record_id,
            "is_pneumonia": is_pneumonia_bool,
            "confidence": confidence_val,
            "heatmap_url": "",
            "message": "AI 예측이 성공적으로 수행되고 결과가 DB에 저장되었습니다."
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"예측 수행 중 오류 발생: {str(e)}")