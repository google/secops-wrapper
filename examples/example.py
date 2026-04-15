#!/usr/bin/env python3
"""Example usage of the Google SecOps SDK for Chronicle."""

from datetime import datetime, timedelta, timezone
from secops import SecOpsClient
from pprint import pprint
from secops.exceptions import APIError
import json
import argparse
import uuid


def get_client(project_id, customer_id, region):
    """Initialize and return the Chronicle client.

    Args:
        project_id: Google Cloud Project ID
        customer_id: Chronicle Customer ID (UUID)
        region: Chronicle region (us or eu)

    Returns:
        Chronicle client instance
    """
    client = SecOpsClient()
    chronicle = client.chronicle(
        customer_id=customer_id, project_id=project_id, region=region
    )
    return chronicle


def get_time_range():
    """Get default time range for queries."""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)
    return start_time, end_time


def example_udm_search(chronicle):
    """Example 1: Basic UDM Search."""
    print("\n=== Example 1: Basic UDM Search ===")
    start_time, end_time = get_time_range()

    try:
        events = chronicle.search_udm(
            query="""metadata.event_type = "NETWORK_CONNECTION"
            ip != ""
            """,
            start_time=start_time,
            end_time=end_time,
            max_events=5,
        )

        total_events = events.get("total_events", 0)
        events_list = events.get("events", [])
        print(f"\nFound {total_events} events")

        if events_list:
            print("\nFirst event details:")
            event = events_list[0]
            print(f"Event name: {event.get('name', 'N/A')}")
            # Extract metadata from UDM
            metadata = event.get("udm", {}).get("metadata", {})
            print(f"Event type: {metadata.get('eventType', 'N/A')}")
            print(f"Event timestamp: {metadata.get('eventTimestamp', 'N/A')}")

            # Show IP information if available
            principal_ip = (
                event.get("udm", {}).get("principal", {}).get("ip", ["N/A"])[0]
            )
            target_ip = event.get("udm", {}).get("target", {}).get("ip", ["N/A"])[0]
            print(f"Connection: {principal_ip} -> {target_ip}")

            print(f"\nMore data available: {events.get('more_data_available', False)}")
        else:
            print("\nNo events found in the specified time range.")
    except Exception as e:
        print(f"Error performing UDM search: {e}")


def example_udm_search_view(chronicle):
    """Example 15: UDM Search View."""
    print("\n=== Example 15: UDM Search View ===")
    start_time, end_time = get_time_range()

    try:
        print("\nFetching UDM search view results...")
        # Basic query for network connection events
        result = chronicle.fetch_udm_search_view(
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=start_time,
            end_time=end_time,
            max_events=5,  # Limit to 5 events for display purposes
        )

        # The result is a list of response objects
        print(f"\nReceived {len(result)} response objects")
        
        if result and len(result) > 0:
            # Check if search completed successfully
            search_complete = result[0].get("complete", False)
            print(f"Search completed: {search_complete}")
            
            # Get events from the response
            events = result[0].get("events", {}).get("events", [])
            print(f"Found {len(events)} events")
            
            if events:
                # Display details of the first event
                print("\nFirst event details:")
                event = events[0].get("event")
                
                # Print basic event information
                print(f'Event ID: {event.get("metadata",{}).get("id", "N/A")}')
                
                # Extract and print metadata
                metadata = event.get("metadata", {})
                print(f"Event Type: {metadata.get('eventType', 'N/A')}")
                print(f"Event Timestamp: {metadata.get('eventTimestamp', 'N/A')}")
                
                # Extract principal and target information if available
                if "principal" in event:
                    principal = event["principal"]
                    print("\nPrincipal Information:")
                    if "ip" in principal:
                        print(f"IP: {principal.get('ip', 'N/A')}")
                    if "hostname" in principal:
                        print(f"Hostname: {principal.get('hostname', 'N/A')}")
                
                if "target" in event:
                    target = event["target"]
                    print("\nTarget Information:")
                    if "ip" in target:
                        print(f"IP: {target.get('ip', 'N/A')}")
                    if "hostname" in target:
                        print(f"Hostname: {target.get('hostname', 'N/A')}")
                
                # Show detection information if available
                detections = event.get("detection", [])
                if detections:
                    print(f"\nDetections: {len(detections)} found")
                    for i, detection in enumerate(detections[:2]):  # Show first 2 detections
                        print(f"Detection {i+1}:")
                        print(f"  Rule Name: {detection.get('ruleName', 'N/A')}")
                        print(f"  Rule ID: {detection.get('ruleId', 'N/A')}")
            else:
                print("\nNo events found in the specified time range.")
                
            # Show if there are more events available
            more_available = result[0].get("events", {}).get("moreDataAvailable", False)
            print(f"\nMore events available: {more_available}")
            
        # Example with snapshot query to filter alerts
        print("\n--- Using snapshot query to filter alerts ---")
        filtered_result = chronicle.fetch_udm_search_view(
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=start_time,
            end_time=end_time,
            snapshot_query='feedback_summary.status = "OPEN"',  # Filter for open alerts
            max_events=5,
        )
        
        if filtered_result and len(filtered_result) > 0:
            filtered_events = filtered_result[0].get("events", {}).get("events", [])
            print(f"Found {len(filtered_events)} events after applying snapshot query")
        
    except APIError as e:
        print(f"Error fetching UDM search view: {e}")
        
        # Additional information for specific error cases
        if "invalid query" in str(e).lower():
            print("\nTip: Make sure your query syntax is correct.")
            print("Example valid query: metadata.event_type = \"NETWORK_CONNECTION\"")
        elif "authorization" in str(e).lower() or "permission" in str(e).lower():
            print("\nTip: Check that your account has permissions to access UDM search.")


def example_stats_query(chronicle):
    """Example 2: Stats Query."""
    print("\n=== Example 2: Stats Query ===")
    start_time, end_time = get_time_range()

    try:
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
            timeout=180,
        )
        print("\nTop hostnames by event count:")
        rows = stats.get("rows", [])
        if rows:
            for row in rows:
                print(
                    f"Hostname: {row.get('target.hostname', 'N/A')}, Count: {row.get('count', 0)}"
                )
        else:
            print("No data found for the specified query and time range.")
    except Exception as e:
        print(f"Error performing stats query: {e}")


def example_entity_summary(chronicle):
    """Example 3: Entity Summary (IP, Domain, Hash)."""
    print("\n=== Example 3: Entity Summary ===")
    start_time, end_time = get_time_range()

    entities_to_summarize = {
        "IP Address": "8.8.8.8",
        "Domain": "google.com",
        "File Hash (SHA256)": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # Empty file hash
    }

    for entity_type, value in entities_to_summarize.items():
        print(f"\n--- Summarizing {entity_type}: {value} ---")
        try:
            summary = chronicle.summarize_entity(
                value=value,
                start_time=start_time,
                end_time=end_time,
            )

            if summary.primary_entity:
                print("\nPrimary Entity:")
                print(f"  Type: {summary.primary_entity.metadata.entity_type}")
                if summary.primary_entity.metric:
                    print(f"  First Seen: {summary.primary_entity.metric.first_seen}")
                    print(f"  Last Seen: {summary.primary_entity.metric.last_seen}")
                # Print specific entity details
                if "ip" in summary.primary_entity.entity.get("asset", {}):
                    print(f"  IPs: {summary.primary_entity.entity['asset']['ip']}")
                elif "name" in summary.primary_entity.entity.get("domain", {}):
                    print(
                        f"  Domain Name: {summary.primary_entity.entity['domain']['name']}"
                    )
                elif "md5" in summary.primary_entity.entity.get("file", {}):
                    print(f"  MD5: {summary.primary_entity.entity['file']['md5']}")
                elif "sha256" in summary.primary_entity.entity.get("file", {}):
                    print(
                        f"  SHA256: {summary.primary_entity.entity['file']['sha256']}"
                    )
            else:
                print("\nNo primary entity found.")

            if summary.related_entities:
                print(f"\nRelated Entities ({len(summary.related_entities)} found):")
                for rel_entity in summary.related_entities[:3]:  # Show first 3
                    print(f"  - Type: {rel_entity.metadata.entity_type}")

            if summary.alert_counts:
                print("\nAlert Counts:")
                for alert in summary.alert_counts:
                    print(f"  Rule: {alert.rule}, Count: {alert.count}")

            if summary.timeline:
                print(
                    f"\nTimeline: {len(summary.timeline.buckets)} buckets (size: {summary.timeline.bucket_size})"
                )

            if summary.prevalence:
                print(f"\nPrevalence ({len(summary.prevalence)} entries):")
                # Show first entry
                print(
                    f"  Time: {summary.prevalence[0].prevalence_time}, Count: {summary.prevalence[0].count}"
                )

            if summary.file_metadata_and_properties:
                print("\nFile Properties:")
                if summary.file_metadata_and_properties.metadata:
                    print("  Metadata:")
                    for prop in summary.file_metadata_and_properties.metadata[
                        :2
                    ]:  # Show first 2
                        print(f"    {prop.key}: {prop.value}")
                if summary.file_metadata_and_properties.properties:
                    print("  Properties:")
                    for group in summary.file_metadata_and_properties.properties:
                        print(f"    {group.title}:")
                        for prop in group.properties[:2]:  # Show first 2 per group
                            print(f"      {prop.key}: {prop.value}")

        except APIError as e:
            print(f"Error summarizing {entity_type} ({value}): {str(e)}")


def example_csv_export(chronicle):
    """Example 4: CSV Export."""
    print("\n=== Example 4: CSV Export ===")
    start_time, end_time = get_time_range()

    try:
        print("\nExporting network connection events to CSV...")
        csv_data = chronicle.fetch_udm_search_csv(
            query='metadata.event_type = "NETWORK_CONNECTION"',
            start_time=start_time,
            end_time=end_time,
            fields=["timestamp", "user", "hostname", "process name"],
        )

        # Print the first few lines of the CSV data
        lines = csv_data.strip().split("\n")
        print(f"\nExported {len(lines)-1} events to CSV")
        print("\nCSV Header:")
        print(lines[0])

        # Print a sample of the data (up to 5 rows)
        if len(lines) > 1:
            print("\nSample data rows:")
            for i in range(1, min(6, len(lines))):
                print(lines[i])

            # Optionally save to a file
            # with open("chronicle_events.csv", "w") as f:
            #     f.write(csv_data)
            # print("\nSaved CSV data to chronicle_events.csv")
    except APIError as e:
        print(f"Error: {str(e)}")


def example_list_iocs(chronicle):
    """Example 5: List IoCs."""
    print("\n=== Example 5: List IoCs ===")
    start_time, end_time = get_time_range()

    try:
        iocs = chronicle.list_iocs(
            start_time=start_time, end_time=end_time, max_matches=10000
        )

        # Handle different possible response structures
        matches = iocs.get("matches", [])
        print(f"\nFound {len(matches)} IoC matches")

        if matches:
            print("\nFirst IoC details:")
            first_ioc = matches[0]

            # Safely extract IoC type and value
            artifact_indicator = first_ioc.get("artifactIndicator", {})
            if artifact_indicator:
                ioc_type = next(iter(artifact_indicator.keys()), "Unknown")
                ioc_value = next(iter(artifact_indicator.values()), "Unknown")
                print(f"Type: {ioc_type}")
                print(f"Value: {ioc_value}")
            else:
                print("No artifact indicator found in IoC")

            # Safely extract sources
            sources = first_ioc.get("sources", [])
            if sources:
                print(f"Sources: {', '.join(sources)}")
            else:
                print("No sources found")

            # Show additional IoC details if available
            if "iocIngestTimestamp" in first_ioc:
                print(f"Ingest Time: {first_ioc['iocIngestTimestamp']}")
            if "firstSeenTimestamp" in first_ioc:
                print(f"First Seen: {first_ioc['firstSeenTimestamp']}")
            if "lastSeenTimestamp" in first_ioc:
                print(f"Last Seen: {first_ioc['lastSeenTimestamp']}")
        else:
            print("\nNo IoC matches found in the specified time range.")
            print("This could mean:")
            print("- No IoCs were ingested during this period")
            print("- No IoCs match the search criteria")
            print("- The time range is too narrow")

        # Print response structure for debugging if no matches
        if not matches:
            print(f"\nResponse keys: {list(iocs.keys())}")
            print(f"Full response structure: {iocs}")

    except APIError as e:
        print(f"Error: {str(e)}")
        print("This might happen if:")
        print("- No IoCs are available in this environment")
        print("- Insufficient permissions to access IoC data")
        print("- The API endpoint is not available")


def example_alerts_and_cases(chronicle):
    """Example 6: Alerts and Cases."""
    print("\n=== Example 6: Alerts and Cases ===")
    start_time, end_time = get_time_range()

    try:
        print("\nQuerying alerts (this may take a few moments)...")
        alerts = chronicle.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query='feedback_summary.status != "CLOSED"',
            max_alerts=1000,
        )

        alert_list = alerts.get("alerts", {}).get("alerts", [])
        print(f"\nNumber of alerts in response: {len(alert_list)}")

        # Debug: Print all alerts with cases
        print("\nDebug - Alerts with cases:")
        alerts_with_cases = 0
        for i, alert in enumerate(alert_list):
            case_name = alert.get("caseName")
            if case_name:
                alerts_with_cases += 1
                print(f"\nAlert {alerts_with_cases}:")
                print(f"Case ID: {case_name}")
                print(f"Alert ID: {alert.get('id')}")
                print(f"Rule Name: {alert.get('detection', [{}])[0].get('ruleName')}")
                print(f"Created Time: {alert.get('createdTime')}")
                print(f"Status: {alert.get('feedbackSummary', {}).get('status')}")

        case_ids = {
            alert.get("caseName") for alert in alert_list if alert.get("caseName")
        }

        if case_ids:
            print(f"\nFound {len(case_ids)} unique case IDs:")
            for case_id in list(case_ids)[:5]:  # Show first 5 case IDs
                print(f"  - {case_id}")

            try:
                cases = chronicle.get_cases(list(case_ids))
                print(f"\nRetrieved {len(cases.cases)} cases:")
                for case in cases.cases[:5]:  # Show first 5 cases
                    print(f"\nCase: {case.display_name}")
                    print(f"ID: {case.id}")
                    print(f"Priority: {case.priority}")
                    print(f"Stage: {case.stage}")
                    print(f"Status: {case.status}")

                    # Show SOAR platform info if available
                    if case.soar_platform_info:
                        print(f"SOAR Case ID: {case.soar_platform_info.case_id}")
                        print(f"SOAR Platform: {case.soar_platform_info.platform_type}")

                    # Count alerts for this case
                    case_alerts = [
                        alert
                        for alert in alert_list
                        if alert.get("caseName") == case.id
                    ]
                    print(f"Total Alerts for Case: {len(case_alerts)}")

                    high_sev_alerts = [
                        alert
                        for alert in case_alerts
                        if alert.get("feedbackSummary", {}).get("severityDisplay")
                        == "HIGH"
                    ]
                    if high_sev_alerts:
                        print(f"High Severity Alerts: {len(high_sev_alerts)}")
            except APIError as e:
                print(f"\nError retrieving case details: {str(e)}")
                print(
                    "This might happen if the case IDs are not accessible or the API has changed."
                )
        else:
            print("\nNo cases found in alerts")
    except APIError as e:
        print(f"Error: {str(e)}")


def example_validate_query(chronicle):
    """Example 7: Query Validation."""
    print("\n=== Example 7: Query Validation ===")

    # Example 1: Valid UDM Query
    try:
        print("\nValidating a correct UDM query:")
        valid_query = 'metadata.event_type = "NETWORK_CONNECTION"'

        print(f"Query: {valid_query}")
        result = chronicle.validate_query(valid_query)

        # More sophisticated validity check - a query is valid if it has a queryType
        # and doesn't have error messages or error text
        is_valid = (
            "queryType" in result
            and not result.get("errorText")
            and not result.get("errorType")
        )

        print(f"Is valid: {is_valid}")
        print(f"Query type: {result.get('queryType', 'Unknown')}")

        if is_valid:
            print("✅ Query is valid")
        elif "errorText" in result:
            print(f"❌ Validation error: {result['errorText']}")
        elif "validationMessage" in result:
            print(f"❌ Validation error: {result['validationMessage']}")

        # Print the full response for debugging
        print(f"Full response: {result}")
    except APIError as e:
        print(f"Error validating query: {str(e)}")

    # Example 2: Invalid UDM Query
    try:
        print("\nValidating an incorrect UDM query:")
        invalid_query = (
            'metadata.event_type === "NETWORK_CONNECTION"'  # Triple equals is invalid
        )

        print(f"Query: {invalid_query}")
        result = chronicle.validate_query(invalid_query)

        # More sophisticated validity check
        is_valid = (
            "queryType" in result
            and not result.get("errorText")
            and not result.get("errorType")
        )

        print(f"Is valid: {is_valid}")

        if is_valid:
            print("✅ Query is valid")
        elif "errorText" in result:
            print(f"❌ Validation error: {result['errorText']}")
        elif "validationMessage" in result:
            print(f"❌ Validation error: {result['validationMessage']}")

        # Print the full response for debugging
        print(f"Full response: {result}")
    except APIError as e:
        print(f"Error validating query: {str(e)}")

    # Example 3: Valid Stats Query
    try:
        print("\nValidating a correct stats query:")
        valid_stats_query = """metadata.event_type = "NETWORK_CONNECTION"
match:
    principal.hostname
outcome:
    $count = count(metadata.id)
order:
    $count desc"""

        print(f"Query: {valid_stats_query}")
        result = chronicle.validate_query(valid_stats_query)

        # More sophisticated validity check
        is_valid = (
            "queryType" in result
            and not result.get("errorText")
            and not result.get("errorType")
        )

        print(f"Is valid: {is_valid}")
        print(f"Query type: {result.get('queryType', 'Unknown')}")

        if is_valid:
            print("✅ Query is valid")
        elif "errorText" in result:
            print(f"❌ Validation error: {result['errorText']}")
        elif "validationMessage" in result:
            print(f"❌ Validation error: {result['validationMessage']}")

        # Print the full response for debugging
        print(f"Full response: {result}")
    except APIError as e:
        print(f"Error validating query: {str(e)}")


def example_nl_search(chronicle):
    """Example 9: Natural Language Search."""
    print("\n=== Example 9: Natural Language Search ===")
    start_time, end_time = get_time_range()

    try:
        # First, translate a natural language query to UDM
        print("\nPart 1: Translate natural language to UDM query")
        print("\nTranslating: 'show me network connections'")

        udm_query = chronicle.translate_nl_to_udm("show me network connections")
        print(f"\nTranslated UDM query: {udm_query}")

        # Now perform a search using natural language directly
        print("\nPart 2: Perform a search using natural language")
        print("\nSearching for: 'show me network connections'")

        results = chronicle.nl_search(
            text="show me network connections",
            start_time=start_time,
            end_time=end_time,
            max_events=5,
        )

        total_events = results.get("total_events", 0)
        events_list = results.get("events", [])
        print(f"\nFound {total_events} events")

        if events_list:
            print("\nFirst event details:")
            pprint(events_list[0])
        else:
            print("\nNo events found for this query.")

        # Try a more specific query
        print("\nPart 3: More specific natural language search")
        print("\nSearching for: 'show me inbound connections to port 443'")

        specific_results = chronicle.nl_search(
            text="show me inbound connections to port 443",
            start_time=start_time,
            end_time=end_time,
            max_events=5,
        )

        specific_total_events = specific_results.get("total_events", 0)
        specific_events_list = specific_results.get("events", [])
        print(f"\nFound {specific_total_events} events")

        if specific_events_list:
            print("\nFirst event details:")
            pprint(specific_events_list[0])
        else:
            print("\nNo events found for this specific query.")

    except APIError as e:
        if "no valid query could be generated" in str(e):
            print(f"\nAPI returned an expected error: {str(e)}")
            print("\nTry using a different phrasing or more specific language.")
            print("Examples of good queries:")
            print("- 'show me all network connections'")
            print("- 'find authentication events'")
            print("- 'show me file modification events'")
        else:
            print(f"API Error: {str(e)}")


def example_log_ingestion(chronicle):
    """Example 10: Log Ingestion."""
    print("\n=== Example 10: Log Ingestion ===")

    # Get current time for examples
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create a sample OKTA log to ingest
    okta_log = {
        "actor": {
            "alternateId": "oshamir1@cymbal-investments.org",
            "detail": None,
            "displayName": "Joe Doe",
            "id": "00u4j7xcb5N6zfiRP5d9",
            "type": "User",
        },
        "client": {
            "userAgent": {
                "rawUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
                "os": "Mac OS X",
                "browser": "SAFARI",
            },
            "zone": "null",
            "device": "Computer",
            "id": None,
            "ipAddress": "159.250.183.180",
            "geographicalContext": {
                "city": "Miami",
                "state": "Florida",
                "country": "United States",
                "postalCode": "33131",
                "geolocation": {"lat": 25.7634, "lon": -80.1886},
            },
        },
        "authenticationContext": {
            "authenticationProvider": None,
            "credentialProvider": None,
            "credentialType": None,
            "issuer": None,
            "interface": None,
            "authenticationStep": 0,
            "externalSessionId": "102VLe8EG5zT2yawpoqTqalcA",
        },
        "displayMessage": "User login to Okta",
        "eventType": "user.session.start",
        "outcome": {"result": "SUCCESS", "reason": None},
        "published": current_time,
        "securityContext": {
            "asNumber": 11776,
            "asOrg": "atlantic broadband",
            "isp": "atlantic broadband finance llc",
            "domain": "atlanticbb.net",
            "isProxy": False,
        },
        "severity": "INFO",
        "debugContext": {
            "debugData": {
                "dtHash": "57e8b514704467a0b0d82a96331c8082a94540c2cab5eb838250fb06d3939f11",
                "behaviors": "{New Geo-Location=NEGATIVE, New Device=POSITIVE, New IP=POSITIVE, New State=NEGATIVE, New Country=NEGATIVE, Velocity=NEGATIVE, New City=POSITIVE}",
                "requestId": "Xfxq0rWgTpMflVcjGjapWAtABNA",
                "requestUri": "/api/v1/authn",
                "threatSuspected": "true",
                "url": "/api/v1/authn?",
            }
        },
        "legacyEventType": "core.user_auth.login_success",
        "transaction": {
            "type": "WEB",
            "id": "Xfxq0rWgTpMflVcjGjapWAtABNA",
            "detail": {},
        },
        "uuid": "661c6bda-12f2-11ea-84eb-2b5358b2525a",
        "version": "0",
        "request": {
            "ipChain": [
                {
                    "ip": "159.250.183.180",
                    "geographicalContext": {
                        "city": "Miami",
                        "state": "Florida",
                        "country": "United States",
                        "postalCode": "33131",
                        "geolocation": {"lat": 24.7634, "lon": -81.1666},
                    },
                    "version": "V4",
                    "source": None,
                }
            ]
        },
        "target": None,
    }

    try:
        print("\nPart 1: Creating or Finding a Forwarder")
        forwarder = chronicle.get_or_create_forwarder(
            display_name="Wrapper-SDK-Forwarder"
        )
        print(f"Using forwarder: {forwarder.get('displayName', 'Unknown')}")

        print("\nPart 2: Ingesting OKTA Log (JSON format)")
        print("Ingesting OKTA log with timestamp:", current_time)

        result = chronicle.ingest_log(log_type="OKTA", log_message=json.dumps(okta_log))

        print("\nLog ingestion successful!")
        print(f"Operation ID: {result.get('operation', 'Unknown')}")

        # Example of ingesting a Windows Event XML log
        print("\nPart 3: Ingesting Windows Event Log (XML format)")

        # Create a Windows Event XML log with current timestamp
        # Use proper XML structure with <System> tags
        xml_content = f"""<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'>
  <System>
    <Provider Name='Microsoft-Windows-Security-Auditing' Guid='{{54849625-5478-4994-A5BA-3E3B0328C30D}}'/>
    <EventID>4624</EventID>
    <Version>1</Version>
    <Level>0</Level>
    <Task>12544</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8020000000000000</Keywords>
    <TimeCreated SystemTime='{current_time}'/>
    <EventRecordID>202117513</EventRecordID>
    <Correlation/>
    <Execution ProcessID='656' ThreadID='700'/>
    <Channel>Security</Channel>
    <Computer>WINSQLPRD354.xyz.net</Computer>
    <Security/>
  </System>
  <EventData>
    <Data Name='SubjectUserSid'>S-1-0-0</Data>
    <Data Name='SubjectUserName'>-</Data>
    <Data Name='SubjectDomainName'>-</Data>
    <Data Name='SubjectLogonId'>0x0</Data>
    <Data Name='TargetUserSid'>S-1-5-21-3666632573-2959896787-3198913328-396976</Data>
    <Data Name='TargetUserName'>svcECM15Search</Data>
    <Data Name='TargetDomainName'>XYZ</Data>
    <Data Name='TargetLogonId'>0x2cc559155</Data>
    <Data Name='LogonType'>3</Data>
    <Data Name='LogonProcessName'>NtLmSsp </Data>
    <Data Name='AuthenticationPackageName'>NTLM</Data>
    <Data Name='WorkstationName'>OKCFSTPRD402</Data>
    <Data Name='LogonGuid'>{{00000000-0000-0000-0000-000000000000}}</Data>
    <Data Name='TransmittedServices'>-</Data>
    <Data Name='LmPackageName'>NTLM V1</Data>
    <Data Name='KeyLength'>128</Data>
    <Data Name='ProcessId'>0x1</Data>
    <Data Name='ProcessName'>-</Data>
    <Data Name='IpAddress'>-</Data>
    <Data Name='IpPort'>-</Data>
    <Data Name='ImpersonationLevel'>%%1833</Data>
  </EventData>
</Event>"""

        print("Ingesting Windows Event log with timestamp:", current_time)

        win_result = chronicle.ingest_log(
            log_type="WINEVTLOG_XML",
            log_message=xml_content,  # Note: XML is passed directly, no json.dumps()
        )

        print("\nWindows Event log ingestion successful!")
        print(f"Operation ID: {win_result.get('operation', 'Unknown')}")

        print("\nPart 4: Listing Available Log Types")
        # Get the first 5 log types for display
        log_types = chronicle.get_all_log_types()[:5]
        print(
            f"\nFound {len(chronicle.get_all_log_types())} log types. First 5 examples:"
        )

        for lt in log_types:
            print(f"- {lt.id}: {lt.description}")

        print("\nTip: You can search for specific log types:")
        print('search_result = chronicle.search_log_types("firewall")')

    except Exception as e:
        print(f"\nError during log ingestion: {e}")


def example_udm_ingestion(chronicle):
    """Example 11: UDM Event Ingestion."""
    print("\n=== Example 11: UDM Event Ingestion ===")

    # Generate current time in ISO 8601 format
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        print("\nPart 1: Creating and Ingesting a Single UDM Event")

        # Generate unique ID
        event_id = str(uuid.uuid4())

        # Create a network connection UDM event
        network_event = {
            "metadata": {
                "id": event_id,
                "eventTimestamp": current_time,
                "eventType": "NETWORK_CONNECTION",
                "productName": "SecOps SDK Example",
                "vendorName": "Google",
            },
            "principal": {
                "hostname": "workstation-1",
                "ip": "192.168.1.100",
                "port": 52734,
            },
            "target": {"ip": "203.0.113.10", "port": 443},
            "network": {"applicationProtocol": "HTTPS", "direction": "OUTBOUND"},
        }

        print(f"Created network connection event with ID: {event_id}")
        print(f"Event type: {network_event['metadata']['eventType']}")
        print(f"Timestamp: {network_event['metadata']['eventTimestamp']}")

        # Ingest the single event
        result = chronicle.ingest_udm(udm_events=network_event)
        print("\nSuccessfully ingested single UDM event!")
        print(f"API Response: {result}")

        print("\nPart 2: Ingesting Multiple UDM Events")

        # Create a second event - process launch
        process_id = str(uuid.uuid4())
        process_event = {
            "metadata": {
                "id": process_id,
                "eventTimestamp": current_time,
                "eventType": "PROCESS_LAUNCH",
                "productName": "SecOps SDK Example",
                "vendorName": "Google",
            },
            "principal": {
                "hostname": "workstation-1",
                "process": {
                    "commandLine": "python example.py",
                    "pid": "12345",
                    "file": {"fullPath": "/usr/bin/python3"},
                },
                "user": {"userid": "user123"},
            },
            "target": {"process": {"pid": "0", "commandLine": "bash"}},
        }

        print(f"Created process launch event with ID: {process_id}")

        # Ingest both events together
        result = chronicle.ingest_udm(udm_events=[network_event, process_event])
        print("\nSuccessfully ingested multiple UDM events!")
        print(f"API Response: {result}")

        print("\nPart 3: Auto-generating Event IDs")

        # Create an event without an ID
        file_event = {
            "metadata": {
                "eventTimestamp": current_time,
                "eventType": "FILE_READ",
                "productName": "SecOps SDK Example",
                "vendorName": "Google",
                # No ID provided - will be auto-generated
            },
            "principal": {"hostname": "workstation-1", "user": {"userid": "user123"}},
            "target": {"file": {"fullPath": "/etc/passwd", "size": "4096"}},
        }

        print("Created file read event without ID (will be auto-generated)")

        # Ingest with auto-ID generation
        result = chronicle.ingest_udm(udm_events=file_event)
        print("\nSuccessfully ingested event with auto-generated ID!")
        print(f"API Response: {result}")

        print(
            "\nUDM events are structured security telemetry in Chronicle's Unified Data Model format."
        )
        print("Benefits of using UDM events directly:")
        print("- No need to format data as raw logs")
        print("- Structured data with semantic meaning")
        print("- Already normalized for Chronicle analytics")
        print("- Supports multiple event types in a single request")

    except APIError as e:
        print(f"\nError during UDM ingestion: {e}")


def example_gemini(chronicle):
    """Example 11: Chronicle Gemini AI."""
    print("\n=== Example 11: Chronicle Gemini AI ===")

    try:
        # First, explicitly opt-in to Gemini (optional, as gemini() will do this automatically)
        print("\nPart 1: Opting in to Gemini")
        try:
            opt_in_result = chronicle.opt_in_to_gemini()
            if opt_in_result:
                print("Successfully opted in to Gemini")
            else:
                print(
                    "Unable to opt-in due to permission issues (will try automatically later)"
                )
        except Exception as e:
            print(f"Error during opt-in: {e}")
            print("Will continue and let gemini() handle opt-in automatically")

        print("\nPart 2: Ask a security question")
        print("Asking: What is Windows event ID 4625?")

        try:
            # Query Gemini with a security question
            response = chronicle.gemini("What is Windows event ID 4625?")
            print(f"\nResponse object: {response}")

            # Display raw response information
            print("\nAccessing raw API response:")
            raw_response = response.get_raw_response()
            if raw_response:
                print(
                    f"- Raw response contains {len(raw_response.keys())} top-level keys"
                )
                if "responses" in raw_response:
                    response_blocks = sum(
                        len(resp.get("blocks", []))
                        for resp in raw_response["responses"]
                    )
                    print(f"- Total blocks in raw response: {response_blocks}")

            if hasattr(response, "raw_response"):
                print("\nRaw API response (first 1000 chars):")
                raw_str = str(response.raw_response)
                print(raw_str[:1000] + ("..." if len(raw_str) > 1000 else ""))

            # Display the types of content blocks received
            print(f"\nReceived {len(response.blocks)} content blocks")
            block_types = [block.block_type for block in response.blocks]
            print(f"Block types in response: {block_types}")

            # Print details for each block
            print("\nDetailed block information:")
            for i, block in enumerate(response.blocks):
                print(f"  Block {i+1}:")
                print(f"    Type: {block.block_type}")
                print(f"    Title: {block.title}")
                print(f"    Content length: {len(block.content)} chars")
                print(
                    f"    Content preview: {block.content[:100]}..."
                    if len(block.content) > 100
                    else f"    Content: {block.content}"
                )

            # Display text content
            text_content = response.get_text_content()
            if text_content:
                print("\nText explanation (from both TEXT and HTML blocks):")
                # Truncate long responses for display
                max_length = 300
                if len(text_content) > max_length:
                    print(f"{text_content[:max_length]}... (truncated)")
                else:
                    print(text_content)

            # Display HTML content (if present)
            html_blocks = response.get_html_blocks()
            if html_blocks:
                print(
                    f"\nFound {len(html_blocks)} HTML blocks (HTML tags included here)"
                )
                for i, block in enumerate(html_blocks):
                    print(
                        f"  HTML Block {i+1} preview: {block.content[:100]}..."
                        if len(block.content) > 100
                        else f"  HTML Block {i+1}: {block.content}"
                    )

            # Display references (if present)
            if response.references:
                print(f"\nFound {len(response.references)} references")
                for i, ref in enumerate(response.references):
                    print(f"  Reference {i+1} type: {ref.block_type}")
                    print(
                        f"  Reference {i+1} preview: {ref.content[:100]}..."
                        if len(ref.content) > 100
                        else f"  Reference {i+1}: {ref.content}"
                    )

            # Part 3: Generate a detection rule
            print("\nPart 3: Generate a detection rule")
            print(
                "Asking: Write a rule to detect powershell downloading a file called gdp.zip"
            )

            rule_response = chronicle.gemini(
                "Write a rule to detect powershell downloading a file called gdp.zip"
            )
            print(f"\nRule generation response object: {rule_response}")

            # Print detailed info about rule response blocks
            print(
                f"\nReceived {len(rule_response.blocks)} content blocks in rule response"
            )
            rule_block_types = [block.block_type for block in rule_response.blocks]
            print(f"Block types in rule response: {rule_block_types}")

            # Print details for each rule response block
            print("\nDetailed rule response block information:")
            for i, block in enumerate(rule_response.blocks):
                print(f"  Block {i+1}:")
                print(f"    Type: {block.block_type}")
                print(f"    Title: {block.title}")
                print(f"    Content length: {len(block.content)} chars")
                content_preview = (
                    block.content[:100] + "..."
                    if len(block.content) > 100
                    else block.content
                )
                print(f"    Content preview: {content_preview}")
                if block.block_type == "CODE" or "rule" in str(block.content).lower():
                    print(f"    Full content:\n{block.content}")

            # Get code blocks that contain the rule
            code_blocks = rule_response.get_code_blocks()
            if code_blocks:
                print(f"\nFound {len(code_blocks)} code blocks")

                # Display the first code block (the rule)
                rule_block = code_blocks[0]
                if rule_block.title:
                    print(f"\nRule title: {rule_block.title}")

                print("\nGenerated rule:")
                print(rule_block.content)
            else:
                print("\nNo dedicated code blocks found in the response")
                # Try to find rule content in other blocks
                for block in rule_response.blocks:
                    if (
                        "rule" in block.content.lower()
                        and "events:" in block.content.lower()
                    ):
                        print(f"\nPossible rule found in {block.block_type} block:")
                        print(block.content)
                        break

            # Display suggested actions (if present)
            if rule_response.suggested_actions:
                print(
                    f"\nFound {len(rule_response.suggested_actions)} suggested actions:"
                )
                for action in rule_response.suggested_actions:
                    print(f"  - {action.display_text} ({action.action_type})")
                    if action.navigation:
                        print(f"    Target: {action.navigation.target_uri}")

            # Part 4: Ask about a CVE
            print("\nPart 4: Ask about a CVE")
            print("Asking: tell me about CVE 2025 3310")

            cve_response = chronicle.gemini("tell me about CVE 2025 3310")

            # Display text content
            cve_text = cve_response.get_text_content()
            if cve_text:
                print("\nCVE Information (from both TEXT and HTML blocks):")
                # Truncate long responses for display
                max_length = 300
                if len(cve_text) > max_length:
                    print(f"{cve_text[:max_length]}... (truncated)")
                else:
                    print(cve_text)

            print(
                "\nThe Gemini API provides structured responses with different content types:"
            )
            print("- TEXT: Plain text for explanations and answers")
            print("- CODE: Code blocks for rules, scripts, and examples")
            print("- HTML: Formatted HTML content with rich formatting")
            print(
                "- get_text_content() combines TEXT blocks and strips HTML from HTML blocks"
            )
            print("It also provides references, suggested actions, and more.")

        except Exception as e:
            if "users must opt-in before using Gemini" in str(e):
                print("\nERROR: User account has not been opted-in to Gemini.")
                print(
                    "You must enable Gemini in Chronicle settings before using this feature."
                )
                print("Please check your Chronicle settings to opt-in to Gemini.")
            else:
                raise

    except Exception as e:
        print(f"\nError using Gemini API: {e}")


def example_parser_workflow(chronicle):
    """Example 12: Parser Workflow - Retrieve, Run, and Ingest UDM."""
    print("\n=== Example 12: Parser Workflow - Retrieve, Run, and Ingest UDM ===")

    # Sample OKTA log for testing
    okta_log = {
        "actor": {
            "alternateId": "mark.taylor@cymbal-investments.org",
            "detail": None,
            "displayName": "Mark Taylor",
            "id": "00u4j7xcb5N6zfiRP5d8",
            "type": "User",
        },
        "client": {
            "userAgent": {
                "rawUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
                "os": "Windows 10",
                "browser": "CHROME",
            },
            "zone": "null",
            "device": "Computer",
            "id": None,
            "ipAddress": "96.6.127.53",
            "geographicalContext": {
                "city": "New York",
                "state": "New York",
                "country": "United States",
                "postalCode": "10118",
                "geolocation": {"lat": 40.7123, "lon": -74.0068},
            },
        },
        "device": None,
        "authenticationContext": {
            "authenticationProvider": None,
            "credentialProvider": None,
            "credentialType": None,
            "issuer": None,
            "interface": None,
            "authenticationStep": 0,
            "externalSessionId": "unknown",
        },
        "displayMessage": "Max sign in attempts exceeded",
        "eventType": "user.account.lock",
        "outcome": {"result": "FAILURE", "reason": "LOCKED_OUT"},
        "published": "2025-06-19T21:51:50.116Z",
        "securityContext": {
            "asNumber": 20940,
            "asOrg": "akamai technologies  inc.",
            "isp": "akamai international b.v.",
            "domain": "akamaitechnologies.com",
            "isProxy": False,
        },
        "severity": "DEBUG",
        "debugContext": {
            "debugData": {
                "requestId": "ATQ6Qmlk2BHFAQGVUY1BfBAVDyI",
                "dtHash": "ab9606c02972cf1f1308deee3ab6f82a18e84d6eef5f6d8de94c90175c087524",
                "requestUri": "/api/v1/authn",
                "threatSuspected": "false",
                "targetEventHookIds": "who3p0a3y5uKucF8I0g7,who3p0a3y5uKucF8I0g8",
                "url": "/api/v1/authn?",
            }
        },
        "legacyEventType": "core.user_auth.account_locked",
        "transaction": {
            "type": "WEB",
            "id": "ATQ6Qmlk2BHFAQGVUY1BfBAVDyI",
            "detail": {},
        },
        "uuid": "5b90a94a-d7ba-11ea-834a-85c24a1b2121",
        "version": "0",
        "request": {
            "ipChain": [
                {
                    "ip": "96.6.127.53",
                    "geographicalContext": {
                        "city": "New York",
                        "state": "New York",
                        "country": "United States",
                        "postalCode": "10118",
                        "geolocation": {"lat": 40.7123, "lon": -74.0068},
                    },
                    "version": "V4",
                    "source": None,
                }
            ]
        },
        "target": None,
    }

    try:
        print("\nStep 1: List OKTA parsers to find the active parser")
        # List parsers for OKTA log type
        parsers = chronicle.list_parsers(log_type="OKTA")
        print(f"Found {len(parsers)} OKTA parsers")

        # Find an active parser (or any parser if no active one)
        active_parser = None
        any_parser = None

        for parser in parsers:
            parser_id = parser.get("name", "").split("/")[-1]
            state = parser.get("state", "")
            print(f"  Parser {parser_id}: state={state}")

            if state == "ACTIVE":
                active_parser = parser
                break
            elif not any_parser:
                any_parser = parser

        # Use active parser if found, otherwise use any parser
        selected_parser = active_parser or any_parser

        if not selected_parser:
            print(
                "\nNo OKTA parsers found. This example requires at least one OKTA parser."
            )
            return

        parser_id = selected_parser.get("name", "").split("/")[-1]
        parser_state = selected_parser.get("state", "")
        print(f"\nUsing parser {parser_id} (state: {parser_state})")

        print("\nStep 2: Retrieve the parser details")
        # Get the full parser details
        parser_details = chronicle.get_parser(log_type="OKTA", id=parser_id)

        # Extract parser code
        parser_code = parser_details.get("cbn", "")
        if parser_code:
            # Decode from base64
            import base64

            try:
                parser_code = base64.b64decode(parser_code).decode("utf-8")
            except:
                pass  # Already decoded

        print(f"\nParser code (first 500 chars):")
        print(parser_code[:500] + "..." if len(parser_code) > 500 else parser_code)

        print("\nStep 3: Run the parser against the sample OKTA log")
        # Convert log to JSON string
        log_json = json.dumps(okta_log)
        print(f"\nLog to parse (first 200 chars): {log_json[:200]}...")

        # Run the parser
        parser_result = chronicle.run_parser(
            log_type="OKTA",
            parser_code=parser_code,
            parser_extension_code=None,
            logs=[log_json],
        )

        print("\nStep 4: Examine the parsed output")
        run_parser_results = parser_result.get("runParserResults", [])
        if run_parser_results:
            for i, result in enumerate(run_parser_results):
                print(f"\nResult for log {i+1}:")

                errors = result.get("errors", [])
                if errors:
                    print(f"  Parsing errors: {errors}")

                parsed_events_data = result.get("parsedEvents", {})

                # Handle the structure - parsedEvents is a dict with 'events' key
                if (
                    isinstance(parsed_events_data, dict)
                    and "events" in parsed_events_data
                ):
                    parsed_events = parsed_events_data["events"]
                else:
                    # In case it's already a list (backward compatibility)
                    parsed_events = (
                        parsed_events_data
                        if isinstance(parsed_events_data, list)
                        else []
                    )

                print(f"  Number of parsed events: {len(parsed_events)}")

                # Extract UDM events
                udm_events = []
                for event in parsed_events:
                    # The parsed event might be the UDM event directly or wrapped in an "event" key
                    if isinstance(event, dict):
                        if "event" in event:
                            udm_event = event["event"]
                        else:
                            udm_event = event

                        udm_events.append(udm_event)

                        # Print a summary of the UDM event
                        print(f"\n  Parsed UDM event summary:")
                        metadata = udm_event.get("metadata", {})
                        if metadata:
                            print(f"    Event Type: {metadata.get('eventType', 'N/A')}")
                            print(f"    Product: {metadata.get('productName', 'N/A')}")
                            print(f"    Vendor: {metadata.get('vendorName', 'N/A')}")
                            print(
                                f"    Event Time: {metadata.get('eventTimestamp', 'N/A')}"
                            )

                        principal = udm_event.get("principal", {})
                        if principal:
                            user = principal.get("user", {})
                            if isinstance(user, dict):
                                print(f"    User: {user.get('userid', 'N/A')}")
                            ip_value = principal.get("ip", "N/A")
                            if isinstance(ip_value, list) and ip_value:
                                print(f"    Source IP: {ip_value[0]}")
                            elif isinstance(ip_value, str):
                                print(f"    Source IP: {ip_value}")

                        security_results = udm_event.get("securityResult", [])
                        if isinstance(security_results, list) and security_results:
                            security = security_results[0]
                            print(f"    Action: {security.get('action', 'N/A')}")
                            print(f"    Summary: {security.get('summary', 'N/A')}")

                if udm_events:
                    print(f"\nStep 5: Ingest the parsed UDM events")
                    print(f"Ingesting {len(udm_events)} UDM event(s)...")

                    try:
                        # Ingest the UDM events
                        ingest_result = chronicle.ingest_udm(
                            udm_events=(
                                udm_events[0] if len(udm_events) == 1 else udm_events
                            )
                        )

                        print("\nUDM ingestion successful!")
                        print(f"API Response: {ingest_result}")

                        # Print the full UDM event for reference
                        print("\nFull UDM event that was ingested:")
                        udm_json = json.dumps(udm_events[0], indent=2)
                        if len(udm_json) > 1000:
                            print(udm_json[:1000] + "...")
                        else:
                            print(udm_json)

                    except Exception as e:
                        print(f"\nError ingesting UDM events: {e}")
                        print(
                            "This might happen if the parsed event doesn't have required UDM fields."
                        )
                else:
                    print("\nNo UDM events were extracted from the parser output.")
        else:
            print("\nNo parser results returned.")

        print("\n" + "=" * 80)
        print("This example demonstrated the complete workflow:")
        print("1. Retrieved an OKTA parser from Chronicle")
        print("2. Displayed the parser code")
        print("3. Ran the parser against a sample OKTA log")
        print("4. Examined the parsed UDM output")
        print("5. Ingested the parsed UDM event back into Chronicle")
        print("\nThis workflow is useful for:")
        print("- Testing parsers before deployment")
        print("- Understanding how logs are transformed to UDM")
        print("- Debugging parsing issues")
        print("- Re-processing logs with updated parsers")

    except APIError as e:
        print(f"\nAPI Error: {e}")
        print("\nTroubleshooting tips:")
        print("- Ensure OKTA log type has at least one parser")
        print("- Check if you have permissions to access parsers")
        print("- Verify the parser is properly configured")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


def example_fetch_parser_candidates(chronicle):
    """Example 13: Fetch Parser Candidates for a log type."""
    print("\n=== Example 13: Fetch Parser Candidates ===")

    log_type = "OKTA"
    parser_action = "PARSER_ACTION_OPT_IN_TO_PREVIEW"

    try:
        print(
            f"\nFetching parser candidates for log type '{log_type}' "
            f"with action '{parser_action}'..."
        )
        candidates = chronicle.fetch_parser_candidates(
            log_type=log_type,
            parser_action=parser_action,
        )

        if not candidates:
            print(f"No parser candidates found for log type '{log_type}'.")
            return

        print(f"Found {len(candidates)} parser candidate(s):")
        for candidate in candidates:
            name = candidate.get("name", "N/A")
            state = candidate.get("state", "N/A")
            parser_id = name.split("/")[-1]
            print(f"  - ID: {parser_id}, State: {state}")

    except APIError as e:
        print(f"\nAPI Error: {e}")
        print("\nTroubleshooting tips:")
        print(
            "- Ensure the log type supports prebuilt parser candidates"
        )
        print("- Check if you have the required permissions")
    except ValueError as e:
        print(f"\nInvalid input: {e}")


def example_rule_test(chronicle):
    """Example 14: Test a detection rule against historical data."""
    print("\n=== Example 14: Test a Detection Rule Against Historical Data ===")

    # Define time range for testing - use a recent time period (last 7 days)
    end_time = datetime.now(timezone.utc) - timedelta(minutes=15)
    start_time = end_time - timedelta(days=7)  # Test against last 7 days

    # Create a simple rule that should find network connection events
    test_rule = """
rule test_network_connections {
  meta:
    description = "Test rule for finding network connection events"
    author = "SecOps SDK Example"
    severity = "Informational" 
    yara_version = "YL2.0"
    rule_version = "1.0"
  events:
    $e.metadata.event_type = "NETWORK_CONNECTION"
  condition:
    $e
}
"""
    print(f"Testing rule against data from {start_time} to {end_time}")
    print("Rule text:")
    print(test_rule)
    print("\nSearching for matching events...")

    # Collect UDM events from rule test results
    udm_events = []

    for result in chronicle.run_rule_test(
        test_rule, start_time, end_time, max_results=5
    ):
        if result.get("type") == "detection":
            detection = result.get("detection", {})
            result_events = detection.get("resultEvents", {})

            # Extract UDM events from resultEvents structure
            for var_name, var_data in result_events.items():
                event_samples = var_data.get("eventSamples", [])
                for sample in event_samples:
                    event = sample.get("event")
                    if event:
                        udm_events.append(event)

    # Print results
    print(f"\nFound {len(udm_events)} UDM events matching the rule:")

    if udm_events:
        print("\nUDM Events (pretty-printed JSON):")
        print("=" * 80)

        for i, event in enumerate(udm_events, 1):
            print(f"\nEvent {i}:")
            print(json.dumps(event, indent=2, default=str))
            print("-" * 40)
    else:
        print("No events found matching the rule in the specified time range.")
        print("Try adjusting the time range or rule criteria.")

    return "Rule testing complete"


# Map of example functions
EXAMPLES = {
    "1": example_udm_search,
    "2": example_stats_query,
    "3": example_entity_summary,
    "4": example_csv_export,
    "5": example_list_iocs,
    "6": example_alerts_and_cases,
    "7": example_validate_query,
    "8": example_nl_search,
    "9": example_log_ingestion,
    "10": example_udm_ingestion,
    "11": example_gemini,
    "12": example_parser_workflow,
    "13": example_fetch_parser_candidates,
    "14": example_rule_test,
    "15": example_udm_search_view,
}


def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(description="Run Chronicle API examples")
    parser.add_argument("--project_id", required=True, help="Google Cloud Project ID")
    parser.add_argument(
        "--customer_id", required=True, help="Chronicle Customer ID (UUID)"
    )
    parser.add_argument("--region", default="us", help="Chronicle region (us or eu)")
    parser.add_argument(
        "--example",
        "-e",
        help="Example number to run (1-15). If not specified, runs all examples.",
    )

    args = parser.parse_args()

    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)

    if args.example:
        if args.example not in EXAMPLES:
            print(
                f"Invalid example number. Available examples: {', '.join(EXAMPLES.keys())}"
            )
            return
        EXAMPLES[args.example](chronicle)
    else:
        # Run all examples in order
        for example_num in sorted(EXAMPLES.keys()):
            EXAMPLES[example_num](chronicle)


if __name__ == "__main__":
    main()
