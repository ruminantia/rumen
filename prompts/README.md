# Prompts Directory

This directory contains prompt files for the Rumen LLM API system. Instead of storing complex prompts directly in the `config.ini` file, you can now store them as individual markdown files for better organization and maintainability.

## Structure

Each folder configuration in `config.ini` can reference two types of prompt files:

- **System Prompt Files** (`*_system.md`): Define the AI assistant's role, behavior, and capabilities
- **User Prompt Templates** (`*_user.md`): Define the user-facing prompt template with `{content}` placeholder

## Usage

### 1. Create Prompt Files

Create markdown files for your prompts in this directory. For example, for a "news_analysis" folder:

- `news_analysis_system.md` - System prompt defining the AI's role
- `news_analysis_user.md` - User prompt template with `{content}` placeholder

### 2. Update Config.ini

Reference these files in your `config.ini`:

```ini
[news_analysis]
folder_path = /app/input/news_analysis
enabled = true
system_prompt_file = prompts/news_analysis_system.md
user_prompt_file = prompts/news_analysis_user.md
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.3
max_tokens = 1024
output_format = markdown
```

### 3. File Naming Convention

Use descriptive names that match your folder configurations:
- `{folder_name}_system.md`
- `{folder_name}_user.md`

## Benefits

- **Better Organization**: Complex prompts are easier to read and maintain in separate files
- **Version Control**: Track prompt changes independently from configuration
- **Reusability**: Share prompts across multiple folder configurations
- **Collaboration**: Multiple team members can work on prompts simultaneously
- **Testing**: Easier to test and iterate on prompts without touching configuration

## Best Practices

1. **Use Descriptive Names**: Name files clearly to indicate their purpose
2. **Include Placeholders**: User prompt templates must include `{content}` for content substitution
3. **Document Complex Logic**: Use comments in markdown files for complex prompt logic
4. **Test Prompts**: Test new prompts with sample content before deploying
5. **Version Your Prompts**: Consider adding version numbers to prompt files for tracking

## Example Prompt Files

### System Prompt Example (`worldnews_system.md`)
```markdown
You are a news analyst with expertise in global affairs, politics, economics, and social trends. Your role is to analyze news articles and provide comprehensive, balanced analysis...

[Detailed system prompt content]
```

### User Prompt Template Example (`worldnews_user.md`)
```markdown
Please analyze this news article and provide a comprehensive analysis:

**Article Content:**
{content}

**Analysis Requirements:**
1. Executive Summary: Begin with a 2-3 sentence overview...
2. Key Facts: Extract the essential information...

[Detailed user prompt template with {content} placeholder]
```

## Fallback Behavior

If a prompt file is not found or cannot be read, the system will fall back to using the inline `system_prompt` and `user_prompt_template` values from the config.ini file (if provided).

## Troubleshooting

- **File Not Found**: Ensure the file paths in config.ini are correct relative to the application root
- **Permission Issues**: Verify the application has read access to the prompt files
- **Encoding Problems**: Use UTF-8 encoding for all prompt files to handle special characters
- **Template Errors**: Ensure user prompt templates contain the `{content}` placeholder

## Docker Deployment

When deploying with Docker, the prompts directory is automatically copied into the container at `/app/prompts/`. The config.ini file paths should use relative paths like `prompts/filename.md`.