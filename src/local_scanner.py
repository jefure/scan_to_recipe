#  Copyright (C) 2026 Jens Reese
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

import logging
import os

from local_processor import LocalFileProcessor


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
