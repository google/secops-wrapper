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
"""Integration tests for Chronicle integration managers.

These tests require valid credentials and API access.
"""

import time
import uuid

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from tests.config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


_MANAGER_SCRIPT = (
    "def helper_function():\n" "    return 'Integration test manager helper'\n"
)


@pytest.mark.integration
def test_integration_managers_workflow():
    """Test full manager lifecycle: template, create, get, list, update, delete.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    integration_name = None
    manager_id = None

    try:
        print("\n1. Finding a target integration")
        integrations_resp = chronicle.soar.list_integrations(page_size=5)
        integrations = integrations_resp.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available to test manager workflow.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")

        print("\n2. Getting manager template")
        template_resp = chronicle.soar.get_integration_manager_template(
            integration_name=integration_name,
        )
        assert template_resp is not None
        print("Retrieved manager template successfully")

        print("\n3. Creating a custom manager")
        unique_id = str(uuid.uuid4())[:8]
        display_name = f"SDK Test Manager {unique_id}"

        create_resp = chronicle.soar.create_integration_manager(
            integration_name=integration_name,
            display_name=display_name,
            script=_MANAGER_SCRIPT,
            description="Temporary manager created by integration test",
        )

        assert create_resp is not None
        assert "name" in create_resp
        manager_id = create_resp["name"].split("/")[-1]
        print(f"Created manager with ID: {manager_id}")

        time.sleep(2)

        print("\n4. Getting manager details")
        get_resp = chronicle.soar.get_integration_manager(
            integration_name=integration_name,
            manager_id=manager_id,
        )
        assert get_resp is not None
        assert "name" in get_resp
        assert get_resp.get("displayName") == display_name
        print(f"Retrieved manager: {get_resp.get('displayName')}")

        print("\n5. Listing managers and verifying created manager appears")
        list_resp = chronicle.soar.list_integration_managers(
            integration_name=integration_name,
        )
        managers = list_resp.get("managers", [])
        assert isinstance(managers, list)
        found = any(m.get("name", "").endswith(manager_id) for m in managers)
        assert found, f"Created manager {manager_id} not found in list."
        print(f"Found manager in list ({len(managers)} total)")

        print("\n5a. Listing managers with as_list=True")
        managers_list = chronicle.soar.list_integration_managers(
            integration_name=integration_name,
            as_list=True,
        )
        assert isinstance(managers_list, list)
        print(f"as_list returned {len(managers_list)} managers")

        print("\n6. Updating the manager")
        updated_description = f"Updated by integration test {unique_id}"
        update_resp = chronicle.soar.update_integration_manager(
            integration_name=integration_name,
            manager_id=manager_id,
            description=updated_description,
        )
        assert update_resp is not None
        assert "name" in update_resp
        print("Updated manager description successfully")

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        raise
    finally:
        print("\n7. Cleaning up")
        if integration_name and manager_id:
            try:
                chronicle.soar.delete_integration_manager(
                    integration_name=integration_name,
                    manager_id=manager_id,
                )
                print(f"Cleaned up manager: {manager_id}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to delete test manager: {cleanup_error}"
                )
