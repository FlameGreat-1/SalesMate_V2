#!/bin/bash

echo "============================================"
echo "  SalesMate AI - Pre-Integration Check"
echo "============================================"
echo "Date: $(date)"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((FAILED++))
    fi
}

echo "============================================"
echo "  1. Running Complete Test Suite"
echo "============================================"
echo ""

./test/run_all.sh > /dev/null 2>&1
print_result $? "All module tests passed"

echo ""
echo "============================================"
echo "  2. Health Check"
echo "============================================"
echo ""

# Check if API is running
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ API is running${NC}"
    echo "$HEALTH_RESPONSE" | jq '.'
    ((PASSED++))
else
    echo -e "${RED}✗ API is not running${NC}"
    echo "Please start the API server: uvicorn src.api.main:app --reload"
    ((FAILED++))
fi

echo ""
echo "============================================"
echo "  3. CORS Configuration"
echo "============================================"
echo ""

# Test CORS for localhost:3000 (common frontend dev server)
CORS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -X OPTIONS \
    http://localhost:8000/api/v1/auth/signup)

if [ "$CORS_RESPONSE" = "200" ]; then
    print_result 0 "CORS configured for localhost:3000"
else
    print_result 1 "CORS not configured properly (Status: $CORS_RESPONSE)"
fi

# Test CORS for localhost:5173 (Vite default)
CORS_RESPONSE_VITE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -X OPTIONS \
    http://localhost:8000/api/v1/auth/signup)

if [ "$CORS_RESPONSE_VITE" = "200" ]; then
    print_result 0 "CORS configured for localhost:5173 (Vite)"
else
    print_result 1 "CORS not configured for Vite (Status: $CORS_RESPONSE_VITE)"
fi

echo ""
echo "============================================"
echo "  4. Authentication Flow"
echo "============================================"
echo ""

# Generate unique test email
TEST_EMAIL="integration_test_$(date +%s)@example.com"
TEST_PASSWORD="Test123!@#"

# Test Signup
echo "Testing Signup..."
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    print_result 0 "Signup successful"
    TOKEN=$(echo "$SIGNUP_RESPONSE" | jq -r '.access_token')
    echo "  Token: ${TOKEN:0:50}..."
else
    print_result 1 "Signup failed"
    echo "  Response: $SIGNUP_RESPONSE"
fi

# Test Login
echo ""
echo "Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    print_result 0 "Login successful"
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
else
    print_result 1 "Login failed"
    echo "  Response: $LOGIN_RESPONSE"
fi

echo ""
echo "============================================"
echo "  5. Protected Endpoints"
echo "============================================"
echo ""

# Test Get Profile
echo "Testing Get Profile..."
PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/users/me)

if echo "$PROFILE_RESPONSE" | grep -q "user"; then
    print_result 0 "Get profile successful"
else
    print_result 1 "Get profile failed"
fi

# Test Product Search
echo ""
echo "Testing Product Search..."
SEARCH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8000/api/v1/products/search?query=laptop&limit=3")

if echo "$SEARCH_RESPONSE" | grep -q "products"; then
    PRODUCT_COUNT=$(echo "$SEARCH_RESPONSE" | jq '.total')
    print_result 0 "Product search successful ($PRODUCT_COUNT products found)"
else
    print_result 1 "Product search failed"
fi

echo ""
echo "============================================"
echo "  6. Chat Functionality"
echo "============================================"
echo ""

# Test Start Conversation
echo "Testing Start Conversation..."
CONV_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/chat/start)

if echo "$CONV_RESPONSE" | grep -q "conversation"; then
    print_result 0 "Start conversation successful"
    CONV_ID=$(echo "$CONV_RESPONSE" | jq -r '.conversation.id')
    echo "  Conversation ID: $CONV_ID"
else
    print_result 1 "Start conversation failed"
fi

# Test Send Message
echo ""
echo "Testing Send Message..."
MESSAGE_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"I need a laptop\",\"conversation_id\":\"$CONV_ID\"}" \
    http://localhost:8000/api/v1/chat/message)

if echo "$MESSAGE_RESPONSE" | grep -q "assistant_message"; then
    print_result 0 "Send message successful"
    AI_RESPONSE=$(echo "$MESSAGE_RESPONSE" | jq -r '.assistant_message.content')
    echo "  AI Response: ${AI_RESPONSE:0:100}..."
else
    print_result 1 "Send message failed"
fi

# Test Streaming (just check if endpoint exists)
echo ""
echo "Testing Streaming Endpoint..."
STREAM_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"message\":\"test\",\"conversation_id\":\"$CONV_ID\"}" \
    http://localhost:8000/api/v1/chat/message/stream)

if [ "$STREAM_RESPONSE" = "200" ]; then
    print_result 0 "Streaming endpoint accessible"
else
    print_result 1 "Streaming endpoint failed (Status: $STREAM_RESPONSE)"
fi

echo ""
echo "============================================"
echo "  7. Conversation History"
echo "============================================"
echo ""

# Test Get Conversations
echo "Testing Get Conversations..."
HISTORY_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/history/conversations)

if echo "$HISTORY_RESPONSE" | grep -q "conversations"; then
    CONV_COUNT=$(echo "$HISTORY_RESPONSE" | jq '.total')
    print_result 0 "Get conversations successful ($CONV_COUNT conversations)"
else
    print_result 1 "Get conversations failed"
fi

# Test Get Active Conversation
echo ""
echo "Testing Get Active Conversation..."
ACTIVE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/history/active)

if echo "$ACTIVE_RESPONSE" | grep -q "conversation"; then
    print_result 0 "Get active conversation successful"
else
    print_result 1 "Get active conversation failed"
fi

echo ""
echo "============================================"
echo "  Summary"
echo "============================================"
echo ""
echo -e "Tests Passed: ${GREEN}$PASSED${NC}"
echo -e "Tests Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  ✓ ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}  Backend is ready for frontend integration${NC}"
    echo -e "${GREEN}============================================${NC}"
    exit 0
else
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  ✗ SOME CHECKS FAILED${NC}"
    echo -e "${RED}  Please fix the issues before integration${NC}"
    echo -e "${RED}============================================${NC}"
    exit 1
fi
