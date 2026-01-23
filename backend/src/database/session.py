from functools import lru_cache
from supabase import create_client, Client

from src.config import settings
from src.core.exceptions import DatabaseError


class SupabaseClient:
    _client: Client = None
    _service_client: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            if not settings.database.supabase_url or not settings.database.supabase_anon_key:
                raise DatabaseError("Supabase not configured")
            
            cls._client = create_client(
                settings.database.supabase_url,
                settings.database.supabase_anon_key
            )
        
        return cls._client

    @classmethod
    def get_service_client(cls) -> Client:
        if cls._service_client is None:
            if not settings.database.supabase_service_key:
                raise DatabaseError("Supabase service key not configured")
            
            cls._service_client = create_client(
                settings.database.supabase_url,
                settings.database.supabase_service_key
            )
        
        return cls._service_client


@lru_cache()
def get_supabase_client() -> Client:
    return SupabaseClient.get_client()


def get_supabase_service_client() -> Client:
    return SupabaseClient.get_service_client()
