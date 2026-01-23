from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    password_hash_rounds: int = 12
    
    class Config:
        env_prefix = ""
        case_sensitive = False
