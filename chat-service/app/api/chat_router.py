from fastapi import APIRouter, File, UploadFile, Body
from app.domain.controlloer.chat_controller import ChatController
import logging
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
controller = ChatController()
logger = logging.getLogger("chat-service")

@router.post("/chat")
async def chat(message: str = Body(..., embed=False)):
    print(f"🤍1 라우터 진입 - 메시지: {message}")
    return await controller.chat(message)


