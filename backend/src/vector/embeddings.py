from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import settings
from src.core.exceptions import DatabaseError


class EmbeddingService:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            try:
                self._model = SentenceTransformer(settings.vector_db.embedding_model)
            except Exception as e:
                raise DatabaseError(f"Failed to load embedding model: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            raise DatabaseError(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as e:
            raise DatabaseError(f"Failed to generate embeddings: {str(e)}")
    
    def get_dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
