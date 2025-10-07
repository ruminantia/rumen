# Testing Guide

Rumen includes a comprehensive test suite to verify functionality, ensure reliability, and facilitate development. This guide covers all available testing options and best practices.

## Overview

The test suite provides multiple testing approaches for different scenarios:

- **Quick Health Checks**: Fast verification of basic functionality
- **Comprehensive API Testing**: Full endpoint validation with actual LLM calls
- **Development Testing**: Python-based testing for debugging and automation
- **Integration Testing**: End-to-end workflow verification

## Available Test Scripts

### `simple_test.sh` - Quick Health Check

**Purpose**: Fast, basic system verification without external dependencies

**Usage**:
```bash
# Basic test (will prompt for API key if needed)
./tests/simple_test.sh

# With explicit API key
./tests/simple_test.sh --api-key YOUR_API_KEY

# Skip API key prompt (for CI/CD)
./tests/simple_test.sh --no-prompt
```

**Tests Performed**:
- API root endpoint accessibility
- Authentication requirement enforcement
- Container status verification
- Port availability check
- Health endpoint functionality (with API key)

**Best For**: Initial setup verification, quick health checks, unreliable network environments

### `test_rumen.sh` - Comprehensive Bash Tests

**Purpose**: Full API functionality testing using curl commands

**Usage**:
```bash
# Full test suite
./tests/test_rumen.sh

# With explicit API key
./tests/test_rumen.sh --api-key YOUR_API_KEY

# Specific test category
./tests/test_rumen.sh --category api
```

**Tests Performed**:
- All API endpoints validation
- Authentication requirements
- Text processing via `/process` endpoint
- File monitor status and configuration
- Results listing and retrieval
- File creation and processing workflows

**Best For**: Complete system verification, integration testing, stable network environments

### `test_rumen.py` - Python Test Suite

**Purpose**: Comprehensive testing with Python requests library

**Requirements**: `pip install requests`

**Usage**:
```bash
# Run all tests
python tests/test_rumen.py

# With explicit API key
python tests/test_rumen.py --api-key YOUR_API_KEY

# Run specific test modules
python tests/test_rumen.py --module api
```

**Tests Performed**: Same comprehensive coverage as bash version with better error handling and reporting

**Best For**: Development, debugging, automated testing, CI/CD integration

## Test Recommendations

| Use Case | Recommended Test | Notes |
|----------|------------------|-------|
| Quick health check | `simple_test.sh` | Fast, minimal dependencies |
| Full system verification | `test_rumen.sh` | Comprehensive, requires stable internet |
| Development/debugging | `test_rumen.py` | Better error reporting, programmatic access |
| Unreliable internet | `simple_test.sh` | Minimal external calls |
| Stable internet | `test_rumen.sh` | Full functionality testing |
| CI/CD pipelines | `test_rumen.py` | Better integration, programmatic control |
| Production deployment | `simple_test.sh` + `test_rumen.sh` | Comprehensive verification |

## Getting Your API Key

Before running tests that require authentication, obtain your API key:

```bash
# Display the current API key
./run-docker.sh api-key

# Save to environment variable (for scripting)
export RUMEN_API_KEY=$(./run-docker.sh api-key)
```

## Test Environment Setup

### Prerequisites

1. **Rumen Running**: Ensure the service is active
   ```bash
   ./run-docker.sh status
   ```

2. **API Key Available**: Have your authentication key ready
   ```bash
   ./run-docker.sh api-key
   ```

3. **Test Permissions**: Ensure test scripts are executable
   ```bash
   chmod +x tests/*.sh
   ```

### Configuration for File Testing

For file monitoring tests, ensure at least one folder is enabled in `config/config.ini`:

```ini
[test_folder]
folder_path = /app/input/test_folder
enabled = true
system_prompt = You are a helpful assistant.
user_prompt_template = Please process: {content}
```

## Running Tests in Different Environments

### Development Environment

```bash
# Start Rumen in development mode
./run-docker.sh start

# Run comprehensive tests
python tests/test_rumen.py --api-key $(./run-docker.sh api-key)

# Monitor test execution
./run-docker.sh logs -f
```

### CI/CD Pipeline

```bash
#!/bin/bash
# Example CI/CD script

# Start Rumen
./run-docker.sh start

# Wait for service to be ready
sleep 30

# Run health check
./tests/simple_test.sh --no-prompt --api-key $RUMEN_API_KEY

# Run comprehensive tests if health check passes
if [ $? -eq 0 ]; then
    python tests/test_rumen.py --api-key $RUMEN_API_KEY
else
    echo "Health check failed"
    exit 1
fi
```

### Production Verification

```bash
# Quick health verification
./tests/simple_test.sh --api-key $PRODUCTION_API_KEY

# Basic functionality test
curl -H "Authorization: Bearer $PRODUCTION_API_KEY" \
  http://localhost:8000/health
```

## Test Categories

### API Endpoint Tests

- **Authentication**: Verify API key requirements
- **Health Checks**: Service status and connectivity
- **Text Processing**: LLM interaction and response formatting
- **File Management**: Processed file listing and retrieval
- **Configuration**: Folder and system settings

### File Processing Tests

- **File Detection**: New file recognition and processing
- **Format Support**: Markdown and text file handling
- **Output Generation**: Result file creation and formatting
- **Cleanup**: Input file removal after processing

### Integration Tests

- **End-to-End Workflow**: Complete file processing pipeline
- **Error Handling**: Graceful failure and recovery
- **Performance**: Processing time and resource usage
- **Concurrency**: Multiple file processing simultaneously

## Troubleshooting Test Failures

### Common Issues

**Authentication Errors**:
```bash
# Verify API key
./run-docker.sh api-key

# Test authentication manually
curl -H "Authorization: Bearer YOUR_KEY" http://localhost:8000/health
```

**Container Not Running**:
```bash
# Check container status
./run-docker.sh status

# Start if needed
./run-docker.sh start

# View logs for issues
./run-docker.sh logs
```

**File Processing Failures**:
```bash
# Check folder configuration
grep -A 10 "\[test_folder\]" config/config.ini

# Verify input directory
ls -la input/test_folder/

# Check file permissions
ls -la input/test_folder/test_file.md
```

**LLM API Errors**:
```bash
# Check provider connectivity
./run-docker.sh logs | grep -i error

# Verify API key in .env
cat .env | grep API_KEY
```

### Debugging Commands

```bash
# Check test script permissions
ls -la tests/

# Verify test environment
./tests/simple_test.sh --verbose

# Manual API testing
curl -v -H "Authorization: Bearer $API_KEY" http://localhost:8000/health

# Container inspection
docker exec rumen ps aux
```

## Test Automation

### Scheduled Testing

```bash
#!/bin/bash
# Daily health check script

API_KEY=$(./run-docker.sh api-key)
LOG_FILE="/var/log/rumen_test_$(date +%Y%m%d).log"

./tests/simple_test.sh --api-key $API_KEY >> $LOG_FILE 2>&1

if [ $? -ne 0 ]; then
    # Alert on failure
    echo "Rumen health check failed - check $LOG_FILE" | mail -s "Rumen Alert" admin@example.com
fi
```

### Integration with Monitoring

```bash
#!/bin/bash
# Integration with monitoring systems

API_KEY=$1
RESULT=$(curl -s -H "Authorization: Bearer $API_KEY" http://localhost:8000/health)

if echo "$RESULT" | grep -q "healthy"; then
    echo "OK - Rumen is healthy"
    exit 0
else
    echo "CRITICAL - Rumen health check failed"
    exit 2
fi
```

## Best Practices

### 1. Test Frequency
- **Development**: Run tests before each commit
- **Staging**: Comprehensive testing before deployment
- **Production**: Regular health checks (hourly/daily)

### 2. Environment Management
- Use different API keys for different environments
- Maintain separate configuration files
- Isolate test data from production data

### 3. Error Handling
- Implement graceful test failure
- Provide clear error messages
- Include retry logic for transient failures

### 4. Performance Considerations
- Monitor test execution time
- Set appropriate timeouts
- Clean up test data after runs

## Next Steps

- [Troubleshooting Guide](../advanced/troubleshooting.md) - Common issues and solutions
- [API Reference](../api/overview.md) - Detailed endpoint documentation
- [Configuration Guide](../configuration/configuration.md) - System configuration options
- [Development Guide](development.md) - Contributing and extending Rumen

---

*Regular testing ensures your Rumen instance remains reliable and functional. Incorporate these tests into your development and deployment workflows for best results.*