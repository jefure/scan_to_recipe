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

import base64
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)
TIMEOUT_IN_SECONDS = 3000.0

try:
    from openai import OpenAI
except ImportError:
    logger.warning("OpenAI library not available")
    OpenAI = None


def get_image_mime_type(image_path: str) -> str:
    extension = image_path.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/jpeg')


def encode_image_to_base64(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            return base64_image
    except Exception as e:
        logger.error(f"Failed to encode image {image_path} to base64: {e}")
        return None


class LLMProcessor:
    def __init__(self, api_key: str, base_url: str = "http://192.168.178.47:8880/v1", model: str = "gpt-4"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            if OpenAI is None:
                raise ImportError("OpenAI library not available")
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"Initialized OpenAI client with base URL: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def analyze_image(self, image_path: str, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        try:
            if self.client is None:
                raise RuntimeError("OpenAI client not initialized")
            
            base64_image = encode_image_to_base64(image_path)
            if not base64_image:
                return None
            
            mime_type = get_image_mime_type(image_path)
            image_url = f"data:{mime_type};base64,{base64_image}"
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                timeout=TIMEOUT_IN_SECONDS
            )
            
            result = response.choices[0].message.content
            logger.info(f"Successfully analyzed image {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze image {image_path}: {e}")
            return None
    
    def analyze_image_with_metadata(self, image_path: str, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        try:
            analysis = self.analyze_image(image_path, prompt)
            if not analysis:
                return None
            
            result = {
                "image_path": image_path,
                "analysis": analysis,
                "model": self.model,
                "prompt": prompt
            }
            
            if metadata:
                result.update(metadata)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze image with metadata {image_path}: {e}")
            return None
    
    def test_connection(self) -> bool:
        try:
            if self.client is None:
                return False
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            
            logger.info("OpenAI connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
