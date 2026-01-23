from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.api.models.requests import ProductSearchRequest
from src.api.models.responses import ProductListResponse, ProductRecommendationResponse
from src.api.dependencies import get_product_service, get_user_service, get_current_user_id
from src.services.product.service import ProductService
from src.services.user.service import UserService
from src.core.schemas.product import ProductResponse, ProductFilter
from src.core.exceptions import ProductNotFoundError

router = APIRouter()


@router.post("/search", response_model=ProductListResponse)
async def search_products_post(
    request: ProductSearchRequest,
    user_id: Optional[str] = Depends(get_current_user_id),
    product_service: ProductService = Depends(get_product_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Search products with filters and user preferences (POST method).
    
    Args:
        request: Search request with query and filters
        
    Returns:
        ProductListResponse with matching products
    """
    profile = None
    if user_id:
        profile = user_service.get_user_profile(user_id)
    
    filters = ProductFilter(
        category=request.category,
        brand=request.brand,
        min_price=request.min_price,
        max_price=request.max_price,
        limit=request.limit
    )
    
    products = product_service.search_products(
        query=request.query,
        profile=profile,
        filters=filters
    )
    
    return ProductListResponse(
        products=products,
        total=len(products),
        query=request.query,
        filters=filters.model_dump(exclude_unset=True)
    )


@router.get("/search", response_model=ProductListResponse)
async def search_products_get(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    limit: int = Query(5, ge=1, le=100, description="Maximum results"),
    user_id: Optional[str] = Depends(get_current_user_id),
    product_service: ProductService = Depends(get_product_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Search products using GET method (for easier testing and direct URL access).
    
    Args:
        query: Search query
        category: Filter by category
        brand: Filter by brand
        min_price: Minimum price
        max_price: Maximum price
        limit: Maximum results
        
    Returns:
        ProductListResponse with matching products
    """
    profile = None
    if user_id:
        profile = user_service.get_user_profile(user_id)
    
    filters = ProductFilter(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        limit=limit
    )
    
    products = product_service.search_products(
        query=query,
        profile=profile,
        filters=filters
    )
    
    return ProductListResponse(
        products=products,
        total=len(products),
        query=query,
        filters=filters.model_dump(exclude_unset=True)
    )


@router.get("/category/{category}", response_model=ProductListResponse)
async def get_products_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get products by category.
    
    Args:
        category: Category name
        limit: Maximum number of products to return
        
    Returns:
        ProductListResponse with products in the category
    """
    products = product_service.get_products_by_category(category, limit)
    
    return ProductListResponse(
        products=products,
        total=len(products),
        filters={"category": category}
    )


@router.get("/recommendations/personalized", response_model=ProductRecommendationResponse)
async def get_personalized_recommendations(
    limit: int = Query(5, ge=1, le=20),
    user_id: str = Depends(get_current_user_id),
    product_service: ProductService = Depends(get_product_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get personalized product recommendations based on user profile.
    
    Args:
        limit: Maximum number of recommendations
        
    Returns:
        ProductRecommendationResponse with recommended products
    """
    profile = user_service.get_user_profile(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile not found. Please complete your profile first."
        )
    
    products = product_service.get_recommendations_for_user(profile, limit)
    
    based_on = {}
    if profile.preferred_categories:
        based_on["categories"] = profile.preferred_categories[:3]
    if profile.preferred_brands:
        based_on["brands"] = profile.preferred_brands[:3]
    if profile.budget_max:
        based_on["budget"] = f"Up to ${profile.budget_max}"
    
    return ProductRecommendationResponse(
        products=products,
        reason="Based on your preferences and shopping history",
        based_on=based_on
    )


@router.get("/meta/categories", response_model=List[str])
async def get_categories(
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get all available product categories.
    
    Returns:
        List of category names
    """
    return product_service.get_available_categories()


@router.get("/meta/brands", response_model=List[str])
async def get_brands(
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get all available product brands.
    
    Returns:
        List of brand names
    """
    return product_service.get_available_brands()


@router.get("/{product_id}/similar", response_model=ProductListResponse)
async def get_similar_products(
    product_id: str,
    limit: int = Query(3, ge=1, le=10),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get products similar to a specific product.
    
    Args:
        product_id: Product ID to find similar products for
        limit: Maximum number of similar products
        
    Returns:
        ProductListResponse with similar products
    """
    try:
        products = product_service.get_similar_products(product_id, limit)
        
        return ProductListResponse(
            products=products,
            total=len(products),
            filters={"similar_to": product_id}
        )
        
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Get product details by ID.
    
    Args:
        product_id: Product ID
        
    Returns:
        ProductResponse with full product details
    """
    try:
        product = product_service.get_product_by_id(product_id)
        return product
        
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
