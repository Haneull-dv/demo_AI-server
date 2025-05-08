import logging
logger = logging.getLogger("chat-service")
from app.domain.service.chat_service import ChatService

class ChatController:
    def __init__(self):
        self.service = ChatService()

    async def chat(self, message: str):
        logger.info(f"🤍2 컨트롤러 진입: {message}")
        return await self.service.chat(message)


