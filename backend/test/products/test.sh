#!/bin/bash
# =============================================================================
# Products Module - Complete Test Script
# =============================================================================
# Tests: Search, Details, Recommendations, Meta
# =============================================================================

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
UNIQUE_ID=$(date +%s)
USERNAME="prod_test_${UNIQUE_ID}"
EMAIL="${USERNAME}@example.com"
PASSWORD="SecurePass123!"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  Products Module - Test Suite"
echo "============================================"

# Setup: Register
echo -e "${YELLOW}[Setup] Registering test user...${NC}"
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"Product Test\"}")

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token')

# 1. Search Products
echo -e "${YELLOW}[1/4] Search Products${NC}"
SEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/products/search" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop", "limit": 5}')

echo "$SEARCH_RESPONSE" | jq .
# Basic check: if 'products' array exists
if echo "$SEARCH_RESPONSE" | jq -e '.products' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Search successful${NC}"
     # Capture a product ID for next tests if available
     PRODUCT_ID=$(echo "$SEARCH_RESPONSE" | jq -r '.products[0].id // empty')
else
     echo -e "${RED}✗ Search failed${NC}"
     exit 1
fi
echo ""

# 2. Get Product Details (if products exist)
if [ ! -z "$PRODUCT_ID" ] && [ "$PRODUCT_ID" != "null" ]; then
    echo -e "${YELLOW}[2/4] Get Product Details ($PRODUCT_ID)${NC}"
    DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/products/$PRODUCT_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "$DETAIL_RESPONSE" | jq .
    if echo "$DETAIL_RESPONSE" | jq -e '.id == "'"$PRODUCT_ID"'"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Get Details successful${NC}"
    else
        echo -e "${RED}✗ Get Details failed${NC}"
    fi
else
    echo -e "${YELLOW}[2/4] Skipping Get Details (No products found)${NC}"
fi
echo ""

# 3. Get Recommendations
echo -e "${YELLOW}[3/4] Get Personalized Recommendations${NC}"
REC_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/products/recommendations/personalized?limit=3" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$REC_RESPONSE" | jq .
if echo "$REC_RESPONSE" | jq -e '.products' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Recommendations successful${NC}"
else
     echo -e "${RED}✗ Recommendations failed${NC}"
fi
echo ""

# 4. Get Meta Data
echo -e "${YELLOW}[4/4] Get Categories Metadata${NC}"
META_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/products/meta/categories" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$META_RESPONSE" | jq .
if echo "$META_RESPONSE" | jq -e 'type == "array"' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Metadata successful${NC}"
else
     echo -e "${RED}✗ Metadata failed${NC}"
     exit 1
fi
echo ""

echo "============================================"
echo -e "${GREEN}Products Module Tests Passed!${NC}"
echo "============================================"
