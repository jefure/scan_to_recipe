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
import time
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    from webdav3.client import Client
except ImportError:
    logger.warning("webdav3.client not available, using fallback implementation")
    Client = None


class WebDAVHandler:
    def __init__(self, config: dict, max_retries: int = 3, retry_delay: int = 2):
        self.config = config
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = None
        self._connect()
    
    def _connect(self):
        try:
            if Client is None:
                raise ImportError("webdav3.client not available")
            self.client = Client(self.config)
            logger.info(f"Connected to WebDAV server: {self.config['webdav_hostname']}")
        except Exception as e:
            logger.error(f"Failed to connect to WebDAV server: {e}")
            raise
    
    def _retry_operation(self, operation, *args, **kwargs):
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"WebDAV operation failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"WebDAV operation failed after {self.max_retries} attempts: {e}")
        
        if last_exception:
            raise last_exception
    
    def list_files(self, remote_path: str = "/", filter_extensions: Optional[List[str]] = None) -> List[str]:
        def _list():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                files = self.client.list(remote_path)
                if filter_extensions:
                    files = [
                        f for f in files 
                        if any(f.lower().endswith(ext.lower()) for ext in filter_extensions)
                    ]
                return files
            except Exception as e:
                logger.error(f"Failed to list files in {remote_path}: {e}")
                raise
        
        return self._retry_operation(_list)
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        def _download():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                self.client.download_sync(remote_path, local_path)
                logger.info(f"Downloaded {remote_path} to {local_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to download {remote_path}: {e}")
                raise
        
        return self._retry_operation(_download)
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        def _upload():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                remote_dir = os.path.dirname(remote_path)
                if remote_dir and remote_dir != "/":
                    self.client.mkdir(remote_dir)
                
                self.client.upload_sync(local_path, remote_path)
                logger.info(f"Uploaded {local_path} to {remote_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to upload {local_path}: {e}")
                raise
        
        return self._retry_operation(_upload)
    
    def file_exists(self, remote_path: str) -> bool:
        def _exists():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                return self.client.check(remote_path)
            except Exception as e:
                logger.error(f"Failed to check if {remote_path} exists: {e}")
                return False
        
        return self._retry_operation(_exists)
    
    def get_file_info(self, remote_path: str) -> Optional[dict]:
        def _info():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                return self.client.info(remote_path)
            except Exception as e:
                logger.error(f"Failed to get info for {remote_path}: {e}")
                return None
        
        return self._retry_operation(_info)
    
    def create_directory(self, remote_path: str) -> bool:
        def _mkdir():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                self.client.mkdir(remote_path)
                logger.info(f"Created directory: {remote_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to create directory {remote_path}: {e}")
                raise
        
        return self._retry_operation(_mkdir)
    
    def delete_file(self, remote_path: str) -> bool:
        def _delete():
            try:
                if self.client is None:
                    raise RuntimeError("WebDAV client not initialized")
                self.client.clean(remote_path)
                logger.info(f"Deleted file: {remote_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete {remote_path}: {e}")
                raise
        
        return self._retry_operation(_delete)