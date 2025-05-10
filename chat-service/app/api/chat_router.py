from fastapi import APIRouter, Body
from app.domain.controller.chat_controller import ChatController

router = APIRouter()
controller = ChatController()

@router.post("/chat")
async def chat(message: str = Body(..., embed=False)):
    print(f"🩷1 라우터 진입 - 메시지: {message}")
    return await controller.chat(message)


