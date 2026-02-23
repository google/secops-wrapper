"""Constants for CLI"""

import os
from pathlib import Path

# Define config directory and file paths
# Global config (user home)
CONFIG_DIR = Path.home() / ".secops"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Local config (current working directory or from env var)
# If SECOPS_LOCAL_CONFIG_DIR is set, use it.
# Otherwise, default to current working directory + .secops
_local_config_env = os.environ.get("SECOPS_LOCAL_CONFIG_DIR")
if _local_config_env:
    LOCAL_CONFIG_DIR = Path(_local_config_env)
else:
    LOCAL_CONFIG_DIR = Path.cwd() / ".secops"

LOCAL_CONFIG_FILE = LOCAL_CONFIG_DIR / "config.json"
