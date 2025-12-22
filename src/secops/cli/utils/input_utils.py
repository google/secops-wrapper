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
"""Google SecOps CLI input utilities"""

import json
import sys
from pathlib import Path
from typing import Any


def load_json_or_file(value: str) -> Any:
    """Load JSON from string or file path.

    Args:
        value: JSON string or file path

    Returns:
        Parsed JSON object (dict, list, etc.)

    Raises:
        SystemExit: If file not found or JSON parsing fails
    """
    try:
        file_path = Path(value)
        if file_path.exists() and file_path.is_file():
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        print(
            f"Error: Not a valid JSON string or file path: {value}",
            file=sys.stderr,
        )
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)


def load_string_or_file(value: str) -> str:
    """Load string content from direct value or file path.

    Args:
        value: String content or file path

    Returns:
        String content

    Raises:
        SystemExit: If file exists but cannot be read
    """
    try:
        file_path = Path(value)
        if file_path.exists() and file_path.is_file():
            with open(file_path, encoding="utf-8") as f:
                return f.read()
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    return value
