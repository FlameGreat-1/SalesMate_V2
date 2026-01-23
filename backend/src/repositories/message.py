from typing import List, Dict, Any
from datetime import datetime, timezone
from src.repositories.base import BaseRepository
from src.core.exceptions import DatabaseError


class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__("messages")
    
    def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "intent": intent,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self.create(message_data)
    
    def get_by_conversation_id(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=False)
                .limit(limit)
                .offset(offset)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            messages = response.data or []
            return list(reversed(messages))
        except Exception:
            return []
    
    def count_by_conversation_id(self, conversation_id: str) -> int:
        try:
            response = (
                self.client.table(self.table_name)
                .select("id", count="exact")
                .eq("conversation_id", conversation_id)
                .execute()
            )
            return response.count or 0
        except Exception:
            return 0
    
    def delete_by_conversation_id(self, conversation_id: str) -> bool:
        try:
            self.client.table(self.table_name).delete().eq("conversation_id", conversation_id).execute()
            return True
        except Exception:
            return False
