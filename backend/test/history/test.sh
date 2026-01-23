#!/bin/bash
# =============================================================================
# History Module - Complete Test Script
# =============================================================================
# Tests: List Conversations, Get Active, Get Detail
# =============================================================================

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
UNIQUE_ID=$(date +%s)
USERNAME="hist_test_${UNIQUE_ID}"
EMAIL="${USERNAME}@example.com"
PASSWORD="SecurePass123!"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  History Module - Test Suite"
echo "============================================"

# Setup
echo -e "${YELLOW}[Setup] Registering test user...${NC}"
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"History User\"}")

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token')

# Create a conversation first
echo -e "${YELLOW}[Setup] Creating a conversation...${NC}"
curl -s -X POST "$BASE_URL/api/v1/chat/start" \
  -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

# 1. List Conversations
echo -e "${YELLOW}[1/3] List Conversations${NC}"
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/history/conversations" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$LIST_RESPONSE" | jq .

if echo "$LIST_RESPONSE" | jq -e '.total >= 1' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ List Conversations successful${NC}"
else
     echo -e "${RED}✗ List Conversations failed (Expected at least 1)${NC}"
     exit 1
fi
echo ""

# 2. Get Active Conversation
echo -e "${YELLOW}[2/3] Get Active Conversation${NC}"
ACTIVE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/history/conversations/active" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$ACTIVE_RESPONSE" | jq .

if echo "$ACTIVE_RESPONSE" | jq -e '.conversation.id' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Get Active Conversation successful${NC}"
     CONV_ID=$(echo "$ACTIVE_RESPONSE" | jq -r '.conversation.id')
else
     echo -e "${RED}✗ Get Active Conversation failed${NC}"
     exit 1
fi
echo ""

# 3. Get Conversation Detail
if [ ! -z "$CONV_ID" ]; then
    echo -e "${YELLOW}[3/3] Get Details for $CONV_ID${NC}"
    DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/history/conversations/$CONV_ID" \
       -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "$DETAIL_RESPONSE" | jq .
    if echo "$DETAIL_RESPONSE" | jq -e '.conversation.id == "'"$CONV_ID"'"' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Get Details successful${NC}"
    else
        echo -e "${RED}✗ Get Details failed${NC}"
        exit 1
    fi
fi
echo ""

echo "============================================"
echo -e "${GREEN}History Module Tests Passed!${NC}"
echo "============================================"
