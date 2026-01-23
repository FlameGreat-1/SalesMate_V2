from typing import Optional
from fastapi import Depends

from src.services.auth.service import AuthService
from src.services.user.service import UserService
from src.services.product.service import ProductService
from src.services.conversation.service import ConversationService
from src.api.middleware.auth import get_current_user


def get_auth_service() -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService()


def get_user_service() -> UserService:
    """Dependency to get UserService instance."""
    return UserService()


def get_product_service() -> ProductService:
    """Dependency to get ProductService instance."""
    return ProductService()


def get_conversation_service() -> ConversationService:
    """Dependency to get ConversationService instance."""
    return ConversationService()


def get_current_user_id(
    current_user: dict = Depends(get_current_user)
) -> str:
    """
    Dependency to extract user_id from authenticated user.
    
    Args:
        current_user: Authenticated user data from JWT token
        
    Returns:
        User ID string
    """
    return current_user["user_id"]


def get_optional_user_id(
    current_user: Optional[dict] = Depends(get_current_user)
) -> Optional[str]:
    """
    Dependency to extract user_id from authenticated user (optional).
    Returns None if user is not authenticated.
    """
    if current_user:
        return current_user.get("user_id")
    return None
