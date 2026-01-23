import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming HTTP requests and responses.
    Logs request method, path, status code, and processing time.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", "N/A")
        start_time = time.time()
        
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[Request ID: {request_id}]"
        )
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Duration: {process_time:.3f}s "
                f"[Request ID: {request_id}]"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"Error: {str(e)} "
                f"Duration: {process_time:.3f}s "
                f"[Request ID: {request_id}]"
            )
            raise
