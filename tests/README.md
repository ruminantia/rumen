# Rumen Test Suite

> [!NOTE]
> This documentation has been moved to the main documentation directory.
> For the most up-to-date information, see [Testing](../docs/development/testing.md) in the main documentation.

This directory contains test scripts for verifying Rumen LLM API functionality.

## 📚 Documentation

For comprehensive testing documentation, including:
- Test strategy and methodology
- Running tests in different environments
- Test automation and CI/CD integration
- Debugging and troubleshooting tests

Please refer to the main documentation:
- [Testing Guide](../docs/development/testing.md)
- [Troubleshooting Guide](../docs/advanced/troubleshooting.md)
- [Quick Start Guide](../docs/getting-started/quick-start.md)

## 🚀 Quick Reference

### Quick Health Check
```bash
# Basic system verification
./tests/simple_test.sh

# With API key
./tests/simple_test.sh --api-key YOUR_API_KEY
```

### Comprehensive Testing
```bash
# Full API functionality testing
./tests/test_rumen.sh

# Python test suite
python tests/test_rumen.py
```

### Get API Key
```bash
# Required for authenticated tests
./run-docker.sh api-key
```

## 🔗 Related Documentation

- [Testing Guide](../docs/development/testing.md) - Complete testing documentation
- [Troubleshooting Guide](../docs/advanced/troubleshooting.md) - Test failure resolution
- [API Reference](../docs/api/overview.md) - API endpoint documentation
- [Configuration Guide](../docs/configuration/configuration.md) - System configuration

## 🆘 Troubleshooting

For test troubleshooting help, see the [Troubleshooting Guide](../docs/advanced/troubleshooting.md) in the main documentation.

---
*This directory contains test scripts. For detailed testing documentation, refer to the main documentation in the `docs/` directory.*

















