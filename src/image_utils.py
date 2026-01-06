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
import logging
import shutil
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ImportError:
    logger.warning("PIL library not available")
    Image = None


class ImageUtils:
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    
    @staticmethod
    def is_valid_image(file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        
        extension = os.path.splitext(file_path)[1].lower()
        if extension not in ImageUtils.SUPPORTED_FORMATS:
            return False
        
        try:
            if Image is None:
                return True
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_image_size(file_path: str) -> Optional[Tuple[int, int]]:
        try:
            if Image is None:
                return None
            with Image.open(file_path) as img:
                return img.size
        except Exception as e:
            logger.error(f"Failed to get image size for {file_path}: {e}")
            return None
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Failed to get file size for {file_path}: {e}")
            return 0
    
    @staticmethod
    def resize_image_if_needed(file_path: str, max_size: int = 10485760, output_path: Optional[str] = None) -> Optional[str]:
        try:
            if Image is None:
                return file_path
            
            file_size = ImageUtils.get_file_size(file_path)
            if file_size <= max_size:
                return file_path
            
            logger.info(f"Resizing image {file_path} (size: {file_size} bytes)")
            
            with Image.open(file_path) as img:
                img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                
                if output_path is None:
                    base, ext = os.path.splitext(file_path)
                    output_path = f"{base}_resized{ext}"
                
                img.save(output_path, optimize=True, quality=85)
                
                new_size = ImageUtils.get_file_size(output_path)
                logger.info(f"Resized image saved to {output_path} (new size: {new_size} bytes)")
                
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to resize image {file_path}: {e}")
            return None
    
    @staticmethod
    def convert_to_jpeg(file_path: str, output_path: Optional[str] = None) -> Optional[str]:
        try:
            if Image is None:
                return file_path
            
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                
                if output_path is None:
                    base, _ = os.path.splitext(file_path)
                    output_path = f"{base}.jpg"
                
                img.save(output_path, 'JPEG', quality=85, optimize=True)
                logger.info(f"Converted image to JPEG: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to convert image {file_path} to JPEG: {e}")
            return None
    
    @staticmethod
    def filter_image_files(file_list: List[str]) -> List[str]:
        return [
            f for f in file_list 
            if os.path.splitext(f)[1].lower() in ImageUtils.SUPPORTED_FORMATS
        ]
    
    @staticmethod
    def create_temp_copy(file_path: str, temp_dir: str) -> Optional[str]:
        try:
            import shutil
            filename = os.path.basename(file_path)
            temp_path = os.path.join(temp_dir, filename)
            
            os.makedirs(temp_dir, exist_ok=True)
            shutil.copy2(file_path, temp_path)
            
            logger.info(f"Created temporary copy: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create temporary copy of {file_path}: {e}")
            return None
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup temporary file {file_path}: {e}")
            return False


def resize_image_in_place(image_path: str) -> bool:
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
