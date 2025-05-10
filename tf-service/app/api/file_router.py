import cv2
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import shutil
import os
import logging
from urllib.parse import unquote
from typing import Optional

router = APIRouter()
logger = logging.getLogger("tf_main")

# 업로드 디렉토리 절대 경로로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
print(f"🟠UPLOAD_DIR: {UPLOAD_DIR}")
print(f"🟠OUTPUT_DIR: {OUTPUT_DIR}")

os.makedirs(UPLOAD_DIR, exist_ok=True)
logger.info(f"파일 업로드 디렉토리: {UPLOAD_DIR}")

CASCADE_DIR = os.path.join(BASE_DIR, "data")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info("👻👻업로드 요청 도착!")
    if not file:
        raise HTTPException(status_code=400, detail="파일이 전송되지 않았습니다.")
    
    # 파일 저장 경로를 BASE_DIR 기준으로 설정
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    logger.info(f"파일 업로드 시작: {file.filename}, 저장 위치: {file_location}")
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"🥰🥰파일 업로드 성공: {file.filename}")
        
        # 파일 존재 여부 확인 및 크기 정보 가져오기
        if os.path.exists(file_location):
            file_size = os.path.getsize(file_location)
            logger.info(f"파일 저장 확인: {file_location}, 크기: {file_size} bytes")
            
            return JSONResponse(
                content={
                    "filename": file.filename,
                    "path": file_location,
                    "size": file_size,
                    "message": "파일 업로드 성공!"
                }
            )
        else:
            logger.error(f"⚠️파일이 저장되지 않음: {file_location}")
            raise HTTPException(status_code=500, detail="파일 저장에 실패했습니다.")
            
    except Exception as e:
        logger.error(f"파일 업로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}")

@router.post("/mosaic")
async def mosaic_file(filename: str = Form(...)):
    logger.info(f"👻👻 모자이크 요청 도착: {filename}")
    try:
        # URL 디코딩 처리
        decoded_filename = unquote(filename)
        input_path = os.path.join(UPLOAD_DIR, decoded_filename)
        output_path = os.path.join(OUTPUT_DIR, f"mosaic_{decoded_filename}")
        
        logger.info(f"입력 파일 경로: {input_path}")
        logger.info(f"출력 파일 경로: {output_path}")

        # output 폴더가 없으면 생성
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 파일 존재 여부 확인
        if not os.path.exists(input_path):
            logger.error(f"입력 파일 없음: {input_path}")
            return JSONResponse(status_code=404, content={"error": f"파일을 찾을 수 없습니다: {decoded_filename}"})

        # Haar Cascade 파일 경로 (절대경로로 지정)
        cascade_path = os.path.join(CASCADE_DIR, "haarcascade_frontalface_alt.xml")
        if not os.path.exists(cascade_path):
            logger.error(f"cascade 파일 없음: {cascade_path}")
            return JSONResponse(status_code=500, content={"error": f"Haar Cascade 파일이 존재하지 않습니다: {cascade_path}"})

        # 이미지 읽기
        img = cv2.imread(input_path)
        if img is None:
            logger.error(f"이미지 파일 읽기 실패: {input_path}")
            return JSONResponse(status_code=400, content={"error": f"이미지 파일을 읽을 수 없습니다: {input_path}"})

        cascade = cv2.CascadeClassifier(cascade_path)
        if cascade.empty():
            logger.error(f"cascade 로드 실패: {cascade_path}")
            return JSONResponse(status_code=500, content={"error": f"cascade 로드 실패: {cascade_path}"})

        faces = cascade.detectMultiScale(img, minSize=(30, 30))
        if len(faces) == 0:
            logger.info("얼굴을 찾지 못했습니다.")
            cv2.imwrite(output_path, img)  # 얼굴이 없어도 원본 저장
            return JSONResponse(status_code=200, content={"message": "얼굴을 찾지 못했습니다.", "output": output_path})

        # 얼굴마다 10x10 모자이크 적용
        for (x, y, w, h) in faces:
            face_img = img[y:y+h, x:x+w]
            if face_img.size == 0:
                logger.warning(f"잘못된 얼굴 영역: {(x, y, w, h)}")
                continue
            mosaic = cv2.resize(face_img, (10, 10), interpolation=cv2.INTER_LINEAR)
            mosaic = cv2.resize(mosaic, (w, h), interpolation=cv2.INTER_NEAREST)
            img[y:y+h, x:x+w] = mosaic

        # 결과 저장
        cv2.imwrite(output_path, img)
        logger.info(f"모자이크 이미지 저장: {output_path}")
        return JSONResponse(status_code=200, content={"message": "모자이크 처리 및 저장 성공", "output": output_path})
    except Exception as e:
        logger.error(f"모자이크 처리 중 오류: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"모자이크 처리 중 오류: {str(e)}"})