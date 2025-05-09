import logging
logger = logging.getLogger("chat-service")

class ChatService:
    def __init__(self):
        pass

    async def chat(self, message: str):
        logger.info(f"🤍3 서비스 진입: {message}")
        return {"❤️ message": "d"}
