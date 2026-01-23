from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    user_id: str


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    status: str
    stage: str
    context: Dict[str, Any]
    products_discussed: List[str]
    started_at: datetime
    ended_at: Optional[datetime]
    last_activity_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True
