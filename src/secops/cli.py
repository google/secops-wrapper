import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
import os
from typing import Optional, Dict, Any, List, Tuple, Union
from pathlib import Path

from secops import SecOpsClient
from secops.exceptions import SecOpsError, AuthenticationError, APIError


# Define config directory and file paths
CONFIG_DIR = Path.home() / ".secops"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from config file.
    
    Returns:
        Dictionary containing configuration values
    """
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print(f"Warning: Failed to load config from {CONFIG_FILE}", file=sys.stderr)
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config file.
    
    Args:
        config: Dictionary containing configuration values to save
    """
    # Create config directory if it doesn't exist
    CONFIG_DIR.mkdir(exist_ok=True)
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        print(f"Error: Failed to save config to {CONFIG_FILE}: {e}", file=sys.stderr)


def setup_config_command(subparsers):
    """Set up the config command parser.
    
    Args:
        subparsers: Subparsers object to add to
    """
    config_parser = subparsers.add_parser("config", help="Manage CLI configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config command")
    
    # Set config command
    set_parser = config_subparsers.add_parser("set", help="Set configuration values")
    set_parser.add_argument("--customer-id", "--customer_id", dest="customer_id", help="Chronicle instance ID")
    set_parser.add_argument("--project-id", "--project_id", dest="project_id", help="GCP project ID")
    set_parser.add_argument("--region", help="Chronicle API region")
    set_parser.add_argument("--service-account", "--service_account", dest="service_account", help="Path to service account JSON file")
    set_parser.add_argument("--start-time", "--start_time", dest="start_time", help="Default start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    set_parser.add_argument("--end-time", "--end_time", dest="end_time", help="Default end time in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    set_parser.add_argument("--time-window", "--time_window", dest="time_window", type=int, help="Default time window in hours")
    set_parser.set_defaults(func=handle_config_set_command)
    
    # View config command
    view_parser = config_subparsers.add_parser("view", help="View current configuration")
    view_parser.set_defaults(func=handle_config_view_command)
    
    # Clear config command
    clear_parser = config_subparsers.add_parser("clear", help="Clear current configuration")
    clear_parser.set_defaults(func=handle_config_clear_command)


def handle_config_set_command(args, chronicle=None):
    """Handle config set command.
    
    Args:
        args: Command line arguments
        chronicle: Not used for this command
    """
    config = load_config()
    
    # Update config with new values
    if args.customer_id:
        config["customer_id"] = args.customer_id
    if args.project_id:
        config["project_id"] = args.project_id
    if args.region:
        config["region"] = args.region
    if args.service_account:
        config["service_account"] = args.service_account
    if args.start_time:
        config["start_time"] = args.start_time
    if args.end_time:
        config["end_time"] = args.end_time
    if args.time_window is not None:
        config["time_window"] = args.time_window
    
    save_config(config)
    print(f"Configuration saved to {CONFIG_FILE}")


def handle_config_view_command(args, chronicle=None):
    """Handle config view command.
    
    Args:
        args: Command line arguments
        chronicle: Not used for this command
    """
    config = load_config()
    
    if not config:
        print("No configuration found.")
        return
    
    print("Current configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")


def handle_config_clear_command(args, chronicle=None):
    """Handle config clear command.
    
    Args:
        args: Command line arguments
        chronicle: Not used for this command
    """
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("Configuration cleared.")
    else:
        print("No configuration found.")


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string in ISO format.
    
    Args:
        dt_str: ISO formatted datetime string
        
    Returns:
        Parsed datetime object
    """
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))


def setup_client(args: argparse.Namespace) -> Tuple[SecOpsClient, Any]:
    """Set up and return SecOpsClient and Chronicle client based on args.
    
    Args:
        args: Command line arguments
        
    Returns:
        Tuple of (SecOpsClient, Chronicle client)
    """
    # Authentication setup
    client_kwargs = {}
    if args.service_account:
        client_kwargs["service_account_path"] = args.service_account
    
    # Create client
    try:
        client = SecOpsClient(**client_kwargs)
        
        # Initialize Chronicle client if required
        if hasattr(args, 'customer_id') or hasattr(args, 'project_id') or hasattr(args, 'region'):
            chronicle_kwargs = {}
            if hasattr(args, 'customer_id') and args.customer_id:
                chronicle_kwargs["customer_id"] = args.customer_id
            if hasattr(args, 'project_id') and args.project_id:
                chronicle_kwargs["project_id"] = args.project_id
            if hasattr(args, 'region') and args.region:
                chronicle_kwargs["region"] = args.region
            
            # Check if required args for Chronicle client are present
            missing_args = []
            if not chronicle_kwargs.get("customer_id"):
                missing_args.append("customer_id")
            if not chronicle_kwargs.get("project_id"):
                missing_args.append("project_id")
            
            if missing_args:
                print("Error: Missing required configuration parameters:", ", ".join(missing_args), file=sys.stderr)
                print("\nPlease run the config command to set up your configuration:", file=sys.stderr)
                print("  secops config set --customer-id YOUR_CUSTOMER_ID --project-id YOUR_PROJECT_ID", file=sys.stderr)
                print("\nOr provide them as command-line options:", file=sys.stderr)
                print("  secops --customer-id YOUR_CUSTOMER_ID --project-id YOUR_PROJECT_ID [command]", file=sys.stderr)
                print("\nFor help finding these values, run:", file=sys.stderr)
                print("  secops help --topic customer-id", file=sys.stderr)
                print("  secops help --topic project-id", file=sys.stderr)
                sys.exit(1)
            
            chronicle = client.chronicle(**chronicle_kwargs)
            return client, chronicle
        
        return client, None
    except (AuthenticationError, SecOpsError) as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        print("\nFor configuration help, run:", file=sys.stderr)
        print("  secops help --topic config", file=sys.stderr)
        sys.exit(1)


def output_formatter(data: Any, output_format: str = "json") -> None:
    """Format and print output data.
    
    Args:
        data: Data to output
        output_format: Output format (json, text, table)
    """
    if output_format == "json":
        print(json.dumps(data, indent=2, default=str))
    elif output_format == "text":
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(item)
        else:
            print(data)


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to a parser.
    
    Args:
        parser: Parser to add arguments to
    """
    config = load_config()
    
    parser.add_argument("--service-account", "--service_account", dest="service_account",
                      default=config.get("service_account"),
                      help="Path to service account JSON file")
    parser.add_argument("--output", choices=["json", "text"], default="json", 
                      help="Output format")


def add_chronicle_args(parser: argparse.ArgumentParser) -> None:
    """Add Chronicle-specific arguments to a parser.
    
    Args:
        parser: Parser to add arguments to
    """
    config = load_config()
    
    parser.add_argument("--customer-id", "--customer_id", dest="customer_id", 
                      default=config.get("customer_id"),
                      help="Chronicle instance ID")
    parser.add_argument("--project-id", "--project_id", dest="project_id", 
                      default=config.get("project_id"),
                      help="GCP project ID")
    parser.add_argument("--region", 
                      default=config.get("region", "us"),
                      help="Chronicle API region")


def add_time_range_args(parser: argparse.ArgumentParser) -> None:
    """Add time range arguments to a parser.
    
    Args:
        parser: Parser to add arguments to
    """
    config = load_config()
    
    parser.add_argument("--start-time", "--start_time", dest="start_time", 
                      default=config.get("start_time"),
                      help="Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    parser.add_argument("--end-time", "--end_time", dest="end_time", 
                      default=config.get("end_time"),
                      help="End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    parser.add_argument("--time-window", "--time_window", dest="time_window", 
                      type=int, 
                      default=config.get("time_window", 24),
                      help="Time window in hours (alternative to start/end time)")


def get_time_range(args: argparse.Namespace) -> Tuple[datetime, datetime]:
    """Get start and end time from arguments.
    
    Args:
        args: Command line arguments
        
    Returns:
        Tuple of (start_time, end_time)
    """
    end_time = parse_datetime(args.end_time) if args.end_time else datetime.now(timezone.utc)
    
    if args.start_time:
        start_time = parse_datetime(args.start_time)
    else:
        start_time = end_time - timedelta(hours=args.time_window)
    
    return start_time, end_time


def setup_search_command(subparsers):
    """Set up the search command parser.
    
    Args:
        subparsers: Subparsers object to add to
    """
    search_parser = subparsers.add_parser("search", help="Search UDM events")
    search_parser.add_argument("--query", help="UDM query string")
    search_parser.add_argument("--nl-query", "--nl_query", dest="nl_query", help="Natural language query")
    search_parser.add_argument("--max-events", "--max_events", dest="max_events", type=int, default=100, 
                             help="Maximum events to return")
    search_parser.add_argument("--fields", help="Comma-separated list of fields to include in CSV output")
    search_parser.add_argument("--csv", action="store_true", help="Output in CSV format")
    add_time_range_args(search_parser)
    search_parser.set_defaults(func=handle_search_command)


def handle_search_command(args, chronicle):
    """Handle the search command.
    
    Args:
        args: Command line arguments
        chronicle: Chronicle client
    """
    start_time, end_time = get_time_range(args)
    
    try:
        if args.csv and args.fields:
            fields = [f.strip() for f in args.fields.split(',')]
            result = chronicle.fetch_udm_search_csv(
                query=args.query,
                start_time=start_time,
                end_time=end_time,
                fields=fields
            )
            print(result)
        elif args.nl_query:
            result = chronicle.nl_search(
                text=args.nl_query,
                start_time=start_time,
                end_time=end_time,
                max_events=args.max_events
            )
            output_formatter(result, args.output)
        else:
            result = chronicle.search_udm(
                query=args.query,
                start_time=start_time,
                end_time=end_time,
                max_events=args.max_events
            )
            output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_stats_command(subparsers):
    """Set up the stats command parser."""
    stats_parser = subparsers.add_parser("stats", help="Get UDM statistics")
    stats_parser.add_argument("--query", required=True, help="Stats query string")
    stats_parser.add_argument("--max-events", "--max_events", dest="max_events", type=int, default=1000, 
                            help="Maximum events to process")
    stats_parser.add_argument("--max-values", "--max_values", dest="max_values", type=int, default=100, 
                            help="Maximum values per field")
    add_time_range_args(stats_parser)
    stats_parser.set_defaults(func=handle_stats_command)


def handle_stats_command(args, chronicle):
    """Handle the stats command."""
    start_time, end_time = get_time_range(args)
    
    try:
        result = chronicle.get_stats(
            query=args.query,
            start_time=start_time,
            end_time=end_time,
            max_events=args.max_events,
            max_values=args.max_values
        )
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_entity_command(subparsers):
    """Set up the entity command parser."""
    entity_parser = subparsers.add_parser("entity", help="Get entity information")
    entity_parser.add_argument("--value", required=True, 
                             help="Entity value (IP, domain, hash, etc.)")
    entity_parser.add_argument("--entity-type", "--entity_type", dest="entity_type", help="Entity type hint")
    add_time_range_args(entity_parser)
    entity_parser.set_defaults(func=handle_entity_command)


def handle_entity_command(args, chronicle):
    """Handle the entity command."""
    start_time, end_time = get_time_range(args)
    
    try:
        result = chronicle.summarize_entity(
            value=args.value,
            start_time=start_time,
            end_time=end_time,
            preferred_entity_type=args.entity_type
        )
        
        # Handle alert_counts properly - could be different types based on API
        alert_counts_list = []
        if result.alert_counts:
            for ac in result.alert_counts:
                # Try different methods to convert to dict
                try:
                    if hasattr(ac, '_asdict'):
                        alert_counts_list.append(ac._asdict())
                    elif hasattr(ac, '__dict__'):
                        alert_counts_list.append(vars(ac))
                    else:
                        # If it's already a dict or another type, just use it
                        alert_counts_list.append(ac)
                except Exception:
                    # If all conversion attempts fail, use string representation
                    alert_counts_list.append(str(ac))
        
        # Safely handle prevalence data which may not be available for all entity types
        prevalence_list = []
        if result.prevalence:
            try:
                prevalence_list = [vars(p) for p in result.prevalence]
            except Exception as prev_err:
                print(f"Warning: Unable to process prevalence data: {prev_err}", file=sys.stderr)
        
        # Convert the EntitySummary to a dictionary for output
        result_dict = {
            "primary_entity": result.primary_entity,
            "related_entities": result.related_entities,
            "alert_counts": alert_counts_list,
            "timeline": vars(result.timeline) if result.timeline else None,
            "prevalence": prevalence_list
        }
        output_formatter(result_dict, args.output)
    except Exception as e:
        if "Unsupported artifact type" in str(e):
            print(f"Error: The entity type for '{args.value}' is not supported. Try specifying a different entity type with --entity-type.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_iocs_command(subparsers):
    """Set up the IOCs command parser."""
    iocs_parser = subparsers.add_parser("iocs", help="List IoCs")
    iocs_parser.add_argument("--max-matches", "--max_matches", dest="max_matches", type=int, default=100, 
                           help="Maximum matches to return")
    iocs_parser.add_argument("--mandiant", action="store_true", 
                           help="Include Mandiant attributes")
    iocs_parser.add_argument("--prioritized", action="store_true", 
                           help="Only return prioritized IoCs")
    add_time_range_args(iocs_parser)
    iocs_parser.set_defaults(func=handle_iocs_command)


def handle_iocs_command(args, chronicle):
    """Handle the IOCs command."""
    start_time, end_time = get_time_range(args)
    
    try:
        result = chronicle.list_iocs(
            start_time=start_time,
            end_time=end_time,
            max_matches=args.max_matches,
            add_mandiant_attributes=args.mandiant,
            prioritized_only=args.prioritized
        )
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_log_command(subparsers):
    """Set up the log command parser."""
    log_parser = subparsers.add_parser("log", help="Ingest logs")
    log_subparsers = log_parser.add_subparsers(dest="log_command", help="Log command")
    
    # Ingest log command
    ingest_parser = log_subparsers.add_parser("ingest", help="Ingest raw logs")
    ingest_parser.add_argument("--type", required=True, help="Log type")
    ingest_parser.add_argument("--file", help="File containing log data")
    ingest_parser.add_argument("--message", help="Log message (alternative to file)")
    ingest_parser.add_argument("--forwarder-id", "--forwarder_id", dest="forwarder_id", help="Custom forwarder ID")
    ingest_parser.add_argument("--force", action="store_true", 
                             help="Force unknown log type")
    ingest_parser.add_argument("--labels", 
                             help="JSON string or comma-separated key=value pairs for custom labels")
    ingest_parser.set_defaults(func=handle_log_ingest_command)
    
    # Ingest UDM command
    udm_parser = log_subparsers.add_parser("ingest-udm", help="Ingest UDM events")
    udm_parser.add_argument("--file", required=True, help="File containing UDM event(s)")
    udm_parser.set_defaults(func=handle_udm_ingest_command)
    
    # List log types command
    types_parser = log_subparsers.add_parser("types", help="List available log types")
    types_parser.add_argument("--search", help="Search term for log types")
    types_parser.set_defaults(func=handle_log_types_command)


def handle_log_ingest_command(args, chronicle):
    """Handle log ingestion command."""
    try:
        log_message = args.message
        if args.file:
            with open(args.file, 'r') as f:
                log_message = f.read()
                
        # Process labels if provided
        labels = None
        if args.labels:
            # Try parsing as JSON first
            try:
                labels = json.loads(args.labels)
            except json.JSONDecodeError:
                # If not valid JSON, try parsing as comma-separated key=value pairs
                labels = {}
                for pair in args.labels.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        labels[key.strip()] = value.strip()
                    else:
                        print(f"Warning: Ignoring invalid label format: {pair}", file=sys.stderr)
                
                if not labels:
                    print("Warning: No valid labels found. Labels should be in JSON format or comma-separated key=value pairs.", file=sys.stderr)
        
        result = chronicle.ingest_log(
            log_type=args.type,
            log_message=log_message,
            forwarder_id=args.forwarder_id,
            force_log_type=args.force,
            labels=labels
        )
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_udm_ingest_command(args, chronicle):
    """Handle UDM ingestion command."""
    try:
        with open(args.file, 'r') as f:
            udm_events = json.load(f)
        
        result = chronicle.ingest_udm(udm_events=udm_events)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_log_types_command(args, chronicle):
    """Handle listing log types command."""
    try:
        if args.search:
            result = chronicle.search_log_types(args.search)
        else:
            result = chronicle.get_all_log_types()
        
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_rule_command(subparsers):
    """Set up the rule command parser."""
    rule_parser = subparsers.add_parser("rule", help="Manage detection rules")
    rule_subparsers = rule_parser.add_subparsers(dest="rule_command", help="Rule command")
    
    # List rules command
    list_parser = rule_subparsers.add_parser("list", help="List rules")
    list_parser.set_defaults(func=handle_rule_list_command)
    
    # Get rule command
    get_parser = rule_subparsers.add_parser("get", help="Get rule details")
    get_parser.add_argument("--id", required=True, help="Rule ID")
    get_parser.set_defaults(func=handle_rule_get_command)
    
    # Create rule command
    create_parser = rule_subparsers.add_parser("create", help="Create a rule")
    create_parser.add_argument("--file", required=True, help="File containing rule text")
    create_parser.set_defaults(func=handle_rule_create_command)
    
    # Update rule command
    update_parser = rule_subparsers.add_parser("update", help="Update a rule")
    update_parser.add_argument("--id", required=True, help="Rule ID")
    update_parser.add_argument("--file", required=True, help="File containing updated rule text")
    update_parser.set_defaults(func=handle_rule_update_command)
    
    # Enable/disable rule command
    enable_parser = rule_subparsers.add_parser("enable", help="Enable or disable a rule")
    enable_parser.add_argument("--id", required=True, help="Rule ID")
    enable_parser.add_argument("--enabled", choices=["true", "false"], required=True, 
                             help="Enable or disable the rule")
    enable_parser.set_defaults(func=handle_rule_enable_command)
    
    # Delete rule command
    delete_parser = rule_subparsers.add_parser("delete", help="Delete a rule")
    delete_parser.add_argument("--id", required=True, help="Rule ID")
    delete_parser.add_argument("--force", action="store_true", 
                             help="Force deletion of rule with retrohunts")
    delete_parser.set_defaults(func=handle_rule_delete_command)
    
    # Validate rule command
    validate_parser = rule_subparsers.add_parser("validate", help="Validate a rule")
    validate_parser.add_argument("--file", required=True, help="File containing rule text")
    validate_parser.set_defaults(func=handle_rule_validate_command)

    # Search rules command
    search_parser = rule_subparsers.add_parser("search", help="Search rules")
    search_parser.set_defaults(func=handle_rule_search_command)
    search_parser.add_argument("--query", required=True, help="Rule query string in regex")


def handle_rule_list_command(args, chronicle):
    """Handle rule list command."""
    try:
        result = chronicle.list_rules()
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_get_command(args, chronicle):
    """Handle rule get command."""
    try:
        result = chronicle.get_rule(args.id)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_create_command(args, chronicle):
    """Handle rule create command."""
    try:
        with open(args.file, 'r') as f:
            rule_text = f.read()
        
        result = chronicle.create_rule(rule_text)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_update_command(args, chronicle):
    """Handle rule update command."""
    try:
        with open(args.file, 'r') as f:
            rule_text = f.read()
        
        result = chronicle.update_rule(args.id, rule_text)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_enable_command(args, chronicle):
    """Handle rule enable/disable command."""
    try:
        enabled = args.enabled.lower() == "true"
        result = chronicle.enable_rule(args.id, enabled=enabled)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_delete_command(args, chronicle):
    """Handle rule delete command."""
    try:
        result = chronicle.delete_rule(args.id, force=args.force)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_validate_command(args, chronicle):
    """Handle rule validate command."""
    try:
        with open(args.file, 'r') as f:
            rule_text = f.read()
        
        result = chronicle.validate_rule(rule_text)
        if result.success:
            print("Rule is valid.")
        else:
            print(f"Rule is invalid: {result.message}")
            if result.position:
                print(f"Error at line {result.position['startLine']}, column {result.position['startColumn']}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_rule_search_command(args, chronicle):
    """Handle rule search command."""
    try:
        result = chronicle.search_rules(args.query)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_alert_command(subparsers):
    """Set up the alert command parser."""
    alert_parser = subparsers.add_parser("alert", help="Manage alerts")
    alert_parser.add_argument("--snapshot-query", "--snapshot_query", dest="snapshot_query", 
                            help="Query to filter alerts (e.g. feedback_summary.status != \"CLOSED\")")
    alert_parser.add_argument("--baseline-query", "--baseline_query", dest="baseline_query", help="Baseline query for alerts")
    alert_parser.add_argument("--max-alerts", "--max_alerts", dest="max_alerts", type=int, default=100, 
                            help="Maximum alerts to return")
    add_time_range_args(alert_parser)
    alert_parser.set_defaults(func=handle_alert_command)


def handle_alert_command(args, chronicle):
    """Handle alert command."""
    start_time, end_time = get_time_range(args)
    
    try:
        result = chronicle.get_alerts(
            start_time=start_time,
            end_time=end_time,
            snapshot_query=args.snapshot_query,
            baseline_query=args.baseline_query,
            max_alerts=args.max_alerts
        )
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_case_command(subparsers):
    """Set up the case command parser."""
    case_parser = subparsers.add_parser("case", help="Manage cases")
    case_parser.add_argument("--ids", help="Comma-separated list of case IDs")
    case_parser.set_defaults(func=handle_case_command)


def handle_case_command(args, chronicle):
    """Handle case command."""
    try:
        if args.ids:
            case_ids = [id.strip() for id in args.ids.split(',')]
            result = chronicle.get_cases(case_ids)
            
            # Convert CaseList to dictionary for output
            cases_dict = {
                "cases": [case._asdict() for case in result.cases]
            }
            output_formatter(cases_dict, args.output)
        else:
            print("Error: No case IDs provided", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_export_command(subparsers):
    """Set up the data export command parser."""
    export_parser = subparsers.add_parser("export", help="Manage data exports")
    export_subparsers = export_parser.add_subparsers(dest="export_command", help="Export command")
    
    # List available log types command
    log_types_parser = export_subparsers.add_parser("log-types", 
                                                 help="List available log types for export")
    add_time_range_args(log_types_parser)
    log_types_parser.add_argument("--page-size", "--page_size", dest="page_size", type=int, default=100, 
                                help="Page size for results")
    log_types_parser.set_defaults(func=handle_export_log_types_command)
    
    # Create export command
    create_parser = export_subparsers.add_parser("create", help="Create a data export")
    create_parser.add_argument("--gcs-bucket", "--gcs_bucket", dest="gcs_bucket", required=True, 
                             help="GCS bucket in format 'projects/PROJECT_ID/buckets/BUCKET_NAME'")
    create_parser.add_argument("--log-type", "--log_type", dest="log_type", help="Log type to export")
    create_parser.add_argument("--all-logs", "--all_logs", dest="all_logs", action="store_true", help="Export all log types")
    add_time_range_args(create_parser)
    create_parser.set_defaults(func=handle_export_create_command)
    
    # Get export status command
    status_parser = export_subparsers.add_parser("status", help="Get export status")
    status_parser.add_argument("--id", required=True, help="Export ID")
    status_parser.set_defaults(func=handle_export_status_command)
    
    # Cancel export command
    cancel_parser = export_subparsers.add_parser("cancel", help="Cancel an export")
    cancel_parser.add_argument("--id", required=True, help="Export ID")
    cancel_parser.set_defaults(func=handle_export_cancel_command)


def handle_export_log_types_command(args, chronicle):
    """Handle export log types command."""
    start_time, end_time = get_time_range(args)
    
    try:
        result = chronicle.fetch_available_log_types(
            start_time=start_time,
            end_time=end_time,
            page_size=args.page_size
        )
        
        # Convert to a simple dict for output
        log_types_dict = {
            "log_types": [
                {
                    "log_type": lt.log_type.split('/')[-1],
                    "display_name": lt.display_name,
                    "start_time": lt.start_time.isoformat(),
                    "end_time": lt.end_time.isoformat()
                }
                for lt in result["available_log_types"]
            ],
            "next_page_token": result.get("next_page_token", "")
        }
        
        output_formatter(log_types_dict, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_export_create_command(args, chronicle):
    """Handle export create command."""
    start_time, end_time = get_time_range(args)
    
    try:
        # First, try to fetch available log types to see if there are any
        available_logs = chronicle.fetch_available_log_types(
            start_time=start_time,
            end_time=end_time
        )
        
        if not available_logs.get("available_log_types") and not args.log_type:
            print("Warning: No log types are available for export in the specified time range.", file=sys.stderr)
            print("You may need to adjust your time range or check your Chronicle instance configuration.", file=sys.stderr)
            if args.all_logs:
                print("Creating export with --all-logs flag anyway...", file=sys.stderr)
            else:
                print("Error: Cannot create export without specifying a log type when no log types are available.", file=sys.stderr)
                sys.exit(1)
        
        # If log_type is specified, check if it exists in available log types
        if args.log_type and available_logs.get("available_log_types"):
            log_type_found = False
            for lt in available_logs.get("available_log_types", []):
                if lt.log_type.endswith("/" + args.log_type) or lt.log_type.endswith("/logTypes/" + args.log_type):
                    log_type_found = True
                    break
            
            if not log_type_found:
                print(f"Warning: Log type '{args.log_type}' not found in available log types.", file=sys.stderr)
                print("Available log types:", file=sys.stderr)
                for lt in available_logs.get("available_log_types", [])[:5]:  # Show first 5
                    print(f"  {lt.log_type.split('/')[-1]}", file=sys.stderr)
                print("Attempting to create export anyway...", file=sys.stderr)
        
        # Proceed with export creation
        if args.all_logs:
            result = chronicle.create_data_export(
                gcs_bucket=args.gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                export_all_logs=True
            )
        elif args.log_type:
            result = chronicle.create_data_export(
                gcs_bucket=args.gcs_bucket,
                start_time=start_time,
                end_time=end_time,
                log_type=args.log_type
            )
        else:
            print("Error: Either --log-type or --all-logs must be specified", file=sys.stderr)
            sys.exit(1)
        
        output_formatter(result, args.output)
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}", file=sys.stderr)
        
        # Provide helpful advice based on common errors
        if "unrecognized log type" in error_msg.lower():
            print("\nPossible solutions:", file=sys.stderr)
            print("1. Verify the log type exists in your Chronicle instance", file=sys.stderr)
            print("2. Try using 'secops export log-types' to see available log types", file=sys.stderr)
            print("3. Check if your time range contains data for this log type", file=sys.stderr)
            print("4. Make sure your GCS bucket is properly formatted as 'projects/PROJECT_ID/buckets/BUCKET_NAME'", file=sys.stderr)
        elif "permission" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print("\nPossible authentication or permission issues:", file=sys.stderr)
            print("1. Verify your credentials have access to Chronicle and the specified GCS bucket", file=sys.stderr)
            print("2. Check if your service account has the required IAM roles", file=sys.stderr)
        
        sys.exit(1)


def handle_export_status_command(args, chronicle):
    """Handle export status command."""
    try:
        result = chronicle.get_data_export(args.id)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_export_cancel_command(args, chronicle):
    """Handle export cancel command."""
    try:
        result = chronicle.cancel_data_export(args.id)
        output_formatter(result, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_gemini_command(subparsers):
    """Set up the Gemini command parser."""
    gemini_parser = subparsers.add_parser("gemini", help="Interact with Gemini AI")
    gemini_parser.add_argument("--query", required=True, help="Query for Gemini")
    gemini_parser.add_argument("--conversation-id", "--conversation_id", dest="conversation_id", help="Continue an existing conversation")
    gemini_parser.add_argument("--raw", action="store_true", 
                             help="Output raw API response")
    gemini_parser.add_argument("--opt-in", "--opt_in", dest="opt_in", action="store_true", 
                             help="Explicitly opt-in to Gemini")
    gemini_parser.set_defaults(func=handle_gemini_command)


def handle_gemini_command(args, chronicle):
    """Handle Gemini command."""
    try:
        if args.opt_in:
            result = chronicle.opt_in_to_gemini()
            print(f"Opt-in result: {'Success' if result else 'Failed'}")
            if not result:
                return
        
        response = chronicle.gemini(
            query=args.query,
            conversation_id=args.conversation_id
        )
        
        if args.raw:
            # Output raw API response
            output_formatter(response.get_raw_response(), args.output)
        else:
            # Output formatted text content
            print(response.get_text_content())
            
            # Print code blocks if any
            code_blocks = response.get_code_blocks()
            if code_blocks:
                print("\nCode blocks:")
                for i, block in enumerate(code_blocks, 1):
                    print(f"\n--- Code Block {i}" + (f" ({block.title})" if block.title else "") + " ---")
                    print(block.content)
            
            # Print suggested actions if any
            if response.suggested_actions:
                print("\nSuggested actions:")
                for action in response.suggested_actions:
                    print(f"- {action.display_text}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def setup_help_command(subparsers):
    """Set up the help command parser.
    
    Args:
        subparsers: Subparsers object to add to
    """
    help_parser = subparsers.add_parser("help", help="Get help with configuration and usage")
    help_parser.add_argument("--topic", choices=["config", "customer-id", "project-id"], 
                           default="config", help="Help topic")
    help_parser.set_defaults(func=handle_help_command)


def handle_help_command(args, chronicle=None):
    """Handle help command.
    
    Args:
        args: Command line arguments
        chronicle: Not used for this command
    """
    if args.topic == "config":
        print("Configuration Help:")
        print("------------------")
        print("To use the SecOps CLI with Chronicle, you need to configure:")
        print("  1. Chronicle Customer ID (your Chronicle instance ID)")
        print("  2. GCP Project ID (the Google Cloud project associated with your Chronicle instance)")
        print("  3. Region (e.g., 'us', 'europe', 'asia-northeast1')")
        print("  4. Optional: Service Account credentials")
        print()
        print("Configuration commands:")
        print("  secops config set --customer-id YOUR_CUSTOMER_ID --project-id YOUR_PROJECT_ID --region YOUR_REGION")
        print("  secops config view")
        print("  secops config clear")
        print()
        print("For help finding your Customer ID or Project ID, run:")
        print("  secops help --topic customer-id")
        print("  secops help --topic project-id")
   

def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Google SecOps CLI")
    
    # Global arguments
    add_common_args(parser)
    add_chronicle_args(parser)
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Set up individual command parsers
    setup_search_command(subparsers)
    setup_stats_command(subparsers)
    setup_entity_command(subparsers)
    setup_iocs_command(subparsers)
    setup_log_command(subparsers)
    setup_rule_command(subparsers)
    setup_alert_command(subparsers)
    setup_case_command(subparsers)
    setup_export_command(subparsers)
    setup_gemini_command(subparsers)
    setup_config_command(subparsers)  # Add the config command
    setup_help_command(subparsers)  # Add the help command
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle config commands directly without setting up Chronicle client
    if args.command == "config" or args.command == "help":
        args.func(args)
        return
    
    # Check if this is a Chronicle-related command that requires configuration
    chronicle_commands = ["search", "stats", "entity", "iocs", "rule", "alert", "case", "export", "gemini"]
    requires_chronicle = any(cmd in args.command for cmd in chronicle_commands)
    
    if requires_chronicle:
        # Check for required configuration before attempting to create the client
        config = load_config()
        customer_id = args.customer_id or config.get("customer_id")
        project_id = args.project_id or config.get("project_id")
        
        if not customer_id or not project_id:
            missing = []
            if not customer_id:
                missing.append("customer_id")
            if not project_id:
                missing.append("project_id")
                
            print(f"Error: Missing required configuration: {', '.join(missing)}", file=sys.stderr)
            print("\nPlease set up your configuration first:", file=sys.stderr)
            print("  secops config set --customer-id YOUR_CUSTOMER_ID --project-id YOUR_PROJECT_ID --region YOUR_REGION", file=sys.stderr)
            print("\nOr provide them directly on the command line:", file=sys.stderr)
            print(f"  secops --customer-id YOUR_CUSTOMER_ID --project-id YOUR_PROJECT_ID --region YOUR_REGION {args.command}", file=sys.stderr)
            print("\nNeed help finding these values?", file=sys.stderr)
            print("  secops help --topic customer-id", file=sys.stderr)
            print("  secops help --topic project-id", file=sys.stderr)
            print("\nFor general configuration help:", file=sys.stderr)
            print("  secops help --topic config", file=sys.stderr)
            sys.exit(1)
        
    # Set up client
    client, chronicle = setup_client(args)
    
    # Execute command
    if hasattr(args, 'func'):
        if not requires_chronicle or chronicle is not None:
            args.func(args, chronicle)
        else:
            print("Error: Chronicle client required for this command", file=sys.stderr)
            print("\nFor help with configuration:", file=sys.stderr)
            print("  secops help --topic config", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
