from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        import re
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SendMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, description="User message content")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (optional)")


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    preferred_categories: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None
    feature_priorities: Optional[Dict[str, int]] = None
    shopping_preferences: Optional[Dict[str, Any]] = None

    @field_validator("budget_max")
    @classmethod
    def validate_budget_range(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None and "budget_min" in info.data:
            budget_min = info.data.get("budget_min")
            if budget_min is not None and v < budget_min:
                raise ValueError("Maximum budget must be greater than or equal to minimum budget")
        return v


class ProductSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200, description="Search query")
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    limit: int = Field(10, ge=1, le=50)


class UpdateBudgetRequest(BaseModel):
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)

    @field_validator("budget_max")
    @classmethod
    def validate_budget_range(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None and "budget_min" in info.data:
            budget_min = info.data.get("budget_min")
            if budget_min is not None and v < budget_min:
                raise ValueError("Maximum budget must be greater than or equal to minimum budget")
        return v


class UpdatePreferencesRequest(BaseModel):
    preferred_categories: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None
    feature_priorities: Optional[Dict[str, int]] = None
