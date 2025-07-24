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
"""Pytest configuration and fixtures."""
import os
import sys

import pytest

from secops import SecOpsClient
from tests.config import CHRONICLE_CONFIG

# Add tests directory to Python path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TEST_DIR)


@pytest.fixture
def client():
    """Create a SecOps client for testing."""
    return SecOpsClient()


# CLI Integration test fixture
@pytest.fixture
def cli_env():
    """Set up environment for CLI tests."""
    env = os.environ.copy()
    # Add any environment variables needed for testing
    return env


@pytest.fixture
def common_args():
    """Return common command line arguments for the CLI."""
    return [
        "--customer-id",
        CHRONICLE_CONFIG.get("customer_id", ""),
        "--project-id",
        CHRONICLE_CONFIG.get("project_id", ""),
        "--region",
        CHRONICLE_CONFIG.get("region", "us"),
    ]
