# API Overview

Rumen provides a comprehensive HTTP API for interacting with Large Language Models (LLMs) and managing automated file processing. The API supports both direct text processing and file system monitoring.

## Base URL

All API endpoints are available at:
```
http://localhost:8000
```

When deployed in production, replace `localhost` with your server's hostname or IP address.

## Authentication

Most API endpoints require Bearer token authentication. The API key is automatically generated on first run and can be retrieved using:

```bash
./run-docker.sh api-key
```

Include the API key in the `Authorization` header:
```
Authorization: Bearer YOUR_API_KEY
```

## Response Format

### Success Responses

Successful API calls return HTTP 200 status with JSON responses:

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Responses

Error responses include detailed information:

```json
{
  "status": "error",
  "error": "Error description",
  "details": "Additional error information"
}
```

## Endpoint Categories

### Public Endpoints
- `GET /` - API information and status
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Health & Status
- `GET /health` - Service health check
- `GET /status` - System status and configuration

### Text Processing
- `POST /process` - Process text content with custom prompts
- `POST /process/batch` - Process multiple texts in batch

### File Management
- `GET /files/processed` - List processed files
- `GET /files/processed/{filename}` - Get specific processed file
- `GET /monitor/status` - File monitoring status
- `POST /monitor/restart` - Restart file monitoring

### Configuration
- `GET /config/folders` - List configured folders
- `GET /config/folders/{name}` - Get specific folder configuration
- `PUT /config/folders/{name}` - Update folder configuration

## Quick Start Examples

### Health Check
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health
```

### Process Text
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant&user_prompt=Please%20respond%20to%3A%20%7Bcontent%7D"
```

### Check File Monitor Status
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/monitor/status
```

## Rate Limiting

The API implements basic rate limiting to prevent abuse:
- Maximum 100 requests per minute per IP address
- File processing: 10 concurrent operations
- Batch processing: Limited to 50 items per request

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid API key |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side issue |

## Content Types

The API supports:
- `application/x-www-form-urlencoded` - For simple parameters
- `application/json` - For complex data structures
- `multipart/form-data` - For file uploads (future)

## Next Steps

- [Authentication](authentication.md) - Detailed authentication guide
- [Processing Endpoints](processing.md) - Text and file processing APIs
- [Health & Status](health-status.md) - Monitoring and health checks
- [API Client Examples](../development/api-clients.md) - Code examples in various languages

---

*For interactive API exploration, visit `http://localhost:8000/docs` after starting Rumen.*