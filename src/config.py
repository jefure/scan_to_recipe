
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

try:
    import importlib
    dotenv = importlib.import_module('dotenv')
    dotenv.load_dotenv()
except ImportError:
    pass


class Config:
    def __init__(self):
        self.webdav_source_host = self._get_required_env("WEBDAV_SOURCE_HOST")
        self.webdav_source_username = self._get_required_env("WEBDAV_SOURCE_USERNAME")
        self.webdav_source_password = self._get_required_env("WEBDAV_SOURCE_PASSWORD")
        
        self.webdav_dest_host = self._get_required_env("WEBDAV_DEST_HOST")
        self.webdav_dest_username = self._get_required_env("WEBDAV_DEST_USERNAME")
        self.webdav_dest_password = self._get_required_env("WEBDAV_DEST_PASSWORD")
        
        self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4-vision-preview")
        
        self.vision_prompt = os.getenv(
            "VISION_PROMPT", 
            "Analyze this image and extract recipe information including ingredients, instructions, and cooking time."
        )
        
        self.max_image_size = int(os.getenv("MAX_IMAGE_SIZE", "10485760"))  # 10MB
        self.supported_formats = os.getenv("SUPPORTED_FORMATS", "jpg,jpeg,png").split(",")
        self.temp_dir = os.getenv("TEMP_DIR", "/tmp/scan_to_cookbook")
        
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY", "2"))
        
        self._ensure_temp_dir()
    
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _ensure_temp_dir(self):
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_source_webdav_config(self) -> dict:
        return {
            "webdav_hostname": self.webdav_source_host,
            "webdav_login": self.webdav_source_username,
            "webdav_password": self.webdav_source_password,
        }
    
    def get_dest_webdav_config(self) -> dict:
        return {
            "webdav_hostname": self.webdav_dest_host,
            "webdav_login": self.webdav_dest_username,
            "webdav_password": self.webdav_dest_password,
        }
    
    def get_openai_config(self) -> dict:
        return {
            "api_key": self.openai_api_key,
            "base_url": self.openai_base_url,
        }