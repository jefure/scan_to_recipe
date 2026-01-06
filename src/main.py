#  Copyright (C) 2025 Jens Reese
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys
import logging
import argparse

from local_scanner import LocalScanToCookbook
from remote_scanner import RemoteScanToCookbook

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
except ImportError:
    Config = None
try:
    from webdav_handler import WebDAVHandler
except ImportError:
    WebDAVHandler = None
try:
    from llm_processor import LLMProcessor
except ImportError:
    LLMProcessor = None
try:
    from image_utils import ImageUtils
except ImportError:
    ImageUtils = None
try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = None
try:
    from local_processor import LocalFileProcessor
except ImportError:
    LocalFileProcessor = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scan_to_cookbook.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    # Check for Docker mode environment variable
    mode = os.getenv('MODE', '').lower()
    is_docker_local = mode == 'local'
    
    parser = argparse.ArgumentParser(description="ScanToCookbook - Process images with AI and store results")
    parser.add_argument("--source-dir", default="/", help="Source WebDAV directory")
    parser.add_argument("--dest-dir", default="/Rezepte", help="Destination WebDAV directory")
    parser.add_argument("--test", action="store_true", help="Test connections only")
    parser.add_argument("--single", help="Process a single image file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    parser.add_argument("--local-test", action="store_true", help="Enable local file processing mode")
    parser.add_argument("--local-input", help="Local input file or directory path")
    parser.add_argument("--local-output", default="./output", help="Local output directory")
    parser.add_argument("--local-config", help="Local config file (.env or .yaml)")
    parser.add_argument("--progress", action="store_true", default=True, help="Show progress bar for batch operations")
    
    args = parser.parse_args()
    
    # Docker local mode defaults
    if is_docker_local:
        args.local_test = True
        if not args.local_input:
            args.local_input = os.getenv('LOCAL_INPUT_DIR', '/app/input')
        if not args.local_output:
            args.local_output = os.getenv('LOCAL_OUTPUT_DIR', '/app/output')
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.local_test or is_docker_local:
            if LocalConfig is None:
                logger.error("LocalConfig module not available")
                return 1
            
            # For Docker mode, try to load from environment variables first
            if is_docker_local:
                try:
                    local_config = LocalConfig()  # Will load from env vars
                except Exception:
                    # Fallback to config file if env loading fails
                    local_config = LocalConfig(args.local_config)
            else:
                local_config = LocalConfig(args.local_config)
            
            app = LocalScanToCookbook(local_config)
            
            input_path = args.local_input or local_config.local_input_dir
            output_path = args.local_output or local_config.local_output_dir
            
            processed = app.run_local(input_path, output_path, args.progress)
            logger.info(f"Processed {processed} images successfully")
            return 0 if processed > 0 else 1
        
        else:
            app = RemoteScanToCookbook()
            
            if args.test:
                success = app.test_connections()
                return 0 if success else 1
            
            if args.single:
                success = app.process_single_image(args.single, args.source_dir, args.dest_dir)
                return 0 if success else 1
            else:
                processed = app.process_directory(args.source_dir, args.dest_dir)
                logger.info(f"Processed {processed} images successfully")
                return 0 if processed > 0 else 1
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())