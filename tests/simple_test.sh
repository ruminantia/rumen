#!/bin/bash

# Rumen Simple Test
# Quick health check without external LLM dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[Test]${NC} $1"; }
print_success() { echo -e "${GREEN}[Test]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[Test]${NC} $1"; }
print_error() { echo -e "${RED}[Test]${NC} $1"; }

BASE_URL="http://localhost:8000"
API_KEY=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key) API_KEY="$2"; shift 2 ;;
        --url) BASE_URL="$2"; shift 2 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

# Make request
make_request() {
    local method="$1"
    local endpoint="$2"
    if [ -n "$API_KEY" ]; then
        curl -s -w "%{http_code}" -X "$method" -H "Authorization: Bearer $API_KEY" "${BASE_URL}${endpoint}"
    else
        curl -s -w "%{http_code}" -X "$method" "${BASE_URL}${endpoint}"
    fi
}

echo "Rumen Simple Test"
echo "================="

# Test 1: Root endpoint (no auth)
print_status "Testing root endpoint..."
response=$(curl -s "${BASE_URL}/")
if echo "$response" | grep -q '"message":"Rumen LLM API"'; then
    print_success "✓ API is running"
else
    print_error "✗ API not responding"
    exit 1
fi

# Test 2: Authentication check
print_status "Testing authentication..."
response=$(curl -s "${BASE_URL}/health")
if echo "$response" | grep -q '"detail":"Not authenticated"'; then
    print_success "✓ Authentication required"
else
    print_warning "⚠ Authentication not enforced"
fi

# Test 3: Health with auth (if key provided)
if [ -n "$API_KEY" ]; then
    print_status "Testing health with API key..."
    response=$(curl -s -H "Authorization: Bearer $API_KEY" "${BASE_URL}/health")
    if echo "$response" | grep -q '"status"'; then
        print_success "✓ Health check passed"
        # Extract status
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        llm_healthy=$(echo "$response" | grep -o '"llm_healthy":[^,]*' | cut -d':' -f2)
        echo "    Status: $status, LLM: $llm_healthy"
    else
        print_error "✗ Health check failed"
    fi
else
    print_warning "⚠ No API key - skipping authenticated tests"
    print_warning "Get key: ./run-docker.sh api-key"
fi

# Test 4: Container status
print_status "Checking container..."
if docker compose ps 2>/dev/null | grep -q "Up"; then
    print_success "✓ Container is running"
else
    print_error "✗ Container not running"
fi

# Test 5: Port check
print_status "Checking port 8000..."
if nc -z localhost 8000 2>/dev/null; then
    print_success "✓ Port 8000 is open"
else
    print_error "✗ Port 8000 not accessible"
fi

echo
echo "================="
print_success "Basic system check complete!"
if [ -n "$API_KEY" ]; then
    print_success "Rumen is operational"
else
    print_warning "Run with --api-key for full test"
fi
