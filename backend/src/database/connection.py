"""
SalesMate MVP - Database Connection Manager
Supabase PostgreSQL connection handling
"""

from typing import Optional
from supabase import create_client, Client

from src.config import settings
from src.core.exceptions import DatabaseConnectionError

from src.utils.logger import get_logger
logger = get_logger(__name__)


class DatabaseConnection:
    """
    Manages Supabase database connections.
    Provides both anon and service role clients.
    """
    
    _client: Optional[Client] = None
    _service_client: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Get Supabase client with anon key (for user operations).
        
        Returns:
            Configured Supabase client
            
        Raises:
            DatabaseConnectionError: If Supabase is not configured
        """
        if cls._client is None:
            if not settings.database.supabase_url or not settings.database.supabase_anon_key:
                raise DatabaseConnectionError(
                    "Supabase URL or anon key not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY."
                )
            
            cls._client = create_client(
                settings.database.supabase_url,
                settings.database.supabase_anon_key
            )
            
            logger.info("Supabase client created (anon)")
        
        return cls._client

    @classmethod
    def get_service_client(cls) -> Client:
        """
        Get Supabase client with service key (for admin operations).
        
        Returns:
            Configured Supabase service client
            
        Raises:
            DatabaseConnectionError: If service key is not configured
        """
        if cls._service_client is None:
            if not settings.database.supabase_url or not settings.database.supabase_service_key:
                raise DatabaseConnectionError(
                    "Supabase service key not configured. Set SUPABASE_SERVICE_KEY."
                )
            
            cls._service_client = create_client(
                settings.database.supabase_url,
                settings.database.supabase_service_key
            )
            
            logger.info("Supabase service client created")
        
        return cls._service_client

    @classmethod
    async def health_check(cls) -> bool:
        """
        Check database connectivity.
        
        Returns:
            True if database is reachable
        """
        try:
            client = cls.get_client()
            # Simple query to test connection
            result = client.table('users').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    @classmethod
    def close(cls) -> None:
        """Close database connections."""
        cls._client = None
        cls._service_client = None
        logger.info("Database connections closed")


def get_db_client() -> Client:
    """
    Dependency injection function for FastAPI.
    
    Returns:
        Supabase client for the request
    """
    return DatabaseConnection.get_client()


def get_db_service_client() -> Client:
    """
    Dependency injection for admin operations.
    
    Returns:
        Supabase service client
    """
    return DatabaseConnection.get_service_client()
