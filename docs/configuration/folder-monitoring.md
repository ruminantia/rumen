# Folder Monitoring Guide

Rumen's file monitoring system automatically processes files in configured directories, making it ideal for automated content processing pipelines.

## Overview

The file monitoring system:
- Watches specified directories for new files
- Automatically processes files using configured prompts
- Saves results to output directories
- Cleans up processed files
- Handles multiple folders with different configurations

## Basic Setup

### 1. Create Folder Configuration

Add a new section to `config/config.ini`:

```ini
[my_folder]
folder_path = /app/input/my_folder
enabled = true
system_prompt = You are a helpful assistant.
user_prompt_template = Please process this content: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.7
max_tokens = 1024
output_format = markdown
```

### 2. Create Input Directory

```bash
# Create the directory locally
mkdir -p input/my_folder

# The directory will be mounted in the container at /app/input/my_folder
```

### 3. Restart and Test

```bash
# Restart to load new configuration
./run-docker.sh restart

# Add a test file
echo "# Test Content" > input/my_folder/test.md

# Monitor processing
./run-docker.sh logs -f
```

## Configuration Options

### Required Settings

- `folder_path`: Absolute path to monitor (must start with `/app/`)
- `enabled`: Set to `true` to activate monitoring
- `system_prompt`: Defines the AI's role and behavior
- `user_prompt_template`: Template with `{content}` placeholder

### Optional Settings

- `provider`: LLM provider (overrides default)
- `model`: Specific model to use
- `temperature`: Creativity level (0.0-2.0)
- `max_tokens`: Maximum response length
- `output_format`: Output format (`markdown` or `json`)
- `output_directory`: Custom output location

## File Processing Behavior

### Supported File Types

The system processes these file extensions:
- `.md` - Markdown files
- `.markdown` - Markdown files
- `.txt` - Plain text files

### Processing Flow

1. **File Detection**: System detects new or modified files
2. **Stability Check**: Waits for file to stop changing (30 seconds default)
3. **Content Reading**: Reads file content with UTF-8 encoding
4. **LLM Processing**: Sends content to configured LLM with prompts
5. **Result Saving**: Saves processed output to bolus directory
6. **Cleanup**: Deletes original input file

### File Stability

The system ensures files are complete before processing:
- Checks file size stability
- Default timeout: 30 seconds
- Configurable via `file_timeout` in `[DEFAULT]` section

## Multiple Folder Setup

### Independent Configurations

Each folder can have completely different settings:

```ini
[news_analysis]
folder_path = /app/input/news
enabled = true
system_prompt = You are a news analyst...
user_prompt_template = Analyze this news: {content}
provider = gemini
temperature = 0.3
max_tokens = 1024

[research_papers]
folder_path = /app/input/research
enabled = true
system_prompt = You are a research analyst...
user_prompt_template = Analyze this research: {content}
provider = openai
temperature = 0.5
max_tokens = 2048

[content_summary]
folder_path = /app/input/summary
enabled = true
system_prompt = You are a summarization expert...
user_prompt_template = Summarize this: {content}
provider = deepseek
temperature = 0.2
max_tokens = 512
```

### Concurrent Monitoring

All enabled folders are monitored simultaneously:
- Independent event handlers per folder
- Shared file processor for efficiency
- Separate configuration per folder
- Individual output directories possible

## Output Management

### Default Output Location

Processed files are saved to:
```
/app/bolus/
```

Files are named with timestamps and original filenames for tracking.

### Custom Output Directories

Specify folder-specific output locations:

```ini
[news_analysis]
output_directory = /app/bolus/news

[research_papers]
output_directory = /app/bolus/research
```

### Output File Naming

Output files follow this pattern:
```
{timestamp}_{original_filename}.{format}
```

Example: `20241201_143022_article.md`

## Advanced Features

### Recursive Directory Support

The system can handle nested directory structures:

```
/app/input/news/
├── 2024/
│   ├── 01/
│   │   ├── article1.md
│   │   └── article2.md
│   └── 02/
│       └── article3.md
└── 2025/
    └── ...
```

### File Filtering

The system automatically filters:
- Hidden files (starting with `.`)
- Temporary files (ending with `~`)
- Non-supported file types
- Empty files

### Error Handling

- Failed processing doesn't delete input files
- Retry logic for transient API errors
- Comprehensive error logging
- Graceful degradation

## Best Practices

### 1. Organize by Content Type

```ini
# News content - concise, factual
[news]
temperature = 0.3
max_tokens = 1024

# Creative content - more flexible
[creative]
temperature = 0.8
max_tokens = 2048

# Technical content - precise, detailed
[technical]
temperature = 0.2
max_tokens = 4096
```

### 2. Use Appropriate Token Limits

- **Short summaries**: 256-512 tokens
- **Standard articles**: 1024-2048 tokens
- **Long documents**: 4096+ tokens

### 3. Monitor Resource Usage

```bash
# Check container resource usage
docker stats rumen

# Monitor output directory size
du -sh bolus/

# Check processing queue
./run-docker.sh logs | grep "processing"
```

### 4. Implement File Naming Conventions

Use descriptive naming for easier tracking:
```
2024-01-15_news_article.md
research_paper_analysis.md
content_summary_v2.md
```

## Troubleshooting

### Common Issues

**Files Not Processing:**
- Check folder is enabled in config
- Verify file has supported extension (.md, .txt)
- Ensure file is not empty
- Check file permissions

**Processing Errors:**
- Review logs: `./run-docker.sh logs`
- Check LLM API key validity
- Verify prompt templates contain `{content}`
- Ensure sufficient tokens for content length

**Performance Issues:**
- Reduce monitoring interval if too frequent
- Increase file timeout if files are large
- Monitor LLM API rate limits
- Check network connectivity

### Monitoring Commands

```bash
# View real-time processing
./run-docker.sh logs -f

# Check folder status
docker exec rumen ls -la /app/input/

# Verify output
docker exec rumen ls -la /app/bolus/

# Test file detection
docker exec rumen touch /app/input/my_folder/test.md
```

## Example Use Cases

### News Aggregation

```ini
[news_aggregation]
folder_path = /app/input/news
enabled = true
system_prompt = You are a news aggregator. Extract key facts, summarize main points, and identify important entities.
user_prompt_template = Please analyze this news article: {content}
provider = gemini
temperature = 0.3
max_tokens = 1024
output_format = markdown
output_directory = /app/bolus/news
```

### Research Paper Analysis

```ini
[research_analysis]
folder_path = /app/input/research
enabled = true
system_prompt = You are a research analyst. Extract methodology, key findings, limitations, and future work.
user_prompt_template = Analyze this research paper: {content}
provider = openai
temperature = 0.5
max_tokens = 2048
output_format = markdown
output_directory = /app/bolus/research
```

### Content Summarization

```ini
[content_summary]
folder_path = /app/input/summary
enabled = true
system_prompt = You are a summarization expert. Create concise summaries that preserve key information.
user_prompt_template = Summarize this content: {content}
provider = deepseek
temperature = 0.2
max_tokens = 512
output_format = markdown
output_directory = /app/bolus/summary
```

## Next Steps

- [Prompt Management](prompt-management.md) - Advanced prompt configuration
- [External Volumes](external-volumes.md) - Docker volume integration
- [API Reference](../api/overview.md) - HTTP API documentation
- [Troubleshooting](../advanced/troubleshooting.md) - Common issues and solutions