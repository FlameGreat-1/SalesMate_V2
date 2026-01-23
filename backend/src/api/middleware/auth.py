from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.auth.service import AuthService
from src.core.exceptions import TokenInvalidError, TokenExpiredError

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    auth_service = AuthService()
    
    try:
        token = credentials.credentials
        user_data = auth_service.verify_token(token)
        return user_data
        
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Optional authentication dependency.
    Returns user data if token is provided and valid, None otherwise.
    """
    if not credentials:
        return None
    
    try:
        auth_service = AuthService()
        token = credentials.credentials
        user_data = auth_service.verify_token(token)
        return user_data
    except:
        return None


def require_auth(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that requires authentication.
    Alias for get_current_user for clearer intent.
    """
    return user
