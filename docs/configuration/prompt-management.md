# Prompt Management Guide

Rumen provides flexible prompt management through both inline configuration and external prompt files, allowing you to create sophisticated AI interactions for different content types.

## Overview

Prompts in Rumen consist of two components:

- **System Prompt**: Defines the AI's role, behavior, and capabilities
- **User Prompt Template**: Contains the user-facing instruction with `{content}` placeholder

## Inline Prompts

### Basic Inline Configuration

```ini
[my_folder]
system_prompt = You are a helpful assistant. Provide clear, concise responses.
user_prompt_template = Please analyze this content: {content}
```

### Advanced Inline Prompts

For complex prompts, use multi-line configuration:

```ini
[research_analysis]
system_prompt = You are a research analyst with expertise in scientific literature. Your role is to extract key findings, evaluate methodology, identify limitations, and suggest future research directions. Maintain academic rigor while ensuring clarity for non-specialist readers.

user_prompt_template = Please analyze this research paper:

**Paper Content:**
{content}

**Analysis Requirements:**
1. Extract key findings and conclusions
2. Evaluate research methodology
3. Identify stated limitations
4. Suggest future research directions
5. Provide context within the field

Format your response in clear markdown with appropriate headings.
```

## Prompt Files

For complex or reusable prompts, use external prompt files.

### File Structure

```
prompts/
├── news_system.md
├── news_user.md
├── research_system.md
├── research_user.md
├── summary_system.md
└── summary_user.md
```

### Configuration with Prompt Files

```ini
[news_analysis]
system_prompt_file = prompts/news_system.md
user_prompt_file = prompts/news_user.md
```

### Example Prompt Files

**System Prompt File** (`prompts/news_system.md`):
```markdown
You are a news analyst with expertise in global affairs, politics, economics, and social trends. Your role is to analyze news articles and provide comprehensive, balanced analysis.

When analyzing news articles:

1. **Extract Key Information**: Identify the who, what, when, where, why, and how
2. **Summarize Main Points**: Provide a concise yet comprehensive summary
3. **Provide Context**: Explain how this story fits into broader trends
4. **Identify Implications**: Discuss potential consequences
5. **Maintain Objectivity**: Present facts clearly while acknowledging perspectives

Focus on delivering analysis that is:
- Factual and evidence-based
- Clear and well-structured
- Insightful and contextual
- Balanced and objective
- Actionable for quick understanding

Avoid sensationalism and maintain a professional, analytical tone.
```

**User Prompt Template File** (`prompts/news_user.md`):
```markdown
Please analyze this news article and provide a comprehensive analysis:

**Article Content:**
{content}

**Analysis Requirements:**

1. **Executive Summary**: Begin with a 2-3 sentence overview
2. **Key Facts**: Extract essential information (who, what, when, where, why, how)
3. **Main Points**: Summarize core arguments and findings
4. **Context & Background**: Explain relevant historical or social context
5. **Significance**: Discuss why this story matters
6. **Related Developments**: Mention connected events or trends
7. **Expert Perspectives**: Note any expert opinions cited

Format your response in clear, well-structured markdown with appropriate headings. Focus on delivering objective, factual analysis.
```

## Prompt Design Best Practices

### Effective System Prompts

**Good Examples:**
```markdown
# Clear role definition
You are a technical writer specializing in software documentation.

# Specific behavior guidance
Focus on clarity, accuracy, and practical examples. Avoid jargon when possible.

# Output format specification
Structure responses with clear headings, bullet points, and code examples when relevant.
```

**Poor Examples:**
```markdown
# Too vague
Be helpful.

# Contradictory instructions
Be concise but also provide extensive details.

# No clear role
Just answer the question.
```

### Effective User Prompt Templates

**Good Examples:**
```markdown
Please summarize this technical document, focusing on:
- Key concepts and definitions
- Implementation steps
- Common use cases
- Potential pitfalls

Format as a markdown document with clear section headings.
```

**Poor Examples:**
```markdown
# Missing structure
Summarize this.

# No formatting guidance
Tell me about this content.

# Missing content placeholder
Please analyze the document.
```

## Advanced Prompt Techniques

### Chain-of-Thought Prompts

```markdown
You are a critical thinker. When analyzing content, follow this reasoning process:

1. **Comprehension**: First, understand what the content is saying
2. **Analysis**: Break down the arguments and evidence
3. **Evaluation**: Assess the strength and validity
4. **Synthesis**: Connect to broader knowledge
5. **Application**: Consider practical implications

Show your reasoning at each step before providing the final analysis.
```

### Multi-Step Processing

```markdown
You are a content analyst. Process this content in three stages:

**Stage 1: Information Extraction**
- Identify key facts, dates, names, and numbers
- Extract main arguments and supporting evidence

**Stage 2: Analysis and Interpretation**
- Evaluate the strength of arguments
- Identify biases or assumptions
- Connect to relevant context

**Stage 3: Synthesis and Application**
- Summarize key insights
- Suggest practical applications
- Identify areas for further investigation

Present your analysis following this three-stage structure.
```

### Conditional Logic in Prompts

```markdown
You are a versatile content processor. Adapt your analysis based on content type:

If the content appears to be **news**:
- Focus on timeliness and impact
- Identify key stakeholders
- Consider political/social context

If the content appears to be **research**:
- Evaluate methodology rigor
- Assess statistical significance
- Consider field-specific standards

If the content appears to be **opinion/editorial**:
- Identify underlying assumptions
- Evaluate argument structure
- Consider counterarguments

Begin your analysis by identifying the content type and explaining your approach.
```

## Prompt Testing and Iteration

### Testing Methodology

1. **Start Simple**: Begin with basic prompts and gradually add complexity
2. **Use Sample Content**: Test with representative examples of your actual content
3. **Compare Outputs**: Test different prompt variations on the same content
4. **Iterate Based on Results**: Refine prompts based on output quality

### Quality Assessment Checklist

- [ ] Output matches intended purpose
- [ ] Response is appropriately detailed
- [ ] Formatting is consistent and readable
- [ ] Tone matches requirements
- [ ] Key information is preserved
- [ ] Analysis is balanced and objective

## Prompt Versioning

### File Naming Convention

Use descriptive names with version indicators:

```
prompts/
├── news_analysis_v1_system.md
├── news_analysis_v1_user.md
├── news_analysis_v2_system.md  # Improved version
└── news_analysis_v2_user.md
```

### Configuration Management

```ini
# Version 1
[news_v1]
system_prompt_file = prompts/news_analysis_v1_system.md
user_prompt_file = prompts/news_analysis_v1_user.md
enabled = false  # Old version

# Version 2 (current)
[news_v2]
system_prompt_file = prompts/news_analysis_v2_system.md
user_prompt_file = prompts/news_analysis_v2_user.md
enabled = true
```

## Performance Considerations

### Token Usage

- **System Prompts**: Count against token limits; keep concise but effective
- **User Templates**: Include `{content}` placeholder; content will be inserted
- **Total Context**: System + User + Content must fit within model limits

### Optimization Tips

1. **Remove Redundancy**: Eliminate repetitive instructions
2. **Use Clear Structure**: Well-organized prompts often work better
3. **Be Specific**: Vague prompts lead to inconsistent results
4. **Test Different Lengths**: Sometimes shorter prompts work better

## Troubleshooting

### Common Issues

**Inconsistent Output:**
- Review prompt clarity and specificity
- Test with multiple content samples
- Consider adding more explicit instructions

**Formatting Problems:**
- Add explicit formatting requirements
- Provide examples of desired output format
- Use markdown syntax in your prompts

**Content Omission:**
- Ensure `{content}` placeholder is present
- Check that prompts don't override content focus
- Verify token limits aren't being exceeded

### Debugging Commands

```bash
# Test prompt loading
docker exec rumen python -c "
from src.config import get_settings
s = get_settings()
fc = s.folders['news_analysis']
print('System prompt length:', len(fc.load_system_prompt()))
print('User prompt length:', len(fc.load_user_prompt_template()))
"

# Check prompt files exist
docker exec rumen ls -la /app/prompts/
```

## Example Configurations

### News Analysis

```ini
[news_analysis]
system_prompt_file = prompts/news_system.md
user_prompt_file = prompts/news_user.md
provider = gemini
temperature = 0.3
max_tokens = 1024
```

### Research Paper Analysis

```ini
[research_papers]
system_prompt_file = prompts/research_system.md
user_prompt_file = prompts/research_user.md
provider = openai
temperature = 0.5
max_tokens = 2048
```

### Content Summarization

```ini
[content_summary]
system_prompt_file = prompts/summary_system.md
user_prompt_file = prompts/summary_user.md
provider = deepseek
temperature = 0.2
max_tokens = 512
```

## Next Steps

- [Configuration Guide](configuration.md) - Main configuration options
- [Folder Monitoring](folder-monitoring.md) - File processing setup
- [External Volumes](external-volumes.md) - Docker volume integration
- [API Reference](../api/overview.md) - HTTP API documentation