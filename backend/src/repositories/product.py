from typing import List, Dict, Any, Optional
from src.repositories.base import BaseRepository
from src.core.exceptions import ProductNotFoundError


class ProductRepository(BaseRepository):
    def __init__(self):
        super().__init__("products")
    
    def get_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU."""
        try:
            response = self.client.table(self.table_name).select("*").eq("sku", sku).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None
    
    def get_by_id(self, product_id: str) -> Dict[str, Any]:
        """Get product by ID, raises exception if not found."""
        product = super().get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return product
    
    def search(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        manufacturer: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        price_tier: Optional[str] = None,
        stock_status: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_new_arrival: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        target_audience: Optional[List[str]] = None,
        use_cases: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Advanced product search with multiple filters.
        
        Args:
            category: Filter by category
            subcategory: Filter by subcategory
            brand: Filter by brand
            manufacturer: Filter by manufacturer
            min_price: Minimum price
            max_price: Maximum price
            price_tier: Filter by price tier (budget, mid_range, premium)
            stock_status: Filter by stock status
            is_featured: Filter featured products
            is_new_arrival: Filter new arrivals
            tags: Filter by tags (any match)
            target_audience: Filter by target audience (any match)
            use_cases: Filter by use cases (any match)
            search_query: Text search in name and description
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of matching products
        """
        try:
            query = self.client.table(self.table_name).select("*").eq("is_active", True)
            
            # Category filters
            if category:
                query = query.eq("category", category)
            
            if subcategory:
                query = query.eq("subcategory", subcategory)
            
            # Brand filters
            if brand:
                query = query.eq("brand", brand)
            
            if manufacturer:
                query = query.eq("manufacturer", manufacturer)
            
            # Price filters
            if min_price is not None:
                query = query.gte("price", min_price)
            
            if max_price is not None:
                query = query.lte("price", max_price)
            
            if price_tier:
                query = query.eq("price_tier", price_tier)
            
            # Stock filter
            if stock_status:
                query = query.eq("stock_status", stock_status)
            
            # Status flags
            if is_featured is not None:
                query = query.eq("is_featured", is_featured)
            
            if is_new_arrival is not None:
                query = query.eq("is_new_arrival", is_new_arrival)
            
            # JSONB array filters (contains any of the values)
            if tags:
                query = query.contains("tags", tags)
            
            if target_audience:
                query = query.contains("target_audience", target_audience)
            
            if use_cases:
                query = query.contains("use_cases", use_cases)
            
            # Text search
            if search_query:
                query = query.or_(
                    f"name.ilike.%{search_query}%,"
                    f"description.ilike.%{search_query}%,"
                    f"short_description.ilike.%{search_query}%"
                )
            
            response = query.limit(limit).offset(offset).order("created_at", desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def get_by_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by category."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("category", category)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_subcategory(self, subcategory: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by subcategory."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("subcategory", subcategory)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_brand(self, brand: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by brand."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("brand", brand)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_price_tier(self, price_tier: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by price tier (budget, mid_range, premium)."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("price_tier", price_tier)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_featured(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get featured products."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("is_featured", True)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_new_arrivals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get new arrival products."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("is_new_arrival", True)
                .eq("is_active", True)
                .limit(limit)
                .order("release_date", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_tags(self, tags: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """Get products matching any of the provided tags."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .contains("tags", tags)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_target_audience(self, audience: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """Get products for specific target audience."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .contains("target_audience", audience)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_use_cases(self, use_cases: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """Get products for specific use cases."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .contains("use_cases", use_cases)
                .eq("is_active", True)
                .limit(limit)
                .order("rating", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_by_ids(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple products by IDs."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .in_("id", product_ids)
                .eq("is_active", True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_all_active(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all active products."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("is_active", True)
                .limit(limit)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data or []
        except Exception:
            return []
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("category")
                .eq("is_active", True)
                .execute()
            )
            categories = set(item["category"] for item in response.data if item.get("category"))
            return sorted(list(categories))
        except Exception:
            return []
    
    def get_all_subcategories(self, category: Optional[str] = None) -> List[str]:
        """Get all unique subcategories, optionally filtered by category."""
        try:
            query = self.client.table(self.table_name).select("subcategory").eq("is_active", True)
            
            if category:
                query = query.eq("category", category)
            
            response = query.execute()
            subcategories = set(item["subcategory"] for item in response.data if item.get("subcategory"))
            return sorted(list(subcategories))
        except Exception:
            return []
    
    def get_all_brands(self) -> List[str]:
        """Get all unique brands."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("brand")
                .eq("is_active", True)
                .execute()
            )
            brands = set(item["brand"] for item in response.data if item.get("brand"))
            return sorted(list(brands))
        except Exception:
            return []
    
    def get_all_manufacturers(self) -> List[str]:
        """Get all unique manufacturers."""
        try:
            response = (
                self.client.table(self.table_name)
                .select("manufacturer")
                .eq("is_active", True)
                .execute()
            )
            manufacturers = set(item["manufacturer"] for item in response.data if item.get("manufacturer"))
            return sorted(list(manufacturers))
        except Exception:
            return []
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product."""
        return self.create(product_data)
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing product."""
        return self.update(product_id, product_data)
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product (soft delete by setting is_active=False)."""
        try:
            self.update(product_id, {"is_active": False})
            return True
        except Exception:
            return False
