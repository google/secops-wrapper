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
"""Tests for authentication functionality."""
import pytest
from secops.auth import SecOpsAuth
from secops.exceptions import AuthenticationError

# Marked tests for integration as ADC and Service Account Information 
# Required for tests

@pytest.mark.integration
def test_default_auth():
    """Test authentication with default credentials."""
    auth = SecOpsAuth()
    assert auth.credentials is not None
    # Some credential types might not expose scopes directly
    assert hasattr(auth.credentials, "requires_scopes")

@pytest.mark.integration
def test_invalid_service_account_path():
    """Test authentication with invalid service account path."""
    with pytest.raises(AuthenticationError):
        SecOpsAuth(service_account_path="invalid/path.json")

@pytest.mark.integration
def test_service_account_info():
    """Test authentication with service account JSON data."""
    from config import SERVICE_ACCOUNT_JSON

    auth = SecOpsAuth(service_account_info=SERVICE_ACCOUNT_JSON)
    assert auth.credentials is not None
    assert (
        auth.credentials.service_account_email == SERVICE_ACCOUNT_JSON["client_email"]
    )
    # For service account credentials, we can check scopes
    assert set(auth.scopes).issubset(set(auth.credentials.scopes))


def test_invalid_service_account_info():
    """Test authentication with invalid service account JSON data."""
    with pytest.raises(AuthenticationError):
        SecOpsAuth(service_account_info={"invalid": "data"})

@pytest.mark.integration
def test_custom_scopes():
    """Test authentication with custom scopes."""
    from config import SERVICE_ACCOUNT_JSON

    custom_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    auth = SecOpsAuth(service_account_info=SERVICE_ACCOUNT_JSON, scopes=custom_scopes)
    assert auth.credentials is not None
    assert set(custom_scopes).issubset(set(auth.credentials.scopes))

@pytest.mark.integration
def test_custom_user_agent():
    """Test that custom user agent is set on the session."""
    from config import SERVICE_ACCOUNT_JSON
    
    auth = SecOpsAuth(service_account_info=SERVICE_ACCOUNT_JSON)
    session = auth.session
    assert session is not None
    assert hasattr(session, "headers")
    assert session.headers.get("User-Agent") == "secops-wrapper-sdk"
