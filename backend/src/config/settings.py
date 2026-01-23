from functools import lru_cache
from pydantic_settings import BaseSettings

from src.config.auth import AuthConfig
from src.config.database import DatabaseConfig
from src.config.vector_db import VectorDBConfig
from src.config.llm import LLMConfig


class AppConfig(BaseSettings):
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class ConversationConfig(BaseSettings):
    max_history_length: int = 20
    context_window_messages: int = 3
    session_timeout_minutes: int = 30
    greeting_enabled: bool = True
    enable_logging: bool = True
    log_format: str = "txt"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class ProductConfig(BaseSettings):
    product_recommendation_limit: int = 5
    enable_product_comparison: bool = True
    enable_price_discussion: bool = True
    enable_upselling: bool = True
    enable_cross_selling: bool = True
    min_confidence_threshold: float = 0.6
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class Settings:
    def __init__(self):
        self.app = AppConfig()
        self.auth = AuthConfig()
        self.database = DatabaseConfig()
        self.vector_db = VectorDBConfig()
        self.llm = LLMConfig()
        self.conversation = ConversationConfig()
        self.product = ProductConfig()


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
