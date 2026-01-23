from datetime import datetime
from fastapi import APIRouter, Depends
from src.api.models.common import HealthCheckResponse
from src.services.llm.service import LLMService
from src.database.session import get_supabase_client
from src.vector.pinecone_client import get_pinecone_client
from src.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify all services are operational.
    
    Returns:
        HealthCheckResponse with status of all services
    """
    services_status = {}
    
    # Check database
    try:
        supabase = get_supabase_client()
        supabase.table("users").select("id").limit(1).execute()
        services_status["database"] = True
    except Exception:
        services_status["database"] = False
    
    # Check vector database
    try:
        pinecone_client = get_pinecone_client()
        index = pinecone_client.get_index()
        index.describe_index_stats()
        services_status["vector_db"] = True
    except Exception:
        services_status["vector_db"] = False
    
    # Check LLM service
    try:
        llm_service = LLMService()
        services_status["llm"] = llm_service.health_check()
    except Exception:
        services_status["llm"] = False
    
    # Overall status
    all_healthy = all(services_status.values())
    status = "healthy" if all_healthy else "degraded"
    
    return HealthCheckResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        services=services_status
    )


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SalesMate AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }
