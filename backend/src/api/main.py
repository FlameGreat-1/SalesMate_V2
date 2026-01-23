from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import api_router
from src.api.middleware.cors import setup_cors
from src.api.middleware.request_logger import RequestLoggerMiddleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.middleware.rate_limiter import RateLimiterMiddleware
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting SalesMate AI API...")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"LLM Provider: {settings.llm.provider}")
    
    # Initialize services (lazy loading will happen on first use)
    logger.info("Services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SalesMate AI API...")


# Create FastAPI application
app = FastAPI(
    title="SalesMate AI API",
    description="AI-powered sales assistant for electronics e-commerce",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Setup CORS
setup_cors(app)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(
    RateLimiterMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SalesMate AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
        log_level=settings.app.log_level.lower()
    )
