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
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from secops.exceptions import SecOpsError

# Use built-in StrEnum if Python 3.11+, otherwise create a compatible version
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        """String enum implementation for Python versions before 3.11."""

        def __str__(self) -> str:
            return self.value


class AlertState(str, Enum):
    """Alert state for filtering detections.

    The type of alerting set up for a security result.
    """

    UNSPECIFIED = "UNSPECIFIED"
    NOT_ALERTING = "NOT_ALERTING"
    ALERTING = "ALERTING"

    def __str__(self) -> str:
        return self.value


class ListBasis(str, Enum):
    """List basis for determining time filter application.

    Type of timestamp to use for listing detections.
    """

    LIST_BASIS_UNSPECIFIED = "LIST_BASIS_UNSPECIFIED"
    DETECTION_TIME = "DETECTION_TIME"
    CREATED_TIME = "CREATED_TIME"

    def __str__(self) -> str:
        return self.value


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

    ip: list[str]


@dataclass
class Entity:
    """Entity information returned by Chronicle."""

    name: str
    metadata: EntityMetadata
    metric: EntityMetrics
    entity: dict  # Can contain domain or asset info


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

    buckets: list[TimelineBucket]
    bucket_size: str


@dataclass
class AlertCount:
    """Alert count for a rule."""

    rule: str
    count: int


@dataclass
class PrevalenceData:
    """Represents prevalence data for an entity."""

    prevalence_time: datetime
    count: int


@dataclass
class FileProperty:
    """Represents a key-value property for a file."""

    key: str
    value: str


@dataclass
class FilePropertyGroup:
    """Represents a group of file properties."""

    title: str
    properties: list[FileProperty]


@dataclass
class FileMetadataAndProperties:
    """Represents file metadata and properties."""

    metadata: list[FileProperty]
    properties: list[FilePropertyGroup]
    query_state: str | None = None


@dataclass
class EntitySummary:
    """
    Complete entity summary response, potentially combining multiple API calls.
    """

    primary_entity: Entity | None = None
    related_entities: list[Entity] = field(default_factory=list)
    alert_counts: list[AlertCount] | None = None
    timeline: Timeline | None = None
    widget_metadata: WidgetMetadata | None = None
    prevalence: list[PrevalenceData] | None = None
    tpd_prevalence: list[PrevalenceData] | None = None
    file_metadata_and_properties: FileMetadataAndProperties | None = None
    has_more_alerts: bool = False
    next_page_token: str | None = None


class DataExportStage(str, Enum):
    """Stage/status of a data export request."""

    STAGE_UNSPECIFIED = "STAGE_UNSPECIFIED"
    IN_QUEUE = "IN_QUEUE"
    PROCESSING = "PROCESSING"
    FINISHED_FAILURE = "FINISHED_FAILURE"
    FINISHED_SUCCESS = "FINISHED_SUCCESS"
    CANCELLED = "CANCELLED"


@dataclass
class DataExportStatus:
    """Status of a data export request."""

    stage: DataExportStage
    progress_percentage: int | None = None
    error: str | None = None


@dataclass
class DataExport:
    """Data export resource."""

    name: str
    start_time: datetime
    end_time: datetime
    gcs_bucket: str
    data_export_status: DataExportStatus
    log_type: str | None = None
    export_all_logs: bool = False


class SoarPlatformInfo:
    """SOAR platform information for a case."""

    def __init__(self, case_id: str, platform_type: str):
        self.case_id = case_id
        self.platform_type = platform_type

    @classmethod
    def from_dict(cls, data: dict) -> "SoarPlatformInfo":
        """Create from API response dict."""
        return cls(
            case_id=data.get("caseId"),
            platform_type=data.get("responsePlatformType"),
        )


class Case:
    """Represents a Chronicle case."""

    def __init__(
        self,
        id: str,  # pylint: disable=redefined-builtin
        display_name: str,
        stage: str,
        priority: str,
        status: str,
        soar_platform_info: SoarPlatformInfo | None = None,
        alert_ids: list[str] | None = None,
    ):
        self.id = id
        self.display_name = display_name
        self.stage = stage
        self.priority = priority
        self.status = status
        self.soar_platform_info = soar_platform_info
        self.alert_ids = alert_ids or []

    @classmethod
    def from_dict(cls, data: dict) -> "Case":
        """Create from API response dict."""
        return cls(
            id=data.get("id"),
            display_name=data.get("displayName"),
            stage=data.get("stage"),
            priority=data.get("priority"),
            status=data.get("status"),
            soar_platform_info=(
                SoarPlatformInfo.from_dict(data["soarPlatformInfo"])
                if data.get("soarPlatformInfo")
                else None
            ),
            alert_ids=data.get("alertIds", []),
        )


class CaseList:
    """Collection of Chronicle cases with helper methods."""

    def __init__(self, cases: list[Case]):
        self.cases = cases
        self._case_map = {case.id: case for case in cases}

    def get_case(self, case_id: str) -> Case | None:
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
    def from_dict(cls, data: dict) -> "CaseList":
        """Create from API response dict."""
        cases = [
            Case.from_dict(case_data) for case_data in data.get("cases", [])
        ]
        return cls(cases)


# Dashboard Models


class TileType(str, Enum):
    """Valid tile types."""

    VISUALIZATION = "TILE_TYPE_VISUALIZATION"
    BUTTON = "TILE_TYPE_BUTTON"


@dataclass
class InputInterval:
    """Input interval values to query."""

    time_window: dict[str, Any] | None = None
    relative_time: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Create from a dictionary."""
        return cls(
            time_window=data.get("time_window") or data.get("timeWindow"),
            relative_time=data.get("relative_time") or data.get("relativeTime"),
        )

    def __post_init__(self):
        """Validate that only one of `time_window` or `relative_time` is set."""
        if self.time_window is not None and self.relative_time is not None:
            raise ValueError(
                "Only one of `time_window` or `relative_time` can be set."
            )
        if self.time_window is None and self.relative_time is None:
            raise ValueError(
                "One of `time_window` or `relative_time` must be set."
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        result = {}
        if self.time_window:
            result["timeWindow"] = self.time_window
        if self.relative_time:
            result["relativeTime"] = self.relative_time
        return result


@dataclass
class DashboardQuery:
    """Dashboard query Model."""

    query: str
    input: InputInterval | str
    name: str
    etag: str

    def __post_init__(self):
        """Post init to handle field validation and transformation."""

        try:
            if isinstance(self.input, str):
                self.input = InputInterval.from_dict(json.loads(self.input))
        except ValueError as e:
            raise SecOpsError(f"Value must be valid JSON string: {e}") from e

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Create from a dictionary."""
        return cls(
            query=data.get("query"),
            input=(
                InputInterval.from_dict(data["input"])
                if isinstance(data["input"], dict)
                else data["input"]
            ),
            name=data.get("name"),
            etag=data.get("etag"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

    def update_fields(self) -> list[str]:
        """Return a list of fields that have been modified."""
        return [
            f"dashboard_query.{field}"
            for field in ["query", "input"]
            if getattr(self, field) is not None
        ]


@dataclass
class DashboardChart:
    """Dashboard Chart Model."""

    name: str
    etag: str
    display_name: str | None = None
    description: str | None = None
    tile_type: TileType | None = None
    visualization: dict[str, Any] | str | None = None
    drill_down_config: dict[str, Any] | str | None = None
    chart_datasource: dict[str, Any] | str | None = None

    def __post_init__(self):
        """Post init to handle field validation and transformation."""
        try:
            if self.visualization and isinstance(self.visualization, str):
                self.visualization = json.loads(self.visualization)
            if self.drill_down_config and isinstance(
                self.drill_down_config, str
            ):
                self.drill_down_config = json.loads(self.drill_down_config)
            if self.chart_datasource and isinstance(self.chart_datasource, str):
                self.chart_datasource = json.loads(self.chart_datasource)
        except ValueError as e:
            raise SecOpsError(f"Value must be valid JSON string: {e}") from e

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Create from a dictionary."""
        return cls(
            name=data.get("name"),
            etag=data.get("etag"),
            display_name=data.get("displayName") or data.get("display_name"),
            description=data.get("description"),
            tile_type=data.get("tileType") or data.get("tile_type"),
            visualization=data.get("visualization"),
            drill_down_config=(
                data.get("drillDownConfig") or data.get("drill_down_config")
            ),
            chart_datasource=(
                data.get("chartDatasource") or data.get("chart_datasource")
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary."""
        return asdict(
            self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )

    def update_fields(self) -> list[str]:
        """Return a list of fields that have been modified."""
        return [
            f"dashboard_chart.{field}"
            for field in [
                "display_name",
                "description",
                "tile_type",
                "visualization",
                "drill_down_config",
                "chart_datasource",
            ]
            if getattr(self, field) is not None
        ]


class APIVersion(StrEnum):
    V1 = "v1"
    V1BETA = "v1beta"
    V1ALPHA = "v1alpha"
