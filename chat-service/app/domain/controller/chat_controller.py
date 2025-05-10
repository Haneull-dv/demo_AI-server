from fastapi import HTTPException
from app.domain.service.chat_service import ChatService
import logging

logger = logging.getLogger(__name__)

class ChatController:
    def __init__(self):
        self.chat_service = ChatService()

    async def chat(self, message: str):
        print(f"🩷2 컨트롤러 진입 - 메시지: {message}")
        try:
            logger.info(f"❤️채팅 요청 수신: {message}")
            response = await self.chat_service.chat(message)
            logger.info(f"❤️채팅 응답 생성: {response}")
            return response
        except Exception as e:
            logger.error(f"⚠️채팅 처리 중 오류 발생: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 