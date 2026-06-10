import os
from pathlib import Path
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# 데이터베이스 연결 엔진 및 테이블 자동 생성을 위한 모듈 임포트
from app.core.db.databases import engine, Base
from app.apis.practice_apis import router as practice_router
from app.apis.users import auth_router, user_router
from app.apis.patients import router as patients_router
from app.apis.ai_analysis import router as ai_analysis_router

# [테이블 자동 생성 활성화] 앱 기동 시 등록된 모델 스키마를 추적하여 DB 테이블을 자동 생성합니다.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="폐렴 환자 관리 백오피스")

# 메인 앱에 각각의 API 라우터들을 연동합니다.
app.include_router(practice_router)
app.include_router(auth_router)     # 인증 관리 라우터 연동 (/api/v1/auth)
app.include_router(user_router)     # 유저 관리 라우터 연동 (/api/v1/users)
app.include_router(patients_router) # 환자 및 진료 기록 관리 라우터 연동
app.include_router(ai_analysis_router)


BASE_DIR = Path(__file__).resolve().parent.parent

# 만약 static, media 폴더가 존재하지 않으면 생성
if not (BASE_DIR / "static").exists():
    os.mkdir(BASE_DIR / "static")
if not (BASE_DIR / "media").exists():
    os.mkdir(BASE_DIR / "media")

# 파일 업로드 서빙을 보장하기 위해 media 하위 디렉토리를 포함시킵니다.
media_xray_path = BASE_DIR / "media" / "xray"
media_xray_path.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")


@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    if (
        path.startswith("api/v1")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")