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

### Alert Management

Get alerts:

```bash
secops alert --time-window 24 --max-alerts 50
secops alert --snapshot-query "feedback_summary.status != \"CLOSED\"" --time-window 24
secops alert --baseline-query "detection.rule_name = \"My Rule\"" --time-window 24
```

### Case Management

Get case details:

```bash
secops case --ids "case-123,case-456"
```

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

### Ask Gemini About a Security Threat

```bash
secops gemini --query "Explain how to defend against Log4Shell vulnerability"
```

## Conclusion

The SecOps CLI provides a powerful way to interact with Google Security Operations products directly from your terminal. For more detailed information about the SDK capabilities, refer to the [main README](README.md).