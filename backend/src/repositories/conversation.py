from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from src.repositories.base import BaseRepository
from src.core.exceptions import ConversationNotFoundError


class ConversationRepository(BaseRepository):
    def __init__(self):
        super().__init__("conversations")
    
    def create_conversation(self, user_id: str) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        conversation_data = {
            "user_id": user_id,
            "status": "active",
            "stage": "greeting",
            "context": {},
            "products_discussed": [],
            "message_count": 0,  
            "started_at": now,
            "last_activity_at": now,
        }
        return self.create(conversation_data)
    
    def get_by_id(self, conversation_id: str) -> Dict[str, Any]:
        conversation = super().get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundError(conversation_id)
        return conversation
    
    def get_by_user_id(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .order("last_activity_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_active_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .eq("status", "active")
                .order("last_activity_at", desc=True)
                .limit(1)
                .execute()
            )
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None
    
    def update_activity(self, conversation_id: str) -> Dict[str, Any]:
        return self.update(conversation_id, {
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
    
    def update_stage(self, conversation_id: str, stage: str) -> Dict[str, Any]:
        return self.update(conversation_id, {
            "stage": stage,
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
    
    def update_context(self, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return self.update(conversation_id, {
            "context": context,
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
    
    def add_product_discussed(self, conversation_id: str, product_id: str) -> Dict[str, Any]:
        conversation = self.get_by_id(conversation_id)
        products_discussed = conversation.get("products_discussed", [])
        
        if product_id not in products_discussed:
            products_discussed.append(product_id)
        
        return self.update(conversation_id, {
            "products_discussed": products_discussed,
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
    
    def close_conversation(self, conversation_id: str) -> Dict[str, Any]:
        return self.update(conversation_id, {
            "status": "completed",
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
    
    def abandon_conversation(self, conversation_id: str) -> Dict[str, Any]:
        return self.update(conversation_id, {
            "status": "abandoned",
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
    
    def increment_message_count(self, conversation_id: str) -> Dict[str, Any]:
        """Increment the message count for a conversation."""
        conversation = self.get_by_id(conversation_id)
        current_count = conversation.get("message_count", 0)
        
        return self.update(conversation_id, {
            "message_count": current_count + 1,
            "last_activity_at": datetime.now(timezone.utc).isoformat()
        })
