# Installation Guide

## System Requirements

### Minimum Requirements
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Disk Space**: 500MB free space
- **Memory**: 2GB RAM
- **Network**: Internet connection for LLM API calls

### Recommended Requirements
- **Docker**: Latest stable version
- **Docker Compose**: Latest version
- **Disk Space**: 1GB free space
- **Memory**: 4GB RAM or more
- **Network**: Stable internet connection

## Docker Installation

### Install Docker

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install docker.io

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, for convenience)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

#### macOS
```bash
# Install using Homebrew
brew install --cask docker

# Or download from Docker website:
# https://docs.docker.com/desktop/install/mac-install/
```

#### Windows
- Download Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
- Follow the installation wizard
- Enable WSL 2 backend for better performance

### Install Docker Compose

#### Linux
```bash
# Download latest version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

#### macOS/Windows
- Docker Compose is included with Docker Desktop

## Project Setup

### Clone or Download

#### Option 1: Clone Repository
```bash
git clone <repository-url>
cd rumen
```

#### Option 2: Download Archive
1. Download the latest release from the project repository
2. Extract the archive
3. Navigate to the extracted directory

### Verify Directory Structure

After setup, your project should have this structure:
```
rumen/
├── config/
│   └── config.ini
├── src/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run-docker.sh
└── .env.example
```

### Environment Setup

#### Create Environment File
```bash
# Copy the example file
cp .env.example .env

# Or create manually
touch .env
```

#### Configure API Keys

Edit the `.env` file and add your LLM provider API key:

```bash
# Choose one provider:

# For OpenRouter (recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# For Google Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# For DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

## LLM Provider Setup

### OpenRouter (Recommended)
1. Visit https://openrouter.ai/
2. Create an account
3. Generate an API key
4. Add funds if required for the models you want to use
5. Copy the API key to your `.env` file

### Google Gemini
1. Visit https://aistudio.google.com/
2. Create a project or use existing
3. Enable the Gemini API
4. Generate an API key
5. Copy the API key to your `.env` file

### OpenAI
1. Visit https://platform.openai.com/
2. Create an account
3. Generate an API key
4. Add billing information if required
5. Copy the API key to your `.env` file

### DeepSeek
1. Visit https://platform.deepseek.com/
2. Create an account
3. Generate an API key
4. Copy the API key to your `.env` file

## Verification Steps

### Check Docker Installation
```bash
# Verify Docker is running
docker --version
docker ps

# Verify Docker Compose
docker-compose --version
```

### Check Project Structure
```bash
# Verify key files exist
ls -la Dockerfile docker-compose.yml run-docker.sh

# Make management script executable
chmod +x run-docker.sh
```

### Test Setup
```bash
# Quick health check (before starting)
./run-docker.sh status

# Should show: "Rumen is not running"
```

## Platform-Specific Notes

### Linux
- Ensure your user has permissions to run Docker commands
- Consider setting up Docker to start on boot
- Monitor disk space for Docker images and volumes

### macOS
- Docker Desktop may require additional permissions
- Consider increasing allocated resources in Docker Desktop settings
- Monitor resource usage in Activity Monitor

### Windows
- Ensure WSL 2 is enabled for better performance
- Check Windows Subsystem for Linux installation
- Verify Docker Desktop is running in the system tray

## Troubleshooting Installation

### Docker Issues
```bash
# Check Docker service status
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker

# Check Docker logs
sudo journalctl -u docker.service
```

### Permission Issues
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker
```

### Port Conflicts
```bash
# Check if port 8000 is in use
netstat -tulpn | grep 8000

# Or use lsof (macOS/Linux)
lsof -i :8000
```

## Next Steps

After successful installation, proceed to:
- [First Run Guide](first-run.md) - Start Rumen and verify functionality
- [Configuration Guide](../configuration/configuration.md) - Customize settings
- [Quick Start Guide](quick-start.md) - Get up and running quickly

---

*Having issues? Check the [Troubleshooting Guide](../advanced/troubleshooting.md) for solutions to common problems.*