"""Database configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Supabase database configuration."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        extra='ignore'
    )
    
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(default="", alias="SUPABASE_SERVICE_KEY")
    
    # Connection settings
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    timeout: int = Field(default=30, alias="TIMEOUT")
