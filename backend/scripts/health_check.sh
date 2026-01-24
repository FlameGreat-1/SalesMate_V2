#!/bin/bash

echo "Running health checks..."

# Check API health
echo -n "API Health: "
curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ OK"
else
    echo "✗ FAILED"
    exit 1
fi

# Check database connection
echo -n "Database: "
python -c "
from src.repositories.product import ProductRepository
repo = ProductRepository()
products = repo.get_all()
print('✓ OK' if len(products) > 0 else '✗ FAILED')
"

# Check Pinecone
echo -n "Pinecone: "
python -c "
from src.vector.pinecone_client import get_pinecone_client
client = get_pinecone_client()
index = client.get_index()
stats = index.describe_index_stats()
print('✓ OK' if stats.total_vector_count > 0 else '✗ FAILED')
"

# Check Gemini
echo -n "Gemini LLM: "
python -c "
from src.services.llm.service import LLMService
llm = LLMService()
result = llm.health_check()
print('✓ OK' if result else '✗ FAILED')
"

echo ""
echo "All health checks passed!"
