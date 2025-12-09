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
"""
Provides entity search, analysis and summarization functionality for Chronicle.
"""
import ipaddress
import re
from datetime import datetime
from typing import Any

from secops.chronicle.models import (
    AlertCount,
    Entity,
    EntityMetadata,
    EntityMetrics,
    EntitySummary,
    FileMetadataAndProperties,
    FileProperty,
    FilePropertyGroup,
    PrevalenceData,
    TimeInterval,
    Timeline,
    TimelineBucket,
    WidgetMetadata,
)
from secops.exceptions import APIError


def _detect_value_type_for_query(
    value: str,
) -> tuple[str | None, str | None]:
    """Detect query fragment and preferred entity type from input value.

    Args:
        value: The value to analyze.

    Returns:
        A tuple containing query fragment and preferred entity type.
    """
    # Try IP address
    try:
        ipaddress.ip_address(value)
        return f'ip = "{value}"', "ASSET"
    except ValueError:
        pass

    # Try hash (MD5, SHA1, SHA256)
    if (
        re.match(r"^[a-fA-F0-9]{32}$", value)
        or re.match(r"^[a-fA-F0-9]{40}$", value)
        or re.match(r"^[a-fA-F0-9]{64}$", value)
    ):
        return f'hash = "{value}"', "FILE"

    # Try domain name
    if re.match(
        r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)+$",  # pylint: disable=line-too-long
        value,
    ):
        return f'domain = "{value}"', "DOMAIN_NAME"

    # Try email address
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
        return f'email = "{value}"', "USER"

    # Try MAC address
    if re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", value):
        return f'mac = "{value}"', "ASSET"

    # Try hostname
    if re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", value):
        return f'hostname = "{value}"', "ASSET"

    # Likely username pattern
    if re.match(r"^[a-zA-Z0-9_.-]+$", value):
        return f'user.userid = "{value}"', "USER"

    # Fallback to generic search
    return f'string_value = "{value}"', "ASSET"


def _parse_entity(entity_data: dict) -> Entity:
    """Parse entity dictionary into an Entity object."""
    metadata = entity_data.get("metadata", {})
    interval = metadata.get("interval", {})

    start_time = None
    end_time = None
    if interval.get("startTime"):
        start_time = datetime.fromisoformat(
            interval["startTime"].replace("Z", "+00:00")
        )
    if interval.get("endTime"):
        end_time = datetime.fromisoformat(
            interval["endTime"].replace("Z", "+00:00")
        )

    metric_data = entity_data.get("metric", {})
    first_seen = None
    last_seen = None
    if metric_data.get("firstSeen"):
        first_seen = datetime.fromisoformat(
            metric_data["firstSeen"].replace("Z", "+00:00")
        )
    if metric_data.get("lastSeen"):
        last_seen = datetime.fromisoformat(
            metric_data["lastSeen"].replace("Z", "+00:00")
        )

    return Entity(
        name=entity_data.get("name", ""),
        metadata=EntityMetadata(
            entity_type=metadata.get("entityType", ""),
            interval=(
                TimeInterval(start_time=start_time, end_time=end_time)
                if start_time and end_time
                else None
            ),
        ),
        metric=(
            EntityMetrics(first_seen=first_seen, last_seen=last_seen)
            if first_seen and last_seen
            else None
        ),
        entity=entity_data.get("entity", {}),
    )


def _summarize_entity_by_id(
    client: Any,
    entity_id: str,
    start_time: datetime,
    end_time: datetime,
    return_alerts: bool,
    return_prevalence: bool,
    include_all_udm_types: bool,
    page_size: int,
    page_token: str | None,
) -> dict:
    """Fetch entity summary data using the entity ID.

    Args:
        client: ChronicleClient instance.
        entity_id: The entity ID to query.
        start_time: Start time for data range.
        end_time: End time for data range.
        return_alerts: Whether to include alert data.
        return_prevalence: Whether to include prevalence data.
        include_all_udm_types: Whether to include all UDM event types.
        page_size: Maximum number of results per page.
        page_token: Token for pagination.

    Returns:
        Dictionary with entity summary data.

    Raises:
        APIError: If API request fails.
    """
    url = f"{client.base_url}/{client.instance_id}:summarizeEntity"

    params = {
        "entityId": entity_id,
        "timeRange.startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "timeRange.endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "returnAlerts": return_alerts,
        "returnPrevalence": return_prevalence,
        "includeAllUdmEventTypesForFirstLastSeen": include_all_udm_types,
        "pageSize": page_size,
    }
    if page_token:
        params["pageToken"] = page_token

    response = client.session.get(url, params=params)

    if response.status_code != 200:
        raise APIError(
            f"Error getting entity summary by ID ({entity_id}): {response.text}"
        )

    try:
        return response.json()
    except Exception as e:
        raise APIError(
            "Error parsing entity summary response for "
            f"ID {entity_id}: {str(e)}"
        ) from e


def summarize_entity(
    client: Any,
    value: str,
    start_time: datetime,
    end_time: datetime,
    preferred_entity_type: str | None = None,
    include_all_udm_types: bool = True,
    page_size: int = 1000,
    page_token: str | None = None,
) -> EntitySummary:
    """Get comprehensive summary information about an entity.

    Performs entity search, identifies the primary entity, and retrieves
    detailed information including alerts, timeline, and prevalence data.

    Args:
        client: Authenticated ChronicleClient instance.
        value: Entity value to search (IP, domain, hash, etc.).
        start_time: Start time for data range.
        end_time: End time for data range.
        preferred_entity_type: Preferred entity type ("ASSET", "FILE", etc.).
        include_all_udm_types: Whether to include all UDM event types.
        page_size: Maximum number of results per page.
        page_token: Token for pagination.

    Returns:
        EntitySummary object with comprehensive entity data.

    Raises:
        APIError: If API request fails.
        ValueError: If input value cannot be mapped to a query.
    """
    query_fragment, auto_detected_preferred_type = _detect_value_type_for_query(
        value
    )

    if not query_fragment:
        raise ValueError(f"Could not determine how to query for value: {value}")

    final_preferred_type = preferred_entity_type or auto_detected_preferred_type

    # Query for entities
    query_url = (
        f"{client.base_url}/{client.instance_id}:summarizeEntitiesFromQuery"
    )
    query_params = {
        "query": query_fragment,
        "timeRange.startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "timeRange.endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    query_response = client.session.get(query_url, params=query_params)
    if query_response.status_code != 200:
        raise APIError(
            f"Error querying entity summaries: {query_response.text}"
        )

    try:
        query_data = query_response.json()
    except Exception as e:
        raise APIError(
            f"Error parsing entity summaries query response: {str(e)}"
        ) from e

    # Identify primary entity and collect all entities
    all_entities: list[Entity] = []
    primary_entity: Entity | None = None
    primary_entity_id: str | None = None

    for summary_data in query_data.get("entitySummaries", []):
        for entity_data in summary_data.get("entity", []):
            entity = _parse_entity(entity_data)
            all_entities.append(entity)
            if (
                not primary_entity_id
                and entity.metadata.entity_type == final_preferred_type
            ):
                primary_entity = entity
                primary_entity_id = entity.name.split("/")[-1]

    # Fallback to first entity if no preferred match
    if not primary_entity_id and all_entities:
        primary_entity = all_entities[0]
        primary_entity_id = primary_entity.name.split("/")[-1]

    related_entities = [e for e in all_entities if e != primary_entity]

    # Create initial summary object
    combined_summary = EntitySummary(
        primary_entity=primary_entity, related_entities=related_entities
    )

    if primary_entity_id:
        # Fetch details using primary entity ID
        details_data = _summarize_entity_by_id(
            client,
            primary_entity_id,
            start_time,
            end_time,
            return_alerts=True,
            return_prevalence=False,
            include_all_udm_types=include_all_udm_types,
            page_size=page_size,
            page_token=page_token,
        )

        # Parse alerts
        alert_counts_data = details_data.get("alertCounts", [])
        if alert_counts_data:
            combined_summary.alert_counts = [
                AlertCount(
                    rule=ac.get("rule", ""), count=int(ac.get("count", 0))
                )
                for ac in alert_counts_data
            ]
        combined_summary.has_more_alerts = details_data.get(
            "hasMoreAlerts", False
        )
        combined_summary.next_page_token = details_data.get("nextPageToken")

        # Parse timeline
        timeline_data = details_data.get("timeline", {})
        if timeline_data.get("buckets"):
            combined_summary.timeline = Timeline(
                buckets=[
                    TimelineBucket(
                        alert_count=int(b.get("alertCount", 0)),
                        event_count=int(b.get("eventCount", 0)),
                    )
                    for b in timeline_data["buckets"]
                ],
                bucket_size=timeline_data.get("bucketSize", ""),
            )

        # Parse widget metadata
        widget_data = details_data.get("widgetMetadata")
        if widget_data:
            combined_summary.widget_metadata = WidgetMetadata(
                uri=widget_data.get("uri", ""),
                detections=widget_data.get("detections", 0),
                total=widget_data.get("total", 0),
            )

        # Parse file metadata/properties
        file_meta_prop_data = details_data.get("fileMetadataAndProperties")
        if file_meta_prop_data:
            metadata_list = [
                FileProperty(key=m.get("key"), value=m.get("value"))
                for m in file_meta_prop_data.get("metadata", [])
            ]
            properties_list = []
            for prop_group in file_meta_prop_data.get("properties", []):
                group_props = [
                    FileProperty(key=p.get("key"), value=p.get("value"))
                    for p in prop_group.get("properties", [])
                ]
                properties_list.append(
                    FilePropertyGroup(
                        title=prop_group.get("title"), properties=group_props
                    )
                )

            combined_summary.file_metadata_and_properties = (
                FileMetadataAndProperties(
                    metadata=metadata_list,
                    properties=properties_list,
                    query_state=file_meta_prop_data.get("queryState"),
                )
            )

        # Update primary entity if details returned a different version
        if details_data.get("entities"):
            updated_primary = _parse_entity(details_data["entities"][0])
            if updated_primary.name == primary_entity.name:
                combined_summary.primary_entity = updated_primary

    # Handle prevalence data
    if primary_entity_id:
        entity_id_for_prevalence = primary_entity_id
        is_ip_value = False
        try:
            ipaddress.ip_address(value)
            is_ip_value = True
        except ValueError:
            pass

        # For IP values, try to find the IP_ADDRESS entity ID
        if is_ip_value:
            ip_entity = next(
                (
                    e
                    for e in all_entities
                    if e.metadata.entity_type == "IP_ADDRESS"
                ),
                None,
            )
            if ip_entity:
                ip_entity_id = ip_entity.name.split("/")[-1]
                if ip_entity_id:
                    entity_id_for_prevalence = ip_entity_id

        # Get prevalence data
        try:
            prevalence_data = _summarize_entity_by_id(
                client,
                entity_id_for_prevalence,
                start_time,
                end_time,
                return_alerts=False,
                return_prevalence=True,
                include_all_udm_types=include_all_udm_types,
                page_size=page_size,
                page_token=None,
            )

            # Parse prevalence
            prevalence_result = prevalence_data.get("prevalenceResult", [])
            if prevalence_result:
                combined_summary.prevalence = [
                    PrevalenceData(
                        prevalence_time=datetime.fromisoformat(
                            p["prevalenceTime"].replace("Z", "+00:00")
                        ),
                        count=int(p.get("count", 0)),
                    )
                    for p in prevalence_result
                ]

            tpd_prevalence_result = prevalence_data.get(
                "tpdPrevalenceResult", []
            )
            if tpd_prevalence_result:
                combined_summary.tpd_prevalence = [
                    PrevalenceData(
                        prevalence_time=datetime.fromisoformat(
                            p["prevalenceTime"].replace("Z", "+00:00")
                        ),
                        count=int(p.get("count", 0)),
                    )
                    for p in tpd_prevalence_result
                ]
        except APIError as e:
            # If prevalence call fails, proceed without prevalence data
            print(
                "Warning: Failed to retrieve prevalence data for "
                f"{entity_id_for_prevalence}: {str(e)}"
            )
            combined_summary.prevalence = None
            combined_summary.tpd_prevalence = None

    return combined_summary
