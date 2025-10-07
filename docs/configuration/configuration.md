# Configuration Guide

Rumen uses a flexible configuration system based on INI files. The main configuration file is `config/config.ini`, which defines global settings, LLM provider configurations, and folder-specific monitoring setups.

## Configuration File Structure

The configuration file is organized into sections:

- `[DEFAULT]` - Global settings and defaults
- Provider sections (`[gemini]`, `[openai]`, `[openrouter]`, `[deepseek]`) - Provider-specific settings
- Folder sections (`[worldnews]`, `[research]`, etc.) - Folder monitoring configurations

## Global Settings ([DEFAULT] Section)

### LLM Provider Settings

```ini
[DEFAULT]
# Default LLM provider settings
provider = gemini
model = gemini-2.5-flash-lite
base_url = https://generativelanguage.googleapis.com/v1beta
temperature = 0.7
max_tokens = 2048
top_p = 0.9
thinking_enabled = false
search_enabled = false
retry_attempts = 3
retry_delay = 2
```

**Settings:**
- `provider`: Default LLM provider (`gemini`, `openai`, `openrouter`, `deepseek`)
- `model`: Default model name
- `base_url`: API endpoint URL
- `temperature`: Creativity level (0.0-2.0, higher = more creative)
- `max_tokens`: Maximum response length
- `top_p`: Diversity sampling parameter (0.0-1.0)
- `thinking_enabled`: Enable chain-of-thought reasoning
- `search_enabled`: Enable web search (if supported)
- `retry_attempts`: Number of retries on API failure
- `retry_delay`: Delay between retries in seconds

### API Server Settings

```ini
# API settings
api_host = 0.0.0.0
api_port = 8000
api_workers = 1
```

**Settings:**
- `api_host`: Bind address for the API server
- `api_port`: Port for the API server
- `api_workers`: Number of worker processes

### File Monitoring Settings

```ini
# File monitoring settings
monitor_interval = 5
file_timeout = 30
```

**Settings:**
- `monitor_interval`: How often to check for new files (seconds)
- `file_timeout`: How long to wait for file stability before processing (seconds)

### Output Settings

```ini
# Output settings
output_format = markdown
output_directory = /app/bolus
```

**Settings:**
- `output_format`: Default output format (`markdown`, `json`)
- `output_directory`: Default directory for processed results

## LLM Provider Configurations

### Gemini Configuration

```ini
[gemini]
# Gemini specific settings
# No additional headers needed for Gemini
```

### OpenAI Configuration

```ini
[openai]
# OpenAI specific settings
base_url = https://api.openai.com/v1
```

### OpenRouter Configuration

```ini
[openrouter]
# OpenRouter specific settings
base_url = https://openrouter.ai/api/v1
http_referer =
x_title =
```

**Settings:**
- `http_referer`: HTTP Referer header for OpenRouter
- `x_title`: X-Title header for OpenRouter

### DeepSeek Configuration

```ini
[deepseek]
# DeepSeek specific settings
base_url = https://api.deepseek.com/v1
```

## Folder Monitoring Configurations

Each monitored folder has its own configuration section. Folder sections can override global settings.

### Basic Folder Configuration

```ini
[worldnews]
folder_path = /app/input/worldnews
enabled = true
system_prompt = You are a news analyst. Analyze the provided news article and extract key information, summarize the main points, and provide context.
user_prompt_template = Please analyze this news article: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.3
max_tokens = 1024
output_format = markdown
# output_directory = /app/bolus/worldnews  # Uncomment to use custom output folder
```

### Configuration Options

**Required Settings:**
- `folder_path`: Absolute path to the folder to monitor
- `enabled`: Whether this folder is actively monitored (`true`/`false`)
- `system_prompt`: The system prompt defining the AI's role
- `user_prompt_template`: User prompt template with `{content}` placeholder

**Optional Settings (override defaults):**
- `provider`: LLM provider for this folder
- `model`: Model name for this folder
- `temperature`: Temperature setting for this folder
- `max_tokens`: Maximum tokens for this folder
- `output_format`: Output format for this folder
- `output_directory`: Custom output directory (overrides global setting)

## Using Prompt Files

For complex prompts, you can reference external prompt files instead of inline prompts:

```ini
[research]
folder_path = /app/input/research
enabled = true
system_prompt_file = prompts/research_system.md
user_prompt_file = prompts/research_user.md
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.5
max_tokens = 2048
output_format = markdown
```

**Prompt File Benefits:**
- Better organization for complex prompts
- Version control for prompt changes
- Reusability across multiple folders
- Easier collaboration

## Environment Variables

API keys are configured via environment variables in the `.env` file:

```bash
# LLM Provider API Keys
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here

# Rumen API Authentication
RUMEN_API_KEY=automatically_generated_key
```

## Configuration Best Practices

### 1. Organize by Use Case

Create separate folder configurations for different types of content:

```ini
[news_analysis]
# For news articles - lower temperature, concise outputs

[research_papers]
# For academic content - higher temperature, detailed analysis

[content_summary]
# For summarization - very low temperature, focused outputs
```

### 2. Use Appropriate Settings

- **Temperature**: Use lower values (0.1-0.5) for factual content, higher (0.7-1.0) for creative tasks
- **Max Tokens**: Set based on expected output length (512-4096 typically)
- **Provider**: Choose based on cost, performance, and model availability

### 3. Enable Folders Selectively

Only enable folders you're actively using to conserve resources:

```ini
[archive]
folder_path = /app/input/archive
enabled = false  # Disabled until needed
```

### 4. Use Custom Output Directories

Organize output by content type:

```ini
[worldnews]
output_directory = /app/bolus/news

[research]
output_directory = /app/bolus/academic
```

## Configuration Validation

The system validates configuration on startup. Common validation errors:

- Missing required folder paths
- Invalid provider names
- Temperature outside valid range (0.0-2.0)
- Non-existent prompt files
- Invalid output formats

## Reloading Configuration

Configuration changes require a restart to take effect:

```bash
./run-docker.sh restart
```

## Example Configurations

### News Analysis Setup

```ini
[news_analysis]
folder_path = /app/input/news
enabled = true
system_prompt = You are a news analyst. Extract key facts, summarize main points, and provide context.
user_prompt_template = Analyze this news article: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.3
max_tokens = 1024
output_format = markdown
output_directory = /app/bolus/news
```

### Research Paper Analysis

```ini
[research_papers]
folder_path = /app/input/research
enabled = true
system_prompt = You are a research analyst. Extract key findings, methodology, and implications.
user_prompt_template = Analyze this research paper: {content}
provider = openai
model = gpt-4
temperature = 0.5
max_tokens = 2048
output_format = markdown
output_directory = /app/bolus/research
```

## Next Steps

- [Folder Monitoring](folder-monitoring.md) - Detailed file monitoring setup
- [Prompt Management](prompt-management.md) - Advanced prompt configuration
- [External Volumes](external-volumes.md) - Docker volume integration
- [Troubleshooting](../advanced/troubleshooting.md) - Configuration issue resolution