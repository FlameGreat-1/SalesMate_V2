#!/bin/bash
set -e

echo "============================================"
echo "  SalesMate AI - Starting Deployment"
echo "============================================"
echo "Date: $(date)"
echo ""

# Wait for dependencies to be ready
echo ">>> Waiting for services to be ready..."
sleep 5

# Test connections
echo ""
echo ">>> Testing connections..."
python scripts/test_connections.py
if [ $? -ne 0 ]; then
    echo "❌ Connection test failed!"
    exit 1
fi
echo "✓ All connections successful"

# Check if database needs seeding
echo ""
echo ">>> Checking database status..."
PRODUCT_COUNT=$(python -c "
from src.repositories.product import ProductRepository
repo = ProductRepository()
products = repo.get_all()
print(len(products))
" 2>/dev/null || echo "0")

if [ "$PRODUCT_COUNT" -eq "0" ]; then
    echo ">>> Database is empty. Seeding products..."
    python scripts/seed_database.py
    if [ $? -ne 0 ]; then
        echo "❌ Database seeding failed!"
        exit 1
    fi
    echo "✓ Database seeded successfully"
else
    echo "✓ Database already contains $PRODUCT_COUNT products"
fi

# Check if Pinecone index needs population
echo ""
echo ">>> Checking Pinecone index status..."
PINECONE_COUNT=$(python -c "
from src.vector.pinecone_client import get_pinecone_client
client = get_pinecone_client()
stats = client.describe_index_stats()
print(stats.total_vector_count)
" 2>/dev/null || echo "0")

if [ "$PINECONE_COUNT" -eq "0" ]; then
    echo ">>> Pinecone index is empty. Indexing products..."
    python scripts/index_products_pinecone.py
    if [ $? -ne 0 ]; then
        echo "❌ Pinecone indexing failed!"
        exit 1
    fi
    echo "✓ Pinecone indexed successfully"
else
    echo "✓ Pinecone already contains $PINECONE_COUNT vectors"
fi

# Start the application
echo ""
echo "============================================"
echo "  Starting SalesMate AI API Server"
echo "============================================"
echo ""

exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --log-level ${LOG_LEVEL:-info}
