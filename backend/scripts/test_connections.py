"""
Test connections to all external services.
Run this script to verify your environment is configured correctly.

Usage:
    python -m scripts.test_connections
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.database.session import get_supabase_client
from src.vector.pinecone_client import get_pinecone_client
from src.services.llm.service import LLMService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_supabase_connection():
    """Test Supabase database connection."""
    logger.info("Testing Supabase Connection...")
    try:
        client = get_supabase_client()
        
        # Test query
        response = client.table("users").select("id").limit(1).execute()
        
        logger.info("✅ Supabase connection successful!")
        logger.info(f"   URL: {settings.database.supabase_url}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {str(e)}")
        return False


def test_pinecone_connection():
    """Test Pinecone vector database connection."""
    logger.info("Testing Pinecone Connection...")
    try:
        pinecone_client = get_pinecone_client()
        index = pinecone_client.get_index()
        
        # Get index stats
        stats = index.describe_index_stats()
        
        logger.info("✅ Pinecone connection successful!")
        logger.info(f"   Index: {settings.vector_db.pinecone_index_name}")
        logger.info(f"   Dimension: {stats.dimension}")
        logger.info(f"   Total vectors: {stats.total_vector_count}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pinecone connection failed: {str(e)}")
        return False


def test_llm_connection():
    """Test LLM service connection."""
    logger.info(f"Testing LLM Connection ({settings.llm.provider})...")
    try:
        llm_service = LLMService()
        
        # Test health check
        is_healthy = llm_service.health_check()
        
        if is_healthy:
            logger.info("✅ LLM connection successful!")
            logger.info(f"   Provider: {settings.llm.provider}")
            if settings.llm.provider == "openai":
                logger.info(f"   Model: {settings.llm.openai.model}")
            else:
                logger.info(f"   Model: {settings.llm.gemini.model}")
            return True
        else:
            logger.error("❌ LLM health check failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ LLM connection failed: {str(e)}")
        return False


def main():
    """Run all connection tests."""
    logger.info("=" * 60)
    logger.info("🚀 SalesMate AI - Connection Tests")
    logger.info("=" * 60)
    
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug Mode: {settings.app.debug}")
    
    results = {
        "Supabase": test_supabase_connection(),
        "Pinecone": test_pinecone_connection(),
        "LLM": test_llm_connection()
    }
    
    logger.info("=" * 60)
    logger.info("📊 Test Results Summary")
    logger.info("=" * 60)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {service}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("🎉 All connections successful! You're ready to go!")
    else:
        logger.warning("⚠️  Some connections failed. Please check your configuration.")
        logger.info("💡 Tips:")
        logger.info("   - Verify your .env file has all required variables")
        logger.info("   - Check API keys are valid and not expired")
        logger.info("   - Ensure services are accessible from your network")
    logger.info("=" * 60)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
