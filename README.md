# Google SecOps SDK for Python

A Python SDK for interacting with Google Security Operations products, currently supporting Chronicle/SecOps SIEM.
This wraps the API for common use cases, including UDM searches, entity lookups, IoCs, alert management, case management, and detection rule management.

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

For detailed CLI documentation and examples, see the [CLI Documentation](CLI.md).

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
[See available regions](regions.md)

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

# Create a data export for a specific log type
export = chronicle.create_data_export(
    gcs_bucket="projects/my-project/buckets/my-export-bucket",
    start_time=start_time,
    end_time=end_time,
    log_type="GCP_DNS"  # Specify log type to export
)

# Get the export ID
export_id = export["name"].split("/")[-1]
print(f"Created export with ID: {export_id}")
print(f"Status: {export['data_export_status']['stage']}")

# Check export status
status = chronicle.get_data_export(export_id)
print(f"Export status: {status['data_export_status']['stage']}")
print(f"Progress: {status['data_export_status'].get('progress_percentage', 0)}%")

# Cancel an export if needed
if status['data_export_status']['stage'] in ['IN_QUEUE', 'PROCESSING']:
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
- Exporting one or all log types to Google Cloud Storage
- Checking export status and progress
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
    max_values=10
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
# List all parsers
parsers = chronicle.list_parsers()
for parser in parsers:
    parser_id = parser.get("name", "").split("/")[-1]
    state = parser.get("state")
    print(f"Parser ID: {parser_id}, State: {state}")

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
# List detections for a rule
detections = chronicle.list_detections(rule_id)
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

### Rule Sets

Manage curated rule sets:

```python
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

# Update rule set deployments
chronicle.batch_update_curated_rule_set_deployments(deployments)
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
        "severity": DataTableColumnType.STRING,
        "description": DataTableColumnType.STRING
    },
    # Optional: Add initial rows
    rows=[
        ["192.168.1.100", "High", "Scanning activity"],
        ["10.0.0.5", "Medium", "Suspicious login attempts"]
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

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
