from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "안녕하세요"
            }
        }

class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "안녕하세요! 무엇을 도와드릴까요?",
                "metadata": {
                    "timestamp": "2024-03-21T12:00:00Z"
                }
            }
        }

