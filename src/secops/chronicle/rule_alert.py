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
"""Alert functionality for Chronicle rules."""

from datetime import datetime
from typing import Any, Literal

from secops.chronicle.utils.request_utils import chronicle_request


def get_alert(
    client, alert_id: str, include_detections: bool = False
) -> dict[str, Any]:
    """Gets an alert by ID.

    Args:
        client: ChronicleClient instance
        alert_id: ID of the alert to retrieve
        include_detections: Whether to include detection details in the response

    Returns:
        Dictionary containing alert information

    Raises:
        APIError: If the API request fails
    """
    params = {"alertId": alert_id}
    if include_detections:
        params["includeDetections"] = True

    return chronicle_request(
        client,
        method="GET",
        endpoint_path="legacy:legacyGetAlert",
        params=params,
        error_message="Failed to get alert",
    )


def update_alert(
    client,
    alert_id: str,
    confidence_score: int | None = None,
    reason: str | None = None,
    reputation: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    verdict: str | None = None,
    risk_score: int | None = None,
    disregarded: bool | None = None,
    severity: int | None = None,
    comment: str | Literal[""] | None = None,
    root_cause: str | Literal[""] | None = None,
) -> dict[str, Any]:
    """Updates an alert's properties.

    Args:
        client: ChronicleClient instance
        alert_id: ID of the alert to update
        confidence_score: Confidence score [0-100] of the alert
        reason: Reason for closing an alert. Valid values:
            - "REASON_UNSPECIFIED"
            - "REASON_NOT_MALICIOUS"
            - "REASON_MALICIOUS"
            - "REASON_MAINTENANCE"
        reputation: Categorization of usefulness. Valid values:
            - "REPUTATION_UNSPECIFIED"
            - "USEFUL"
            - "NOT_USEFUL"
        priority: Alert priority. Valid values:
            - "PRIORITY_UNSPECIFIED"
            - "PRIORITY_INFO"
            - "PRIORITY_LOW"
            - "PRIORITY_MEDIUM"
            - "PRIORITY_HIGH"
            - "PRIORITY_CRITICAL"
        status: Alert status. Valid values:
            - "STATUS_UNSPECIFIED"
            - "NEW"
            - "REVIEWED"
            - "CLOSED"
            - "OPEN"
        verdict: Verdict on the alert. Valid values:
            - "VERDICT_UNSPECIFIED"
            - "TRUE_POSITIVE"
            - "FALSE_POSITIVE"
        risk_score: Risk score [0-100] of the alert
        disregarded: Whether the alert should be disregarded
        severity: Severity score [0-100] of the alert
        comment: Analyst comment (empty string is valid to clear)
        root_cause: Alert root cause (empty string is valid to clear)

    Returns:
        Dictionary containing updated alert information

    Raises:
        APIError: If the API request fails
        ValueError: If invalid values are provided
    """
    # Validate inputs
    priority_values = [
        "PRIORITY_UNSPECIFIED",
        "PRIORITY_INFO",
        "PRIORITY_LOW",
        "PRIORITY_MEDIUM",
        "PRIORITY_HIGH",
        "PRIORITY_CRITICAL",
    ]
    reason_values = [
        "REASON_UNSPECIFIED",
        "REASON_NOT_MALICIOUS",
        "REASON_MALICIOUS",
        "REASON_MAINTENANCE",
    ]
    reputation_values = ["REPUTATION_UNSPECIFIED", "USEFUL", "NOT_USEFUL"]
    status_values = ["STATUS_UNSPECIFIED", "NEW", "REVIEWED", "CLOSED", "OPEN"]
    verdict_values = ["VERDICT_UNSPECIFIED", "TRUE_POSITIVE", "FALSE_POSITIVE"]

    # Validate enum values if provided
    if priority and priority not in priority_values:
        raise ValueError(f"priority must be one of {priority_values}")
    if reason and reason not in reason_values:
        raise ValueError(f"reason must be one of {reason_values}")
    if reputation and reputation not in reputation_values:
        raise ValueError(f"reputation must be one of {reputation_values}")
    if status and status not in status_values:
        raise ValueError(f"status must be one of {status_values}")
    if verdict and verdict not in verdict_values:
        raise ValueError(f"verdict must be one of {verdict_values}")

    # Validate score ranges
    if confidence_score is not None and not 0 <= confidence_score <= 100:
        raise ValueError("confidence_score must be between 0 and 100")
    if risk_score is not None and not 0 <= risk_score <= 100:
        raise ValueError("risk_score must be between 0 and 100")
    if severity is not None and not 0 <= severity <= 100:
        raise ValueError("severity must be between 0 and 100")

    # Build feedback dictionary with only provided values
    feedback = {
        "confidence_score": confidence_score,
        "reason": reason,
        "reputation": reputation,
        "priority": priority,
        "status": status,
        "verdict": verdict,
        "risk_score": risk_score,
        "disregarded": disregarded,
        "severity": severity,
        "comment": comment,
        "root_cause": root_cause,
    }
    feedback = {k: v for k, v in feedback.items() if v is not None}

    # Check if at least one property is provided
    if not feedback:
        raise ValueError(
            "At least one alert property must be specified for update"
        )

    payload = {
        "alert_id": alert_id,
        "feedback": feedback,
    }

    return chronicle_request(
        client,
        method="POST",
        endpoint_path="legacy:legacyUpdateAlert",
        json=payload,
        error_message="Failed to update alert",
    )


def bulk_update_alerts(
    client,
    alert_ids: list[str],
    confidence_score: int | None = None,
    reason: str | None = None,
    reputation: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    verdict: str | None = None,
    risk_score: int | None = None,
    disregarded: bool | None = None,
    severity: int | None = None,
    comment: str | Literal[""] | None = None,
    root_cause: str | Literal[""] | None = None,
) -> list[dict[str, Any]]:
    """Updates multiple alerts with the same properties.

    This is a helper function that iterates through the list of alert IDs
    and applies the same updates to each alert.

    Args:
        client: ChronicleClient instance
        alert_ids: List of alert IDs to update
        confidence_score: Confidence score [0-100] of the alert
        reason: Reason for closing an alert
        reputation: Categorization of usefulness
        priority: Alert priority
        status: Alert status
        verdict: Verdict on the alert
        risk_score: Risk score [0-100] of the alert
        disregarded: Whether the alert should be disregarded
        severity: Severity score [0-100] of the alert
        comment: Analyst comment (empty string is valid to clear)
        root_cause: Alert root cause (empty string is valid to clear)

    Returns:
        List of dictionaries containing updated alert information

    Raises:
        APIError: If any API request fails
        ValueError: If invalid values are provided
    """
    results = []

    for alert_id in alert_ids:
        result = update_alert(
            client,
            alert_id.strip(),
            confidence_score,
            reason,
            reputation,
            priority,
            status,
            verdict,
            risk_score,
            disregarded,
            severity,
            comment,
            root_cause,
        )
        results.append(result)

    return results


def search_rule_alerts(
    client,
    start_time: datetime,
    end_time: datetime,
    rule_status: str | None = None,
    page_size: int | None = None,
) -> dict[str, Any]:
    """Search for alerts generated by rules.

    Args:
        client: ChronicleClient instance
        start_time: Start time for the search (inclusive)
        end_time: End time for the search (exclusive)
        rule_status: Filter by rule status
            (deprecated - not currently supported by the API)
        page_size: Maximum number of alerts to return

    Returns:
        Dictionary containing alert search results with the format:
        {
            "ruleAlerts": [
                {
                    "alerts": [
                        {
                            "id": "alert_id",
                            "detectionTimestamp": "timestamp",
                            "commitTimestamp": "timestamp",
                            "alertingType": "ALERTING",
                            "ruleType": "SINGLE_EVENT",
                            "resultEvents": {
                                "variable_name": {
                                    "eventSamples": [
                                        {
                                            "event": { ... event details ... },
                                            "rawLogToken": "token"
                                        }
                                    ]
                                }
                            },
                            "timeWindow": {
                                "startTime": "timestamp",
                                "endTime": "timestamp"
                            }
                        }
                    ],
                    "ruleMetadata": {
                        "properties": {
                            "ruleId": "rule_id",
                            "name": "rule_name",
                            "text": "rule_text",
                            "metadata": { ... rule metadata ... }
                        }
                    }
                }
            ],
            "tooManyAlerts": boolean
        }

    Raises:
        APIError: If the API request fails
    """
    _ = (rule_status,)

    params = {
        "timeRange.start_time": start_time.isoformat(),
        "timeRange.end_time": end_time.isoformat(),
        "maxNumAlertsToReturn": page_size,
    }
    params = {k: v for k, v in params.items() if v is not None}

    return chronicle_request(
        client,
        method="GET",
        endpoint_path="legacy:legacySearchRulesAlerts",
        params=params,
        error_message="Failed to search rule alerts",
    )
