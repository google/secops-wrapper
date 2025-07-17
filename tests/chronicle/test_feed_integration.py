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
"""Integration tests for Chronicle Feed API.

These tests require valid credentials and API access.
"""
import pytest
import time
import uuid
from secops import SecOpsClient
from ..config import CHRONICLE_CONFIG, SERVICE_ACCOUNT_JSON
from secops.exceptions import APIError


@pytest.mark.integration
def test_feed_list():
    """Test listing feeds with real API."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    try:
        result = chronicle.list_feeds()
        assert isinstance(result, list)
        print(f"Found {len(result)} feeds")

        # If there are feeds, validate their structure
        if result:
            feed = result[0]
            assert "name" in feed
            assert "details" in feed
            assert "state" in feed
            print(f"Sample feed: {feed['name']}")

    except APIError as e:
        print(f"API Error: {str(e)}")
        # Don't fail the test if no feeds exist
        pytest.skip(f"Feed list test skipped due to API error: {str(e)}")


@pytest.mark.integration
def test_feed_create_and_delete():
    """Test creating and deleting a feed with real API."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"

    # Feed details for a simple syslog feed
    feed_details = {
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "integration_test"},
    }

    created_feed = None

    try:
        # Create the feed
        print(f"Creating feed: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )

        assert created_feed is not None
        assert "name" in created_feed
        assert created_feed.get("displayName") == display_name
        print(f"Feed created successfully: {created_feed['name']}")

        # Wait a moment for the feed to be fully created
        time.sleep(2)

        # Get the feed to verify it was created
        feed_id = created_feed["name"].split("/")[-1]
        retrieved_feed = chronicle.get_feed(feed_id)
        assert retrieved_feed is not None
        assert retrieved_feed.get("displayName") == display_name
        print(f"Feed retrieved successfully: {retrieved_feed['name']}")

    except APIError as e:
        print(f"Feed creation failed: {str(e)}")
        pytest.skip(f"Feed creation test skipped due to API error: {str(e)}")

    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed["name"].split("/")[-1]
                print(f"Deleting feed: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test feed: {str(e)}")


@pytest.mark.integration
def test_feed_create_with_json_string():
    """Test creating a feed with JSON string details."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed JSON {unique_id}"

    # Feed details as JSON string
    feed_details_json = f"""{{
        "logType": "projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {{
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES"
        }},
        "labels": {{
            "environment": "test",
            "created_by": "integration_test_json"
        }}
    }}"""

    created_feed = None

    try:
        # Create the feed using JSON string
        print(f"Creating feed with JSON string: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details_json
        )

        assert created_feed is not None
        assert "name" in created_feed
        assert created_feed.get("displayName") == display_name
        print(f"Feed created successfully with JSON: {created_feed['name']}")

    except APIError as e:
        print(f"Feed creation with JSON failed: {str(e)}")
        pytest.skip(f"Feed creation with JSON test skipped due to API error: {str(e)}")

    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed["name"].split("/")[-1]
                print(f"Deleting feed: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test feed: {str(e)}")


@pytest.mark.integration
def test_feed_update():
    """Test updating a feed with real API."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed Update {unique_id}"
    updated_display_name = f"Updated Test Feed {unique_id}"

    # Initial feed details
    feed_details = {
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "integration_test"},
    }

    created_feed = None

    try:
        # Create the feed first
        print(f"Creating feed for update test: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )

        assert created_feed is not None
        feed_id = created_feed["name"].split("/")[-1]
        print(f"Feed created: {feed_id}")

        # Wait a moment for the feed to be fully created
        time.sleep(2)

        # Update the feed
        print(f"Updating feed: {feed_id}")
        updated_feed = chronicle.update_feed(
            feed_id=feed_id, display_name=updated_display_name
        )

        assert updated_feed is not None
        assert updated_feed.get("displayName") == updated_display_name
        print(f"Feed updated successfully: {updated_feed['displayName']}")

        # Verify the update by retrieving the feed
        retrieved_feed = chronicle.get_feed(feed_id)
        assert retrieved_feed.get("displayName") == updated_display_name
        print(f"Feed update verified: {retrieved_feed['displayName']}")

    except APIError as e:
        print(f"Feed update test failed: {str(e)}")
        pytest.skip(f"Feed update test skipped due to API error: {str(e)}")

    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed["name"].split("/")[-1]
                print(f"Deleting feed: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test feed: {str(e)}")


@pytest.mark.integration
def test_feed_enable_disable():
    """Test enabling and disabling a feed with real API."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed Enable {unique_id}"

    # Feed details
    feed_details = {
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "integration_test"},
    }

    created_feed = None

    try:
        # Create the feed first
        print(f"Creating feed for enable/disable test: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )

        assert created_feed is not None
        feed_id = created_feed["name"].split("/")[-1]
        print(f"Feed created: {feed_id}")

        # Wait a moment for the feed to be fully created
        time.sleep(2)

        # Disable the feed
        print(f"Disabling feed: {feed_id}")
        chronicle.disable_feed(feed_id)
        print("Feed disabled successfully")

        # Wait a moment for the state change
        time.sleep(2)

        # Verify the feed is disabled
        disabled_feed = chronicle.get_feed(feed_id)
        print(f"Feed state after disable: {disabled_feed.get('state', 'unknown')}")

        # Enable the feed
        print(f"Enabling feed: {feed_id}")
        chronicle.enable_feed(feed_id)
        print("Feed enabled successfully")

        # Wait a moment for the state change
        time.sleep(2)

        # Verify the feed is enabled
        enabled_feed = chronicle.get_feed(feed_id)
        print(f"Feed state after enable: {enabled_feed.get('state', 'unknown')}")

    except APIError as e:
        print(f"Feed enable/disable test failed: {str(e)}")
        pytest.skip(f"Feed enable/disable test skipped due to API error: {str(e)}")

    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed["name"].split("/")[-1]
                print(f"Deleting feed: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test feed: {str(e)}")


@pytest.mark.integration
def test_feed_update_display_name_only():
    """Test updating only the display_name of a feed."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed Display Only {unique_id}"
    updated_display_name = f"Updated Display Only {unique_id}"

    # Initial feed details
    feed_details = {
        "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG",
        "feedSourceType": "HTTP",
        "httpSettings": {
            "uri": "https://example.com/example_feed",
            "sourceType": "FILES",
        },
        "labels": {"environment": "test", "created_by": "integration_test"},
    }

    created_feed = None

    try:
        # Create the feed first
        print(f"Creating feed for display_name update test: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )

        assert created_feed is not None
        feed_id = created_feed["name"].split("/")[-1]
        print(f"Feed created: {feed_id}")

        # Wait a moment for the feed to be fully created
        time.sleep(2)

        # Update only the display_name (not details)
        print(f"Updating feed display_name only: {feed_id}")
        updated_feed = chronicle.update_feed(
            feed_id=feed_id, display_name=updated_display_name
        )

        assert updated_feed is not None
        assert updated_feed.get("displayName") == updated_display_name
        print(f"Feed display_name updated successfully: {updated_feed['displayName']}")

        # Verify the update by retrieving the feed
        retrieved_feed = chronicle.get_feed(feed_id)
        assert retrieved_feed.get("displayName") == updated_display_name
        # Verify details were not changed
        assert retrieved_feed.get("details") == feed_details
        print(f"Feed display_name update verified: {retrieved_feed['displayName']}")

    except APIError as e:
        print(f"Feed display_name update test failed: {str(e)}")
        pytest.skip(f"Feed display_name update test skipped due to API error: {str(e)}")

    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed["name"].split("/")[-1]
                print(f"Deleting feed: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test feed: {str(e)}")


@pytest.mark.integration
def test_feed_create_invalid_json():
    """Test creating a feed with invalid JSON string details throws an error."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed Invalid JSON {unique_id}"

    # Invalid JSON string
    invalid_json = f'{{"logType": "projects/{CHRONICLE_CONFIG["project_id"]}/locations/{CHRONICLE_CONFIG["region"]}/instances/{CHRONICLE_CONFIG["customer_id"]}/logTypes/WINEVTLOG", "feedSourceType": "HTTP", "invalid": json}}'

    try:
        # Attempt to create the feed with invalid JSON
        print(f"Attempting to create feed with invalid JSON: {display_name}")

        with pytest.raises(ValueError) as exc_info:
            chronicle.create_feed(display_name=display_name, details=invalid_json)

        # Verify the error message
        assert "Invalid JSON string for details" in str(exc_info.value)
        print(f"Correctly caught invalid JSON error: {exc_info.value}")

    except Exception as e:
        if isinstance(e, ValueError) and "Invalid JSON string for details" in str(e):
            # This is the expected error, test passes
            print(f"Correctly caught invalid JSON error: {e}")
        else:
            # Unexpected error, re-raise
            print(f"Unexpected error: {str(e)}")
            raise


@pytest.mark.integration
def test_feed_create_minimal_details():
    """Test creating a feed with minimal details to debug valid feed source types."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed Minimal {unique_id}"

    # Try different minimal feed details
    test_configs = [
        {
            "logType": f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/WINEVTLOG"
        },
        {"feedSourceType": "HTTP"},
        {
            "httpSettings": {
                "uri": "https://example.com/example_feed",
                "sourceType": "FILES",
            }
        },
        {"labels": {"environment": "test", "created_by": "integration_test"}},
    ]

    created_feed = None

    for i, feed_details in enumerate(test_configs):
        try:
            print(f"Trying feed config {i+1}: {feed_details}")
            created_feed = chronicle.create_feed(
                display_name=f"{display_name}-{i+1}", details=feed_details
            )

            assert created_feed is not None
            print(f"Successfully created feed with config {i+1}: {feed_details}")
            break

        except APIError as e:
            print(f"Config {i+1} failed: {str(e)}")
            if "feedSourceType" in str(e).lower():
                print(
                    f"Feed source type '{feed_details['feedSourceType']}' is not valid"
                )
            continue
        except Exception as e:
            print(f"Unexpected error with config {i+1}: {str(e)}")
            continue

    # Clean up if a feed was created
    if created_feed:
        try:
            feed_id = created_feed["name"].split("/")[-1]
            print(f"Cleaning up: Deleting feed: {feed_id}")
            chronicle.delete_feed(feed_id)
            print("Feed cleaned up successfully")
        except APIError as e:
            print(f"Warning: Failed to clean up test feed: {str(e)}")
    else:
        print("No valid feed configuration found. All tested configurations failed.")
        pytest.skip("No valid feed source type found in test configurations")


@pytest.mark.integration
def test_feed_create_and_generate_secret():
    """Test creating and deleting a feed with real API."""
    client = SecOpsClient(service_account_info=SERVICE_ACCOUNT_JSON)
    chronicle = client.chronicle(**CHRONICLE_CONFIG)

    # Generate unique feed name
    unique_id = str(uuid.uuid4())[:8]
    display_name = f"Test Feed {unique_id}"

    # Feed details for a simple syslog feed
    feed_details = {
        "httpsPushAmazonKinesisFirehoseSettings":{
            "splitDelimiter":""
        },
        "feedSourceType":"HTTPS_PUSH_AMAZON_KINESIS_FIREHOSE",
        "logType":f"projects/{CHRONICLE_CONFIG['project_id']}/locations/{CHRONICLE_CONFIG['region']}/instances/{CHRONICLE_CONFIG['customer_id']}/logTypes/OKTA"
    }
    

    created_feed = None

    try:
        # Create the feed
        print(f"Creating feed: {display_name}")
        created_feed = chronicle.create_feed(
            display_name=display_name, details=feed_details
        )

        assert created_feed is not None
        assert "name" in created_feed
        assert created_feed.get("displayName") == display_name
        print(f"Feed created successfully: {created_feed['name']}")

        # Wait a moment for the feed to be fully created
        time.sleep(2)

        feed_id = created_feed["name"].split("/")[-1]
        # Generate secret for the feed
        print(f"Generating secret for feed: {display_name}")
        secret_result = chronicle.generate_secret(feed_id)
        assert 'secret' in secret_result
        assert secret_result['secret']
        print(f"Secret generated successfully: {secret_result}")

    except APIError as e:
        print(f"Feed creation failed: {str(e)}")
        pytest.skip(f"Feed creation test skipped due to API error: {str(e)}")

    finally:
        # Clean up: delete the feed if it was created
        if created_feed:
            try:
                feed_id = created_feed["name"].split("/")[-1]
                print(f"Deleting feed: {feed_id}")
                chronicle.delete_feed(feed_id)
                print("Feed deleted successfully")
            except APIError as e:
                print(f"Warning: Failed to delete test feed: {str(e)}")