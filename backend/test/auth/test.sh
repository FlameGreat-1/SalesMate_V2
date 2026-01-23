#!/bin/bash
set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
UNIQUE_ID=$(date +%s)
EMAIL="test_${UNIQUE_ID}@example.com"
PASSWORD="SecurePass123!"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  Auth Module "
echo "============================================"
echo "User: $EMAIL"
echo ""

# 1. Signup with better error handling
echo -e "${YELLOW}[1/3] Testing Signup${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"Test User\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "201" ]; then
    if echo "$BODY" | jq -e '.access_token' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Signup successful${NC}"
        ACCESS_TOKEN=$(echo "$BODY" | jq -r '.access_token')
    else
        echo -e "${RED}✗ Invalid response format${NC}"
        echo "$BODY"
        exit 1
    fi
else
    echo -e "${RED}✗ Signup failed (HTTP $HTTP_CODE)${NC}"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
    exit 1
fi
echo ""

# 2. Login
echo -e "${YELLOW}[2/3] Testing Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
else
    echo -e "${RED}✗ Login failed${NC}"
    echo "$LOGIN_RESPONSE" | jq .
    exit 1
fi
echo ""

# 3. Get Me 
echo -e "${YELLOW}[3/3] Testing Get Current User${NC}"
ME_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$ME_RESPONSE" | jq -e '.user.email' > /dev/null 2>&1; then
    RETURNED_EMAIL=$(echo "$ME_RESPONSE" | jq -r '.user.email')
    if [ "$RETURNED_EMAIL" = "$EMAIL" ]; then
        echo -e "${GREEN}✓ Get Me successful${NC}"
    else
        echo -e "${RED}✗ Email mismatch${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Get Me failed${NC}"
    echo "$ME_RESPONSE" | jq .
    exit 1
fi
echo ""

echo "============================================"
echo -e "${GREEN}All Auth Tests Passed!${NC}"
echo "============================================"
