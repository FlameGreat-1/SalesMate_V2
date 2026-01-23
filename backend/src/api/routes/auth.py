from fastapi import APIRouter, Depends, HTTPException, status
from src.api.models.requests import SignupRequest, LoginRequest
from src.api.models.responses import AuthResponse
from src.api.dependencies import get_auth_service, get_user_service, get_current_user_id
from src.services.auth.service import AuthService
from src.services.user.service import UserService
from src.core.schemas.user import UserResponse
from src.core.schemas.profile import ProfileResponse, ProfileUpdate
from src.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    ValidationError,
)

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user account.
    
    Creates a new user with email and password, automatically creates
    a profile with default values, and optionally updates it with full_name.
    
    Args:
        request: Signup request with email, password, and optional full_name
        
    Returns:
        AuthResponse with user data, profile, and access token
        
    Raises:
        HTTPException 409: If email already exists
        HTTPException 400: If validation fails
    """
    try:
        # Create user account (this already creates a profile with default values)
        auth_result = auth_service.signup(request.email, request.password)
        
        # Get the profile created by auth service (it's a dict)
        profile = auth_result.get("profile")
        
        # Convert dict to ProfileResponse if profile exists
        profile_response = ProfileResponse(**profile) if profile else None
        
        # Update profile with full_name if provided
        if request.full_name and profile:
            profile_data = ProfileUpdate(full_name=request.full_name)
            # update_profile returns ProfileResponse object, so replace profile_response
            profile_response = user_service.update_profile(
                auth_result["user"]["id"],
                profile_data
            )
        
        return AuthResponse(
            user=UserResponse(**auth_result["user"]),
            profile=profile_response,  # Always ProfileResponse or None
            access_token=auth_result["access_token"],
            token_type=auth_result["token_type"],
            expires_in=auth_result["expires_in"]
        )
        
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and get access token.
    
    Validates credentials and returns user data with profile and JWT token.
    
    Args:
        request: Login request with email and password
        
    Returns:
        AuthResponse with user data, profile, and access token
        
    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 400: If account is deactivated
    """
    try:
        # Login returns user, profile (dict), and token
        auth_result = auth_service.login(request.email, request.password)
        
        # Get profile from auth_result (it's a dict)
        profile = auth_result.get("profile")
        
        return AuthResponse(
            user=UserResponse(**auth_result["user"]),
            profile=ProfileResponse(**profile) if profile else None,
            access_token=auth_result["access_token"],
            token_type=auth_result["token_type"],
            expires_in=auth_result["expires_in"]
        )
        
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current authenticated user information.
    
    Returns the authenticated user's data and profile without issuing
    a new access token.
    
    Returns:
        AuthResponse with user data and profile (no new token)
        
    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 404: If user not found
    """
    try:
        user = user_service.get_user(user_id)
        profile = user_service.get_user_profile(user_id)
        
        return AuthResponse(
            user=user,
            profile=profile,
            access_token="",  # No new token issued for /me endpoint
            token_type="bearer",
            expires_in=0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
