# ScanToCookbook - Docker Quick Start Guide

This is the minimal Docker setup for running ScanToCookbook locally.

## 🚀 Quick Start (Local Mode)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd ScanToCookbook

# Copy test images
cp -r test_images/* ./input/
```

### 2. Configure API Key
```bash
# Create environment file
cat > .env << EOF
OPENAI_API_KEY=your-actual-openai-api-key
MODE=local
LOG_LEVEL=INFO
EOF
```

### 3. Run with Docker
```bash
# Build and run
OPENAI_API_KEY=your-actual-openai-api-key docker-compose -f docker-compose.local.yml up --build

# Or run in background
OPENAI_API_KEY=your-actual-openai-api-key docker-compose -f docker-compose.local.yml up -d --build
```

### 4. Add Your Images
```bash
# Place images in the input directory
cp your-recipe-image.jpg ./input/

# Restart container to process new images
docker-compose -f docker-compose.local.yml restart
```

### 5. Check Results
```bash
# View processed results
ls -la ./output/

# View logs
docker-compose -f docker-compose.local.yml logs -f
```

## 📁 Directory Structure for Docker

```
ScanToCookbook/
├── input/                 # Your test images go here
├── output/                # Processed results appear here
├── logs/                  # Application logs
└── Docker files...
```

## 🔧 Configuration Options

### Environment Variables
Create `.env` file with:
```bash
OPENAI_API_KEY=sk-your-actual-api-key
MODE=local                      # Force local mode
LOG_LEVEL=INFO                  # or DEBUG for verbose
```

### Custom Compose File
```bash
cat > docker-compose.custom.yml << 'EOF'
version: '3.8'

services:
  scantocookbook:
    build: .
    environment:
      - MODE=local
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOCAL_INPUT_DIR=/app/my_images      # Custom input
      - LOCAL_OUTPUT_DIR=/app/my_results    # Custom output
    volumes:
      - ./my_images:/app/my_images:ro
      - ./my_results:/app/my_results
EOF

# Use custom setup
OPENAI_API_KEY=your-key docker-compose -f docker-compose.custom.yml up --build
```

## 🐛 Troubleshooting

### Common Issues

**Permission Denied:**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./input ./output
sudo chmod -R 755 ./input ./output
```

**Build Fails:**
```bash
# Clean and rebuild
docker-compose -f docker-compose.local.yml down -v
docker system prune -f
docker-compose -f docker-compose.local.yml build --no-cache
```

**API Key Issues:**
```bash
# Verify API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Check environment
docker-compose -f docker-compose.local.yml config
```

### Debug Mode
```bash
# Run with debug logging
OPENAI_API_KEY=your-key LOG_LEVEL=DEBUG \
  docker-compose -f docker-compose.local.yml up --build

# Get shell in container
docker-compose -f docker-compose.local.yml exec scantocookbook-local /bin/sh
```

## 🏗️ Build Only

```bash
# Build image without running
docker build -t scantocookbook:local .

# Run container manually
docker run --rm -it \
  -e OPENAI_API_KEY=your-key \
  -e MODE=local \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  scantocookbook:local
```

## 📋 Example Workflow

1. **Setup Phase**
   ```bash
   mkdir -p input output logs
   cp recipe-photos/*.jpg ./input/
   echo "OPENAI_API_KEY=sk-your-key" > .env
   ```

2. **Run Phase**
   ```bash
   docker-compose -f docker-compose.local.yml up --build -d
   ```

3. **Monitor Phase**
   ```bash
   # Check logs
   docker-compose -f docker-compose.local.yml logs -f
   
   # Check progress
   docker-compose -f docker-compose.local.yml ps
   ```

4. **Results Phase**
   ```bash
   # View processed files
   ls -la ./output/
   
   # Download results
   docker cp scantocookbook-local:/app/output ./results
   ```

## 🎯 Next Steps

Once your local Docker setup works:

1. **WebDAV Mode**: Try `docker-compose.yml` for remote server processing
2. **Production**: Add health checks and restart policies  
3. **Monitoring**: Integrate with your logging solution
4. **CI/CD**: Use the included GitHub Actions workflow

## 📚 Full Documentation

For complete documentation, see:
- `README-Docker.md` - Comprehensive Docker guide
- `README.md` - Main application documentation

---

**Quick Test Command:**
```bash
OPENAI_API_KEY=sk-your-key docker-compose -f docker-compose.local.yml up --build
```

That's it! Your Docker containerized ScanToCookbook is ready to process images. 🎉