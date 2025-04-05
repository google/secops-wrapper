#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Command-line interface for Google SecOps SDK."""

import os
import sys
import json
import click
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from secops.client import SecOpsClient
from secops.chronicle.models import EntitySummary


def parse_datetime(ctx, param, value):
    """Parse datetime from string."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try to parse relative time (e.g., "1d" for 1 day ago)
            if value.endswith('d'):
                days = int(value[:-1])
                return datetime.now() - timedelta(days=days)
            elif value.endswith('h'):
                hours = int(value[:-1])
                return datetime.now() - timedelta(hours=hours)
            else:
                raise ValueError(f"Unrecognized time format: {value}")
        except Exception:
            raise click.BadParameter(
                f"Invalid datetime format: {value}. Use ISO format (YYYY-MM-DDTHH:MM:SS) or relative format (1d, 2h)"
            )


@click.group()
@click.option(
    "--service-account-path",
    "-s",
    help="Path to service account JSON key file",
    envvar="SECOPS_SERVICE_ACCOUNT_PATH",
)
@click.option(
    "--project-id",
    "-p",
    help="Google Cloud project ID",
    envvar="SECOPS_PROJECT_ID",
)
@click.option(
    "--customer-id",
    "-c",
    help="Chronicle customer ID",
    envvar="SECOPS_CUSTOMER_ID",
)
@click.option(
    "--region",
    "-r",
    help="Chronicle API region",
    default="us",
    envvar="SECOPS_REGION",
)
@click.option(
    "--dotenv",
    "-d",
    help="Path to .env file to load",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.pass_context
def cli(ctx, service_account_path, project_id, customer_id, region, dotenv):
    """Google SecOps CLI.

    Command-line interface for interacting with Google SecOps services.
    """
    # Load environment variables from specified .env file if provided
    if dotenv:
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv)
            # Re-read environment variables that might have been set in the .env file
            if not service_account_path and os.environ.get("SECOPS_SERVICE_ACCOUNT_PATH"):
                service_account_path = os.environ.get("SECOPS_SERVICE_ACCOUNT_PATH")
            if not project_id and os.environ.get("SECOPS_PROJECT_ID"):
                project_id = os.environ.get("SECOPS_PROJECT_ID")
            if not customer_id and os.environ.get("SECOPS_CUSTOMER_ID"):
                customer_id = os.environ.get("SECOPS_CUSTOMER_ID")
            if not region and os.environ.get("SECOPS_REGION"):
                region = os.environ.get("SECOPS_REGION")
        except ImportError:
            click.echo("Warning: python-dotenv package is not installed. Cannot load .env file.", err=True)

    # Initialize the context object
    ctx.ensure_object(dict)

    # Store configuration in context
    ctx.obj["service_account_path"] = service_account_path
    ctx.obj["project_id"] = project_id
    ctx.obj["customer_id"] = customer_id
    ctx.obj["region"] = region

    # Create SecOps client if required parameters are provided
    if all([project_id, customer_id]):
        # Use service_account_path if provided, otherwise use application default credentials
        if service_account_path:
            client = SecOpsClient(service_account_path=service_account_path)
        else:
            client = SecOpsClient()  # Will use application default credentials

        ctx.obj["client"] = client
        ctx.obj["chronicle"] = client.chronicle(
            customer_id=customer_id,
            project_id=project_id,
            region=region
        )


@cli.group()
@click.pass_context
def chronicle(ctx):
    """Chronicle commands."""
    # Ensure we have a Chronicle client
    if "chronicle" not in ctx.obj:
        if not all([
            ctx.obj.get("project_id"),
            ctx.obj.get("customer_id")
        ]):
            raise click.UsageError(
                "Missing required parameters. Please provide "
                "--project-id and --customer-id options or set the corresponding "
                "environment variables."
            )

        # Create the client if not already created
        service_account_path = ctx.obj.get("service_account_path")
        if service_account_path:
            client = SecOpsClient(service_account_path=service_account_path)
        else:
            client = SecOpsClient()  # Will use application default credentials

        ctx.obj["client"] = client
        ctx.obj["chronicle"] = client.chronicle(
            customer_id=ctx.obj["customer_id"],
            project_id=ctx.obj["project_id"],
            region=ctx.obj["region"]
        )


@chronicle.command("search")
@click.option(
    "--query",
    "-q",
    required=True,
    help="Chronicle search query",
)
@click.option(
    "--start-time",
    "-s",
    required=True,
    callback=parse_datetime,
    help="Start time (ISO format or relative like '1d' for 1 day ago)",
)
@click.option(
    "--end-time",
    "-e",
    callback=parse_datetime,
    help="End time (ISO format or relative like '1h' for 1 hour ago)",
)
@click.option(
    "--max-events",
    "-m",
    type=int,
    default=1000,
    help="Maximum number of events to return",
)
@click.option(
    "--case-insensitive/--case-sensitive",
    default=True,
    help="Whether to perform case-insensitive search",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def search_udm(ctx, query, start_time, end_time, max_events, case_insensitive, output):
    """Search UDM events in Chronicle."""
    # Set default end time to now if not provided
    if not end_time:
        end_time = datetime.now()

    try:
        results = ctx.obj["chronicle"].search_udm(
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_events=max_events,
            case_insensitive=case_insensitive
        )

        if output == "json":
            click.echo(json.dumps(results, default=str, indent=2))
        else:
            # Table output
            if not results.get("events"):
                click.echo("No events found.")
                return

            # Print summary
            click.echo(f"Found {len(results.get('events', []))} events.")

            # Print events in a tabular format
            for i, event in enumerate(results.get("events", [])):
                click.echo(f"\nEvent {i+1}:")
                for key, value in event.items():
                    if isinstance(value, dict):
                        click.echo(f"  {key}:")
                        for sub_key, sub_value in value.items():
                            click.echo(f"    {sub_key}: {sub_value}")
                    else:
                        click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@chronicle.command("entity")
@click.option(
    "--value",
    "-v",
    required=True,
    help="Entity value (e.g., IP address, hostname, etc.)",
)
@click.option(
    "--start-time",
    "-s",
    required=True,
    callback=parse_datetime,
    help="Start time (ISO format or relative like '1d' for 1 day ago)",
)
@click.option(
    "--end-time",
    "-e",
    callback=parse_datetime,
    help="End time (ISO format or relative like '1h' for 1 hour ago)",
)
@click.option(
    "--field-path",
    "-f",
    help="UDM field path for the entity",
)
@click.option(
    "--value-type",
    "-t",
    help="Entity value type",
)
@click.option(
    "--return-alerts/--no-alerts",
    default=True,
    help="Whether to include alerts in the response",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def entity_summary(ctx, value, start_time, end_time, field_path, value_type, return_alerts, output):
    """Get entity summary from Chronicle."""
    # Set default end time to now if not provided
    if not end_time:
        end_time = datetime.now()

    try:
        summary = ctx.obj["chronicle"].summarize_entity(
            value=value,
            start_time=start_time,
            end_time=end_time,
            field_path=field_path,
            value_type=value_type,
            return_alerts=return_alerts
        )

        if output == "json":
            # Convert to dictionary for JSON serialization
            summary_dict = {
                "entity": summary.entity.to_dict() if summary.entity else None,
                "metrics": summary.metrics.to_dict() if summary.metrics else None,
                "timeline": summary.timeline.to_dict() if summary.timeline else None,
                "alerts": [alert.to_dict() for alert in summary.alerts] if summary.alerts else []
            }
            click.echo(json.dumps(summary_dict, default=str, indent=2))
        else:
            # Table output
            click.echo("Entity Summary:")
            if summary.entity:
                click.echo(f"  Type: {summary.entity.type}")
                click.echo(f"  Value: {summary.entity.value}")
                if summary.entity.metadata:
                    click.echo("  Metadata:")
                    for key, value in summary.entity.metadata.items():
                        click.echo(f"    {key}: {value}")

            if summary.metrics:
                click.echo("\nMetrics:")
                click.echo(f"  First Seen: {summary.metrics.first_seen}")
                click.echo(f"  Last Seen: {summary.metrics.last_seen}")
                click.echo(f"  Alert Count: {summary.metrics.alert_count}")
                click.echo(f"  Event Count: {summary.metrics.event_count}")

            if summary.alerts:
                click.echo(f"\nAlerts ({len(summary.alerts)}):")
                for i, alert in enumerate(summary.alerts):
                    click.echo(f"  Alert {i+1}:")
                    click.echo(f"    Name: {alert.name}")
                    click.echo(f"    Severity: {alert.severity}")
                    click.echo(f"    Time: {alert.timestamp}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@chronicle.command("validate-query")
@click.option(
    "--query",
    "-q",
    required=True,
    help="Chronicle search query to validate",
)
@click.pass_context
def validate_query(ctx, query):
    """Validate a Chronicle search query."""
    try:
        result = ctx.obj["chronicle"].validate_query(query)

        if result.get("valid", False):
            click.echo("Query is valid.")
        else:
            click.echo("Query is invalid:")
            for error in result.get("errors", []):
                click.echo(f"  - {error}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@chronicle.command("list-rules")
@click.option(
    "--page-size",
    "-p",
    type=int,
    default=100,
    help="Number of rules to return per page",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_rules(ctx, page_size, output):
    """List detection rules in Chronicle."""
    try:
        rules = ctx.obj["chronicle"].list_rules(page_size=page_size)

        if output == "json":
            click.echo(json.dumps(rules, default=str, indent=2))
        else:
            # Table output
            if not rules.get("rules"):
                click.echo("No rules found.")
                return

            click.echo(f"Found {len(rules.get('rules', []))} rules:")
            for i, rule in enumerate(rules.get("rules", [])):
                click.echo(f"\nRule {i+1}:")
                click.echo(f"  Name: {rule.get('ruleName', 'N/A')}")
                click.echo(f"  Display Name: {rule.get('displayName', 'N/A')}")
                click.echo(f"  Enabled: {rule.get('enabled', False)}")
                click.echo(f"  Version ID: {rule.get('versionId', 'N/A')}")
                click.echo(f"  Rule Type: {rule.get('ruleType', 'N/A')}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@chronicle.command("get-rule")
@click.option(
    "--rule-id",
    "-r",
    required=True,
    help="Rule ID or name",
)
@click.option(
    "--version-id",
    "-v",
    help="Rule version ID (optional)",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def get_rule(ctx, rule_id, version_id, output):
    """Get a specific detection rule from Chronicle."""
    try:
        rule = ctx.obj["chronicle"].get_rule(rule_id=rule_id, version_id=version_id)

        if output == "json":
            click.echo(json.dumps(rule, default=str, indent=2))
        else:
            # Table output
            click.echo("Rule Details:")
            click.echo(f"  Name: {rule.get('ruleName', 'N/A')}")
            click.echo(f"  Display Name: {rule.get('displayName', 'N/A')}")
            click.echo(f"  Enabled: {rule.get('enabled', False)}")
            click.echo(f"  Version ID: {rule.get('versionId', 'N/A')}")
            click.echo(f"  Rule Type: {rule.get('ruleType', 'N/A')}")

            if "metadata" in rule:
                click.echo("\nMetadata:")
                for key, value in rule["metadata"].items():
                    click.echo(f"  {key}: {value}")

            if "rule" in rule:
                click.echo("\nRule Content:")
                click.echo(f"  {rule['rule']}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@chronicle.command("nl-search")
@click.option(
    "--query",
    "-q",
    required=True,
    help="Natural language query",
)
@click.option(
    "--start-time",
    "-s",
    required=True,
    callback=parse_datetime,
    help="Start time (ISO format or relative like '1d' for 1 day ago)",
)
@click.option(
    "--end-time",
    "-e",
    callback=parse_datetime,
    help="End time (ISO format or relative like '1h' for 1 hour ago)",
)
@click.option(
    "--max-events",
    "-m",
    type=int,
    default=1000,
    help="Maximum number of events to return",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def nl_search(ctx, query, start_time, end_time, max_events, output):
    """Search Chronicle using natural language."""
    # Set default end time to now if not provided
    if not end_time:
        end_time = datetime.now()

    try:
        results = ctx.obj["chronicle"].nl_search(
            text=query,
            start_time=start_time,
            end_time=end_time,
            max_events=max_events
        )

        if output == "json":
            click.echo(json.dumps(results, default=str, indent=2))
        else:
            # Table output
            if "udmSearchQuery" in results:
                click.echo(f"Translated UDM query: {results['udmSearchQuery']}")

            if not results.get("events"):
                click.echo("No events found.")
                return

            # Print summary
            click.echo(f"Found {len(results.get('events', []))} events.")

            # Print events in a tabular format
            for i, event in enumerate(results.get("events", [])):
                click.echo(f"\nEvent {i+1}:")
                for key, value in event.items():
                    if isinstance(value, dict):
                        click.echo(f"  {key}:")
                        for sub_key, sub_value in value.items():
                            click.echo(f"    {sub_key}: {sub_value}")
                    else:
                        click.echo(f"  {key}: {value}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli(obj={})
