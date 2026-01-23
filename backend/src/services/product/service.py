from typing import List, Dict, Any, Optional

from src.core.schemas.product import ProductResponse, ProductFilter
from src.core.schemas.profile import ProfileResponse
from src.repositories.product import ProductRepository
from src.vector.search import VectorSearch
from src.vector.indexer import ProductIndexer
from src.services.product.recommendation import RecommendationEngine
from src.config import settings
from src.core.exceptions import ProductNotFoundError

from src.utils.logger import get_logger
logger = get_logger(__name__)

class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.vector_search = VectorSearch()
        self.indexer = ProductIndexer()
        self.recommendation_engine = RecommendationEngine()
        self._initialize_vector_store()
    
    def _initialize_vector_store(self) -> None:
        try:
            if settings.vector_db.enable_auto_indexing:
                from src.vector.pinecone_client import get_pinecone_client
                pinecone_client = get_pinecone_client()
                index = pinecone_client.get_index()
                stats = index.describe_index_stats()
                
                if stats.total_vector_count == 0:
                    logger.info("Vector store empty, indexing products...")
                    count = self.indexer.index_all_products()
                    logger.info(f"Indexed {count} products")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
    
    def get_product_by_id(self, product_id: str) -> ProductResponse:
        product = self.product_repo.get_by_id(product_id)
        return ProductResponse(**product)
    
    def get_product_by_sku(self, sku: str) -> Optional[ProductResponse]:
        product = self.product_repo.get_by_sku(sku)
        if product:
            return ProductResponse(**product)
        return None
    
    def get_all_products(self, limit: int = 1000) -> List[ProductResponse]:
        products = self.product_repo.get_all_active(limit)
        return [ProductResponse(**p) for p in products]
    
    def search_products(
        self,
        query: str,
        profile: Optional[ProfileResponse] = None,
        filters: Optional[ProductFilter] = None,
    ) -> List[ProductResponse]:
        category = filters.category if filters else None
        brand = filters.brand if filters else None
        min_price = filters.min_price if filters else None
        max_price = filters.max_price if filters else None
        limit = filters.limit if filters else 10
        
        return self.recommendation_engine.search_products(
            query=query,
            profile=profile,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            limit=limit
        )
    
    def get_recommendations_for_user(
        self,
        profile: ProfileResponse,
        limit: int = 5
    ) -> List[ProductResponse]:
        return self.recommendation_engine.get_recommendations_for_user(profile, limit)
    
    def get_similar_products(
        self,
        product_id: str,
        limit: int = 3
    ) -> List[ProductResponse]:
        product = self.get_product_by_id(product_id)
        return self.recommendation_engine.get_similar_products(product, limit)
    
    def get_products_by_category(
        self,
        category: str,
        limit: int = 20
    ) -> List[ProductResponse]:
        products = self.product_repo.get_by_category(category, limit)
        return [ProductResponse(**p) for p in products]
    
    def get_products_by_ids(self, product_ids: List[str]) -> List[ProductResponse]:
        products = self.product_repo.get_by_ids(product_ids)
        return [ProductResponse(**p) for p in products]
    
    # def get_product_summary_for_llm(
    #     self,
    #     product: ProductResponse,
    #     user_budget: Optional[float] = None
    # ) -> str:
    #     discount_info = ""
    #     if product.original_price and product.original_price > product.price:
    #         discount_pct = ((product.original_price - product.price) / product.original_price) * 100
    #         savings = product.original_price - product.price
    #         discount_info = f" ({discount_pct:.0f}% off, save ${savings:.2f})"
        
    #     stock_status = "In stock" if product.stock_quantity > 0 else "Out of stock"
    #     if product.stock_quantity > 0 and product.stock_quantity <= 5:
    #         stock_status = f"Limited stock ({product.stock_quantity} left)"
    #     elif product.stock_quantity > 5:
    #         stock_status = "Plenty available"
        
    #     base_summary = (
    #         f"{product.name} by {product.brand} - ${product.price:.2f}{discount_info}. "
    #         f"Category: {product.category}. "
    #         f"Rating: {product.rating or 0.0}/5.0 ({product.review_count} reviews). "
    #     )
        
    #     if product.features:
    #         features_str = ", ".join(product.features[:3])
    #         base_summary += f"Key features: {features_str}. "
        
    #     base_summary += f"Stock: {stock_status}."
        
    #     if user_budget is not None:
    #         if product.price <= user_budget:
    #             base_summary += f" [Within user's ${user_budget:.2f} budget]"
    #         else:
    #             over_amount = product.price - user_budget
    #             base_summary += f" [${over_amount:.2f} above user's ${user_budget:.2f} budget]"
        
    #     return base_summary
    
    # def get_products_summary_for_llm(
    #     self,
    #     products: List[ProductResponse],
    #     user_budget: Optional[float] = None
    # ) -> str:
    #     if not products:
    #         return "No products available."
        
    #     summaries = []
    #     for i, product in enumerate(products, 1):
    #         summary = f"{i}. {self.get_product_summary_for_llm(product, user_budget)}"
    #         summaries.append(summary)
        
    #     return "\n".join(summaries)
    
    def reindex_products(self) -> int:
        logger.info("Starting product reindexing...")
        count = self.indexer.index_all_products()
        logger.info(f"Reindexed {count} products")
        return count
    
    def index_product(self, product_id: str) -> bool:
        product = self.product_repo.get_by_id(product_id)
        return self.indexer.index_product(product)
    
    def get_available_categories(self) -> List[str]:
        products = self.get_all_products()
        categories = set(p.category for p in products)
        return sorted(list(categories))
    
    def get_available_brands(self) -> List[str]:
        products = self.get_all_products()
        brands = set(p.brand for p in products)
        return sorted(list(brands))


def get_product_service() -> ProductService:
    return ProductService()
