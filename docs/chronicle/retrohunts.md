# Retrohunts

The Chronicle client provides capabilities for performing retrohunts, which allow you to run detection rules against historical data.

## Creating Retrohunts

You can create a new retrohunt to search for matches in historical data:

```python
from secops import SecOpsClient

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

# Create a retrohunt using an existing rule
retrohunt = chronicle.create_retrohunt(
    rule_id="ru_12345678",
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-31T23:59:59Z",
    description="January 2023 search for suspicious logins"
)

print(f"Retrohunt ID: {retrohunt.get('id')}")
print(f"Status: {retrohunt.get('status')}")
```

## Creating Retrohunts with Custom Rules

You can also create a retrohunt with a custom rule that is not saved:

```python
# Define a YARA-L2 rule
rule_content = """
rule suspicious_login {
  meta:
    author = "Chronicle Security"
    description = "Detects suspicious login activity"
    severity = "HIGH"
  events:
    $login.metadata.event_type = "USER_LOGIN"
    $login.principal.ip = "192.168.1.100"
    $login.security_result.action = "BLOCK"
  condition:
    $login
}
"""

# Create a retrohunt with a custom rule
custom_retrohunt = chronicle.create_retrohunt_with_rule(
    rule_content=rule_content,
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-31T23:59:59Z",
    description="Custom rule retrohunt for January 2023"
)

print(f"Retrohunt ID: {custom_retrohunt.get('id')}")
```

## Listing Retrohunts

You can list and filter retrohunts:

```python
# List all retrohunts
retrohunts = chronicle.list_retrohunts()

# Process the results
for hunt in retrohunts:
    print(f"Retrohunt ID: {hunt.get('id')}")
    print(f"Description: {hunt.get('description')}")
    print(f"Status: {hunt.get('status')}")
    print(f"Created: {hunt.get('createTime')}")
    print("---")
```

## Getting Retrohunt Details

You can get detailed information about a specific retrohunt:

```python
# Get details of a specific retrohunt
retrohunt_details = chronicle.get_retrohunt(
    retrohunt_id="rh_12345678"
)

print(f"Retrohunt ID: {retrohunt_details.get('id')}")
print(f"Description: {retrohunt_details.get('description')}")
print(f"Rule ID: {retrohunt_details.get('ruleId')}")
print(f"Start Time: {retrohunt_details.get('startTime')}")
print(f"End Time: {retrohunt_details.get('endTime')}")
print(f"Status: {retrohunt_details.get('status')}")
print(f"Created: {retrohunt_details.get('createTime')}")
print(f"Updated: {retrohunt_details.get('updateTime')}")
```

## Retrohunt Statuses

Chronicle retrohunts can have the following statuses:

| Status | Description |
|--------|-------------|
| `PENDING` | Retrohunt is queued and waiting to start |
| `RUNNING` | Retrohunt is currently running |
| `DONE` | Retrohunt has completed successfully |
| `FAILED` | Retrohunt has failed |
| `CANCELLED` | Retrohunt was cancelled |

## Cancelling Retrohunts

You can cancel a retrohunt that is pending or running:

```python
# Cancel a retrohunt
cancel_result = chronicle.cancel_retrohunt(
    retrohunt_id="rh_12345678"
)

print(f"Cancelled: {cancel_result.get('success')}")
```

## Getting Retrohunt Results

You can get the results of a completed retrohunt:

```python
# Get results of a retrohunt
results = chronicle.get_retrohunt_results(
    retrohunt_id="rh_12345678"
)

print(f"Total matches: {results.get('totalMatches')}")

# Process the matches
for match in results.get('matches', []):
    print(f"Match ID: {match.get('id')}")
    print(f"Rule name: {match.get('ruleName')}")
    print(f"Event time: {match.get('eventTime')}")
    
    # Get the UDM event that matched
    event = match.get('event', {})
    print(f"Event type: {event.get('metadata', {}).get('event_type')}")
    print(f"Product: {event.get('metadata', {}).get('product_name')}")
    print("---")
```

## Pagination for Retrohunt Results

For large result sets, use pagination:

```python
# First page
results = chronicle.get_retrohunt_results(
    retrohunt_id="rh_12345678",
    page_size=25
)

# Get next page if there are more results
if results.next_page_token:
    next_page = chronicle.get_retrohunt_results(
        retrohunt_id="rh_12345678",
        page_size=25,
        page_token=results.next_page_token
    )
```

## Creating Alerts from Retrohunt Results

You can create alerts from retrohunt matches:

```python
# Create alerts from retrohunt matches
alert_result = chronicle.create_alerts_from_retrohunt(
    retrohunt_id="rh_12345678",
    alert_name="Retrohunt Alert - Suspicious Logins",
    severity="HIGH"
)

print(f"Alerts created: {alert_result.get('alertCount')}")
```

## Error Handling

```python
try:
    retrohunt_details = chronicle.get_retrohunt(
        retrohunt_id="rh_12345678"
    )
except Exception as e:
    print(f"Retrohunt lookup failed: {e}")
```
