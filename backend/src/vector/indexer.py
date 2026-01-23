from typing import List, Dict, Any
from src.vector.pinecone_client import get_pinecone_client
from src.vector.embeddings import get_embedding_service
from src.repositories.product import ProductRepository
from src.core.exceptions import VectorDatabaseError


class ProductIndexer:
    def __init__(self):
        self.pinecone_client = get_pinecone_client()
        self.embedding_service = get_embedding_service()
        self.product_repo = ProductRepository()
    
    def _create_product_text(self, product: Dict[str, Any]) -> str:
        parts = [
            product.get("name", ""),
            product.get("brand", ""),
            product.get("category", ""),
            product.get("description", ""),
        ]
        
        features = product.get("features", [])
        if features:
            parts.append(" ".join(features))
        
        return " ".join(filter(None, parts))
    
    def index_product(self, product: Dict[str, Any]) -> bool:
        try:
            product_text = self._create_product_text(product)
            embedding = self.embedding_service.generate_embedding(product_text)
            
            metadata = {
                "product_id": product["id"],
                "sku": product["sku"],
                "name": product["name"],
                "category": product["category"],
                "brand": product["brand"],
                "price": float(product["price"]),
                "rating": float(product.get("rating", 0.0)) if product.get("rating") else 0.0,
            }
            
            index = self.pinecone_client.get_index()
            index.upsert(vectors=[(product["id"], embedding, metadata)])
            
            return True
        except Exception as e:
            raise VectorDatabaseError(f"Failed to index product: {str(e)}")
    
    def index_products(self, products: List[Dict[str, Any]], batch_size: int = 100) -> int:
        indexed_count = 0
        
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            vectors = []
            
            try:
                texts = [self._create_product_text(p) for p in batch]
                embeddings = self.embedding_service.generate_embeddings(texts)
                
                for product, embedding in zip(batch, embeddings):
                    metadata = {
                        "product_id": product["id"],
                        "sku": product["sku"],
                        "name": product["name"],
                        "category": product["category"],
                        "brand": product["brand"],
                        "price": float(product["price"]),
                        "rating": float(product.get("rating", 0.0)) if product.get("rating") else 0.0,
                    }
                    vectors.append((product["id"], embedding, metadata))
                
                index = self.pinecone_client.get_index()
                index.upsert(vectors=vectors)
                indexed_count += len(vectors)
                
            except Exception as e:
                raise VectorDatabaseError(f"Failed to index batch: {str(e)}")
        
        return indexed_count
    
    def index_all_products(self) -> int:
        products = self.product_repo.get_all_active(limit=10000)
        return self.index_products(products)
    
    def delete_product(self, product_id: str) -> bool:
        try:
            index = self.pinecone_client.get_index()
            index.delete(ids=[product_id])
            return True
        except Exception:
            return False
    
    def clear_index(self) -> bool:
        try:
            index = self.pinecone_client.get_index()
            index.delete(delete_all=True)
            return True
        except Exception:
            return False


def get_product_indexer() -> ProductIndexer:
    return ProductIndexer()
