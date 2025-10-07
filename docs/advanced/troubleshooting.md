# Troubleshooting Guide

This guide helps you identify and resolve common issues with Rumen. Follow these steps to diagnose problems and implement solutions.

## Quick Diagnosis

### Health Check Commands

```bash
# Check if Rumen is running
./run-docker.sh status

# View recent logs
./run-docker.sh logs

# Test API connectivity
curl http://localhost:8000/

# Get your API key
./run-docker.sh api-key
```

### Common Symptoms and Solutions

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Container won't start | Missing .env file | Create .env with API key |
| Authentication errors | Invalid API key | Use `./run-docker.sh api-key` |
| Files not processing | Folder not enabled | Check config.ini `enabled=true` |
| LLM API errors | Provider API key invalid | Verify .env file |
| Port conflicts | Port 8000 in use | Change port in config.ini |

## Container Issues

### Container Won't Start

**Symptoms:**
- `./run-docker.sh status` shows "not running"
- `docker ps` doesn't list rumen container
- Startup errors in logs

**Diagnosis:**
```bash
# Check Docker service
docker ps

# View detailed error messages
./run-docker.sh logs

# Check port availability
netstat -tulpn | grep 8000

# Verify Docker Compose file
docker compose config
```

**Solutions:**

1. **Missing .env file:**
   ```bash
   # Create .env file
   cp .env.example .env
   # Edit with your API key
   nano .env
   ```

2. **Port conflict:**
   ```ini
   # In config/config.ini
   api_port = 8001
   ```
   Then restart: `./run-docker.sh restart`

3. **Docker issues:**
   ```bash
   # Restart Docker service (Linux)
   sudo systemctl restart docker
   
   # Clean up and rebuild
   ./run-docker.sh clean
   ./run-docker.sh start
   ```

### Container Crashes or Restarts

**Symptoms:**
- Container starts but stops immediately
- Frequent restarts
- High resource usage

**Diagnosis:**
```bash
# Check container status
docker ps -a

# View crash logs
docker logs rumen

# Check resource usage
docker stats rumen

# Monitor memory usage
docker exec rumen free -h
```

**Solutions:**

1. **Insufficient memory:**
   - Increase Docker memory allocation
   - Reduce concurrent processing in config
   - Monitor with `docker stats`

2. **API key issues:**
   ```bash
   # Verify .env file
   cat .env
   # Check for special characters or spaces
   ```

3. **Configuration errors:**
   ```bash
   # Validate config file
   docker exec rumen python -c "from src.config import ConfigManager; c = ConfigManager(); c.load_config()"
   ```

## Authentication Issues

### API Key Problems

**Symptoms:**
- 401 Unauthorized errors
- "Authentication required" messages
- Health endpoint fails

**Diagnosis:**
```bash
# Get current API key
./run-docker.sh api-key

# Test authentication
curl -H "Authorization: Bearer YOUR_KEY" http://localhost:8000/health

# Check .env file
cat .env | grep RUMEN_API_KEY
```

**Solutions:**

1. **Missing API key:**
   ```bash
   # Let Rumen generate one
   ./run-docker.sh restart
   ./run-docker.sh api-key
   ```

2. **Invalid API key format:**
   - Ensure no spaces or special characters
   - Key should be 32 characters
   - Regenerate if compromised

3. **Environment variable issues:**
   ```bash
   # Check container environment
   docker exec rumen env | grep RUMEN_API_KEY
   ```

### LLM Provider Authentication

**Symptoms:**
- "Invalid API key" from LLM provider
- Processing failures with specific providers
- Rate limit errors

**Diagnosis:**
```bash
# Check provider API keys
cat .env | grep API_KEY

# Test provider connectivity (replace with your key)
curl -H "Authorization: Bearer YOUR_LLM_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models"
```

**Solutions:**

1. **Invalid provider key:**
   - Verify key in provider dashboard
   - Check for typos in .env
   - Ensure proper provider prefix

2. **Rate limiting:**
   ```ini
   # In config/config.ini
   retry_attempts = 5
   retry_delay = 10
   ```

3. **Provider service issues:**
   - Check provider status page
   - Try alternative provider
   - Monitor provider-specific errors in logs

## File Processing Issues

### Files Not Processing

**Symptoms:**
- Files remain in input directories
- No output in bolus directory
- No processing logs

**Diagnosis:**
```bash
# Check folder configuration
grep -A 5 "enabled" config/config.ini

# Verify input directories
ls -la input/

# Check file permissions
ls -la input/*/*.md

# Monitor file detection
./run-docker.sh logs -f | grep -i "file\|process"
```

**Solutions:**

1. **Folder not enabled:**
   ```ini
   # In config/config.ini
   [your_folder]
   enabled = true
   ```

2. **Wrong file format:**
   - Use .md, .markdown, or .txt extensions
   - Ensure files are not empty
   - Check file encoding (UTF-8)

3. **File stability timeout:**
   ```ini
   # Increase timeout for large files
   file_timeout = 60
   ```

### Processing Failures

**Symptoms:**
- Files processed but no output
- Error messages in logs
- Partial processing

**Diagnosis:**
```bash
# Check processing logs
./run-docker.sh logs | grep -i error

# Verify output directory
ls -la bolus/

# Test with simple file
echo "Test content" > input/test_folder/test.md
```

**Solutions:**

1. **Prompt issues:**
   - Ensure `{content}` placeholder in user prompts
   - Check prompt file existence and readability
   - Validate prompt syntax

2. **Token limits:**
   ```ini
   # Increase token limit
   max_tokens = 4096
   ```

3. **Output directory problems:**
   ```bash
   # Check permissions
   docker exec rumen ls -la /app/bolus/
   
   # Ensure directory exists
   docker exec rumen mkdir -p /app/bolus
   ```

## Performance Issues

### Slow Processing

**Symptoms:**
- Long processing times
- Queue buildup
- High resource usage

**Diagnosis:**
```bash
# Check processing times
./run-docker.sh logs | grep "processing\|completed"

# Monitor resource usage
docker stats rumen

# Check network latency
docker exec rumen ping -c 3 generativelanguage.googleapis.com
```

**Solutions:**

1. **Optimize configuration:**
   ```ini
   # Reduce monitoring frequency
   monitor_interval = 10
   
   # Adjust timeouts
   file_timeout = 45
   ```

2. **Network issues:**
   - Check internet connectivity
   - Use closer LLM provider regions
   - Monitor provider status

3. **Resource constraints:**
   - Increase Docker memory allocation
   - Reduce concurrent processing
   - Optimize prompt complexity

### High Resource Usage

**Symptoms:**
- Container using excessive CPU/RAM
- System slowdown
- Processing delays

**Diagnosis:**
```bash
# Monitor resources
docker stats rumen

# Check process tree
docker exec rumen ps aux

# Monitor file handles
docker exec rumen lsof | grep rumen
```

**Solutions:**

1. **Limit concurrent processing:**
   ```ini
   # In config/config.ini
   api_workers = 1
   ```

2. **Optimize file handling:**
   - Process smaller files
   - Use appropriate chunk sizes
   - Clean up old processed files

3. **Memory management:**
   ```bash
   # Restart to clear memory
   ./run-docker.sh restart
   ```

## Network and Connectivity

### LLM API Connectivity

**Symptoms:**
- "Connection refused" errors
- Timeout messages
- Intermittent failures

**Diagnosis:**
```bash
# Test provider connectivity
docker exec rumen curl -I https://generativelanguage.googleapis.com/

# Check DNS resolution
docker exec rumen nslookup generativelanguage.googleapis.com

# Monitor network in container
docker exec rumen netstat -tulpn
```

**Solutions:**

1. **DNS issues:**
   ```yaml
   # In docker-compose.yml
   dns:
     - 8.8.8.8
     - 1.1.1.1
   ```

2. **Firewall/proxy:**
   - Configure proxy settings if needed
   - Check firewall rules
   - Verify outbound connectivity

3. **Provider outages:**
   - Check provider status pages
   - Use alternative providers
   - Implement retry logic

### Internal Network Issues

**Symptoms:**
- Container isolation problems
- Volume mount failures
- Inter-container communication issues

**Diagnosis:**
```bash
# Check network configuration
docker network ls
docker inspect rumen | grep -A 20 Networks

# Verify volume mounts
docker inspect rumen | grep -A 10 Mounts
```

**Solutions:**

1. **Network configuration:**
   ```yaml
   # Ensure proper network in docker-compose.yml
   networks:
     - rumen-network
   ```

2. **Volume mount issues:**
   - Verify volume existence
   - Check mount paths
   - Ensure proper permissions

## Configuration Issues

### Invalid Configuration

**Symptoms:**
- Configuration errors on startup
- Missing sections in config.ini
- Validation failures

**Diagnosis:**
```bash
# Validate config file
docker exec rumen python -c "
from src.config import ConfigManager
try:
    c = ConfigManager()
    c.load_config()
    print('Config valid')
except Exception as e:
    print(f'Config error: {e}')
"

# Check required sections
grep -E "\[.+\]" config/config.ini
```

**Solutions:**

1. **Missing sections:**
   ```ini
   # Ensure [DEFAULT] section exists
   [DEFAULT]
   provider = gemini
   # ... other required settings
   ```

2. **Invalid values:**
   - Temperature: 0.0-2.0
   - Max tokens: positive integer
   - Valid provider names

3. **File path issues:**
   - Use absolute paths in container
   - Verify file existence
   - Check permissions

### Prompt Configuration Issues

**Symptoms:**
- Processing with wrong prompts
- Missing content in output
- Formatting problems

**Diagnosis:**
```bash
# Test prompt loading
docker exec rumen python -c "
from src.config import get_settings
s = get_settings()
for name, folder in s.folders.items():
    print(f'{name}: {len(folder.load_system_prompt())} chars')
"

# Check prompt files
ls -la prompts/
```

**Solutions:**

1. **Prompt file issues:**
   - Ensure files exist in prompts/ directory
   - Check file permissions
   - Verify UTF-8 encoding

2. **Template problems:**
   - Include `{content}` placeholder
   - Avoid syntax errors
   - Test with sample content

## Log Analysis

### Understanding Log Messages

**Common log patterns and meanings:**

```
# Normal processing
"Processing file: /app/input/..."
"Successfully processed"
"Saved result to: /app/bolus/..."

# Errors
"API Error:" - LLM provider issues
"File error:" - File system problems
"Config error:" - Configuration issues
"Authentication failed:" - API key problems
```

### Enabling Debug Logging

```ini
# For detailed logging (development only)
# Add to config/config.ini
log_level = DEBUG
```

### Log Management

```bash
# View recent logs
./run-docker.sh logs

# Follow logs in real-time
./run-docker.sh logs -f

# Check specific time period
./run-docker.sh logs --since 1h

# Save logs to file
./run-docker.sh logs > rumen_debug.log
```

## Recovery Procedures

### Complete Reset

If all else fails, perform a complete reset:

```bash
# Stop and clean up
./run-docker.sh clean

# Remove volumes (caution: loses data)
docker volume prune

# Rebuild and restart
./run-docker.sh start
```

### Data Recovery

```bash
# Backup processed files
tar -czf bolus_backup_$(date +%Y%m%d).tar.gz bolus/

# Backup configuration
cp -r config/ config_backup_$(date +%Y%m%d)/
```

### Emergency Access

```bash
# Access container shell
docker exec -it rumen sh

# Check service status inside container
ps aux | grep python

# Manual configuration test
python -c "from src.config import get_settings; s = get_settings()"
```

## Getting Help

If you cannot resolve an issue:

1. **Collect diagnostic information:**
   ```bash
   # System information
   ./run-docker.sh status
   ./run-docker.sh api-key
   docker --version
   docker compose version
   
   # Configuration
   cat config/config.ini
   cat .env | grep API_KEY
   
   # Recent logs
   ./run-docker.sh logs --tail 100
   ```

2. **Check common issues:**
   - Verify all prerequisites are met
   - Confirm Docker and Docker Compose versions
   - Validate API keys with providers

3. **Seek community support:**
   - Provide detailed error messages
   - Include configuration (redact API keys)
   - Share relevant log excerpts

Remember to always backup your configuration and data before making significant changes.