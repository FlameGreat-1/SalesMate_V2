from typing import Dict, Any
from src.repositories.user import UserRepository
from src.repositories.profile import ProfileRepository
from src.services.auth.password_handler import PasswordHandler
from src.services.auth.jwt_handler import JWTHandler
from src.core.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    ValidationError,
    TokenInvalidError,
)
from src.utils.validators import validate_email, validate_password


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = ProfileRepository()
        self.password_handler = PasswordHandler()
        self.jwt_handler = JWTHandler()
    
    def signup(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user and create their profile.
        
        Args:
            email: User email address
            password: User password (will be hashed)
            
        Returns:
            Dict containing user, profile, and access token
            
        Raises:
            EmailAlreadyExistsError: If email is already registered
            ValidationError: If email or password is invalid
        """
        email = validate_email(email)
        validate_password(password)
        
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise EmailAlreadyExistsError(email)
        
        password_hash = self.password_handler.hash_password(password)
        
        user = self.user_repo.create_user(email, password_hash)
        
        # Create profile and get it back
        profile = self.profile_repo.create_profile(user["id"], {})
        
        access_token = self.jwt_handler.create_access_token(user["id"], user["email"])
        
        return {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
            },
            "profile": profile,  
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.jwt_handler.get_token_expiry(),
        }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and return access token.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Dict containing user, profile, and access token
            
        Raises:
            InvalidCredentialsError: If email or password is incorrect
            ValidationError: If account is deactivated
        """
        email = validate_email(email)
        
        user = self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()
        
        if not self.password_handler.verify_password(password, user["password_hash"]):
            raise InvalidCredentialsError()
        
        if not user.get("is_active", True):
            raise ValidationError("Account is deactivated")
        
        self.user_repo.update_last_login(user["id"])
        
        # Get user profile
        profile = self.profile_repo.get_by_user_id(user["id"])
        
        access_token = self.jwt_handler.create_access_token(user["id"], user["email"])
        
        return {
            "user": {
                "id": user["id"],
                "email": user["email"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login_at": user.get("last_login_at"),
            },
            "profile": profile, 
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.jwt_handler.get_token_expiry(),
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return user data.
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing user_id and email
            
        Raises:
            TokenInvalidError: If token is invalid or expired
            ValidationError: If account is deactivated
        """
        payload = self.jwt_handler.decode_token(token)
        
        user_id = payload.get("sub")
        if not user_id:
            raise TokenInvalidError()
        
        user = self.user_repo.get_by_id(user_id)
        
        if not user.get("is_active", True):
            raise ValidationError("Account is deactivated")
        
        return {
            "user_id": user["id"],
            "email": user["email"],
        }
    
    def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Get current authenticated user from token.
        
        Args:
            token: JWT access token
            
        Returns:
            Dict containing user data
            
        Raises:
            TokenInvalidError: If token is invalid or expired
        """
        user_data = self.verify_token(token)
        user = self.user_repo.get_by_id(user_data["user_id"])
        
        return {
            "id": user["id"],
            "email": user["email"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "last_login_at": user.get("last_login_at"),
        }


def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return AuthService()
