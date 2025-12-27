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

import json
import os
from datetime import datetime
from typing import Any

def get_recipe_name(analysis):
    json_data = json.loads(analysis)

    now = datetime.now()

    return json_data.get('name', f'recipe-{now}')

def save_result(analysis: str, output_path: str) -> str:
    text_filename = "recipe.json"
    text_output_path = os.path.join(output_path, text_filename)

    with open(text_output_path, 'w', encoding='utf-8') as f:
        f.write(analysis)

    return text_output_path

def save_metadata_result(base_name: str, output_path: str, result_data: dict[str, str | Any]):
    json_filename = f"{base_name}_analysis.json"
    json_output_path = os.path.join(output_path, json_filename)

    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
