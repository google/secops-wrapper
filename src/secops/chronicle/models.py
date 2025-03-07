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