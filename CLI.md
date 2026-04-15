# Google SecOps SDK Command Line Interface

The Google SecOps SDK provides a comprehensive command-line interface (CLI) that makes it easy to interact with Google Security Operations products from your terminal.

## Installation

The CLI is automatically installed when you install the SecOps SDK:

```bash
pip install secops
```

## Authentication

The CLI supports the same authentication methods as the SDK:

### Using Application Default Credentials

```bash
# Set up ADC with gcloud
gcloud auth application-default login
```

## Configuration

The CLI allows you to save your credentials and other common settings in configuration files. The CLI supports two configuration scopes:

- **Global configuration**: Stored in `~/.secops/config.json` and applies to all projects
- **Local configuration**: Stored in `./.secops/config.json` in the current directory and applies only to the current project

Local configuration takes precedence over global configuration when both are present.

### Saving Configuration

#### Global Configuration

Save your Chronicle instance ID, project ID, and region globally:

```bash
secops config set --customer-id "your-instance-id" --project-id "your-project-id" --region "us"
```

You can also save your service account path:

```bash
secops config set --service-account "/path/to/service-account.json" --customer-id "your-instance-id" --project-id "your-project-id" --region "us"
```

Set the default API version for Chronicle API calls:

```bash
secops config set --api-version "v1"
```

**Supported API versions:**
- `v1` - Stable production API (recommended)
- `v1beta` - Beta API with newer features
- `v1alpha` - Alpha API with experimental features (default)

Additionally, you can set default time parameters:

```bash
secops config set --time-window 48
```

```bash
secops config set --start-time "2023-07-01T00:00:00Z" --end-time "2023-07-02T00:00:00Z"
```

#### Local Configuration

Use the `--local` flag to save configuration for the current project only:

```bash
secops config set --local --customer-id "project-specific-id" --project-id "project-a"
```

This is useful when working with multiple projects or environments. 

#### Managing Multiple Projects

You can use the `SECOPS_LOCAL_CONFIG_DIR` environment variable to switch between different project configurations:

```bash
# Setup configuration for Project A
export SECOPS_LOCAL_CONFIG_DIR=/path/to/project-a/.secops
mkdir -p $SECOPS_LOCAL_CONFIG_DIR
secops config set --local --project-id project-a --customer-id instance-a

# Setup configuration for Project B
export SECOPS_LOCAL_CONFIG_DIR=/path/to/project-b/.secops
mkdir -p $SECOPS_LOCAL_CONFIG_DIR
secops config set --local --project-id project-b --customer-id instance-b

# Use Project A config
export SECOPS_LOCAL_CONFIG_DIR=/path/to/project-a/.secops
secops search --query "..."
```

### Viewing Configuration

View your current global configuration:

```bash
secops config view
```

View local configuration:

```bash
secops config view --local
```

### Clearing Configuration

Clear all saved configuration:

```bash
secops config clear
```

### Using Saved Configuration

Once configured, you can run commands without specifying the common parameters:

```bash
# Before configuration
secops search --customer-id "your-instance-id" --project-id "your-project-id" --region "us" --query "metadata.event_type = \"NETWORK_CONNECTION\"" --time-window 24

# After configuration with credentials and time-window
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\""

# After configuration with start-time and end-time
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\""
```

You can still override configuration values by specifying them in the command line.

## Common Parameters

These parameters can be used with most commands:

- `--service-account PATH` - Path to service account JSON file
- `--customer-id ID` - Chronicle instance ID
- `--project-id ID` - GCP project ID
- `--region REGION` - Chronicle API region (default: us)
- `--api-version VERSION` - Chronicle API version (v1, v1beta, v1alpha; default: v1alpha)
- `--output FORMAT` - Output format (json, text)
- `--start-time TIME` - Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- `--end-time TIME` - End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- `--time-window HOURS` - Time window in hours (alternative to start/end time)

You can override the configured API version on a per-command basis:

```bash
# Use v1 for a specific command, even if config has v1alpha
secops rule list --api-version v1
```

## Commands

### Search UDM Events

Search for events using UDM query syntax:

```bash
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\"" --max-events 10

# Get result as list
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\"" --max-events 10 --as-list
```

Search using natural language:

```bash
secops search --nl-query "show me failed login attempts" --time-window 24
```

Export search results as CSV:

```bash
secops search --query "metadata.event_type = \"USER_LOGIN\" AND security_result.action = \"BLOCK\"" --fields "metadata.event_timestamp,principal.user.userid,principal.ip,security_result.summary" --time-window 24 --csv
```

> **Note:** Chronicle API uses snake_case for UDM field names. For example, use `security_result` instead of `securityResult`, `event_timestamp` instead of `eventTimestamp`. Valid UDM fields include: `metadata`, `principal`, `target`, `security_result`, `network`, etc.

### UDM Search View

Fetch UDM search results with additional contextual information including detection data:

```bash
# Basic search with query
secops udm-search-view --query "metadata.event_type = \"NETWORK_CONNECTION\"" --time-window 24 --max-events 10

# Search with query file
secops udm-search-view --query-file "/path/to/query.txt" --time-window 24 --max-events 10

# Search with snapshot query
secops udm-search-view \
  --query "metadata.event_type = \"NETWORK_CONNECTION\"" \
  --snapshot-query "feedback_summary.status = \"OPEN\"" \
  --time-window 24 \
  --max-events 10 \
  --max-detections 5
  
# Enable case sensitivity (disabled by default)
secops udm-search-view --query "metadata.event_type = \"NETWORK_CONNECTION\"" --case-sensitive --time-window 24
```

### Find UDM Field Values

Search ingested UDM field values that match a query:

```bash
secops search udm-field-values --query "source" --page-size 10
```

### Search Raw Logs

Search for raw logs in Chronicle using the query language:

```bash
secops search raw-logs \
  --query 'raw = \"authentication\"' \
  --snapshot-query 'user != ""' \
  --time-window 24 \
  --case-sensitive \
  --log-types "OKTA,AZURE_AD" \
  --max-aggregations-per-field 100 \
  --page-size 25
```

### Get Statistics

Run statistical analyses on your data:

```bash
secops stats --query "metadata.event_type = \"NETWORK_CONNECTION\"
match:
  target.hostname
outcome:
  \$count = count(metadata.id)
order:
  \$count desc" --time-window 24

# Invoke with custom timeout
secops stats --query "metadata.event_type = \"NETWORK_CONNECTION\"
match:
  target.hostname
outcome:
  \$count = count(metadata.id)
order:
  \$count desc" --time-window 24 --timeout 200
```

### Entity Information

Get detailed information about entities like IPs, domains, or file hashes:

```bash
secops entity --value "8.8.8.8" --time-window 24
secops entity --value "example.com" --time-window 24
secops entity --value "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" --time-window 24
```

### Indicators of Compromise (IoCs)

List IoCs in your environment:

```bash
secops iocs --time-window 24 --max-matches 50
secops iocs --time-window 24 --prioritized --mandiant
```

### Log Ingestion

Ingest raw logs:

```bash
secops log ingest --type "OKTA" --file "/path/to/okta_logs.json"
secops log ingest --type "WINDOWS" --message "{\"event\": \"data\"}"
```

Add custom labels to your logs:
```bash
# Using JSON format
secops log ingest --type "OKTA" --file "/path/to/okta_logs.json" --labels '{"environment": "production", "source": "web-portal"}'

# Using key=value pairs
secops log ingest --type "WINDOWS" --file "/path/to/windows_logs.xml" --labels "environment=test,team=security,version=1.0"
```

Ingest UDM events:

```bash
secops log ingest-udm --file "/path/to/udm_event.json"
```

List available log types:

```bash
# List all log types
secops log types

# Search for specific log types
secops log types --search "windows"

# Fetch specific page using token
secops log types --page-size 50 --page-token "next_page_token"

# Classify logs to predict log type:
secops log classify --log '{"eventType": "user.session.start", "actor": {"alternateId": "user@example.com"}}'

# Classify a log from a file
secops log classify --log /path/to/log_file.json
```

> **Note:** The classify command returns predictions sorted by confidence score. Confidence scores are provided by the API as guidance only and may not always accurately reflect classification certainty. Use scores for relative ranking rather than absolute confidence.

> **Note:** Chronicle uses parsers to process and normalize raw log data into UDM format. If you're ingesting logs for a custom format, you may need to create or configure parsers. See the [Parser Management](#parser-management) section for details on managing parsers.

### Forwarder Management

Log forwarders in Chronicle are used to ingest logs with specific configurations. The CLI provides commands for creating and managing forwarders.

#### Create a new forwarder:

```bash
# Create a basic forwarder
secops forwarder create --display-name "my-custom-forwarder"

# Create a forwarder with metadata and http settings
secops forwarder create --display-name "my-forwarder" --metadata '{"environment":"prod","team":"security"}' --upload-compression true --enable-server true --http-settings '{"port":80,"host":"example.com"}'
```

#### List all forwarders:

```bash
# List forwarders with default page size (50)
secops forwarder list

# List forwarders with custom page size
secops forwarder list --page-size 100
```

#### Get forwarder details:

```bash
# Get a specific forwarder by ID
secops forwarder get --id "1234567890"
```

#### Get or create a forwarder:

```bash
# Get an existing forwarder by display name or create a new one if it doesn't exist
secops forwarder get-or-create --display-name "my-app-forwarder"
```

#### Update a forwarder:

```bash
# Update a forwarder's display name
secops forwarder update --id "1234567890" --display-name "updated-forwarder-name"

# Update a forwarder with multiple properties
secops forwarder update --id "1234567890" --display-name "prod-forwarder" --upload-compression true --http-settings '{"port":80,"host":"example.com"}'

# Update specific fields using update mask
secops forwarder update --id "1234567890" --display-name "prod-forwarder" --update-mask "display_name"
```

#### Delete a forwarder:

```bash
# Delete a forwarder by ID
secops forwarder delete --id "1234567890"
```

### Generate UDM Key/Value Mapping

Generate UDM key/value mapping for provided row log

```bash
secops log generate-udm-mapping \ 
--log-format "JSON" \
--log '{"events":[{"id":"123","user":"test_user","source_ip":"192.168.1.10"}]}' \
--use-array-bracket-notation "true" \
--compress-array-fields "false"
```

### Log Processing Pipelines

Chronicle log processing pipelines allow you to transform, filter, and enrich log data before it is stored in Chronicle. Common use cases include removing empty key-value pairs, redacting sensitive data, adding ingestion labels, filtering logs by field values, and extracting host information. Pipelines can be associated with log types (with optional collector IDs) and feeds, providing flexible control over your data ingestion workflow.

The CLI provides comprehensive commands for managing pipelines, associating streams, testing configurations, and fetching sample logs.

#### List pipelines

```bash
# List all log processing pipelines
secops log-processing list

# List with pagination
secops log-processing list --page-size 50

# List with filter expression
secops log-processing list --filter "displayName:production*"

# List with pagination token
secops log-processing list --page-size 50 --page-token "next_page_token"
```

#### Get pipeline details

```bash
# Get a specific pipeline by ID
secops log-processing get --id "1234567890"
```

#### Create a pipeline

```bash
# Create from inline JSON
secops log-processing create --pipeline '{"displayName":"My Pipeline","description":"Filters error logs","processors":[{"filterProcessor":{"include":{"logMatchType":"REGEXP","logBodies":[".*error.*"]},"errorMode":"IGNORE"}}]}'
```

# Create from JSON file
secops log-processing create --pipeline pipeline_config.json

Example `pipeline_config.json`:
```json
{
  "displayName": "Production Pipeline",
  "description": "Filters and transforms production logs",
  "processors": [
    {
      "filterProcessor": {
        "include": {
          "logMatchType": "REGEXP",
          "logBodies": [".*error.*", ".*warning.*"]
        },
        "errorMode": "IGNORE"
      }
    }
  ],
  "customMetadata": [
    {"key": "environment", "value": "production"},
    {"key": "team", "value": "security"}
  ]
}
```

#### Update a pipeline

```bash
# Update from JSON file with update mask
secops log-processing update --id "1234567890" --pipeline updated_config.json --update-mask "description"

# Update from inline JSON
secops log-processing update --id "1234567890" --pipeline '{description":"Updated description"}' --update-mask "description"
```

#### Delete a pipeline

```bash
# Delete a pipeline by ID
secops log-processing delete --id "1234567890"

# Delete with etag for concurrency control
secops log-processing delete --id "1234567890" --etag "etag_value"
```

#### Associate streams with a pipeline

Associate log streams (by log type or feed) with a pipeline:

```bash
# Associate by log type (inline)
secops log-processing associate-streams --id "1234567890" --streams '[{"logType":"WINEVTLOG"},{"logType":"LINUX"}]'

# Associate by feed ID
secops log-processing associate-streams --id "1234567890" --streams '[{"feed":"feed-uuid-1"},{"feed":"feed-uuid-2"}]'

# Associate by log type (from file)
secops log-processing associate-streams --id "1234567890" --streams streams.json
```

Example `streams.json`:
```json
[
  {"logType": "WINEVTLOG"},
  {"logType": "LINUX"},
  {"logType": "OKTA"}
]
```

#### Dissociate streams from a pipeline

```bash
# Dissociate streams (from file)
secops log-processing dissociate-streams --id "1234567890" --streams streams.json

# Dissociate streams (inline)
secops log-processing dissociate-streams --id "1234567890" --streams '[{"logType":"WINEVTLOG"}]'
```

#### Fetch associated pipeline

Find which pipeline is associated with a specific stream:

```bash
# Find pipeline for a log type (inline)
secops log-processing fetch-associated --stream '{"logType":"WINEVTLOG"}'

# Find pipeline for a feed
secops log-processing fetch-associated --stream '{"feed":"feed-uuid"}'

# Find pipeline for a log type (from file)
secops log-processing fetch-associated --stream stream_query.json
```

Example `stream_query.json`:
```json
{
  "logType": "WINEVTLOG"
}
```

#### Fetch sample logs

Retrieve sample logs for specific streams:

```bash
# Fetch sample logs for log types (from file)
secops log-processing fetch-sample-logs --streams streams.json --count 10

# Fetch sample logs (inline)
secops log-processing fetch-sample-logs --streams '[{"logType":"WINEVTLOG"},{"logType":"LINUX"}]' --count 5

# Fetch sample logs for feeds
secops log-processing fetch-sample-logs --streams '[{"feed":"feed-uuid"}]' --count 10
```

#### Test a pipeline

Test a pipeline configuration against sample logs before deployment:

```bash
# Test with inline JSON
secops log-processing test --pipeline '{"displayName":"Test","processors":[{"filterProcessor":{"include":{"logMatchType":"REGEXP","logBodies":[".*"]},"errorMode":"IGNORE"}}]}' --input-logs input_logs.json

# Test with files
secops log-processing test --pipeline pipeline_config.json --input-logs test_logs.json
```

Example `input_logs.json` (logs must have base64-encoded data):
```json
[
  {
    "data": "U2FtcGxlIGxvZyBlbnRyeQ==",
    "logEntryTime": "2024-01-01T00:00:00Z",
    "collectionTime": "2024-01-01T00:00:00Z"
  },
  {
    "data": "QW5vdGhlciBsb2cgZW50cnk=",
    "logEntryTime": "2024-01-01T00:01:00Z",
    "collectionTime": "2024-01-01T00:01:00Z"
  }
]
```

### Parser Management

Parsers in Chronicle are used to process and normalize raw log data into UDM (Unified Data Model) format. The CLI provides comprehensive parser management capabilities.

#### List parsers:

```bash
# List all parsers
secops parser list

# List parsers for a specific log type
secops parser list --log-type "WINDOWS"

# List with pagination and filtering
secops parser list --log-type "OKTA" --page-size 50 --filter "state=ACTIVE"
```

#### Get parser details:

```bash
secops parser get --log-type "WINDOWS" --id "pa_12345"
```

#### Fetch parser candidates:

```bash
secops parser fetch-candidates --log-type "WINDOWS_DHCP" --parser-action "PARSER_ACTION_OPT_IN_TO_PREVIEW"
```

#### Create a new parser:

```bash
# Create from parser code string
secops parser create --log-type "CUSTOM_LOG" --parser-code "filter { mutate { add_field => { \"test\" => \"value\" } } }"

# Create from parser code file
secops parser create --log-type "CUSTOM_LOG" --parser-code-file "/path/to/parser.conf" --validated-on-empty-logs
```

#### Copy a prebuilt parser:

```bash
secops parser copy --log-type "WINDOWS" --id "pa_prebuilt_123"
```

#### Activate a parser:

```bash
# Activate a custom parser
secops parser activate --log-type "WINDOWS" --id "pa_12345"

# Activate a release candidate parser
secops parser activate-rc --log-type "WINDOWS" --id "pa_67890"
```

#### Deactivate a parser:

```bash
secops parser deactivate --log-type "WINDOWS" --id "pa_12345"
```

#### Delete a parser:

```bash
# Delete an inactive parser
secops parser delete --log-type "WINDOWS" --id "pa_12345"

# Force delete an active parser
secops parser delete --log-type "WINDOWS" --id "pa_12345" --force
```

#### Run a parser against sample logs:

The `parser run` command allows you to test a parser against sample log entries before deploying it. This is useful for validating parser logic and ensuring it correctly processes your log data.

```bash
# Run a parser against sample logs using inline arguments
secops parser run \
  --log-type AZURE_AD \
  --parser-code-file "./parser.conf" \
  --log '{"message": "Test log 1"}' \
  --log '{"message": "Test log 2"}' \
  --log '{"message": "Test log 3"}'

# Run a parser against logs from a file (one log per line)
secops parser run \
  --log-type WINDOWS \
  --parser-code-file "./parser.conf" \
  --logs-file "./sample_logs.txt"

# Run a parser with an extension
secops parser run \
  --log-type CUSTOM_LOG \
  --parser-code-file "./parser.conf" \
  --parser-extension-code-file "./extension.conf" \
  --logs-file "./logs.txt" \
  --statedump-allowed

# Run with inline parser code
secops parser run \
  --log-type OKTA \
  --parser-code 'filter { mutate { add_field => { "test" => "value" } } }' \
  --log '{"user": "john.doe", "action": "login"}'

# Run the active parser on a set of logs
secops parser run \
  --log-type OKTA \
  --logs-file "./test.log"

# Run parser with statedump for debugging (outputs readable parser state)
secops parser run \
  --log-type WINEVTLOG \
  --parser-code-file "./parser.conf" \
  --logs-file "./logs.txt" \
  --statedump-allowed \
  --parse-statedump
```

The `--statedump-allowed` flag enables statedump output in the parser results, which shows the internal state of the parser during execution. The `--parse-statedump` flag converts the statedump string into a structured JSON format.

The command validates:
- Log type and parser code are provided
- At least one log is provided
- Log sizes don't exceed limits (10MB per log, 50MB total)
- Maximum 1000 logs can be processed at once

Error messages are detailed and help identify issues:
- Invalid log types
- Parser syntax errors  
- Size limit violations
- API-specific errors

#### Parser Validation

You can trigger and retrieve analysis reports for parsers associated with GitHub pull requests.

Trigger GitHub checks for a parser:

```bash
secops log-type trigger-checks --log-type "WINDOWS_AD" --associated-pr "owner/repo/pull/123"
```

Get a parser analysis report:

```bash
secops log-type get-analysis-report --log-type "WINDOWS_AD" --parser-id "pa_12345" --report-id "report_12345"
```

### Parser Extension Management

Parser extensions provide a flexible way to extend the capabilities of existing default (or custom) parsers without replacing them.

#### List Parser Extensions
```bash
secops parser-extension list --log-type OKTA

# Provide pagination parameters
secops parser-extension list --log-type OKTA --page-size 50 --page-token "token"
```

#### Create new parser extension
```bash
# With sample log and parser config file (CBN Snippet)
secops parser-extension create --log-type OKTA \
--log /path/to/sample.log \
--parser-config-file /path/to/parser-config.conf

# With parser config file (CBN Snippet) string
secops parser-extension create --log-type OKTA \
--log '{\"sample\":{}}'
--parser-config 'filter {}'

# With field extractor config file
secops parser-extension create --log-type OKTA \
--field-extractor '{\"extractors\":[{}],\"logFormat\":\"JSON\",\"appendRepeatedFields\":true}'
```

#### Get parser extension details
```bash
secops parser-extension get --log-type OKTA --id "1234567890"
```

#### Activate parser extension
```bash
secops parser-extension activate --log-type OKTA --id "1234567890"
```

#### Delete parser extension
```bash
secops parser-extension delete --log-type OKTA --id "1234567890"
```

### Watchlist Management

List watchlists:

```bash
# List all watchlists (returns dict with pagination metadata)
secops watchlist list

# List watchlists as a direct list (fetches all pages automatically)
secops watchlist list --as-list

# List watchlist with pagination 
secops watchlist list --page-size 50
```

Get watchlist details:

```bash
secops watchlist get --watchlist-id "abc-123-def"
```

Create a new watchlist:

```bash
secops watchlist create --name "my_watchlist" --display-name "my_watchlist" --description "My watchlist description" --multiplying-factor 1.5
```

Update a watchlist:

```bash
# Update display name and description
secops watchlist update --watchlist-id "abc-123-def" --display-name "Updated Name" --description "Updated description"

# Update multiplying factor and pin the watchlist
secops watchlist update --watchlist-id "abc-123-def" --multiplying-factor 2.0 --pinned true

# Update entity population mechanism (JSON string or file path)
secops watchlist update --watchlist-id "abc-123-def" --entity-population-mechanism '{"manual": {}}'
```

Delete a watchlist:

```bash
secops watchlist delete --watchlist-id "abc-123-def"
```

### Integration Management

#### Marketplace Integrations

List marketplace integrations:

```bash
# List all marketplace integration (returns dict with pagination metadata)
secops integration marketplace list

# List marketplace integration as a direct list (fetches all pages automatically)
secops integration marketplace list --as-list
```

Get marketplace integration details:

```bash
secops integration marketplace get --integration-name "AWSSecurityHub"
```

Get marketplace integration diff between installed version and latest version:

```bash
secops integration marketplace diff --integration-name "AWSSecurityHub"
```

Install or update a marketplace integration:

```bash
# Install with default settings
secops integration marketplace install --integration-name "AWSSecurityHub"

# Install to staging environment and override any existing ontology mappings
secops integration marketplace install --integration-name "AWSSecurityHub" --staging --override-mapping

# Installing a currently installed integration with no specified version 
# number will update it to the latest version
secops integration marketplace install --integration-name "AWSSecurityHub"

# Or you can specify a specific version to install
secops integration marketplace install --integration-name "AWSSecurityHub" --version "5.0"
```

Uninstall a marketplace integration:

```bash
secops integration marketplace uninstall --integration-name "AWSSecurityHub"
```

#### Integrations

List integrations:

```bash
# List all integrations
secops integration integrations list

# List integrations as a direct list
secops integration integrations list --as-list

# List with pagination
secops integration integrations list --page-size 50

# List with filtering
secops integration integrations list --filter-string "displayName = 'CrowdStrike'"

# List with ordering
secops integration integrations list --order-by "displayName"
```

Get integration details:

```bash
secops integration integrations get --integration-id "MyIntegration"
```

Create a new custom integration:

```bash
# Create a basic integration
secops integration integrations create --display-name "My Custom Integration"

# Create in staging mode
secops integration integrations create \
  --display-name "My Custom Integration" \
  --staging

# Create with all options
secops integration integrations create \
  --display-name "My Custom Integration" \
  --description "Custom integration for internal tooling" \
  --python-version "V3_11" \
  --integration-type "RESPONSE" \
  --staging
```

Update an integration:

```bash
# Update display name
secops integration integrations update \
  --integration-id "MyIntegration" \
  --display-name "Updated Integration Name"

# Update multiple fields
secops integration integrations update \
  --integration-id "MyIntegration" \
  --display-name "Updated Name" \
  --description "Updated description" \
  --python-version "V3_11"

# Update with explicit update mask
secops integration integrations update \
  --integration-id "MyIntegration" \
  --display-name "New Name" \
  --update-mask "displayName"

# Remove dependencies during update
secops integration integrations update \
  --integration-id "MyIntegration" \
  --dependencies-to-remove "old-package" "unused-lib"

# Set integration to staging mode
secops integration integrations update \
  --integration-id "MyIntegration" \
  --staging
```

Update a custom integration definition:

```bash
# Update a custom integration (supports parameters and dependencies)
secops integration integrations update-custom \
  --integration-id "MyIntegration" \
  --display-name "Updated Custom Integration" \
  --description "Updated custom integration"

# Update with all options
secops integration integrations update-custom \
  --integration-id "MyIntegration" \
  --display-name "Updated Custom Integration" \
  --python-version "V3_11" \
  --integration-type "EXTENSION" \
  --dependencies-to-remove "old-dep" \
  --staging
```

Delete an integration:

```bash
secops integration integrations delete --integration-id "MyIntegration"
```

Download an integration package:
#### Integration Actions

List integration actions:

```bash
# List all actions for an integration
secops integration actions list --integration-name "MyIntegration"

# List actions as a direct list (fetches all pages automatically)
secops integration actions list --integration-name "MyIntegration" --as-list

# List with pagination
secops integration actions list --integration-name "MyIntegration" --page-size 50

# List with filtering
secops integration actions list --integration-name "MyIntegration" --filter-string "enabled = true"
```

Get action details:

```bash
secops integration actions get --integration-name "MyIntegration" --action-id "123"
```

Create a new action:

```bash
# Create a basic action with Python code
secops integration actions create \
  --integration-name "MyIntegration" \
  --display-name "Send Alert" \
  --code "def main(context): return {'status': 'success'}"

# Create an async action
secops integration actions create \
  --integration-name "MyIntegration" \
  --display-name "Async Task" \
  --code "async def main(context): return await process()" \
  --is-async

# Create with description
secops integration actions create \
  --integration-name "MyIntegration" \
  --display-name "My Action" \
  --code "def main(context): return {}" \
  --description "Action description"
```

> **Note:** When creating an action, the following default values are automatically applied:
> - `timeout_seconds`: 300 (5 minutes)
> - `enabled`: true
> - `script_result_name`: "result"
> 
> The `--code` parameter contains the Python script that will be executed by the action.

Update an existing action:

```bash
# Update display name
secops integration actions update \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --display-name "Updated Action Name"

# Update code
secops integration actions update \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --code "def main(context): return {'status': 'updated'}"

# Update multiple fields with update mask
secops integration actions update \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --display-name "New Name" \
  --description "New description" \
  --update-mask "displayName,description"
```

Delete an action:

```bash
secops integration actions delete --integration-name "MyIntegration" --action-id "123"
```

Test an action:

```bash
# Test an action to verify it executes correctly
secops integration actions test --integration-name "MyIntegration" --action-id "123"
```

Get action template:

```bash
# Get synchronous action template
secops integration actions template --integration-name "MyIntegration"

# Get asynchronous action template
secops integration actions template --integration-name "MyIntegration" --is-async
```

#### Action Revisions

List action revisions:

```bash
# List all revisions for an action
secops integration action-revisions list \
  --integration-name "MyIntegration" \
  --action-id "123"

# List revisions as a direct list
secops integration action-revisions list \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --as-list

# List with pagination
secops integration action-revisions list \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --page-size 10

# List with filtering and ordering
secops integration action-revisions list \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --filter-string 'version = "1.0"' \
  --order-by "createTime desc"
```

Create a revision backup:

```bash
# Create revision with comment
secops integration action-revisions create \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --comment "Backup before major refactor"

# Create revision without comment
secops integration action-revisions create \
  --integration-name "MyIntegration" \
  --action-id "123"
```

Rollback to a previous revision:

```bash
secops integration action-revisions rollback \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --revision-id "r456"
```

Delete an old revision:

```bash
secops integration action-revisions delete \
  --integration-name "MyIntegration" \
  --action-id "123" \
  --revision-id "r789"
```

#### Integration Managers

List integration managers:

```bash
# Download integration as a ZIP file
secops integration integrations download \
  --integration-id "MyIntegration" \
  --output-file "/tmp/my-integration.zip"
```

Download a Python dependency for a custom integration:

```bash
# Download a specific dependency
secops integration integrations download-dependency \
  --integration-id "MyIntegration" \
  --dependency-name "requests==2.31.0"
```

Export specific items from an integration:

```bash
# Export specific actions and connectors
secops integration integrations export-items \
  --integration-id "MyIntegration" \
  --output-file "/tmp/export.zip" \
  --actions "action1" "action2" \
  --connectors "connector1"

# Export jobs and managers
secops integration integrations export-items \
  --integration-id "MyIntegration" \
  --output-file "/tmp/export.zip" \
  --jobs "job1" "job2" \
  --managers "manager1"

# Export transformers and logical operators
secops integration integrations export-items \
  --integration-id "MyIntegration" \
  --output-file "/tmp/export.zip" \
  --transformers "t1" \
  --logical-operators "lo1" "lo2"
```

Get items affected by changes to an integration:

```bash
secops integration integrations affected-items --integration-id "MyIntegration"
```

Get integrations installed on a specific agent:

```bash
secops integration integrations agent-integrations --agent-id "my-agent-id"
```

Get Python dependencies for a custom integration:

```bash
secops integration integrations dependencies --integration-id "MyIntegration"
```

Get agents restricted from running an updated integration:

```bash
# Check restricted agents for a Python version upgrade
secops integration integrations restricted-agents \
  --integration-id "MyIntegration" \
  --required-python-version "V3_11"

# Check restricted agents for a push request
secops integration integrations restricted-agents \
  --integration-id "MyIntegration" \
  --required-python-version "V3_11" \
  --push-request
```

Get the configuration diff for an integration:

```bash
# Get diff against marketplace version (default)
secops integration integrations diff --integration-id "MyIntegration"

# Get diff between staging and production
secops integration integrations diff \
  --integration-id "MyIntegration" \
  --diff-type "Production"

# Get diff between production and staging
secops integration integrations diff \
  --integration-id "MyIntegration" \
  --diff-type "Staging"
```

Transition an integration between staging and production:

```bash
# Push integration to production
secops integration integrations transition \
  --integration-id "MyIntegration" \
  --target-mode "Production"

# Push integration to staging
secops integration integrations transition \
  --integration-id "MyIntegration" \
  --target-mode "Staging"
```

Example workflow: Create, configure, test, and deploy a custom integration:

```bash
# 1. Create a new custom integration in staging
secops integration integrations create \
  --display-name "My Custom SIEM Connector" \
  --description "Custom connector for internal SIEM" \
  --python-version "V3_11" \
  --integration-type "RESPONSE" \
  --staging

# 2. Check its dependencies
secops integration integrations dependencies \
  --integration-id "MyCustomSIEMConnector"

# 3. View the diff before pushing to production
secops integration integrations diff \
  --integration-id "MyCustomSIEMConnector" \
  --diff-type "Production"

# 4. Check for restricted agents
secops integration integrations restricted-agents \
  --integration-id "MyCustomSIEMConnector" \
  --required-python-version "V3_11" \
  --push-request

# 5. Push to production
secops integration integrations transition \
  --integration-id "MyCustomSIEMConnector" \
  --target-mode "Production"

# 6. Download a backup
secops integration integrations download \
  --integration-id "MyCustomSIEMConnector" \
  --output-file "/tmp/my-siem-connector-backup.zip"

# 7. Export specific items for sharing
secops integration integrations export-items \
  --integration-id "MyCustomSIEMConnector" \
  --output-file "/tmp/siem-actions.zip" \
  --actions "PingAction" "FetchEvents"
```

#### Integration Instances

List integration instances:

```bash
# List all instances for an integration
secops integration instances list --integration-name "MyIntegration"

# List instances as a direct list (fetches all pages automatically)
secops integration instances list --integration-name "MyIntegration" --as-list

# List with pagination
secops integration instances list --integration-name "MyIntegration" --page-size 50

# List with filtering
secops integration instances list --integration-name "MyIntegration" --filter-string "enabled = true"
```

Get integration instance details:

```bash
secops integration instances get \
  --integration-name "MyIntegration" \
  --instance-id "inst123"
```

Create a new integration instance:

```bash
# Create basic integration instance
secops integration instances create \
  --integration-name "MyIntegration" \
  --display-name "Production Instance" \
  --environment "production"

# Create with description and custom ID
secops integration instances create \
  --integration-name "MyIntegration" \
  --display-name "Test Instance" \
  --environment "test" \
  --description "Testing environment instance" \
  --instance-id "test-inst-001"

# Create with configuration
secops integration instances create \
  --integration-name "MyIntegration" \
  --display-name "Configured Instance" \
  --environment "production" \
  --config '{"api_key":"secret123","region":"us-east1"}'
```

Update an integration instance:

```bash
# Update display name
secops integration instances update \
  --integration-name "MyIntegration" \
  --instance-id "inst123" \
  --display-name "Updated Instance Name"

# Update configuration
secops integration instances update \
  --integration-name "MyIntegration" \
  --instance-id "inst123" \
  --config '{"api_key":"newsecret456","region":"us-west1"}'

# Update multiple fields with update mask
secops integration instances update \
  --integration-name "MyIntegration" \
  --instance-id "inst123" \
  --display-name "New Name" \
  --description "New description" \
  --update-mask "displayName,description"
```

Delete an integration instance:

```bash
secops integration instances delete \
  --integration-name "MyIntegration" \
  --instance-id "inst123"
```

Test an integration instance:

```bash
# Test the instance configuration
secops integration instances test \
  --integration-name "MyIntegration" \
  --instance-id "inst123"
```

Get affected items:

```bash
# Get items affected by this instance
secops integration instances get-affected-items \
  --integration-name "MyIntegration" \
  --instance-id "inst123"
```

Get default instance:

```bash
# Get the default integration instance
secops integration instances get-default \
  --integration-name "MyIntegration"
```

### Rule Management

List detection rules:

```bash
# List all rules
secops rule list

# List rule with pagination and specified view scope
secops rule list --page-size 50 --view 'REVISION_METADATA_ONLY'
```

Get rule details:

```bash
secops rule get --id "ru_12345"
```

Create a new rule:

```bash
secops rule create --file "/path/to/rule.yaral"
```

Update an existing rule:

```bash
secops rule update --id "ru_12345" --file "/path/to/updated_rule.yaral"
```

Enable or disable a rule:

```bash
secops rule enable --id "ru_12345" --enabled true
secops rule enable --id "ru_12345" --enabled false
```

Delete a rule:

```bash
secops rule delete --id "ru_12345"
secops rule delete --id "ru_12345" --force
```

List rule deployments:

```bash
# List all rule deployments
secops rule list-deployments

# List deployments with pagination
secops rule list-deployments --page-size 10 --page-token "token"

# List deployments with filter
secops rule list-deployments --filter "enabled=true"
```

Get rule deployment details:

```bash
secops rule get-deployment --id "ru_12345"
```

Update rule deployment:

```bash
# Enable or disable a rule
secops rule update-deployment --id "ru_12345" --enabled true
secops rule update-deployment --id "ru_12345" --enabled false

# Update multiple properties
secops rule update-deployment --id "ru_12345" --enabled true --alerting true --run-frequency HOURLY
```

Manage rule alerting:

```bash
# Enable alerting for a rule
secops rule alerting --id "ru_12345" --enabled true

# Disable alerting for a rule
secops rule alerting --id "ru_12345" --enabled false
```

Validate a rule:

```bash
secops rule validate --file "/path/to/rule.yaral"
```

Search for rules using regex patterns:

```bash
secops rule search --query "suspicious process"
secops rule search --query "MITRE.*T1055"
```

Test a rule against historical data:

```bash
# Test a rule with default result limit (100) for the last 24 hours
secops rule test --file "/path/to/rule.yaral" --time-window 24

# Test with custom time range and higher result limit
secops rule test --file "/path/to/rule.yaral" --start-time "2023-07-01T00:00:00Z" --end-time "2023-07-02T00:00:00Z" --max-results 1000

# Output UDM events as JSON and save to a file for further processing
secops rule test --file "/path/to/rule.yaral" --time-window 24 > udm_events.json
```

The `rule test` command outputs UDM events as pure JSON objects that can be piped to a file or processed by other tools. This makes it easy to integrate with other systems or perform additional analysis on the events.

### Curated Rule Set Management

List all curated rules:

```bash
# List all curated rules (returns dict with pagination metadata)
secops curated-rule rule list

# List curated rules as a direct list
secops curated-rule rule list --as-list
```

Get curated rules:

```bash
# Get rule by UUID
secops curated-rule rule get --id "ur_ttp_GCP_ServiceAPIDisable"

# Get rule by name
secops curated-rule rule get --name "GCP Service API Disable"
```

Search for curated rule detections:

```bash
secops curated-rule search-detections \
  --rule-id "ur_ttp_GCP_MassSecretDeletion" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-31T23:59:59Z" \
  --list-basis "DETECTION_TIME" \
  --alert-state "ALERTING"

# Search with pagination
secops curated-rule search-detections \
  --rule-id "ur_ttp_GCP_MassSecretDeletion" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-31T23:59:59Z" \
  --list-basis "DETECTION_TIME" \
  --page-size 50

```

List all curated rule sets:

```bash
# List all curated rule sets (returns dict with pagination metadata)
secops curated-rule rule-set list

# List curated rule sets as a direct list
secops curated-rule rule-set list --as-list
```

Get specific curated rule set details:

```bash
# Get curated rule set by UUID
secops curated-rule rule-set get --id "f5533b66-9327-9880-93e6-75a738ac2345"

# Get curated rule set by name
secops curated-rule rule-set get --name "Active Breach Priority Host Indicators"
```

List all curated rule set categories:

```bash
# List all curated rule set categories (returns dict with pagination metadata)
secops curated-rule rule-set-category list

# List curated rule set categories as a direct list
secops curated-rule rule-set-category list --as-list
```

Get specific curated rule set category details:

```bash
# Get curated rule set category by UUID
secops curated-rule rule-set-category get --id "db1114d4-569b-5f5d-0fb4-f65aaa766c92"
```

List all curated rule set deployments:

```bash
# List all curated rule set deployments (returns dict with pagination metadata)
secops curated-rule rule-set-deployment list

# List curated rule set deployments as a direct list
secops curated-rule rule-set-deployment list --as-list
```

Get specific curated rule set deployment details:

```bash
# Get curated rule set deployment by UUID
secops curated-rule rule-set-deployment get --id "f5533b66-9327-9880-93e6-75a738ac2345"

# Get curated rule set deployment by name
secops curated-rule rule-set-deployment get --name "Active Breach Priority Host Indicators"
```

Update curated rule set deployment:
```bash
secops curated-rule rule-set-deployment update --category-id "db1114d4-569b-5f5d-0fb4-f65aaa766c92" --rule-set-id "7e52cd71-03c6-97d2-ffcb-b8d7159e08e1" --precision precise --enabled false --alerting false
```

### Alert Management

Get alerts:

```bash
secops alert --time-window 24 --max-alerts 50
secops alert --snapshot-query "feedback_summary.status != \"CLOSED\"" --time-window 24
secops alert --baseline-query "detection.rule_name = \"My Rule\"" --time-window 24
```

### Rule Retrohunt Management

List all retrohunts for a rule
```bash
secops rule-retrohunt list --rule-id "ru_abcdef"
```

Create a new retrohunt for a rule
```bash
secops rule-retrohunt create --rule-id "ru_abcdef" --start-time "2026-01-01T00:00:00Z" --end-time "2026-01-02T00:00:00Z"
```

Get specific retrohunt details
```bash
secops rule-retrohunt get --rule-id "ru_abcdef" --operation-id "oh_abcdef"
```

### Rule Exclusions Management

Rule Exclusions allow you to exclude specific events from triggering detections in Chronicle. Use these commands to manage rule exclusions and their deployments:

List all rule exclusions
```bash
secops rule-exclusion list
```

Get specific rule exclusion details
```bash
secops rule-exclusion get --id "exclusion-id"
```

Create new rule exclusion (aka findings refinement)
```bash
secops rule-exclusion create \
  --display-name "Test Exclusion" \
  --type "DETECTION_EXCLUSION" \
  --query '(ip="8.8.8.8")'
```

Update rule exclusion
```bash
secops rule-exclusion update \
  --id "exclusion-id" \
  --display-name "Updated Exclusion" \
  --query '(domain="googl.com")' \
  --update-mask "display_name,query"
```

Get rule exclusion deployment details
```bash
secops rule-exclusion get-deployment --id "exclusion-id"
```

Update rule exclusion deployment
```bash
secops rule-exclusion update-deployment \
  --id "exclusion-id" \
  --enabled true \
  --archived false \
  --detection-exclusion-application '"{\"curatedRules\": [],\"curatedRuleSets\": [],\"rules\": []}'
```
Compute rule exclusion activity for specific exclusion
```bash
secops rule-exclusion compute-activity \
  --id "exclusion-id" \
  --time-window 168
```

### Case Management

Chronicle also provides comprehensive case management capabilities for tracking and managing security investigations. The CLI supports listing, retrieving, updating, and performing bulk operations on cases.

Get case details for specific case IDs:

```bash
secops case --ids "case-123,case-456"
```

Get case details from alert results:

```bash
# First get alerts
secops alert --time-window 24 --max-alerts 50 > alerts.json

# Extract case IDs and retrieve case details
# Example: if alerts contain case IDs case-123 and case-456
secops case --ids "case-123,case-456"
```

> **Note**: You can provide up to 1000 case IDs separated by commas.

#### List cases

```bash
# List all cases with default pagination
secops case list --page-size 50

# List with filtering
secops case list --page-size 100 --filter 'status = "OPENED"' --order-by "createTime desc"

# Get cases as a flat list instead of paginated dict
secops case list --page-size 50 --as-list
```

#### Get case details

```bash
# Get a specific case by ID
secops case get --id "12345"

# Get case with expanded fields
secops case get --id "12345" --expand "tags,products"

# Legacy: Get multiple cases by IDs (batch API)
secops case --ids "case-123,case-456"
```

> **Note**: The legacy batch API can retrieve up to 1000 case IDs in a single request.

#### Update a case

```bash
# Update case priority
secops case update --id "12345" --data '{"priority": "PRIORITY_HIGH"}' --update-mask "priority"

# Update multiple fields
secops case update --id "12345" --data '{"priority": "PRIORITY_MEDIUM", "stage": "Investigation"}' --update-mask "priority,stage"
```

#### Merge cases

```bash
# Merge source cases into target case
secops case merge --source-ids "12345,67890" --target-id "11111"
```

#### Bulk operations

```bash
# Bulk add tags to cases
secops case bulk-add-tag --ids "12345,67890" --tags "phishing,high-priority"

# Bulk assign cases to a user
secops case bulk-assign --ids "12345,67890" --username "@SecurityTeam"

# Bulk change priority
secops case bulk-change-priority --ids "12345,67890" --priority "HIGH"

# Bulk change stage
secops case bulk-change-stage --ids "12345,67890" --stage "Remediation"

# Bulk close cases
secops case bulk-close --ids "12345,67890" --close-reason "NOT_MALICIOUS" --root-cause "False positive - benign activity"

# Bulk reopen cases
secops case bulk-reopen --ids "12345,67890" --reopen-comment "New evidence discovered"
```

### Investigation Management

Chronicle investigations provide automated analysis and recommendations for alerts and cases. Use these commands to list, retrieve, trigger, and fetch associated investigations.

#### List investigations

```bash
# List all investigations
secops investigation list

# List with pagination
secops investigation list --page-size 50

# List with pagination token
secops investigation list --page-size 50 --page-token "token"
```

#### Get investigation details

```bash
# Get a specific investigation by ID
secops investigation get --id "inv_123"
```

#### Trigger investigation for an alert

```bash
# Trigger an investigation for a specific alert
secops investigation trigger --alert-id "alert_123"
```

#### Fetch associated investigations

```bash
# Fetch investigations associated with specific alerts
secops investigation fetch-associated \
  --detection-type "ALERT" \
  --alert-ids "alert_123,alert_456" \
  --association-limit 5

# Fetch investigations associated with a case
secops investigation fetch-associated \
  --detection-type "CASE" \
  --case-ids "case_123"

# Fetch with ordering
secops investigation fetch-associated \
  --detection-type "ALERT" \
  --alert-ids "alert_123" \
  --order-by "createTime desc"
```

### Data Export

List available log types for export:

```bash
secops export log-types --time-window 24
secops export log-types --page-size 50
```

List recent data exports:

```bash
# List all recent exports
secops export list

# List with pagination
secops export list --page-size 10
```

Create a data export:

```bash
# Export a single log type (legacy method)
secops export create --gcs-bucket "projects/my-project/buckets/my-bucket" --log-type "WINDOWS" --time-window 24

# Export multiple log types
secops export create --gcs-bucket "projects/my-project/buckets/my-bucket" --log-types "WINDOWS,LINUX,GCP_DNS" --time-window 24

# Export all log types
secops export create --gcs-bucket "projects/my-project/buckets/my-bucket" --all-logs --time-window 24

# Export with explicit start and end times
secops export create --gcs-bucket "projects/my-project/buckets/my-bucket" --all-logs --start-time "2025-01-01T00:00:00Z" --end-time "2025-01-02T00:00:00Z"
```

Check export status:

```bash
secops export status --id "export-123"
```

Update an export (only for exports in IN_QUEUE state):

```bash
# Update start time
secops export update --id "export-123" --start-time "2025-01-01T02:00:00Z"

# Update log types
secops export update --id "export-123" --log-types "WINDOWS,LINUX,AZURE"

# Update the GCS bucket
secops export update --id "export-123" --gcs-bucket "projects/my-project/buckets/my-new-bucket"
```

Cancel an export:

```bash
secops export cancel --id "export-123"
```

### Gemini AI

Query Gemini AI for security insights:

```bash
secops gemini --query "What is Windows event ID 4625?"
secops gemini --query "Write a rule to detect PowerShell downloading files" --raw
secops gemini --query "Tell me about CVE-2021-44228" --conversation-id "conv-123"
```

Explicitly opt-in to Gemini:

```bash
secops gemini --opt-in
```

### Data Tables

Data Tables are collections of structured data that can be referenced in detection rules.

#### List data tables:

```bash
secops data-table list
secops data-table list --order-by "createTime asc"
```

#### Get data table details:

```bash
secops data-table get --name "suspicious_ips"
```

#### Create a data table:

```bash
# Basic creation with header definition
secops data-table create \
  --name "suspicious_ips" \
  --description "Known suspicious IP addresses" \
  --header '{"ip_address":"CIDR","description":"STRING","severity":"STRING"}'

# Basic creation with entity mapping and column options
secops data-table create \
  --name "suspicious_ips" \
  --description "Known suspicious IP addresses" \
  --header '{"ip_address":"entity.asset.ip","description":"STRING","severity":"STRING"}'
  --column-options '{"ip_address":{"repeatedValues":true}}'

# Create with initial rows
secops data-table create \
  --name "malicious_domains" \
  --description "Known malicious domains" \
  --header '{"domain":"STRING","category":"STRING","last_seen":"STRING"}' \
  --rows '[["evil.example.com","phishing","2023-07-01"],["malware.example.net","malware","2023-06-15"]]'
```

#### List rows in a data table:

```bash
secops data-table list-rows --name "suspicious_ips"
```

#### Update a data table's properties:

```bash
# Update both description and row TTL
secops data-table update \
  --name "suspicious_ips" \
  --description "Updated description for suspicious IPs" \
  --row-ttl "72h"

# Update only the description with explicit update mask
secops data-table update \
  --name "suspicious_ips" \
  --description "Only updating description" \
  --update-mask "description"
```

#### Add rows to a data table:

```bash
secops data-table add-rows \
  --name "suspicious_ips" \
  --rows '[["192.168.1.100","Scanning activity","Medium"],["10.0.0.5","Suspicious login attempts","High"]]'
```

#### Delete rows from a data table:

```bash
secops data-table delete-rows --name "suspicious_ips" --row-ids "row123,row456"
```

#### Replace all rows in a data table:

```bash
secops data-table replace-rows \
  --name "suspicious_ips" \
  --rows '[["192.168.100.1","Critical","Active scanning"],["10.1.1.5","High","Brute force attempts"],["172.16.5.10","Medium","Suspicious traffic"]]'

# Replace rows with a file
secops data-table replace-rows \
  --name "suspicious_ips" \
  --rows-file "/path/to/rows.json"
```

#### Bulk update rows in a data table:

```bash
# Update rows using JSON with full resource names
secops data-table update-rows \
  --name "suspicious_ips" \
  --rows '[{"name":"projects/my-project/locations/us/instances/my-instance/dataTables/suspicious_ips/dataTableRows/row123","values":["192.168.100.1","Critical","Updated scanning info"]},{"name":"projects/my-project/locations/us/instances/my-instance/dataTables/suspicious_ips/dataTableRows/row456","values":["10.1.1.5","High","Updated brute force info"],"update_mask":"values"}]'

# Update rows from a JSON file
# File format: array of objects with 'name', 'values', and
# optional 'update_mask'
secops data-table update-rows \
  --name "suspicious_ips" \
  --rows-file "/path/to/row_updates.json"
```

Example `row_updates.json` file:

```json
[
  {
    "name": "projects/.../dataTables/suspicious_ips/dataTableRows/row1",
    "values": ["192.168.100.1", "Critical", "Updated info"]
  },
  {
    "name": "projects/.../dataTables/suspicious_ips/dataTableRows/row2",
    "values": ["10.1.1.5", "High", "Updated brute force info"],
    "update_mask": "values"
  }
]
```

#### Delete a data table:

```bash
secops data-table delete --name "suspicious_ips"
secops data-table delete --name "suspicious_ips" --force  # Force deletion of non-empty table
```

### Reference Lists

Reference Lists are simple lists of values (strings, CIDR blocks, or regex patterns) that can be referenced in detection rules.

#### List reference lists:

```bash
secops reference-list list
secops reference-list list --view "FULL"  # Include entries (can be large)
```

#### Get reference list details:

```bash
secops reference-list get --name "malicious_domains"
secops reference-list get --name "malicious_domains" --view "BASIC"  # Metadata only
```

#### Create a reference list:

```bash
# Create with inline entries
secops reference-list create \
  --name "admin_accounts" \
  --description "Administrative accounts" \
  --entries "admin,administrator,root,superuser"

# Create with entries from a file
secops reference-list create \
  --name "malicious_domains" \
  --description "Known malicious domains" \
  --entries-file "/path/to/domains.txt" \
  --syntax-type "STRING"

# Create with CIDR entries
secops reference-list create \
  --name "trusted_networks" \
  --description "Internal network ranges" \
  --entries "10.0.0.0/8,192.168.0.0/16,172.16.0.0/12" \
  --syntax-type "CIDR"
```

#### Update a reference list:

```bash
# Update description
secops reference-list update \
  --name "admin_accounts" \
  --description "Updated administrative accounts list"

# Update entries
secops reference-list update \
  --name "admin_accounts" \
  --entries "admin,administrator,root,superuser,sysadmin"

# Update entries from file
secops reference-list update \
  --name "malicious_domains" \
  --entries-file "/path/to/updated_domains.txt"
```

### Featured Content Rules

Featured content rules are pre-built detection rules available in the Chronicle Content Hub. These curated rules can be listed and filtered to help you discover and deploy detections.

#### List all featured content rules:

```bash
# List all featured content rules (returns dict with pagination metadata)
secops featured-content-rules list

# List featured content rules as a direct list
secops featured-content-rules list --as-list
```

#### List with pagination:

```bash
# Get first page with 10 rules
secops featured-content-rules list --page-size 10

# Get next page using token from previous response
secops featured-content-rules list --page-size 10 --page-token "token123"
```

#### Get filtered list:

```bash
secops featured-content-rules list \
  --filter 'category_name:"Threat Detection" AND rule_precision:"Precise"'
```

## Examples

### Search for Recent Network Connections

```bash
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\"" --time-window 1 --max-events 10
```

### Export Failed Login Attempts to CSV

```bash
secops search --query "metadata.event_type = \"USER_LOGIN\" AND security_result.action = \"BLOCK\"" --fields "metadata.event_timestamp,principal.user.userid,principal.ip,security_result.summary" --time-window 24 --csv
```

### Find Entity Details for an IP Address

```bash
secops entity --value "192.168.1.100" --time-window 72
```

### Import entities:

```bash
secops entity import --type "CUSTOM_LOG_TYPE" --file "/path/to/entities.json"
```

### Check for Critical IoCs

```bash
secops iocs --time-window 168 --prioritized
```

### Ingest Custom Logs

```bash
secops log ingest --type "CUSTOM_JSON" --file "logs.json" --force
```

### Ingest Logs with Labels

```bash
# Add labels to categorize logs
secops log ingest --type "OKTA" --file "auth_logs.json" --labels "environment=production,application=web-app,region=us-central"
```

### Ingest Logs from a File(Multiple Logs)

```bash
secops log ingest --type "OKTA" --file "auth_multi_logs.json"
```

### Create and Enable a Detection Rule

```bash
secops rule create --file "new_rule.yaral"
# If successful, enable the rule using the returned rule ID
secops rule enable --id "ru_abcdef" --enabled true
```

### Get Rule Detections

```bash
secops rule detections --rule-id "ru_abcdef" --time-window 24 --list-basis "CREATED_TIME"
```

### Get Critical Alerts

```bash
secops alert --snapshot-query "feedback_summary.priority = \"PRIORITY_CRITICAL\"" --time-window 24
```

### Export All Logs from the Last Week

```bash
secops export create --gcs-bucket "projects/my-project/buckets/my-export-bucket" --all-logs --time-window 168
```

### Test a Detection Rule Against Historical Data

```bash
# Create a rule file
cat > test.yaral << 'EOF'
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
EOF

# Test the rule against the last 24 hours of data
secops rule test --file test.yaral --time-window 24

# Test the rule with a larger result set from a specific time range
secops rule test --file test.yaral --start-time "2023-08-01T00:00:00Z" --end-time "2023-08-08T00:00:00Z" --max-results 500
```

### Ask Gemini About a Security Threat

```bash
secops gemini --query "Explain how to defend against Log4Shell vulnerability"
```

### Create a Data Table and Reference List

```bash
# Create a data table for suspicious IP address tracking
secops data-table create \
  --name "suspicious_ips" \
  --description "IP addresses with suspicious activity" \
  --header '{"ip_address":"CIDR","detection_count":"STRING","last_seen":"STRING"}' \
  --rows '[["192.168.1.100","5","2023-08-15"],["10.0.0.5","12","2023-08-16"]]'

# Create a reference list with trusted domains
secops reference-list create \
  --name "trusted_domains" \
  --description "Internal trusted domains" \
  --entries "internal.example.com,trusted.example.org,secure.example.net" \
  --syntax-type "STRING"
```

### Parser Management Workflow

```bash
# List all parsers to see what's available
secops parser list

# Get details of a specific parser
secops parser get --log-type "WINDOWS" --id "pa_12345"

# Create a custom parser for a new log format
secops parser create \
  --log-type "CUSTOM_APPLICATION" \
  --parser-code-file "/path/to/custom_parser.conf" \
  --validated-on-empty-logs

# Copy an existing parser as a starting point
secops parser copy --log-type "OKTA" --id "pa_okta_base"

# Activate your custom parser
secops parser activate --log-type "CUSTOM_APPLICATION" --id "pa_new_custom"

# If needed, deactivate and delete old parser
secops parser deactivate --log-type "CUSTOM_APPLICATION" --id "pa_old_custom"
secops parser delete --log-type "CUSTOM_APPLICATION" --id "pa_old_custom"
```

### Complete Parser Workflow Example: Retrieve, Run, and Ingest

This example demonstrates the complete workflow of retrieving an OKTA parser, running it against a sample log, and ingesting the parsed UDM event:

```bash
# Step 1: List OKTA parsers to find an active one
secops parser list --log-type "OKTA" > okta_parsers.json

# Extract the first parser ID (you can use jq or grep)
PARSER_ID=$(cat okta_parsers.json | jq -r '.[0].name' | awk -F'/' '{print $NF}')
echo "Using parser: $PARSER_ID"

# Step 2: Get the parser details and save to a file
secops parser get --log-type "OKTA" --id "$PARSER_ID" > parser_details.json

# Extract and decode the parser code (base64 encoded in 'cbn' field)
cat parser_details.json | jq -r '.cbn' | base64 -d > okta_parser.conf

# Step 3: Create a sample OKTA log file
cat > okta_log.json << 'EOF'
{
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
}
EOF

# Step 4: Run the parser against the sample log
secops parser run \
  --log-type "OKTA" \
  --parser-code-file "okta_parser.conf" \
  --log "$(cat okta_log.json)" > parser_result.json

# Display the parser result
echo "Parser execution result:"
cat parser_result.json | jq '.'

# Step 5: Extract the parsed UDM event from the result
# The structure is: runParserResults[0].parsedEvents.events[0].event
cat parser_result.json | jq '.runParserResults[0].parsedEvents.events[0].event' > udm_event.json

# Verify the UDM event looks correct
echo "Extracted UDM event:"
cat udm_event.json | jq '.'

# Step 6: Ingest the parsed UDM event back into Chronicle
secops log ingest-udm --file "udm_event.json"

echo "UDM event successfully ingested!"
```

#### Alternative: Using a logs file instead of inline log

If you have multiple logs to test, you can use a logs file:

```bash
# Create a file with multiple logs (one per line)
cat > okta_logs.txt << 'EOF'
{"actor":{"alternateId":"user1@example.com","displayName":"User 1","type":"User"},"eventType":"user.session.start","outcome":{"result":"SUCCESS"},"published":"2025-06-19T21:51:50.116Z"}
{"actor":{"alternateId":"user2@example.com","displayName":"User 2","type":"User"},"eventType":"user.account.lock","outcome":{"result":"FAILURE","reason":"LOCKED_OUT"},"published":"2025-06-19T21:52:50.116Z"}
{"actor":{"alternateId":"user3@example.com","displayName":"User 3","type":"User"},"eventType":"user.session.end","outcome":{"result":"SUCCESS"},"published":"2025-06-19T21:53:50.116Z"}
EOF

# Run parser against all logs in the file
secops parser run \
  --log-type "OKTA" \
  --parser-code-file "okta_parser.conf" \
  --logs-file "okta_logs.txt" > multi_parser_result.json

# Extract all parsed UDM events
cat multi_parser_result.json | jq '[.runParserResults[].parsedEvents.events[].event]' > udm_events.json

# Ingest all UDM events
secops log ingest-udm --file "udm_events.json"
```

This workflow is useful for:
- Testing parsers before deployment
- Understanding how logs are transformed to UDM format
- Debugging parsing issues
- Re-processing logs with updated parsers
- Validating parser changes against real log samples

### Feed Management

Manage data ingestion feeds in Chronicle.

List feeds:

```bash
secops feed list
```

Get feed details:

```bash
secops feed get --id "feed-123"
```

Create feed:

```bash
# Create an HTTP feed
secops feed create \
  --display-name "My HTTP Feed" \
  --details '{"logType":"projects/your-project-id/locations/us/instances/your-instance-id/logTypes/WINEVTLOG","feedSourceType":"HTTP","httpSettings":{"uri":"https://example.com/feed","sourceType":"FILES"},"labels":{"environment":"production"}}'
```

Update feed:

```bash
# Update feed display name
secops feed update --id "feed-123" --display-name "Updated Feed Name"

# Update feed details
secops feed update --id "feed-123" --details '{"httpSettings":{"uri":"https://example.com/updated-feed","sourceType":"FILES"}}'

# Update both display name and details
secops feed update --id "feed-123" --display-name "Updated Name" --details '{"httpSettings":{"uri":"https://example.com/updated-feed"}}'
```

Enable and disable feeds:

```bash
# Enable a feed
secops feed enable --id "feed-123"

# Disable a feed
secops feed disable --id "feed-123"
```

Generate feed secret:

```bash
# Generate a secret for feeds that support authentication
secops feed generate-secret --id "feed-123"
```

Delete feed:

```bash
secops feed delete --id "feed-123"
```

### Native Dashboards

The Dashboard commands allow you to manage and interact with dashboards in Chronicle.

Create native dashboard:
```bash
# Create minimal dashboard
secops dashboard create --display-name "Security Overview" \
                        --description "Security monitoring dashboard" \
                        --access-type PRIVATE

# Create with filters and charts
secops dashboard create --display-name "Security Overview" \
                        --description "Security monitoring dashboard" \
                        --access-type PRIVATE \
                        --filters-file filters.json \
                        --charts '[{\"dashboardChart\": \"projects/<project_id>/locations/<location>/instances/<instacne_id>/dashboardCharts/<chart_id>\", \"chartLayout\": {\"startX\": 0, \"spanX\": 48, \"startY\": 0, \"spanY\": 26}, \"filtersIds\": [\"GlobalTimeFilter\"]}]'
```

Get dashboard details:
```bash
secops dashboard get --id dashboard-id --view FULL
```

List dashboards:
```bash
secops dashboard list --page-size 10
```

Update dashboard:
```bash
secops dashboard update --id dashboard-id --display-name "Updated Security Dashboard" --description "Updated security monitoring dashboard" --access-type PRIVATE --filters '[{"id": "GlobalTimeFilter", "dataSource": "GLOBAL", "filterOperatorAndFieldValues": [{"filterOperator": "PAST", "fieldValues": ["7", "DAY"]}], "displayName": "Global Time Filter", "chartIds": [], "isStandardTimeRangeFilter": true, "isStandardTimeRangeFilterEnabled": true}]' --charts-file charts.json
```

Delete dashboard:
```bash
secops dashboard delete --id dashboard-id
```

Create Duplicate dashboard from existing:
```bash
secops dashboard duplicate --id source-dashboard-id \
                           --display-name "Copy of Security Overview"
```

Import dashboard:
```bash
secops dashboard import --dashboard-data-file dashboard_data.json

# import with chart and query
secops dashboard import --dashboard-data-file dashboard_data.json --chart-file chart.json --query-file query.json

# Or with dashboard JSON
secops dashboard import --dashboard-data '{"name":"12312321321321"}'
```

Export dashboard:
```bash
secops dashboard export --dashboard-names 'projects/your-project-id/locations/us/instances/your-instance-id/nativeDashboard/xxxxxxx'
```

Adding Chart to existing dashboard:
```bash
secops dashboard add-chart --dashboard-id dashboard-id \
                           --display-name "DNS Query Chart" \
                           --description "Shows DNS query patterns" \
                           --query-file dns_query.txt \
                           --chart_layout '{\"startX\": 0, \"spanX\": 12, \"startY\": 0, \"spanY\": 8}' \
                           --chart_datasource '{\"dataSources\": [\"UDM\"]}' \
                           --interval '{\"relativeTime\": {\"timeUnit\": \"DAY\", \"startTimeVal\": \"1\"}}' \
                           --visualization-file visualization.json \
                           --tile_type VISUALIZATION
```

Get existing chart detail:
```bash
secops dashboard get-chart --id chart-id
```

Edit existing chart details:
```bash
secops dashboard edit-chart --dashboard-id dashboard-id \
                            --dashboard-chart-from-file dashboard_chart.json \
                            --dashboard-query-from-file dashboard_query.json

# Edit with JSON string        
secops dashboard edit-chart --dashboard-id dashboard-id \
                            --dashboard-chart '{\"name\": \"<query_id>\",\n    \"query\": \"metadata.event_type = \\\"USER_LOGIN\\\"\\nmatch:\\n  principal.user.userid\\noutcome:\\n  $logon_count = count(metadata.id)\\norder:\\n  $logon_count desc\\nlimit: 10\",\n    \"input\": {\"relativeTime\": {\"timeUnit\": \"DAY\", \"startTimeVal\": \"1\"}},\n    \"etag\": \"<etag>\"}' \
                            --dashboard-query '{\"name\": \"<ChartID>\",\n    \"displayName\": \"Updated Display name\",\n    \"description\": \"Updaed description\",\n    \"etag\": \"<etag>\"}'
```

Remove Chart from existing dashboard:
```bash
secops dashboard remove-chart --dashboard-id dashboard-id \
                              --chart-id chart-id
```

### Dashboard Query

Dashboard query commands provide option to execute query without dashboard and get details of existing dashboard query.

Executing Dashboard Query:
```bash
secops dashboard-query execute --query-file dns_query.txt \
                              --interval '{\"relativeTime\": {\"timeUnit\": \"DAY\", \"startTimeVal\": \"7\"}}' \
                              --filters-file filters.json
```

Get Dashboard Query details:
```bash
secops dashboard-query get --id query-id
```

## Conclusion

The SecOps CLI provides a powerful way to interact with Google Security Operations products directly from your terminal. For more detailed information about the SDK capabilities, refer to the [main README](README.md).