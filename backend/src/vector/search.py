from typing import List, Dict, Any, Optional
from src.vector.pinecone_client import get_pinecone_client
from src.vector.embeddings import get_embedding_service
from src.repositories.product import ProductRepository
from src.core.exceptions import VectorDatabaseError


class VectorSearch:
    def __init__(self):
        self.pinecone_client = get_pinecone_client()
        self.embedding_service = get_embedding_service()
        self.product_repo = ProductRepository()
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.embedding_service.generate_embedding(query)
            
            index = self.pinecone_client.get_index()
            
            search_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "include_metadata": True,
            }
            
            if filters:
                search_params["filter"] = filters
            
            results = index.query(**search_params)
            
            filtered_results = [
                {
                    "product_id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
                if match.score >= min_score
            ]
            
            return filtered_results
            
        except Exception as e:
            raise VectorDatabaseError(f"Vector search failed: {str(e)}")
    
    def search_with_products(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        vector_results = self.search(query, top_k, min_score, filters)
        
        if not vector_results:
            return []
        
        product_ids = [r["product_id"] for r in vector_results]
        products = self.product_repo.get_by_ids(product_ids)
        
        product_map = {p["id"]: p for p in products}
        
        results = []
        for vector_result in vector_results:
            product_id = vector_result["product_id"]
            if product_id in product_map:
                product = product_map[product_id]
                product["similarity_score"] = vector_result["score"]
                results.append(product)
        
        return results
    
    def search_by_category(
        self,
        query: str,
        category: str,
        top_k: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        filters = {"category": {"$eq": category}}
        return self.search_with_products(query, top_k, min_score, filters)
    
    def search_by_price_range(
        self,
        query: str,
        min_price: float,
        max_price: float,
        top_k: int = 10,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        filters = {
            "price": {
                "$gte": min_price,
                "$lte": max_price
            }
        }
        return self.search_with_products(query, top_k, min_score, filters)
    
    def find_similar_products(
        self,
        product_id: str,
        top_k: int = 5,
        min_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        try:
            index = self.pinecone_client.get_index()
            
            fetch_result = index.fetch(ids=[product_id])
            if not fetch_result.vectors or product_id not in fetch_result.vectors:
                return []
            
            product_vector = fetch_result.vectors[product_id].values
            
            results = index.query(
                vector=product_vector,
                top_k=top_k + 1,
                include_metadata=True
            )
            
            similar_products = [
                {
                    "product_id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
                if match.id != product_id and match.score >= min_score
            ]
            
            return similar_products[:top_k]
            
        except Exception as e:
            raise VectorDatabaseError(f"Similar product search failed: {str(e)}")


def get_vector_search() -> VectorSearch:
    return VectorSearch()
