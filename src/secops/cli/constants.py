"""Constants for CLI"""

from pathlib import Path

# Define config directory and file paths
# Global config (user home)
CONFIG_DIR = Path.home() / ".secops"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Local config (current working directory)
LOCAL_CONFIG_DIR = Path.cwd() / ".secops"
LOCAL_CONFIG_FILE = LOCAL_CONFIG_DIR / "config.json"
