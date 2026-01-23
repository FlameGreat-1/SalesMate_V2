#!/bin/bash
# =============================================================================
# Chat Module - Complete Test Script
# =============================================================================
# Tests: Start Chat, Send Message
# =============================================================================

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
UNIQUE_ID=$(date +%s)
USERNAME="chat_test_${UNIQUE_ID}"
EMAIL="${USERNAME}@example.com"
PASSWORD="SecurePass123!"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  Chat Module - Test Suite"
echo "============================================"

# Setup
echo -e "${YELLOW}[Setup] Registering test user...${NC}"
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"Chat User\"}")

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token')

# 1. Start Conversation
echo -e "${YELLOW}[1/2] Start Conversation${NC}"
START_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/start" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$START_RESPONSE" | jq .
CONV_ID=$(echo "$START_RESPONSE" | jq -r '.conversation.id')

if [ "$CONV_ID" != "null" ]; then
    echo -e "${GREEN}✓ Conversation Started: $CONV_ID${NC}"
else
    echo -e "${RED}✗ Start Conversation failed${NC}"
    exit 1
fi
echo ""

# 2. Send Message
echo -e "${YELLOW}[2/2] Send Message (Hello)${NC}"
MSG_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/message" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Hello, looks like I need a laptop\", \"conversation_id\": \"$CONV_ID\"}")

echo "$MSG_RESPONSE" | jq .

if echo "$MSG_RESPONSE" | jq -e '.assistant_message.content' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Message sent successfully${NC}"
else
    echo -e "${RED}✗ Message failed${NC}"
    exit 1
fi
echo ""

echo "============================================"
echo -e "${GREEN}Chat Module Tests Passed!${NC}"
echo "============================================"
