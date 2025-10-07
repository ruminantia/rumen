# Rumen - Containerized LLM API

Rumen is a containerized API for interacting with Large Language Models (LLMs) via HTTP API and file system monitoring. It provides a flexible, secure way to process text content using various LLM providers.

## 🚀 Quick Start

Get up and running in minutes:

```bash
# Clone and setup
cd rumen
chmod +x run-docker.sh

# Configure API key (edit .env file)
cp .env.example .env

# Start Rumen
./run-docker.sh start

# Get API key for authentication
./run-docker.sh api-key

# Test the API
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/health
```

For detailed setup instructions, see the [Quick Start Guide](docs/getting-started/quick-start.md).

## ✨ Features

- **Multiple LLM Providers**: Support for OpenRouter, OpenAI, Google Gemini, and DeepSeek
- **Dual Operation Modes**: HTTP API for direct interaction and file monitoring for automated processing
- **Secure by Design**: API key authentication and internal networking
- **Configurable Processing**: Custom prompts and parameters per monitored folder
- **Prompt Management**: Store complex prompts as individual files for better organization
- **External Volume Support**: Monitor Docker volumes for automated processing
- **Error Handling**: Graceful retries and comprehensive error logging
- **Containerized**: Easy deployment with Docker and Docker Compose

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### Getting Started
- [Quick Start Guide](docs/getting-started/quick-start.md) - Get up and running in minutes
- [Installation Guide](docs/getting-started/installation.md) - System requirements and setup
- [First Run Guide](docs/getting-started/first-run.md) - Initial configuration and testing

### Configuration
- [Configuration Guide](docs/configuration/configuration.md) - Main configuration file setup
- [Folder Monitoring](docs/configuration/folder-monitoring.md) - Setting up automated file processing
- [Prompt Management](docs/configuration/prompt-management.md) - Using prompt files and templates
- [External Volumes](docs/configuration/external-volumes.md) - Integrating with Docker volumes

### API Reference
- [API Overview](docs/api/overview.md) - HTTP API endpoints and usage
- [Authentication](docs/api/authentication.md) - API key authentication
- [Processing Endpoints](docs/api/processing.md) - Text and file processing APIs
- [Health & Status](docs/api/health-status.md) - Monitoring and health checks

### Advanced Usage
- [Multi-Folder Setup](docs/advanced/multi-folder.md) - Managing multiple input folders
- [Custom Prompts](docs/advanced/custom-prompts.md) - Creating complex prompt templates
- [Docker Deployment](docs/advanced/docker-deployment.md) - Production deployment guidelines
- [Troubleshooting](docs/advanced/troubleshooting.md) - Common issues and solutions

### Development
- [Project Structure](docs/development/project-structure.md) - Code organization and architecture
- [Testing](docs/development/testing.md) - Test suite and quality assurance
- [Contributing](docs/development/contributing.md) - Development guidelines
- [API Client Examples](docs/development/api-clients.md) - Example code for various languages

## 🛠️ Management

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

## 📁 Project Structure

```
rumen/
├── config/           # Configuration files
├── docs/            # Comprehensive documentation
├── src/             # Python source code
├── prompts/         # Prompt files for complex prompts
├── input/           # Input files for processing
├── bolus/           # Output files (processed results)
├── tests/           # Test scripts and suites
├── Dockerfile       # Container definition
├── docker-compose.yml # Service orchestration
└── run-docker.sh    # Management script
```

## 🔧 Configuration

The main configuration file is `config/config.ini`. Key sections:

- `[DEFAULT]` - Global settings and LLM provider defaults
- Provider sections (`[gemini]`, `[openai]`, etc.) - Provider-specific settings
- Folder sections (`[worldnews]`, `[research]`, etc.) - Folder monitoring configurations

Example folder configuration:
```ini
[my_folder]
folder_path = /app/input/my_folder
enabled = true
system_prompt = You are a helpful assistant.
user_prompt_template = Please process: {content}
provider = gemini
model = gemini-2.5-flash-lite
```

## 🔌 API Usage

### Basic Text Processing
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  -X POST "http://localhost:8000/process?text=Hello%20world&system_prompt=You%20are%20a%20helpful%20assistant&user_prompt=Please%20respond%20to%3A%20%7Bcontent%7D"
```

### File Monitoring
Enable folders in `config/config.ini` and place files in the corresponding input directories. Rumen will automatically process them and save results to the `bolus/` directory.

## 🎯 Use Cases

- **News Analysis**: Automatically process and summarize news articles
- **Research Papers**: Analyze academic content and extract key insights
- **Content Summarization**: Create concise summaries of long documents
- **Data Processing**: Transform and analyze text data from various sources
- **Integration**: Connect with other applications via HTTP API

## 🤝 Support

If you encounter issues:

1. Check the [Troubleshooting Guide](docs/advanced/troubleshooting.md)
2. Review the application logs: `./run-docker.sh logs`
3. Verify your configuration in `config/config.ini`
4. Ensure your LLM provider API key is valid

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file included in the repository.

## 🔄 Updates

For the latest updates, check the project repository and release notes. The documentation in the `docs/` directory is maintained alongside the codebase.

---

*Rumen - Containerized LLM API for automated text processing*