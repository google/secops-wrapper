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
"""Integration tests for Chronicle integration instances.

These tests require valid credentials and API access.
"""

import time
import uuid

import pytest

from secops import SecOpsClient
from secops.exceptions import APIError
from tests.config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON


@pytest.mark.integration
def test_integration_instances_crud_workflow():
    """Test full integration instance lifecycle: create, get, update, delete.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    integration_name = None
    created_instance_id = None

    try:
        print("\n1. Finding a target integration")
        integrations_resp = chronicle.soar.list_integrations(page_size=1)
        integrations = integrations_resp.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available to test instance creation.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")

        print("\n2. Creating integration instance")
        unique_id = str(uuid.uuid4())[:8]
        display_name = f"SDK Test Instance {unique_id}"
        environment = "Default Environment"

        create_resp = chronicle.soar.create_integration_instance(
            integration_name=integration_name,
            environment=environment,
            display_name=display_name,
            description="Created by integration test",
        )

        assert create_resp is not None
        assert "name" in create_resp
        created_instance_id = create_resp["name"].split("/")[-1]
        assert create_resp.get("displayName") == display_name
        print(f"Created instance with ID: {created_instance_id}")

        time.sleep(2)

        print("\n3. Getting instance details")
        get_resp = chronicle.soar.get_integration_instance(
            integration_name=integration_name,
            integration_instance_id=created_instance_id,
        )

        assert get_resp.get("displayName") == display_name
        print(f"Successfully retrieved instance: {display_name}")

        print("\n4. Updating instance")
        updated_name = f"Updated SDK Test Instance {unique_id}"
        update_resp = chronicle.soar.update_integration_instance(
            integration_name=integration_name,
            integration_instance_id=created_instance_id,
            display_name=updated_name,
            description="Updated description",
        )

        assert update_resp.get("displayName") == updated_name
        print(f"Successfully updated instance: {updated_name}")

        print("\n5. Executing integration instance test")
        try:
            test_resp = chronicle.soar.execute_integration_instance_test(
                integration_name=integration_name,
                integration_instance_id=created_instance_id,
            )
            assert "successful" in test_resp
            print(f"Test executed. Successful: {test_resp.get('successful')}")
        except APIError as e:
            print(
                f"Test execution returned API error (expected for some configs): {e}"
            )

        print("\n6. Listing integration instances")
        list_resp = chronicle.soar.list_integration_instances(
            integration_name=integration_name,
            page_size=10,
        )

        instances = list_resp.get("integrationInstances", [])
        found = any(
            i.get("name", "").endswith(created_instance_id) for i in instances
        )
        assert (
            found
        ), f"Created instance {created_instance_id} not found in list."
        print("Successfully found instance in list results")

        print("\n7. Getting affected items")
        affected_resp = chronicle.soar.get_integration_instance_affected_items(
            integration_name=integration_name,
            integration_instance_id=created_instance_id,
        )
        # Assuming response is a dict with affectedPlaybooks or affectedItems
        assert isinstance(affected_resp, dict)
        print("Successfully retrieved affected items")

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        if "400" in error_msg:
            pytest.skip(
                f"Skipping due to 400 Bad Request (integration may require specific parameters): {e}"
            )
        raise
    finally:
        print("\n8. Cleaning up: Deleting integration instance")
        if integration_name and created_instance_id:
            try:
                chronicle.soar.delete_integration_instance(
                    integration_name=integration_name,
                    integration_instance_id=created_instance_id,
                )
                print(f"Successfully deleted instance: {created_instance_id}")
            except Exception as cleanup_error:
                print(
                    f"Warning: Failed to delete test instance: {cleanup_error}"
                )


@pytest.mark.integration
def test_get_default_integration_instance():
    """Test getting default integration instance.

    TODO: Remove 401 skip logic once SOAR IAM role issue is fixed.
    """
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        print("\n1. Finding a target integration")
        integrations_resp = chronicle.soar.list_integrations(page_size=1)
        integrations = integrations_resp.get("integrations", [])
        if not integrations:
            pytest.skip("No integrations available.")

        integration_name = integrations[0]["name"].split("/")[-1]
        print(f"Using integration: {integration_name}")

        print("\n2. Getting default instance")
        default_instance = chronicle.soar.get_default_integration_instance(
            integration_name=integration_name
        )

        assert default_instance is not None
        assert "name" in default_instance.get("instance")
        print(
            "Successfully retrieved default instance: "
            f"{default_instance.get('instance').get('name')}"
        )

    except APIError as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            pytest.skip(f"Skipping due to SOAR IAM issue (401): {e}")
        if "400" in error_msg or "404" in error_msg:
            pytest.skip(
                f"Skipping due to {error_msg} (integration may not have a default instance)"
            )
        raise
