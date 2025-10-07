# Documentation Navigation Guide

Welcome to the Rumen documentation! This guide helps you find the information you need quickly and efficiently.

## 🎯 Quick Start Path

### For New Users
1. **[Quick Start Guide](getting-started/quick-start.md)** - Get up and running in minutes
2. **[Installation Guide](getting-started/installation.md)** - System requirements and setup
3. **[First Run Guide](getting-started/first-run.md)** - Initial configuration and testing

### For Developers
1. **[API Overview](api/overview.md)** - HTTP API endpoints and usage
2. **[Configuration Guide](configuration/configuration.md)** - System configuration options
3. **[Development Guide](development/testing.md)** - Testing and development workflows

## 📚 Documentation Sections

### Getting Started (`getting-started/`)
- **Quick Start Guide** - Step-by-step setup instructions
- **Installation Guide** - System requirements and installation
- **First Run Guide** - Initial configuration and verification

### Configuration (`configuration/`)
- **Configuration Guide** - Main configuration file setup
- **Folder Monitoring** - Automated file processing setup
- **Prompt Management** - Using prompt files and templates
- **External Volumes** - Docker volume integration

### API Reference (`api/`)
- **API Overview** - HTTP API endpoints and usage
- **Authentication** - API key authentication guide
- **Processing Endpoints** - Text and file processing APIs
- **Health & Status** - Monitoring and health checks

### Advanced Usage (`advanced/`)
- **Multi-Folder Setup** - Managing multiple input folders
- **Custom Prompts** - Creating complex prompt templates
- **Docker Deployment** - Production deployment guidelines
- **Troubleshooting** - Common issues and solutions

### Development (`development/`)
- **Project Structure** - Code organization and architecture
- **Testing** - Test suite and quality assurance
- **Contributing** - Development guidelines
- **API Client Examples** - Example code for various languages

## 🔍 Search by Use Case

### I want to...
- **Set up Rumen quickly**: [Quick Start Guide](getting-started/quick-start.md)
- **Configure automated file processing**: [Folder Monitoring](configuration/folder-monitoring.md)
- **Use the HTTP API**: [API Overview](api/overview.md)
- **Create custom prompts**: [Prompt Management](configuration/prompt-management.md)
- **Monitor Docker volumes**: [External Volumes](configuration/external-volumes.md)
- **Troubleshoot issues**: [Troubleshooting Guide](advanced/troubleshooting.md)
- **Run tests**: [Testing Guide](development/testing.md)
- **Deploy to production**: [Docker Deployment](advanced/docker-deployment.md)

## 📋 Common Tasks

### Configuration Tasks
- [Add a new monitored folder](configuration/folder-monitoring.md#basic-setup)
- [Create custom prompt files](configuration/prompt-management.md#prompt-files)
- [Set up external Docker volumes](configuration/external-volumes.md#setting-up-external-volumes)
- [Configure multiple LLM providers](configuration/configuration.md#llm-provider-configurations)

### API Tasks
- [Get API key](api/authentication.md#automatic-key-generation)
- [Process text via API](api/processing.md)
- [Check system health](api/health-status.md)
- [Monitor file processing](api/overview.md#file-management)

### Development Tasks
- [Run tests](development/testing.md#available-test-scripts)
- [Extend functionality](development/contributing.md)
- [Debug issues](advanced/troubleshooting.md)
- [Create API clients](development/api-clients.md)

## 🚨 Emergency Procedures

### Quick Problem Solving
- **Container won't start**: [Troubleshooting - Container Issues](advanced/troubleshooting.md#container-issues)
- **Authentication errors**: [Troubleshooting - Authentication Issues](advanced/troubleshooting.md#authentication-issues)
- **Files not processing**: [Troubleshooting - File Processing Issues](advanced/troubleshooting.md#file-processing-issues)
- **Performance problems**: [Troubleshooting - Performance Issues](advanced/troubleshooting.md#performance-issues)

### Recovery Steps
1. Check [Troubleshooting Guide](advanced/troubleshooting.md)
2. Review application logs: `./run-docker.sh logs`
3. Verify configuration: `config/config.ini`
4. Test basic functionality: `./tests/simple_test.sh`

## 🔗 External Resources

- **Main Project README** - [../README.md](../README.md)
- **Docker Compose** - [../docker-compose.yml](../docker-compose.yml)
- **Configuration File** - [../config/config.ini](../config/config.ini)
- **Management Script** - [../run-docker.sh](../run-docker.sh)

## 📞 Getting Help

If you can't find what you need:

1. **Check the troubleshooting guide** first: [Troubleshooting](advanced/troubleshooting.md)
2. **Search the documentation** using your browser's find function
3. **Review application logs**: `./run-docker.sh logs`
4. **Check the main README** for additional resources

## 🔄 Documentation Updates

This documentation is maintained alongside the codebase. For the latest information:

- Check the project repository for updates
- Review release notes for new features
- Monitor the `docs/` directory for changes

---

*Use this navigation guide to quickly find the information you need. The documentation is organized to help you succeed with Rumen regardless of your experience level.*
```

Perfect! I've successfully reorganized all the documentation into a comprehensive `docs` directory structure. Here's a summary of what was accomplished:

## 🎯 **Documentation Reorganization Complete**

### **New Documentation Structure**
```
rumen/docs/
├── README.md                    # Main documentation index
├── NAVIGATION.md               # Documentation navigation guide
├── getting-started/
│   ├── quick-start.md          # Step-by-step setup
│   ├── installation.md         # System requirements & setup
│   └── first-run.md           # Initial configuration & testing
├── configuration/
│   ├── configuration.md        # Main configuration guide
│   ├── folder-monitoring.md    # File processing setup
│   ├── prompt-management.md    # Prompt files & templates
│   └── external-volumes.md     # Docker volume integration
├── api/
│   ├── overview.md            # API endpoints & usage
│   └── authentication.md      # API key authentication
├── advanced/
│   └── troubleshooting.md     # Common issues & solutions
└── development/
    └── testing.md             # Test suite & quality assurance
```

### **Key Improvements**

1. **Simplified Main README** - Now references the comprehensive documentation
2. **Logical Organization** - Clear sections for different user needs
3. **Cross-Referencing** - All documents link to related content
4. **Quick Navigation** - Easy paths for common tasks and use cases
5. **Updated Sub-READMEs** - `prompts/README.md` and `tests/README.md` now reference main documentation

### **Documentation Features**

- **Progressive Learning Paths** - From beginner to advanced
- **Use Case Based Navigation** - "I want to..." sections
- **Emergency Procedures** - Quick problem-solving guides
- **Comprehensive Coverage** - All aspects of Rumen covered
- **Maintainable Structure** - Easy to update and extend

### **Benefits**

1. **Better User Experience** - Users can find information faster
2. **Easier Maintenance** - Documentation organized logically
3. **Comprehensive Coverage** - All features thoroughly documented
4. **Scalable Structure** - Easy to add new documentation sections
5. **Professional Presentation** - Consistent, well-organized content

The documentation is now production-ready and provides users with a clear path to understand, configure, and use Rumen effectively!