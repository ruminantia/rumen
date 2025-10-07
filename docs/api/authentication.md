# Authentication Guide

Rumen uses Bearer token authentication to secure API endpoints and protect your LLM processing resources. This guide covers authentication setup, usage, and security best practices.

## Overview

Rumen implements a two-layer authentication system:

1. **Rumen API Authentication**: Secures access to the Rumen API endpoints
2. **LLM Provider Authentication**: Handles communication with external LLM services

## Rumen API Authentication

### Automatic Key Generation

On first run, Rumen automatically generates a secure 32-character API key:

```bash
# Get your API key
./run-docker.sh api-key

# Example output:
# Your Rumen API key: abc123def456ghi789jkl012mno345pqr678stu901
```

The API key is stored in the `.env` file and persists across container restarts.

### Using the API Key

Include the API key in the `Authorization` header for all authenticated requests:

```bash
# Health check with authentication
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/health

# Process text with authentication
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant"
```

### Public Endpoints

The following endpoints do not require authentication:

- `GET /` - API information and status
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

All other endpoints require valid authentication.

## LLM Provider Authentication

### Provider API Keys

LLM provider authentication is handled via environment variables in the `.env` file:

```bash
# OpenRouter (recommended)
OPENROUTER_API_KEY=your_openrouter_key_here

# Google Gemini
GEMINI_API_KEY=your_gemini_key_here

# OpenAI
OPENAI_API_KEY=your_openai_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### Key Rotation

#### Rumen API Key

To regenerate your Rumen API key:

```bash
# Stop Rumen
./run-docker.sh stop

# Remove the existing key from .env
# Or let it regenerate automatically

# Restart (new key will be generated)
./run-docker.sh start

# Get the new key
./run-docker.sh api-key
```

#### LLM Provider Keys

Update provider keys by editing the `.env` file:

```bash
# Edit the .env file
nano .env

# Update the API key
GEMINI_API_KEY=your_new_gemini_key_here

# Restart to apply changes
./run-docker.sh restart
```

## Security Best Practices

### Key Storage

- **Never commit API keys** to version control
- Use `.env` file for local development
- For production, use secure secret management
- Regularly rotate API keys

### Environment Security

```bash
# Set proper file permissions
chmod 600 .env

# Verify .env is in .gitignore
grep .env .gitignore
```

### Network Security

- Use HTTPS in production environments
- Restrict API access to trusted networks
- Monitor API usage and set rate limits
- Use firewall rules to limit access

## Error Responses

### Authentication Failures

**401 Unauthorized** - Missing or invalid API key:
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden** - Valid key but insufficient permissions:
```json
{
  "detail": "Not enough permissions"
}
```

### Provider Authentication Errors

**400 Bad Request** - Invalid provider configuration:
```json
{
  "detail": "Invalid API key for provider: gemini"
}
```

## API Client Examples

### Python

```python
import requests

class RumenClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def health_check(self):
        response = requests.get(
            f"{self.base_url}/health",
            headers=self.headers
        )
        return response.json()
    
    def process_text(self, text: str, system_prompt: str, user_prompt: str):
        params = {
            "text": text,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt
        }
        response = requests.post(
            f"{self.base_url}/process",
            params=params,
            headers=self.headers
        )
        return response.json()

# Usage
client = RumenClient("http://localhost:8000", "your_api_key_here")
result = client.process_text(
    text="Hello world",
    system_prompt="You are a helpful assistant",
    user_prompt="Please respond to: {content}"
)
```

### JavaScript/Node.js

```javascript
const RumenClient = class {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`, {
            headers: this.headers
        });
        return await response.json();
    }

    async processText(text, systemPrompt, userPrompt) {
        const params = new URLSearchParams({
            text: text,
            system_prompt: systemPrompt,
            user_prompt: userPrompt
        });
        
        const response = await fetch(`${this.baseUrl}/process?${params}`, {
            method: 'POST',
            headers: this.headers
        });
        return await response.json();
    }
};

// Usage
const client = new RumenClient('http://localhost:8000', 'your_api_key_here');
client.processText(
    'Hello world',
    'You are a helpful assistant',
    'Please respond to: {content}'
).then(console.log);
```

### cURL Examples

```bash
# Health check
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/health

# Process text (URL encoded)
curl -H "Authorization: Bearer $API_KEY" \
  -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant"

# Process text (JSON body)
curl -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/process \
  -d '{
    "text": "Hello world",
    "system_prompt": "You are a helpful assistant",
    "user_prompt": "Please respond to: {content}"
  }'
```

## Troubleshooting

### Common Issues

**Missing API Key:**
```bash
# Check if key exists
./run-docker.sh api-key

# If no output, restart to generate
./run-docker.sh restart
```

**Invalid API Key:**
- Verify no trailing spaces in the key
- Ensure proper Bearer token format
- Check .env file encoding

**Provider Authentication Errors:**
- Verify provider API key in .env
- Check provider service status
- Ensure sufficient credits/quotas

### Debugging Commands

```bash
# Test authentication
curl -v -H "Authorization: Bearer $API_KEY" http://localhost:8000/health

# Check container environment
docker exec rumen env | grep API_KEY

# View authentication logs
./run-docker.sh logs | grep -i auth
```

## Next Steps

- [API Overview](overview.md) - Complete API reference
- [Processing Endpoints](processing.md) - Text and file processing APIs
- [Configuration Guide](../configuration/configuration.md) - System configuration
- [Troubleshooting](../advanced/troubleshooting.md) - Common issues and solutions

---
*Always keep your API keys secure and monitor your API usage for suspicious activity.*