# Quick Start Guide

Get Rumen up and running in minutes with this step-by-step guide.

## 🎯 Overview

Rumen is a containerized LLM API that provides:
- HTTP API for direct LLM interaction
- File system monitoring for automated processing
- Support for multiple LLM providers (Gemini, OpenAI, OpenRouter, DeepSeek)
- Custom prompts per monitored folder

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- API key from your preferred LLM provider

### Recommended LLM Providers

| Provider | Best For | Setup Complexity |
|----------|----------|------------------|
| **OpenRouter** | Flexibility, multiple models | Easy |
| **Google Gemini** | Free tier, good performance | Easy |
| **OpenAI** | GPT models, reliability | Easy |
| **DeepSeek** | Cost-effective, good quality | Easy |

## 🚀 Step-by-Step Setup

### 1. Clone and Prepare

```bash
# Clone or download the project
cd rumen

# Make the management script executable
chmod +x run-docker.sh
```

### 2. Configure API Key

Create or edit the `.env` file:

```bash
# Copy the example (if available)
cp .env.example .env

# Or create manually
touch .env
```

Edit `.env` with your API key:

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

### 3. First Run

```bash
# Build and start Rumen
./run-docker.sh start

# Check if it's running
./run-docker.sh status

# View initialization logs
./run-docker.sh logs
```

### 4. Get Your API Key

Rumen automatically generates a secure API key for authentication:

```bash
./run-docker.sh api-key
```

Save this key for API requests.

## 🧪 Test Your Setup

### Quick Health Check

```bash
# Health check (requires authentication)
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health
```

### Process Text via API

```bash
# Get your API key first
API_KEY=$(./run-docker.sh api-key)

# Process text directly
curl -H "Authorization: Bearer $API_KEY" \
  -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant&user_prompt=Please%20respond%20to%3A%20%7Bcontent%7D"
```

### Enable File Monitoring

Edit `config/config.ini` and enable a test folder:

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

Restart to apply changes:

```bash
./run-docker.sh restart
```

### Test File Processing

```bash
# Create test directory
mkdir -p input/test_folder

# Create test file
echo "# Test Article\nThis is test content for automated processing." > input/test_folder/test.md

# Rumen will automatically process it and save results to bolus/
```

Check the output:

```bash
ls -la bolus/
```

## 🔧 Management Commands

Use the provided management script for common tasks:

```bash
# Start/Stop
./run-docker.sh start
./run-docker.sh stop

# View logs
./run-docker.sh logs

# Restart (after config changes)
./run-docker.sh restart

# Check status
./run-docker.sh status

# Clean up containers
./run-docker.sh clean

# Get API key
./run-docker.sh api-key
```

## ✅ Verification Checklist

- [ ] Docker and Docker Compose installed
- [ ] `.env` file created with LLM API key
- [ ] Rumen container starts without errors
- [ ] API key retrieved successfully
- [ ] Health endpoint responds
- [ ] Text processing works via API
- [ ] File monitoring enabled in config
- [ ] Test file processed automatically

## 🚨 Common First-Run Issues

### Container Won't Start
- Check Docker is running: `docker ps`
- Verify ports are available: `netstat -tulpn | grep 8000`
- Check logs: `./run-docker.sh logs`

### Authentication Errors
- Get your API key: `./run-docker.sh api-key`
- Include Bearer token in requests
- Check `.env` file exists and is readable

### File Processing Not Working
- Verify folder is enabled in `config/config.ini`
- Check input files have `.md` or `.txt` extension
- Ensure files are not empty
- Monitor logs: `./run-docker.sh logs -f`

### LLM API Errors
- Verify API key in `.env` is correct
- Check provider connectivity
- Review logs for specific error messages

## 🎉 Next Steps

Your Rumen instance is now ready! Explore these features:

1. **Customize Prompts**: Edit prompts in `config/config.ini` or use prompt files
2. **Add More Folders**: Configure additional monitored folders for different use cases
3. **Integrate with Apps**: Use the HTTP API from other applications
4. **Monitor Output**: Check the `bolus/` directory for processed results
5. **Scale Up**: Add more external volumes or customize configurations

## 📚 Further Reading

- [Configuration Guide](../configuration/configuration.md) - Detailed configuration options
- [API Reference](../api/overview.md) - Complete API documentation
- [Folder Monitoring](../configuration/folder-monitoring.md) - Advanced file processing setup
- [Troubleshooting](../advanced/troubleshooting.md) - Solutions for common problems

---

*Need help? Check the [Troubleshooting](../advanced/troubleshooting.md) guide or review the logs with `./run-docker.sh logs`.*