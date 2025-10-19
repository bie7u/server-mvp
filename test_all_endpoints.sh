#!/bin/bash
# test_all_endpoints.sh - Comprehensive API endpoint testing
# Tests all documented endpoints with proper authentication

set -e

BASE_URL="${API_BASE_URL:-http://localhost:8000}"
COOKIES_FILE="test_cookies.txt"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test credentials (you may need to create these users first)
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"
USER_EMAIL="${USER_EMAIL:-user@example.com}"
USER_PASSWORD="${USER_PASSWORD:-user123}"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Comprehensive API Endpoint Testing      ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║ Base URL: ${BASE_URL}${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

# Helper function to test endpoint
test_endpoint() {
  local test_name=$1
  local method=$2
  local endpoint=$3
  local data=$4
  local expected_status=$5
  local use_cookies=$6
  
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  
  echo -e "${YELLOW}[Test $TOTAL_TESTS] $test_name${NC}"
  
  local curl_cmd="curl -s -X $method $BASE_URL$endpoint"
  
  if [ "$data" != "null" ]; then
    curl_cmd="$curl_cmd -H 'Content-Type: application/json' -d '$data'"
  fi
  
  if [ "$use_cookies" = "true" ]; then
    curl_cmd="$curl_cmd -b $COOKIES_FILE"
  fi
  
  curl_cmd="$curl_cmd -w '\n%{http_code}'"
  
  response=$(eval $curl_cmd)
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$http_code" = "$expected_status" ]; then
    echo -e "${GREEN}✓ PASS - HTTP $http_code${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    if [ "$body" != "" ] && [ "$http_code" != "204" ]; then
      echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    fi
  else
    echo -e "${RED}✗ FAIL - Expected $expected_status but got $http_code${NC}"
    echo -e "${RED}Response: $body${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
  fi
  echo ""
}

# Clean up function
cleanup() {
  rm -f "$COOKIES_FILE"
}

trap cleanup EXIT

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}AUTHENTICATION ENDPOINTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

# Test 1: Login with invalid credentials
test_endpoint \
  "Login with invalid credentials (should fail)" \
  "POST" \
  "/api/login/" \
  '{"email":"invalid@example.com","password":"wrong"}' \
  "401" \
  "false"

# Test 2: Login with valid credentials
echo -e "${YELLOW}Attempting login with valid credentials...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$USER_EMAIL\",\"password\":\"$USER_PASSWORD\"}" \
  -c "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

TOTAL_TESTS=$((TOTAL_TESTS + 1))
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}✓ PASS - Login successful${NC}"
  echo "$BODY" | python3 -m json.tool
  PASSED_TESTS=$((PASSED_TESTS + 1))
else
  echo -e "${RED}✗ FAIL - Login failed with HTTP $HTTP_CODE${NC}"
  echo -e "${RED}Note: Make sure test user exists. Run:${NC}"
  echo -e "${RED}  python manage.py shell${NC}"
  echo -e "${RED}  >>> from django.contrib.auth.models import User${NC}"
  echo -e "${RED}  >>> User.objects.create_user('$USER_EMAIL', '$USER_EMAIL', '$USER_PASSWORD')${NC}"
  FAILED_TESTS=$((FAILED_TESTS + 1))
  exit 1
fi
echo ""

# Test 3: Get current user
test_endpoint \
  "Get current user info" \
  "GET" \
  "/api/me/" \
  "null" \
  "200" \
  "true"

# Test 4: Refresh token
test_endpoint \
  "Refresh access token" \
  "POST" \
  "/api/refresh/" \
  "null" \
  "200" \
  "true"

# Save cookies after refresh
curl -s -X POST "$BASE_URL/api/refresh/" \
  -b "$COOKIES_FILE" \
  -c "$COOKIES_FILE" >/dev/null 2>&1

# ============================================================================
# LEAGUES ENDPOINTS (Public)
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}LEAGUES ENDPOINTS (Public)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

# Test 5: Get upcoming matches
test_endpoint \
  "Get upcoming matches" \
  "GET" \
  "/leagues/upcoming-matches/" \
  "null" \
  "200" \
  "false"

# Test 6: Get league standings
test_endpoint \
  "Get league standings" \
  "GET" \
  "/leagues/standings/" \
  "null" \
  "200" \
  "false"

# Test 7: Get rounds
test_endpoint \
  "Get league rounds" \
  "GET" \
  "/leagues/rounds/" \
  "null" \
  "200" \
  "false"

# ============================================================================
# PREDICTIONS ENDPOINTS (Authenticated)
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}PREDICTIONS ENDPOINTS (Authenticated)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

# Test 8: Get user predictions
test_endpoint \
  "Get user's predictions" \
  "GET" \
  "/predictions/predictions/" \
  "null" \
  "200" \
  "true"

# Test 9: Get client rankings
test_endpoint \
  "Get client rankings" \
  "GET" \
  "/predictions/client-rankings/" \
  "null" \
  "200" \
  "true"

# Test 10: Create prediction (will likely fail if no upcoming matches)
echo -e "${YELLOW}[Test $((TOTAL_TESTS + 1))] Create a prediction (may fail if no upcoming matches)${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
CREATE_PRED_RESPONSE=$(curl -s -X POST "$BASE_URL/predictions/predictions/" \
  -H "Content-Type: application/json" \
  -d '{"match":1,"predicted_home_score":2,"predicted_away_score":1}' \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$CREATE_PRED_RESPONSE" | tail -n1)
BODY=$(echo "$CREATE_PRED_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
  echo -e "${GREEN}✓ PASS - Prediction created${NC}"
  echo "$BODY" | python3 -m json.tool
  PASSED_TESTS=$((PASSED_TESTS + 1))
  PREDICTION_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
elif [ "$HTTP_CODE" = "400" ]; then
  echo -e "${YELLOW}⚠ SKIP - Cannot create prediction (validation error - expected)${NC}"
  echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
  echo -e "${RED}✗ FAIL - Unexpected status $HTTP_CODE${NC}"
  FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo ""

# ============================================================================
# ADMIN ENDPOINTS (Requires admin user)
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}ADMIN ENDPOINTS (Requires admin authentication)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

# Logout current user first
curl -s -X POST "$BASE_URL/api/logout/" -b "$COOKIES_FILE" >/dev/null 2>&1

# Try to login as admin
echo -e "${YELLOW}Attempting admin login...${NC}"
ADMIN_LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login/" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" \
  -c "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$ADMIN_LOGIN_RESPONSE" | tail -n1)

TOTAL_TESTS=$((TOTAL_TESTS + 1))
if [ "$HTTP_CODE" = "200" ]; then
  echo -e "${GREEN}✓ PASS - Admin login successful${NC}"
  PASSED_TESTS=$((PASSED_TESTS + 1))
  
  # Test 11: Get all clients
  test_endpoint \
    "Get all clients (admin only)" \
    "GET" \
    "/admin-panel/clients/" \
    "null" \
    "200" \
    "true"
  
  # Test 12: Create a client
  echo -e "${YELLOW}[Test $((TOTAL_TESTS + 1))] Create a new client (admin only)${NC}"
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  CREATE_CLIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/admin-panel/clients/" \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Corp","admin_name":"Test Admin","admin_email":"test@corp.com","client_root_admin_username":"testadmin","password":"testpass123"}' \
    -b "$COOKIES_FILE" \
    -w "\n%{http_code}")
  
  HTTP_CODE=$(echo "$CREATE_CLIENT_RESPONSE" | tail -n1)
  BODY=$(echo "$CREATE_CLIENT_RESPONSE" | sed '$d')
  
  if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✓ PASS - Client created${NC}"
    echo "$BODY" | python3 -m json.tool
    PASSED_TESTS=$((PASSED_TESTS + 1))
    CLIENT_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
  elif [ "$HTTP_CODE" = "400" ]; then
    echo -e "${YELLOW}⚠ SKIP - Client creation failed (may already exist)${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
  else
    echo -e "${RED}✗ FAIL - Unexpected status $HTTP_CODE${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
  fi
  echo ""
  
else
  echo -e "${YELLOW}⚠ SKIP - Admin user not available${NC}"
  echo -e "${YELLOW}Create admin user to test admin endpoints:${NC}"
  echo -e "  python manage.py createsuperuser${NC}"
fi
echo ""

# ============================================================================
# CLEANUP TESTS
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}CLEANUP AND LOGOUT${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}\n"

# Test logout
test_endpoint \
  "Logout user" \
  "POST" \
  "/api/logout/" \
  "null" \
  "200" \
  "true"

# Test access after logout (should fail)
test_endpoint \
  "Access after logout (should fail)" \
  "GET" \
  "/api/me/" \
  "null" \
  "401" \
  "true"

# ============================================================================
# SUMMARY
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              TEST SUMMARY                  ║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║ Total Tests:  ${TOTAL_TESTS}                         ║${NC}"
echo -e "${GREEN}║ Passed:       ${PASSED_TESTS}                         ║${NC}"
echo -e "${RED}║ Failed:       ${FAILED_TESTS}                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}\n"

if [ $FAILED_TESTS -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
  exit 1
fi
