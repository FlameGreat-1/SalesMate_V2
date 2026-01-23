#!/bin/bash
# =============================================================================
# SalesMate AI - Master Test Runner
# =============================================================================
# Runs all module tests in sequence.
# =============================================================================

set -e

# Base directory for tests
TEST_DIR="$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================"
echo "    SalesMate AI - Comprehensive Test Run"
echo "============================================"
echo "Date: $(date)"
echo ""

# Function to run test script
run_test() {
    local script="$1"
    local name="$2"
    
    echo -e "${BLUE}>>> Running $name Tests ($script)...${NC}"
    chmod +x "$script"
    
    if "$script"; then
        echo -e "${GREEN}>>> $name Tests PASSED${NC}"
        echo ""
    else
        echo -e "${RED}>>> $name Tests FAILED${NC}"
        exit 1
    fi
}

run_test "$TEST_DIR/auth/test.sh" "Auth"
run_test "$TEST_DIR/users/test.sh" "Users"
run_test "$TEST_DIR/products/test.sh" "Products"
run_test "$TEST_DIR/chat/test.sh" "Chat"
run_test "$TEST_DIR/history/test.sh" "History"

echo "============================================"
echo -e "${GREEN}    ALL TESTS PASSED SUCCESSFULLY!    ${NC}"
echo "============================================"
