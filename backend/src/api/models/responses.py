from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from src.core.schemas.user import UserResponse
from src.core.schemas.profile import ProfileResponse
from src.core.schemas.product import ProductResponse
from src.core.schemas.conversation import ConversationResponse
from src.core.schemas.message import MessageResponse


class AuthResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse]
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse]


class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]
    products_discussed: List[ProductResponse]


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    conversation_id: str


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


class ChatResponse(BaseModel):
    conversation_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse
    products: Optional[List[ProductResponse]] = None
    intent: Optional[str] = None
    stage: Optional[str] = None


class ProductRecommendationResponse(BaseModel):
    products: List[ProductResponse]
    reason: str
    based_on: Dict[str, Any]


class ConversationSummaryResponse(BaseModel):
    conversation_id: str
    user_id: str
    status: str
    stage: str
    started_at: datetime
    last_activity: datetime
    message_count: int
    user_message_count: int
    assistant_message_count: int
    products_discussed_count: int
    products_discussed: List[str]
    intents: Dict[str, int]
    context: Dict[str, Any]
