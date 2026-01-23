"""Vector database configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorDBConfig(BaseSettings):
    """Pinecone and embedding configuration."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Pinecone settings
    pinecone_api_key: str = Field(default="", alias="PINECONE_API_KEY")
    pinecone_environment: str = Field(default="", alias="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="salesmate-products", alias="PINECONE_INDEX_NAME")
    pinecone_dimension: int = Field(default=384, alias="PINECONE_DIMENSION")
    pinecone_metric: str = Field(default="cosine", alias="PINECONE_METRIC")
    pinecone_cloud: str = Field(default="aws", alias="PINECONE_CLOUD")
    pinecone_region: str = Field(default="us-east-1", alias="PINECONE_REGION")
    
    # Embedding settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    embedding_batch_size: int = Field(default=32, alias="EMBEDDING_BATCH_SIZE")
    
    # Indexing settings
    enable_auto_indexing: bool = Field(default=True, alias="ENABLE_AUTO_INDEXING")
    
    # Search settings
    top_k: int = Field(default=10, alias="TOP_K")
    min_score: float = Field(default=0.7, alias="MIN_SCORE")
