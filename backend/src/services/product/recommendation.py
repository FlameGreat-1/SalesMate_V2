from typing import List, Dict, Any, Optional
from src.core.schemas.profile import ProfileResponse
from src.core.schemas.product import ProductResponse
from src.vector.search import VectorSearch
from src.repositories.product import ProductRepository


class RecommendationEngine:
    def __init__(self):
        self.vector_search = VectorSearch()
        self.product_repo = ProductRepository()
    
    def get_recommendations_for_user(
        self,
        profile: ProfileResponse,
        limit: int = 5
    ) -> List[ProductResponse]:
        query = self._build_user_query(profile)
        
        filters = self._build_user_filters(profile)
        
        search_limit = limit * 3
        vector_results = self.vector_search.search(
            query=query,
            top_k=search_limit,
            min_score=0.5,
            filters=filters
        )
        
        product_ids = [r["product_id"] for r in vector_results]
        products = self.product_repo.get_by_ids(product_ids)
        
        products_with_scores = []
        score_map = {r["product_id"]: r["score"] for r in vector_results}
        
        for product in products:
            product_dict = product if isinstance(product, dict) else product.__dict__
            product_response = ProductResponse(**product_dict)
            product_response.similarity_score = score_map.get(product_response.id, 0.0)
            products_with_scores.append(product_response)
        
        ranked_products = self._rank_by_budget(products_with_scores, profile)
        
        return ranked_products[:limit]
    
    def get_similar_products(
        self,
        product: ProductResponse,
        limit: int = 3
    ) -> List[ProductResponse]:
        query = self._build_product_query(product)
        
        filters = {"category": {"$eq": product.category}}
        
        vector_results = self.vector_search.search(
            query=query,
            top_k=limit + 5,
            min_score=0.6,
            filters=filters
        )
        
        similar_products = []
        for result in vector_results:
            if result["product_id"] == product.id:
                continue
            
            product_data = self.product_repo.get_by_id(result["product_id"])
            if product_data:
                product_dict = product_data if isinstance(product_data, dict) else product_data.__dict__
                similar_product = ProductResponse(**product_dict)
                similar_product.similarity_score = result["score"]
                similar_products.append(similar_product)
            
            if len(similar_products) >= limit:
                break
        
        return similar_products
    
    def search_products(
        self,
        query: str,
        profile: Optional[ProfileResponse] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10
    ) -> List[ProductResponse]:
        filters = {}
        
        if category:
            filters["category"] = {"$eq": category}
        
        if brand:
            filters["brand"] = {"$eq": brand}
        
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            filters["price"] = price_filter
        
        search_limit = limit * 2
        vector_results = self.vector_search.search(
            query=query,
            top_k=search_limit,
            min_score=0.4,
            filters=filters if filters else None
        )
        
        product_ids = [r["product_id"] for r in vector_results]
        products = self.product_repo.get_by_ids(product_ids)
        
        products_with_scores = []
        score_map = {r["product_id"]: r["score"] for r in vector_results}
        
        for product in products:
            product_dict = product if isinstance(product, dict) else product.__dict__
            product_response = ProductResponse(**product_dict)
            product_response.similarity_score = score_map.get(product_response.id, 0.0)
            products_with_scores.append(product_response)
        
        if profile:
            products_with_scores = self._rank_by_budget(products_with_scores, profile)
        else:
            products_with_scores.sort(key=lambda p: p.similarity_score, reverse=True)
        
        return products_with_scores[:limit]
    
    def _build_user_query(self, profile: ProfileResponse) -> str:
        query_parts = []
        
        if profile.preferred_categories:
            categories_str = ", ".join(profile.preferred_categories[:3])
            query_parts.append(f"Categories: {categories_str}")
        
        if profile.feature_priorities:
            top_features = sorted(
                profile.feature_priorities.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            features_str = ", ".join([f[0] for f in top_features])
            query_parts.append(f"Features: {features_str}")
        
        if profile.preferred_brands:
            brands_str = ", ".join(profile.preferred_brands[:3])
            query_parts.append(f"Brands: {brands_str}")
        
        return " ".join(query_parts) if query_parts else "recommended products"
    
    def _build_product_query(self, product: ProductResponse) -> str:
        query_parts = [
            product.name,
            product.brand,
            product.category,
        ]
        
        if product.features:
            query_parts.extend(product.features[:5])
        
        return " ".join(query_parts)
    
    def _build_user_filters(self, profile: ProfileResponse) -> Optional[Dict[str, Any]]:
        filters = {}
        
        if profile.preferred_categories:
            filters["category"] = {"$in": profile.preferred_categories}
        
        return filters if filters else None
    
    def _rank_by_budget(
        self,
        products: List[ProductResponse],
        profile: ProfileResponse
    ) -> List[ProductResponse]:
        if not profile.budget_max:
            return sorted(products, key=lambda p: p.similarity_score, reverse=True)
        
        within_budget = [p for p in products if p.price <= profile.budget_max]
        above_budget = [p for p in products if p.price > profile.budget_max]
        
        within_budget.sort(key=lambda p: p.similarity_score, reverse=True)
        above_budget.sort(key=lambda p: p.similarity_score, reverse=True)
        
        return within_budget + above_budget


def get_recommendation_engine() -> RecommendationEngine:
    return RecommendationEngine()
