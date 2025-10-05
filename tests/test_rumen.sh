#!/bin/bash

# Rumen Test Suite
# Simple test script using curl commands to verify Rumen LLM API functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[Test]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Test]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Test]${NC} $1"
}

print_error() {
    echo -e "${RED}[Test]${NC} $1"
}

# Default values
BASE_URL="http://localhost:8000"
API_KEY=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --url)
            BASE_URL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to make authenticated request
make_request() {
    local method="$1"
    local endpoint="$2"
    local params="$3"

    if [ -n "$API_KEY" ]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $API_KEY" \
            "${BASE_URL}${endpoint}${params}"
    else
        curl -s -X "$method" "${BASE_URL}${endpoint}${params}"
    fi
}

# Function to test root endpoint
test_root() {
    print_status "Testing root endpoint..."
    response=$(make_request "GET" "/" "")
    if echo "$response" | grep -q '"message":"Rumen LLM API"'; then
        print_success "Root endpoint: ✓"
        echo "    Response: $(echo "$response" | tr -d '\n')"
        return 0
    else
        print_error "Root endpoint failed"
        return 1
    fi
}

# Function to test health endpoint
test_health() {
    print_status "Testing health endpoint..."
    response=$(make_request "GET" "/health" "")
    if echo "$response" | grep -q '"status"'; then
        print_success "Health endpoint: ✓"
        echo "    Response: $(echo "$response" | tr -d '\n')"
        return 0
    else
        if echo "$response" | grep -q '"detail":"Not authenticated"'; then
            print_warning "Health endpoint requires authentication (no API key provided)"
        else
            print_error "Health endpoint failed"
        fi
        return 1
    fi
}

# Function to test process endpoint
test_process() {
    print_status "Testing process endpoint..."
    params="?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant&user_prompt=Please%20respond%20to%3A%20%7Bcontent%7D&temperature=0.3&max_tokens=100&output_format=markdown"
    response=$(make_request "POST" "/process" "$params")
    if echo "$response" | grep -q '"status":"success"'; then
        print_success "Process endpoint: ✓"
        echo "    Response: $(echo "$response" | tr -d '\n')"
        return 0
    else
        if echo "$response" | grep -q '"detail":"Not authenticated"'; then
            print_warning "Process endpoint requires authentication (no API key provided)"
        else
            print_error "Process endpoint failed"
            echo "    Response: $response"
        fi
        return 1
    fi
}

# Function to test folders endpoint
test_folders() {
    print_status "Testing folders endpoint..."
    response=$(make_request "GET" "/folders" "")
    if echo "$response" | grep -q '"monitored_folders"'; then
        print_success "Folders endpoint: ✓"
        echo "    Response: $(echo "$response" | tr -d '\n')"
        return 0
    else
        if echo "$response" | grep -q '"detail":"Not authenticated"'; then
            print_warning "Folders endpoint requires authentication (no API key provided)"
        else
            print_error "Folders endpoint failed"
        fi
        return 1
    fi
}

# Function to test file monitor status
test_file_monitor() {
    print_status "Testing file monitor status..."
    response=$(make_request "GET" "/file-monitor/status" "")
    if echo "$response" | grep -q '"running"'; then
        print_success "File monitor status: ✓"
        echo "    Response: $(echo "$response" | tr -d '\n')"
        return 0
    else
        if echo "$response" | grep -q '"detail":"Not authenticated"'; then
            print_warning "File monitor status requires authentication (no API key provided)"
        else
            print_error "File monitor status failed"
        fi
        return 1
    fi
}

# Function to test results endpoint
test_results() {
    print_status "Testing results endpoint..."
    response=$(make_request "GET" "/results?limit=5" "")
    if echo "$response" | grep -q '"results"'; then
        print_success "Results endpoint: ✓"
        echo "    Response: $(echo "$response" | tr -d '\n')"
        return 0
    else
        if echo "$response" | grep -q '"detail":"Not authenticated"'; then
            print_warning "Results endpoint requires authentication (no API key provided)"
        else
            print_error "Results endpoint failed"
        fi
        return 1
    fi
}

# Function to test authentication requirements
test_auth_required() {
    print_status "Testing authentication requirements..."
    endpoints=("/health" "/folders" "/results?limit=1" "/file-monitor/status")
    all_protected=true

    for endpoint in "${endpoints[@]}"; do
        response=$(curl -s "${BASE_URL}${endpoint}")
        if echo "$response" | grep -q '"detail":"Not authenticated"'; then
            print_success "Endpoint $endpoint correctly requires authentication: ✓"
        else
            print_error "Endpoint $endpoint should require authentication but doesn't"
            all_protected=false
        fi
    done

    if [ "$all_protected" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to test file creation
test_file_creation() {
    print_status "Testing file creation..."
    mkdir -p input
    cat > input/test_article.md << EOF
# Test Article

This is a test article for Rumen file processing.
It contains some sample content that should be processed by the LLM.

The quick brown fox jumps over the lazy dog.
Artificial intelligence is transforming many industries.
EOF
    if [ -f "input/test_article.md" ]; then
        print_success "Test file created: ✓"
        echo "    File: input/test_article.md"
        print_warning "Note: File processing requires folder monitoring to be enabled in config.ini"
        return 0
    else
        print_error "Failed to create test file"
        return 1
    fi
}

# Main test function
main() {
    echo "Rumen Test Suite"
    echo "========================"

    if [ -z "$API_KEY" ]; then
        print_warning "No API key provided. Some tests will fail due to authentication requirements."
        print_warning "Get your API key with: ./run-docker.sh api-key"
        print_warning "Then run: ./test_rumen.sh --api-key YOUR_API_KEY"
        echo
    else
        print_success "Using API key: ${API_KEY:0:10}..."
    fi

    print_status "Testing Rumen API at: $BASE_URL"
    echo

    # Run tests
    tests_passed=0
    tests_total=0

    # Always run these tests (no auth required)
    if test_root; then ((tests_passed++)); fi; ((tests_total++))
    echo

    # Test authentication requirements
    if test_auth_required; then ((tests_passed++)); fi; ((tests_total++))
    echo

    # These tests require authentication
    if test_health; then ((tests_passed++)); fi; ((tests_total++))
    echo

    if test_process; then ((tests_passed++)); fi; ((tests_total++))
    echo

    if test_folders; then ((tests_passed++)); fi; ((tests_total++))
    echo

    if test_file_monitor; then ((tests_passed++)); fi; ((tests_total++))
    echo

    if test_results; then ((tests_passed++)); fi; ((tests_total++))
    echo

    # File creation test
    if test_file_creation; then ((tests_passed++)); fi; ((tests_total++))
    echo

    # Results
    echo "========================"
    echo "Test Results: $tests_passed/$tests_total tests passed"

    if [ $tests_passed -eq $tests_total ]; then
        print_success "🎉 All tests passed! Rumen is working correctly."
        exit 0
    else
        print_warning "⚠ Some tests failed."
        if [ -z "$API_KEY" ]; then
            print_warning "💡 Tip: Most tests require an API key. Run with --api-key YOUR_KEY"
        fi
        exit 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --api-key KEY    Rumen API key for authentication"
    echo "  --url URL        Rumen API base URL (default: http://localhost:8000)"
    echo ""
    echo "Examples:"
    echo "  $0                              # Run tests without API key"
    echo "  $0 --api-key YOUR_KEY          # Run tests with API key"
    echo "  $0 --url http://192.168.1.100:8000 --api-key YOUR_KEY"
    echo ""
    echo "Get your API key: ./run-docker.sh api-key"
}

# Check for help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Run main function
main
