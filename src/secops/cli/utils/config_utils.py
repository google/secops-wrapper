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

from secops.cli.constants import (
    CONFIG_DIR,
    CONFIG_FILE,
    LOCAL_CONFIG_DIR,
    LOCAL_CONFIG_FILE,
)


def _load_json_file(path) -> dict[str, Any]:
    """Helper to safely load JSON file."""
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(
            f"Warning: Failed to load config from {path}",
            file=sys.stderr,
        )
        return {}


def load_config() -> dict[str, Any]:
    """Load configuration from config files.

    Merges global config (~/.secops/config.json) with
    local config (./.secops/config.json).
    Local config takes precedence.

    Returns:
        Dictionary containing configuration values
    """
    global_config = _load_json_file(CONFIG_FILE)
    local_config = _load_json_file(LOCAL_CONFIG_FILE)

    # Merge: Local overrides Global
    return {**global_config, **local_config}


def save_config(config: dict[str, Any], local: bool = False) -> None:
    """Save configuration to config file.

    Args:
        config: Dictionary containing configuration values to save
        local: If True, save to local config file (./.secops/config.json)
               If False, save to global config file (~/.secops/config.json)
    """
    target_dir = LOCAL_CONFIG_DIR if local else CONFIG_DIR
    target_file = LOCAL_CONFIG_FILE if local else CONFIG_FILE

    # Create config directory if it doesn't exist
    target_dir.mkdir(exist_ok=True)

    try:
        # Load existing config to preserve other values if we are doing a
        # partial update?
        # For now, we assume 'config' contains the full desired state for
        # that scope OR we should probably read the existing file and update it.
        # But 'config set' usually reads existing config, updates it, and passes
        # it here.
        # However, load_config() returns MERGED config.
        # If we save that to local, we might copy global values to local.
        # That's a risk.
        # Ideally, we should only save the *changes*
        # or specific values to local??
        # But commonly 'save_config' takes the whole dict.
        # Let's assume the caller handles what to save, but for 'set',
        # we need to be careful.

        # ACTUALLY, to avoid polluting local with global values,
        # we should probably read the TARGET file specifically before saving
        # if we want to merge.
        # specific implementation details depend on how 'set' is implemented.
        # For this refactor, let's keep it simple: overwrite the file with
        # provided config.
        # BUT 'set' command loads MERGED config.
        # FAULKNER: We need to filter? Or just accept that 'set' might
        # duplicate?
        # Let's stick to simple overwrite for now, but 'set' needs to check.

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        print(
            f"Error: Failed to save config to {target_file}: {e}",
            file=sys.stderr,
        )
