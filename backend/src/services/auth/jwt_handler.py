from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import jwt
from src.config import settings
from src.core.exceptions import TokenExpiredError, TokenInvalidError


class JWTHandler:
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.auth.jwt_access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "iat": now,
            "exp": expires_at,
        }
        
        token = jwt.encode(
            payload,
            settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_algorithm
        )
        
        return token
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                settings.auth.jwt_secret_key,
                algorithms=[settings.auth.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise TokenInvalidError()
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        try:
            payload = JWTHandler.decode_token(token)
            return payload.get("sub")
        except (TokenExpiredError, TokenInvalidError):
            return None
    
    @staticmethod
    def get_token_expiry() -> int:
        return settings.auth.jwt_access_token_expire_minutes * 60


def get_jwt_handler() -> JWTHandler:
    return JWTHandler()
