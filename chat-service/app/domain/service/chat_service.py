import logging
logger = logging.getLogger("chat-service")

class ChatService:
    def __init__(self):
        pass

    async def chat(self, message: str):
        logger.info(f"🤍3 서비스 진입: {message}")
        return {"❤️ message": "넌 아주 잘하고 있어. 힘들다는 건 성장하고 있다는 거고, 시간을 쓰는 만큼 잘하게 되는 거야. 아플 때 많이 못했으니까 지금 느린 건 당연해. 조급해하지말고 어제보다 발전하는 걸 목표로 하자!"}
