from fastapi import APIRouter, Form, Depends
from app.domain.controller.chat_controller import ChatController
from app.domain.model.chat_schema import ChatRequest, ChatResponse

router = APIRouter()
controller = ChatController()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(..., description="채팅 메시지", example="안녕하세요")
):
    """
    채팅 메시지를 받아 응답을 생성합니다.
    
    - **message**: 사용자의 채팅 메시지
    """
    print(f"🩷1 라우터 진입 - 메시지: {message}")
    return await controller.chat(message)


