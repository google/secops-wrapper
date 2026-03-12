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


class DetectionType(StrEnum):
    """Detection type for investigation associations.

    The type of identifiers provided for fetching associated investigations.
    """

    UNSPECIFIED = "DETECTION_TYPE_UNSPECIFIED"
    ALERT = "DETECTION_TYPE_ALERT"
    CASE = "DETECTION_TYPE_CASE"


class PythonVersion(str, Enum):
    """Python version for compatibility checks."""

    UNSPECIFIED = "PYTHON_VERSION_UNSPECIFIED"
    PYTHON_2_7 = "V2_7"
    PYTHON_3_7 = "V3_7"
    PYTHON_3_11 = "V3_11"


class DiffType(str, Enum):
    """Type of diff to retrieve."""

    COMMERCIAL = "Commercial"
    PRODUCTION = "Production"
    STAGING = "Staging"


class TargetMode(str, Enum):
    """Target mode for integration transition."""

    PRODUCTION = "Production"
    STAGING = "Staging"


class IntegrationType(str, Enum):
    """Type of integration."""

    UNSPECIFIED = "INTEGRATION_TYPE_UNSPECIFIED"
    RESPONSE = "RESPONSE"
    EXTENSION = "EXTENSION"


class IntegrationParamType(str, Enum):
    """Type of integration parameter."""

    PARAM_TYPE_UNSPECIFIED = "PARAM_TYPE_UNSPECIFIED"
    BOOLEAN = "BOOLEAN"
    INT = "INT"
    STRING = "STRING"
    PASSWORD = "PASSWORD"
    IP = "IP"
    IP_OR_HOST = "IP_OR_HOST"
    URL = "URL"
    DOMAIN = "DOMAIN"
    EMAIL = "EMAIL"
    VALUES_LIST = "VALUES_LIST"
    VALUES_AS_SEMICOLON_SEPARATED_STRING = (
        "VALUES_AS_SEMICOLON_SEPARATED_STRING"
    )
    MULTI_VALUES_SELECTION = "MULTI_VALUES_SELECTION"
    SCRIPT = "SCRIPT"
    FILTER_LIST = "FILTER_LIST"


@dataclass
class IntegrationParam:
    """A parameter definition for a Chronicle SOAR integration.

    Attributes:
        display_name: Human-readable label shown in the UI.
        property_name: The programmatic key used in code/config.
        type: The data type of the parameter (see IntegrationParamType).
        description: Optional. Explanation of what the parameter is for.
        mandatory: Whether the parameter must be supplied. Defaults to False.
        default_value: Optional. Pre-filled value shown in the UI.
    """

    display_name: str
    property_name: str
    type: IntegrationParamType
    mandatory: bool
    description: str | None = None
    default_value: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "displayName": self.display_name,
            "propertyName": self.property_name,
            "type": str(self.type.value),
            "mandatory": self.mandatory,
        }
        if self.description is not None:
            data["description"] = self.description
        if self.default_value is not None:
            data["defaultValue"] = self.default_value
        return data


class ActionParamType(str, Enum):
    """Action parameter types for Chronicle SOAR integration actions."""

    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    WFS_REPOSITORY = "WFS_REPOSITORY"
    USER_REPOSITORY = "USER_REPOSITORY"
    STAGES_REPOSITORY = "STAGES_REPOSITORY"
    CLOSE_CASE_REASON_REPOSITORY = "CLOSE_CASE_REASON_REPOSITORY"
    CLOSE_CASE_ROOT_CAUSE_REPOSITORY = "CLOSE_CASE_ROOT_CAUSE_REPOSITORY"
    PRIORITIES_REPOSITORY = "PRIORITIES_REPOSITORY"
    EMAIL_CONTENT = "EMAIL_CONTENT"
    CONTENT = "CONTENT"
    PASSWORD = "PASSWORD"
    ENTITY_TYPE = "ENTITY_TYPE"
    MULTI_VALUES = "MULTI_VALUES"
    LIST = "LIST"
    CODE = "CODE"
    MULTIPLE_CHOICE_PARAMETER = "MULTIPLE_CHOICE_PARAMETER"


class ActionType(str, Enum):
    """Action types for Chronicle SOAR integration actions."""

    UNSPECIFIED = "ACTION_TYPE_UNSPECIFIED"
    STANDARD = "STANDARD"
    AI_AGENT = "AI_AGENT"


@dataclass
class ActionParameter:
    """A parameter definition for a Chronicle SOAR integration action.

    Attributes:
        display_name: The parameter's display name. Maximum 150 characters.
        type: The parameter's type.
        description: The parameter's description. Maximum 150 characters.
        mandatory: Whether the parameter is mandatory.
        default_value: The default value of the parameter.
            Maximum 150 characters.
        optional_values: Parameter's optional values. Maximum 50 items.
    """

    display_name: str
    type: ActionParamType
    description: str
    mandatory: bool
    default_value: str | None = None
    optional_values: list[str] | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "displayName": self.display_name,
            "type": str(self.type.value),
            "description": self.description,
            "mandatory": self.mandatory,
        }
        if self.default_value is not None:
            data["defaultValue"] = self.default_value
        if self.optional_values is not None:
            data["optionalValues"] = self.optional_values
        return data


class ParamType(str, Enum):
    """Parameter types for Chronicle SOAR integration functions."""

    UNSPECIFIED = "PARAM_TYPE_UNSPECIFIED"
    BOOLEAN = "BOOLEAN"
    INT = "INT"
    STRING = "STRING"
    PASSWORD = "PASSWORD"
    IP = "IP"
    IP_OR_HOST = "IP_OR_HOST"
    URL = "URL"
    DOMAIN = "DOMAIN"
    EMAIL = "EMAIL"
    VALUES_LIST = "VALUES_LIST"
    VALUES_AS_SEMICOLON_SEPARATED_STRING = (
        "VALUES_AS_SEMICOLON_SEPARATED_STRING"
    )
    MULTI_VALUES_SELECTION = "MULTI_VALUES_SELECTION"
    SCRIPT = "SCRIPT"
    FILTER_LIST = "FILTER_LIST"
    NUMERICAL_VALUES = "NUMERICAL_VALUES"


class ConnectorParamMode(str, Enum):
    """Parameter modes for Chronicle SOAR integration connectors."""

    UNSPECIFIED = "PARAM_MODE_UNSPECIFIED"
    REGULAR = "REGULAR"
    CONNECTIVITY = "CONNECTIVITY"
    SCRIPT = "SCRIPT"


class ConnectorRuleType(str, Enum):
    """Rule types for Chronicle SOAR integration connectors."""

    UNSPECIFIED = "RULE_TYPE_UNSPECIFIED"
    ALLOW_LIST = "ALLOW_LIST"
    BLOCK_LIST = "BLOCK_LIST"


@dataclass
class ConnectorParameter:
    """A parameter definition for a Chronicle SOAR integration connector.

    Attributes:
        display_name: The parameter's display name.
        type: The parameter's type.
        mode: The parameter's mode.
        mandatory: Whether the parameter is mandatory for configuring a
            connector instance.
        default_value: The default value of the parameter. Required for
            boolean and mandatory parameters.
        description: The parameter's description.
        advanced: The parameter's advanced flag.
    """

    display_name: str
    type: ParamType
    mode: ConnectorParamMode
    mandatory: bool
    default_value: str | None = None
    description: str | None = None
    advanced: bool | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "displayName": self.display_name,
            "type": str(self.type.value),
            "mode": str(self.mode.value),
            "mandatory": self.mandatory,
        }
        if self.default_value is not None:
            data["defaultValue"] = self.default_value
        if self.description is not None:
            data["description"] = self.description
        if self.advanced is not None:
            data["advanced"] = self.advanced
        return data


@dataclass
class IntegrationJobInstanceParameter:
    """A parameter instance for a Chronicle SOAR integration job instance.

    Note: Most fields are output-only and will be populated by the API.
    Only value needs to be provided when configuring a job instance.

    Attributes:
        value: The value of the parameter.
    """

    value: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {}
        if self.value is not None:
            data["value"] = self.value
        return data


class ScheduleType(str, Enum):
    """Schedule types for Chronicle SOAR integration job
    instance advanced config."""

    UNSPECIFIED = "SCHEDULE_TYPE_UNSPECIFIED"
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class DayOfWeek(str, Enum):
    """Days of the week for Chronicle SOAR weekly schedule details."""

    UNSPECIFIED = "DAY_OF_WEEK_UNSPECIFIED"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


@dataclass
class Date:
    """A calendar date for Chronicle SOAR schedule details.

    Attributes:
        year: The year.
        month: The month of the year (1-12).
        day: The day of the month (1-31).
    """

    year: int
    month: int
    day: int

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {"year": self.year, "month": self.month, "day": self.day}


@dataclass
class TimeOfDay:
    """A time of day for Chronicle SOAR schedule details.

    Attributes:
        hours: The hour of the day (0-23).
        minutes: The minute of the hour (0-59).
        seconds: The second of the minute (0-59).
        nanos: The nanoseconds of the second (0-999999999).
    """

    hours: int
    minutes: int
    seconds: int = 0
    nanos: int = 0

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {
            "hours": self.hours,
            "minutes": self.minutes,
            "seconds": self.seconds,
            "nanos": self.nanos,
        }


@dataclass
class OneTimeScheduleDetails:
    """One-time schedule details for a Chronicle SOAR job instance.

    Attributes:
        start_date: The date to run the job.
        time: The time to run the job.
    """

    start_date: Date
    time: TimeOfDay

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {
            "startDate": self.start_date.to_dict(),
            "time": self.time.to_dict(),
        }


@dataclass
class DailyScheduleDetails:
    """Daily schedule details for a Chronicle SOAR job instance.

    Attributes:
        start_date: The start date.
        time: The time to run the job.
        interval: The day interval.
    """

    start_date: Date
    time: TimeOfDay
    interval: int

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {
            "startDate": self.start_date.to_dict(),
            "time": self.time.to_dict(),
            "interval": self.interval,
        }


@dataclass
class WeeklyScheduleDetails:
    """Weekly schedule details for a Chronicle SOAR job instance.

    Attributes:
        start_date: The start date.
        days: The days of the week to run the job.
        time: The time to run the job.
        interval: The week interval.
    """

    start_date: Date
    days: list[DayOfWeek]
    time: TimeOfDay
    interval: int

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {
            "startDate": self.start_date.to_dict(),
            "days": [d.value for d in self.days],
            "time": self.time.to_dict(),
            "interval": self.interval,
        }


@dataclass
class MonthlyScheduleDetails:
    """Monthly schedule details for a Chronicle SOAR job instance.

    Attributes:
        start_date: The start date.
        day: The day of the month to run the job.
        time: The time to run the job.
        interval: The month interval.
    """

    start_date: Date
    day: int
    time: TimeOfDay
    interval: int

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {
            "startDate": self.start_date.to_dict(),
            "day": self.day,
            "time": self.time.to_dict(),
            "interval": self.interval,
        }


@dataclass
class AdvancedConfig:
    """Advanced scheduling configuration for a Chronicle SOAR job instance.

    Exactly one of the schedule detail fields should be provided, corresponding
    to the schedule_type.

    Attributes:
        time_zone: The zone id.
        schedule_type: The schedule type.
        one_time_schedule: One-time schedule details. Use with ONCE.
        daily_schedule: Daily schedule details. Use with DAILY.
        weekly_schedule: Weekly schedule details. Use with WEEKLY.
        monthly_schedule: Monthly schedule details. Use with MONTHLY.
    """

    time_zone: str
    schedule_type: ScheduleType
    one_time_schedule: OneTimeScheduleDetails | None = None
    daily_schedule: DailyScheduleDetails | None = None
    weekly_schedule: WeeklyScheduleDetails | None = None
    monthly_schedule: MonthlyScheduleDetails | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "timeZone": self.time_zone,
            "scheduleType": str(self.schedule_type.value),
        }
        if self.one_time_schedule is not None:
            data["oneTimeSchedule"] = self.one_time_schedule.to_dict()
        if self.daily_schedule is not None:
            data["dailySchedule"] = self.daily_schedule.to_dict()
        if self.weekly_schedule is not None:
            data["weeklySchedule"] = self.weekly_schedule.to_dict()
        if self.monthly_schedule is not None:
            data["monthlySchedule"] = self.monthly_schedule.to_dict()
        return data


@dataclass
class JobParameter:
    """A parameter definition for a Chronicle SOAR integration job.

    Attributes:
        id: The parameter's id.
        display_name: The parameter's display name.
        description: The parameter's description.
        mandatory: Whether the parameter is mandatory.
        type: The parameter's type.
        default_value: The default value of the parameter.
    """

    id: int
    display_name: str
    description: str
    mandatory: bool
    type: ParamType
    default_value: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "id": self.id,
            "displayName": self.display_name,
            "description": self.description,
            "mandatory": self.mandatory,
            "type": str(self.type.value),
        }
        if self.default_value is not None:
            data["defaultValue"] = self.default_value
        return data


class IntegrationParameterType(str, Enum):
    """Parameter types for Chronicle SOAR integration instances."""

    UNSPECIFIED = "INTEGRATION_PARAMETER_TYPE_UNSPECIFIED"
    BOOLEAN = "BOOLEAN"
    INT = "INT"
    STRING = "STRING"
    PASSWORD = "PASSWORD"
    IP = "IP"
    IP_OR_HOST = "IP_OR_HOST"
    URL = "URL"
    DOMAIN = "DOMAIN"
    EMAIL = "EMAIL"
    VALUES_LIST = "VALUES_LIST"
    VALUES_AS_SEMICOLON_SEPARATED_STRING = (
        "VALUES_AS_SEMICOLON_SEPARATED_STRING"
    )
    MULTI_VALUES_SELECTION = "MULTI_VALUES_SELECTION"
    SCRIPT = "SCRIPT"
    FILTER_LIST = "FILTER_LIST"


@dataclass
class IntegrationInstanceParameter:
    """A parameter instance for a Chronicle SOAR integration instance.

    Note: Most fields are output-only and will be populated by the API.
    Only value needs to be provided when configuring an integration instance.

    Attributes:
        value: The parameter's value.
    """

    value: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {}
        if self.value is not None:
            data["value"] = self.value
        return data


class ConnectorConnectivityStatus(str, Enum):
    """Connectivity status for Chronicle SOAR connector instances."""

    LIVE = "LIVE"
    NOT_LIVE = "NOT_LIVE"


@dataclass
class ConnectorInstanceParameter:
    """A parameter instance for a Chronicle SOAR connector instance.

    Note: Most fields are output-only and will be populated by the API.
    Only value needs to be provided when configuring a connector instance.

    Attributes:
        value: The value of the parameter.
    """

    value: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {}
        if self.value is not None:
            data["value"] = self.value
        return data


class TransformerType(str, Enum):
    """Transformer types for Chronicle SOAR integration transformers."""

    UNSPECIFIED = "TRANSFORMER_TYPE_UNSPECIFIED"
    BUILT_IN = "BUILT_IN"
    CUSTOM = "CUSTOM"


@dataclass
class TransformerDefinitionParameter:
    """A parameter definition for a Chronicle SOAR transformer definition.

    Attributes:
        display_name: The parameter's display name. May contain letters,
            numbers, and underscores. Maximum 150 characters.
        mandatory: Whether the parameter is mandatory for configuring a
            transformer instance.
        id: The parameter's id. Server-generated on creation; must be
            provided when updating an existing parameter.
        default_value: The default value of the parameter. Required for
            boolean and mandatory parameters.
        description: The parameter's description. Maximum 2050 characters.
    """

    display_name: str
    mandatory: bool
    id: str | None = None
    default_value: str | None = None
    description: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "displayName": self.display_name,
            "mandatory": self.mandatory,
        }
        if self.id is not None:
            data["id"] = self.id
        if self.default_value is not None:
            data["defaultValue"] = self.default_value
        if self.description is not None:
            data["description"] = self.description
        return data


class LogicalOperatorType(str, Enum):
    """Logical operator types for Chronicle SOAR
    integration logical operators."""

    UNSPECIFIED = "LOGICAL_OPERATOR_TYPE_UNSPECIFIED"
    BUILT_IN = "BUILT_IN"
    CUSTOM = "CUSTOM"


@dataclass
class IntegrationLogicalOperatorParameter:
    """A parameter definition for a Chronicle SOAR logical operator.

    Attributes:
        display_name: The parameter's display name. May contain letters,
            numbers, and underscores. Maximum 150 characters.
        mandatory: Whether the parameter is mandatory for configuring a
            logical operator instance.
        id: The parameter's id. Server-generated on creation; must be
            provided when updating an existing parameter.
        default_value: The default value of the parameter. Required for
            boolean and mandatory parameters.
        order: The parameter's order in the parameters list.
        description: The parameter's description. Maximum 2050 characters.
    """

    display_name: str
    mandatory: bool
    id: str | None = None
    default_value: str | None = None
    order: int | None = None
    description: str | None = None

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        data: dict = {
            "displayName": self.display_name,
            "mandatory": self.mandatory,
        }
        if self.id is not None:
            data["id"] = self.id
        if self.default_value is not None:
            data["defaultValue"] = self.default_value
        if self.order is not None:
            data["order"] = self.order
        if self.description is not None:
            data["description"] = self.description
        return data


@dataclass
class ConnectorRule:
    """A rule definition for a Chronicle SOAR integration connector.

    Attributes:
        display_name: Connector's rule data name.
        type: Connector's rule data type.
    """

    display_name: str
    type: ConnectorRuleType

    def to_dict(self) -> dict:
        """Serialize to the dict shape expected by the Chronicle API."""
        return {
            "displayName": self.display_name,
            "type": str(self.type.value),
        }


class CasePriority(StrEnum):
    """Priority levels for cases."""

    UNSPECIFIED = "PRIORITY_UNSPECIFIED"
    INFO = "PRIORITY_INFO"
    LOW = "PRIORITY_LOW"
    MEDIUM = "PRIORITY_MEDIUM"
    HIGH = "PRIORITY_HIGH"
    CRITICAL = "PRIORITY_CRITICAL"


class CaseCloseReason(StrEnum):
    """Close reason values for cases."""

    UNSPECIFIED = "CLOSE_REASON_UNSPECIFIED"
    MALICIOUS = "MALICIOUS"
    NOT_MALICIOUS = "NOT_MALICIOUS"
    MAINTENANCE = "MAINTENANCE"
    INCONCLUSIVE = "INCONCLUSIVE"
    UNKNOWN = "UNKNOWN"


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
