from fastapi import FastAPI, APIRouter, Request, HTTPException, File, UploadFile, Form, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Dict, Any, Literal, Optional, Annotated, Union
import os
from dotenv import load_dotenv
import logging
import sys
from contextlib import asynccontextmanager
import json
from pydantic import BaseModel
import traceback
import json as pyjson
import httpx
from app.domain.model.service_proxy_factory import ServiceProxyFactory
from app.domain.model.service_type import ServiceType

# ✅ 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

# ✅ 환경변수 로드
# Load environment variables from .env file
load_dotenv()



# ✅ 요청 모델 정의
class FinanceRequest(BaseModel):
    data: Dict[str, Any]


# ✅ 라이프스팬 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀🚀🚀 FastAPI 앱이 시작됩니다.")
    yield
    print("🛑 FastAPI 앱이 종료됩니다.")

# ✅ FastAPI 설정
app = FastAPI(
    title="Gateway API",
    description="Gateway API for jinmini.com",
    version="0.1.0",
    lifespan=lifespan
)

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 메인 라우터 생성
gateway_router = APIRouter(prefix="/ai/v1", tags=["Gateway API"])

# ✅ 메인 라우터 실행
# GET
@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: ServiceType, 
    path: str, 
    request: Request
):
    try:
        logger.info(f"GET 요청: {service.value}/{path}")
        factory = ServiceProxyFactory(service_type=service)
        print(f"🍊1")
        response = await factory.request(
            method="GET",
            path=path,
            headers=request.headers.raw
        )
        print(f"🍊2 response: {response}")
        if response.status_code == 200:
            print(f"🍊3 response: {response}")
            try:
                return JSONResponse(content=response.json(), status_code=response.status_code)
            except Exception:
                print(f"⚠️ 메인라우터 get 에러 발생")
                return JSONResponse(
                    content={"message": "성공", "raw_response": response.text[:1000]},
                    status_code=200
                )
        else:
            print(f"🍊4")
            return JSONResponse(
                content={"error": f"서비스 오류: HTTP {response.status_code}", "details": response.text[:500]},
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"게이트웨이 오류: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

# 통합 POST 요청 처리 (JSON 또는 파일 업로드)
@gateway_router.post(
    "/{service}/{path:path}",
    summary="통합 POST 프록시 (JSON 또는 파일 업로드)",
    description="하나의 엔드포인트에서 JSON 요청과 파일 업로드를 모두 처리합니다."
)
async def proxy_post(
    service: ServiceType,
    path: str,
    request: Request,
    file: UploadFile = File(None),
    json_data: str = Form(None)
):
    try:
        logger.info(f"🟠1. POST 요청: {service.value}/{path}")
        factory = ServiceProxyFactory(service_type=service)
        
        # Content-Type 헤더 제거 (httpx가 자동으로 설정하도록)
        headers = {k: v for k, v in request.headers.items() 
                  if k.lower() not in ['content-length', 'host', 'content-type']}
        
        # 데이터 초기화
        files = {}  # 파일 데이터용
        data = {}   # 폼 데이터용

        # ✅ 파일이 있는 경우 files에 추가
        if file and file.filename:
            files["file"] = (file.filename, await file.read(), file.content_type)
            logger.info(f"파일 업로드 설정: {file.filename}")

        # ✅ json_data를 서비스 타입에 따라 적절한 키로 data에 추가
        if json_data:
            try:
                # JSON 문자열인 경우 파싱 시도
                json_dict = json.loads(json_data)
                if isinstance(json_dict, dict) and "filename" in json_dict:
                    # JSON에 filename 필드가 있는 경우
                    data["filename"] = json_dict["filename"]
                    logger.info(f"JSON에서 filename 필드 추출: {json_dict['filename']}")
                else:
                    # JSON이지만 filename 필드가 없는 경우
                    data["filename"] = json_data
                    logger.info(f"JSON 데이터를 그대로 filename으로 사용: {json_data}")
            except json.JSONDecodeError:
                # JSON이 아닌 경우 그대로 사용
                data["filename"] = json_data
                logger.info(f"일반 문자열을 filename으로 사용: {json_data}")

        # ✅ 서비스 타입에 따라 data 키 변경
        if service == ServiceType.CHAT:
            if "filename" in data:
                data["message"] = data.pop("filename")
                logger.info(f"chat 서비스용으로 키를 'message'로 변경: {data['message']}")
            
        # ✅ 프록시 요청
        prefix_path = f"{service.value}/{path}"
        response = await factory.request(
            method="POST",
            path=prefix_path,
            headers=headers,
            data=data if data else None,  # data가 비어있으면 None 전달
            files=files if files else None  # files가 비어있으면 None 전달
        )
        logger.info(f"🟠5. response: {response}")
        # ✅ 응답 처리
        if response.status_code == 200:
            try:
                return JSONResponse(content=response.json(), status_code=response.status_code)
            except Exception:
                return JSONResponse(
                    content={"message": "성공", "raw_response": response.text[:1000]},
                    status_code=200
                )
        else:
            return JSONResponse(
                content={"error": f"서비스 오류: HTTP {response.status_code}", "details": response.text[:500]},
                status_code=response.status_code
            )

    except Exception as e:
        logger.error(f"⚠️ 게이트웨이 오류: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


        

# PUT
@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        response = await factory.request(
            method="PUT",
            path=path,
            headers=request.headers.raw,
            body=await request.body()
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# DELETE
@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        response = await factory.request(
            method="DELETE",
            path=path,
            headers=request.headers.raw,
            body=await request.body()
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# PATCH
@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        response = await factory.request(
            method="PATCH",
            path=path,
            headers=request.headers.raw,
            body=await request.body()
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ 메인 라우터 등록
app.include_router(gateway_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    ) 