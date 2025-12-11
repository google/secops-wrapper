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
"""Google SecOps CLI config utils"""

import json
import sys
from typing import Any

from secops.cli.constants import CONFIG_DIR, CONFIG_FILE


def load_config() -> dict[str, Any]:
    """Load configuration from config file.

    Returns:
        Dictionary containing configuration values
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(
            f"Warning: Failed to load config from {CONFIG_FILE}",
            file=sys.stderr,
        )
        return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to config file.

    Args:
        config: Dictionary containing configuration values to save
    """
    # Create config directory if it doesn't exist
    CONFIG_DIR.mkdir(exist_ok=True)

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print(
            f"Error: Failed to save config to {CONFIG_FILE}: {e}",
            file=sys.stderr,
        )
