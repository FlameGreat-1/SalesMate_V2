from fastapi import APIRouter
from src.api.routes import health, auth, users, products, chat, history

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(history.router, prefix="/history", tags=["History"])

__all__ = ["api_router"]
