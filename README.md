# Google SecOps SDK for Python

A Python SDK for interacting with Google Security Operations products, currently supporting Chronicle/SecOps SIEM.
This wraps the API for common use cases, including UDM searches, entity lookups, IoCs, alert management, case management, and detection rule management.

## Installation

```bash
pip install secops
```

## Running Locally Without Installation

To use the module directly from source without installing via pip:

1. Clone the repository:
   ```bash
   git clone https://github.com/google/secops-wrapper.git
   cd secops-wrapper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add the source directory to your Python path:
   ```python
   import sys
   import os
   
   # Add the src directory to the Python path
   sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
   
   # Now you can import the module
   from secops import SecOpsClient
   
   # Initialize with default credentials
   client = SecOpsClient()
   ```

Alternatively, you can use the PYTHONPATH environment variable:

```bash
# From the root of the secops-wrapper directory
PYTHONPATH=$PYTHONPATH:$(pwd)/src python your_script.py
```

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

For more explicit control, you can authenticate using a service account. This can be done in two ways:

#### a. Using a Service Account JSON File

```python
from secops import SecOpsClient

# Initialize with service account JSON file
client = SecOpsClient(service_account_path="/path/to/service-account.json")
```

#### b. Using Service Account Info Dictionary

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
        "displayName": "Joe Doe",
        "alternateId": "jdoe@example.com"
    },
    "client": {
        "ipAddress": "192.168.1.100",
        "userAgent": {
            "os": "Mac OS X",
            "browser": "SAFARI"
        }
    },
    "displayMessage": "User login to Okta",
    "eventType": "user.session.start",
    "outcome": {
        "result": "SUCCESS"
    },
    "published": current_time  # Current time in ISO format
}

# Ingest the log using the default forwarder
result = chronicle.ingest_log(
    log_type="OKTA",  # Chronicle log type
    log_message=json.dumps(okta_log)  # JSON string of the log
)

print(f"Operation: {result.get('operation')}")
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

## Using the Command Line Interface (CLI)

The SecOps SDK includes a command-line interface (CLI) that allows you to interact with Google SecOps services without writing Python code.

### Installation

The CLI is automatically installed when you install the SecOps SDK:

```bash
pip install secops
```

After installation, you can use the `secops` command directly from your terminal.

### Running Without Installation

For development or testing purposes, you can run the CLI directly from the source code without installing the package. The repository includes two scripts for this purpose:

#### Using the Python Script

```bash
# From the secops-wrapper directory
./secops-cli.py chronicle search --query "principal.ip = \"192.168.1.1\"" --start-time "1d"
```

#### Using the Shell Script

```bash
# From the secops-wrapper directory
./secops-cli.sh chronicle search --query "principal.ip = \"192.168.1.1\"" --start-time "1d"
```

Both scripts automatically add the `src` directory to the Python path, allowing you to run the CLI without installing the package. This is particularly useful during development when you're making changes to the CLI code and want to test them immediately.

### Authentication

The CLI supports the same authentication methods as the Python SDK. You can authenticate using the following methods:

1. **Application Default Credentials (ADC)** - This is the default method when no service account path is specified:

```bash
# Login and set up application-default credentials
gcloud auth application-default login

# Then run the CLI with just project and customer IDs
# Note: Global options (--project-id, --customer-id) must come BEFORE the subcommand
secops --project-id="your-project-id" --customer-id="your-customer-id" \
       chronicle search --query "principal.ip = \"192.168.1.1\"" --start-time "1d"
```

2. **Using environment variables**:

```bash
# Optional: Set service account path (if not using ADC)
export SECOPS_SERVICE_ACCOUNT_PATH="/path/to/service-account.json"

# Required parameters
export SECOPS_PROJECT_ID="your-project-id"
export SECOPS_CUSTOMER_ID="your-customer-id"
export SECOPS_REGION="us"  # Optional, defaults to "us"
```

3. **Using command-line options**:

```bash
# With service account (optional if using ADC)
# Note: Global options must come BEFORE the subcommand
secops --service-account-path="/path/to/service-account.json" \
       --project-id="your-project-id" --customer-id="your-customer-id" --region="us" \
       <command> <subcommand> [options]

# With application default credentials
secops --project-id="your-project-id" --customer-id="your-customer-id" \
       <command> <subcommand> [options]
```

3. Using a .env file:

Create a `.env` file with your configuration:

```
# Google SecOps CLI Configuration
SECOPS_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
SECOPS_PROJECT_ID=your-project-id
SECOPS_CUSTOMER_ID=your-customer-id
SECOPS_REGION=us
```

Then use the `--dotenv` option to specify the path to your .env file:

```bash
# Note: The --dotenv option is a global option and must come BEFORE the subcommand
secops --dotenv=.env chronicle search --query "principal.ip = \"192.168.1.1\"" --start-time "1d"
```

For convenience, the included `secops-cli.sh` script automatically looks for a `.env` file in the repository root directory and uses it if found:

```bash
# This will automatically use .env if it exists in the repository root
# Note: All command-line options for the main CLI must come AFTER ./secops-cli.sh and BEFORE the subcommand
./secops-cli.sh chronicle search --query "principal.ip = \"192.168.1.1\"" --start-time "1d"
```

A template `.env.template` file is provided in the repository that you can copy and customize:

```bash
cp .env.template .env
# Edit .env with your configuration
```

### Available Commands

The CLI is organized into groups of commands. Currently, the main group is `chronicle`, which contains commands for interacting with Chronicle:

#### Search UDM Events

```bash
# Basic search with a time range
secops chronicle search --query "principal.ip = \"192.168.1.1\"" --start-time "1d"

# Search with specific time range and output as JSON
secops chronicle search \
  --query "principal.ip = \"192.168.1.1\"" \
  --start-time "2023-03-20T00:00:00" \
  --end-time "2023-03-27T00:00:00" \
  --max-events 100 \
  --output json
```

#### Entity Summary

```bash
# Get summary for an IP address
secops chronicle entity --value "192.168.1.1" --start-time "1d"

# Get summary for a file hash
secops chronicle entity \
  --value "e17dd4eef8b4978673791ef4672f4f6a" \
  --start-time "7d" \
  --output json
```

#### Validate Query

```bash
# Validate a Chronicle search query
secops chronicle validate-query --query "principal.ip = \"192.168.1.1\""
```

#### List Rules

```bash
# List detection rules
secops chronicle list-rules

# List rules with JSON output
secops chronicle list-rules --output json
```

#### Get Rule

```bash
# Get a specific rule by ID
secops chronicle get-rule --rule-id "ru_12345678-1234-1234-1234-123456789012"

# Get a specific rule version
secops chronicle get-rule \
  --rule-id "ru_12345678-1234-1234-1234-123456789012" \
  --version-id "rv_12345678-1234-1234-1234-123456789012" \
  --output json
```

#### Natural Language Search

```bash
# Search using natural language
secops chronicle nl-search \
  --query "Show me all failed login attempts in the last 24 hours" \
  --start-time "1d"
```

### Time Format

The CLI supports both ISO format and relative time formats:

- ISO format: `YYYY-MM-DDTHH:MM:SS` (e.g., `2023-03-27T12:00:00`)
- Relative format: 
  - `Nd` for N days ago (e.g., `1d` for 1 day ago)
  - `Nh` for N hours ago (e.g., `12h` for 12 hours ago)

### Output Formats

Most commands support two output formats:

- `table`: Human-readable tabular format (default)
- `json`: JSON format for programmatic processing

Specify the output format using the `--output` option:

```bash
secops chronicle search --query "..." --start-time "1d" --output json
```
```


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
            "event": {
                "metadata": {
                    "eventTimestamp": "2024-02-09T10:30:00Z",
                    "eventType": "NETWORK_CONNECTION"
                },
                "target": {
                    "ip": "192.168.1.100",
                    "port": 443
                },
                "principal": {
                    "hostname": "workstation-1"
                }
            }
        }
    ],
    "total_events": 1
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

Get detailed information about specific entities:

```python
# IP address summary
ip_summary = chronicle.summarize_entity(
    start_time=start_time,
    end_time=end_time,
    value="192.168.1.100"  # Automatically detects IP
)

# Domain summary 
domain_summary = chronicle.summarize_entity(
    start_time=start_time,
    end_time=end_time,
    value="example.com"  # Automatically detects domain
)

# File hash summary
file_summary = chronicle.summarize_entity(
    start_time=start_time,
    end_time=end_time,
    value="e17dd4eef8b4978673791ef4672f4f6a"  # Automatically detects MD5
)

# Example response structure:
{
    "entities": [
        {
            "name": "entities/...",
            "metadata": {
                "entityType": "ASSET",
                "interval": {
                    "startTime": "2024-02-08T10:30:00Z",
                    "endTime": "2024-02-09T10:30:00Z"
                }
            },
            "metric": {
                "firstSeen": "2024-02-08T10:30:00Z",
                "lastSeen": "2024-02-09T10:30:00Z"
            },
            "entity": {
                "asset": {
                    "ip": ["192.168.1.100"]
                }
            }
        }
    ],
    "alertCounts": [
        {
            "rule": "Suspicious Network Connection",
            "count": 5
        }
    ],
    "widgetMetadata": {
        "detections": 5,
        "total": 1000
    }
}
```

### Entity Summary from Query

Look up entities based on a UDM query:

```python
# Search for a specific file hash across multiple UDM paths
md5_hash = "e17dd4eef8b4978673791ef4672f4f6a"
query = f'target.file.md5 = "{md5_hash}" OR principal.file.md5 = "{md5_hash}"'

entity_summaries = chronicle.summarize_entities_from_query(
    query=query,
    start_time=start_time,
    end_time=end_time
)

# Example response:
[
    {
        "entities": [
            {
                "name": "entities/...",
                "metadata": {
                    "entityType": "FILE",
                    "interval": {
                        "startTime": "2024-02-08T10:30:00Z",
                        "endTime": "2024-02-09T10:30:00Z"
                    }
                },
                "metric": {
                    "firstSeen": "2024-02-08T10:30:00Z",
                    "lastSeen": "2024-02-09T10:30:00Z"
                },
                "entity": {
                    "file": {
                        "md5": "e17dd4eef8b4978673791ef4672f4f6a",
                        "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
                        "filename": "suspicious.exe"
                    }
                }
            }
        ]
    }
]
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

# Get case details
if case_ids:
    cases = chronicle.get_cases(list(case_ids))
    
    # Process cases
    for case in cases.cases:
        print(f"Case: {case.display_name}")
        print(f"Priority: {case.priority}")
        print(f"Status: {case.status}")
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
# Get details for specific cases
cases = chronicle.get_cases(["case-id-1", "case-id-2"])

# Filter cases by priority
high_priority = cases.filter_by_priority("PRIORITY_HIGH")

# Filter cases by status
open_cases = cases.filter_by_status("STATUS_OPEN")

# Look up a specific case
case = cases.get_case("case-id-1")
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

The SDK automatically detects these entity types:
- IPv4 addresses
- MD5/SHA1/SHA256 hashes
- Domain names
- Email addresses
- MAC addresses
- Hostnames

Example of automatic detection:

```python
# These will automatically use the correct field paths and value types
ip_summary = chronicle.summarize_entity(value="192.168.1.100")
domain_summary = chronicle.summarize_entity(value="example.com")
hash_summary = chronicle.summarize_entity(value="e17dd4eef8b4978673791ef4672f4f6a")
```

You can also override the automatic detection:

```python
summary = chronicle.summarize_entity(
    value="example.com",
    field_path="custom.field.path",  # Override automatic detection
    value_type="DOMAIN_NAME"         # Explicitly set value type
)
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.