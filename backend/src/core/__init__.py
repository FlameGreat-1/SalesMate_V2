"""
SalesMate MVP - Core Package
Domain models and business logic
"""

from src.core.exceptions import (
    SalesMateException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    ResourceNotFoundError,
    DatabaseError,
    LLMError,
)

__all__ = [
    "SalesMateException",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "ResourceNotFoundError",
    "DatabaseError",
    "LLMError",
]
