# Case Management

The Chronicle client provides capabilities for managing cases, which allow security teams to track and document their investigations.

## Creating Cases

You can create new cases to track investigations:

```python
from secops import SecOpsClient

# Initialize the client
client = SecOpsClient()
chronicle = client.chronicle(
    customer_id="your-chronicle-instance-id",
    project_id="your-project-id",
    region="us"
)

# Create a new case
new_case = chronicle.create_case(
    display_name="Suspicious Activity Investigation",
    description="Investigation into suspicious login attempts",
    severity="HIGH",
    priority="P1"
)

print(f"Case ID: {new_case.get('id')}")
print(f"Case URL: {new_case.get('url')}")
```

## Listing Cases

You can list and filter cases:

```python
# List all open cases
open_cases = chronicle.list_cases(
    status="OPEN"
)

# Process the results
for case in open_cases:
    print(f"Case ID: {case.get('id')}")
    print(f"Name: {case.get('displayName')}")
    print(f"Severity: {case.get('severity')}")
    print(f"Priority: {case.get('priority')}")
    print(f"Created: {case.get('createTime')}")
    print("---")
```

## Getting Case Details

You can get detailed information about a specific case:

```python
# Get details of a specific case
case_details = chronicle.get_case(
    case_id="ca_12345678"
)

print(f"Case ID: {case_details.get('id')}")
print(f"Name: {case_details.get('displayName')}")
print(f"Description: {case_details.get('description')}")
print(f"Severity: {case_details.get('severity')}")
print(f"Priority: {case_details.get('priority')}")
print(f"Status: {case_details.get('status')}")
print(f"Created: {case_details.get('createTime')}")
print(f"Updated: {case_details.get('updateTime')}")
```

## Updating Cases

You can update case properties:

```python
# Update case details
update_result = chronicle.update_case(
    case_id="ca_12345678",
    display_name="Updated Investigation Title",
    description="Updated description with new findings",
    severity="CRITICAL",
    priority="P0"
)

print(f"Updated: {update_result.get('success')}")
```

## Changing Case Status

You can update the status of a case:

```python
# Update case status to CLOSED
status_result = chronicle.update_case_status(
    case_id="ca_12345678",
    status="CLOSED",
    resolution="RESOLVED",
    resolution_summary="Investigation complete, remediation actions taken"
)

print(f"Status updated: {status_result.get('success')}")
```

## Case Statuses

Chronicle supports the following case statuses:

| Status | Description |
|--------|-------------|
| `OPEN` | Case is open and under investigation |
| `IN_PROGRESS` | Case is actively being worked on |
| `PENDING` | Case is waiting for external input |
| `CLOSED` | Case investigation is complete |

## Case Resolutions

When closing a case, you can specify a resolution:

| Resolution | Description |
|------------|-------------|
| `RESOLVED` | Issue was resolved |
| `FALSE_POSITIVE` | Alert was a false positive |
| `DUPLICATE` | Case is a duplicate of another case |
| `NO_ACTION_NEEDED` | No action was required |

## Adding Alerts to Cases

You can associate alerts with cases:

```python
# Add alerts to a case
add_alerts_result = chronicle.add_alerts_to_case(
    case_id="ca_12345678",
    alert_ids=["al_12345678", "al_87654321"]
)

print(f"Alerts added: {add_alerts_result.get('successCount')}")
```

## Adding Comments to Cases

You can add comments to document investigation progress:

```python
# Add a comment to a case
comment_result = chronicle.add_case_comment(
    case_id="ca_12345678",
    comment="Identified source of suspicious activity, proceeding with containment"
)

print(f"Comment added: {comment_result.get('id')}")
```

## Case Attachments

You can add attachments to cases:

```python
# Add an attachment to a case
attachment_result = chronicle.add_case_attachment(
    case_id="ca_12345678",
    file_path="/path/to/evidence.pdf",
    display_name="Evidence Document"
)

print(f"Attachment added: {attachment_result.get('id')}")
```

## Pagination

For large result sets, use pagination:

```python
# First page
results = chronicle.list_cases(
    page_size=25
)

# Get next page if there are more results
if results.next_page_token:
    next_page = chronicle.list_cases(
        page_size=25,
        page_token=results.next_page_token
    )
```

## Error Handling

```python
try:
    case_details = chronicle.get_case(
        case_id="ca_12345678"
    )
except Exception as e:
    print(f"Case lookup failed: {e}")
```
