# Rumen Test Suite

This directory contains test scripts for verifying Rumen LLM API functionality.

## Available Tests

### `simple_test.sh` - Quick Health Check
**Purpose**: Fast, basic system verification without external dependencies  
**Usage**: 
```bash
./tests/simple_test.sh
./tests/simple_test.sh --api-key YOUR_API_KEY
```
**Tests**:
- API root endpoint accessibility
- Authentication requirement enforcement
- Container status
- Port availability
- Health endpoint (with API key)

**Best for**: Initial setup verification, quick health checks

### `test_rumen.sh` - Comprehensive Bash Tests
**Purpose**: Full API functionality testing using curl commands  
**Usage**:
```bash
./tests/test_rumen.sh
./tests/test_rumen.sh --api-key YOUR_API_KEY
```
**Tests**:
- All API endpoints
- Authentication requirements
- Text processing via `/process` endpoint
- File monitor status
- Results listing
- File creation for processing

**Best for**: Complete system verification, integration testing

### `test_rumen.py` - Python Test Suite
**Purpose**: Comprehensive testing with Python requests library  
**Usage**:
```bash
python tests/test_rumen.py
python tests/test_rumen.py --api-key YOUR_API_KEY
```
**Requirements**: `pip install requests`

**Tests**: Same comprehensive coverage as bash version

**Best for**: Development, debugging, automated testing

## Getting Your API Key

Before running tests that require authentication, get your API key:

```bash
# From the project root
./run-docker.sh api-key
```

## Test Recommendations

| Use Case | Recommended Test |
|----------|------------------|
| Quick health check | `simple_test.sh` |
| Full system verification | `test_rumen.sh` |
| Development/debugging | `test_rumen.py` |
| Unreliable internet | `simple_test.sh` |
| Stable internet | `test_rumen.sh` |

## Notes

- **Authentication**: Most endpoints require Bearer token authentication
- **File Processing**: File monitoring tests require folders to be enabled in `config/config.ini`
- **LLM Dependencies**: Some tests make actual LLM API calls and may fail with poor internet connectivity
- **Container**: Ensure Rumen is running with `./run-docker.sh status` before testing

## Troubleshooting

- **Permission denied**: Run `chmod +x tests/*.sh` to make scripts executable
- **API key not found**: Use `./run-docker.sh api-key` to display your key
- **Container not running**: Start with `./run-docker.sh start`
- **Authentication errors**: Ensure API key is included with `--api-key` flag