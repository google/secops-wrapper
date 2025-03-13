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
"""Chronicle API client implementation."""
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import time
import logging
from google.auth.transport import requests as google_auth_requests
from secops.auth import SecOpsAuth
from secops.exceptions import APIError
from secops.chronicle.models import Entity, EntityMetadata, EntityMetrics, TimeInterval, TimelineBucket, Timeline, WidgetMetadata, EntitySummary, AlertCount, AlertState, ListBasis, CaseList, RuleView, CompilationResult, Rule
import re
from enum import Enum


LOGGER = logging.getLogger(__name__)


class ValueType(Enum):
    """Chronicle API value types."""
    ASSET_IP_ADDRESS = "ASSET_IP_ADDRESS"
    MAC = "MAC"
    HOSTNAME = "HOSTNAME"
    DOMAIN_NAME = "DOMAIN_NAME"
    HASH_MD5 = "HASH_MD5"
    HASH_SHA256 = "HASH_SHA256"
    HASH_SHA1 = "HASH_SHA1"
    EMAIL = "EMAIL"
    USERNAME = "USERNAME"

def _detect_value_type(value: str) -> tuple[Optional[str], Optional[str]]:
    """Detect the type of value and return appropriate field path or value type.

    Args:
        value: The value to analyze

    Returns:
        Tuple of (field_path, value_type)
    """
    # IPv4 pattern with validation for numbers 0-255
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ipv4_pattern, value):
        return ("principal.ip", None)  # Use field_path for IPs

    # MD5 pattern (32 hex chars)
    md5_pattern = r'^[a-fA-F0-9]{32}$'
    if re.match(md5_pattern, value):
        return ("target.file.md5", None)  # Use field_path for file hashes

    # SHA1 pattern (40 hex chars)
    sha1_pattern = r'^[a-fA-F0-9]{40}$'
    if re.match(sha1_pattern, value):
        return ("target.file.sha1", None)

    # SHA256 pattern (64 hex chars)
    sha256_pattern = r'^[a-fA-F0-9]{64}$'
    if re.match(sha256_pattern, value):
        return ("target.file.sha256", None)

    # Domain pattern
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
    if re.match(domain_pattern, value):
        return (None, ValueType.DOMAIN_NAME.value)

    # Email pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, value):
        return (None, ValueType.EMAIL.value)

    # MAC address pattern
    mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    if re.match(mac_pattern, value):
        return (None, ValueType.MAC.value)

    # Default to hostname if it looks like one
    hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'
    if re.match(hostname_pattern, value):
        return (None, ValueType.HOSTNAME.value)

    return (None, None)

class ChronicleClient:
    """Client for interacting with Chronicle API."""

    def __init__(
            self,
            customer_id: str,
            project_id: str,
            region: str = "us",
            auth: Optional[SecOpsAuth] = None
    ):
        """Initialize Chronicle client.

        Args:
            customer_id: Chronicle customer ID
            project_id: GCP project ID
            region: Chronicle API region (default: "us")
            auth: Optional SecOpsAuth instance
        """
        self.customer_id = customer_id
        self.project_id = project_id
        self.region = region
        self.auth = auth or SecOpsAuth()

        self.instance_id = f"projects/{project_id}/locations/{region}/instances/{customer_id}"
        self.base_url = f"https://{region}-chronicle.googleapis.com/v1alpha"
        self._session = None

    @property
    def session(self) -> google_auth_requests.AuthorizedSession:
        """Get or create authorized session."""
        if self._session is None:
            self._session = google_auth_requests.AuthorizedSession(self.auth.credentials)
        return self._session

    def fetch_udm_search_csv(
            self,
            query: str,
            start_time: datetime,
            end_time: datetime,
            fields: list[str],
            case_insensitive: bool = True
    ) -> str:
        """Fetch UDM search results in CSV format.

        Args:
            query: Chronicle search query
            start_time: Search start time
            end_time: Search end time
            fields: List of fields to include in results
            case_insensitive: Whether to perform case-insensitive search

        Returns:
            CSV formatted string of results

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/{self.instance_id}/legacy:legacyFetchUdmSearchCsv"

        search_query = {
            "baselineQuery": query,
            "baselineTimeRange": {
                "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            },
            "fields": {
                "fields": fields
            },
            "caseInsensitive": case_insensitive
        }

        response = self.session.post(
            url,
            json=search_query,
            headers={"Accept": "*/*"}
        )

        if response.status_code != 200:
            raise APIError(f"Chronicle API request failed: {response.text}")

        return response.text

    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a UDM search query.

        Args:
            query: The query to validate

        Returns:
            Dict containing validation results

        Raises:
            APIError: If validation fails
        """
        url = f"{self.base_url}/{self.instance_id}:validateQuery"

        # Replace special characters with Unicode escapes
        encoded_query = query.replace('!', '\u0021')

        params = {
            "rawQuery": encoded_query,
            "dialect": "DIALECT_UDM_SEARCH",
            "allowUnreplacedPlaceholders": "false"
        }

        response = self.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Query validation failed: {response.text}")

        return response.json()

    def get_stats(
            self,
            query: str,
            start_time: datetime,
            end_time: datetime,
            max_values: int = 60,
            max_events: int = 10000,
            case_insensitive: bool = True,
            max_attempts: int = 30
    ) -> Dict[str, Any]:
        """Perform a UDM stats search query."""
        url = f"{self.base_url}/{self.instance_id}/legacy:legacyFetchUdmSearchView"

        payload = {
            "baselineQuery": query,
            "baselineTimeRange": {
                "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            },
            "caseInsensitive": case_insensitive,
            "returnOperationIdOnly": True,
            "eventList": {
                "maxReturnedEvents": max_events
            },
            "fieldAggregations": {
                "maxValuesPerField": max_values
            },
            "generateAiOverview": True
        }

        # Start the search operation
        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise APIError(
                f"Error initiating search: Status {response.status_code}, "
                f"Response: {response.text}"
            )

        operation = response.json()

        # Extract operation ID from response
        try:
            if isinstance(operation, list):
                operation_id = operation[0].get("operation")
            else:
                operation_id = operation.get("operation") or operation.get("name")
        except Exception as e:
            raise APIError(
                f"Error extracting operation ID. Response: {operation}, Error: {str(e)}"
            )

        if not operation_id:
            raise APIError(f"No operation ID found in response: {operation}")

        # Poll for results using the full operation ID path
        results_url = f"{self.base_url}/{operation_id}:streamSearch"
        attempt = 0

        while attempt < max_attempts:
            results_response = self.session.get(results_url)
            if results_response.status_code != 200:
                raise APIError(f"Error fetching results: {results_response.text}")

            results = results_response.json()

            if isinstance(results, list):
                results = results[0]

            # Check both possible paths for completion status
            done = (
                    results.get("done") or  # Check top level
                    results.get("operation", {}).get("done") or  # Check under operation
                    results.get("response", {}).get("complete")  # Check under response
            )

            if done:
                # Check both possible paths for stats
                stats = (
                        results.get("response", {}).get("stats") or  # Check under response
                        results.get("operation", {}).get("response", {}).get("stats")  # Check under operation.response
                )
                if stats:
                    return self._process_stats_results({"response": {"stats": stats}})
                else:
                    raise APIError("No stats found in completed response")

            attempt += 1
            time.sleep(1)

        raise APIError(f"Search timed out after {max_attempts} attempts")

    def _process_stats_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format stats search results.

        Args:
            results: Raw API response

        Returns:
            Processed results with formatted rows
        """
        try:
            stats = results.get("response", {}).get("stats", {})
            if not stats:
                return {"rows": [], "columns": []}

            # Extract column information
            columns = []
            for col in stats.get("results", []):
                if "column" in col:
                    columns.append(col["column"])

            # Process rows
            rows = []
            if stats.get("results"):
                first_col = stats["results"][0]
                num_rows = len(first_col.get("values", []))

                for i in range(num_rows):
                    row = {}
                    for col in stats["results"]:
                        col_name = col["column"]
                        value = col["values"][i]["value"]

                        # Handle different value types
                        if "stringVal" in value:
                            row[col_name] = value["stringVal"]
                        elif "int64Val" in value:
                            row[col_name] = int(value["int64Val"])
                        else:
                            row[col_name] = None

                    rows.append(row)

            return {
                "columns": columns,
                "rows": rows,
                "total_rows": len(rows)
            }

        except Exception as e:
            raise APIError(f"Error processing stats results: {str(e)}")

    def search_udm(
            self,
            query: str,
            start_time: datetime,
            end_time: datetime,
            max_events: int = 10000,
            case_insensitive: bool = True,
            max_attempts: int = 30
    ) -> Dict[str, Any]:
        """Perform a UDM search query.

        Args:
            query: The UDM search query
            start_time: Search start time
            end_time: Search end time
            max_events: Maximum events to return
            case_insensitive: Whether to perform case-insensitive search
            max_attempts: Maximum number of polling attempts (default: 30)

        Returns:
            Dict containing the search results with events
        """
        url = f"{self.base_url}/{self.instance_id}/legacy:legacyFetchUdmSearchView"

        payload = {
            "baselineQuery": query,
            "baselineTimeRange": {
                "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            },
            "caseInsensitive": case_insensitive,
            "returnOperationIdOnly": True,
            "eventList": {
                "maxReturnedEvents": max_events
            }
        }

        # Start the search operation
        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise APIError(
                f"Error initiating search: Status {response.status_code}, "
                f"Response: {response.text}"
            )

        operation = response.json()

        # Extract operation ID from response
        try:
            if isinstance(operation, list):
                operation_id = operation[0].get("operation")
            else:
                operation_id = operation.get("operation") or operation.get("name")
        except Exception as e:
            raise APIError(
                f"Error extracting operation ID. Response: {operation}, Error: {str(e)}"
            )

        if not operation_id:
            raise APIError(f"No operation ID found in response: {operation}")

        # Poll for results using the full operation ID path
        results_url = f"{self.base_url}/{operation_id}:streamSearch"
        attempt = 0

        while attempt < max_attempts:
            results_response = self.session.get(results_url)
            if results_response.status_code != 200:
                raise APIError(f"Error fetching results: {results_response.text}")

            results = results_response.json()

            if isinstance(results, list):
                results = results[0]

            # Check both possible paths for completion status
            done = (
                    results.get("done") or  # Check top level
                    results.get("operation", {}).get("done") or  # Check under operation
                    results.get("response", {}).get("complete")  # Check under response
            )

            if done:
                events = (
                        results.get("response", {}).get("events", {}).get("events", []) or
                        results.get("operation", {}).get("response", {}).get("events", {}).get("events", [])
                )
                return {"events": events, "total_events": len(events)}

            attempt += 1
            time.sleep(1)

        raise APIError(f"Search timed out after {max_attempts} attempts")

    def summarize_entity(
            self,
            start_time: datetime,
            end_time: datetime,
            value: str,
            field_path: Optional[str] = None,
            value_type: Optional[str] = None,
            entity_id: Optional[str] = None,
            entity_namespace: Optional[str] = None,
            return_alerts: bool = True,
            return_prevalence: bool = False,
            include_all_udm_types: bool = True,
            page_size: int = 1000,
            page_token: Optional[str] = None
    ) -> EntitySummary:
        """Get summary information about an entity.

        Args:
            start_time: Start time for the summary
            end_time: End time for the summary
            value: Value to search for (IP, domain, file hash, etc)
            field_path: Optional override for UDM field path
            value_type: Optional override for value type
            entity_id: Entity ID to look up
            entity_namespace: Entity namespace
            return_alerts: Whether to include alerts
            return_prevalence: Whether to include prevalence data
            include_all_udm_types: Whether to include all UDM event types
            page_size: Maximum number of results per page
            page_token: Token for pagination

        Returns:
            EntitySummary object containing the results

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/{self.instance_id}:summarizeEntity"

        params = {
            "timeRange.startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "timeRange.endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "returnAlerts": return_alerts,
            "returnPrevalence": return_prevalence,
            "includeAllUdmEventTypesForFirstLastSeen": include_all_udm_types,
            "pageSize": page_size
        }

        # Add optional parameters
        if page_token:
            params["pageToken"] = page_token

        if entity_id:
            params["entityId"] = entity_id
        else:
            # Auto-detect type if not explicitly provided
            detected_field_path, detected_value_type = _detect_value_type(value)

            # Use explicit values if provided, otherwise use detected values
            final_field_path = field_path or detected_field_path
            final_value_type = value_type or detected_value_type

            if final_field_path:
                params["fieldAndValue.fieldPath"] = final_field_path
                params["fieldAndValue.value"] = value
            elif final_value_type:
                params["fieldAndValue.value"] = value
                params["fieldAndValue.valueType"] = final_value_type
            else:
                raise ValueError(
                    f"Could not determine type for value: {value}. "
                    "Please specify field_path or value_type explicitly."
                )

            if entity_namespace:
                params["fieldAndValue.entityNamespace"] = entity_namespace

        response = self.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Error getting entity summary: {response.text}")

        try:
            data = response.json()

            # Parse entities
            entities = []
            for entity_data in data.get("entities", []):
                metadata = entity_data.get("metadata", {})
                interval = metadata.get("interval", {})

                entity = Entity(
                    name=entity_data.get("name", ""),
                    metadata=EntityMetadata(
                        entity_type=metadata.get("entityType", ""),
                        interval=TimeInterval(
                            start_time=datetime.fromisoformat(interval.get("startTime").replace('Z', '+00:00')),
                            end_time=datetime.fromisoformat(interval.get("endTime").replace('Z', '+00:00'))
                        )
                    ),
                    metric=EntityMetrics(
                        first_seen=datetime.fromisoformat(entity_data.get("metric", {}).get("firstSeen").replace('Z', '+00:00')),
                        last_seen=datetime.fromisoformat(entity_data.get("metric", {}).get("lastSeen").replace('Z', '+00:00'))
                    ),
                    entity=entity_data.get("entity", {})
                )
                entities.append(entity)

            # Parse alert counts
            alert_counts = []
            for alert_data in data.get("alertCounts", []):
                alert_counts.append(AlertCount(
                    rule=alert_data.get("rule", ""),
                    count=int(alert_data.get("count", 0))
                ))

            # Parse timeline
            timeline_data = data.get("timeline", {})
            timeline = Timeline(
                buckets=[TimelineBucket(**bucket) for bucket in timeline_data.get("buckets", [])],
                bucket_size=timeline_data.get("bucketSize", "")
            ) if timeline_data else None

            # Parse widget metadata
            widget_data = data.get("widgetMetadata")
            widget_metadata = WidgetMetadata(
                uri=widget_data.get("uri", ""),
                detections=widget_data.get("detections", 0),
                total=widget_data.get("total", 0)
            ) if widget_data else None

            return EntitySummary(
                entities=entities,
                alert_counts=alert_counts,
                timeline=timeline,
                widget_metadata=widget_metadata,
                has_more_alerts=data.get("hasMoreAlerts", False),
                next_page_token=data.get("nextPageToken")
            )

        except Exception as e:
            raise APIError(f"Error parsing entity summary response: {str(e)}")

    def summarize_entities_from_query(
            self,
            query: str,
            start_time: datetime,
            end_time: datetime,
    ) -> List[EntitySummary]:
        """Get entity summaries from a UDM query.

        Args:
            query: UDM query to find entities
            start_time: Start time for the summary
            end_time: End time for the summary

        Returns:
            List of EntitySummary objects containing the results

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.base_url}/{self.instance_id}:summarizeEntitiesFromQuery"

        params = {
            "query": query,
            "timeRange.startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "timeRange.endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        }

        response = self.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Error getting entity summaries: {response.text}")

        try:
            data = response.json()
            summaries = []

            for summary_data in data.get("entitySummaries", []):
                entities = []
                for entity_data in summary_data.get("entity", []):
                    metadata = entity_data.get("metadata", {})
                    interval = metadata.get("interval", {})

                    entity = Entity(
                        name=entity_data.get("name", ""),
                        metadata=EntityMetadata(
                            entity_type=metadata.get("entityType", ""),
                            interval=TimeInterval(
                                start_time=datetime.fromisoformat(interval.get("startTime").replace('Z', '+00:00')),
                                end_time=datetime.fromisoformat(interval.get("endTime").replace('Z', '+00:00'))
                            )
                        ),
                        metric=EntityMetrics(
                            first_seen=datetime.fromisoformat(entity_data.get("metric", {}).get("firstSeen").replace('Z', '+00:00')),
                            last_seen=datetime.fromisoformat(entity_data.get("metric", {}).get("lastSeen").replace('Z', '+00:00'))
                        ),
                        entity=entity_data.get("entity", {})
                    )
                    entities.append(entity)

                summary = EntitySummary(entities=entities)
                summaries.append(summary)

            return summaries

        except Exception as e:
            raise APIError(f"Error parsing entity summaries response: {str(e)}")

    def list_iocs(
            self,
            start_time: datetime,
            end_time: datetime,
            max_matches: int = 1000,
            add_mandiant_attributes: bool = True,
            prioritized_only: bool = False,
    ) -> dict:
        """List IoC matches against ingested events."""
        url = f"{self.base_url}/{self.instance_id}/legacy:legacySearchEnterpriseWideIoCs"

        params = {
            "timestampRange.startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "timestampRange.endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "maxMatchesToReturn": max_matches,
            "addMandiantAttributes": add_mandiant_attributes,
            "fetchPrioritizedIocsOnly": prioritized_only,
        }

        response = self.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Failed to list IoCs: {response.text}")

        try:
            data = response.json()

            # Process each IoC match to ensure consistent field names
            if "matches" in data:
                for match in data["matches"]:
                    # Convert timestamps if present
                    for ts_field in ["iocIngestTimestamp", "firstSeenTimestamp", "lastSeenTimestamp"]:
                        if ts_field in match:
                            match[ts_field] = match[ts_field].rstrip("Z")

                    # Ensure consistent field names
                    if "filterProperties" in match and "stringProperties" in match["filterProperties"]:
                        props = match["filterProperties"]["stringProperties"]
                        match["properties"] = {
                            k: [v["rawValue"] for v in values["values"]]
                            for k, values in props.items()
                        }

                    # Process associations
                    if "associationIdentifier" in match:
                        # Remove duplicate associations (some have same name but different regionCode)
                        seen = set()
                        unique_associations = []
                        for assoc in match["associationIdentifier"]:
                            key = (assoc["name"], assoc["associationType"])
                            if key not in seen:
                                seen.add(key)
                                unique_associations.append(assoc)
                        match["associationIdentifier"] = unique_associations

            return data

        except Exception as e:
            raise APIError(f"Failed to process IoCs response: {str(e)}")

    def get_cases(self, case_ids: list[str]) -> CaseList:
        """Get details for specified cases.

        Args:
            case_ids (list[str]): List of case IDs to retrieve

        Returns:
            CaseList: Collection of cases with helper methods for filtering and lookup

        Raises:
            APIError: If the API request fails
            ValueError: If more than 1000 case IDs are requested
        """
        if len(case_ids) > 1000:
            raise ValueError("Maximum of 1000 cases can be retrieved in a batch")

        url = f"{self.base_url}/{self.instance_id}/legacy:legacyBatchGetCases"

        params = {
            "names": case_ids
        }

        response = self.session.get(url, params=params)

        if response.status_code != 200:
            raise APIError(f"Failed to get cases: {response.text}")

        return CaseList.from_dict(response.json())

    def get_alerts(
            self,
            start_time: datetime,
            end_time: datetime,
            snapshot_query: str = "feedback_summary.status != \"CLOSED\"",
            baseline_query: str = None,
            max_alerts: int = 1000,
            enable_cache: bool = True,
            max_attempts: int = 30,
            poll_interval: float = 1.0
    ) -> dict:
        """Get alerts within a time range.

        Args:
            start_time: Start time for alerts search
            end_time: End time for alerts search
            snapshot_query: Query to filter alerts (default: non-closed alerts)
            baseline_query: Optional baseline query
            max_alerts: Maximum number of alerts to return
            enable_cache: Whether to use caching for the request
            max_attempts: Maximum number of polling attempts
            poll_interval: Polling interval in seconds

        Returns:
            Dict containing the alerts response

        Raises:
            APIError: If the API request fails or response parsing fails
        """
        url = f"{self.base_url}/{self.instance_id}/legacy:legacyFetchAlertsView"

        params = {
            "timeRange.startTime": start_time.isoformat(),
            "timeRange.endTime": end_time.isoformat(),
            "snapshotQuery": snapshot_query,
            "alertListOptions.maxReturnedAlerts": max_alerts,
            "enableCache": "ALERTS_FEATURE_PREFERENCE_ENABLED" if enable_cache else "ALERTS_FEATURE_PREFERENCE_DISABLED",
            "fieldAggregationOptions.maxValuesPerField": 60
        }

        if baseline_query:
            params["baselineQuery"] = baseline_query

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # Create an accumulator for all updates
        final_response = {
            'progress': 0,
            'alerts': {'alerts': []},
            'complete': False
        }

        # Poll until complete or max attempts
        attempt = 0
        while attempt < max_attempts:
            attempt += 1

            # Make the request
            response = self.session.get(url, params=params, headers=headers, stream=True)

            if response.status_code != 200:
                raise APIError(f"Failed to get alerts: {response.text}")

            # Process this response
            updates = self._process_alerts_response(response)

            # Merge the updates into our accumulator
            self._merge_alert_updates(final_response, updates)

            # Check if we're done
            if final_response.get('complete'):
                break

            # If not complete and we have more attempts, wait and try again
            if attempt < max_attempts:
                time.sleep(poll_interval)

        return final_response

    def _process_alerts_response(self, response) -> list:
        """Process streaming response from alerts API.

        Args:
            response: HTTP response with streaming data

        Returns:
            List of parsed JSON updates

        Raises:
            APIError: If parsing fails and no valid updates were found
        """
        # The API can return either individual JSON objects per line
        # or an array of objects, or a mix of both
        line_buffer = []
        updates = []

        for line in response.iter_lines():
            if not line:
                continue

            line_str = line.decode('utf-8').strip()
            if not line_str:
                continue

            line_buffer.append(line_str)

            # Try to parse what we have so far
            current_buffer = ''.join(line_buffer)

            # Handle case where response starts with an array bracket
            if current_buffer.startswith('[') and not current_buffer.endswith(']'):
                # Not a complete array yet, continue collecting
                continue

            # Fix any JSON formatting issues
            current_buffer = self._fix_json_formatting(current_buffer)

            try:
                # Try parsing it as a complete object or array
                parsed_data = json.loads(current_buffer)

                # Handle the case where parsed_data is an array of updates
                if isinstance(parsed_data, list):
                    updates.extend(parsed_data)
                else:
                    updates.append(parsed_data)

                # Clear the buffer after successful parsing
                line_buffer = []
            except json.JSONDecodeError:
                # If it fails, it might be incomplete. Continue to the next line
                pass

        # If we have leftover data, try once more with aggressive fix-ups
        if line_buffer:
            try:
                current_buffer = ''.join(line_buffer)
                # Make sure array has closing bracket if it started with one
                if current_buffer.startswith('[') and not current_buffer.endswith(']'):
                    current_buffer += ']'
                # Fix potential trailing commas
                current_buffer = self._fix_json_formatting(current_buffer)

                parsed_data = json.loads(current_buffer)
                if isinstance(parsed_data, list):
                    updates.extend(parsed_data)
                else:
                    updates.append(parsed_data)
            except json.JSONDecodeError as e:
                # If we can't parse the remaining data, log but don't fail if we have some updates
                if not updates:
                    raise APIError(f"Failed to parse alerts response: {str(e)} - Data: {current_buffer}")

        if not updates:
            raise APIError("No valid data received from alerts API")

        return updates

    def _merge_alert_updates(self, target: dict, updates: list) -> None:
        """Merge alerts updates into the target dictionary.

        Args:
            target: Target dictionary to update
            updates: List of updates to merge in

        This method modifies the target dictionary in place.
        """
        for update in updates:
            # Merge all fields from this update
            for key, value in update.items():
                # Special handling for alerts to accumulate them
                if key == 'alerts' and isinstance(value, dict) and 'alerts' in value:
                    if 'alerts' not in target:
                        target['alerts'] = {'alerts': []}
                    if not isinstance(target['alerts'], dict):
                        target['alerts'] = {'alerts': []}
                    if 'alerts' not in target['alerts']:
                        target['alerts']['alerts'] = []
                    target['alerts']['alerts'].extend(value['alerts'])
                # Take the latest value for progress or overwrite other fields
                elif key == 'progress':
                    if value > target.get('progress', 0):
                        target['progress'] = value
                # For all other fields, take the latest value
                else:
                    target[key] = value

    def _fix_json_formatting(self, json_str: str) -> str:
        """Fix common JSON formatting issues.

        Args:
            json_str: JSON string to fix

        Returns:
            Fixed JSON string
        """
        # Replace trailing commas in arrays and objects which cause JSON parsing to fail
        # This regex finds commas followed by a closing bracket
        json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        return json_str

    def get_detections(
            self,
            rule_id: str,
            start_time: datetime,
            end_time: datetime,
            alert_state: AlertState = AlertState.UNSPECIFIED,
            list_basis: ListBasis = ListBasis.LIST_BASIS_UNSPECIFIED,
            snapshot_query: str = "feedback_summary.status != \"CLOSED\"",
            page_size: int = 1000,
            page_token: str = None,
            max_resp_size_bytes: int = 0,
            include_nested_detections: bool = False
    ) -> LegacySearchDetectionsResponse:
        """Get alerts within a time range."""
        url = f"{self.base_url}/{self.instance_id}/legacy:legacySearchDetections"

        params = {
            "ruleId": rule_id,
            "alertState": alert_state.value,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
            "listBasis": list_basis.value,
            "pageSize": page_size,
            "pageToken": page_token,
            "maxRespSizeBytes": max_resp_size_bytes,
            "includeNestedDetections": include_nested_detections
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }


        response = self.session.get(url, params=params, headers=headers, stream=True)

        if response.status_code != 200:
            LOGGER.error("Error Response:", response.text)
            raise APIError(f"Failed to get alerts: {response.text}")

        try:
            # Parse the array of detections
            response_content = json.loads(response.content)
            return LegacySearchDetectionsResponse.from_dict(response_content)

        except json.JSONDecodeError as e:
            LOGGER.error(f"\nError parsing JSON: {str(e)}")
            LOGGER.error("Error location:", e.pos)
            LOGGER.error("Line:", e.lineno, "Column:", e.colno)
            raise APIError(f"Failed to parse alerts response: {str(e)}")

    def import_logs(
            self,
            log_type: str,
            logs: list(),
            forwarder: str,
            source_filename: str = None
    ) -> dict:
        """Get alerts within a time range."""
        url = f"{self.base_url}/{self.instance_id}/logTypes/{log_type}/logs:import"

        body = {
            "inline_source": {
                "logs": logs,
                "forwarder": f"{self.base_url}/{self.instance_id}/forwarders/{forwarder}",
                "source_filename": source_filename
            }
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }

        response = self.session.post(url, json=body, headers=headers)

        if response.status_code != 200:
            LOGGER.error("Error Response:", response.text)
            raise APIError(f"Failed to get alerts: {response.text}")

    def list_rules(
            self,
            filter: str = "",
            page_size: int = 100,
            page_token: str = None,
            view: RuleView = RuleView.BASIC
    ) -> dict:
        """Get alerts within a time range."""
        url = f"{self.base_url}/{self.instance_id}/rules"

        params = {
            "filter": filter,
            "pageSize": page_size,
            "pageToken": page_token,
            "view": view.value
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }

        response = self.session.get(url, params=params, headers=headers)

        if response.status_code != 200:
            LOGGER.error("Error Response:", response.text)
            raise APIError(f"Failed to get alerts: {response.text}")

        try:
            # Parse the array of detections
            response_content = json.loads(response.content)
            return ListRulesResponse.from_dict(response_content)

        except json.JSONDecodeError as e:
            LOGGER.error(f"\nError parsing JSON: {str(e)}")
            LOGGER.error("Error location:", e.pos)
            LOGGER.error("Line:", e.lineno, "Column:", e.colno)
            raise APIError(f"Failed to parse alerts response: {str(e)}")

    def get_rule(
            self,
            name: str,
            view: RuleView = RuleView.BASIC
    ) -> Rule:
        """Get alerts within a time range."""
        url = f"{self.base_url}/{self.instance_id}/rules/{name}"

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }

        logging.debug("\nDebug - Initial Request:")
        logging.debug(f"URL: {url}")

        response = self.session.get(url, headers=headers)

        if response.status_code != 200:
            LOGGER.error("Error Response:", response.text)
            raise APIError(f"Failed to get alerts: {response.text}")

        try:
            # Parse the JSON response and create a CompilationResult object
            response_content = json.loads(response.content)
            return Rule.from_dict(response_content)

        except json.JSONDecodeError as e:
            LOGGER.error(f"\nError parsing JSON: {str(e)}")
            LOGGER.error("Error location:", e.pos)
            LOGGER.error("Line:", e.lineno, "Column:", e.colno)
            raise APIError(f"Failed to parse alerts response: {str(e)}")

    def verify_rule(
            self,
            rule_text: str
    ) -> CompilationResult:
        """Verifies the given rule text as UTF8 string."""
        url = f"{self.base_url}/{self.instance_id}:verifyRuleText"

        body = {
            "rule_text": rule_text
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
        }

        logging.debug("\nDebug - Initial Request:")
        logging.debug(f"URL: {url}")

        response = self.session.post(url, json=body, headers=headers)

        if response.status_code != 200:
            logging.error("Error Response:", response.text)
            raise Exception(f"Failed to verify rule: {response.text}")  # Use a more specific exception if needed

        try:
            # Parse the JSON response and create a CompilationResult object
            response_content = json.loads(response.content)
            return CompilationResult.from_dict(response_content)

        except json.JSONDecodeError as e:
            logging.error(f"\nError parsing JSON: {str(e)}")
            logging.error("Error location:", e.pos)
            logging.error("Line:", e.lineno, "Column:", e.colno)
            raise Exception(f"Failed to parse rule verification response: {str(e)}")
