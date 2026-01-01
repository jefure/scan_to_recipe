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
import json
import logging
import argparse
from datetime import datetime
from typing import List, Optional
from file_utils import get_recipe_name

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


class ScanToCookbook:
    def __init__(self, config_path: Optional[str] = None):
        if Config is None:
            raise ImportError("Config module not available")
        if WebDAVHandler is None:
            raise ImportError("WebDAVHandler module not available")
        if LLMProcessor is None:
            raise ImportError("LLMProcessor module not available")
        
        self.config = Config()
        self.source_webdav = WebDAVHandler(
            self.config.get_source_webdav_config(),
            self.config.max_retries,
            self.config.retry_delay
        )
        self.dest_webdav = WebDAVHandler(
            self.config.get_dest_webdav_config(),
            self.config.max_retries,
            self.config.retry_delay
        )
        self.llm_processor = LLMProcessor(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_base_url,
            model=self.config.llm_model
        )
        
        os.makedirs(self.config.temp_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def process_single_image(self, image_path: str, source_dir: str = "/", dest_dir: str = "/") -> bool:
        try:
            logger.info(f"Processing image: {image_path}")
            
            local_image_path = os.path.join(self.config.temp_dir, os.path.basename(image_path))
            
            if not self.source_webdav.download_file(image_path, local_image_path):
                logger.error(f"Failed to download image: {image_path}")
                return False
            
            if ImageUtils and not ImageUtils.is_valid_image(local_image_path):
                logger.error(f"Invalid image file: {local_image_path}")
                return False
            
            file_size = ImageUtils.get_file_size(local_image_path) if ImageUtils else 0
            if file_size > self.config.max_image_size:
                logger.info(f"Image too large ({file_size} bytes), resizing...")
                if ImageUtils:
                    resized_path = ImageUtils.resize_image_if_needed(
                        local_image_path, 
                        self.config.max_image_size
                    )
                    if resized_path:
                        local_image_path = resized_path
                    else:
                        logger.warning(f"Failed to resize image, proceeding with original")
            
            analysis = self.llm_processor.analyze_image(
                local_image_path,
                self.config.system_prompt,
                self.config.vision_prompt
            )
            
            if not analysis:
                logger.error(f"Failed to analyze image: {image_path}")
                return False
            
            result_data = {
                "source_path": image_path,
                "processed_at": datetime.now().isoformat(),
                "analysis": analysis,
                "model": self.config.llm_model,
                "prompt": self.config.vision_prompt
            }
            
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            folder_name = get_recipe_name(analysis)
            dest_dir = os.path.join(dest_dir, folder_name)
            result_filename = f"{base_name}_analysis.json.txt"
            result_path = os.path.join(dest_dir.lstrip('/'), result_filename)
            
            local_result_path = os.path.join(self.config.temp_dir, result_filename)
            with open(local_result_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

            logger.info(f"upload analysis result {analysis} to path {result_path}")
            
            if self.dest_webdav.upload_file(local_result_path, result_path):
                logger.info(f"Successfully uploaded analysis result: {result_path}")
                
                text_filename = f"recipe.json"
                text_path = os.path.join(dest_dir.lstrip('/'), text_filename)
                local_text_path = os.path.join(self.config.temp_dir, text_filename)
                
                with open(local_text_path, 'w', encoding='utf-8') as f:
                    f.write(analysis)
                
                if self.dest_webdav.upload_file(local_text_path, text_path):
                    logger.info(f"Successfully uploaded text result: {text_path}")
                
                self._cleanup_temp_files([local_image_path, local_result_path, local_text_path])
                return True
            else:
                logger.error(f"Failed to upload analysis result: {result_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return False
    
    def process_directory(self, source_dir: str = "/", dest_dir: str = "/", 
                         filter_extensions: Optional[List[str]] = None) -> int:
        try:
            logger.info(f"Processing directory: {source_dir}")
            
            if filter_extensions is None:
                filter_extensions = self.config.supported_formats
            
            image_files = self.source_webdav.list_files(source_dir, filter_extensions)
            
            if not image_files:
                logger.info(f"No image files found in {source_dir}")
                return 0
            
            logger.info(f"Found {len(image_files)} image files to process")
            
            self.dest_webdav.create_directory(dest_dir)
            
            processed_count = 0
            failed_count = 0
            
            for image_file in image_files:
                if image_file == source_dir:
                    continue
                
                full_image_path = os.path.join(source_dir, image_file).replace('\\', '/')
                
                if self.process_single_image(full_image_path, source_dir, dest_dir):
                    processed_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"Processing complete. Success: {processed_count}, Failed: {failed_count}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing directory {source_dir}: {e}")
            return 0
    
    def _cleanup_temp_files(self, file_paths: List[str]):
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")
    
    def test_connections(self) -> bool:
        try:
            logger.info("Testing WebDAV source connection...")
            source_files = self.source_webdav.list_files()
            logger.info(f"Source connection OK. Found {len(source_files)} files in root.")
            
            logger.info("Testing WebDAV destination connection...")
            self.dest_webdav.create_directory("/test")
            logger.info("Destination connection OK.")
            
            logger.info("Testing OpenAI connection...")
            if self.llm_processor.test_connection():
                logger.info("OpenAI connection OK.")
                return True
            else:
                logger.error("OpenAI connection failed.")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


class LocalScanToCookbook:
    def __init__(self, config):
        if LocalFileProcessor is None:
            raise ImportError("LocalFileProcessor module not available")
        
        self.config = config
        self.processor = LocalFileProcessor(config)
        self._setup_logging()
    
    def _setup_logging(self):
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/local_test.log'),
                logging.StreamHandler()
            ]
        )
    
    def run_local(self, input_path: str, output_path: str, show_progress: bool = True) -> int:
        if not os.path.exists(input_path):
            raise ValueError(f"Input path not found: {input_path}")
        
        self.config.ensure_output_directory()
        
        if os.path.isfile(input_path):
            return 1 if self.processor.process_single_image(input_path, output_path) else 0
        elif os.path.isdir(input_path):
            results = self.processor.process_directory(input_path, output_path, show_progress)
            return results['processed']
        else:
            raise ValueError(f"Invalid input path: {input_path}")


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
            app = ScanToCookbook()
            
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