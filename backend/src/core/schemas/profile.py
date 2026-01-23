from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ProfileCreate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    preferred_categories: List[str] = Field(default_factory=list)
    preferred_brands: List[str] = Field(default_factory=list)
    feature_priorities: Dict[str, int] = Field(default_factory=dict)
    shopping_preferences: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("budget_max")
    @classmethod
    def validate_budget_range(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None and "budget_min" in info.data:
            budget_min = info.data.get("budget_min")
            if budget_min is not None and v < budget_min:
                raise ValueError("Maximum budget must be greater than minimum")
        return v


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    preferred_categories: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None
    feature_priorities: Optional[Dict[str, int]] = None
    shopping_preferences: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    preferred_categories: List[str]
    preferred_brands: List[str]
    feature_priorities: Dict[str, int]
    shopping_preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
