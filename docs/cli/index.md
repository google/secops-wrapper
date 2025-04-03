# Command Line Interface

## Installation

The CLI is automatically installed when you install the SecOps SDK:

```bash
pip install secops
```

## Basic Usage

The CLI follows this general pattern:

```bash
secops [common options] COMMAND_GROUP COMMAND [command options]
```

### Common Options

Common options can be provided either via command-line arguments or environment variables:

| CLI Option | Environment Variable | Description |
|------------|----------------------|-------------|
| --credentials-file | SECOPS_CREDENTIALS_FILE | Path to service account file |
| --project-id | SECOPS_PROJECT_ID | GCP project id or number |
| --customer-id | SECOPS_CUSTOMER_ID | Chronicle instance ID |
| --region | SECOPS_REGION | Region where project is located |

### Using Environment Variables

You can set options in a .env file in your project root:

```bash
# .env file
SECOPS_CREDENTIALS_FILE=path/to/credentials.json
SECOPS_PROJECT_ID=your-project-id
SECOPS_CUSTOMER_ID=your-instance-id
SECOPS_REGION=your-region
```

## Example Commands

### Search for Events

```bash
# Search for events in the last 24 hours
secops chronicle search \
  --query "metadata.log_type = \"OKTA\"" \
  --start-time "1d"
```

### Natural Language Search

```bash
# Search using natural language
secops chronicle nl-search \
  --query "Show me all failed login attempts in the last 24 hours" \
  --start-time "1d"
```

### List IoCs

```bash
# List IoCs
secops chronicle iocs list \
  --start-time "7d"
```

### Get Alert Details

```bash
# Get details of a specific alert
secops chronicle alerts get \
  --alert-id "your-alert-id"
```

## Command Reference

For a complete reference of all available commands, see the CLI Commands page.
