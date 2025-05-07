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
        response = await factory.request(
            method="GET",
            path=path,
            headers=request.headers.raw
        )
        
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
    file: UploadFile = File(None, description="업로드할 파일 (선택 사항)"),
    json_data: Optional[str] = Form(None, description="JSON 형식의 데이터 (선택 사항)")
):
    import json as pyjson
    import httpx
    try:
        logger.info(f"POST 요청: {service.value}/{path}")
        headers = dict(request.headers.items())
        # 파일 업로드 처리
        if file and file.filename:
            file_content = await file.read()
            files = {"file": (file.filename, file_content, file.content_type)}
            data = {}
            if json_data:
                try:
                    data = pyjson.loads(json_data)
                except Exception:
                    data = {"json_data": json_data}
            async with httpx.AsyncClient() as client:
                base_url = ServiceProxyFactory(service_type=service).base_url
                url = f"{base_url}/{service}/{path}"
                response = await client.post(url, files=files, data=data, headers=headers)
        else:
            # JSON 요청 처리
            body = None
            if json_data:
                try:
                    body = pyjson.dumps(pyjson.loads(json_data))
                except Exception:
                    body = pyjson.dumps({"json_data": json_data})
            else:
                body = await request.body()
                if not body:
                    body = b"{}"
            base_url = ServiceProxyFactory(service_type=service).base_url
            url = f"{base_url}/{path}"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, content=body, headers=headers)
        # 응답 처리
        if response.status_code < 400:
            try:
                return JSONResponse(content=response.json(), status_code=response.status_code)
            except Exception:
                return JSONResponse(
                    content={"message": "성공", "raw_response": response.text[:1000]},
                    status_code=response.status_code
                )
        else:
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