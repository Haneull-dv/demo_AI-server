"""
TF 서비스 메인 애플리케이션 진입점
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.file_router import router as file_router
import uvicorn
import logging
import traceback
import os
import cv2

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tf_main")

# 현재 환경 정보 출력
logger.info(f"🚀 TF 서비스 시작")
logger.info(f"📂 현재 작업 디렉토리: {os.getcwd()}")
logger.info(f"📂 파일 목록: {os.listdir()}")

# 필요한 디렉토리 생성
uploads_dir = "uploads"
output_dir = "output"
logger.info(f"📂 uploads 폴더: {os.path.exists(uploads_dir)} (생성됨: {os.makedirs(uploads_dir, exist_ok=True) or True})")
logger.info(f"📂 output 폴더: {os.path.exists(output_dir)} (생성됨: {os.makedirs(output_dir, exist_ok=True) or True})")

# 의존성 확인
try:

    logger.info(f"✅ OpenCV 버전: {cv2.__version__}")
except ImportError:
    logger.warning(f"⚠️ OpenCV가 설치되어 있지 않습니다. 얼굴 인식 기능이 동작하지 않을 수 있습니다.")

# FastAPI 앱 생성
app = FastAPI(
    title="TensorFlow & Computer Vision Service API",
    description="TensorFlow 기반 계산 및 컴퓨터 비전 서비스",
    version="1.0.0",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 예외 처리 미들웨어 추가
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 요청: {request.method} {request.url.path} (클라이언트: {request.client.host})")
    try:
        response = await call_next(request)
        logger.info(f"📤 응답: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ 요청 처리 중 오류: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# 파일 업로드 라우터 등록
logger.info("🔄 파일 업로드 라우터 등록 (prefix='/tf')")
app.include_router(file_router, prefix="/tf", tags=["파일 업로드"])

# 직접 실행 시 (개발 환경)
if __name__ == "__main__":
    logger.info(f"💻 개발 모드로 실행 - 포트: 9005")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9005,
        reload=True,
        log_level="info"
    ) 