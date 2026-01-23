"""LLM configuration settings."""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAIConfig(BaseSettings):
    """OpenAI-specific configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix='OPENAI_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore'
    )
    
    api_key: str = ""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 300
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3


class GeminiConfig(BaseSettings):
    """Gemini-specific configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix='GEMINI_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore'
    )
    
    api_key: str = ""
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40
    timeout: int = 60
    max_retries: int = 3


class LLMConfig(BaseSettings):
    """LLM provider configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix='LLM_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
        arbitrary_types_allowed=True
    )
    
    provider: Literal["openai", "gemini"] = "gemini"
    
    # Nested configs
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
