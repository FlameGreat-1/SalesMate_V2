from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.exceptions import (
    SalesMateException,
    ValidationError,
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    DuplicateResourceError,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware.
    Catches all exceptions and returns standardized JSON error responses.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "ValidationError",
                    "message": e.message,
                    "code": e.code,
                    "details": e.details,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                }
            )
        
        except ResourceNotFoundError as e:
            logger.warning(f"Not found: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "error": "NotFoundError",
                    "message": e.message,
                    "code": e.code,
                    "details": e.details,
                    "status_code": status.HTTP_404_NOT_FOUND,
                }
            )
        
        except AuthenticationError as e:
            logger.warning(f"Unauthorized: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "UnauthorizedError",
                    "message": e.message,
                    "code": e.code,
                    "details": e.details,
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                }
            )
        
        except AuthorizationError as e:
            logger.warning(f"Forbidden: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "ForbiddenError",
                    "message": e.message,
                    "code": e.code,
                    "details": e.details,
                    "status_code": status.HTTP_403_FORBIDDEN,
                }
            )
        
        except DuplicateResourceError as e:
            logger.warning(f"Conflict: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "ConflictError",
                    "message": e.message,
                    "code": e.code,
                    "details": e.details,
                    "status_code": status.HTTP_409_CONFLICT,
                }
            )
        
        except SalesMateException as e:
            logger.error(f"Application error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": e.__class__.__name__,
                    "message": e.message,
                    "code": e.code,
                    "details": e.details,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
        
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )
