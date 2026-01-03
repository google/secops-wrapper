# Google SecOps SDK for Python

[![PyPI version](https://img.shields.io/pypi/v/secops.svg)](https://pypi.org/project/secops/)


A Python SDK for interacting with Google Security Operations products, currently supporting Chronicle/SecOps SIEM.
This wraps the API for common use cases, including UDM searches, entity lookups, IoCs, alert management, case management, and detection rule management.

## Prerequisites

Follow these steps to ensure your environment is properly configured:

1. **Configure a Google Cloud Project for Google SecOps**
   - Your Google Cloud project must be linked to your Google SecOps instance.
   - Chronicle API needs to be enabled in your Google Cloud project.
   - The project used for authentication must be the same project that was set up during your SecOps onboarding.
   - For detailed instructions, see [Configure a Google Cloud project for Google SecOps](https://cloud.google.com/chronicle/docs/onboard/configure-cloud-project).

2. **Set up IAM Permissions**
   - The service account or user credentials you use must have appropriate permissions
   - The recommended predefined role is **Chronicle API Admin** (`roles/chronicle.admin`)
   - For more granular access control, you can create custom roles with specific permissions
   - See [Access control using IAM](https://cloud.google.com/chronicle/docs/onboard/configure-feature-access) for detailed permission information

3. **Required Information**
   - Your Chronicle instance ID (customer_id)
   - Your Google Cloud project number (project_id)
   - Your preferred region (e.g., "us", "europe", "asia")


> **Note:** Using a Google Cloud project that is not linked to your SecOps instance will result in authentication failures, even if the service account/user has the correct IAM roles assigned.

## Installation

```bash
pip install secops
```

## Command Line Interface

The SDK also provides a comprehensive command-line interface (CLI) that makes it easy to interact with Google Security Operations products from your terminal:

```bash
# Save your credentials
secops config set --customer-id "your-instance-id" --project-id "your-project-id" --region "us"

# Now use commands without specifying credentials each time
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\""
```

For detailed CLI documentation and examples, see the [CLI Documentation](https://github.com/google/secops-wrapper/blob/main/CLI.md).


## Authentication

The SDK supports two main authentication methods:

### 1. Application Default Credentials (ADC)

The simplest and recommended way to authenticate the SDK. Application Default Credentials provide a consistent authentication method that works across different Google Cloud environments and local development.

There are several ways to use ADC:

#### a. Using `gcloud` CLI (Recommended for Local Development)

```bash
# Login and set up application-default credentials
gcloud auth application-default login
```

Then in your code:
```python
from secops import SecOpsClient

# Initialize with default credentials - no explicit configuration needed
client = SecOpsClient()
```

#### b. Using Environment Variable

Set the environment variable pointing to your service account key:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

Then in your code:
```python
from secops import SecOpsClient

# Initialize with default credentials - will automatically use the credentials file
client = SecOpsClient()
```

#### c. Google Cloud Environment (Automatic)

When running on Google Cloud services (Compute Engine, Cloud Functions, Cloud Run, etc.), ADC works automatically without any configuration:

```python
from secops import SecOpsClient

# Initialize with default credentials - will automatically use the service account 
# assigned to your Google Cloud resource
client = SecOpsClient()
```

ADC will automatically try these authentication methods in order:
1. Environment variable `GOOGLE_APPLICATION_CREDENTIALS`
2. Google Cloud SDK credentials (set by `gcloud auth application-default login`)
3. Google Cloud-provided service account credentials
4. Local service account impersonation credentials

### 2. Service Account Authentication

For more explicit control, you can authenticate using a service account that is created in the Google Cloud project associated with Google SecOps.

**Important Note on Permissions:**
* This service account needs to be granted the appropriate Identity and Access Management (IAM) role to interact with the Google Secops (Chronicle) API. The recommended predefined role is **Chronicle API Admin** (`roles/chronicle.admin`). Alternatively, if your security policies require more granular control, you can create a custom IAM role with the specific permissions needed for the operations you intend to use (e.g., `chronicle.instances.get`, `chronicle.events.create`, `chronicle.rules.list`, etc.). 

Once the service account is properly permissioned, you can authenticate using it in two ways: 

#### a. Using a Service Account JSON File

```python
from secops import SecOpsClient

# Initialize with service account JSON file
client = SecOpsClient(service_account_path="/path/to/service-account.json")
```

#### b. Using Service Account Info Dictionary

If you prefer to manage credentials programmatically without a file, you can create a dictionary containing the service account key's contents.

```python
from secops import SecOpsClient

# Service account details as a dictionary
service_account_info = {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...",
    "client_email": "service-account@project.iam.gserviceaccount.com",
    "client_id": "client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}

# Initialize with service account info
client = SecOpsClient(service_account_info=service_account_info)
```

### Impersonate Service Account

Both [Application Default Credentials](#1-application-default-credentials-adc) and [Service Account Authentication](#2-service-account-authentication) supports impersonating a Service Account leveraging the corresponding `impersonate_service_account` parameter as per the following configuration:

```python
from secops import SecOpsClient

# Initialize with default credentials and impersonate service account
client = SecOpsClient(impersonate_service_account="secops@test-project.iam.gserviceaccount.com")
```

### Retry Configuration

The SDK provides built-in retry functionality that automatically handles transient errors such as rate limiting (429), server errors (500, 502, 503, 504), and network issues. You can customize the retry behavior when initializing the client:

```python
from secops import SecOpsClient
from secops.auth import RetryConfig

# Define retry configurations
retry_config = RetryConfig(
    total=3,                     # Maximum number of retries (default: 5)
    retry_status_codes=[429, 500, 502, 503, 504],  # HTTP status codes to retry
    allowed_methods=["GET", "DELETE"],  # HTTP methods to retry
    backoff_factor=0.5           # Backoff factor (default: 0.3)
)

# Initialize with custom retry config
client = SecOpsClient(retry_config=retry_config)


# Disable retry completely by marking retry config as False
client = SecOpsClient(retry_config=False)
```

## Using the Chronicle API

### Initializing the Chronicle Client

After creating a SecOpsClient, you need to initialize the Chronicle-specific client:

```python
# Initialize Chronicle client
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",  # Your Chronicle instance ID
    project_id="your-project-id",             # Your GCP project ID
    region="us"                               # Chronicle API region 
)
```
[See available regions](https://github.com/google/secops-wrapper/blob/main/regions.md)

#### API Version Control

The SDK supports flexible API version selection:

- **Default Version**: Set `default_api_version` during client initialization (default is `v1alpha`)
- **Per-Method Override**: Many methods accept an `api_version` parameter to override the default for specific calls

**Supported API versions:**
- `v1` - Stable production API
- `v1beta` - Beta API with newer features
- `v1alpha` - Alpha API with experimental features

**Example with per-method version override:**
```python
from secops.chronicle.models import APIVersion

# Client defaults to v1alpha
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us",
    default_api_version="v1alpha"
)

# Use v1 for a specific rule operation
rule = chronicle.get_rule(
    rule_id="ru_12345678-1234-1234-1234-123456789abc",
    api_version=APIVersion.V1  # Override to use v1 for this call
)
```

### Log Ingestion

Ingest raw logs directly into Chronicle:

```python
from datetime import datetime, timezone
import json

# Create a sample log (this is an OKTA log)
current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
okta_log = {
    "actor": {
        "alternateId": "mark.taylor@cymbal-investments.org",
        "displayName": "Mark Taylor",
        "id": "00u4j7xcb5N6zfiRP5d8",
        "type": "User"
    },
    "client": {
        "userAgent": {
            "rawUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "os": "Windows 10",
            "browser": "CHROME"
        },
        "ipAddress": "96.6.127.53",
        "geographicalContext": {
            "city": "New York",
            "state": "New York",
            "country": "United States",
            "postalCode": "10118",
            "geolocation": {"lat": 40.7123, "lon": -74.0068}
        }
    },
    "displayMessage": "Max sign in attempts exceeded",
    "eventType": "user.account.lock",
    "outcome": {"result": "FAILURE", "reason": "LOCKED_OUT"},
    "published": "2025-06-19T21:51:50.116Z",
    "securityContext": {
        "asNumber": 20940,
        "asOrg": "akamai technologies inc.",
        "isp": "akamai international b.v.",
        "domain": "akamaitechnologies.com",
        "isProxy": false
    },
    "severity": "DEBUG",
    "legacyEventType": "core.user_auth.account_locked",
    "uuid": "5b90a94a-d7ba-11ea-834a-85c24a1b2121",
    "version": "0"
    # ... additional OKTA log fields may be included
}

# Ingest a single log using the default forwarder
result = chronicle.ingest_log(
    log_type="OKTA",  # Chronicle log type
    log_message=json.dumps(okta_log)  # JSON string of the log
)

print(f"Operation: {result.get('operation')}")

# Batch ingestion: Ingest multiple logs in a single request
batch_logs = [
    json.dumps({"actor": {"displayName": "User 1"}, "eventType": "user.session.start"}),
    json.dumps({"actor": {"displayName": "User 2"}, "eventType": "user.session.start"}),
    json.dumps({"actor": {"displayName": "User 3"}, "eventType": "user.session.start"})
]

# Ingest multiple logs in a single API call
batch_result = chronicle.ingest_log(
    log_type="OKTA",
    log_message=batch_logs  # List of log message strings
)

print(f"Batch operation: {batch_result.get('operation')}")

# Add custom labels to your logs
labeled_result = chronicle.ingest_log(
    log_type="OKTA",
    log_message=json.dumps(okta_log),
    labels={"environment": "production", "app": "web-portal", "team": "security"}
)
```
The SDK also supports non-JSON log formats. Here's an example with XML for Windows Event logs:

```python
# Create a Windows Event XML log
xml_content = """<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
  <System>
    <Provider Name='Microsoft-Windows-Security-Auditing' Guid='{54849625-5478-4994-A5BA-3E3B0328C30D}'/>
    <EventID>4624</EventID>
    <Version>1</Version>
    <Level>0</Level>
    <Task>12544</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8020000000000000</Keywords>
    <TimeCreated SystemTime='2024-05-10T14:30:00Z'/>
    <EventRecordID>202117513</EventRecordID>
    <Correlation/>
    <Execution ProcessID='656' ThreadID='700'/>
    <Channel>Security</Channel>
    <Computer>WIN-SERVER.xyz.net</Computer>
    <Security/>
  </System>
  <EventData>
    <Data Name='SubjectUserSid'>S-1-0-0</Data>
    <Data Name='SubjectUserName'>-</Data>
    <Data Name='TargetUserName'>svcUser</Data>
    <Data Name='WorkstationName'>CLIENT-PC</Data>
    <Data Name='LogonType'>3</Data>
  </EventData>
</Event>"""

# Ingest the XML log - no json.dumps() needed for XML
result = chronicle.ingest_log(
    log_type="WINEVTLOG_XML",  # Windows Event Log XML format
    log_message=xml_content    # Raw XML content
)

print(f"Operation: {result.get('operation')}")
```
The SDK supports all log types available in Chronicle. You can:

1. View available log types:
```python
# Get all available log types
log_types = chronicle.get_all_log_types()
for lt in log_types[:5]:  # Show first 5
    print(f"{lt.id}: {lt.description}")


# Fetch only first 50 log types (single page)
log_types_page = chronicle.get_all_log_types(page_size=50)

# Fetch specific page using token
log_types_next = chronicle.get_all_log_types(
    page_size=50, 
    page_token="next_page_token"
)
```

2. Search for specific log types:
```python
# Search for log types related to firewalls
firewall_types = chronicle.search_log_types("firewall")
for lt in firewall_types:
    print(f"{lt.id}: {lt.description}")
```

3. Validate log types:
```python
# Check if a log type is valid
if chronicle.is_valid_log_type("OKTA"):
    print("Valid log type")
else:
    print("Invalid log type")
```

4. Use custom forwarders:
```python
# Create or get a custom forwarder
forwarder = chronicle.get_or_create_forwarder(display_name="MyCustomForwarder")
forwarder_id = forwarder["name"].split("/")[-1]

# Use the custom forwarder for log ingestion
result = chronicle.ingest_log(
    log_type="WINDOWS",
    log_message=json.dumps(windows_log),
    forwarder_id=forwarder_id
)
```

### Forwarder Management

Chronicle log forwarders are essential for handling log ingestion with specific configurations. The SDK provides comprehensive methods for creating and managing forwarders:

#### Create a new forwarder

```python
# Create a basic forwarder with just a display name
forwarder = chronicle.create_forwarder(display_name="MyAppForwarder")

# Create a forwarder with optional configuration
forwarder = chronicle.create_forwarder(
    display_name="ProductionForwarder",
    metadata={"labels": {"env": "prod"}},
    upload_compression=True,  # Enable upload compression for efficiency
    enable_server=False  # Server functionality disabled,
    http_settings={
        "port":8080,
        "host":"192.168.0.100",
        "routeSettings":{
            "availableStatusCode": 200,
            "readyStatusCode": 200,
            "unreadyStatusCode": 500
        }
    }
)

print(f"Created forwarder with ID: {forwarder['name'].split('/')[-1]}")
```

#### List all forwarders

Retrieve all forwarders in your Chronicle environment with pagination support:

```python
# Get the default page size (50)
forwarders = chronicle.list_forwarders()

# Get forwarders with custom page size
forwarders = chronicle.list_forwarders(page_size=100)

# Process the forwarders
for forwarder in forwarders.get("forwarders", []):
    forwarder_id = forwarder.get("name", "").split("/")[-1]
    display_name = forwarder.get("displayName", "")
    create_time = forwarder.get("createTime", "")
    print(f"Forwarder ID: {forwarder_id}, Name: {display_name}, Created: {create_time}")
```

#### Get forwarder details

Retrieve details about a specific forwarder using its ID:

```python
# Get a specific forwarder using its ID
forwarder_id = "1234567890"
forwarder = chronicle.get_forwarder(forwarder_id=forwarder_id)

# Access forwarder properties
display_name = forwarder.get("displayName", "")
metadata = forwarder.get("metadata", {})
server_enabled = forwarder.get("enableServer", False)

print(f"Forwarder {display_name} details:")
print(f"  Metadata: {metadata}")
print(f"  Server enabled: {server_enabled}")
```

#### Get or create a forwarder

Retrieve an existing forwarder by display name or create a new one if it doesn't exist:

```python
# Try to find a forwarder with the specified display name
# If not found, create a new one with that display name
forwarder = chronicle.get_or_create_forwarder(display_name="ApplicationLogForwarder")

# Extract the forwarder ID for use in log ingestion
forwarder_id = forwarder["name"].split("/")[-1]
```

#### Update a forwarder

Update an existing forwarder's configuration with specific properties:

```python
# Update a forwarder with new properties
forwarder = chronicle.update_forwarder(
    forwarder_id="1234567890",
    display_name="UpdatedForwarderName",
    metadata={"labels": {"env": "prod"}},
    upload_compression=True
)

# Update specific fields using update mask
forwarder = chronicle.update_forwarder(
    forwarder_id="1234567890",
    display_name="ProdForwarder",
    update_mask=["display_name"]
)

print(f"Updated forwarder: {forwarder['name']}")
```

#### Delete a forwarder

Delete an existing forwarder by its ID:

```python
# Delete a forwarder by ID
chronicle.delete_forwarder(forwarder_id="1234567890")

print("Forwarder deleted successfully")
```

### Log Processing Pipelines

Chronicle log processing pipelines allow you to transform, filter, and enrich log data before it is stored in Chronicle. Common use cases include removing empty key-value pairs, redacting sensitive data, adding ingestion labels, filtering logs by field values, and extracting host information. Pipelines can be associated with log types (with optional collector IDs) and feeds, providing flexible control over your data ingestion workflow.

The SDK provides comprehensive methods for managing pipelines, associating streams, testing configurations, and fetching sample logs.

#### List pipelines

Retrieve all log processing pipelines in your Chronicle instance:

```python
# Get all pipelines
result = chronicle.list_log_processing_pipelines()
pipelines = result.get("logProcessingPipelines", [])

for pipeline in pipelines:
    pipeline_id = pipeline["name"].split("/")[-1]
    print(f"Pipeline: {pipeline['displayName']} (ID: {pipeline_id})")

# List with pagination
result = chronicle.list_log_processing_pipelines(
    page_size=50,
    page_token="next_page_token"
)
```

#### Get pipeline details

Retrieve details about a specific pipeline:

```python
# Get pipeline by ID
pipeline_id = "1234567890"
pipeline = chronicle.get_log_processing_pipeline(pipeline_id)

print(f"Name: {pipeline['displayName']}")
print(f"Description: {pipeline.get('description', 'N/A')}")
print(f"Processors: {len(pipeline.get('processors', []))}")
```

#### Create a pipeline

Create a new log processing pipeline with processors:

```python
# Define pipeline configuration
pipeline_config = {
    "displayName": "My Custom Pipeline",
    "description": "Filters and transforms application logs",
    "processors": [
        {
            "filterProcessor": {
                "include": {
                    "logMatchType": "REGEXP",
                    "logBodies": [".*error.*", ".*warning.*"],
                },
                "errorMode": "IGNORE",
            }
        }
    ],
    "customMetadata": [
        {"key": "environment", "value": "production"},
        {"key": "team", "value": "security"}
    ]
}

# Create the pipeline (server generates ID)
created_pipeline = chronicle.create_log_processing_pipeline(
    pipeline=pipeline_config
)

pipeline_id = created_pipeline["name"].split("/")[-1]
print(f"Created pipeline with ID: {pipeline_id}")
```

#### Update a pipeline

Update an existing pipeline's configuration:

```python
# Get the existing pipeline first
pipeline = chronicle.get_log_processing_pipeline(pipeline_id)

# Update specific fields
updated_config = {
    "name": pipeline["name"], 
    "description": "Updated description",
    "processors": pipeline["processors"]
}

# Patch with update mask
updated_pipeline = chronicle.update_log_processing_pipeline(
    pipeline_id=pipeline_id,
    pipeline=updated_config,
    update_mask="description"
)

print(f"Updated: {updated_pipeline['displayName']}")
```

#### Delete a pipeline

Delete an existing pipeline:

```python
# Delete by ID
chronicle.delete_log_processing_pipeline(pipeline_id)
print("Pipeline deleted successfully")

# Delete with etag for concurrency control
chronicle.delete_log_processing_pipeline(
    pipeline_id=pipeline_id,
    etag="etag_value"
)
```

#### Associate streams with a pipeline

Associate log streams (by log type or feed) with a pipeline:

```python
# Associate by log type
streams = [
    {"logType": "WINEVTLOG"},
    {"logType": "LINUX"}
]

chronicle.associate_streams(
    pipeline_id=pipeline_id,
    streams=streams
)
print("Streams associated successfully")

# Associate by feed ID
feed_streams = [
    {"feed": "feed-uuid-1"},
    {"feed": "feed-uuid-2"}
]

chronicle.associate_streams(
    pipeline_id=pipeline_id,
    streams=feed_streams
)
```

#### Dissociate streams from a pipeline

Remove stream associations from a pipeline:

```python
# Dissociate streams
streams = [{"logType": "WINEVTLOG"}]

chronicle.dissociate_streams(
    pipeline_id=pipeline_id,
    streams=streams
)
print("Streams dissociated successfully")
```

#### Fetch associated pipeline

Find which pipeline is associated with a specific stream:

```python
# Find pipeline for a log type
stream_query = {"logType": "WINEVTLOG"}
associated = chronicle.fetch_associated_pipeline(stream=stream_query)

if associated:
    print(f"Associated pipeline: {associated['name']}")
else:
    print("No pipeline associated with this stream")

# Find pipeline for a feed
feed_query = {"feed": "feed-uuid"}
associated = chronicle.fetch_associated_pipeline(stream=feed_query)
```

#### Fetch sample logs

Retrieve sample logs for specific streams:

```python
# Fetch sample logs for log types
streams = [
    {"logType": "WINEVTLOG"},
    {"logType": "LINUX"}
]

result = chronicle.fetch_sample_logs_by_streams(
    streams=streams,
    sample_logs_count=10
)

for log in result.get("logs", []):
    print(f"Log: {log}")
```

#### Test a pipeline

Test a pipeline configuration against sample logs before deployment:

```python
import base64
from datetime import datetime, timezone

# Define pipeline to test
pipeline_config = {
    "displayName": "Test Pipeline",
    "processors": [
        {
            "filterProcessor": {
                "include": {
                    "logMatchType": "REGEXP",
                    "logBodies": [".*"],
                },
                "errorMode": "IGNORE",
            }
        }
    ]
}

# Create test logs with base64-encoded data
current_time = datetime.now(timezone.utc).isoformat()
log_data = base64.b64encode(b"Sample log entry").decode("utf-8")

input_logs = [
    {
        "data": log_data,
        "logEntryTime": current_time,
        "collectionTime": current_time,
    }
]

# Test the pipeline
result = chronicle.test_pipeline(
    pipeline=pipeline_config,
    input_logs=input_logs
)

print(f"Processed {len(result.get('logs', []))} logs")
for processed_log in result.get("logs", []):
    print(f"Result: {processed_log}")
```

5. Use custom timestamps:
```python
from datetime import datetime, timedelta, timezone

# Define custom timestamps
log_entry_time = datetime.now(timezone.utc) - timedelta(hours=1)
collection_time = datetime.now(timezone.utc)

result = chronicle.ingest_log(
    log_type="OKTA",
    log_message=json.dumps(okta_log),
    log_entry_time=log_entry_time,  # When the log was generated
    collection_time=collection_time  # When the log was collected
)
```

Ingest UDM events directly into Chronicle:

```python
import uuid
from datetime import datetime, timezone

# Generate a unique ID
event_id = str(uuid.uuid4())

# Get current time in ISO 8601 format
current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# Create a UDM event for a network connection
network_event = {
    "metadata": {
        "id": event_id,
        "event_timestamp": current_time,
        "event_type": "NETWORK_CONNECTION",
        "product_name": "My Security Product", 
        "vendor_name": "My Company"
    },
    "principal": {
        "hostname": "workstation-1",
        "ip": "192.168.1.100",
        "port": 12345
    },
    "target": {
        "ip": "203.0.113.10",
        "port": 443
    },
    "network": {
        "application_protocol": "HTTPS",
        "direction": "OUTBOUND"
    }
}

# Ingest a single UDM event
result = chronicle.ingest_udm(udm_events=network_event)
print(f"Ingested event with ID: {event_id}")

# Create a second event
process_event = {
    "metadata": {
        # No ID - one will be auto-generated
        "event_timestamp": current_time,
        "event_type": "PROCESS_LAUNCH",
        "product_name": "My Security Product", 
        "vendor_name": "My Company"
    },
    "principal": {
        "hostname": "workstation-1",
        "process": {
            "command_line": "ping 8.8.8.8",
            "pid": 1234
        },
        "user": {
            "userid": "user123"
        }
    }
}

# Ingest multiple UDM events in a single call
result = chronicle.ingest_udm(udm_events=[network_event, process_event])
print("Multiple events ingested successfully")
```

Import entities into Chronicle:

```python
# Create a sample entity
entity = {
    "metadata": {
        "collected_timestamp": "2025-01-01T00:00:00Z",
        "vendor_name": "TestVendor",
        "product_name": "TestProduct",
        "entity_type": "USER",
    },
    "entity": {
        "user": {
            "userid": "testuser",
        }
    },
}

# Import a single entity
result = chronicle.import_entities(entities=entity, log_type="TEST_LOG_TYPE")
print(f"Imported entity: {result}")

# Import multiple entities
entity2 = {
    "metadata": {
        "collected_timestamp": "2025-01-01T00:00:00Z",
        "vendor_name": "TestVendor",
        "product_name": "TestProduct",
        "entity_type": "ASSET",
    },
    "entity": {
        "asset": {
            "hostname": "testhost",
        }
    },
}
entities = [entity, entity2]
result = chronicle.import_entities(entities=entities, log_type="TEST_LOG_TYPE")
print(f"Imported entities: {result}")
```

### Data Export

> **Note**: The Data Export API features are currently under test and review. We welcome your feedback and encourage you to submit any issues or unexpected behavior to the issue tracker so we can improve this functionality.

You can export Chronicle logs to Google Cloud Storage using the Data Export API:

```python
from datetime import datetime, timedelta, timezone

# Set time range for export
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=1)  # Last 24 hours

# Get available log types for export
available_log_types = chronicle.fetch_available_log_types(
    start_time=start_time,
    end_time=end_time
)

# Print available log types
for log_type in available_log_types["available_log_types"]:
    print(f"{log_type.display_name} ({log_type.log_type.split('/')[-1]})")
    print(f"  Available from {log_type.start_time} to {log_type.end_time}")

# Create a data export for a single log type (legacy method)
export = chronicle.create_data_export(
    gcs_bucket="projects/my-project/buckets/my-export-bucket",
    start_time=start_time,
    end_time=end_time,
    log_type="GCP_DNS"  # Single log type to export
)

# Create a data export for multiple log types
export_multiple = chronicle.create_data_export(
    gcs_bucket="projects/my-project/buckets/my-export-bucket",
    start_time=start_time,
    end_time=end_time,
    log_types=["WINDOWS", "LINUX", "GCP_DNS"]  # Multiple log types to export
)

# Get the export ID
export_id = export["name"].split("/")[-1]
print(f"Created export with ID: {export_id}")
    print(f"Status: {export['data_export_status']['stage']}")

# List recent exports
recent_exports = chronicle.list_data_export(page_size=10)
print(f"Found {len(recent_exports.get('dataExports', []))} recent exports")

# Print details of recent exports
for item in recent_exports.get("dataExports", []):
    item_id = item["name"].split("/")[-1]
    if "dataExportStatus" in item:
        status = item["dataExportStatus"]["stage"]
    else:
        status = item["data_export_status"]["stage"]
    print(f"Export ID: {item_id}, Status: {status}")

# Check export status
status = chronicle.get_data_export(export_id)

# Update an export that is in IN_QUEUE state
if status.get("dataExportStatus", {}).get("stage") == "IN_QUEUE":
    # Update with a new start time
    updated_start = start_time + timedelta(hours=2)
    update_result = chronicle.update_data_export(
        data_export_id=export_id,
        start_time=updated_start,
        # Optionally update other parameters like end_time, gcs_bucket, or log_types
    )
    print("Export updated successfully")

# Cancel an export if needed
if status.get("dataExportStatus", {}).get("stage") in ["IN_QUEUE", "PROCESSING"]:
    cancelled = chronicle.cancel_data_export(export_id)
    print(f"Export has been cancelled. New status: {cancelled['data_export_status']['stage']}")

# Export all log types at once
export_all = chronicle.create_data_export(
    gcs_bucket="projects/my-project/buckets/my-export-bucket",
    start_time=start_time,
    end_time=end_time,
    export_all_logs=True
)

print(f"Created export for all logs. Status: {export_all['data_export_status']['stage']}")
```

The Data Export API supports:
- Exporting one, multiple, or all log types to Google Cloud Storage
- Listing recent exports and filtering results
- Checking export status and progress
- Updating exports that are in the queue
- Cancelling exports in progress
- Fetching available log types for a specific time range

If you encounter any issues with the Data Export functionality, please submit them to our issue tracker with detailed information about the problem and steps to reproduce.

### Basic UDM Search

Search for network connection events:

```python
from datetime import datetime, timedelta, timezone

# Set time range for queries
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=24)  # Last 24 hours

# Perform UDM search
results = chronicle.search_udm(
    query="""
    metadata.event_type = "NETWORK_CONNECTION"
    ip != ""
    """,
    start_time=start_time,
    end_time=end_time,
    max_events=5
)

# Example response:
{
    "events": [
        {
            "name": "projects/my-project/locations/us/instances/my-instance/events/encoded-event-id",
            "udm": {
                "metadata": {
                    "eventTimestamp": "2024-02-09T10:30:00Z",
                    "eventType": "NETWORK_CONNECTION"
                },
                "target": {
                    "ip": ["192.168.1.100"],
                    "port": 443
                },
                "principal": {
                    "hostname": "workstation-1"
                }
            }
        }
    ],
    "total_events": 1,
    "more_data_available": false
}
```

### UDM Search View

Retrieve UDM search results with additional contextual information, including detection data:

```python
from datetime import datetime, timedelta, timezone

# Set time range for queries
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=24)  # Last 24 hours

# Fetch UDM search view results
results = chronicle.fetch_udm_search_view(
    query='metadata.event_type = "NETWORK_CONNECTION"',
    start_time=start_time,
    end_time=end_time,
    max_events=5,  # Limit to 5 events
    max_detections=10,  # Get up to 10 detections
    snapshot_query='feedback_summary.status = "OPEN"',  # Filter for open alerts
    case_insensitive=True  # Case-insensitive search
)
```

> **Note:** The `fetch_udm_search_view` method is synchronous and returns all results at once, not as a streaming response since the parameter passed to endpoint(legacyFetchUDMSearchView) provides synchronous response.

### Fetch UDM Field Values

Search for ingested UDM field values that match a query:

```python
# Search for fields containing "source"
results = chronicle.find_udm_field_values(
    query="source",
    page_size=10
)

# Example response:
{
    "valueMatches": [
        {
            "fieldPath": "metadata.ingestion_labels.key",
            "value": "source",
            "ingestionTime": "2025-08-18T08:00:11.670673Z",
            "matchEnd": 6
        },
        {
            "fieldPath": "additional.fields.key",
            "value": "source",
            "ingestionTime": "2025-02-18T19:45:01.811426Z",
            "matchEnd": 6
        }
    ],
    "fieldMatches": [
        {
            "fieldPath": "about.labels.value"
        },
        {
            "fieldPath": "additional.fields.value.string_value"
        }
    ],
    "fieldMatchRegex": "source"
}
```

### Statistics Queries

Get statistics about network connections grouped by hostname:

```python
stats = chronicle.get_stats(
    query="""metadata.event_type = "NETWORK_CONNECTION"
match:
    target.hostname
outcome:
    $count = count(metadata.id)
order:
    $count desc""",
    start_time=start_time,
    end_time=end_time,
    max_events=1000,
    max_values=10,
    timeout=180
)

# Example response:
{
    "columns": ["hostname", "count"],
    "rows": [
        {"hostname": "server-1", "count": 1500},
        {"hostname": "server-2", "count": 1200}
    ],
    "total_rows": 2
}
```

### CSV Export

Export specific fields to CSV format:

```python
csv_data = chronicle.fetch_udm_search_csv(
    query='metadata.event_type = "NETWORK_CONNECTION"',
    start_time=start_time,
    end_time=end_time,
    fields=["timestamp", "user", "hostname", "process name"]
)

# Example response:
"""
metadata.eventTimestamp,principal.hostname,target.ip,target.port
2024-02-09T10:30:00Z,workstation-1,192.168.1.100,443
2024-02-09T10:31:00Z,workstation-2,192.168.1.101,80
"""
```

### Query Validation

Validate a UDM query before execution:

```python
query = 'target.ip != "" and principal.hostname = "test-host"'
validation = chronicle.validate_query(query)

# Example response:
{
    "isValid": true,
    "queryType": "QUERY_TYPE_UDM_QUERY",
    "suggestedFields": [
        "target.ip",
        "principal.hostname"
    ]
}
```

### Natural Language Search

Search for events using natural language instead of UDM query syntax:

```python
from datetime import datetime, timedelta, timezone

# Set time range for queries
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=24)  # Last 24 hours

# Option 1: Translate natural language to UDM query
udm_query = chronicle.translate_nl_to_udm("show me network connections")
print(f"Translated query: {udm_query}")
# Example output: 'metadata.event_type="NETWORK_CONNECTION"'

# Then run the query manually if needed
results = chronicle.search_udm(
    query=udm_query,
    start_time=start_time,
    end_time=end_time
)

# Option 2: Perform complete search with natural language
results = chronicle.nl_search(
    text="show me failed login attempts",
    start_time=start_time,
    end_time=end_time,
    max_events=100
)

# Example response (same format as search_udm):
{
    "events": [
        {
            "event": {
                "metadata": {
                    "eventTimestamp": "2024-02-09T10:30:00Z",
                    "eventType": "USER_LOGIN"
                },
                "principal": {
                    "user": {
                        "userid": "jdoe"
                    }
                },
                "securityResult": {
                    "action": "BLOCK",
                    "summary": "Failed login attempt"
                }
            }
        }
    ],
    "total_events": 1
}
```

The natural language search feature supports various query patterns:
- "Show me network connections"
- "Find suspicious processes"
- "Show login failures in the last hour"
- "Display connections to IP address 192.168.1.100"

If the natural language cannot be translated to a valid UDM query, an `APIError` will be raised with a message indicating that no valid query could be generated.

### Entity Summary

Get detailed information about specific entities like IP addresses, domains, or file hashes. The function automatically detects the entity type based on the provided value and fetches a comprehensive summary including related entities, alerts, timeline, prevalence, and more.

```python
# IP address summary
ip_summary = chronicle.summarize_entity(
    value="8.8.8.8",
    start_time=start_time,
    end_time=end_time
)

# Domain summary
domain_summary = chronicle.summarize_entity(
    value="google.com",
    start_time=start_time,
    end_time=end_time
)

# File hash summary (SHA256)
file_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" 
file_summary = chronicle.summarize_entity(
    value=file_hash,
    start_time=start_time,
    end_time=end_time
)

# Optionally hint the preferred type if auto-detection might be ambiguous
user_summary = chronicle.summarize_entity(
    value="jdoe",
    start_time=start_time,
    end_time=end_time,
    preferred_entity_type="USER"
)


# Example response structure (EntitySummary object):
# Access attributes like: ip_summary.primary_entity, ip_summary.related_entities,
# ip_summary.alert_counts, ip_summary.timeline, ip_summary.prevalence, etc.

# Example fields within the EntitySummary object:
# primary_entity: {
#     "name": "entities/...",
#     "metadata": {
#         "entityType": "ASSET",  # Or FILE, DOMAIN_NAME, USER, etc.
#         "interval": { "startTime": "...", "endTime": "..." }
#     },
#     "metric": { "firstSeen": "...", "lastSeen": "..." },
#     "entity": {  # Contains specific details like 'asset', 'file', 'domain'
#         "asset": { "ip": ["8.8.8.8"] }
#     }
# }
# related_entities: [ { ... similar to primary_entity ... } ]
# alert_counts: [ { "rule": "Rule Name", "count": 5 } ]
# timeline: { "buckets": [ { "alertCount": 1, "eventCount": 10 } ], "bucketSize": "3600s" }
# prevalence: [ { "prevalenceTime": "...", "count": 100 } ]
# file_metadata_and_properties: {  # Only for FILE entities
#     "metadata": [ { "key": "...", "value": "..." } ],
#     "properties": [ { "title": "...", "properties": [ { "key": "...", "value": "..." } ] } ]
# }
```

### List IoCs (Indicators of Compromise)

Retrieve IoC matches against ingested events:

```python
iocs = chronicle.list_iocs(
    start_time=start_time,
    end_time=end_time,
    max_matches=1000,
    add_mandiant_attributes=True,
    prioritized_only=False
)

# Process the results
for ioc in iocs['matches']:
    ioc_type = next(iter(ioc['artifactIndicator'].keys()))
    ioc_value = next(iter(ioc['artifactIndicator'].values()))
    print(f"IoC Type: {ioc_type}, Value: {ioc_value}")
    print(f"Sources: {', '.join(ioc['sources'])}")
```

The IoC response includes:
- The indicator itself (domain, IP, hash, etc.)
- Sources and categories
- Affected assets in your environment
- First and last seen timestamps
- Confidence scores and severity ratings
- Associated threat actors and malware families (with Mandiant attributes)

### Alerts and Case Management

Retrieve alerts and their associated cases:

```python
# Get non-closed alerts
alerts = chronicle.get_alerts(
    start_time=start_time,
    end_time=end_time,
    snapshot_query='feedback_summary.status != "CLOSED"',
    max_alerts=100
)

# Get alerts from the response
alert_list = alerts.get('alerts', {}).get('alerts', [])

# Extract case IDs from alerts
case_ids = {alert.get('caseName') for alert in alert_list if alert.get('caseName')}

# Get case details using the batch API
if case_ids:
    cases = chronicle.get_cases(list(case_ids))
    
    # Process cases
    for case in cases.cases:
        print(f"Case: {case.display_name}")
        print(f"Priority: {case.priority}")
        print(f"Status: {case.status}")
        print(f"Stage: {case.stage}")
        
        # Access SOAR platform information if available
        if case.soar_platform_info:
            print(f"SOAR Case ID: {case.soar_platform_info.case_id}")
            print(f"SOAR Platform: {case.soar_platform_info.platform_type}")
```

The alerts response includes:
- Progress status and completion status
- Alert counts (baseline and filtered)
- Alert details (rule information, detection details, etc.)
- Case associations

You can filter alerts using the snapshot query parameter with fields like:
- `detection.rule_name`
- `detection.alert_state`
- `feedback_summary.verdict`
- `feedback_summary.priority`
- `feedback_summary.status`

### Case Management Helpers

The `CaseList` class provides helper methods for working with cases:

```python
# Get details for specific cases (uses the batch API)
cases = chronicle.get_cases(["case-id-1", "case-id-2"])

# Filter cases by priority
high_priority = cases.filter_by_priority("PRIORITY_HIGH")

# Filter cases by status
open_cases = cases.filter_by_status("STATUS_OPEN")

# Look up a specific case
case = cases.get_case("case-id-1")
```

> **Note**: The case management API uses the `legacy:legacyBatchGetCases` endpoint to retrieve multiple cases in a single request. You can retrieve up to 1000 cases in a single batch.

### Generating UDM Key/Value Mapping
Chronicle provides a feature to generate UDM key-value mapping for a given row log.

```python
mapping = chronicle.generate_udm_key_value_mappings(
    log_format="JSON",
    log='{"events":[{"id":"123","user":"test_user","source_ip":"192.168.1.10"}]}',
    use_array_bracket_notation=True,
    compress_array_fields=False,
)

print(f"Generated UDM key/value mapping: {mapping}")
```

```python
# Generate UDM key-value mapping
udm_mapping = chronicle.generate_udm_mapping(log_type="WINDOWS_AD")
print(udm_mapping)
```

## Parser Management

Chronicle parsers are used to process and normalize raw log data into Chronicle's Unified Data Model (UDM) format. Parsers transform various log formats (JSON, XML, CEF, etc.) into a standardized structure that enables consistent querying and analysis across different data sources.

The SDK provides comprehensive support for managing Chronicle parsers:

### Creating Parsers

Create new parser:

```python
parser_text = """
filter {
    mutate {
      replace => {
        "event1.idm.read_only_udm.metadata.event_type" => "GENERIC_EVENT"
        "event1.idm.read_only_udm.metadata.vendor_name" =>  "ACME Labs"
      }
    }
    grok {
      match => {
        "message" => ["^(?P<_firstWord>[^\s]+)\s.*$"]
      }
      on_error => "_grok_message_failed"
    }
    if ![_grok_message_failed] {
      mutate {
        replace => {
          "event1.idm.read_only_udm.metadata.description" => "%{_firstWord}"
        }
      }
    }
    mutate {
      merge => {
        "@output" => "event1"
      }
    }
}
"""

log_type = "WINDOWS_AD"

# Create the parser
parser = chronicle.create_parser(
    log_type=log_type, 
    parser_code=parser_text,
    validated_on_empty_logs=True  # Whether to validate parser on empty logs
)
parser_id = parser.get("name", "").split("/")[-1]
print(f"Parser ID: {parser_id}")
```

### Managing Parsers

Retrieve, list, copy, activate/deactivate, and delete parsers:

```python
# List all parsers (returns complete list)
parsers = chronicle.list_parsers()
for parser in parsers:
    parser_id = parser.get("name", "").split("/")[-1]
    state = parser.get("state")
    print(f"Parser ID: {parser_id}, State: {state}")

# Manual pagination: get raw API response with nextPageToken
response = chronicle.list_parsers(page_size=50)
parsers = response.get("parsers", [])
next_token = response.get("nextPageToken")
# Use next_token for subsequent calls:
# response = chronicle.list_parsers(page_size=50, page_token=next_token)

log_type = "WINDOWS_AD"
    
# Get specific parser
parser = chronicle.get_parser(log_type=log_type, id=parser_id)
print(f"Parser content: {parser.get('text')}")

# Activate/Deactivate parser
chronicle.activate_parser(log_type=log_type, id=parser_id)
chronicle.deactivate_parser(log_type=log_type, id=parser_id)

# Copy an existing parser as a starting point
copied_parser = chronicle.copy_parser(log_type=log_type, id="pa_existing_parser")

# Delete parser
chronicle.delete_parser(log_type=log_type, id=parser_id)

# Force delete an active parser
chronicle.delete_parser(log_type=log_type, id=parser_id, force=True)

# Activate a release candidate parser
chronicle.activate_release_candidate_parser(log_type=log_type, id="pa_release_candidate")
```

> **Note:** Parsers work in conjunction with log ingestion. When you ingest logs using `chronicle.ingest_log()`, Chronicle automatically applies the appropriate parser based on the log type to transform your raw logs into UDM format. If you're working with custom log formats, you may need to create or configure custom parsers first.

### Run Parser against sample logs

Run the parser on one or more sample logs:

```python
# Sample parser code that extracts fields from logs
parser_text = """
filter {
    mutate {
      replace => {
        "event1.idm.read_only_udm.metadata.event_type" => "GENERIC_EVENT"
        "event1.idm.read_only_udm.metadata.vendor_name" =>  "ACME Labs"
      }
    }
    grok {
      match => {
        "message" => ["^(?P<_firstWord>[^\s]+)\s.*$"]
      }
      on_error => "_grok_message_failed"
    }
    if ![_grok_message_failed] {
      mutate {
        replace => {
          "event1.idm.read_only_udm.metadata.description" => "%{_firstWord}"
        }
      }
    }
    mutate {
      merge => {
        "@output" => "event1"
      }
    }
}
"""

log_type = "WINDOWS_AD"

# Sample log entries to test
sample_logs = [
    '{"message": "ERROR: Failed authentication attempt"}',
    '{"message": "WARNING: Suspicious activity detected"}',
    '{"message": "INFO: User logged in successfully"}'
]

# Run parser evaluation
result = chronicle.run_parser(
    log_type=log_type, 
    parser_code=parser_text,
    parser_extension_code=None,  # Optional parser extension
    logs=sample_logs,
    statedump_allowed=False  # Enable if using statedump filters
)

# Check the results
if "runParserResults" in result:
    for i, parser_result in enumerate(result["runParserResults"]):
        print(f"\nLog {i+1} parsing result:")
        if "parsedEvents" in parser_result:
            print(f"  Parsed events: {parser_result['parsedEvents']}")
        if "errors" in parser_result:
            print(f"  Errors: {parser_result['errors']}")
```

The `run_parser` function includes comprehensive validation:
- Validates log type and parser code are provided
- Ensures logs are provided as a list of strings
- Enforces size limits (10MB per log, 50MB total, max 1000 logs)
- Provides detailed error messages for different failure scenarios

### Complete Parser Workflow Example

Here's a complete example that demonstrates retrieving a parser, running it against a log, and ingesting the parsed UDM event:

```python
# Step 1: List and retrieve an OKTA parser
parsers = chronicle.list_parsers(log_type="OKTA")
parser_id = parsers[0]["name"].split("/")[-1]
parser_details = chronicle.get_parser(log_type="OKTA", id=parser_id)

# Extract and decode parser code
import base64
parser_code = base64.b64decode(parser_details["cbn"]).decode('utf-8')

# Step 2: Run the parser against a sample log
okta_log = {
    "actor": {"alternateId": "user@example.com", "displayName": "Test User"},
    "eventType": "user.account.lock",
    "outcome": {"result": "FAILURE", "reason": "LOCKED_OUT"},
    "published": "2025-06-19T21:51:50.116Z"
    # ... other OKTA log fields
}

result = chronicle.run_parser(
    log_type="OKTA",
    parser_code=parser_code,
    parser_extension_code=None,
    logs=[json.dumps(okta_log)]
)

# Step 3: Extract and ingest the parsed UDM event
if result["runParserResults"][0]["parsedEvents"]:
    # parsedEvents is a dict with 'events' key containing the actual events list
    parsed_events_data = result["runParserResults"][0]["parsedEvents"]
    if isinstance(parsed_events_data, dict) and "events" in parsed_events_data:
        events = parsed_events_data["events"]
        if events and len(events) > 0:
            # Extract the first event
            if "event" in events[0]:
                udm_event = events[0]["event"]
            else:
                udm_event = events[0]
            
            # Ingest the parsed UDM event back into Chronicle
            ingest_result = chronicle.ingest_udm(udm_events=udm_event)
            print(f"UDM event ingested: {ingest_result}")
```

This workflow is useful for:
- Testing parsers before deployment
- Understanding how logs are transformed to UDM format
- Re-processing logs with updated parsers
- Debugging parsing issues

## Parser Extension

Parser extensions provide a flexible way to extend the capabilities of existing default (or custom) parsers without replacing them. The extensions let you customize the parser pipeline by adding new parsing logic, extracting and transforming fields, and updating or removing UDM field mappings.

The SDK provides comprehensive support for managing Chronicle parser extensions:

### List Parser Extensions

List parser extensions for a log type:

```python
log_type = "OKTA"

extensions = chronicle.list_parser_extensions(log_type)
print(f"Found {len(extensions["parserExtensions"])} parser extensions for log type: {log_type}")
```

### Create a new parser extension

Create new parser extension using either CBN snippet, field extractor or dynamic parsing:

```python
log_type = "OKTA"
field_extractor = {
    "extractors": [
        {
            "preconditionPath": "severity",
            "preconditionValue": "Info",
            "preconditionOp": "EQUALS",
            "fieldPath": "displayMessage",
            "destinationPath": "udm.metadata.description",
        }
    ],
    "logFormat": "JSON",
    "appendRepeatedFields": True,
}

chronicle.create_parser_extension(log_type, field_extractor=field_extractor)
```

### Get parser extension

Get parser extension details:

```python
log_type = "OKTA"
extension_id = "1234567890"

extension = chronicle.get_parser_extension(log_type, extension_id)

print(extension)
```

### Activate Parser Extension

Activate parser extension:

```python
log_type = "OKTA"
extension_id = "1234567890"

chronicle.activate_parser_extension(log_type, extension_id)
```

### Delete Parser Extension

Delete parser extension:

```python
log_type = "OKTA"
extension_id = "1234567890"

chronicle.delete_parser_extension(log_type, extension_id)
```

## Watchlist Management

### Creating a Watchlist

Create a new watchlist:

```python
watchlist = chronicle.create_watchlist(
    name="my_watchlist",
    display_name="my_watchlist",
    multiplying_factor=1.5,
    description="My new watchlist"
)
```

### Updating a Watchlist

Update a watchlist by ID:

```python
updated_watchlist = chronicle.update_watchlist(
    watchlist_id="abc-123-def",
    display_name="Updated Watchlist Name",
    description="Updated description",
    multiplying_factor=2.0,
    entity_population_mechanism={"manual": {}},
    watchlist_user_preferences={"pinned": True}
)
```

### Deleting a Watchlist

Delete a watchlist by ID:

```python
chronicle.delete_watchlist("acb-123-def", force=True)
```

### Getting a Watchlist

Get a watchlist by ID:

```python
watchlist = chronicle.get_watchlist("acb-123-def")
```

### List all Watchlists

List all watchlists:

```python
watchlists = chronicle.list_watchlists()
```

## Rule Management

The SDK provides comprehensive support for managing Chronicle detection rules:

### Creating Rules

Create new detection rules using YARA-L 2.0 syntax:

```python
rule_text = """
rule simple_network_rule {
    meta:
        description = "Example rule to detect network connections"
        author = "SecOps SDK Example"
        severity = "Medium"
        priority = "Medium"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
        $e.principal.hostname != ""
    condition:
        $e
}
"""

# Create the rule
rule = chronicle.create_rule(rule_text)
rule_id = rule.get("name", "").split("/")[-1]
print(f"Rule ID: {rule_id}")
```

### Managing Rules

Retrieve, list, update, enable/disable, and delete rules:

```python
# List all rules
rules = chronicle.list_rules()
for rule in rules.get("rules", []):
    rule_id = rule.get("name", "").split("/")[-1]
    enabled = rule.get("deployment", {}).get("enabled", False)
    print(f"Rule ID: {rule_id}, Enabled: {enabled}")

# List paginated rules and `REVISION_METADATA_ONLY` view
rules = chronicle.list_rules(view="REVISION_METADATA_ONLY",page_size=50)
print(f"Fetched {len(rules.get("rules"))} rules")

# Get specific rule
rule = chronicle.get_rule(rule_id)
print(f"Rule content: {rule.get('text')}")

# Update rule
updated_rule = chronicle.update_rule(rule_id, updated_rule_text)

# Enable/disable rule
deployment = chronicle.enable_rule(rule_id, enabled=True)  # Enable
deployment = chronicle.enable_rule(rule_id, enabled=False) # Disable

# Delete rule
chronicle.delete_rule(rule_id)
```

### Rule Deployment

Manage a rule's deployment (enabled/alerting/archive state and run frequency):

```python
# Get current deployment for a rule
deployment = chronicle.get_rule_deployment(rule_id)

# List deployments (paginated)
page = chronicle.list_rule_deployments(page_size=10)

# List deployments with filter
filtered = chronicle.list_rule_deployments(filter_query="enabled=true")

# Update deployment fields (partial updates supported)
chronicle.update_rule_deployment(
    rule_id=rule_id,
    enabled=True,          # continuously execute
    alerting=False,        # detections do not generate alerts
    run_frequency="LIVE" # LIVE | HOURLY | DAILY
)

# Archive a rule (must set enabled to False when archived=True)
chronicle.update_rule_deployment(
    rule_id=rule_id,
    archived=True
)
```

### Searching Rules

Search for rules using regular expressions:

```python
# Search for rules containing specific patterns
results = chronicle.search_rules("suspicious process")
for rule in results.get("rules", []):
    rule_id = rule.get("name", "").split("/")[-1]
    print(f"Rule ID: {rule_id}, contains: 'suspicious process'")
    
# Find rules mentioning a specific MITRE technique
mitre_rules = chronicle.search_rules("T1055")
print(f"Found {len(mitre_rules.get('rules', []))} rules mentioning T1055 technique")
```

### Testing Rules

Test rules against historical data to validate their effectiveness before deployment:

```python
from datetime import datetime, timedelta, timezone

# Define time range for testing
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)  # Test against last 7 days

# Rule to test
rule_text = """
rule test_rule {
    meta:
        description = "Test rule for validation"
        author = "Test Author"
        severity = "Low"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
    condition:
        $e
}
"""

# Test the rule
test_results = chronicle.run_rule_test(
    rule_text=rule_text,
    start_time=start_time,
    end_time=end_time,
    max_results=100
)

# Process streaming results
detection_count = 0
for result in test_results:
    result_type = result.get("type")
    
    if result_type == "progress":
        # Progress update
        percent_done = result.get("percentDone", 0)
        print(f"Progress: {percent_done}%")
    
    elif result_type == "detection":
        # Detection result
        detection_count += 1
        detection = result.get("detection", {})
        print(f"Detection {detection_count}:")
        
        # Process detection details
        if "rule_id" in detection:
            print(f"  Rule ID: {detection['rule_id']}")
        if "data" in detection:
            print(f"  Data: {detection['data']}")
            
    elif result_type == "error":
        # Error information
        print(f"Error: {result.get('message', 'Unknown error')}")

print(f"Finished testing. Found {detection_count} detection(s).")
```

# Extract just the UDM events for programmatic processing
```python
udm_events = []
for result in chronicle.run_rule_test(rule_text, start_time, end_time, max_results=100):
    if result.get("type") == "detection":
        detection = result.get("detection", {})
        result_events = detection.get("resultEvents", {})
        
        for var_name, var_data in result_events.items():
            event_samples = var_data.get("eventSamples", [])
            for sample in event_samples:
                event = sample.get("event")
                if event:
                    udm_events.append(event)

# Process the UDM events
for event in udm_events:
    # Process each UDM event
    metadata = event.get("metadata", {})
    print(f"Event type: {metadata.get('eventType')}")
```

### Retrohunts

Run rules against historical data to find past matches:

```python
from datetime import datetime, timedelta, timezone

# Set time range for retrohunt
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)  # Search past 7 days

# Create retrohunt
retrohunt = chronicle.create_retrohunt(rule_id, start_time, end_time)
operation_id = retrohunt.get("name", "").split("/")[-1]

# Check retrohunt status
retrohunt_status = chronicle.get_retrohunt(rule_id, operation_id)
is_complete = retrohunt_status.get("metadata", {}).get("done", False)
```

### Detections and Errors

Monitor rule detections and execution errors:

```python
from datetime import datetime, timedelta

start_time = datetime.now(timezone.utc)
end_time = start_time - timedelta(days=7)
# List detections for a rule
detections = chronicle.list_detections(
    rule_id=rule_id,
    start_time=start_time,
    end_time=end_time,
    list_basis="CREATED_TIME"
)
for detection in detections.get("detections", []):
    detection_id = detection.get("id", "")
    event_time = detection.get("eventTime", "")
    alerting = detection.get("alertState", "") == "ALERTING"
    print(f"Detection: {detection_id}, Time: {event_time}, Alerting: {alerting}")

# List execution errors for a rule
errors = chronicle.list_errors(rule_id)
for error in errors.get("ruleExecutionErrors", []):
    error_message = error.get("error_message", "")
    create_time = error.get("create_time", "")
    print(f"Error: {error_message}, Time: {create_time}")
```

### Rule Alerts

Search for alerts generated by rules:

```python
# Set time range for alert search
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)  # Search past 7 days

# Search for rule alerts
alerts_response = chronicle.search_rule_alerts(
    start_time=start_time,
    end_time=end_time,
    page_size=10
)

# The API returns a nested structure where alerts are grouped by rule
# Extract and process all alerts from this structure
all_alerts = []
too_many_alerts = alerts_response.get('tooManyAlerts', False)

# Process the nested response structure - alerts are grouped by rule
for rule_alert in alerts_response.get('ruleAlerts', []):
    # Extract rule metadata
    rule_metadata = rule_alert.get('ruleMetadata', {})
    rule_id = rule_metadata.get('properties', {}).get('ruleId', 'Unknown')
    rule_name = rule_metadata.get('properties', {}).get('name', 'Unknown')
    
    # Get alerts for this rule
    rule_alerts = rule_alert.get('alerts', [])
    
    # Process each alert
    for alert in rule_alerts:
        # Extract important fields
        alert_id = alert.get("id", "")
        detection_time = alert.get("detectionTimestamp", "")
        commit_time = alert.get("commitTimestamp", "")
        alerting_type = alert.get("alertingType", "")
        
        print(f"Alert ID: {alert_id}")
        print(f"Rule ID: {rule_id}")
        print(f"Rule Name: {rule_name}")
        print(f"Detection Time: {detection_time}")
        
        # Extract events from the alert
        if 'resultEvents' in alert:
            for var_name, event_data in alert.get('resultEvents', {}).items():
                if 'eventSamples' in event_data:
                    for sample in event_data.get('eventSamples', []):
                        if 'event' in sample:
                            event = sample['event']
                            # Process event data
                            event_type = event.get('metadata', {}).get('eventType', 'Unknown')
                            print(f"Event Type: {event_type}")
```

If `tooManyAlerts` is True in the response, consider narrowing your search criteria using a smaller time window or more specific filters.

### Curated Rule Sets

Query curated rules:

```python
# List all curated rules
rules = chronicle.list_curated_rules()
for rule in rules:
    rule_id = rule.get("name", "").split("/")[-1]
    display_name = rule.get("description")
    description = rule.get("description")
    print(f"Rule: {display_name}, Description: {description}")

# Get a curated rule
rule = chronicle.get_curated_rule("ur_ttp_lol_Atbroker")

# Get a curated rule set by display name
# NOTE: This is a linear scan of all curated rules which may be inefficient for large rule sets.
rule_set = chronicle.get_curated_rule_by_name("Atbroker.exe Abuse")
```

Search for curated rules detections:

```python
from datetime import datetime, timedelta, timezone
from secops.chronicle.models import AlertState, ListBasis

# Search for detections from a specific curated rule
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=7)

result = chronicle.search_curated_detections(
    rule_id="ur_ttp_GCP_MassSecretDeletion",
    start_time=start_time,
    end_time=end_time,
    list_basis=ListBasis.DETECTION_TIME,
    alert_state=AlertState.ALERTING,
    page_size=100
)

detections = result.get("curatedDetections", [])
print(f"Found {len(detections)} detections")

# Check if more results are available
if "nextPageToken" in result:
    # Retrieve next page
    next_result = chronicle.search_curated_detections(
        rule_id="ur_ttp_GCP_MassSecretDeletion",
        start_time=start_time,
        end_time=end_time,
        list_basis=ListBasis.DETECTION_TIME,
        page_token=result["nextPageToken"],
        page_size=100
    )
```

Query curated rule sets:

```python
# List all curated rule sets
rule_sets = chronicle.list_curated_rule_sets()
for rule_set in rule_sets:
    rule_set_id = rule_set.get("name", "").split("/")[-1]
    display_name = rule_set.get("displayName")
    print(f"Rule Set: {display_name}, ID: {rule_set_id}")

# Get a curated rule set by ID
rule_set = chronicle.get_curated_rule_set("00ad672e-ebb3-0dd1-2a4d-99bd7c5e5f93")
```

Query curated rule set categories:

```python
# List all curated rule set categories
rule_set_categories = chronicle.list_curated_rule_set_categories()
for rule_set_category in rule_set_categories:
    rule_set_category_id = rule_set_category.get("name", "").split("/")[-1]
    display_name = rule_set_category.get("displayName")
    print(f"Rule Set Category: {display_name}, ID: {rule_set_category_id}")

# Get a curated rule set category by ID
rule_set_category = chronicle.get_curated_rule_set_category("110fa43d-7165-2355-1985-a63b7cdf90e8")
```

Manage curated rule set deployments (turn alerting on or off (either precise or broad) for curated rule sets):

```python
# List all curated rule set deployments
rule_set_deployments = chronicle.list_curated_rule_set_deployments()
for rs_deployment in rule_set_deployments:
    rule_set_id = rs_deployment.get("name", "").split("/")[-3]
    category_id = rs_deployment.get("name", "").split("/")[-5]
    deployment_status = rs_deployment.get("name", "").split("/")[-1]
    display_name = rs_deployment.get("displayName")
    alerting = rs_deployment.get("alerting", False)
    print(
        f"Rule Set: {display_name},"
        f"Rule Set ID: {rule_set_id}",
        f"Category ID: {category_id}",
        f"Precision: {deployment_status}",
        f"Alerting: {alerting}",
    )

# Get curated rule set deployment by ID
rule_set_deployment = chronicle.get_curated_rule_set_deployment("00ad672e-ebb3-0dd1-2a4d-99bd7c5e5f93")

# Get curated rule set deployment by rule set display name
# NOTE: This is a linear scan of all curated rules which may be inefficient for large rule sets.
rule_set_deployment = chronicle.get_curated_rule_set_deployment_by_name("Azure - Network")
    
# Update multiple curated rule set deployments
# Define deployments for rule sets
deployments = [
    {
        "category_id": "category-uuid",
        "rule_set_id": "ruleset-uuid",
        "precision": "broad",
        "enabled": True,
        "alerting": False
    }
]

chronicle.batch_update_curated_rule_set_deployments(deployments)

# Update a single curated rule set deployment
chronicle.update_curated_rule_set_deployment(
    category_id="category-uuid",
    rule_set_id="ruleset-uuid",
    precision="broad",
    enabled=True,
    alerting=False
)

```

### Rule Validation

Validate a YARA-L2 rule before creating or updating it:

```python
# Example rule
rule_text = """
rule test_rule {
    meta:
        description = "Test rule for validation"
        author = "Test Author"
        severity = "Low"
        yara_version = "YL2.0"
        rule_version = "1.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
    condition:
        $e
}
"""

# Validate the rule
result = chronicle.validate_rule(rule_text)

if result.success:
    print("Rule is valid")
else:
    print(f"Rule is invalid: {result.message}")
    if result.position:
        print(f"Error at line {result.position['startLine']}, column {result.position['startColumn']}")
```

### Rule Exclusions

Rule Exclusions allow you to exclude specific events from triggering detections in Chronicle. They are useful for filtering out known false positives or excluding test/development traffic from production detections.

```python
from secops.chronicle.rule_exclusion import RuleExclusionType
from datetime import datetime, timedelta

# Create a new rule exclusion
exclusion = chronicle.create_rule_exclusion(
    display_name="Exclusion Display Name",
    refinement_type=RuleExclusionType.DETECTION_EXCLUSION,
    query='(domain = "google.com")'
)

# Get exclusion id from name
exclusion_id = exclusion["name"].split("/")[-1]

# Get details of a specific rule exclusion
exclusion_details = chronicle.get_rule_exclusion(exclusion_id)
print(f"Exclusion: {exclusion_details.get('display_name')}")
print(f"Query: {exclusion_details.get('query')}")

# List all rule exclusions with pagination
exclusions = chronicle.list_rule_exclusions(page_size=10)
for exclusion in exclusions.get("findingsRefinements", []):
    print(f"- {exclusion.get('display_name')}: {exclusion.get('name')}")

# Update an existing exclusion
updated = chronicle.patch_rule_exclusion(
    exclusion_id=exclusion_id,
    display_name="Updated Exclusion",
    query='(ip = "8.8.8.8")',
    update_mask="display_name,query"
)

# Manage deployment settings
chronicle.update_rule_exclusion_deployment(
    exclusion_id,
    enabled=True,
    archived=False,
    detection_exclusion_application={
        "curatedRules": [],
        "curatedRuleSets": [],
        "rules": [],
    }
)

# Compute rule exclusion Activity for provided time period
end_time = datetime.utcnow()
start_time = end_time - timedelta(days=7)

activity = chronicle.compute_rule_exclusion_activity(
    exclusion_id,
    start_time=start_time,
    end_time=end_time
)
```

### Featured Content Rules

Featured content rules are pre-built detection rules available in the Chronicle Content Hub. These curated rules help you quickly deploy detections without writing custom rules.

```python
# List all featured content rules
rules = chronicle.list_featured_content_rules()
for rule in rules.get("featuredContentRules", []):
    rule_id = rule.get("name", "").split("/")[-1]
    content_metadata = rule.get("contentMetadata", {})
    display_name = content_metadata.get("displayName", "Unknown")
    severity = rule.get("severity", "UNSPECIFIED")
    print(f"Rule: {display_name} [{rule_id}] - Severity: {severity}")

# List with pagination
result = chronicle.list_featured_content_rules(page_size=10)
rules = result.get("featuredContentRules", [])
next_page_token = result.get("nextPageToken")

if next_page_token:
    next_page = chronicle.list_featured_content_rules(
        page_size=10,
        page_token=next_page_token
    )

# Filter list
filtered_rules = chronicle.list_featured_content_rules(
    filter_expression=(
        'category_name:"Threat Detection" AND '
        'rule_precision:"Precise"'
    )
)
```

## Data Tables and Reference Lists

Chronicle provides two ways to manage and reference structured data in detection rules: Data Tables and Reference Lists. These can be used to maintain lists of trusted/suspicious entities, mappings of contextual information, or any other structured data useful for detection.

### Data Tables

Data Tables are collections of structured data with defined columns and data types. They can be referenced in detection rules to enhance your detections with additional context.

#### Creating Data Tables

```python
from secops.chronicle.data_table import DataTableColumnType

# Create a data table with different column types
data_table = chronicle.create_data_table(
    name="suspicious_ips",
    description="Known suspicious IP addresses with context",
    header={
        "ip_address": DataTableColumnType.CIDR,
        # Alternately, you can map a column to an entity proto field
        # See: https://cloud.google.com/chronicle/docs/investigation/data-tables#map_column_names_to_entity_fields_optional
        # "ip_address": "entity.asset.ip"
        "port": DataTableColumnType.NUMBER,
        "severity": DataTableColumnType.STRING,
        "description": DataTableColumnType.STRING
    },
    # Optional: Set additional column options (valid options: repeatedValues, keyColumns)
    column_options: {"ip_address": {"repeatedValues": True}},
    # Optional: Add initial rows
    rows=[
        ["192.168.1.100", 3232, "High", "Scanning activity"],
        ["10.0.0.5", 9000, "Medium", "Suspicious login attempts"]
    ]
)

print(f"Created table: {data_table['name']}")
```

#### Managing Data Tables

```python
# List all data tables
tables = chronicle.list_data_tables()
for table in tables:
    table_id = table["name"].split("/")[-1]
    print(f"Table: {table_id}, Created: {table.get('createTime')}")

# Get a specific data table's details
table_details = chronicle.get_data_table("suspicious_ips")
print(f"Column count: {len(table_details.get('columnInfo', []))}")

# Update a data table's properties
updated_table = chronicle.update_data_table(
    "suspicious_ips",
    description="Updated description for suspicious IPs",
    row_time_to_live="72h"  # Set TTL for rows to 72 hours
    update_mask=["description", "row_time_to_live"]
)
print(f"Updated data table: {updated_table['name']}")

# Add rows to a data table
chronicle.create_data_table_rows(
    "suspicious_ips",
    [
        ["172.16.0.1", "Low", "Unusual outbound connection"],
        ["192.168.2.200", "Critical", "Data exfiltration attempt"]
    ]
)

# List rows in a data table
rows = chronicle.list_data_table_rows("suspicious_ips")
for row in rows:
    row_id = row["name"].split("/")[-1]
    values = row.get("values", [])
    print(f"Row {row_id}: {values}")

# Delete specific rows by ID
row_ids = [rows[0]["name"].split("/")[-1], rows[1]["name"].split("/")[-1]]
chronicle.delete_data_table_rows("suspicious_ips", row_ids)

# Replace all rows in a data table with new rows
chronicle.replace_data_table_rows(
    name="suspicious_ips", # Data table Name
    rows=[
        ["192.168.100.1", "Critical", "Active scanning"],
        ["10.1.1.5", "High", "Brute force attempts"],
        ["172.16.5.10", "Medium", "Suspicious traffic"]
    ]
)

# Bulk update rows in a data table
row_updates = [
    {
        "name": "projects/my-project/locations/us/instances/my-instance/dataTables/suspicious_ips/dataTableRows/row123",  # Full resource name
        "values": ["192.168.100.1", "Critical", "Updated description"]
    },
    {
        "name": "projects/my-project/locations/us/instances/my-instance/dataTables/suspicious_ips/dataTableRows/row456",  # Full resource name
        "values": ["10.1.1.5", "High", "Updated brute force info"],
        "update_mask": "values"  # Optional: only update values field
    }
]

# Execute bulk update
chronicle.update_data_table_rows(
    name="suspicious_ips",
    row_updates=row_updates
)

# Delete a data table
chronicle.delete_data_table("suspicious_ips", force=True)  # force=True deletes even if it has rows
```

### Reference Lists

Reference Lists are simple lists of values (strings, CIDR blocks, or regex patterns) that can be referenced in detection rules. They are useful for maintaining whitelists, blacklists, or any other categorized sets of values.

#### Creating Reference Lists

```python
from secops.chronicle.reference_list import ReferenceListSyntaxType, ReferenceListView

# Create a reference list with string entries
string_list = chronicle.create_reference_list(
    name="admin_accounts",
    description="Administrative user accounts",
    entries=["admin", "administrator", "root", "system"],
    syntax_type=ReferenceListSyntaxType.STRING
)

print(f"Created reference list: {string_list['name']}")

# Create a reference list with CIDR entries
cidr_list = chronicle.create_reference_list(
    name="trusted_networks",
    description="Internal network ranges",
    entries=["10.0.0.0/8", "192.168.0.0/16", "172.16.0.0/12"],
    syntax_type=ReferenceListSyntaxType.CIDR
)

# Create a reference list with regex patterns
regex_list = chronicle.create_reference_list(
    name="email_patterns",
    description="Email patterns to watch for",
    entries=[".*@suspicious\\.com", "malicious_.*@.*\\.org"],
    syntax_type=ReferenceListSyntaxType.REGEX
)
```

#### Managing Reference Lists

```python
# List all reference lists (basic view without entries)
lists = chronicle.list_reference_lists(view=ReferenceListView.BASIC)
for ref_list in lists:
    list_id = ref_list["name"].split("/")[-1]
    print(f"List: {list_id}, Description: {ref_list.get('description')}")

# Get a specific reference list including all entries
admin_list = chronicle.get_reference_list("admin_accounts", view=ReferenceListView.FULL)
entries = [entry.get("value") for entry in admin_list.get("entries", [])]
print(f"Admin accounts: {entries}")

# Update reference list entries
chronicle.update_reference_list(
    name="admin_accounts",
    entries=["admin", "administrator", "root", "system", "superuser"]
)

# Update reference list description
chronicle.update_reference_list(
    name="admin_accounts",
    description="Updated administrative user accounts list"
)

```

### Using in YARA-L Rules

Both Data Tables and Reference Lists can be referenced in YARA-L detection rules.

#### Using Data Tables in Rules

```
rule detect_with_data_table {
    meta:
        description = "Detect connections to suspicious IPs"
        author = "SecOps SDK Example"
        severity = "Medium"
        yara_version = "YL2.0"
    events:
        $e.metadata.event_type = "NETWORK_CONNECTION"
        $e.target.ip != ""
        $lookup in data_table.suspicious_ips
        $lookup.ip_address = $e.target.ip
        $severity = $lookup.severity
        
    condition:
        $e and $lookup and $severity = "High"
}
```

#### Using Reference Lists in Rules

```
rule detect_with_reference_list {
    meta:
        description = "Detect admin account usage from untrusted networks"
        author = "SecOps SDK Example" 
        severity = "High"
        yara_version = "YL2.0"
    events:
        $login.metadata.event_type = "USER_LOGIN"
        $login.principal.user.userid in reference_list.admin_accounts
        not $login.principal.ip in reference_list.trusted_networks
        
    condition:
        $login
}
```

## Gemini AI

You can use Chronicle's Gemini AI to get security insights, generate detection rules, explain security concepts, and more:

> **Note:** Only enterprise tier users have access to Advanced Gemini features. Users must opt-in to use Gemini in Chronicle before accessing this functionality. 
The SDK will automatically attempt to opt you in when you first use the Gemini functionality. If the automatic opt-in fails due to permission issues, 
you'll see an error message that includes "users must opt-in before using Gemini."

```python
# Query Gemini with a security question
response = chronicle.gemini("What is Windows event ID 4625?")

# Get text content (combines TEXT blocks and stripped HTML content)
text_explanation = response.get_text_content()
print("Explanation:", text_explanation)

# Work with different content blocks
for block in response.blocks:
    print(f"Block type: {block.block_type}")
    if block.block_type == "TEXT":
        print("Text content:", block.content)
    elif block.block_type == "CODE":
        print(f"Code ({block.title}):", block.content)
    elif block.block_type == "HTML":
        print("HTML content (with tags):", block.content)

# Get all code blocks
code_blocks = response.get_code_blocks()
for code_block in code_blocks:
    print(f"Code block ({code_block.title}):", code_block.content)

# Get all HTML blocks (with HTML tags preserved)
html_blocks = response.get_html_blocks()
for html_block in html_blocks:
    print(f"HTML block (with tags):", html_block.content)

# Check for references
if response.references:
    print(f"Found {len(response.references)} references")

# Check for suggested actions
for action in response.suggested_actions:
    print(f"Suggested action: {action.display_text} ({action.action_type})")
    if action.navigation:
        print(f"Action URI: {action.navigation.target_uri}")
```

### Response Content Methods

The `GeminiResponse` class provides several methods to work with response content:

- `get_text_content()`: Returns a combined string of all TEXT blocks plus the text content from HTML blocks with HTML tags removed
- `get_code_blocks()`: Returns a list of blocks with `block_type == "CODE"`
- `get_html_blocks()`: Returns a list of blocks with `block_type == "HTML"` (HTML tags preserved)
- `get_raw_response()`: Returns the complete, unprocessed API response as a dictionary

These methods help you work with different types of content in a structured way.

### Accessing Raw API Response

For advanced use cases or debugging, you can access the raw API response:

```python
# Get the complete raw API response
response = chronicle.gemini("What is Windows event ID 4625?")
raw_response = response.get_raw_response()

# Now you can access any part of the original JSON structure
print(json.dumps(raw_response, indent=2))

# Example of navigating the raw response structure
if "responses" in raw_response:
    for resp in raw_response["responses"]:
        if "blocks" in resp:
            print(f"Found {len(resp['blocks'])} blocks in raw response")
```

This gives you direct access to the original API response format, which can be useful for accessing advanced features or troubleshooting.

### Manual Opt-In

If your account has sufficient permissions, you can manually opt-in to Gemini before using it:

```python
# Manually opt-in to Gemini
opt_success = chronicle.opt_in_to_gemini()
if opt_success:
    print("Successfully opted in to Gemini")
else:
    print("Unable to opt-in due to permission issues")

# Then use Gemini as normal
response = chronicle.gemini("What is Windows event ID 4625?")
```

This can be useful in environments where you want to explicitly control when the opt-in happens.

### Generate Detection Rules

Chronicle Gemini can generate YARA-L rules for detection:

```python
# Generate a rule to detect potential security issues
rule_response = chronicle.gemini("Write a rule to detect powershell downloading a file called gdp.zip")

# Extract the generated rule(s)
code_blocks = rule_response.get_code_blocks()
if code_blocks:
    rule = code_blocks[0].content
    print("Generated rule:", rule)
    
    # Check for rule editor action
    for action in rule_response.suggested_actions:
        if action.display_text == "Open in Rule Editor" and action.action_type == "NAVIGATION":
            rule_editor_url = action.navigation.target_uri
            print("Rule can be opened in editor:", rule_editor_url)
```

### Get Intel Information

Get detailed information about malware, threat actors, files, vulnerabilities:

```python
# Ask about a CVE
cve_response = chronicle.gemini("tell me about CVE-2021-44228")

# Get the explanation
cve_explanation = cve_response.get_text_content()
print("CVE explanation:", cve_explanation)
```

### Maintain Conversation Context

You can maintain conversation context by reusing the same conversation ID:

```python
# Start a conversation
initial_response = chronicle.gemini("What is a DDoS attack?")

# Get the conversation ID from the response
conversation_id = initial_response.name.split('/')[-3]  # Extract from format: .../conversations/{id}/messages/{id}

# Ask a follow-up question in the same conversation context
followup_response = chronicle.gemini(
    "What are the most common mitigation techniques?",
    conversation_id=conversation_id
)

# Gemini will remember the context of the previous question about DDoS
```

## Feed Management

Feeds are used to ingest data into Chronicle. The SDK provides methods to manage feeds.

```python
import json

# List existing feeds
feeds = chronicle.list_feeds()
print(f"Found {len(feeds)} feeds")

# Create a new feed
feed_details = {
    "logType": f"projects/your-project-id/locations/us/instances/your-chronicle-instance-id/logTypes/WINEVTLOG",
    "feedSourceType": "HTTP",
    "httpSettings": {
        "uri": "https://example.com/example_feed",
        "sourceType": "FILES",
    },
    "labels": {"environment": "production", "created_by": "secops_sdk"}
}

created_feed = chronicle.create_feed(
    display_name="My New Feed",
    details=feed_details
)

# Get feed ID from name
feed_id = created_feed["name"].split("/")[-1]
print(f"Feed created with ID: {feed_id}")

# Get feed details
feed_details = chronicle.get_feed(feed_id)
print(f"Feed state: {feed_details.get('state')}")

# Update feed
updated_details = {
    "httpSettings": {
        "uri": "https://example.com/updated_feed_url",
        "sourceType": "FILES"
    },
    "labels": {"environment": "production", "updated": "true"}
}

updated_feed = chronicle.update_feed(
    feed_id=feed_id,
    display_name="Updated Feed Name",
    details=updated_details
)

# Disable feed
disabled_feed = chronicle.disable_feed(feed_id)
print(f"Feed disabled. State: {disabled_feed.get('state')}")

# Enable feed
enabled_feed = chronicle.enable_feed(feed_id)
print(f"Feed enabled. State: {enabled_feed.get('state')}")

# Generate secret for feed (for supported feed types)
try:
    secret_result = chronicle.generate_secret(feed_id)
    print(f"Generated secret: {secret_result.get('secret')}")
except Exception as e:
    print(f"Error generating secret for feed: {e}")

# Delete feed
chronicle.delete_feed(feed_id)
print("Feed deleted successfully")
```

The Feed API supports different feed types such as HTTP, HTTPS Push, and S3 bucket data sources etc. Each feed type has specific configuration options that can be specified in the `details` dictionary.

> **Note**: Secret generation is only available for certain feed types that require authentication.

## Chronicle Dashboard

The Chronicle Dashboard API provides methods to manage native dashboards and dashboard charts in Chronicle.

### Create Dashboard
```python
# Create a dashboard
dashboard = chronicle.create_dashboard(
    display_name="Security Overview",
    description="Dashboard showing security metrics",
    access_type="PRIVATE"  # "PRIVATE" or "PUBLIC"
)
dashboard_id = dashboard["name"].split("/")[-1]
print(f"Created dashboard with ID: {dashboard_id}")
```

### Get Specific Dashboard Details
```python
# Get a specific dashboard
dashboard = chronicle.get_dashboard(
    dashboard_id="dashboard-id-here",
    view="FULL"  # Optional: "BASIC" or "FULL" 
)
print(f"Dashboard Details: {dashboard}")
```

### List Dashboards with pagination
```python
# List dashboards (first page)
dashboards = chronicle.list_dashboards(page_size=10)
for dashboard in dashboards.get("nativeDashboards", []):
    print(f"- {dashboard.get('displayName')}")

# Get next page if available
if "nextPageToken" in dashboards:
    next_page = chronicle.list_dashboards(
        page_size=10,
        page_token=dashboards["nextPageToken"]
    )
```

### Update existing dashboard details
```python
filters = [
    {
        "id": "GlobalTimeFilter",
        "dataSource": "GLOBAL",
        "filterOperatorAndFieldValues": [
            {"filterOperator": "PAST", "fieldValues": ["7", "DAY"]}
        ],
        "displayName": "Global Time Filter",
        "chartIds": [],
        "isStandardTimeRangeFilter": True,
        "isStandardTimeRangeFilterEnabled": True,
    }
]
charts = [
    {
        "dashboardChart": "projects/<project_id>/locations/<location>/instances/<instacne_id>/dashboardCharts/<chart_id>",
        "chartLayout": {"startX": 0, "spanX": 48, "startY": 0, "spanY": 26},
        "filtersIds": ["GlobalTimeFilter"],
    }
]
# Update a dashboard
updated_dashboard = chronicle.update_dashboard(
    dashboard_id="dashboard-id-here",
    display_name="Updated Security Dashboard",
    filters=filters,
    charts=charts,
)
print(f"Updated dashboard: {updated_dashboard['displayName']}")
```

### Duplicate existing dashboard
```python
# Duplicate a dashboard
duplicate = chronicle.duplicate_dashboard(
    dashboard_id="dashboard-id-here",
    display_name="Copy of Security Dashboard",
    access_type="PRIVATE"
)
duplicate_id = duplicate["name"].split("/")[-1]
print(f"Created duplicate dashboard with ID: {duplicate_id}")
```

#### Import Dashboard
Imports a dashboard from a JSON file.

```python
import os
from secops.chronicle import client

# Assumes the CHRONICLE_SA_KEY environment variable is set with service account JSON
chronicle_client = client.Client()

# Path to the dashboard file
dashboard = {
    "dashboard": {...}
    "dashboardCharts": [...],
    "dashboardQueries": [...]
}

# Import the dashboard
try:
    new_dashboard = chronicle_client.import_dashboard(dashboard)
    print(new_dashboard)
except Exception as e:
    print(f"An error occurred: {e}")

```

#### Export Dashboards

Export one or more dashboards to a dictionary.

```python
import os
from secops.chronicle import client

# Assumes the CHRONICLE_SA_KEY environment variable is set with service account JSON
chronicle_client = client.Client()

# Export a single dashboard
dashboards = chronicle.export_dashboard(dashboard_names=["<dashboard_id>"])

# Export multiple dashboards
dashboards = chronicle.export_dashboard(dashboard_names=["<dashboard_id_1>", "<dashboard_id_2>"])
```


### Add Chart to existing dashboard
```python
# Define chart configuration
query = """
metadata.event_type = "NETWORK_DNS"
match:
  principal.hostname
outcome:
  $dns_query_count = count(metadata.id)
order:
  principal.hostname asc
"""

chart_layout = {
    "startX": 0, 
    "spanX": 12, 
    "startY": 0, 
    "spanY": 8
}

chart_datasource = {
    "dataSources": ["UDM"]
}

interval = {
    "relativeTime": {
        "timeUnit": "DAY",
        "startTimeVal": "1"
    }
}

# Add chart to dashboard
chart = chronicle.add_chart(
    dashboard_id="dashboard-id-here",
    display_name="DNS Query Metrics",
    query=query,
    chart_layout=chart_layout,
    chart_datasource=chart_datasource,
    interval=interval,
    tile_type="VISUALIZATION" # Option: "VISUALIZATION" or "BUTTOn"
)
```

### Get Dashboard Chart Details
```python
# Get dashboard chart details
dashboard_chart = chronicle.get_chart(
    chart_id="chart-id-here"
)
print(f"Dashboard Chart Details: {dashboard_chart}")
```

### Edit Dashboard Chart
```python
# Dashboard Query updated details
updated_dashboard_query={
    "name": "project/<projectNumber>/instance/<instanceNumber>/dashboardQueries/<query_id>",
    "query": 'metadata.event_type = "USER_LOGIN"\nmatch:\n  principal.user.userid\noutcome:\n  $logon_count = count(metadata.id)\norder:\n  $logon_count desc\nlimit: 10',
    "input": {"relativeTime": {"timeUnit": "DAY", "startTimeVal": "1"}},
    "etag": "123456", # Latest etag from server
}

# Dashboard Chart updated details
updated_dashboard_chart={
    "name": "project/<projectNumber>/instance/<instanceNumber>/dashboardCharts/<chart_id>",
    "display_name": "Updated chart display Name",
    "description": "Updated chart description",
    "etag": "12345466", # latest etag from server
    "visualization": {},
    "chart_datasource":{"data_sources":[]}
}

updated_chart = chronicle.edit_chart(
    dashboard_id="dashboard-id-here",
    dashboard_chart=updated_dashboard_chart,
    dashboard_query=updated_dashboard_query
)
print(f"Updated dashboard chart: {updated_chart}")
```

### Remove Chart from existing dashboard
```python
# Remove chart from dashboard
chronicle.remove_chart(
    dashboard_id="dashboard-id-here",
    chart_id="chart-id-here"
)
```

### Delete existing dashboard
```python
# Delete a dashboard
chronicle.delete_dashboard(dashboard_id="dashboard-id-here")
print("Dashboard deleted successfully")
```

## Dashboard Query

The Chronicle Dashboard Query API provides methods to execute dashboard queries without creating a dashboard and get details of dashboard query.

### Execute Dashboard Query
```python
# Define query and time interval
query = """
metadata.event_type = "USER_LOGIN"
match:
  principal.user.userid
outcome:
  $logon_count = count(metadata.id)
order:
  $logon_count desc
limit: 10
"""

interval = {
    "relativeTime": {
        "timeUnit": "DAY",
        "startTimeVal": "7"
    }
}

# Execute the query
results = chronicle.execute_dashboard_query(
    query=query,
    interval=interval
)

# Process results
for result in results.get("results", []):
    print(result)
```

### Get Dashboard Query details
```python
# Get dashboard query details
dashboard_query = chronicle.get_dashboard_query(
    query_id="query-id-here"
)
print(f"Dashboard Query Details: {dashboard_query}")
```

## Error Handling

The SDK defines several custom exceptions:

```python
from secops.exceptions import SecOpsError, AuthenticationError, APIError

try:
    results = chronicle.search_udm(...)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except APIError as e:
    print(f"API request failed: {e}")
except SecOpsError as e:
    print(f"General error: {e}")
```

## Value Type Detection

The SDK automatically detects the most common entity types when using the `summarize_entity` function:
- IP addresses (IPv4 and IPv6)
- MD5/SHA1/SHA256 hashes
- Domain names
- Email addresses
- MAC addresses
- Hostnames

This detection happens internally within `summarize_entity`, simplifying its usage. You only need to provide the `value` argument.

```python
# The SDK automatically determines how to query for these values
ip_summary = chronicle.summarize_entity(value="192.168.1.100", ...)
domain_summary = chronicle.summarize_entity(value="example.com", ...)
hash_summary = chronicle.summarize_entity(value="e17dd4eef8b4978673791ef4672f4f6a", ...)
```

You can optionally provide a `preferred_entity_type` hint to `summarize_entity` if the automatic detection might be ambiguous (e.g., a string could be a username or a hostname).

## License

This project is licensed under the Apache License 2.0 - [see the LICENSE file for details.](https://github.com/google/secops-wrapper/blob/main/LICENSE)
