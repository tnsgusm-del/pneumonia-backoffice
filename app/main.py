import os
from pathlib import Path
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse 

# [수정된 부분] prediction 객체가 아닌 router 자체를 가져와서 별칭을 붙입니다.
from app.apis.practice_apis import router as practice_router
from app.apis.prediction import router as prediction_router 

app = FastAPI(title="폐렴 환자 관리 백오피스")

app.include_router(practice_router)
# [수정된 부분] prediction_router를 등록합니다.
app.include_router(prediction_router, prefix="/api/v1", tags=["Prediction"])

BASE_DIR = Path(__file__).resolve().parent.parent

if not (BASE_DIR / "static").exists():
    os.mkdir(BASE_DIR / "static")
if not (BASE_DIR / "media").exists():
    os.mkdir(BASE_DIR / "media")

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
    # API나 정적 파일 경로는 제외 (FastAPI가 먼저 매칭하지 못한 경우에만 실행됨)
    if (
        path.startswith("api/v1")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")
