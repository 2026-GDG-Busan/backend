import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers import wakeup, tts, ranking

app = FastAPI(title="The Noble AI Backend")

# CORS 설정 (프론트엔드 도메인에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결
app.include_router(wakeup.router, tags=["Wakeup"])
app.include_router(tts.router, tags=["TTS"])
app.include_router(ranking.router, tags=["Ranking"])

# 프론트엔드 정적 파일 서빙 (로컬 개발용 및 단일 배포용)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
