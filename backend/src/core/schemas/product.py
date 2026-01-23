from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    # Core Identity
    id: str
    sku: str
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    
    # Classification
    category: str
    subcategory: Optional[str] = None
    brand: str
    manufacturer: Optional[str] = None
    
    # Pricing
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    currency: str = "USD"
    
    # Inventory
    stock_status: str = "in_stock"
    stock_quantity: int = 0
    reorder_level: Optional[int] = None
    
    # Product Details
    specifications: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    included_accessories: List[str] = Field(default_factory=list)
    
    # Targeting & Classification
    target_audience: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    price_tier: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Ratings & Reviews
    rating: Optional[float] = None
    review_count: int = 0
    
    # Policies & Dates
    warranty_months: Optional[int] = None
    return_policy_days: Optional[int] = 30
    release_date: Optional[datetime] = None
    
    # Status Flags
    is_active: bool = True
    is_featured: bool = False
    is_new_arrival: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed field for vector search (not stored in DB)
    similarity_score: Optional[float] = Field(None, exclude=True)

    class Config:
        from_attributes = True


class ProductFilter(BaseModel):
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    price_tier: Optional[str] = None
    stock_status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_new_arrival: Optional[bool] = None
    tags: Optional[List[str]] = None
    target_audience: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    search_query: Optional[str] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    brand: str
    manufacturer: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    currency: str = "USD"
    stock_status: str = "in_stock"
    stock_quantity: int = 0
    reorder_level: Optional[int] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    included_accessories: List[str] = Field(default_factory=list)
    target_audience: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    price_tier: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    review_count: int = 0
    warranty_months: Optional[int] = None
    return_policy_days: Optional[int] = 30
    release_date: Optional[datetime] = None
    is_featured: bool = False
    is_new_arrival: bool = False


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    stock_status: Optional[str] = None
    stock_quantity: Optional[int] = None
    specifications: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None
    included_accessories: Optional[List[str]] = None
    target_audience: Optional[List[str]] = None
    use_cases: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_new_arrival: Optional[bool] = None
