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

from secops.chronicle.alert import get_alerts
from secops.chronicle.case import get_cases
from secops.chronicle.client import (
    ChronicleClient,
    ValueType,
    _detect_value_type,
)
from secops.chronicle.dashboard import (
    DashboardAccessType,
    DashboardView,
    add_chart,
    create_dashboard,
    delete_dashboard,
    duplicate_dashboard,
    get_chart,
    get_dashboard,
    list_dashboards,
    remove_chart,
    update_dashboard,
)
from secops.chronicle.dashboard_query import execute_query, get_execute_query
from secops.chronicle.data_export import (
    AvailableLogType,
    cancel_data_export,
    create_data_export,
    fetch_available_log_types,
    get_data_export,
)

# Import data table and reference list classes
from secops.chronicle.data_table import (
    DataTableColumnType,
    update_data_table,
    replace_data_table_rows,
)
from secops.chronicle.entity import summarize_entity
from secops.chronicle.gemini import (
    Block,
    GeminiResponse,
    NavigationAction,
    SuggestedAction,
)
from secops.chronicle.ioc import list_iocs
from secops.chronicle.log_ingest import (
    create_forwarder,
    extract_forwarder_id,
    get_forwarder,
    get_or_create_forwarder,
    ingest_log,
    list_forwarders,
)
from secops.chronicle.log_types import (
    LogType,
    get_all_log_types,
    get_log_type_description,
    is_valid_log_type,
    search_log_types,
)
from secops.chronicle.models import (
    AlertCount,
    Case,
    CaseList,
    DataExport,
    DataExportStage,
    DataExportStatus,
    Entity,
    EntityMetadata,
    EntityMetrics,
    EntitySummary,
    FileMetadataAndProperties,
    InputInterval,
    PrevalenceData,
    SoarPlatformInfo,
    TileType,
    TimeInterval,
    Timeline,
    TimelineBucket,
    WidgetMetadata,
)
from secops.chronicle.nl_search import translate_nl_to_udm
from secops.chronicle.reference_list import (
    ReferenceListSyntaxType,
    ReferenceListView,
)

# Rule functionality
from secops.chronicle.rule import (
    create_rule,
    delete_rule,
    enable_rule,
    get_rule,
    list_rules,
    search_rules,
    update_rule,
)
from secops.chronicle.rule_alert import (
    bulk_update_alerts,
    get_alert,
    search_rule_alerts,
    update_alert,
)
from secops.chronicle.rule_detection import list_detections, list_errors
from secops.chronicle.rule_exclusion import (
    UpdateRuleDeployment,
    compute_rule_exclusion_activity,
    create_rule_exclusion,
    get_rule_exclusion,
    get_rule_exclusion_deployment,
    list_rule_exclusions,
    patch_rule_exclusion,
    update_rule_exclusion_deployment,
)
from secops.chronicle.rule_retrohunt import create_retrohunt, get_retrohunt
from secops.chronicle.rule_set import batch_update_curated_rule_set_deployments
from secops.chronicle.rule_validation import ValidationResult
from secops.chronicle.search import search_udm
from secops.chronicle.stats import get_stats
from secops.chronicle.udm_mapping import (
    RowLogFormat,
    generate_udm_key_value_mappings,
)
from secops.chronicle.udm_search import (
    fetch_udm_search_csv,
    find_udm_field_values,
)
from secops.chronicle.validate import validate_query

__all__ = [
    # Client
    "_detect_value_type",
    "ChronicleClient",
    "ValueType",
    # UDM and Search
    "fetch_udm_search_csv",
    "find_udm_field_values",
    "validate_query",
    "get_stats",
    "search_udm",
    # Natural Language Search
    "translate_nl_to_udm",
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
    "search_rules",
    # Rule exclusion operations
    "create_rule_exclusion",
    "get_rule_exclusion",
    "list_rule_exclusions",
    "patch_rule_exclusion",
    "compute_rule_exclusion_activity",
    "get_rule_exclusion_deployment",
    "update_rule_exclusion_deployment",
    # UDM Mapping
    "generate_udm_key_value_mappings",
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
    # Native Dashboard
    "add_chart",
    "create_dashboard",
    "delete_dashboard",
    "duplicate_dashboard",
    "get_chart",
    "get_dashboard",
    "list_dashboards",
    "remove_chart",
    "update_dashboard",
    # Dashboard Queries
    "execute_query",
    "get_execute_query",
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
    "UpdateRuleDeployment",
    "RowLogFormat",
    "DashboardAccessType",
    "DashboardView",
    "InputInterval",
    "TileType",
    # Data Table and Reference List
    "DataTableColumnType",
    "ReferenceListSyntaxType",
    "ReferenceListView",
    "update_data_table",
    "replace_data_table_rows",
]
