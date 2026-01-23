from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def create(cls, items: List[T], total: int, limit: int, offset: int):
        return cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + len(items)) < total
        )


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    status_code: int


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, bool]
