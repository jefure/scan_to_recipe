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
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

yaml = None
try:
    import yaml
except ImportError:
    logger.warning("PyYAML not available, YAML config files not supported")

try:
    from dotenv import load_dotenv
except ImportError:
    logger.warning("python-dotenv not available, .env config files not supported")
    def load_dotenv(file_path=None):
        pass


class LocalConfig:
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = self._load_config(config_file)
        self._validate_config()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        if config_file:
            if config_file.endswith(('.yaml', '.yml')):
                return self._load_yaml_config(config_file)
            elif config_file.endswith('.env'):
                return self._load_env_config(config_file)
        
        for default_file in ['local.yaml', 'local.yml', 'local.env']:
            if os.path.exists(default_file):
                return self._load_config(default_file)
        
        return self._load_env_vars()
    
    def _load_yaml_config(self, file_path: str) -> Dict[str, Any]:
        if yaml is None:
            raise ImportError("PyYAML not available. Install with: pip install PyYAML")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self._flatten_yaml_config(config)
                logger.info(f"Loaded YAML config from {file_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load YAML config from {file_path}: {e}")
            raise
    
    def _load_env_config(self, file_path: str) -> Dict[str, Any]:
        if load_dotenv is None:
            raise ImportError("python-dotenv not available. Install with: pip install python-dotenv")
        
        try:
            load_dotenv(file_path)
            config = self._load_env_vars()
            logger.info(f"Loaded .env config from {file_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load .env config from {file_path}: {e}")
            raise
    
    def _load_env_vars(self) -> Dict[str, Any]:
        return {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'openai_base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            'llm_model': os.getenv('LLM_MODEL', 'gpt-4-vision-preview'),
            'local_input_dir': os.getenv('LOCAL_INPUT_DIR', './test_images'),
            'local_output_dir': os.getenv('LOCAL_OUTPUT_DIR', './output'),
            'vision_prompt': os.getenv(
                'VISION_PROMPT', 
                'Analyze this image and extract recipe information including ingredients, instructions, and cooking time.'
            ),
            'max_image_size': int(os.getenv('MAX_IMAGE_SIZE', '10485760')),
            'supported_formats': os.getenv('SUPPORTED_FORMATS', 'jpg,jpeg,png').split(','),
            'log_level': os.getenv('LOG_LEVEL', 'INFO')
        }
    
    def _flatten_yaml_config(self, config: Dict[str, Any]):
        flattened = {}
        for key, value in config.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flattened[f"{key}_{sub_key}"] = sub_value
            else:
                flattened[key] = value
        
        config.update(flattened)
    
    def _validate_config(self):
        if not self.config.get('openai_api_key'):
            raise ValueError("OPENAI_API_KEY is required for local mode")
        
        if not self.config.get('local_input_dir'):
            raise ValueError("LOCAL_INPUT_DIR is required for local mode")
        
        if not self.config.get('local_output_dir'):
            raise ValueError("LOCAL_OUTPUT_DIR is required for local mode")
        
        supported_formats = self.config.get('supported_formats', [])
        if not supported_formats:
            raise ValueError("SUPPORTED_FORMATS is required for local mode")
        
        max_image_size = self.config.get('max_image_size', 0)
        if max_image_size <= 0:
            raise ValueError("MAX_IMAGE_SIZE must be a positive integer")
    
    @property
    def openai_api_key(self) -> str:
        return self.config['openai_api_key']
    
    @property
    def openai_base_url(self) -> str:
        return self.config['openai_base_url']
    
    @property
    def llm_model(self) -> str:
        return self.config['llm_model']
    
    @property
    def local_input_dir(self) -> str:
        return os.path.expanduser(self.config['local_input_dir'])
    
    @property
    def local_output_dir(self) -> str:
        return os.path.expanduser(self.config['local_output_dir'])
    
    @property
    def vision_prompt(self) -> str:
        return self.config['vision_prompt']
    
    @property
    def max_image_size(self) -> int:
        return self.config['max_image_size']
    
    @property
    def supported_formats(self) -> list:
        return self.config['supported_formats']
    
    @property
    def log_level(self) -> str:
        return self.config['log_level']
    
    def ensure_output_directory(self):
        os.makedirs(self.local_output_dir, exist_ok=True)
    
    def ensure_input_directory(self):
        input_dir = self.local_input_dir
        if not os.path.exists(input_dir):
            logger.info(f"Creating input directory: {input_dir}")
            os.makedirs(input_dir, exist_ok=True)