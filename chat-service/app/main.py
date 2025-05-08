from fastapi import FastAPI, Request
from app.api.chat_router import router as chat_router
import logging
# FastAPI 앱 생성
app = FastAPI(
    title="TensorFlow & Computer Vision Service API",
    description="TensorFlow 기반 계산 및 컴퓨터 비전 서비스",
    version="1.0.0",
)

logger = logging.getLogger("chat-service")
logger.info(f"🤍0 메인 진입")
app.include_router(chat_router, prefix="/chat", tags=["파일 업로드"])

