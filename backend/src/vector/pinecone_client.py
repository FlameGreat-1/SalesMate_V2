from typing import Optional
from pinecone import Pinecone, ServerlessSpec
from src.config import settings
from src.core.exceptions import VectorDatabaseError


class PineconeClient:
    _instance = None
    _client = None
    _index = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        try:
            self._client = Pinecone(api_key=settings.vector_db.pinecone_api_key)
            self._ensure_index_exists()
        except Exception as e:
            raise VectorDatabaseError(f"Failed to initialize Pinecone: {str(e)}")
    
    def _ensure_index_exists(self):
        index_name = settings.vector_db.pinecone_index_name
        
        try:
            existing_indexes = self._client.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if index_name not in index_names:
                self._client.create_index(
                    name=index_name,
                    dimension=settings.vector_db.pinecone_dimension,
                    metric=settings.vector_db.pinecone_metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.vector_db.pinecone_environment
                    )
                )
        except Exception as e:
            raise VectorDatabaseError(f"Failed to create index: {str(e)}")
    
    def get_index(self):
        if self._index is None:
            try:
                self._index = self._client.Index(settings.vector_db.pinecone_index_name)
            except Exception as e:
                raise VectorDatabaseError(f"Failed to get index: {str(e)}")
        return self._index
    
    def health_check(self) -> bool:
        try:
            index = self.get_index()
            stats = index.describe_index_stats()
            return True
        except Exception:
            return False


def get_pinecone_client() -> PineconeClient:
    return PineconeClient()
