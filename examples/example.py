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
        customer_id=customer_id,
        project_id=project_id,
        region=region
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
            max_events=5
        )
        
        print(f"\nFound {events['total_events']} events")
        if events['events']:
            print("\nFirst event details:")
            event = events['events'][0]
            print(f"Event name: {event.get('name', 'N/A')}")
            # Extract metadata from UDM
            metadata = event.get('udm', {}).get('metadata', {})
            print(f"Event type: {metadata.get('eventType', 'N/A')}")
            print(f"Event timestamp: {metadata.get('eventTimestamp', 'N/A')}")
            
            # Show IP information if available
            principal_ip = event.get('udm', {}).get('principal', {}).get('ip', ['N/A'])[0]
            target_ip = event.get('udm', {}).get('target', {}).get('ip', ['N/A'])[0]
            print(f"Connection: {principal_ip} -> {target_ip}")
            
            print(f"\nMore data available: {events.get('more_data_available', False)}")
    except Exception as e:
        print(f"Error performing UDM search: {e}")

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
            max_values=10
        )
        print("\nTop hostnames by event count:")
        for row in stats['rows']:
            print(f"Hostname: {row.get('target.hostname', 'N/A')}, Count: {row.get('count', 0)}")
    except Exception as e:
        print(f"Error performing stats query: {e}")

def example_entity_summary(chronicle):
    """Example 3: Entity Summary (IP, Domain, Hash)."""
    print("\n=== Example 3: Entity Summary ===")
    start_time, end_time = get_time_range()
    
    entities_to_summarize = {
        "IP Address": "8.8.8.8",
        "Domain": "google.com",
        "File Hash (SHA256)": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Empty file hash
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
                    print(f"  Domain Name: {summary.primary_entity.entity['domain']['name']}")
                elif "md5" in summary.primary_entity.entity.get("file", {}):
                    print(f"  MD5: {summary.primary_entity.entity['file']['md5']}")
                elif "sha256" in summary.primary_entity.entity.get("file", {}):
                     print(f"  SHA256: {summary.primary_entity.entity['file']['sha256']}")
            else:
                 print("\nNo primary entity found.")

            if summary.related_entities:
                print(f"\nRelated Entities ({len(summary.related_entities)} found):")
                for rel_entity in summary.related_entities[:3]: # Show first 3
                    print(f"  - Type: {rel_entity.metadata.entity_type}")

            if summary.alert_counts:
                print("\nAlert Counts:")
                for alert in summary.alert_counts:
                    print(f"  Rule: {alert.rule}, Count: {alert.count}")

            if summary.timeline:
                print(f"\nTimeline: {len(summary.timeline.buckets)} buckets (size: {summary.timeline.bucket_size})")

            if summary.prevalence:
                print(f"\nPrevalence ({len(summary.prevalence)} entries):")
                # Show first entry
                print(f"  Time: {summary.prevalence[0].prevalence_time}, Count: {summary.prevalence[0].count}")

            if summary.file_metadata_and_properties:
                print("\nFile Properties:")
                if summary.file_metadata_and_properties.metadata:
                    print("  Metadata:")
                    for prop in summary.file_metadata_and_properties.metadata[:2]: # Show first 2
                        print(f"    {prop.key}: {prop.value}")
                if summary.file_metadata_and_properties.properties:
                     print("  Properties:")
                     for group in summary.file_metadata_and_properties.properties:
                         print(f"    {group.title}:")
                         for prop in group.properties[:2]: # Show first 2 per group
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
            fields=[
                "timestamp",
                "user",
                "hostname",
                "process name"
            ]
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
            start_time=start_time,
            end_time=end_time,
            max_matches=10000
        )
        
        print(f"\nFound {len(iocs['matches'])} IoC matches")
        if iocs['matches']:
            print("\nFirst IoC details:")
            first_ioc = iocs['matches'][0]
            print(f"Type: {next(iter(first_ioc['artifactIndicator'].keys()))}")
            print(f"Value: {next(iter(first_ioc['artifactIndicator'].values()))}")
            print(f"Sources: {', '.join(first_ioc['sources'])}")
    except APIError as e:
        print(f"Error: {str(e)}")

def example_alerts_and_cases(chronicle):
    """Example 6: Alerts and Cases."""
    print("\n=== Example 6: Alerts and Cases ===")
    start_time, end_time = get_time_range()
    
    try:
        print("\nQuerying alerts (this may take a few moments)...")
        alerts = chronicle.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query="feedback_summary.status != \"CLOSED\"",
            max_alerts=10
        )
        
        alert_list = alerts.get('alerts', {}).get('alerts', [])
        print(f"\nNumber of alerts in response: {len(alert_list)}")
        
        # Debug: Print all alerts with cases
        print("\nDebug - Alerts with cases:")
        for i, alert in enumerate(alert_list):
            case_name = alert.get('caseName')
            if case_name:
                print(f"\nAlert {i+1}:")
                print(f"Case ID: {case_name}")
                print(f"Alert ID: {alert.get('id')}")
                print(f"Rule Name: {alert.get('detection', [{}])[0].get('ruleName')}")
                print(f"Created Time: {alert.get('createdTime')}")
                print(f"Status: {alert.get('feedbackSummary', {}).get('status')}")
        
        case_ids = {alert.get('caseName') for alert in alert_list if alert.get('caseName')}
        
        if case_ids:
            print(f"\nFound {len(case_ids)} unique case IDs:")
            print(list(case_ids))
            
            cases = chronicle.get_cases(list(case_ids))
            print(f"\nRetrieved {len(cases.cases)} cases:")
            for case in cases.cases:
                print(f"\nCase: {case.display_name}")
                print(f"ID: {case.id}")  # Add case ID for comparison
                print(f"Priority: {case.priority}")
                print(f"Stage: {case.stage}")
                print(f"Status: {case.status}")
                
                # Debug: Print all alerts for this case
                case_alerts = [
                    alert for alert in alert_list
                    if alert.get('caseName') == case.id
                ]
                print(f"Total Alerts for Case: {len(case_alerts)}")
                
                high_sev_alerts = [
                    alert for alert in case_alerts
                    if alert.get('feedbackSummary', {}).get('severityDisplay') == 'HIGH'
                ]
                if high_sev_alerts:
                    print(f"High Severity Alerts: {len(high_sev_alerts)}")
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
            'queryType' in result and 
            not result.get('errorText') and 
            not result.get('errorType')
        )
        
        print(f"Is valid: {is_valid}")
        print(f"Query type: {result.get('queryType', 'Unknown')}")
        
        if is_valid:
            print("✅ Query is valid")
        elif 'errorText' in result:
            print(f"❌ Validation error: {result['errorText']}")
        elif 'validationMessage' in result:
            print(f"❌ Validation error: {result['validationMessage']}")
            
        # Print the full response for debugging
        print(f"Full response: {result}")
    except APIError as e:
        print(f"Error validating query: {str(e)}")
    
    # Example 2: Invalid UDM Query
    try:
        print("\nValidating an incorrect UDM query:")
        invalid_query = 'metadata.event_type === "NETWORK_CONNECTION"'  # Triple equals is invalid
        
        print(f"Query: {invalid_query}")
        result = chronicle.validate_query(invalid_query)
        
        # More sophisticated validity check
        is_valid = (
            'queryType' in result and 
            not result.get('errorText') and 
            not result.get('errorType')
        )
        
        print(f"Is valid: {is_valid}")
        
        if is_valid:
            print("✅ Query is valid")
        elif 'errorText' in result:
            print(f"❌ Validation error: {result['errorText']}")
        elif 'validationMessage' in result:
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
            'queryType' in result and 
            not result.get('errorText') and 
            not result.get('errorType')
        )
        
        print(f"Is valid: {is_valid}")
        print(f"Query type: {result.get('queryType', 'Unknown')}")
        
        if is_valid:
            print("✅ Query is valid")
        elif 'errorText' in result:
            print(f"❌ Validation error: {result['errorText']}")
        elif 'validationMessage' in result:
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
            max_events=5
        )
        
        print(f"\nFound {results['total_events']} events")
        if results['events']:
            print("\nFirst event details:")
            pprint(results['events'][0])
            
        # Try a more specific query
        print("\nPart 3: More specific natural language search")
        print("\nSearching for: 'show me inbound connections to port 443'")
        
        specific_results = chronicle.nl_search(
            text="show me inbound connections to port 443",
            start_time=start_time,
            end_time=end_time,
            max_events=5
        )
        
        print(f"\nFound {specific_results['total_events']} events")
        if specific_results['events']:
            print("\nFirst event details:")
            pprint(specific_results['events'][0])
        
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
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Create a sample OKTA log to ingest
    okta_log = {
        "actor": {
            "alternateId": "oshamir1@cymbal-investments.org",
            "detail": None,
            "displayName": "Joe Doe",
            "id": "00u4j7xcb5N6zfiRP5d9",
            "type": "User"
        },
        "client": {
            "userAgent": {
                "rawUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
                "os": "Mac OS X",
                "browser": "SAFARI"
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
                "geolocation": {
                    "lat": 25.7634,
                    "lon": -80.1886
                }
            }
        },
        "authenticationContext": {
            "authenticationProvider": None,
            "credentialProvider": None,
            "credentialType": None,
            "issuer": None,
            "interface": None,
            "authenticationStep": 0,
            "externalSessionId": "102VLe8EG5zT2yawpoqTqalcA"
        },
        "displayMessage": "User login to Okta",
        "eventType": "user.session.start",
        "outcome": {
            "result": "SUCCESS",
            "reason": None
        },
        "published": current_time,
        "securityContext": {
            "asNumber": 11776,
            "asOrg": "atlantic broadband",
            "isp": "atlantic broadband finance llc",
            "domain": "atlanticbb.net",
            "isProxy": False
        },
        "severity": "INFO",
        "debugContext": {
            "debugData": {
                "dtHash": "57e8b514704467a0b0d82a96331c8082a94540c2cab5eb838250fb06d3939f11",
                "behaviors": "{New Geo-Location=NEGATIVE, New Device=POSITIVE, New IP=POSITIVE, New State=NEGATIVE, New Country=NEGATIVE, Velocity=NEGATIVE, New City=POSITIVE}",
                "requestId": "Xfxq0rWgTpMflVcjGjapWAtABNA",
                "requestUri": "/api/v1/authn",
                "threatSuspected": "true",
                "url": "/api/v1/authn?"
            }
        },
        "legacyEventType": "core.user_auth.login_success",
        "transaction": {
            "type": "WEB",
            "id": "Xfxq0rWgTpMflVcjGjapWAtABNA",
            "detail": {}
        },
        "uuid": "661c6bda-12f2-11ea-84eb-2b5358b2525a",
        "version": "0",
        "request": {
            "ipChain": [{
                "ip": "159.250.183.180",
                "geographicalContext": {
                    "city": "Miami",
                    "state": "Florida",
                    "country": "United States",
                    "postalCode": "33131",
                    "geolocation": {
                        "lat": 24.7634,
                        "lon": -81.1666
                    }
                },
                "version": "V4",
                "source": None
            }]
        },
        "target": None
    }
    
    try:
        print("\nPart 1: Creating or Finding a Forwarder")
        forwarder = chronicle.get_or_create_forwarder(display_name="Wrapper-SDK-Forwarder")
        print(f"Using forwarder: {forwarder.get('displayName', 'Unknown')}")
        
        print("\nPart 2: Ingesting OKTA Log (JSON format)")
        print("Ingesting OKTA log with timestamp:", current_time)
        
        result = chronicle.ingest_log(
            log_type="OKTA",
            log_message=json.dumps(okta_log)
        )
        
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
            log_message=xml_content  # Note: XML is passed directly, no json.dumps()
        )
        
        print("\nWindows Event log ingestion successful!")
        print(f"Operation ID: {win_result.get('operation', 'Unknown')}")
        
        print("\nPart 4: Listing Available Log Types")
        # Get the first 5 log types for display
        log_types = chronicle.get_all_log_types()[:5]
        print(f"\nFound {len(chronicle.get_all_log_types())} log types. First 5 examples:")
        
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
                "event_timestamp": current_time,
                "event_type": "NETWORK_CONNECTION",
                "product_name": "SecOps SDK Example",
                "vendor_name": "Google"
            },
            "principal": {
                "hostname": "workstation-1",
                "ip": "192.168.1.100",
                "port": 52734
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
        
        print(f"Created network connection event with ID: {event_id}")
        print(f"Event type: {network_event['metadata']['event_type']}")
        print(f"Timestamp: {network_event['metadata']['event_timestamp']}")
        
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
                "event_timestamp": current_time,
                "event_type": "PROCESS_LAUNCH",
                "product_name": "SecOps SDK Example",
                "vendor_name": "Google"
            },
            "principal": {
                "hostname": "workstation-1",
                "process": {
                    "command_line": "python example.py",
                    "pid": "12345",
                    "file": {
                        "full_path": "/usr/bin/python3"
                    }
                },
                "user": {
                    "userid": "user123"
                }
            },
            "target": {
                "process": {
                    "pid": "0",
                    "command_line": "bash"
                }
            }
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
                "event_timestamp": current_time,
                "event_type": "FILE_READ",
                "product_name": "SecOps SDK Example",
                "vendor_name": "Google"
                # No ID provided - will be auto-generated
            },
            "principal": {
                "hostname": "workstation-1",
                "user": {
                    "userid": "user123"
                }
            },
            "target": {
                "file": {
                    "full_path": "/etc/passwd",
                    "size": "4096"
                }
            }
        }
        
        print("Created file read event without ID (will be auto-generated)")
        
        # Ingest with auto-ID generation
        result = chronicle.ingest_udm(udm_events=file_event)
        print("\nSuccessfully ingested event with auto-generated ID!")
        print(f"API Response: {result}")
        
        print("\nUDM events are structured security telemetry in Chronicle's Unified Data Model format.")
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
                print("Unable to opt-in due to permission issues (will try automatically later)")
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
                print(f"- Raw response contains {len(raw_response.keys())} top-level keys")
                if "responses" in raw_response:
                    response_blocks = sum(len(resp.get("blocks", [])) for resp in raw_response["responses"])
                    print(f"- Total blocks in raw response: {response_blocks}")
            
            if hasattr(response, 'raw_response'):
                print("\nRaw API response (first 1000 chars):")
                raw_str = str(response.raw_response)
                print(raw_str[:1000] + ('...' if len(raw_str) > 1000 else ''))
            
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
                print(f"    Content preview: {block.content[:100]}..." if len(block.content) > 100 
                      else f"    Content: {block.content}")
            
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
                print(f"\nFound {len(html_blocks)} HTML blocks (HTML tags included here)")
                for i, block in enumerate(html_blocks):
                    print(f"  HTML Block {i+1} preview: {block.content[:100]}..." if len(block.content) > 100 
                          else f"  HTML Block {i+1}: {block.content}")
            
            # Display references (if present)
            if response.references:
                print(f"\nFound {len(response.references)} references")
                for i, ref in enumerate(response.references):
                    print(f"  Reference {i+1} type: {ref.block_type}")
                    print(f"  Reference {i+1} preview: {ref.content[:100]}..." if len(ref.content) > 100 
                          else f"  Reference {i+1}: {ref.content}")
            
            # Part 3: Generate a detection rule
            print("\nPart 3: Generate a detection rule")
            print("Asking: Write a rule to detect powershell downloading a file called gdp.zip")
            
            rule_response = chronicle.gemini("Write a rule to detect powershell downloading a file called gdp.zip")
            print(f"\nRule generation response object: {rule_response}")
            
            # Print detailed info about rule response blocks
            print(f"\nReceived {len(rule_response.blocks)} content blocks in rule response")
            rule_block_types = [block.block_type for block in rule_response.blocks]
            print(f"Block types in rule response: {rule_block_types}")
            
            # Print details for each rule response block
            print("\nDetailed rule response block information:")
            for i, block in enumerate(rule_response.blocks):
                print(f"  Block {i+1}:")
                print(f"    Type: {block.block_type}")
                print(f"    Title: {block.title}")
                print(f"    Content length: {len(block.content)} chars")
                content_preview = block.content[:100] + '...' if len(block.content) > 100 else block.content
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
                    if "rule" in block.content.lower() and "events:" in block.content.lower():
                        print(f"\nPossible rule found in {block.block_type} block:")
                        print(block.content)
                        break
            
            # Display suggested actions (if present)
            if rule_response.suggested_actions:
                print(f"\nFound {len(rule_response.suggested_actions)} suggested actions:")
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
                
            print("\nThe Gemini API provides structured responses with different content types:")
            print("- TEXT: Plain text for explanations and answers")
            print("- CODE: Code blocks for rules, scripts, and examples")
            print("- HTML: Formatted HTML content with rich formatting")
            print("- get_text_content() combines TEXT blocks and strips HTML from HTML blocks")
            print("It also provides references, suggested actions, and more.")
        
        except Exception as e:
            if "users must opt-in before using Gemini" in str(e):
                print("\nERROR: User account has not been opted-in to Gemini.")
                print("You must enable Gemini in Chronicle settings before using this feature.")
                print("Please check your Chronicle settings to opt-in to Gemini.")
            else:
                raise
        
    except Exception as e:
        print(f"\nError using Gemini API: {e}")

# Map of example functions
EXAMPLES = {
    '1': example_udm_search,
    '2': example_stats_query,
    '3': example_entity_summary,
    '4': example_csv_export,
    '5': example_list_iocs,
    '6': example_alerts_and_cases,
    '7': example_validate_query,
    '8': example_nl_search,
    '9': example_log_ingestion,
    '10': example_udm_ingestion,
    '11': example_gemini,
}

def main():
    """Main function to run examples."""
    parser = argparse.ArgumentParser(description='Run Chronicle API examples')
    parser.add_argument('--project_id', required=True, help='Google Cloud Project ID')
    parser.add_argument('--customer_id', required=True, help='Chronicle Customer ID (UUID)')
    parser.add_argument('--region', default='us', help='Chronicle region (us or eu)')
    parser.add_argument('--example', '-e', 
                      help='Example number to run (1-11). If not specified, runs all examples.')
    
    args = parser.parse_args()
    
    # Initialize the client
    chronicle = get_client(args.project_id, args.customer_id, args.region)
    
    if args.example:
        if args.example not in EXAMPLES:
            print(f"Invalid example number. Available examples: {', '.join(EXAMPLES.keys())}")
            return
        EXAMPLES[args.example](chronicle)
    else:
        # Run all examples in order
        for example_num in sorted(EXAMPLES.keys()):
            EXAMPLES[example_num](chronicle)

if __name__ == "__main__":
    main()
