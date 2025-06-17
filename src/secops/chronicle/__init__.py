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
"""Chronicle API specific functionality."""

from secops.chronicle.client import ChronicleClient, _detect_value_type, ValueType
from secops.chronicle.udm_search import fetch_udm_search_csv
from secops.chronicle.validate import validate_query
from secops.chronicle.stats import get_stats
from secops.chronicle.search import search_udm
from secops.chronicle.entity import summarize_entity
from secops.chronicle.ioc import list_iocs
from secops.chronicle.case import get_cases
from secops.chronicle.alert import get_alerts
from secops.chronicle.nl_search import translate_nl_to_udm, nl_search
from secops.chronicle.log_ingest import (
    ingest_log,
    create_forwarder,
    get_or_create_forwarder,
    list_forwarders,
    get_forwarder,
    extract_forwarder_id,
)
from secops.chronicle.log_types import (
    LogType,
    get_all_log_types,
    is_valid_log_type,
    get_log_type_description,
    search_log_types,
)
from secops.chronicle.data_export import (
    get_data_export,
    create_data_export,
    cancel_data_export,
    fetch_available_log_types,
    AvailableLogType,
)

# Rule functionality
from secops.chronicle.rule import (
    create_rule,
    get_rule,
    list_rules,
    update_rule,
    delete_rule,
    enable_rule,
    search_rules,
)
from secops.chronicle.rule_alert import (
    get_alert,
    update_alert,
    bulk_update_alerts,
    search_rule_alerts,
)
from secops.chronicle.rule_detection import list_detections, list_errors
from secops.chronicle.rule_retrohunt import create_retrohunt, get_retrohunt
from secops.chronicle.rule_set import batch_update_curated_rule_set_deployments

from secops.chronicle.models import (
    Entity,
    EntityMetadata,
    EntityMetrics,
    TimeInterval,
    TimelineBucket,
    Timeline,
    WidgetMetadata,
    EntitySummary,
    AlertCount,
    Case,
    SoarPlatformInfo,
    CaseList,
    DataExport,
    DataExportStatus,
    DataExportStage,
    PrevalenceData,
    FileMetadataAndProperties,
)

from secops.chronicle.rule_validation import ValidationResult
from secops.chronicle.gemini import (
    GeminiResponse,
    Block,
    SuggestedAction,
    NavigationAction,
)

# Import data table and reference list classes
from secops.chronicle.data_table import DataTableColumnType
from secops.chronicle.reference_list import ReferenceListSyntaxType, ReferenceListView

__all__ = [
    # Client
    "ChronicleClient",
    "ValueType",
    # UDM and Search
    "fetch_udm_search_csv",
    "validate_query",
    "get_stats",
    "search_udm",
    # Natural Language Search
    "translate_nl_to_udm",
    "nl_search",
    # Entity
    "summarize_entity",
    # IoC
    "list_iocs",
    # Case
    "get_cases",
    # Alert
    "get_alerts",
    # Log Ingestion
    "ingest_log",
    "create_forwarder",
    "get_or_create_forwarder",
    "list_forwarders",
    "get_forwarder",
    "extract_forwarder_id",
    # Log Types
    "LogType",
    "get_all_log_types",
    "is_valid_log_type",
    "get_log_type_description",
    "search_log_types",
    # Data Export
    "get_data_export",
    "create_data_export",
    "cancel_data_export",
    "fetch_available_log_types",
    "AvailableLogType",
    "DataExport",
    "DataExportStatus",
    "DataExportStage",
    # Rule management
    "create_rule",
    "get_rule",
    "list_rules",
    "update_rule",
    "delete_rule",
    "enable_rule",
    "search_rules"
    # Rule alert operations
    "get_alert",
    "update_alert",
    "bulk_update_alerts",
    "search_rule_alerts",
    # Rule detection operations
    "list_detections",
    "list_errors",
    # Rule retrohunt operations
    "create_retrohunt",
    "get_retrohunt",
    # Rule set operations
    "batch_update_curated_rule_set_deployments",
    # Models
    "Entity",
    "EntityMetadata",
    "EntityMetrics",
    "TimeInterval",
    "TimelineBucket",
    "Timeline",
    "WidgetMetadata",
    "EntitySummary",
    "AlertCount",
    "Case",
    "SoarPlatformInfo",
    "CaseList",
    "PrevalenceData",
    "FileMetadataAndProperties",
    "ValidationResult",
    "GeminiResponse",
    "Block",
    "SuggestedAction",
    "NavigationAction",
    # Data Table and Reference List
    "DataTableColumnType",
    "ReferenceListSyntaxType",
    "ReferenceListView",
]
