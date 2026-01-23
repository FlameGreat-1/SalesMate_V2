from typing import Optional, Dict, Any
from datetime import datetime, timezone
from src.repositories.base import BaseRepository
from src.core.exceptions import UserNotFoundError, EmailAlreadyExistsError


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__("users")
    
    def create_user(self, email: str, password_hash: str) -> Dict[str, Any]:
        existing = self.get_by_email(email)
        if existing:
            raise EmailAlreadyExistsError(email)
        
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return self.create(user_data)
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(self.table_name).select("*").eq("email", email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None
    
    def get_by_id(self, user_id: str) -> Dict[str, Any]:
        user = super().get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user
    
    def update_last_login(self, user_id: str) -> Dict[str, Any]:
        return self.update(user_id, {
            "last_login_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    
    def deactivate(self, user_id: str) -> Dict[str, Any]:
        return self.update(user_id, {
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    
    def activate(self, user_id: str) -> Dict[str, Any]:
        return self.update(user_id, {
            "is_active": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
