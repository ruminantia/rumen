# First Run Guide

## Overview

This guide walks you through starting Rumen for the first time, verifying the setup, and performing initial tests to ensure everything is working correctly.

## Prerequisites

Before starting, ensure you have:
- [x] Docker and Docker Compose installed
- [x] `.env` file configured with your LLM API key
- [x] Project directory set up correctly

## Step 1: Start Rumen

### Using the Management Script (Recommended)

```bash
# Build and start Rumen
./run-docker.sh start

# This will:
# 1. Build the Docker image (first time only)
# 2. Start the container
# 3. Generate a secure API key if not already set
# 4. Begin monitoring enabled folders
```

### Alternative: Direct Docker Compose

```bash
# Start with Docker Compose
docker compose up -d

# View logs
docker compose logs -f
```

## Step 2: Verify Container Status

```bash
# Check if Rumen is running
./run-docker.sh status

# Expected output: "Rumen is running"

# View container details
docker ps

# Should show rumen container with status "Up"
```

## Step 3: Get Your API Key

Rumen automatically generates a secure API key for authentication:

```bash
# Display the API key
./run-docker.sh api-key

# Save it for later use
API_KEY=$(./run-docker.sh api-key)
echo "Your API key: $API_KEY"
```

**Important**: This API key is required for all authenticated API calls.

## Step 4: Test Basic Functionality

### Health Check

```bash
# Test without authentication (should fail)
curl http://localhost:8000/health

# Test with authentication (should succeed)
curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

### Root Endpoint

```bash
# Root endpoint doesn't require authentication
curl http://localhost:8000/

# Should return basic API information
```

## Step 5: Test Text Processing

### Simple Text Processing

```bash
# Process text via API
curl -H "Authorization: Bearer $API_KEY" \
  -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant&user_prompt=Please%20respond%20to%3A%20%7Bcontent%7D"

# This sends "Hello world" to the LLM with the specified prompts
```

### Using JSON for Complex Content

```bash
# For longer content, use JSON format
curl -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/process \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog. This is a test of the text processing capabilities.",
    "system_prompt": "You are a helpful assistant.",
    "user_prompt": "Please analyze this text: {content}",
    "temperature": 0.7,
    "max_tokens": 100,
    "output_format": "markdown"
  }'
```

## Step 6: Test File Monitoring

### Enable a Test Folder

Edit `config/config.ini` and ensure at least one folder is enabled:

```ini
[test_folder]
folder_path = /app/input/test_folder
enabled = true
system_prompt = You are a helpful assistant.
user_prompt_template = Please summarize this content: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.7
max_tokens = 1024
output_format = markdown
```

### Restart to Apply Changes

```bash
# Restart Rumen to load new configuration
./run-docker.sh restart
```

### Create Test Files

```bash
# Create test directory
mkdir -p input/test_folder

# Create a test markdown file
cat > input/test_folder/test_article.md << EOF
# Test Article

This is a test article to verify file processing functionality.

## Key Points

- Rumen should automatically detect this file
- Process it using the configured prompts
- Save the result to the output directory
- Delete the original file after processing

Let's see if it works!
EOF
```

### Monitor Processing

```bash
# Watch the logs to see file processing
./run-docker.sh logs -f

# In another terminal, check for output
ls -la bolus/

# Should show processed files with timestamps
```

## Step 7: Verify Output

### Check Processed Results

```bash
# List processed files
find bolus/ -name "*.md" -type f

# View a processed file
cat bolus/$(ls -t bolus/ | head -1)
```

### Expected Behavior

- Input files in monitored folders are automatically processed
- Results are saved to the `bolus/` directory
- Original files are deleted after successful processing
- Each processed file contains LLM-generated content based on your prompts

## Common First-Run Issues

### Container Fails to Start

```bash
# Check detailed logs
./run-docker.sh logs

# Common causes:
# - Missing .env file
# - Invalid API key
# - Port 8000 already in use
# - Docker daemon not running
```

### Authentication Errors

```bash
# Verify API key is correct
./run-docker.sh api-key

# Test authentication
curl -H "Authorization: Bearer YOUR_KEY" http://localhost:8000/health
```

### File Processing Not Working

```bash
# Check folder configuration
cat config/config.ini | grep -A 10 "\[test_folder\]"

# Verify input directory exists
ls -la input/test_folder/

# Check file permissions
ls -la input/test_folder/test_article.md
```

### LLM API Errors

```bash
# View detailed error messages
./run-docker.sh logs | grep -i error

# Common issues:
# - Invalid LLM API key
# - Network connectivity
# - Provider rate limits
# - Model availability
```

## Next Steps

Congratulations! Your Rumen instance is now running. Here's what to explore next:

1. **Customize Configuration**: Edit `config/config.ini` for your specific needs
2. **Add More Folders**: Configure additional monitored folders
3. **Use Prompt Files**: Create complex prompts in the `prompts/` directory
4. **Integrate with Applications**: Use the HTTP API from other software
5. **Set Up External Volumes**: Monitor Docker volumes for automated processing

## Getting Help

If you encounter issues:

1. Check the logs: `./run-docker.sh logs`
2. Review configuration: `config/config.ini`
3. Consult the [Troubleshooting Guide](../advanced/troubleshooting.md)
4. Verify your LLM provider API key is valid

---

*Your Rumen instance is now ready for production use! Explore the [Configuration Guide](../configuration/configuration.md) to customize it for your specific needs.*