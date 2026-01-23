from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.models.requests import UpdateProfileRequest, UpdateBudgetRequest, UpdatePreferencesRequest
from src.api.models.responses import UserProfileResponse
from src.api.dependencies import get_user_service, get_current_user_id
from src.services.user.service import UserService
from src.core.schemas.profile import ProfileResponse, ProfileUpdate
from src.core.exceptions import UserNotFoundError, ValidationError

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current authenticated user's profile information.
    
    This is the primary endpoint for getting user profile data.
    Alias: /profile
    
    Returns:
        UserProfileResponse with user and profile data
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        user_with_profile = user_service.get_user_with_profile(user_id)
        
        return UserProfileResponse(
            user=user_with_profile["user"],
            profile=user_with_profile["profile"]
        )
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get current user's profile information (alias for /me).
    
    Returns:
        UserProfileResponse with user and profile data
        
    Raises:
        HTTPException 404: If user not found
    """
    # Reuse the /me endpoint logic
    return await get_current_user_profile(user_id, user_service)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update user profile information.
    
    Updates fields like full_name and other profile attributes.
    
    Args:
        request: Profile update data
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If user not found
    """
    try:
        profile_data = ProfileUpdate(**request.model_dump(exclude_unset=True))
        profile = user_service.update_profile(user_id, profile_data)
        
        return profile
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/budget", response_model=ProfileResponse)
async def update_budget(
    request: UpdateBudgetRequest,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update user budget preferences.
    
    Sets minimum and/or maximum budget for product recommendations.
    
    Args:
        request: Budget update data (min and/or max)
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 400: If validation fails (e.g., min > max)
        HTTPException 404: If user not found
    """
    try:
        profile = user_service.update_budget(
            user_id,
            request.budget_min,
            request.budget_max
        )
        
        return profile
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/preferences", response_model=ProfileResponse)
async def update_preferences(
    request: UpdatePreferencesRequest,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update user shopping preferences.
    
    Updates preferred categories, brands, and feature priorities.
    
    Args:
        request: Preferences update data
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If user not found
    """
    try:
        profile = user_service.update_preferences(
            user_id,
            preferred_categories=request.preferred_categories,
            preferred_brands=request.preferred_brands,
            feature_priorities=request.feature_priorities
        )
        
        return profile
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/preferences/categories/{category}", response_model=ProfileResponse)
async def add_preferred_category(
    category: str,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Add a category to user's preferred categories.
    
    Args:
        category: Category name to add (e.g., "laptops", "smartphones")
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        profile = user_service.add_preferred_category(user_id, category)
        return profile
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/preferences/categories/{category}", response_model=ProfileResponse)
async def remove_preferred_category(
    category: str,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Remove a category from user's preferred categories.
    
    Args:
        category: Category name to remove
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        profile = user_service.remove_preferred_category(user_id, category)
        return profile
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/preferences/brands/{brand}", response_model=ProfileResponse)
async def add_preferred_brand(
    brand: str,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Add a brand to user's preferred brands.
    
    Args:
        brand: Brand name to add (e.g., "Apple", "Samsung")
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        profile = user_service.add_preferred_brand(user_id, brand)
        return profile
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/preferences/brands/{brand}", response_model=ProfileResponse)
async def remove_preferred_brand(
    brand: str,
    user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    """
    Remove a brand from user's preferred brands.
    
    Args:
        brand: Brand name to remove
        
    Returns:
        Updated ProfileResponse
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        profile = user_service.remove_preferred_brand(user_id, brand)
        return profile
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
