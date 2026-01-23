from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    In production, restrict origins to specific domains.
    In development, allow all origins for testing.
    """
    
    if settings.app.environment == "production":
        allowed_origins = [
            "https://yourdomain.com",
            "https://www.yourdomain.com",
        ]
    else:
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Requested-With",
        ],
        expose_headers=["Content-Length", "X-Request-ID"],
        max_age=600,
    )
