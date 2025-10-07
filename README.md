# Rumen - Containerized LLM API

Rumen is a containerized API for interacting with Large Language Models (LLMs) via HTTP API and file system monitoring. It provides a flexible, secure way to process text content using various LLM providers.

## Features

- **Multiple LLM Providers**: Support for OpenRouter, OpenAI, Google Gemini, and DeepSeek
- **Dual Operation Modes**:
  - HTTP API for direct interaction
  - File monitoring for automated processing
- **Secure by Design**: API key authentication and internal networking
- **Configurable Processing**: Custom prompts and parameters per monitored folder, with support for prompt files
- **Prompt Management**: Store complex prompts as individual files for better organization
- **Error Handling**: Graceful retries and comprehensive error logging
- **Containerized**: Easy deployment with Docker and Docker Compose
- **External Volume Support**: Monitor Docker volumes for automated processing
- **API Security**: Bearer token authentication for all endpoints

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API key from your preferred LLM provider

### 1. Clone and Setup

```bash
git clone <https://github.com/ruminantia/rumen.git>
cd rumen
```

### 2. Configure API Key

Edit the `.env` file (created automatically on first run):

```bash
# For OpenRouter (recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Or for OpenAI directly
# OPENAI_API_KEY=your_openai_api_key_here

# For Gemini directly
# GEMINI_API_KEY=your_gemini_api_key_here

# For DeepSeek directly
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. Start Rumen

```bash
./run-docker.sh start
```

This will:
- Build the Docker image
- Start the container on port 8000
- Begin monitoring configured folders

### 4. Test the Setup

```bash
python test_rumen.py
```

## Configuration

### Config File Structure

The main configuration is in `config/config.ini`:

```ini
[DEFAULT]
# Default LLM settings
provider = openrouter
model = google/gemini-2.5-flash-lite
base_url = https://openrouter.ai/api/v1
temperature = 0.7
max_tokens = 2048
top_p = 0.9
thinking_enabled = false
search_enabled = false
retry_attempts = 3
retry_delay = 2

# API settings
api_host = 0.0.0.0
api_port = 8000
api_workers = 1

# File monitoring
monitor_interval = 5
file_timeout = 30

# Output settings
output_format = markdown
output_directory = /app/bolus
```

### Folder-Specific Configurations

Add folder configurations for automated processing:

```ini
[worldnews]
folder_path = /app/input/worldnews
enabled = false
# Use prompt files for complex prompts (recommended)
system_prompt_file = prompts/worldnews_system.md
user_prompt_file = prompts/worldnews_user.md
# Or use inline prompts for simple cases
# system_prompt = You are a news analyst. Analyze the provided news article and extract key information, summarize the main points, and provide context.
# user_prompt_template = Please analyze this news article: {content}
provider = openrouter
model = google/gemini-2.5-flash-lite
temperature = 0.3
max_tokens = 1024
output_format = markdown

[research]
folder_path = /app/input/research
enabled = false
# Use prompt files for complex prompts (recommended)
system_prompt_file = prompts/research_system.md
user_prompt_file = prompts/research_user.md
# Or use inline prompts for simple cases
# system_prompt = You are a research assistant. Analyze the provided research material and extract key insights, summarize findings, and identify potential applications.
# user_prompt_template = Please analyze this research material: {content}
provider = openrouter
model = google/gemini-2.5-flash-lite
temperature = 0.5
max_tokens = 2048
output_format = markdown
```

## Usage

### HTTP API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Process Text
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog.",
    "system_prompt": "You are a helpful assistant.",
    "user_prompt": "Please analyze this text: {content}",
    "temperature": 0.7,
    "max_tokens": 100,
    "output_format": "markdown"
  }'
```

#### List Monitored Folders
```bash
curl http://localhost:8000/folders
```

#### List Results
```bash
curl http://localhost:8000/results?limit=10
```

### File Monitoring

1. **Enable a folder** in `config/config.ini` by setting `enabled = true`
2. **Place files** in the corresponding input folder
3. **Rumen automatically processes** new files and saves results to the bolus directory

Supported file types: `.md`, `.markdown`, `.txt`

### Python Client Example

```python
import requests

def process_with_rumen(text, system_prompt, user_prompt, api_key):
    response = requests.post(
        "http://localhost:8000/process",
        params={
            "text": text,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "temperature": 0.7,
            "max_tokens": 1000,
            "output_format": "markdown"
        },
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return response.json()

# Usage
api_key = "your_rumen_api_key_here"  # Get from .env file or run-docker.sh api-key
result = process_with_rumen(
    text="Your content here",
    system_prompt="You are a helpful assistant.",
    user_prompt="Please analyze: {content}",
    api_key=api_key
)
print(result)
```

## Management Commands

Use the provided management script:

```bash
# Start Rumen
./run-docker.sh start

# Stop Rumen
./run-docker.sh stop

# View logs
./run-docker.sh logs

# Restart
./run-docker.sh restart

# Check status
./run-docker.sh status

# Build/rebuild image
./run-docker.sh build

# Clean up containers
./run-docker.sh clean

# Show API key
./run-docker.sh api-key

# Show help
./run-docker.sh help
```

## Project Structure

```
rumen/
├── src/                    # Python source code
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration management
│   ├── llm_client.py      # LLM provider clients
│   ├── file_monitor.py    # File system monitoring
├── output_handler.py  # Result output management
├── prompts/           # Prompt files for complex system and user prompts
│   ├── worldnews_system.md
│   ├── worldnews_user.md
│   ├── research_system.md
│   └── research_user.md
├── config/
│   └── config.ini         # Main configuration file
├── input/                 # Input files for processing
├── bolus/                 # Output files (processed results)
├── Dockerfile             # Container definition
├── docker-compose.yml     # Service orchestration
├── requirements.txt       # Python dependencies
├── run-docker.sh          # Management script
├── tests/                 # Test scripts (see tests/README.md)
│   ├── simple_test.sh     # Quick health check
│   ├── test_rumen.sh      # Comprehensive bash tests
│   └── test_rumen.py      # Python test suite
```

## External Volumes

Rumen supports monitoring external Docker volumes for automated processing. This is useful for integrating with other systems that generate content.

### Adding External Volumes

1. **Define the volume in docker-compose.yml**:
```yaml
volumes:
  pasture_pastures:
    external: true
```

2. **Mount the volume in the service**:
```yaml
services:
  rumen:
    volumes:
      - pasture_pastures:/app/pasture_pastures
```

3. **Configure the folder in config.ini**:
```ini
[pasture_pastures]
folder_path = /app/pasture_pastures
enabled = true
system_prompt = Your custom system prompt
user_prompt_template = Your custom user prompt template: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.4
max_tokens = 2048
output_format = markdown
```

### Example Use Case: Pasture Pastures

The system includes a pre-configured example for monitoring scraped news/web articles from an external volume called "pasture_pastures":

- **Volume**: `pasture_pastures` (external Docker volume)
- **Mount Point**: `/app/pasture_pastures`
- **Structure**: Articles organized recursively by `/year/month/day/feed/hash.md`
- **Processing**: Automatically analyzes new articles as they appear

### Volume Management

- **External Volumes**: Must be created separately before starting Rumen
- **Permissions**: Ensure the container has read access to mounted volumes
- **Structure**: The system can handle nested directory structures
- **Performance**: File monitoring works efficiently even with thousands of files

## Security

- **API Authentication**: All endpoints (except root) require Bearer token authentication
- **Secure Key Generation**: Random 32-character API keys using secure generation
- **Network Isolation**: Docker network configuration prevents unintended access
- **Volume Mounts**: Only necessary directories are mounted
- **API Key Security**: LLM keys stored in environment variables, not in code
- **File Permissions**: Container runs with minimal privileges

### API Key Authentication

Rumen uses Bearer token authentication for API security:

1. **Automatic Key Generation**: If no `RUMEN_API_KEY` is set in `.env`, a secure random key is generated
2. **Environment Variable**: Set `RUMEN_API_KEY` in your `.env` file for persistence
3. **Bearer Token**: Include `Authorization: Bearer YOUR_API_KEY` header in all requests
4. **Protected Endpoints**: All endpoints except `/` require authentication

```bash
# Get your API key
./run-docker.sh api-key

# Use with curl
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health

# Use in applications
headers = {"Authorization": "Bearer YOUR_API_KEY"}
```

### Security Features

- **No Default Keys**: No hardcoded or default API keys
- **Key Persistence**: API keys survive container rebuilds and restarts
- **Minimal Exposure**: Only required ports are exposed
- **Internal Network**: Optional internal Docker network for additional isolation

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Ensure your API key is set in the `.env` file
   - Verify the environment variable name matches your provider

2. **File Monitoring Not Working**
   - Check that folder configurations have `enabled = true`
   - Verify folder paths exist and are writable
   - Check Docker volume mounts

3. **LLM Provider Errors**
   - Verify your API key is valid and has sufficient credits
   - Check the provider's service status
   - Review logs with `./run-docker.sh logs`

4. **Authentication Errors**
   - Check your Rumen API key with `./run-docker.sh api-key`
   - Ensure `Authorization: Bearer YOUR_KEY` header is included
   - Verify the API key in your `.env` file matches what you're using

### Logs and Debugging

```bash
# View application logs
./run-docker.sh logs

# Check container status
./run-docker.sh status

# Test API connectivity (with authentication)
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health

# Get your API key
./run-docker.sh api-key
```

## Development

### Local Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
python -m src.main
```

### Adding New LLM Providers

1. Add provider configuration in `config/config.ini`
2. Update API key mapping in `src/config.py`
3. Test with the provider's base URL and model names

## License

This project is licensed under the terms of the LICENSE file included in the repository.

## Prompt Files

For complex prompts, you can store them as individual files in the `prompts/` directory instead of embedding them in `config.ini`. This provides better organization and maintainability.

### Using Prompt Files

1. **Create prompt files** in the `prompts/` directory:
   - `{folder_name}_system.md` - System prompt defining the AI's role
   - `{folder_name}_user.md` - User prompt template with `{content}` placeholder

2. **Reference them in config.ini**:
```ini
[worldnews]
folder_path = /app/input/worldnews
enabled = true
system_prompt_file = prompts/worldnews_system.md
user_prompt_file = prompts/worldnews_user.md
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.3
max_tokens = 1024
```

### Benefits

- **Better Organization**: Complex prompts are easier to read and maintain
- **Version Control**: Track prompt changes independently from configuration
- **Reusability**: Share prompts across multiple folder configurations
- **Collaboration**: Multiple team members can work on prompts simultaneously

See the `prompts/README.md` for detailed documentation and examples.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Open an issue in the repository
