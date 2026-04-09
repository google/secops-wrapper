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
"""Integration tests for Chronicle integrations.

These tests require valid credentials and API access.
"""

import time
import uuid

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from tests.config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_integrations_crud_workflow():
    """Test full integration lifecycle: create, get, update, list, delete.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    integration_name = None

    try:
        print("\n1. Creating custom integration")
        unique_id = str(uuid.uuid4())[:8]
        display_name = f"SDK Test Integration {unique_id}"

        create_resp = chronicle.soar.create_integration(
            display_name=display_name,
            staging=False,
            description="Created by integration test",
        )

        assert create_resp is not None
        assert "name" in create_resp
        integration_name = create_resp["name"].split("/")[-1]
        assert create_resp.get("displayName") == display_name
        print(f"Created integration with ID: {integration_name}")

        time.sleep(2)

        print("\n2. Getting integration details")
        get_resp = chronicle.soar.get_integration(
            integration_name=integration_name,
        )

        assert get_resp.get("displayName") == display_name
        print(f"Successfully retrieved integration: {display_name}")

        print("\n3. Updating integration")
        updated_name = f"Updated SDK Test Integration {unique_id}"
        update_resp = chronicle.soar.update_custom_integration(
            integration_name=integration_name,
            display_name=updated_name,
            description="Updated description",
        )

        assert (
            update_resp.get("integration", {}).get("description")
            == "Updated description"
        )
        print(f"Successfully updated integration description")

        print("\n4. Listing integrations")
        list_resp = chronicle.soar.list_integrations(
            page_size=10,
        )

        integrations = list_resp.get("integrations", [])
        found = any(
            i.get("name", "").endswith(integration_name) for i in integrations
        )
        assert (
            found
        ), f"Created integration {integration_name} not found in list."
        print("Successfully found integration in list results")

        print("\n5. Getting affected items")
        affected_resp = chronicle.soar.get_integration_affected_items(
            integration_name=integration_name,
        )
        assert isinstance(affected_resp, dict)
        print("Successfully retrieved affected items")

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        raise
    finally:
        print("\n6. Cleaning up: Deleting integration")
        if integration_name:
            try:
                chronicle.soar.delete_integration(
                    integration_name=integration_name,
                )
                print(f"Successfully deleted integration: {integration_name}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to delete test integration: {cleanup_error}"
                )
