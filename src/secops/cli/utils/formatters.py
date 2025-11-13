# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Google SecOps CLI formatting utils"""

import json
from typing import Any


def output_formatter(data: Any, output_format: str = "json") -> None:
    """Format and print output data.

    Args:
        data: Data to output
        output_format: Output format (json, text, table)
    """
    if output_format == "json":
        print(json.dumps(data, indent=2, default=str))
    elif output_format == "text":
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(item)
        else:
            print(data)
