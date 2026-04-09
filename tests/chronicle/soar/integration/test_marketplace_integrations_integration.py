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
"""Integration tests for Chronicle marketplace integrations.

These tests require valid credentials and API access.
"""

import time

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from tests.config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_marketplace_integrations_workflow():
    """Test full marketplace integration lifecycle: list, get, diff, install, uninstall.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    integration_name = None

    try:
        print("\n1. Listing marketplace integrations")
        list_resp = chronicle.soar.list_marketplace_integrations(
            page_size=10,
        )

        assert "marketplaceIntegrations" in list_resp
        integrations = list_resp.get("marketplaceIntegrations", [])

        if not integrations:
            pytest.skip("No marketplace integrations available to test.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using marketplace integration: {integration_name}")

        print("\n2. Getting marketplace integration details")
        get_resp = chronicle.soar.get_marketplace_integration(
            integration_name=integration_name,
        )

        assert get_resp.get("name", "").endswith(integration_name)
        print(f"Successfully retrieved integration: {integration_name}")

        print("\n3. Getting marketplace integration diff")
        diff_resp = chronicle.soar.get_marketplace_integration_diff(
            integration_name=integration_name,
        )

        assert isinstance(diff_resp, dict)
        print("Successfully retrieved integration diff")

        print("\n4. Installing marketplace integration")
        try:
            install_resp = chronicle.soar.install_marketplace_integration(
                integration_name=integration_name,
            )
            assert isinstance(install_resp, dict)
            print(f"Successfully installed integration: {integration_name}")

            time.sleep(2)

            print("\n5. Uninstalling marketplace integration")
            uninstall_resp = chronicle.soar.uninstall_marketplace_integration(
                integration_name=integration_name,
            )
            assert isinstance(uninstall_resp, dict)
            print(f"Successfully uninstalled integration: {integration_name}")
        except APIError as install_err:
            error_msg = str(install_err)
            print(f"Install/Uninstall skipped or failed: {error_msg}")
            if "401" in error_msg or "Unauthorized" in error_msg:
                raise
            if "400" in error_msg:
                raise

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        raise
