import time
from typing import Callable, Dict
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter middleware.
    
    For production, use Redis-based rate limiting (e.g., slowapi, fastapi-limiter).
    This implementation is suitable for single-instance deployments.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request.
        Uses X-Forwarded-For header if available, otherwise client IP.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _clean_old_requests(self, requests: list, window_seconds: int) -> list:
        """Remove requests older than the time window."""
        current_time = time.time()
        return [req_time for req_time in requests if current_time - req_time < window_seconds]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Clean old requests
        self.minute_requests[client_id] = self._clean_old_requests(
            self.minute_requests[client_id], 60
        )
        self.hour_requests[client_id] = self._clean_old_requests(
            self.hour_requests[client_id], 3600
        )
        
        # Check minute limit
        if len(self.minute_requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                headers={"Retry-After": "60"}
            )
        
        # Check hour limit
        if len(self.hour_requests[client_id]) >= self.requests_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour",
                headers={"Retry-After": "3600"}
            )
        
        # Record this request
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(self.minute_requests[client_id])
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(self.hour_requests[client_id])
        )
        
        return response
