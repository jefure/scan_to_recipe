import os
import json
import shutil
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

try:
    from local_config import LocalConfig
except ImportError:
    pass

try:
    from llm_processor import LLMProcessor
except ImportError:
    LLMProcessor = None

try:
    from image_utils import ImageUtils
except ImportError:
    ImageUtils = None

try:
    from PIL import Image
except ImportError:
    Image = None

logger = logging.getLogger(__name__)


class LocalFileProcessor:
    def __init__(self, config):
        self.config = config
        if LLMProcessor:
            self.llm_processor = LLMProcessor(
                api_key=config.openai_api_key,
                base_url=config.openai_base_url,
                model=config.llm_model
            )
        else:
            raise ImportError("LLMProcessor not available")
    
    def process_single_image(self, input_path: str, output_path: str) -> bool:
        try:
            logger.info(f"Processing local image: {input_path}")
            
            if not os.path.exists(input_path):
                logger.error(f"Input file not found: {input_path}")
                return False
            
            if not os.access(input_path, os.R_OK):
                logger.error(f"Cannot read input file: {input_path}")
                return False
            
            if ImageUtils and not ImageUtils.is_valid_image(input_path):
                logger.error(f"Invalid image file: {input_path}")
                return False
            
            file_size = ImageUtils.get_file_size(input_path) if ImageUtils else 0
            if file_size > self.config.max_image_size:
                logger.info(f"Image too large ({file_size} bytes), resizing in-place...")
                if not self._resize_image_in_place(input_path):
                    logger.warning(f"Failed to resize image, proceeding with original")
            
            analysis = self.llm_processor.analyze_image(
                input_path,
                self.config.vision_prompt
            )
            
            if not analysis:
                logger.error(f"Failed to analyze image: {input_path}")
                return False
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if not os.access(os.path.dirname(output_path), os.W_OK):
                logger.error(f"Cannot write to output directory: {os.path.dirname(output_path)}")
                return False
            
            result_data = {
                "source_path": input_path,
                "processed_at": datetime.now().isoformat(),
                "analysis": analysis,
                "model": self.config.llm_model,
                "prompt": self.config.vision_prompt
            }
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            json_filename = f"{base_name}_analysis.json"
            json_output_path = os.path.join(output_path, json_filename)
            
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved JSON analysis: {json_output_path}")
            
            text_filename = f"{base_name}_recipe.txt"
            text_output_path = os.path.join(output_path, text_filename)
            
            with open(text_output_path, 'w', encoding='utf-8') as f:
                f.write(f"Recipe Analysis for {os.path.basename(input_path)}\n")
                f.write("=" * 50 + "\n\n")
                f.write(analysis)
            
            logger.info(f"Saved text recipe: {text_output_path}")
            return True
            
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return False
        except OSError as e:
            logger.error(f"Filesystem error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error processing local image {input_path}: {e}")
            return False
    
    def process_directory(self, input_dir: str, output_dir: str, 
                        show_progress: bool = True) -> Dict[str, int]:
        try:
            logger.info(f"Processing local directory: {input_dir}")
            
            if not os.path.exists(input_dir):
                logger.error(f"Input directory not found: {input_dir}")
                return {"processed": 0, "failed": 0}
            
            image_files = self._find_images_recursive(input_dir)
            
            if not image_files:
                logger.info(f"No image files found in {input_dir}")
                return {"processed": 0, "failed": 0}
            
            logger.info(f"Found {len(image_files)} image files to process")
            
            processed_count = 0
            failed_count = 0
            
            if show_progress and tqdm:
                iterator = tqdm(image_files, desc="Processing images", unit="file")
                for image_file in iterator:
                    rel_path = os.path.relpath(image_file, input_dir)
                    output_subdir = os.path.join(output_dir, os.path.dirname(rel_path))
                    
                    if self.process_single_image(image_file, output_subdir):
                        processed_count += 1
                    else:
                        failed_count += 1
            else:
                for image_file in image_files:
                    rel_path = os.path.relpath(image_file, input_dir)
                    output_subdir = os.path.join(output_dir, os.path.dirname(rel_path))
                    
                    if self.process_single_image(image_file, output_subdir):
                        processed_count += 1
                    else:
                        failed_count += 1
            
            logger.info(f"Processing complete. Success: {processed_count}, Failed: {failed_count}")
            return {"processed": processed_count, "failed": failed_count}
            
        except Exception as e:
            logger.error(f"Error processing local directory {input_dir}: {e}")
            return {"processed": 0, "failed": 0}
    
    def _find_images_recursive(self, directory: str) -> List[str]:
        image_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_supported_image(file_path):
                    image_files.append(file_path)
        
        return image_files
    
    def _is_supported_image(self, file_path: str) -> bool:
        extension = os.path.splitext(file_path)[1].lower()
        return extension in [f'.{fmt}' for fmt in self.config.supported_formats]
    
    def _resize_image_in_place(self, image_path: str) -> bool:
        try:
            backup_path = f"{image_path}.backup"
            shutil.copy2(image_path, backup_path)
            
            try:
                if Image:
                    with Image.open(image_path) as img:
                        img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                        img.save(image_path, optimize=True, quality=85)
                
                os.remove(backup_path)
                new_size = ImageUtils.get_file_size(image_path) if ImageUtils else 0
                logger.info(f"Resized image in-place: {image_path} (new size: {new_size} bytes)")
                return True
                
            except Exception as resize_error:
                if os.path.exists(backup_path):
                    shutil.move(backup_path, image_path)
                raise resize_error
                
        except Exception as e:
            logger.error(f"Failed to resize {image_path}: {e}")
            return False