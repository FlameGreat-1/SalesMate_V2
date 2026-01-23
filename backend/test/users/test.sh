#!/bin/bash
# =============================================================================
# Users Module - Complete Test Script
# =============================================================================
# Tests: Profile, Budget, Preferences
# =============================================================================

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
UNIQUE_ID=$(date +%s)
USERNAME="user_test_${UNIQUE_ID}"
EMAIL="${USERNAME}@example.com"
PASSWORD="SecurePass123!"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  Users Module - Test Suite"
echo "============================================"

# Setup: Register
echo -e "${YELLOW}[Setup] Registering test user...${NC}"
AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"User Test\"}")

ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token')
if [ "$ACCESS_TOKEN" == "null" ]; then
    echo -e "${RED}Setup failed: Could not register${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Setup complete${NC}"
echo ""

# 1. Get Profile
echo -e "${YELLOW}[1/4] Get Profile${NC}"
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/users/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$PROFILE_RESPONSE" | jq .
if echo "$PROFILE_RESPONSE" | jq -e '.user.email == "'"$EMAIL"'"' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Get Profile successful${NC}"
else
     echo -e "${RED}✗ Get Profile failed${NC}"
     exit 1
fi
echo ""

# 2. Update Profile
echo -e "${YELLOW}[2/4] Update Profile${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/users/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Updated Name"}')

echo "$UPDATE_RESPONSE" | jq .
if echo "$UPDATE_RESPONSE" | jq -e '.full_name == "Updated Name"' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Update Profile successful${NC}"
else
     echo -e "${RED}✗ Update Profile failed${NC}"
     exit 1
fi
echo ""

# 3. Update Budget
echo -e "${YELLOW}[3/4] Update Budget${NC}"
BUDGET_RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/v1/users/budget" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"budget_min": 100, "budget_max": 2000}')

echo "$BUDGET_RESPONSE" | jq .
if echo "$BUDGET_RESPONSE" | jq -e '.budget_max == 2000.0' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Update Budget successful${NC}"
else
     echo -e "${RED}✗ Update Budget failed${NC}"
     exit 1
fi
echo ""

# 4. Update Preferences
echo -e "${YELLOW}[4/4] Update Preferences${NC}"
PREF_RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/v1/users/preferences" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"preferred_categories": ["Laptops"]}')

echo "$PREF_RESPONSE" | jq .
if echo "$PREF_RESPONSE" | jq -e '.preferred_categories[0] == "Laptops"' > /dev/null 2>&1; then
     echo -e "${GREEN}✓ Update Preferences successful${NC}"
else
     echo -e "${RED}✗ Update Preferences failed${NC}"
     exit 1
fi
echo ""

echo "============================================"
echo -e "${GREEN}Users Module Tests Passed!${NC}"
echo "============================================"
