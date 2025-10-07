# Setting Up External Volumes for Rumen

This guide explains how to set up and use external Docker volumes with Rumen for automated processing of content from other systems.

## Overview

Rumen can monitor external Docker volumes for automated processing. This is particularly useful for integrating with other systems that generate content (like web scrapers, data pipelines, etc.) and need automated LLM processing.

## Current External Volume: `pasture_pastures`

The system is pre-configured to monitor an external volume called `pasture_pastures` which is designed for scraped news/web articles organized in a structured format.

### Volume Structure

The expected structure for the `pasture_pastures` volume:
```
/app/pasture_pastures/
├── 2024/
│   ├── 01/          # January
│   │   ├── 15/      # 15th day
│   │   │   ├── feed_name_1/
│   │   │   │   ├── abc123.md
│   │   │   │   └── def456.md
│   │   │   └── feed_name_2/
│   │   │       └── ghi789.md
│   │   └── 20/
│   │       └── another_feed/
│   │           └── jkl012.md
│   └── 02/          # February
│       └── ...
└── 2025/
    └── ...
```

## Setup Steps

### 1. Create the External Volume

```bash
# Create the Docker volume
docker volume create pasture_pastures
```

### 2. Verify Volume Creation

```bash
# List all volumes to confirm creation
docker volume ls

# Inspect the volume details
docker volume inspect pasture_pastures
```

### 3. Start Rumen with the External Volume

```bash
# Start Rumen (this will mount the external volume)
docker compose up -d
```

### 4. Verify Volume Mounting

```bash
# Check if the volume is properly mounted
docker exec rumen ls -la /app/pasture_pastures
```

## Adding Content to the Volume

### Option 1: Direct File Copy (Development)

```bash
# Create test directory structure
mkdir -p test_articles/2024/01/15/news_feed

# Create a test article
cat > test_articles/2024/01/15/news_feed/test_article.md << EOF
# Test News Article

This is a test article about current events. The quick brown fox jumps over the lazy dog. Technology continues to advance at a rapid pace, with new developments in artificial intelligence and machine learning.

Key points:
- AI is transforming industries
- Machine learning models are becoming more sophisticated
- Ethical considerations are important

This content should be automatically processed by Rumen when placed in the pasture_pastures volume.
EOF

# Copy to the volume (if using bind mount for development)
# For production, use the methods below
```

### Option 2: Using Another Container

```bash
# Start a temporary container to add files
docker run -it --rm \
  -v pasture_pastures:/data \
  alpine sh

# Inside the container, create directories and files
mkdir -p /data/2024/01/15/my_feed
echo "# Sample Article" > /data/2024/01/15/my_feed/sample.md
exit
```

### Option 3: Programmatic Access

If you have another service that needs to write to the volume, you can mount it in that service's `docker-compose.yml`:

```yaml
services:
  your_scraper_service:
    volumes:
      - pasture_pastures:/path/to/output
    # ... other configuration
```

## Configuration Details

### Current Pasture Pastures Settings

The `pasture_pastures` folder is configured in `config/config.ini` with:

```ini
[pasture_pastures]
folder_path = /app/pasture_pastures
enabled = true
system_prompt = You are a news and web content analyst. Analyze the provided content and extract key information, summarize main points, and provide context.
user_prompt_template = Please analyze this content: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.4
max_tokens = 2048
output_format = markdown
# output_directory = /app/bolus/pasture_pastures  # Uncomment to use custom output folder
```

### Processing Behavior

- **File Detection**: The system monitors for new `.md` files in the volume
- **Automatic Processing**: Files are processed as soon as they're stable (not being written to)
- **File Cleanup**: Processed files are automatically deleted from the input directory
- **Output**: Results are saved to the configured output directory (default: `/app/bolus`)

## Monitoring and Debugging

### Check Processing Status

```bash
# View Rumen logs
docker compose logs rumen

# Follow logs in real-time
docker compose logs -f rumen
```

### Verify File Processing

```bash
# Check if files are being processed
docker exec rumen ls -la /app/bolus/

# Check for any pasture_pastures specific output
docker exec rumen find /app/bolus -name "*pasture*" -type f
```

### Test with Sample Content

```bash
# Create a quick test file directly in the volume
docker run --rm -v pasture_pastures:/data alpine \
  sh -c 'mkdir -p /data/test && echo "# Test Article" > /data/test/test.md'
```

## Adding More External Volumes

To add additional external volumes:

### 1. Update `docker-compose.yml`

```yaml
services:
  rumen:
    volumes:
      - your_new_volume:/app/your_new_folder

volumes:
  your_new_volume:
    external: true
```

### 2. Update `Dockerfile`

```dockerfile
RUN mkdir -p /app/input /app/bolus /app/prompts /app/your_new_folder
```

### 3. Add Configuration in `config/config.ini`

```ini
[your_new_folder]
folder_path = /app/your_new_folder
enabled = true
system_prompt = Your custom system prompt
user_prompt_template = Your custom user prompt: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.7
max_tokens = 2048
output_format = markdown
```

## Troubleshooting

### Common Issues

1. **Volume not found**: Ensure the volume is created before starting Rumen
2. **Permission denied**: The container runs as a non-root user; ensure proper permissions
3. **Files not processing**: Check that files have `.md` extension and are not empty
4. **Volume not mounting**: Verify the volume name matches in both `docker-compose.yml` and volume creation

### Debug Commands

```bash
# Check if volume exists
docker volume ls | grep pasture_pastures

# Check container mounts
docker inspect rumen | grep -A 10 Mounts

# Check file monitoring status
docker exec rumen ps aux | grep python

# Test file detection manually
docker exec rumen python -c "from src.config import get_settings; s = get_settings(); print([f.name for f in s.folders.values() if f.enabled])"
```

## Best Practices

1. **Organize Content**: Use the year/month/day/feed structure for better organization
2. **Unique Filenames**: Use hash-based filenames to avoid conflicts
3. **Monitor Disk Usage**: External volumes can grow large; monitor storage
4. **Backup Strategy**: Implement backups for important processed content
5. **Error Handling**: Check logs regularly for processing errors

## Next Steps

After setting up the external volume:

1. Integrate your content generation system to write to the volume
2. Monitor the processing through Rumen logs
3. Customize prompts for your specific use case
4. Set up custom output directories if needed
5. Consider adding more external volumes for different content types

For prompt customization, see `prompts/README.md` for details on creating custom prompt files.