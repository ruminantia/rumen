# Rumen Quick Start Guide

## Security Note
Rumen now includes API key authentication for security. All API endpoints (except the root) require a Bearer token. A secure API key is automatically generated on first run.

## 1. Prerequisites

- Docker and Docker Compose installed
- API key from your preferred LLM provider (OpenRouter recommended)

## 2. Setup

```bash
# Clone or download the project
cd rumen

# Make the management script executable
chmod +x run-docker.sh

# Create your .env file with API key
cp .env.example .env  # If available, or create manually

# Or let Rumen generate the .env file automatically on first run
```

Edit `.env` file (created automatically if missing):
```bash
# For OpenRouter (recommended)
OPENROUTER_API_KEY=your_actual_api_key_here

# Or for other providers:
# OPENAI_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
# DEEPSEEK_API_KEY=your_key_here

# Rumen API authentication (automatically generated)
# RUMEN_API_KEY=your_generated_api_key_here
```

## 3. First Run

```bash
# Build and start Rumen
./run-docker.sh start

# Check if it's running
./run-docker.sh status

# View logs to see initialization
./run-docker.sh logs

# Get your API key for authentication
./run-docker.sh api-key
```

## 4. Test the API

```bash
# Health check (requires authentication)
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health

# Get your API key
./run-docker.sh api-key

# Process text directly (requires authentication)
curl -H "Authorization: Bearer YOUR_API_KEY" -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant&user_prompt=Please%20respond%20to%3A%20%7Bcontent%7D"

# Or with JSON body (requires different endpoint structure)

# Or run the test suite (may need updates for authentication)
python tests/test_rumen.py
```

## 5. Enable File Monitoring

Edit `config/config.ini` and enable a folder:

```ini
[news_summary]
folder_path = /app/input/news_summary
enabled = true
system_prompt = You are a news summarizer...
user_prompt_template = Please summarize: {content}
```

Restart to apply changes:
```bash
./run-docker.sh restart
```

## 6. Process Files Automatically

```bash
# Create test file
echo "# Test Article\nThis is test content." > input/news_summary/test.md

# Rumen will automatically process it and save results to bolus/
```

## 7. Management Commands

```bash
# Start/Stop
./run-docker.sh start
./run-docker.sh stop

# View logs
./run-docker.sh logs

# Restart (after config changes)
./run-docker.sh restart

# Clean up
./run-docker.sh clean
```

## 8. Verify Everything Works

1. API responds: `curl http://localhost:8000/`
2. Authentication works: `curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health`
3. File processing works: Check `bolus/` directory for output
4. No errors in logs: `./run-docker.sh logs`

## Common Issues

- **API key not set**: Check `.env` file exists and has valid key
- **Authentication errors**: Use `./run-docker.sh api-key` to get your API key
- **Container won't start**: Check Docker is running and ports are available
- **File processing not working**: Verify folder is enabled in config and input files are in correct format (.md, .txt)
- **Running tests**: Use `./tests/simple_test.sh` for quick health checks or `./tests/test_rumen.sh` for comprehensive testing

## Next Steps

- Customize folder configurations in `config/config.ini`
- Add more monitored folders for different use cases
- Integrate with other applications via HTTP API (remember authentication!)
- Monitor the `bolus/` directory for processed results
- Keep your API key secure and rotate if needed

Your Rumen instance is now ready to process text via API and automatically handle files in monitored folders!