"""
SalesMate MVP - Custom Exceptions
Business logic exceptions for error handling
"""

from typing import Optional, Any, Dict


class SalesMateException(Exception):
    """Base exception for all SalesMate errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "SALESMATE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(SalesMateException):
    """Authentication-related errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_ERROR", details)


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)
        self.code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """JWT token has expired."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)
        self.code = "TOKEN_EXPIRED"


class TokenInvalidError(AuthenticationError):
    """JWT token is malformed or invalid."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)
        self.code = "TOKEN_INVALID"


class AuthorizationError(SalesMateException):
    """Authorization-related errors."""
    
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ResourceNotFoundError(SalesMateException):
    """Requested resource not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None
    ):
        msg = message or f"{resource_type} with id '{resource_id}' not found"
        super().__init__(msg, "NOT_FOUND", {"resource_type": resource_type, "resource_id": resource_id})


class UserNotFoundError(ResourceNotFoundError):
    """User not found."""
    
    def __init__(self, user_id: str):
        super().__init__("User", user_id)
        self.code = "USER_NOT_FOUND"


class ProductNotFoundError(ResourceNotFoundError):
    """Product not found."""
    
    def __init__(self, product_id: str):
        super().__init__("Product", product_id)
        self.code = "PRODUCT_NOT_FOUND"


class ConversationNotFoundError(ResourceNotFoundError):
    """Conversation not found."""
    
    def __init__(self, conversation_id: str):
        super().__init__("Conversation", conversation_id)
        self.code = "CONVERSATION_NOT_FOUND"


class ValidationError(SalesMateException):
    """Input validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class DuplicateResourceError(SalesMateException):
    """Resource already exists."""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            f"{resource_type} already exists: {identifier}",
            "DUPLICATE_RESOURCE",
            {"resource_type": resource_type, "identifier": identifier}
        )


class EmailAlreadyExistsError(DuplicateResourceError):
    """Email already registered."""
    
    def __init__(self, email: str):
        super().__init__("User", email)
        self.code = "EMAIL_EXISTS"


class DatabaseError(SalesMateException):
    """Database operation errors."""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class DatabaseConnectionError(DatabaseError):
    """Cannot connect to database."""
    
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message)
        self.code = "DATABASE_CONNECTION_ERROR"


class VectorDatabaseError(SalesMateException):
    """Vector database operation errors."""
    
    def __init__(self, message: str = "Vector database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VECTOR_DB_ERROR", details)


class EmbeddingError(SalesMateException):
    """Embedding generation errors."""
    
    def __init__(self, message: str = "Failed to generate embedding", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EMBEDDING_ERROR", details)


class LLMError(SalesMateException):
    """LLM service errors."""
    
    def __init__(self, message: str = "LLM service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "LLM_ERROR", details)


class LLMRateLimitError(LLMError):
    """LLM rate limit exceeded."""
    
    def __init__(self, message: str = "LLM rate limit exceeded"):
        super().__init__(message)
        self.code = "LLM_RATE_LIMIT"


class LLMTimeoutError(LLMError):
    """LLM request timeout."""
    
    def __init__(self, message: str = "LLM request timed out"):
        super().__init__(message)
        self.code = "LLM_TIMEOUT"


class ConversationError(SalesMateException):
    """Conversation-related errors."""
    
    def __init__(self, message: str = "Conversation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONVERSATION_ERROR", details)


class ConversationExpiredError(ConversationError):
    """Conversation session has expired."""
    
    def __init__(self, conversation_id: str):
        super().__init__(
            f"Conversation {conversation_id} has expired",
            {"conversation_id": conversation_id}
        )
        self.code = "CONVERSATION_EXPIRED"


class ConversationClosedError(ConversationError):
    """Conversation is already closed."""
    
    def __init__(self, conversation_id: str):
        super().__init__(
            f"Conversation {conversation_id} is already closed",
            {"conversation_id": conversation_id}
        )
        self.code = "CONVERSATION_CLOSED"


class RateLimitError(SalesMateException):
    """API rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else None
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class ConfigurationError(SalesMateException):
    """Configuration-related errors."""
    
    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class ExternalServiceError(SalesMateException):
    """External service communication errors."""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["service"] = service
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)
