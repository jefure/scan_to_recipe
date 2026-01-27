# ScanToRecipe Docker Setup

This directory contains Docker configuration for running ScanToRecipe in containerized environments.

## Quick Start

### Local Mode (Development)

1. **Create environment file:**
```bash
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key
MODE=local
LOG_LEVEL=INFO
EOF
```

2. **Run with local preset:**
```bash
# Build and run (bind mount your test images)
docker compose -f docker-compose.local.yml up --build
```

3. **Add test images:**
```bash
# Place your test images in the test_images directory
cp your-image.jpg ./test_images/
```

### WebDAV Mode (Production)

1. **Create environment file:**
```bash
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key
MODE=webdav
WEBDAV_SOURCE_HOST=https://your-webdav-server.com/webdav
WEBDAV_SOURCE_USERNAME=your-username
WEBDAV_SOURCE_PASSWORD=your-password
WEBDAV_DEST_HOST=https://your-destination.com/webdav
WEBDAV_DEST_USERNAME=your-username
WEBDAV_DEST_PASSWORD=your-password
EOF
```

2. **Run with WebDAV preset:**
```bash
docker compose -f docker-compose.webdav.yml up --build
```

## Configuration

### Environment Variables

All configuration is done via environment variables:

#### Required
- `OPENAI_API_KEY`: Your OpenAI API key

#### Mode Selection
- `MODE`: `local` or `webdav` (default: webdav)

#### OpenAI Settings
- `OPENAI_BASE_URL`: OpenAI base URL (default: https://api.openai.com/v1)
- `LLM_MODEL`: Model to use (default: gpt-4-vision-preview)

#### WebDAV Settings (webdav mode)
- `WEBDAV_SOURCE_HOST`: Source WebDAV server URL
- `WEBDAV_SOURCE_USERNAME`: Source WebDAV username
- `WEBDAV_SOURCE_PASSWORD`: Source WebDAV password
- `WEBDAV_DEST_HOST`: Destination WebDAV server URL
- `WEBDAV_DEST_USERNAME`: Destination WebDAV username
- `WEBDAV_DEST_PASSWORD`: Destination WebDAV password

#### Local Settings (local mode)
- `LOCAL_INPUT_DIR`: Input directory path (default: /app/input)
- `LOCAL_OUTPUT_DIR`: Output directory path (default: /app/output)

#### Processing Options
- `VISION_PROMPT`: Custom prompt for image analysis
- `MAX_IMAGE_SIZE`: Maximum image size before resizing (default: 10485760)
- `SUPPORTED_FORMATS`: Supported image formats (default: jpg,jpeg,png)
- `TEMP_DIR`: Temporary directory path (default: /app/temp)
- `LOG_LEVEL`: Logging level (default: INFO)

## Volume Mounts

### Local Mode
```yaml
volumes:
  - ./test_images:/app/input:ro     # Your test images
  - ./output:/app/output             # Processed results
  - ./logs:/app/logs               # Application logs
  - ./temp:/app/temp               # Temporary files
```

### WebDAV Mode
```yaml
volumes:
  - ./logs:/app/logs               # Application logs
  - ./temp:/app/temp               # Temporary files
  - ./input:/app/input             # Optional input files
  - ./output:/app/output           # Optional output files
```

## Usage Examples

### Development with Local Mode
```bash
# Set up environment
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "MODE=local" >> .env

# Build and run
docker compose -f docker-compose.local.yml up --build

# Follow logs
docker compose -f docker-compose.local.yml logs -f
```

### Production with WebDAV Mode
```bash
# Production environment
export OPENAI_API_KEY=sk-prod-key
export MODE=webdav
export WEBDAV_SOURCE_HOST=https://prod-server.com/webdav
# ... other config

# Deploy
docker compose up -d --build
```

### Custom Docker Compose
```bash
# Create custom compose file
cat > docker-compose.custom.yml << EOF
services:
  scan-to-recipe:
    image: scan-to-recipe:latest
    environment:
      - MODE=local
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOCAL_INPUT_DIR=/app/my_images
      - LOCAL_OUTPUT_DIR=/app/my_results
    volumes:
      - ./my_images:/app/my_images:ro
      - ./my_results:/app/my_results
      - ./logs:/app/logs
EOF

# Run custom configuration
docker compose -f docker-compose.custom.yml up --build
```

## Building from Source

### Build Image
```bash
# Build locally
docker build -t scan-to-recipe:local .

# Tag for GitHub Container Registry
docker tag scan-to-recipe:local ghcr.io/yourusername/scan-to-recipe:latest
```

### Push to Registry
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Push image
docker push ghcr.io/yourusername/scan-to-recipe:latest
```

## Troubleshooting

### Common Issues

**Permission Denied Errors:**
```bash
# Check volume permissions
ls -la ./test_images ./output

# Fix permissions if needed
sudo chown -R 1000:1000 ./test_images ./output
sudo chmod -R 755 ./test_images ./output
```

**Image Build Failures:**
```bash
# Clean and rebuild
docker compose down --volumes --remove-orphans
docker system prune -f
docker compose build --no-cache
```

**Configuration Issues:**
```bash
# Check environment variables
docker compose config

# Verify config in container
docker compose run --rm scan-to-recipe env | grep OPENAI
```

### Debug Mode
```bash
# Run with verbose logging
docker compose run --rm -e LOG_LEVEL=DEBUG scan-to-recipe --local-test --local-input /app/input --verbose
```

### Interactive Shell
```bash
# Get shell in container for debugging
docker compose run --rm -it scan-to-recipe /bin/sh
```

## Production Considerations

### Security
- Images run as non-root user (UID 1000)
- No sensitive data in Docker image
- Environment variables for secrets (no hardcoded values)
- Read-only mounts for input data where possible

### Performance
- Alpine Linux base for minimal size (~50MB)
- Optimized layer caching
- Minimal runtime dependencies
- Efficient file copying

### Monitoring
- All logs output to stdout/stderr
- Structured logging format
- Easy integration with log aggregators
- Health check capabilities (can be added)

## GitHub Actions CI/CD

The included GitHub Actions workflow automatically:
1. Builds Docker image on push to main/master
2. Builds on tag creation for releases
3. Pushes to GitHub Container Registry
4. Supports semantic versioning

The workflow is triggered by:
- Push to `main` or `master` branches
- Push of tags (e.g., `v1.0.0`)

## Support

For issues with Docker setup:
1. Check the logs: `docker compose logs scan-to-recipe`
2. Verify environment variables: `docker compose config`
3. Ensure proper volume mounts and permissions
4. Test with local mode first to isolate WebDAV issues
