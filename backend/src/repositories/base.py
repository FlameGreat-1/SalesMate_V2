from typing import Optional, List, Dict, Any
from supabase import Client
from src.database.session import get_supabase_service_client
from src.core.exceptions import DatabaseError


class BaseRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.client: Client = get_supabase_service_client()
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return response.data[0]
            raise DatabaseError(f"Failed to create {self.table_name} record")
        except Exception as e:
            raise DatabaseError(f"Database error: {str(e)}")
    
    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(self.table_name).select("*").eq("id", record_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            raise DatabaseError(f"Database error: {str(e)}")
    
    def update(self, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.table(self.table_name).update(data).eq("id", record_id).execute()
            if response.data:
                return response.data[0]
            raise DatabaseError(f"Failed to update {self.table_name} record")
        except Exception as e:
            raise DatabaseError(f"Database error: {str(e)}")
    
    def delete(self, record_id: str) -> bool:
        try:
            self.client.table(self.table_name).delete().eq("id", record_id).execute()
            return True
        except Exception as e:
            raise DatabaseError(f"Database error: {str(e)}")
    
    def list(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            query = self.client.table(self.table_name).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.limit(limit).offset(offset).execute()
            return response.data or []
        except Exception as e:
            raise DatabaseError(f"Database error: {str(e)}")
