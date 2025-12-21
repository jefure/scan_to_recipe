# ScanToCookbook

A Python application that reads images from a WebDAV server, processes them with OpenAI-compatible vision models, and saves the results to another WebDAV folder.

## Features

- **WebDAV Integration**: Connect to source and destination WebDAV servers
- **AI Vision Processing**: Uses OpenAI GPT-4 Vision or compatible models to analyze images
- **Recipe Extraction**: Optimized prompts for extracting recipe information from food images
- **Batch Processing**: Process multiple images in a directory
- **Error Handling**: Robust retry logic and error recovery
- **Flexible Configuration**: Environment-based configuration management
- **Multiple Output Formats**: Saves results as both JSON and text files

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ScanToCookbook
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
```

## Configuration

Edit the `.env` file with your configuration:

### WebDAV Source
```env
WEBDAV_SOURCE_HOST=https://your-source-server.com/webdav
WEBDAV_SOURCE_USERNAME=your-username
WEBDAV_SOURCE_PASSWORD=your-password
```

### WebDAV Destination
```env
WEBDAV_DEST_HOST=https://your-destination-server.com/webdav
WEBDAV_DEST_USERNAME=your-username
WEBDAV_DEST_PASSWORD=your-password
```

### OpenAI/LLM Configuration
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # or custom endpoint
LLM_MODEL=gpt-4-vision-preview
VISION_PROMPT=Analyze this image and extract recipe information...
```

### Optional Settings
```env
MAX_IMAGE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=jpg,jpeg,png
TEMP_DIR=/tmp/scan_to_cookbook
MAX_RETRIES=3
RETRY_DELAY=2
```

## Usage

### WebDAV Mode (Default)

Process all images in a directory:
```bash
python src/main.py --source-dir /recipes --dest-dir /processed
```

### Process Single Image
```bash
python src/main.py --single "/recipes/pasta.jpg" --dest-dir /processed
```

### Test Connections
```bash
python src/main.py --test
```

### Verbose Logging
```bash
python src/main.py --source-dir /recipes --dest-dir /processed --verbose
```

### Local Test Mode

**Single File:**
```bash
python src/main.py --local-test --local-input ./test_image.jpg
```

**Directory with Progress Bar:**
```bash
python src/main.py --local-test --local-input ./recipes --local-output ./processed --progress
```

**Custom Configuration:**
```bash
# Using .env file
python src/main.py --local-test --local-config ./my_local.env --local-input ./images

# Using YAML file
python src/main.py --local-test --local-config ./local.yaml --local-input ./photos
```

**Default Local Configuration:**
```bash
# Uses local.env or local.yaml (or environment variables)
python src/main.py --local-test --local-input ./test_images
```

## Command Line Options

### WebDAV Mode
- `--source-dir`: Source WebDAV directory (default: "/")
- `--dest-dir`: Destination WebDAV directory (default: "/processed")
- `--test`: Test connections only
- `--single`: Process a single image file
- `--verbose, -v`: Enable verbose logging

### Local Test Mode
- `--local-test`: Enable local file processing mode
- `--local-input`: Local input file or directory path
- `--local-output`: Local output directory (default: "./output")
- `--local-config`: Local config file (.env or .yaml)
- `--progress`: Show progress bar for batch operations (default: True)
- `--help`: Show help message

### Mode Selection
The application automatically detects the mode:
- **WebDAV Mode**: Default (no `--local-test` flag)
- **Local Mode**: When `--local-test` flag is used

## Output Files

For each processed image, the application creates:

1. **JSON Analysis**: `{filename}_analysis.json`
   - Contains structured analysis results
   - Includes metadata (timestamp, model, prompt)
   - Machine-readable format

2. **Text Recipe**: `{filename}_recipe.txt`
   - Human-readable recipe text
   - Formatted for easy reading
   - Plain text format

## Logging

The application logs to:
- Console output
- `logs/scan_to_cookbook.log` file

Log levels:
- INFO: General operation information
- WARNING: Non-critical issues
- ERROR: Critical errors
- DEBUG: Detailed debugging information (use `--verbose`)

## Error Handling

- **Connection Failures**: Automatic retry with configurable delays
- **Invalid Images**: Skips corrupted or unsupported files
- **Large Images**: Automatically resizes images over the size limit
- **API Errors**: Handles rate limits and API failures gracefully

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)

## Examples

### Recipe Processing Workflow

1. Upload recipe images to `/incoming` on your WebDAV server
2. Run the processor:
```bash
python src/main.py --source-dir /incoming --dest-dir /recipes
```

3. Results appear in `/recipes` with:
   - `pasta_analysis.json` - Structured data
   - `pasta_recipe.txt` - Human-readable recipe

### Custom Prompt Example

Set a custom vision prompt in `.env`:
```env
VISION_PROMPT=Extract detailed cooking instructions, ingredients with measurements, cooking time, temperature, and serving size from this recipe image.
```

## Configuration

### WebDAV Mode Configuration

Edit the `.env` file for WebDAV settings:
```env
# WebDAV Source
WEBDAV_SOURCE_HOST=https://your-source-server.com/webdav
WEBDAV_SOURCE_USERNAME=your-username
WEBDAV_SOURCE_PASSWORD=your-password

# WebDAV Destination
WEBDAV_DEST_HOST=https://your-destination-server.com/webdav
WEBDAV_DEST_USERNAME=your-username
WEBDAV_DEST_PASSWORD=your-password

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4-vision-preview
```

### Local Mode Configuration

For local testing, copy and configure:
```bash
# Copy template
cp local.env.example local.env
# Edit with your settings
nano local.env
```

Or use YAML format:
```bash
cp local.yaml.example local.yaml
# Edit with your settings
nano local.yaml
```

**Required Local Settings:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `LOCAL_INPUT_DIR`: Directory containing test images
- `LOCAL_OUTPUT_DIR`: Directory for processed results

**Optional Local Settings:**
- `MAX_IMAGE_SIZE`: Maximum image size before resizing (default: 10MB)
- `SUPPORTED_FORMATS`: Image formats to process (default: jpg,jpeg,png)
- `LOG_LEVEL`: Logging level (default: INFO)

## Troubleshooting

### Common Issues

1. **WebDAV Connection Failed**
   - Verify server URL and credentials
   - Check network connectivity
   - Ensure WebDAV is enabled on server

2. **OpenAI API Error**
   - Verify API key is valid
   - Check API quota and rate limits
   - Ensure model supports vision (gpt-4-vision-preview)

3. **Local Mode Issues**
   - Verify OpenAI API key is set in local config
   - Check input directory exists and contains images
   - Ensure output directory is writable

4. **Image Processing Errors**
   - Check image file format is supported
   - Verify image isn't corrupted
   - Check file size limits

### Debug Mode

Run with verbose logging to diagnose issues:
```bash
# WebDAV mode
python src/main.py --test --verbose

# Local mode
python src/main.py --local-test --local-input ./test --verbose
```

## Development

### Project Structure

```
ScanToCookbook/
├── src/
│   ├── __init__.py
│   ├── config.py              # WebDAV configuration management
│   ├── local_config.py         # Local configuration management
│   ├── webdav_handler.py      # WebDAV operations
│   ├── local_processor.py      # Local file processing
│   ├── llm_processor.py       # OpenAI API client
│   ├── image_utils.py         # Image processing utilities
│   └── main.py               # Main application logic
├── logs/                     # Log files
├── temp/                     # Temporary files (WebDAV mode only)
├── output/                   # Local output directory
├── requirements.txt
├── .env.example             # WebDAV configuration template
├── local.env.example        # Local configuration template (.env)
├── local.yaml.example       # Local configuration template (YAML)
└── README.md
```

### Dependencies

- `webdavclient3`: WebDAV client library
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management
- `PyYAML`: YAML configuration file support
- `Pillow`: Image processing
- `requests`: HTTP requests
- `tqdm`: Progress bar for batch operations (included with OpenAI)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]