#!/bin/bash

# Rumen Startup Script
# A simple script to run Rumen with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[Rumen]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Rumen]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Rumen]${NC} $1"
}

print_error() {
    echo -e "${RED}[Rumen]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if required files exist
check_requirements() {
    local missing_files=()

    if [ ! -f "docker-compose.yml" ]; then
        missing_files+=("docker-compose.yml")
    fi

    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating template .env file."
        cat > .env << EOF
# Rumen Environment Variables
# Set your API key for your preferred LLM provider

# For OpenRouter (recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Or for OpenAI directly
# OPENAI_API_KEY=your_openai_api_key_here

# For DeepSeek directly (if not using OpenRouter)
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# For Gemini directly (if not using OpenRouter)
# GEMINI_API_KEY=your_gemini_api_key_kere
EOF
        print_status "Created .env template. Please edit it with your API key."
    fi

    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start      Start Rumen in detached mode (default)"
    echo "  stop       Stop Rumen"
    echo "  restart    Restart Rumen"
    echo "  logs       Show logs from Rumen"
    echo "  status     Show status of Rumen"
    echo "  build      Build the Docker image"
    echo "  clean      Stop and remove containers"
    echo "  api-key    Show the current Rumen API key"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the service"
    echo "  $0 logs      # View logs"
    echo "  $0 stop      # Stop the service"
}

# Function to start Rumen
start_rumen() {
    print_status "Starting Rumen..."
    check_docker
    check_requirements

    # Check if API key is set
        if ! grep -q "OPENROUTER_API_KEY=your_openrouter_api_key_here" .env && ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env && ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env && ! grep -q "DEEPSEEK_API_KEY=your_deepseek_api_key_here" .env; then
            print_success "API key configuration detected"
        else
            print_warning "Please set your API key in the .env file before starting"
            exit 1
        fi

        # Check if Rumen API key is set, generate one if not
        if ! grep -q "RUMEN_API_KEY=" .env; then
            print_warning "RUMEN_API_KEY not found in .env file"
            print_status "Generating secure API key for Rumen API access..."
            RUMEN_API_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))")
            echo "RUMEN_API_KEY=$RUMEN_API_KEY" >> .env
            print_success "Generated RUMEN_API_KEY and added to .env file"
            print_warning "Save this API key for accessing the Rumen API: $RUMEN_API_KEY"
        fi

    docker compose up -d
    print_success "Rumen started successfully!"
    print_status "View logs with: $0 logs"
}

# Function to stop Rumen
stop_rumen() {
    print_status "Stopping Rumen..."
    docker compose down
    print_success "Rumen stopped successfully!"
}

# Function to restart Rumen
restart_rumen() {
    print_status "Restarting Rumen..."
    docker compose restart
    print_success "Rumen restarted successfully!"
}

# Function to show logs
show_logs() {
    print_status "Showing Rumen logs (Ctrl+C to exit)..."
    docker compose logs -f rumen
}

# Function to show status
show_status() {
    print_status "Rumen status:"
    docker compose ps
}

# Function to build the image
build_image() {
    print_status "Building Rumen Docker image..."
    docker compose build
    print_success "Docker image built successfully!"
}

# Function to clean up
clean_up() {
    print_status "Cleaning up Rumen containers..."
    docker compose down
    print_success "Cleanup completed!"
}

# Function to show API key
show_api_key() {
    if [ -f ".env" ]; then
        if grep -q "RUMEN_API_KEY=" .env; then
            RUMEN_API_KEY=$(grep "RUMEN_API_KEY=" .env | cut -d'=' -f2)
            print_success "Rumen API Key: $RUMEN_API_KEY"
            print_status "Use this key in the Authorization header: Bearer $RUMEN_API_KEY"
        else
            print_error "RUMEN_API_KEY not found in .env file"
            print_status "Run './run-docker.sh start' to generate an API key"
        fi
    else
        print_error ".env file not found"
        print_status "Run './run-docker.sh start' to create .env file with API key"
    fi
}

# Main script logic
COMMAND=${1:-start}

case $COMMAND in
    start)
        start_rumen
        ;;
    stop)
        stop_rumen
        ;;
    restart)
        restart_rumen
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    build)
        build_image
        ;;
    clean)
        clean_up
        ;;
    api-key)
        show_api_key
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac
