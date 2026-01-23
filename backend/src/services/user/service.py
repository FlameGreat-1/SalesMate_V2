from typing import Dict, Any, Optional

from src.repositories.user import UserRepository
from src.repositories.profile import ProfileRepository
from src.core.schemas.user import UserResponse, UserUpdate
from src.core.schemas.profile import ProfileResponse, ProfileCreate, ProfileUpdate
from src.core.exceptions import UserNotFoundError, ValidationError


class UserService:
    def __init__(self):  
        self.user_repo = UserRepository()
        self.profile_repo = ProfileRepository()
    
    def get_user(self, user_id: str) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        return UserResponse(**user)
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        user = self.user_repo.get_by_email(email)
        if user:
            return UserResponse(**user)
        return None
    
    def get_user_profile(self, user_id: str) -> Optional[ProfileResponse]:
        profile = self.profile_repo.get_by_user_id(user_id)
        if profile:
            return ProfileResponse(**profile)
        return None
    
    def get_user_with_profile(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user(user_id)
        profile = self.get_user_profile(user_id)
        
        return {
            "user": user,
            "profile": profile
        }
    
    def create_profile(self, user_id: str, profile_data: ProfileCreate) -> ProfileResponse:
        existing_profile = self.profile_repo.get_by_user_id(user_id)
        if existing_profile:
            raise ValidationError("User already has a profile")
        
        profile_dict = profile_data.model_dump(exclude_unset=True)
        profile = self.profile_repo.create_profile(user_id, profile_dict)
        return ProfileResponse(**profile)
    
    def update_profile(self, user_id: str, profile_data: ProfileUpdate) -> ProfileResponse:
        profile_dict = profile_data.model_dump(exclude_unset=True)
        profile = self.profile_repo.update_profile(user_id, profile_dict)
        return ProfileResponse(**profile)
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        user_dict = user_data.model_dump(exclude_unset=True)
        
        if not user_dict:
            raise ValidationError("No fields to update")
        
        user = self.user_repo.update(user_id, user_dict)
        return UserResponse(**user)
    
    def deactivate_user(self, user_id: str) -> UserResponse:
        user = self.user_repo.deactivate(user_id)
        return UserResponse(**user)
    
    def activate_user(self, user_id: str) -> UserResponse:
        user = self.user_repo.activate(user_id)
        return UserResponse(**user)
    
    def delete_user(self, user_id: str) -> bool:
        self.profile_repo.delete_by_user_id(user_id)
        return self.user_repo.delete(user_id)
    
    def update_budget(self, user_id: str, budget_min: Optional[float], budget_max: Optional[float]) -> ProfileResponse:
        profile_data = {}
        if budget_min is not None:
            profile_data["budget_min"] = budget_min
        if budget_max is not None:
            profile_data["budget_max"] = budget_max
        
        profile = self.profile_repo.update_profile(user_id, profile_data)
        return ProfileResponse(**profile)
    
    def update_preferences(
        self,
        user_id: str,
        preferred_categories: Optional[list] = None,
        preferred_brands: Optional[list] = None,
        feature_priorities: Optional[dict] = None
    ) -> ProfileResponse:
        profile_data = {}
        
        if preferred_categories is not None:
            profile_data["preferred_categories"] = preferred_categories
        
        if preferred_brands is not None:
            profile_data["preferred_brands"] = preferred_brands
        
        if feature_priorities is not None:
            profile_data["feature_priorities"] = feature_priorities
        
        profile = self.profile_repo.update_profile(user_id, profile_data)
        return ProfileResponse(**profile)
    
    def add_preferred_category(self, user_id: str, category: str) -> ProfileResponse:
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserNotFoundError(user_id)
        
        categories = profile.get("preferred_categories", [])
        if category not in categories:
            categories.append(category)
        
        updated_profile = self.profile_repo.update_profile(user_id, {
            "preferred_categories": categories
        })
        return ProfileResponse(**updated_profile)
    
    def remove_preferred_category(self, user_id: str, category: str) -> ProfileResponse:
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserNotFoundError(user_id)
        
        categories = profile.get("preferred_categories", [])
        if category in categories:
            categories.remove(category)
        
        updated_profile = self.profile_repo.update_profile(user_id, {
            "preferred_categories": categories
        })
        return ProfileResponse(**updated_profile)
    
    def add_preferred_brand(self, user_id: str, brand: str) -> ProfileResponse:
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserNotFoundError(user_id)
        
        brands = profile.get("preferred_brands", [])
        if brand not in brands:
            brands.append(brand)
        
        updated_profile = self.profile_repo.update_profile(user_id, {
            "preferred_brands": brands
        })
        return ProfileResponse(**updated_profile)
    
    def remove_preferred_brand(self, user_id: str, brand: str) -> ProfileResponse:
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserNotFoundError(user_id)
        
        brands = profile.get("preferred_brands", [])
        if brand in brands:
            brands.remove(brand)
        
        updated_profile = self.profile_repo.update_profile(user_id, {
            "preferred_brands": brands
        })
        return ProfileResponse(**updated_profile)


def get_user_service() -> UserService:
    return UserService()
