from typing import Optional, Dict, Any
from datetime import datetime, timezone
from src.repositories.base import BaseRepository
from src.core.exceptions import ResourceNotFoundError


class ProfileRepository(BaseRepository):
    def __init__(self):
        super().__init__("user_profiles")
    
    def create_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        data = {
            "user_id": user_id,
            "full_name": profile_data.get("full_name"),
            "budget_min": profile_data.get("budget_min"),
            "budget_max": profile_data.get("budget_max"),
            "preferred_categories": profile_data.get("preferred_categories", []),
            "preferred_brands": profile_data.get("preferred_brands", []),
            "feature_priorities": profile_data.get("feature_priorities", {}),
            "shopping_preferences": profile_data.get("shopping_preferences", {}),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return self.create(data)
    
    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(self.table_name).select("*").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        existing = self.get_by_user_id(user_id)
        if not existing:
            raise ResourceNotFoundError("Profile", user_id)
        
        update_data = {k: v for k, v in profile_data.items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        try:
            response = self.client.table(self.table_name).update(update_data).eq("user_id", user_id).execute()
            if response.data:
                return response.data[0]
            raise ResourceNotFoundError("Profile", user_id)
        except Exception as e:
            raise ResourceNotFoundError("Profile", user_id)
    
    def delete_by_user_id(self, user_id: str) -> bool:
        try:
            self.client.table(self.table_name).delete().eq("user_id", user_id).execute()
            return True
        except Exception:
            return False
