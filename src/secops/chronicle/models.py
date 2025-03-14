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
"""Data models for Chronicle API responses."""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

@dataclass
class TimeInterval:
    """Time interval with start and end times."""
    start_time: datetime
    end_time: datetime

@dataclass
class EntityMetadata:
    """Metadata about an entity."""
    entity_type: str
    interval: TimeInterval

@dataclass
class EntityMetrics:
    """Metrics about an entity."""
    first_seen: datetime
    last_seen: datetime

@dataclass
class DomainInfo:
    """Information about a domain entity."""
    name: str
    first_seen_time: datetime
    last_seen_time: datetime

@dataclass
class AssetInfo:
    """Information about an asset entity."""
    ip: List[str]

@dataclass
class Entity:
    """Entity information returned by Chronicle."""
    name: str
    metadata: EntityMetadata
    metric: EntityMetrics
    entity: Dict  # Can contain domain or asset info

@dataclass
class WidgetMetadata:
    """Metadata for UI widgets."""
    uri: str
    detections: int
    total: int

@dataclass
class TimelineBucket:
    """A bucket in the timeline."""
    alert_count: int = 0
    event_count: int = 0

@dataclass
class Timeline:
    """Timeline information."""
    buckets: List[TimelineBucket]
    bucket_size: str

@dataclass
class AlertCount:
    """Alert count for a rule."""
    rule: str
    count: int

class AlertState(Enum):
    UNSPECIFIED = 'UNSPECIFIED'
    NOT_ALERTING = 'NOT_ALERTING'
    ALERTING = 'ALERTING'

class ListBasis(Enum):
    LIST_BASIS_UNSPECIFIED = "LIST_BASIS_UNSPECIFIED"
    DETECTION_TIME = "DETECTION_TIME"
    CREATED_TIME = "CREATED_TIME"

class RuleView(Enum):
    RULE_VIEW_UNSPECIFIED = "RULE_VIEW_UNSPECIFIED"
    BASIC = "BASIC"
    FULL = "FULL"
    REVISION_METADATA_ONLY = "REVISION_METADATA_ONLY"

@dataclass
class EntitySummary:
    """Complete entity summary response."""
    entities: List[Entity]
    alert_counts: Optional[List[AlertCount]] = None
    timeline: Optional[Timeline] = None
    widget_metadata: Optional[WidgetMetadata] = None
    has_more_alerts: bool = False
    next_page_token: Optional[str] = None

class SoarPlatformInfo:
    """SOAR platform information for a case."""
    def __init__(self, case_id: str, platform_type: str):
        self.case_id = case_id
        self.platform_type = platform_type

    @classmethod
    def from_dict(cls, data: dict) -> 'SoarPlatformInfo':
        """Create from API response dict."""
        return cls(
            case_id=data.get('caseId'),
            platform_type=data.get('responsePlatformType')
        )

class Case:
    """Represents a Chronicle case."""
    def __init__(
        self,
        id: str,
        display_name: str,
        stage: str,
        priority: str,
        status: str,
        soar_platform_info: SoarPlatformInfo = None,
        alert_ids: list[str] = None
    ):
        self.id = id
        self.display_name = display_name
        self.stage = stage
        self.priority = priority
        self.status = status
        self.soar_platform_info = soar_platform_info
        self.alert_ids = alert_ids or []

    @classmethod
    def from_dict(cls, data: dict) -> 'Case':
        """Create from API response dict."""
        return cls(
            id=data.get('id'),
            display_name=data.get('displayName'),
            stage=data.get('stage'),
            priority=data.get('priority'),
            status=data.get('status'),
            soar_platform_info=SoarPlatformInfo.from_dict(data['soarPlatformInfo']) if data.get('soarPlatformInfo') else None,
            alert_ids=data.get('alertIds', [])
        )

class CaseList:
    """Collection of Chronicle cases with helper methods."""
    def __init__(self, cases: list[Case]):
        self.cases = cases
        self._case_map = {case.id: case for case in cases}

    def get_case(self, case_id: str) -> Optional[Case]:
        """Get a case by ID."""
        return self._case_map.get(case_id)

    def filter_by_priority(self, priority: str) -> list[Case]:
        """Get cases with specified priority."""
        return [case for case in self.cases if case.priority == priority]

    def filter_by_status(self, status: str) -> list[Case]:
        """Get cases with specified status."""
        return [case for case in self.cases if case.status == status]

    def filter_by_stage(self, stage: str) -> list[Case]:
        """Get cases with specified stage."""
        return [case for case in self.cases if case.stage == stage]

    @classmethod
    def from_dict(cls, data: dict) -> 'CaseList':
        """Create from API response dict."""
        cases = [Case.from_dict(case_data) for case_data in data.get('cases', [])]
        return cls(cases)

class Severity:
    """Represents the severity level of the rule."""

    def __init__(self, display_name: str):
        """Initializes a Severity object."""
        self.display_name = display_name

    def __repr__(self):
        """Returns a string representation of the Severity object."""
        return f"Severity(display_name='{self.display_name}')"

    @classmethod
    def from_dict(cls, data: dict) -> "Severity":
        """Creates a Severity object from a dictionary."""
        return cls(display_name=data.get("displayName"))

class CompilationPosition:
    """Represents the location of a compilation diagnostic in rule text."""

    def __init__(
            self,
            start_line: Optional[int] = None,
            start_column: Optional[int] = None,
            end_line: Optional[int] = None,
            end_column: Optional[int] = None,
    ):
        """Initializes a CompilationPosition object."""
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    def __repr__(self):
        """Returns a string representation of the CompilationPosition object."""
        return f"CompilationPosition(start_line={self.start_line}, start_column={self.start_column}, end_line={self.end_line}, end_column={self.end_column})"

    @classmethod
    def from_dict(cls, data: dict) -> 'CompilationPosition':
        """Creates a CompilationPosition object from a dictionary."""
        return cls(
            start_line=data.get('startLine'),
            start_column=data.get('startColumn'),
            end_line=data.get('endLine'),
            end_column=data.get('endColumn'),
        )

class CompilationDiagnostic:
    """Represents a compilation diagnostic object."""

    def __init__(
            self,
            message: str,
            position: Optional[CompilationPosition] = None,
            severity: Optional[Severity] = None,
            uri: Optional[str] = None
    ):
        """Initializes a CompilationDiagnostic object."""
        self.message = message
        self.position = position
        self.severity = severity
        self.uri = uri

    def __repr__(self):
        """Returns a string representation of the CompilationDiagnostic object."""
        return f"CompilationDiagnostic(message='{self.message}', position={self.position}, severity={self.severity}, uri='{self.uri}')"

    @classmethod
    def from_dict(cls, data: dict) -> 'CompilationDiagnostic':
        """Creates a CompilationDiagnostic object from a dictionary."""
        severity_str = data.get('severity')
        severity = Severity(severity_str) if severity_str else None

        position_data = data.get('position')
        position = CompilationPosition.from_dict(position_data) if position_data else None

        return cls(
            message=data.get('message'),
            position=position,
            severity=severity,
            uri=data.get('uri')
        )

class CompilationResult:
    """Represents the result of rule text compilation."""

    def __init__(
            self,
            success: bool,
            compilation_diagnostics: Optional[List["CompilationDiagnostic"]] = None,
    ):
        """Initializes a CompilationResult object."""
        self.success = success
        self.compilation_diagnostics = compilation_diagnostics

    def __repr__(self):
        """Returns a string representation of the CompilationResult object."""
        return f"CompilationResult(success={self.success}, compilation_diagnostics={self.compilation_diagnostics})"

    @classmethod
    def from_dict(cls, data: dict) -> "CompilationResult":
        """Creates a CompilationResult object from a dictionary."""
        diagnostics_data = data.get("compilationDiagnostics")
        diagnostics = []
        if diagnostics_data:
            for diagnostic_data in diagnostics_data:
                diagnostics.append(CompilationDiagnostic.from_dict(diagnostic_data))

        return cls(
            success=data.get("success", False),
            compilation_diagnostics=diagnostics
        )

class CompilationState(Enum):
    """Represents the compilation state of a rule."""
    COMPILATION_STATE_UNSPECIFIED = "COMPILATION_STATE_UNSPECIFIED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"

class RuleType(Enum):
    """Represents the YARA-L rule type."""
    RULE_TYPE_UNSPECIFIED = "RULE_TYPE_UNSPECIFIED"
    SINGLE_EVENT = "SINGLE_EVENT"
    MULTI_EVENT = "MULTI_EVENT"

class RunFrequency(Enum):
    """Represents the allowed run frequencies of a rule."""
    RUN_FREQUENCY_UNSPECIFIED = "RUN_FREQUENCY_UNSPECIFIED"
    LIVE = "LIVE"
    HOURLY = "HOURLY"
    DAILY = "DAILY"

# Rest of the Rule class remains the same as in the previous response
class Rule:
    """Represents a rule resource."""

    def __init__(
            self,
            name: str,
            revision_id: str,
            display_name: str,
            text: str,
            author: str,
            severity: Optional["Severity"] = None,
            metadata: Optional[Dict[str, str]] = None,
            create_time: Optional[datetime] = None,
            revision_create_time: Optional[datetime] = None,
            compilation_state: Optional["CompilationState"] = None,
            type: Optional["RuleType"] = None,
            reference_lists: Optional[List[str]] = None,
            allowed_run_frequencies: Optional[List["RunFrequency"]] = None,
            etag: Optional[str] = None,
            scope: Optional[str] = None,
            compilation_diagnostics: Optional[List["CompilationDiagnostic"]] = None,
            near_real_time_live_rule_eligible: Optional[bool] = None,
            data_tables: Optional[List[str]] = None,
    ):
        """Initializes a Rule object."""
        self.name = name
        self.revision_id = revision_id
        self.display_name = display_name
        self.text = text
        self.author = author
        self.severity = severity
        self.metadata = metadata or {}
        self.create_time = create_time
        self.revision_create_time = revision_create_time
        self.compilation_state = compilation_state
        self.type = type
        self.reference_lists = reference_lists or []
        self.allowed_run_frequencies = allowed_run_frequencies or []
        self.etag = etag
        self.scope = scope
        self.compilation_diagnostics = compilation_diagnostics or []
        self.near_real_time_live_rule_eligible = near_real_time_live_rule_eligible
        self.data_tables = data_tables or []

    def __repr__(self):
        """Returns a string representation of the Rule object."""
        return f"Rule(name='{self.name}', revision_id='{self.revision_id}', display_name='{self.display_name}', ...)"  # Add more attributes if needed

    @classmethod
    def from_dict(cls, data: dict) -> "Rule":
        """Creates a Rule object from a dictionary."""
        severity_data = data.get("severity")
        severity = Severity.from_dict(severity_data) if severity_data else None  # Updated to use Severity.from_dict

        diagnostics_data = data.get("compilationDiagnostics")
        diagnostics = [CompilationDiagnostic.from_dict(d) for d in diagnostics_data] if diagnostics_data else []

        create_time = data.get("createTime", None)

        revision_create_time = data.get("revisionCreateTime", None)

        compilation_state_str = data.get("compilationState")
        compilation_state = CompilationState(compilation_state_str) if compilation_state_str else None

        rule_type_str = data.get("type")
        rule_type = RuleType(rule_type_str) if rule_type_str else None

        allowed_run_frequencies_str = data.get("allowedRunFrequencies")
        allowed_run_frequencies = [RunFrequency(f) for f in allowed_run_frequencies_str] if allowed_run_frequencies_str else []

        return cls(
            name=data.get("name"),
            revision_id=data.get("revisionId"),
            display_name=data.get("displayName"),
            text=data.get("text"),
            author=data.get("author"),
            severity=severity,
            metadata=data.get("metadata"),
            create_time=create_time,
            revision_create_time=revision_create_time,
            compilation_state=compilation_state,
            type=rule_type,
            reference_lists=data.get("referenceLists"),
            allowed_run_frequencies=allowed_run_frequencies,
            etag=data.get("etag"),
            scope=data.get("scope"),
            compilation_diagnostics=diagnostics,
            near_real_time_live_rule_eligible=data.get("nearRealTimeLiveRuleEligible"),
            data_tables=data.get("dataTables"),
        )

class ListRulesResponse:
    """Represents the response body for the ListRules method."""

    def __init__(self, rules: Optional[List["Rule"]] = None, next_page_token: Optional[str] = None):
        """Initializes a ListRulesResponse object."""
        self.rules = rules or []
        self.next_page_token = next_page_token

    def __repr__(self):
        """Returns a string representation of the ListRulesResponse object."""
        return f"ListRulesResponse(rules={self.rules}, next_page_token='{self.next_page_token}')"

    @classmethod
    def from_dict(cls, data: dict) -> "ListRulesResponse":
        """Creates a ListRulesResponse object from a dictionary."""
        rules_data = data.get("rules")
        rules = [Rule.from_dict(rule_data) for rule_data in rules_data] if rules_data else []

        return cls(
            rules=rules,
            next_page_token=data.get("next_page_token"),
        )

class LegacySearchDetectionsResponse:
    """Represents the LegacySearchDetections response message."""

    def __init__(
            self,
            detections: Optional[List[Dict[str, any]]] = None,
            nested_detection_samples: Optional[List[Dict[str, any]]] = None,
            next_page_token: Optional[str] = None,
            resp_too_large_detections_truncated: Optional[bool] = None,
    ):
        """Initializes a LegacySearchDetectionsResponse object."""
        self.detections = detections or []
        self.nested_detection_samples = nested_detection_samples or []
        self.next_page_token = next_page_token
        self.resp_too_large_detections_truncated = resp_too_large_detections_truncated

    def __repr__(self):
        """Returns a string representation of the LegacySearchDetectionsResponse object."""
        return (
            f"LegacySearchDetectionsResponse(detections={self.detections}, "
            f"nested_detection_samples={self.nested_detection_samples}, "
            f"next_page_token='{self.next_page_token}', "
            f"resp_too_large_detections_truncated={self.resp_too_large_detections_truncated})"
        )

    @classmethod
    def from_dict(cls, data: dict) -> "LegacySearchDetectionsResponse":
        """Creates a LegacySearchDetectionsResponse object from a dictionary."""
        return cls(
            detections=data.get("detections", []),
            nested_detection_samples=data.get("nestedDetectionSamples", []),
            next_page_token=data.get("nextPageToken"),
            resp_too_large_detections_truncated=data.get("respTooLargeDetectionsTruncated"),
        )