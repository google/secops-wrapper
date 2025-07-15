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

The CLI allows you to save your credentials and other common settings in a configuration file, so you don't have to specify them in every command.

### Saving Configuration

Save your Chronicle instance ID, project ID, and region:

```bash
secops config set --customer-id "your-instance-id" --project-id "your-project-id" --region "us"
```

You can also save your service account path:

```bash
secops config set --service-account "/path/to/service-account.json" --customer-id "your-instance-id" --project-id "your-project-id" --region "us"
```

Additionally, you can set default time parameters:

```bash
secops config set --time-window 48
```

```bash
secops config set --start-time "2023-07-01T00:00:00Z" --end-time "2023-07-02T00:00:00Z"
```

The configuration is stored in `~/.secops/config.json`.

### Viewing Configuration

View your current configuration settings:

```bash
secops config view
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
- `--output FORMAT` - Output format (json, text)
- `--start-time TIME` - Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- `--end-time TIME` - End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)
- `--time-window HOURS` - Time window in hours (alternative to start/end time)

## Commands

### Search UDM Events

Search for events using UDM query syntax:

```bash
secops search --query "metadata.event_type = \"NETWORK_CONNECTION\"" --max-events 10
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
secops log types
secops log types --search "windows"
```

> **Note:** Chronicle uses parsers to process and normalize raw log data into UDM format. If you're ingesting logs for a custom format, you may need to create or configure parsers. See the [Parser Management](#parser-management) section for details on managing parsers.

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
```

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

### Rule Management

List detection rules:

```bash
secops rule list
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

### Alert Management

Get alerts:

```bash
secops alert --time-window 24 --max-alerts 50
secops alert --snapshot-query "feedback_summary.status != \"CLOSED\"" --time-window 24
secops alert --baseline-query "detection.rule_name = \"My Rule\"" --time-window 24
```

### Case Management

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

> **Note**: The case management uses a batch API that can retrieve multiple cases in a single request. You can provide up to 1000 case IDs separated by commas.

### Data Export

List available log types for export:

```bash
secops export log-types --time-window 24
secops export log-types --page-size 50
```

Create a data export:

```bash
secops export create --gcs-bucket "projects/my-project/buckets/my-bucket" --log-type "WINDOWS" --time-window 24
secops export create --gcs-bucket "projects/my-project/buckets/my-bucket" --all-logs --time-window 24
```

Check export status:

```bash
secops export status --id "export-123"
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

### Create and Enable a Detection Rule

```bash
secops rule create --file "new_rule.yaral"
# If successful, enable the rule using the returned rule ID
secops rule enable --id "ru_abcdef" --enabled true
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

## Conclusion

The SecOps CLI provides a powerful way to interact with Google Security Operations products directly from your terminal. For more detailed information about the SDK capabilities, refer to the [main README](README.md).