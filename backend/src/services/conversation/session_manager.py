from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from src.repositories.conversation import ConversationRepository
from src.repositories.message import MessageRepository
from src.core.schemas.conversation import ConversationResponse, ConversationCreate
from src.core.schemas.message import MessageResponse
from src.core.exceptions import ConversationNotFoundError


class SessionManager:
    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()
    
    def create_session(self, user_id: str) -> ConversationResponse:
        conversation = self.conversation_repo.create_conversation(user_id)
        return ConversationResponse(**conversation)
    
    def get_session(self, conversation_id: str) -> ConversationResponse:
        conversation = self.conversation_repo.get_by_id(conversation_id)
        return ConversationResponse(**conversation)
    
    def get_active_session(self, user_id: str) -> Optional[ConversationResponse]:
        conversation = self.conversation_repo.get_active_by_user_id(user_id)
        if conversation:
            return ConversationResponse(**conversation)
        return None
    
    def get_or_create_session(self, user_id: str) -> ConversationResponse:
        active_session = self.get_active_session(user_id)
        if active_session:
            return active_session
        return self.create_session(user_id)
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[ConversationResponse]:
        conversations = self.conversation_repo.get_by_user_id(user_id, limit)
        return [ConversationResponse(**c) for c in conversations]
    
    def update_session_activity(self, conversation_id: str) -> ConversationResponse:
        conversation = self.conversation_repo.update_activity(conversation_id)
        return ConversationResponse(**conversation)
    
    def update_session_stage(self, conversation_id: str, stage: str) -> ConversationResponse:
        conversation = self.conversation_repo.update_stage(conversation_id, stage)
        return ConversationResponse(**conversation)
    
    def update_session_context(self, conversation_id: str, context: Dict[str, Any]) -> ConversationResponse:
        conversation = self.conversation_repo.update_context(conversation_id, context)
        return ConversationResponse(**conversation)
    
    def add_product_to_session(self, conversation_id: str, product_id: str) -> ConversationResponse:
        conversation = self.conversation_repo.add_product_discussed(conversation_id, product_id)
        return ConversationResponse(**conversation)
    
    def get_session_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[MessageResponse]:
        messages = self.message_repo.get_by_conversation_id(conversation_id, limit, offset)
        return [MessageResponse(**m) for m in messages]
    
    def get_recent_messages(self, conversation_id: str, limit: int = 20) -> List[MessageResponse]:
        messages = self.message_repo.get_recent_messages(conversation_id, limit)
        return [MessageResponse(**m) for m in messages]
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MessageResponse:
        message = self.message_repo.create_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            intent=intent,
            metadata=metadata
        )
        
        self.update_session_activity(conversation_id)
        
        self.conversation_repo.increment_message_count(conversation_id)
        
        return MessageResponse(**message)
    
    def get_message_count(self, conversation_id: str) -> int:
        return self.message_repo.count_by_conversation_id(conversation_id)
    
    def close_session(self, conversation_id: str) -> ConversationResponse:
        conversation = self.conversation_repo.close_conversation(conversation_id)
        return ConversationResponse(**conversation)
    
    def abandon_session(self, conversation_id: str) -> ConversationResponse:
        conversation = self.conversation_repo.abandon_conversation(conversation_id)
        return ConversationResponse(**conversation)
    
    def delete_session(self, conversation_id: str) -> bool:
        self.message_repo.delete_by_conversation_id(conversation_id)
        return self.conversation_repo.delete(conversation_id)
    
    def get_session_context(self, conversation_id: str) -> Dict[str, Any]:
        conversation = self.get_session(conversation_id)
        return conversation.context or {}
    
    def merge_session_context(
        self,
        conversation_id: str,
        new_context: Dict[str, Any]
    ) -> ConversationResponse:
        current_context = self.get_session_context(conversation_id)
        merged_context = {**current_context, **new_context}
        return self.update_session_context(conversation_id, merged_context)


def get_session_manager() -> SessionManager:
    return SessionManager()
