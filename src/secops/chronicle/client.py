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
"""Chronicle API client."""
import ipaddress
import re
from collections.abc import Iterator
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Union

from google.auth.transport import requests as google_auth_requests

from secops import auth as secops_auth
from secops.auth import RetryConfig
from secops.chronicle.alert import get_alerts as _get_alerts
from secops.chronicle.case import get_cases_from_list
from secops.chronicle.dashboard import DashboardAccessType, DashboardView
from secops.chronicle.dashboard import add_chart as _add_chart
from secops.chronicle.dashboard import create_dashboard as _create_dashboard
from secops.chronicle.dashboard import delete_dashboard as _delete_dashboard
from secops.chronicle.dashboard import (
    duplicate_dashboard as _duplicate_dashboard,
)
from secops.chronicle.dashboard import edit_chart as _edit_chart
from secops.chronicle.dashboard import export_dashboard as _export_dashboard
from secops.chronicle.dashboard import get_chart as _get_chart
from secops.chronicle.dashboard import get_dashboard as _get_dashboard
from secops.chronicle.dashboard import import_dashboard as _import_dashboard
from secops.chronicle.dashboard import list_dashboards as _list_dashboards
from secops.chronicle.dashboard import remove_chart as _remove_chart
from secops.chronicle.dashboard import update_dashboard as _update_dashboard
from secops.chronicle.dashboard_query import (
    execute_query as _execute_dashboard_query,
)
from secops.chronicle.dashboard_query import (
    get_execute_query as _get_execute_query,
)
from secops.chronicle.data_export import (
    cancel_data_export as _cancel_data_export,
)
from secops.chronicle.data_export import (
    create_data_export as _create_data_export,
)
from secops.chronicle.data_export import (
    fetch_available_log_types as _fetch_available_log_types,
)
from secops.chronicle.data_export import get_data_export as _get_data_export
from secops.chronicle.data_export import list_data_export as _list_data_export
from secops.chronicle.data_export import (
    update_data_export as _update_data_export,
)
from secops.chronicle.data_table import DataTableColumnType
from secops.chronicle.data_table import create_data_table as _create_data_table
from secops.chronicle.data_table import (
    create_data_table_rows as _create_data_table_rows,
)
from secops.chronicle.data_table import delete_data_table as _delete_data_table
from secops.chronicle.data_table import (
    delete_data_table_rows as _delete_data_table_rows,
)
from secops.chronicle.data_table import get_data_table as _get_data_table
from secops.chronicle.data_table import (
    list_data_table_rows as _list_data_table_rows,
)
from secops.chronicle.data_table import list_data_tables as _list_data_tables
from secops.chronicle.data_table import (
    replace_data_table_rows as _replace_data_table_rows,
)
from secops.chronicle.data_table import update_data_table as _update_data_table
from secops.chronicle.data_table import (
    update_data_table_rows as _update_data_table_rows,
)
from secops.chronicle.entity import _detect_value_type_for_query
from secops.chronicle.entity import summarize_entity as _summarize_entity
from secops.chronicle.feeds import CreateFeedModel, UpdateFeedModel
from secops.chronicle.feeds import create_feed as _create_feed
from secops.chronicle.feeds import delete_feed as _delete_feed
from secops.chronicle.feeds import disable_feed as _disable_feed
from secops.chronicle.feeds import enable_feed as _enable_feed
from secops.chronicle.feeds import generate_secret as _generate_secret
from secops.chronicle.feeds import get_feed as _get_feed
from secops.chronicle.feeds import list_feeds as _list_feeds
from secops.chronicle.feeds import update_feed as _update_feed
from secops.chronicle.gemini import GeminiResponse
from secops.chronicle.gemini import opt_in_to_gemini as _opt_in_to_gemini
from secops.chronicle.gemini import query_gemini as _query_gemini
from secops.chronicle.ioc import list_iocs as _list_iocs
from secops.chronicle.log_ingest import create_forwarder as _create_forwarder
from secops.chronicle.log_ingest import delete_forwarder as _delete_forwarder
from secops.chronicle.log_ingest import get_forwarder as _get_forwarder
from secops.chronicle.log_ingest import (
    get_or_create_forwarder as _get_or_create_forwarder,
)
from secops.chronicle.log_ingest import import_entities as _import_entities
from secops.chronicle.log_ingest import ingest_log as _ingest_log
from secops.chronicle.log_ingest import ingest_udm as _ingest_udm
from secops.chronicle.log_ingest import list_forwarders as _list_forwarders
from secops.chronicle.log_ingest import update_forwarder as _update_forwarder
from secops.chronicle.log_types import get_all_log_types as _get_all_log_types
from secops.chronicle.log_types import (
    get_log_type_description as _get_log_type_description,
)
from secops.chronicle.log_types import is_valid_log_type as _is_valid_log_type
from secops.chronicle.log_types import search_log_types as _search_log_types
from secops.chronicle.log_processing_pipelines import (
    associate_streams as _associate_streams,
)
from secops.chronicle.log_processing_pipelines import (
    create_log_processing_pipeline as _create_log_processing_pipeline,
)
from secops.chronicle.log_processing_pipelines import (
    delete_log_processing_pipeline as _delete_log_processing_pipeline,
)
from secops.chronicle.log_processing_pipelines import (
    dissociate_streams as _dissociate_streams,
)
from secops.chronicle.log_processing_pipelines import (
    fetch_associated_pipeline as _fetch_associated_pipeline,
)
from secops.chronicle.log_processing_pipelines import (
    fetch_sample_logs_by_streams as _fetch_sample_logs_by_streams,
)
from secops.chronicle.log_processing_pipelines import (
    get_log_processing_pipeline as _get_log_processing_pipeline,
)
from secops.chronicle.log_processing_pipelines import (
    list_log_processing_pipelines as _list_log_processing_pipelines,
)
from secops.chronicle.log_processing_pipelines import (
    update_log_processing_pipeline as _update_log_processing_pipeline,
)
from secops.chronicle.log_processing_pipelines import (
    test_pipeline as _test_pipeline,
)
from secops.chronicle.models import (
    APIVersion,
    CaseList,
    DashboardChart,
    DashboardQuery,
    EntitySummary,
    InputInterval,
    TileType,
)
from secops.chronicle.nl_search import nl_search as _nl_search
from secops.chronicle.nl_search import translate_nl_to_udm
from secops.chronicle.parser import activate_parser as _activate_parser
from secops.chronicle.parser import (
    activate_release_candidate_parser as _activate_release_candidate_parser,
)
from secops.chronicle.parser import copy_parser as _copy_parser
from secops.chronicle.parser import create_parser as _create_parser
from secops.chronicle.parser import deactivate_parser as _deactivate_parser
from secops.chronicle.parser import delete_parser as _delete_parser
from secops.chronicle.parser import get_parser as _get_parser
from secops.chronicle.parser import list_parsers as _list_parsers
from secops.chronicle.parser import run_parser as _run_parser
from secops.chronicle.parser_extension import ParserExtensionConfig
from secops.chronicle.parser_extension import (
    activate_parser_extension as _activate_parser_extension,
)
from secops.chronicle.parser_extension import (
    create_parser_extension as _create_parser_extension,
)
from secops.chronicle.parser_extension import (
    delete_parser_extension as _delete_parser_extension,
)
from secops.chronicle.parser_extension import (
    get_parser_extension as _get_parser_extension,
)
from secops.chronicle.parser_extension import (
    list_parser_extensions as _list_parser_extensions,
)
from secops.chronicle.reference_list import (
    ReferenceListSyntaxType,
    ReferenceListView,
)
from secops.chronicle.reference_list import (
    create_reference_list as _create_reference_list,
)
from secops.chronicle.reference_list import (
    get_reference_list as _get_reference_list,
)
from secops.chronicle.reference_list import (
    list_reference_lists as _list_reference_lists,
)
from secops.chronicle.reference_list import (
    update_reference_list as _update_reference_list,
)

# Import rule functions
from secops.chronicle.rule import create_rule as _create_rule
from secops.chronicle.rule import delete_rule as _delete_rule
from secops.chronicle.rule import enable_rule as _enable_rule
from secops.chronicle.rule import get_rule as _get_rule
from secops.chronicle.rule import get_rule_deployment as _get_rule_deployment
from secops.chronicle.rule import (
    list_rule_deployments as _list_rule_deployments,
)
from secops.chronicle.rule import list_rules as _list_rules
from secops.chronicle.rule import run_rule_test
from secops.chronicle.rule import search_rules as _search_rules
from secops.chronicle.rule import set_rule_alerting as _set_rule_alerting
from secops.chronicle.rule import update_rule as _update_rule
from secops.chronicle.rule import (
    update_rule_deployment as _update_rule_deployment,
)
from secops.chronicle.rule_alert import (
    bulk_update_alerts as _bulk_update_alerts,
)
from secops.chronicle.rule_alert import get_alert as _get_alert
from secops.chronicle.rule_alert import (
    search_rule_alerts as _search_rule_alerts,
)
from secops.chronicle.rule_alert import update_alert as _update_alert
from secops.chronicle.rule_detection import list_detections as _list_detections
from secops.chronicle.rule_detection import list_errors as _list_errors
from secops.chronicle.rule_exclusion import (
    RuleExclusionType,
    UpdateRuleDeployment,
)
from secops.chronicle.rule_exclusion import (
    compute_rule_exclusion_activity as _compute_rule_exclusion_activity,
)
from secops.chronicle.rule_exclusion import (
    create_rule_exclusion as _create_rule_exclusion,
)
from secops.chronicle.rule_exclusion import (
    get_rule_exclusion as _get_rule_exclusion,
)
from secops.chronicle.rule_exclusion import (
    get_rule_exclusion_deployment as _get_rule_exclusion_deployment,
)
from secops.chronicle.rule_exclusion import (
    list_rule_exclusions as _list_rule_exclusions,
)
from secops.chronicle.rule_exclusion import (
    patch_rule_exclusion as _patch_rule_exclusion,
)
from secops.chronicle.rule_exclusion import (
    update_rule_exclusion_deployment as _update_rule_exclusion_deployment,
)
from secops.chronicle.rule_retrohunt import (
    create_retrohunt as _create_retrohunt,
)
from secops.chronicle.rule_retrohunt import get_retrohunt as _get_retrohunt
from secops.chronicle.rule_set import (
    batch_update_curated_rule_set_deployments as _batch_update_curated_rule_set_deployments,  # pylint: disable=line-too-long
)
from secops.chronicle.rule_set import get_curated_rule as _get_curated_rule
from secops.chronicle.rule_set import (
    get_curated_rule_by_name as _get_curated_rule_by_name,
)
from secops.chronicle.rule_set import (
    get_curated_rule_set as _get_curated_rule_set,
)
from secops.chronicle.rule_set import (
    get_curated_rule_set_category as _get_curated_rule_set_category,
)
from secops.chronicle.rule_set import (
    get_curated_rule_set_deployment as _get_curated_rule_set_deployment,
)
from secops.chronicle.rule_set import (
    get_curated_rule_set_deployment_by_name as _get_curated_rule_set_deployment_by_name,  # pylint: disable=line-too-long
)
from secops.chronicle.rule_set import (
    list_curated_rule_set_categories as _list_curated_rule_set_categories,
)
from secops.chronicle.rule_set import (
    list_curated_rule_set_deployments as _list_curated_rule_set_deployments,
)
from secops.chronicle.rule_set import (
    list_curated_rule_sets as _list_curated_rule_sets,
)
from secops.chronicle.rule_set import list_curated_rules as _list_curated_rules
from secops.chronicle.rule_set import (
    search_curated_detections as _search_curated_detections,
)
from secops.chronicle.rule_set import (
    update_curated_rule_set_deployment as _update_curated_rule_set_deployment,
)
from secops.chronicle.featured_content_rules import (
    list_featured_content_rules as _list_featured_content_rules,
)
from secops.chronicle.rule_validation import validate_rule as _validate_rule
from secops.chronicle.search import search_udm as _search_udm
from secops.chronicle.stats import get_stats as _get_stats
from secops.chronicle.udm_mapping import RowLogFormat
from secops.chronicle.udm_mapping import (
    generate_udm_key_value_mappings as _generate_udm_key_value_mappings,
)

# Import functions from the new modules
from secops.chronicle.udm_search import (
    fetch_udm_search_csv as _fetch_udm_search_csv,
)
from secops.chronicle.udm_search import (
    fetch_udm_search_view as _fetch_udm_search_view,
)
from secops.chronicle.udm_search import (
    find_udm_field_values as _find_udm_field_values,
)
from secops.chronicle.validate import validate_query as _validate_query
from secops.chronicle.watchlist import (
    list_watchlists as _list_watchlists,
    get_watchlist as _get_watchlist,
    delete_watchlist as _delete_watchlist,
    create_watchlist as _create_watchlist,
    update_watchlist as _update_watchlist,
)
from secops.exceptions import SecOpsError


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


class BaseUrl(str):
    """Chronicle base url generation based on version and region.

    Supports production, dev, and staging regions with appropriate
    domain names.
    """

    def __new__(cls, version: APIVersion, region: str = "us"):
        domain = cls._get_domain(region)
        return super().__new__(cls, f"https://{domain}/{version}")

    def __init__(self, version: APIVersion, region: str = "us"):
        self._default = version
        self._region = region

    @staticmethod
    def _get_domain(region: str) -> str:
        """Get the appropriate domain for the given region.

        Args:
            region: Region identifier (e.g., 'us', 'europe', 'dev',
                'staging')

        Returns:
            str: Domain name for the region
        """
        if region == "dev":
            return "autopush-chronicle.sandbox.googleapis.com"
        elif region == "staging":
            return "staging-chronicle.sandbox.googleapis.com"
        else:
            return f"{region}-chronicle.googleapis.com"

    def __call__(
        self, version: APIVersion = None, allowed: list[APIVersion] = None
    ) -> str:
        """
        Returns the base URL for a specific API version.

        Args:
            version: (Optional) The API version to use. If not provided,
            uses the default.
            allowed: (Optional) A list of allowed API versions for the
            endpoint.

        Returns:
            The base URL string.

        Raises:
            SecOpsError: If the requested API version is not supported.
        """
        selected_version = APIVersion(version or self._default)
        if allowed and selected_version not in allowed:
            raise SecOpsError(
                f'API version "{selected_version}" is not supported for this '
                f'endpoint. Allowed versions: {", ".join(allowed)}'
            )
        domain = self._get_domain(self._region)
        return f"https://{domain}/{selected_version}"


def _detect_value_type(value: str) -> tuple[str | None, str | None]:
    """Detect value type from a string.

    Args:
        value: The value to detect type for

    Returns:
        Tuple of (field_path, value_type) where one or both may be None
    """
    # Try to detect IP address
    try:
        ipaddress.ip_address(value)
        return "principal.ip", None
    except ValueError:
        pass

    # Try to detect MD5 hash
    if re.match(r"^[a-fA-F0-9]{32}$", value):
        return "target.file.md5", None

    # Try to detect SHA-1 hash
    if re.match(r"^[a-fA-F0-9]{40}$", value):
        return "target.file.sha1", None

    # Try to detect SHA-256 hash
    if re.match(r"^[a-fA-F0-9]{64}$", value):
        return "target.file.sha256", None

    # Try to detect domain name
    if re.match(
        r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$", value
    ):
        return None, "DOMAIN_NAME"

    # Try to detect email address
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
        return None, "EMAIL"

    # Try to detect MAC address
    if re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", value):
        return None, "MAC"

    # Try to detect hostname (simple rule)
    if re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", value):
        return None, "HOSTNAME"

    # If no match found
    return None, None


class ChronicleClient:
    """Client for the Chronicle API."""

    def __init__(
        self,
        project_id: str,
        customer_id: str,
        region: str = "us",
        auth: Any | None = None,
        session: Any | None = None,
        extra_scopes: list[str] | None = None,
        credentials: Any | None = None,
        retry_config: RetryConfig | dict[str, Any] | bool | None = None,
        default_api_version: APIVersion | str = APIVersion.V1ALPHA,
    ):
        """Initialize ChronicleClient.

        Args:
            project_id: Google Cloud project ID
            customer_id: Chronicle customer ID
            region: Chronicle region, typically "us" or "eu"
            auth: Authentication object
            session: Custom session object
            extra_scopes: Additional OAuth scopes
            credentials: Credentials object
            retry_config: Request retry configurations.
                If set to false, retry will be disabled.
            default_api_version: Default API version to use for requests.
        """
        self.project_id = project_id
        self.customer_id = customer_id
        self.region = region
        self.default_api_version = APIVersion(default_api_version)
        self._default_forwarder_display_name: str = "Wrapper-SDK-Forwarder"
        self._cached_default_forwarder_id: str | None = None

        # Format the instance ID to match the expected format
        if region in ["dev", "staging"]:
            # Dev and staging use 'us' as the location
            self.instance_id = (
                f"projects/{project_id}/locations/us/instances/{customer_id}"
            )
        else:
            # Standard production regions use the normal format
            self.instance_id = (
                f"projects/{project_id}/locations/{region}/"
                f"instances/{customer_id}"
            )

        # Set up base URLs using BaseUrl for all regions
        self.base_url = BaseUrl(self.default_api_version, self.region)

        # Create a session with authentication
        if session:
            self._session = session
        else:
            if auth is None:
                auth = secops_auth.SecOpsAuth(
                    scopes=[
                        "https://www.googleapis.com/auth/cloud-platform",
                        "https://www.googleapis.com/auth/chronicle-backstory",
                    ]
                    + (extra_scopes or []),
                    credentials=credentials,
                    retry_config=retry_config,
                )

            self._session = auth.session

        # Ensure custom user agent is set
        if hasattr(self._session, "headers"):
            self._session.headers["User-Agent"] = "secops-wrapper-sdk"

    @property
    def session(self) -> google_auth_requests.AuthorizedSession:
        """Get an authenticated session.

        Returns:
            Authorized session for API requests
        """
        return self._session

    def fetch_udm_search_csv(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        fields: list[str],
        case_insensitive: bool = True,
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
        return _fetch_udm_search_csv(
            self, query, start_time, end_time, fields, case_insensitive
        )

    def fetch_udm_search_view(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        snapshot_query: str | None = 'feedback_summary.status != "CLOSED"',
        max_events: int | None = 10000,
        max_detections: int | None = 1000,
        case_insensitive: bool = True,
    ) -> str:
        """Fetch UDM Search View results.

        Args:
            client: The ChronicleClient instance.
            query: Chronicle search query to search for. The baseline
                query is used for this request and its results are cached for
                subsequent requests, so supplying additional filters in the
                snapshot_query will not require re-running the baseline query.
            start_time: Search start time.
            end_time: Search end time.
            snapshot_query: Query for filtering alerts. Uses a syntax similar
                to UDM search, with supported fields including:
                detection.rule_set, detection.rule_id, detection.rule_name,
                case_name, feedback_summary.status,
                feedback_summary.priority, etc.
            max_events: Maximum number of events to return. If not specified, a
            default of 10000 events will be returned.
            max_detections: Maximum number of detections to return. If not
                specified, a default of 1000 detections will be returned.
            case_insensitive: Whether to perform case-insensitive search or not.

        Returns:
            List of udm search results.
        """
        return _fetch_udm_search_view(
            self,
            query,
            start_time,
            end_time,
            snapshot_query,
            max_events,
            max_detections,
            case_insensitive,
        )

    def validate_query(self, query: str) -> dict[str, Any]:
        """Validate a Chronicle search query.

        Args:
            query: Chronicle search query to validate

        Returns:
            Dictionary with validation results

        Raises:
            APIError: If the API request fails
        """
        return _validate_query(self, query)

    def list_watchlists(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of all watchlists.

        Args:
            page_size: Maximum number of watchlists to return per page
            page_token: Token for the next page of results, if available

        Returns:
            Dictionary with list of watchlists

        Raises:
            APIError: If the API request fails
        """
        return _list_watchlists(self, page_size, page_token)

    def get_watchlist(
        self,
        watchlist_id: str,
    ) -> dict[str, Any]:
        """Get a specific watchlist by ID.

        Args:
            watchlist_id: ID of the watchlist to retrieve

        Returns:
            Watchlist

        Raises:
            APIError: If the API request fails
        """
        return _get_watchlist(self, watchlist_id)

    def delete_watchlist(
        self,
        watchlist_id: str,
        force: bool | None = None,
    ) -> dict[str, Any]:
        """Delete a watchlist by ID.

        Args:
            watchlist_id: ID of the watchlist to delete
            force: Optional. If set to true, any entities under this
             watchlist will also be deleted.
              (Otherwise, the request will only work if the
               watchlist has no entities.)

        Returns:
            Deleted watchlist

        Raises:
            APIError: If the API request fails
        """
        return _delete_watchlist(self, watchlist_id, force)

    def create_watchlist(
        self,
        name: str,
        display_name: str,
        multiplying_factor: float,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a watchlist

        Args:
            name: Name of the watchlist
            display_name: Display name of the watchlist
            multiplying_factor: Multiplying factor for the watchlist
            description: Optional. Description of the watchlist

        Returns:
            Created watchlist

        Raises:
            APIError: If the API request fails
        """
        return _create_watchlist(
            self, name, display_name, multiplying_factor, description
        )

    def update_watchlist(
        self,
        watchlist_id: str,
        display_name: str | None = None,
        description: str | None = None,
        multiplying_factor: float | None = None,
        entity_population_mechanism: dict[str, Any] | None = None,
        watchlist_user_preferences: dict[str, Any] | None = None,
        update_mask: str | None = None,
    ) -> dict[str, Any]:
        """Update a watchlist.

        Args:
            watchlist_id: ID of the watchlist to update.
            display_name: Optional. Display name of the watchlist.
                Must be 1-63 characters.
            description: Optional. Description of the watchlist.
            multiplying_factor: Optional. Weight applied to risk score
                for entities in this watchlist. Default is 1.0.
            entity_population_mechanism: Optional. Mechanism to populate
                entities in the watchlist. Example: {"manual": {}}.
            watchlist_user_preferences: Optional. User preferences for
                watchlist configuration. Example: {"pinned": True}.
            update_mask: Optional. Comma-separated list of fields to
                update. If not provided, all non-None fields are updated.

        Returns:
            Updated watchlist.

        Raises:
            APIError: If the API request fails.
        """
        return _update_watchlist(
            self,
            watchlist_id,
            display_name,
            description,
            multiplying_factor,
            entity_population_mechanism,
            watchlist_user_preferences,
            update_mask,
        )

    def get_stats(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        max_values: int = 60,
        timeout: int = 120,
        max_events: int = 10000,
        case_insensitive: bool = True,
        max_attempts: int = 30,
    ) -> dict[str, Any]:
        """Get statistics from a Chronicle search query.

        Args:
            query: Chronicle search query in stats format
            start_time: Search start time
            end_time: Search end time
            max_values: Maximum number of values to return per field
            timeout: Timeout in seconds for API request (default: 120)
            max_events: Maximum number of events to process
            case_insensitive: Whether to perform case-insensitive search
            max_attempts: Maximum number of polling attempts (deprecated)

        Returns:
            Dictionary with search statistics containing:
            - columns: List of column names
            - rows: List of dictionaries with row data
            - total_rows: Total number of rows

        Raises:
            APIError: If the API request fails
        """
        return _get_stats(
            self,
            query,
            start_time,
            end_time,
            max_values,
            timeout,
            max_events,
            case_insensitive,
            max_attempts,
        )

    def _process_stats_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """Process stats search results.

        Args:
            results: Stats search results from API

        Returns:
            Processed statistics
        """
        processed_results = {"total_rows": 0, "columns": [], "rows": []}

        # Return early if no stats results
        if "stats" not in results or "results" not in results["stats"]:
            return processed_results

        # Extract columns
        columns = []
        column_data = {}

        for col_data in results["stats"]["results"]:
            col_name = col_data.get("column", "")
            columns.append(col_name)

            # Process values for this column
            values = []
            for val_data in col_data.get("values", []):
                if "value" in val_data:
                    val = val_data["value"]
                    if "int64Val" in val:
                        values.append(int(val["int64Val"]))
                    elif "doubleVal" in val:
                        values.append(float(val["doubleVal"]))
                    elif "stringVal" in val:
                        values.append(val["stringVal"])
                    else:
                        values.append(None)
                else:
                    values.append(None)

            column_data[col_name] = values

        # Build result rows
        rows = []
        if columns and all(col in column_data for col in columns):
            max_rows = max(len(column_data[col]) for col in columns)
            processed_results["total_rows"] = max_rows

            for i in range(max_rows):
                row = {}
                for col in columns:
                    col_values = column_data[col]
                    row[col] = col_values[i] if i < len(col_values) else None
                rows.append(row)

        processed_results["columns"] = columns
        processed_results["rows"] = rows

        return processed_results

    def search_udm(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        max_events: int = 10000,
        case_insensitive: bool = True,
        max_attempts: int = 30,
        timeout: int = 30,
        debug: bool = False,
    ) -> dict[str, Any]:
        """Search UDM events in Chronicle.

        Args:
            query: Chronicle search query
            start_time: Search start time
            end_time: Search end time
            max_events: Maximum events to return
            case_insensitive: Whether to perform case-insensitive search
            max_attempts: Maximum number of polling attempts (default: 30)
            timeout: Timeout in seconds for each API request (default: 30)
            debug: Print debug information during execution

        Returns:
            Dictionary with search results containing:
            - events: List of UDM events with 'name' and 'udm' fields
            - total_events: Number of events returned
            - more_data_available: Boolean indicating
                if more results are available

        Raises:
            APIError: If the API request fails
        """
        return _search_udm(
            self,
            query,
            start_time,
            end_time,
            max_events,
            case_insensitive,
            max_attempts,
            timeout,
            debug,
        )

    def find_udm_field_values(
        self, query: str, page_size: int | None = None
    ) -> dict[str, Any]:
        """Fetch UDM field values that match a query.

        Args:
            query: The partial UDM field value to match
            page_size: The maximum number of value matches to return

        Returns:
            Dictionary containing field values that match the query

           Raises:
            APIError: If the API request fails
        """
        return _find_udm_field_values(self, query=query, page_size=page_size)

    def summarize_entity(
        self,
        value: str,
        start_time: datetime,
        end_time: datetime,
        preferred_entity_type: str | None = None,
        include_all_udm_types: bool = True,
        page_size: int = 1000,
        page_token: str | None = None,
    ) -> EntitySummary:
        """
        Get comprehensive summary information about an entity
        (IP, domain, file hash, etc.).

        This function mimics the Chronicle UI behavior:
        1. It first calls `summarizeEntitiesFromQuery` using a query
            derived from the value.
        2. It identifies a 'primary' entity from the results
            (preferring ASSET for IPs/MACs/Hostnames, FILE for hashes,
            DOMAIN_NAME for domains, USER for emails).
        3. If a primary entity is found, it makes subsequent calls to
            `summarizeEntity` using the primary entity's ID to fetch details
            like alerts, timeline, and prevalence.
        4. It combines all information into a single EntitySummary object.

        Args:
            value: The entity value to search for
                (e.g., "8.8.8.8", "google.com", hash).
            start_time: Start time for the summary data range.
            end_time: End time for the summary data range.
            preferred_entity_type: Optionally hint the preferred type
                                   ("ASSET", "FILE", "DOMAIN_NAME", "USER").
                                   If None, the function attempts to autodetect.
            include_all_udm_types: Whether to include all UDM event types for
                first/last seen times.
            page_size: Maximum number of results per page
                (primarily for alerts).
            page_token: Token for pagination (primarily for alerts).

        Returns:
            An EntitySummary object containing the combined results.

        Raises:
            APIError: If any API request fails or returns unexpected data.
            ValueError: If the input value cannot be mapped to a query.
        """
        return _summarize_entity(
            client=self,
            value=value,
            start_time=start_time,
            end_time=end_time,
            preferred_entity_type=preferred_entity_type,
            include_all_udm_types=include_all_udm_types,
            page_size=page_size,
            page_token=page_token,
        )

    def list_iocs(
        self,
        start_time: datetime,
        end_time: datetime,
        max_matches: int = 1000,
        add_mandiant_attributes: bool = True,
        prioritized_only: bool = False,
    ) -> dict:
        """List IoCs from Chronicle.

        Args:
            start_time: Start time for IoC search
            end_time: End time for IoC search
            max_matches: Maximum number of matches to return
            add_mandiant_attributes: Whether to add Mandiant attributes
            prioritized_only: Whether to only include prioritized IoCs

        Returns:
            Dictionary with IoC matches

        Raises:
            APIError: If the API request fails
        """
        return _list_iocs(
            self,
            start_time,
            end_time,
            max_matches,
            add_mandiant_attributes,
            prioritized_only,
        )

    def get_cases(self, case_ids: list[str]) -> CaseList:
        """Get case information for the specified case IDs.

        Uses the legacy:legacyBatchGetCases endpoint to retrieve multiple cases
        in a single API request.

        Args:
            case_ids: List of case IDs to retrieve (maximum 1000)

        Returns:
            A CaseList object containing the requested cases

        Raises:
            APIError: If the API request fails
            ValueError: If more than 1000 case IDs are provided
        """
        return get_cases_from_list(self, case_ids)

    def get_alerts(
        self,
        start_time: datetime,
        end_time: datetime,
        snapshot_query: str = 'feedback_summary.status != "CLOSED"',
        baseline_query: str | None = None,
        max_alerts: int = 1000,
        enable_cache: bool = True,
        max_attempts: int = 30,
        poll_interval: float = 1.0,
    ) -> dict:
        """Get alerts from Chronicle.

        Args:
            start_time: Start time for alert search
            end_time: End time for alert search
            snapshot_query: Query to filter alerts
            baseline_query: Baseline query to compare against
            max_alerts: Maximum number of alerts to return
            enable_cache: Whether to use cached results
            max_attempts: Maximum number of attempts to poll for results
            poll_interval: Interval between polling attempts in seconds

        Returns:
            Dictionary with alert data

        Raises:
            APIError: If the API request fails or times out
        """
        return _get_alerts(
            self,
            start_time,
            end_time,
            snapshot_query,
            baseline_query,
            max_alerts,
            enable_cache,
            max_attempts,
            poll_interval,
        )

    def _process_alerts_response(self, response) -> list:
        """Process alerts response.

        Args:
            response: Response data from API

        Returns:
            Processed response
        """
        # Simply return the response as it should already be processed
        return response

    def _merge_alert_updates(self, target: dict, updates: list) -> None:
        """Merge alert updates into the target dictionary.

        Args:
            target: Target dictionary to update
            updates: List of updates to apply
        """
        if "alerts" not in target or "alerts" not in target["alerts"]:
            return

        alerts = target["alerts"]["alerts"]

        # Create a map of alerts by ID for faster lookups
        alert_map = {alert["id"]: alert for alert in alerts}

        # Apply updates
        for update in updates:
            if "id" in update and update["id"] in alert_map:
                target_alert = alert_map[update["id"]]

                # Update each field
                for field, value in update.items():
                    if field != "id":
                        if (
                            isinstance(value, dict)
                            and field in target_alert
                            and isinstance(target_alert[field], dict)
                        ):
                            # Merge nested dictionaries
                            target_alert[field].update(value)
                        else:
                            # Replace value
                            target_alert[field] = value

    def _fix_json_formatting(self, json_str: str) -> str:
        """Fix common JSON formatting issues.

        Args:
            json_str: JSON string to fix

        Returns:
            Fixed JSON string
        """
        # Fix trailing commas in objects
        json_str = re.sub(r",\s*}", "}", json_str)
        # Fix trailing commas in arrays
        json_str = re.sub(r",\s*]", "]", json_str)

        return json_str

    def create_parser_extension(
        self,
        log_type: str,
        log: str | None = None,
        parser_config: str | None = None,
        field_extractors: str | dict[str, Any] | None = None,
        dynamic_parsing: str | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new parser extension.

        Args:
            log_type: The log type for which to create the parser extension
            log: Optional sample log string
                (will be base64 encoded if provided in string)
            parser_config: Parser configuration(CBN code snippet)
                (mutually exclusive with field_extractors and dynamic_parsing)
                (will be base64 encoded if provided in string)
            field_extractors: Optional field extractors configuration
                (mutually exclusive with cbn_snippet and dynamic_parsing)
                Example: {
                    "extractors": [
                        {
                            "precondition_path": "path_value",
                            "precondition_value": "precondition",
                            "precondition_op": "EQUALS", // or NOT_EQUALS
                            "field_path": "field_path_value",
                            "destination_path": "destination_path_value",
                            "value": "value_to_map",
                        }
                    ]
                }
            dynamic_parsing: Optional dynamic parsing configuration
                (mutually exclusive with cbn_snippet and field_extractors)
                Example: {
                    "opted_fields": [
                        {
                            "path": "path_value_1",
                            "sample_value": "sample_value_1"
                        },
                        {
                            "path": "path_value_2",
                            "sample_value": "sample_value_2"
                        }
                    ]
                }

        Returns:
            Dict containing the created parser extension details

        Raises:
            APIError: If the API request fails
            ValueError: If configuration is invalid
                (must provide exactly one of cbn_snippet, field_extractors,
                or dynamic_parsing)
        """
        config = ParserExtensionConfig(
            log=log,
            parser_config=parser_config,
            field_extractors=field_extractors,
            dynamic_parsing=dynamic_parsing,
        )

        return _create_parser_extension(self, log_type, config)

    def get_parser_extension(
        self, log_type: str, extension_id: str
    ) -> dict[str, Any]:
        """Get details of a parser extension.

        Args:
            log_type: The log type of the parser extension
            extension_id: The ID of the parser extension

        Returns:
            Dict containing the parser extension details
        """
        return _get_parser_extension(self, log_type, extension_id)

    def list_parser_extensions(
        self,
        log_type: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List parser extensions.

        Args:
            log_type: The log type to list parser extensions for
            page_size: Maximum number of parser extensions to return
            page_token: Token for pagination

        Returns:
            Dict containing list of parser extensions and next page token if any
        """
        return _list_parser_extensions(self, log_type, page_size, page_token)

    def activate_parser_extension(
        self, log_type: str, extension_id: str
    ) -> None:
        """Activate a parser extension.

        Args:
            log_type: The log type of the parser extension
            extension_id: The ID of the parser extension to activate

        Returns:
            None
        """
        _activate_parser_extension(self, log_type, extension_id)

    def delete_parser_extension(self, log_type: str, extension_id: str) -> None:
        """Delete a parser extension.

        Args:
            log_type: The log type of the parser extension
            extension_id: The ID of the parser extension to delete

        Returns:
            None
        """
        _delete_parser_extension(self, log_type, extension_id)

    # pylint: disable=function-redefined
    def _detect_value_type(self, value: str) -> tuple[str | None, str | None]:
        """
        Instance method version of _detect_value_type for
        backward compatibility.

        Args:
            value: The value to detect type for

        Returns:
            Tuple of (field_path, value_type) where one or both may be None
        """
        return _detect_value_type(value)

    def _detect_value_type(self, value, value_type=None):
        """Detect value type for entity values.

        This is a legacy method maintained for backward compatibility.
        It calls the standalone detect_value_type function.

        Args:
            value: Value to detect type for
            value_type: Optional explicit value type

        Returns:
            Tuple of (field_path, value_type)
        """
        _ = (value_type,)
        return _detect_value_type_for_query(value)

    # pylint: enable=function-redefined

    # Rule Management methods

    def create_rule(
        self,
        rule_text: str,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Creates a new detection rule to find matches in logs.

        Args:
            rule_text: Content of the new detection rule, used to evaluate logs.
            api_version: Preferred API version to use. Defaults to V1

        Returns:
            Dictionary containing the created rule information

        Raises:
            APIError: If the API request fails
        """
        return _create_rule(self, rule_text, api_version)

    def get_rule(
        self,
        rule_id: str,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Get a rule by ID.

        Args:
            rule_id: Unique ID of the detection rule to retrieve ("ru_<UUID>" or
              "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version suffix isn't
              specified we use the rule's latest version.
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing rule information

        Raises:
            APIError: If the API request fails
        """
        return _get_rule(self, rule_id, api_version)

    def list_feeds(
        self,
        page_size: int = 100,
        page_token: str = None,
        api_version: APIVersion | None = None,
    ) -> list[dict[str, Any]]:
        """List feeds.

        Args:
            page_size: The maximum number of feeds to return
            page_token: A page token, received from a previous ListFeeds call
            api_version: (Optional) Preferred API version to use.

        Returns:
            List of feed dictionaries

        Raises:
            APIError: If the API request fails
        """
        return _list_feeds(self, page_size, page_token, api_version)

    def get_feed(
        self, feed_id: str, api_version: APIVersion | None = None
    ) -> dict[str, Any]:
        """Get a feed by ID.

        Args:
            feed_id: Feed ID
            api_version: (Optional) Preferred API version to use.

        Returns:
            Feed dictionary

        Raises:
            APIError: If the API request fails
        """
        return _get_feed(self, feed_id, api_version)

    def create_feed(
        self,
        display_name: str,
        details: str | dict[str, Any],
        api_version: APIVersion | None = None,
    ) -> dict[str, Any]:
        """Create a new feed.

        Args:
            display_name: Display name for the feed
            details: Feed details as JSON string or dict
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the created feed

        Raises:
            APIError: If the API request fails
        """
        feed_config = CreateFeedModel(
            display_name=display_name, details=details
        )
        return _create_feed(self, feed_config, api_version)

    def update_feed(
        self,
        feed_id: str,
        display_name: str | None = None,
        details: dict[str, Any] | None = None,
        api_version: APIVersion | None = None,
    ) -> dict[str, Any]:
        """Update a feed.

        Args:
            feed_id: Feed ID
            display_name: Display name for the feed
            details: Feed details as dict
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the updated feed

        Raises:
            APIError: If the API request fails
        """
        feed_config = UpdateFeedModel(
            display_name=display_name, details=details
        )
        return _update_feed(self, feed_id, feed_config, api_version)

    def enable_feed(
        self, feed_id: str, api_version: APIVersion | None = None
    ) -> dict[str, Any]:
        """Enable a feed.

        Args:
            feed_id: Feed ID
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the enabled feed

        Raises:
            APIError: If the API request fails
        """
        return _enable_feed(self, feed_id, api_version)

    def disable_feed(
        self, feed_id: str, api_version: APIVersion | None = None
    ) -> dict[str, Any]:
        """Disable a feed.

        Args:
            feed_id: Feed ID
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the disabled feed

        Raises:
            APIError: If the API request fails
        """
        return _disable_feed(self, feed_id, api_version)

    def generate_secret(
        self, feed_id: str, api_version: APIVersion | None = None
    ) -> dict[str, Any]:
        """Generate a secret for a feed.

        Args:
            feed_id: Feed ID
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the secret

        Raises:
            APIError: If the API request fails
        """
        return _generate_secret(self, feed_id, api_version)

    def delete_feed(
        self, feed_id: str, api_version: APIVersion | None = None
    ) -> None:
        """Delete a feed.

        Args:
            feed_id: Feed ID
            api_version: (Optional) Preferred API version to use.

        Returns:
            None

        Raises:
            APIError: If the API request fails
        """
        return _delete_feed(self, feed_id, api_version)

    # Log Processing Pipeline methods

    def list_log_processing_pipelines(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        filter_expr: str | None = None,
    ) -> dict[str, Any]:
        """Lists log processing pipelines.

        Args:
            page_size: Maximum number of pipelines to return.
            page_token: Page token for pagination.
            filter_expr: Filter expression to restrict results.

        Returns:
            Dictionary containing pipelines and pagination info.

        Raises:
            APIError: If the API request fails.
        """
        return _list_log_processing_pipelines(
            self, page_size, page_token, filter_expr
        )

    def get_log_processing_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        """Gets a log processing pipeline by ID.

        Args:
            pipeline_id: ID of the pipeline to retrieve.

        Returns:
            Dictionary containing pipeline information.

        Raises:
            APIError: If the API request fails.
        """
        return _get_log_processing_pipeline(self, pipeline_id)

    def create_log_processing_pipeline(
        self,
        pipeline: dict[str, Any],
        pipeline_id: str | None = None,
    ) -> dict[str, Any]:
        """Creates a new log processing pipeline.

        Args:
            pipeline: Pipeline configuration dict containing:
                - displayName: Display name for the pipeline
                - description: Optional description
                - processors: List of processor configurations
                - customMetadata: Optional custom metadata list
            pipeline_id: Optional ID for the pipeline.

        Returns:
            Dictionary containing the created pipeline.

        Raises:
            APIError: If the API request fails.
        """
        return _create_log_processing_pipeline(self, pipeline, pipeline_id)

    def update_log_processing_pipeline(
        self,
        pipeline_id: str,
        pipeline: dict[str, Any],
        update_mask: str | None = None,
    ) -> dict[str, Any]:
        """Updates a log processing pipeline.

        Args:
            pipeline_id: ID of the pipeline to update.
            pipeline: Pipeline configuration with fields to update containing:
                - displayName: Display name for the pipeline
                - description: Optional description
                - processors: List of processor configurations
                - customMetadata: Optional custom metadata list
            update_mask: Optional comma-separated list of fields.

        Returns:
            Dictionary containing the updated pipeline.

        Raises:
            APIError: If the API request fails.
        """
        return _update_log_processing_pipeline(
            self, pipeline_id, pipeline, update_mask
        )

    def delete_log_processing_pipeline(
        self, pipeline_id: str, etag: str | None = None
    ) -> dict[str, Any]:
        """Deletes a log processing pipeline.

        Args:
            pipeline_id: ID of the pipeline to delete.
            etag: Optional etag for optimistic concurrency control.

        Returns:
            Empty dictionary on success.

        Raises:
            APIError: If the API request fails.
        """
        return _delete_log_processing_pipeline(self, pipeline_id, etag)

    def associate_streams(
        self, pipeline_id: str, streams: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Associates streams with a pipeline.

        Args:
            pipeline_id: ID of the pipeline.
            streams: List of stream dicts.

        Returns:
            Empty dictionary on success.

        Raises:
            APIError: If the API request fails.
        """
        return _associate_streams(self, pipeline_id, streams)

    def dissociate_streams(
        self, pipeline_id: str, streams: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Dissociates streams from a pipeline.

        Args:
            pipeline_id: ID of the pipeline.
            streams: List of stream dicts.

        Returns:
            Empty dictionary on success.

        Raises:
            APIError: If the API request fails.
        """
        return _dissociate_streams(self, pipeline_id, streams)

    def fetch_associated_pipeline(
        self, stream: dict[str, Any]
    ) -> dict[str, Any]:
        """Fetches the pipeline associated with a stream.

        Args:
            stream: Stream dict (logType or feedId).

        Returns:
            Dictionary containing the associated pipeline.

        Raises:
            APIError: If the API request fails.
        """
        return _fetch_associated_pipeline(self, stream)

    def fetch_sample_logs_by_streams(
        self,
        streams: list[dict[str, Any]],
        sample_logs_count: int | None = None,
    ) -> dict[str, Any]:
        """Fetches sample logs for specified streams.

        Args:
            streams: List of stream dicts.
            sample_logs_count: Number of sample logs per stream.

        Returns:
            Dictionary containing sample logs.

        Raises:
            APIError: If the API request fails.
        """
        return _fetch_sample_logs_by_streams(self, streams, sample_logs_count)

    def test_pipeline(
        self,
        pipeline: dict[str, Any],
        input_logs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Tests a pipeline with input logs.

        Args:
            pipeline: Pipeline configuration to test.
            input_logs: List of log objects to process.

        Returns:
            Dictionary containing processed logs.

        Raises:
            APIError: If the API request fails.
        """
        return _test_pipeline(self, pipeline, input_logs)

    def list_rules(
        self,
        view: str | None = "FULL",
        page_size: int | None = None,
        page_token: str | None = None,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Gets a list of rules.

        Args:
            view: Scope of fields to populate for the rules being returned.
                allowed values are:
                - "BASIC"
                - "FULL"
                - "REVISION_METADATA_ONLY"
                - "RULE_VIEW_UNSPECIFIED"
                Defaults to "FULL".
            page_size: Maximum number of rules to return per page.
            page_token: Token for the next page of results, if available.
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing information about rules

        Raises:
            APIError: If the API request fails
        """
        return _list_rules(
            self,
            view=view,
            page_size=page_size,
            page_token=page_token,
            api_version=api_version,
        )

    def update_rule(
        self,
        rule_id: str,
        rule_text: str,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Updates a rule.

        Args:
            rule_id: Unique ID of the detection rule to update ("ru_<UUID>")
            rule_text: Updated content of the detection rule
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the updated rule information

        Raises:
            APIError: If the API request fails
        """
        return _update_rule(self, rule_id, rule_text, api_version)

    def delete_rule(
        self,
        rule_id: str,
        force: bool = False,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Deletes a rule.

        Args:
            rule_id: Unique ID of the detection rule to delete ("ru_<UUID>")
            force: If True, deletes the rule even if it has
            associated retrohunts
            api_version: (Optional) Preferred API version to use.

        Returns:
            Empty dictionary or deletion confirmation

        Raises:
            APIError: If the API request fails
        """
        return _delete_rule(self, rule_id, force, api_version)

    def enable_rule(self, rule_id: str, enabled: bool = True) -> dict[str, Any]:
        """Enables or disables a rule.

        Args:
            rule_id: Unique ID of the detection rule to enable/disable
                ("ru_<UUID>")
            enabled: Whether to enable (True) or disable (False) the rule

        Returns:
            Dictionary containing rule deployment information

        Raises:
            APIError: If the API request fails
        """
        return _enable_rule(self, rule_id, enabled)

    def search_rules(
        self, query: str, api_version: APIVersion | None = APIVersion.V1
    ) -> dict[str, Any]:
        """Search for rules.

        Args:
            query: Search query string that supports regex
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing search results

        Raises:
            APIError: If the API request fails
        """
        return _search_rules(self, query, api_version)

    def run_rule_test(
        self,
        rule_text: str,
        start_time: datetime,
        end_time: datetime,
        max_results: int = 100,
        timeout: int = 300,
    ) -> Iterator[dict[str, Any]]:
        """Tests a rule against historical data and returns matches.

        This function connects to the legacy:legacyRunTestRule streaming
        API endpoint and processes the response which contains progress updates
        and detection results.

        Args:
            rule_text: Content of the detection rule to test
            start_time: Start time for the test range
            end_time: End time for the test range
            max_results: Maximum number of results to return
                (default 100, max 10000)
            timeout: Request timeout in seconds (default 300)

        Yields:
            Dictionaries containing detection results, progress updates
            or error information, depending on the response type.

        Raises:
            APIError: If the API request fails
            SecOpsError: If the input parameters are invalid
            ValueError: If max_results is outside valid range
        """
        return run_rule_test(
            self, rule_text, start_time, end_time, max_results, timeout
        )

    # Rule Alert methods

    def get_alert(
        self, alert_id: str, include_detections: bool = False
    ) -> dict[str, Any]:
        """Gets an alert by ID.

        Args:
            alert_id: ID of the alert to retrieve
            include_detections: Whether to include detection details in
                the response

        Returns:
            Dictionary containing alert information

        Raises:
            APIError: If the API request fails
        """
        return _get_alert(self, alert_id, include_detections)

    def update_alert(
        self,
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
        return _update_alert(
            self,
            alert_id,
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

    def bulk_update_alerts(
        self,
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
        return _bulk_update_alerts(
            self,
            alert_ids,
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

    def search_rule_alerts(
        self,
        start_time: datetime,
        end_time: datetime,
        rule_status: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Search for alerts generated by rules.

        Args:
            start_time: Start time for the search (inclusive)
            end_time: End time for the search (exclusive)
            rule_status: Filter by rule status (deprecated - not currently
                supported by the API)
            page_size: Maximum number of alerts to return

        Returns:
            Dictionary containing alert search results

        Raises:
            APIError: If the API request fails
        """

        return _search_rule_alerts(
            self, start_time, end_time, rule_status, page_size
        )

    # Rule Detection methods

    def list_detections(
        self,
        rule_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        list_basis: None | (
            Literal["LIST_BASIS_UNSPECIFIED", "CREATED_TIME", "DETECTION_TIME"]
        ) = None,
        alert_state: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List detections for a rule.

        Args:
            rule_id: Unique ID of the rule to list detections for. Options are:
                - {rule_id} (latest version)
                - {rule_id}@v_<seconds>_<nanoseconds> (specific version)
                - {rule_id}@- (all versions)
            start_time: If provided, filter by start time.
            end_time: If provided, filter by end time.
            list_basis: If provided, sort detections by list basis. Valid values
              are:
                - "LIST_BASIS_UNSPECIFIED"
                - "CREATED_TIME"
                - "DETECTION_TIME"
            alert_state: If provided, filter by alert state. Valid values are:
                - "UNSPECIFIED"
                - "NOT_ALERTING"
                - "ALERTING"
            page_size: If provided, maximum number of detections to return
            page_token: If provided, continuation token for pagination

        Returns:
            Dictionary containing detection information

        Raises:
            APIError: If the API request fails
            ValueError: If an invalid alert_state is provided
        """
        return _list_detections(
            self,
            rule_id,
            start_time,
            end_time,
            list_basis,
            alert_state,
            page_size,
            page_token,
        )

    def list_errors(self, rule_id: str) -> dict[str, Any]:
        """List execution errors for a rule.

        Args:
            rule_id: Unique ID of the rule to list errors for. Options are:
                - {rule_id} (latest version)
                - {rule_id}@v_<seconds>_<nanoseconds> (specific version)
                - {rule_id}@- (all versions)

        Returns:
            Dictionary containing rule execution errors

        Raises:
            APIError: If the API request fails
        """
        return _list_errors(self, rule_id)

    # Rule Retrohunt methods

    def create_retrohunt(
        self,
        rule_id: str,
        start_time: datetime,
        end_time: datetime,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Creates a retrohunt for a rule.

        A retrohunt applies a rule to historical data within
        the specified time range.

        Args:
            rule_id: Unique ID of the rule to run retrohunt for ("ru_<UUID>")
            start_time: Start time for retrohunt analysis
            end_time: End time for retrohunt analysis
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing operation information for the retrohunt

        Raises:
            APIError: If the API request fails
        """
        return _create_retrohunt(
            self, rule_id, start_time, end_time, api_version
        )

    def get_retrohunt(
        self,
        rule_id: str,
        operation_id: str,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Get retrohunt status and results.

        Args:
            rule_id: Unique ID of the rule the retrohunt is for ("ru_<UUID>" or
              "ru_<UUID>@v_<seconds>_<nanoseconds>")
            operation_id: Operation ID of the retrohunt
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing retrohunt information

        Raises:
            APIError: If the API request fails
        """
        return _get_retrohunt(self, rule_id, operation_id, api_version)

    # Parser Management methods

    def activate_parser(
        self, log_type: str, id: str  # pylint: disable=redefined-builtin
    ) -> dict[str, Any]:
        """Activate a custom parser.

        Args:
            log_type: Log type of the parser
            id: Parser ID

        Returns:
            Empty JSON object

        Raises:
            APIError: If the API request fails
        """
        return _activate_parser(self, log_type=log_type, id=id)

    def activate_release_candidate_parser(
        self, log_type: str, id: str  # pylint: disable=redefined-builtin
    ) -> dict[str, Any]:
        """
        Activate the release candidate parser making it live for that customer.

        Args:
            log_type: Log type of the parser
            id: Parser ID

        Returns:
            Empty JSON object

        Raises:
            APIError: If the API request fails
        """
        return _activate_release_candidate_parser(
            self, log_type=log_type, id=id
        )

    def copy_parser(
        self, log_type: str, id: str  # pylint: disable=redefined-builtin
    ) -> dict[str, Any]:
        """Makes a copy of a prebuilt parser.

        Args:
            log_type: Log type of the parser
            id: Parser ID

        Returns:
            Dictionary containing the newly copied parser

        Raises:
            APIError: If the API request fails
        """
        return _copy_parser(client=self, log_type=log_type, id=id)

    def create_parser(
        self, log_type: str, parser_code: str, validated_on_empty_logs: bool
    ) -> dict[str, Any]:
        """Creates a new parser.

        Args:
            log_type: Log type of the parser
            parser_code: Content of the new parser, used to evaluate logs
            validated_on_empty_logs: Whether the parser is validated
                on empty logs

        Returns:
            Dictionary containing the created parser information

        Raises:
            APIError: If the API request fails
        """
        return _create_parser(
            self,
            log_type=log_type,
            parser_code=parser_code,
            validated_on_empty_logs=validated_on_empty_logs,
        )

    def deactivate_parser(
        self, log_type: str, id: str  # pylint: disable=redefined-builtin
    ) -> dict[str, Any]:
        """Deactivate a custom parser.

        Args:
            log_type: Log type of the parser
            id: Parser ID

        Returns:
            Empty JSON object

        Raises:
            APIError: If the API request fails
        """
        return _deactivate_parser(client=self, log_type=log_type, id=id)

    def delete_parser(
        self,
        log_type: str,
        id: str,  # pylint: disable=redefined-builtin
        force: bool = False,
    ) -> dict[str, Any]:
        """Delete a parser.

        Args:
            log_type: Log type of the parser
            id: Parser ID
            force: Flag to forcibly delete an ACTIVE parser

        Returns:
            Empty JSON object

        Raises:
            APIError: If the API request fails
        """
        return _delete_parser(
            client=self, log_type=log_type, id=id, force=force
        )

    def get_parser(
        self, log_type: str, id: str  # pylint: disable=redefined-builtin
    ) -> dict[str, Any]:
        """Get a parser by ID.

        Args:
            log_type: Log type of the parser
            id: Parser ID

        Returns:
            Dictionary containing the parser information

        Raises:
            APIError: If the API request fails
        """
        return _get_parser(self, log_type=log_type, id=id)

    def list_parsers(
        self,
        log_type: str = "-",
        page_size: int | None = None,
        page_token: str | None = None,
        filter: str = None,  # pylint: disable=redefined-builtin
    ) -> list[Any] | dict[str, Any]:
        """List parsers.

        Args:
            log_type: Log type to filter by
            page_size: The maximum number of parsers to return per page.
                If provided, returns raw API response with pagination info.
                If None (default), auto-paginates and returns all parsers.
            page_token: A page token, received from a previous ListParsers
                call.
            filter: Optional filter expression

        Returns:
            If page_size is None: List of all parsers
                (auto-paginated)
            If page_size is provided: List of parsers with next page token if
                available.

        Raises:
            APIError: If the API request fails
        """
        return _list_parsers(
            self,
            log_type=log_type,
            page_size=page_size,
            page_token=page_token,
            filter=filter,
        )

    def run_parser(
        self,
        log_type: str,
        parser_code: str,
        parser_extension_code: str,
        logs: list,
        statedump_allowed: bool = False,
    ):
        """Run parser against sample logs.

        Args:
            client: ChronicleClient instance
            log_type: Log type of the parser
            parser_code: Content of the new parser, used to evaluate logs.
            parser_extension_code: Content of the parser extension
            logs: list of logs to test parser against
            statedump_allowed: Statedump filter is enabled or not for a config

        Returns:
            Dictionary containing the parser result

        Raises:
            APIError: If the API request fails
        """
        return _run_parser(
            self,
            log_type=log_type,
            parser_code=parser_code,
            parser_extension_code=parser_extension_code,
            logs=logs,
            statedump_allowed=statedump_allowed,
        )

    # Rule Set methods

    def batch_update_curated_rule_set_deployments(
        self, deployments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Batch update curated rule set deployments.

        Args:
            deployments: List of deployment configurations where each
                item contains:
                - category_id: UUID of the category
                - rule_set_id: UUID of the rule set
                - precision: Precision level (e.g., "broad", "precise")
                - enabled: Whether the rule set should be enabled
                - alerting: Whether alerting should be enabled for the rule set

        Returns:
            Dictionary containing information about the modified deployments

        Raises:
            APIError: If the API request fails
            ValueError: If required fields are missing from the deployments
        """
        return _batch_update_curated_rule_set_deployments(self, deployments)

    def list_curated_rule_sets(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get a list of all curated rule sets.

        Args:
            page_size: Number of results to return per page
            page_token: Token for the page to retrieve

        Returns:
            Dictionary containing the list of curated rule sets

        Raises:
            APIError: If the API request fails
        """
        return _list_curated_rule_sets(self, page_size, page_token)

    def list_curated_rule_set_categories(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get a list of all curated rule set categories.

        Args:
            page_size: Number of results to return per page
            page_token: Token for the page to retrieve

        Returns:
            Dictionary containing the list of curated rule set categories

        Raises:
            APIError: If the API request fails
        """
        return _list_curated_rule_set_categories(self, page_size, page_token)

    def list_curated_rule_set_deployments(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        only_enabled: bool | None = False,
        only_alerting: bool | None = False,
    ) -> list[dict[str, Any]]:
        """Get a list of all curated rule set deployments.

        Args:
            page_size: Number of results to return per page
            page_token: Token for the page to retrieve
            only_enabled: Only return enabled rule set deployments
            only_alerting: Only return alerting rule set deployments

        Returns:
            Dictionary containing the list of curated rule set deployments

        Raises:
            APIError: If the API request fails
        """
        return _list_curated_rule_set_deployments(
            self, page_size, page_token, only_enabled, only_alerting
        )

    def get_curated_rule_set_deployment(
        self,
        rule_set_id: str,
        precision: str = "precise",
    ) -> dict[str, Any]:
        """Get a curated rule set deployment by ID

        Args:
            rule_set_id: Unique ID of the curated rule set
            precision: Precision level ("precise" or "broad")

        Returns:
            Dictionary containing the curated rule set deployment

        Raises:
            APIError: If the API request fails
        """
        return _get_curated_rule_set_deployment(self, rule_set_id, precision)

    def get_curated_rule_set_deployment_by_name(
        self,
        display_name: str,
        precision: str = "precise",
    ) -> dict[str, Any]:
        """Get a curated rule set deployment by human-readable display name
            NOTE: This is a linear scan of all curated rules,
            so it may be inefficient for large rule sets.

        Args:
            display_name: Display name of the curated rule set
            precision: Precision level ("precise" or "broad")

        Returns:
            Dictionary containing the curated rule set deployment

        Raises:
            APIError: If the API request fails
            SecOpsError: If the rule set is not found or precision is invalid
        """
        return _get_curated_rule_set_deployment_by_name(
            self, display_name, precision
        )

    def list_curated_rules(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get a list of all curated rules.

        Args:
            page_size: Number of results to return per page
            page_token: Token for the page to retrieve

        Returns:
            Dictionary containing the list of curated rules

        Raises:
            APIError: If the API request fails
        """
        return _list_curated_rules(self, page_size, page_token)

    def get_curated_rule(self, rule_id: str) -> dict[str, Any]:
        """Get a curated rule by ID.

        Args:
            rule_id: ID of the curated rule

        Returns:
            Dictionary containing the curated rule

        Raises:
            APIError: If the API request fails
        """
        return _get_curated_rule(self, rule_id)

    def get_curated_rule_by_name(self, display_name: str) -> dict[str, Any]:
        """Get a curated rule by human-readable display name
            NOTE: This is a linear scan of all curated rules,
            so it may be inefficient for large rule sets.

        Args:
            display_name: Display name of the curated rule

        Returns:
            Dictionary containing the curated rule

        Raises:
            APIError: If the API request fails
            SecOpsError: If the rule is not found
        """
        return _get_curated_rule_by_name(self, display_name)

    def update_curated_rule_set_deployment(
        self, deployment: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a curated rule set deployment to enable or disable
            alerting or change precision.

        Args:
            deployment: Dict of deployment configuration containing:
                - category_id: UUID of the category
                - rule_set_id: UUID of the rule set
                - precision: Precision level either "broad" or "precise"
                - enabled: Whether the rule set should be enabled
                - alerting: Whether alerting should be enabled for the rule set

        Returns:
            Dictionary containing the updated curated rule set deployment

        Raises:
            APIError: If the API request fails
            SecOpsError: If the rule set is not found or precision is invalid
        """
        return _update_curated_rule_set_deployment(self, deployment)

    def get_curated_rule_set_category(self, category_id: str) -> dict[str, Any]:
        """Get a curated rule set category by ID.

        Args:
            category_id: ID of the curated rule set category

        Returns:
            Dictionary containing the curated rule set category

        Raises:
            APIError: If the API request fails
        """
        return _get_curated_rule_set_category(self, category_id)

    def get_curated_rule_set(self, rule_set_id: str) -> dict[str, Any]:
        """Get a curated rule set by ID.

        Args:
            rule_set_id: ID of the curated rule set

        Returns:
            Dictionary containing the curated rule set

        Raises:
            APIError: If the API request fails
        """
        return _get_curated_rule_set(self, rule_set_id)

    def list_featured_content_rules(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        filter_expression: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List featured content rules from Chronicle Content Hub.

        Args:
            page_size: Maximum number of featured content rules to return.
                If unspecified, at most 100 rules will be returned.
                Maximum value is 1000. If provided, returns dict with
                nextPageToken.
            page_token: Token for retrieving the next page of results.
            filter_expression: Optional filter expression. Supported:
                - category_name:"<category_name>" (OR for multiple)
                - policy_name:"<policy_name>" (OR for multiple)
                - rule_id:"ur_<id>" (OR for multiple)
                - rule_precision:"<rule_precision>" (Precise or Broad)
                - search_rule_name_or_description=~"<text>"
                Multiple filters can be combined with AND operator.

        Returns:
            If page_size is not provided: A dictionary containing a list of all
                featured content rules.
            If page_size is provided: A dictionary containing a list of
                featuredContentRules and a nextPageToken if more results are
                available.

        Raises:
            APIError: If the API request fails
        """
        return _list_featured_content_rules(
            self, page_size, page_token, filter_expression
        )

    def search_curated_detections(
        self,
        rule_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        list_basis: Union["ListBasis", str] = None,
        alert_state: Union["AlertState", str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        max_resp_size_bytes: int | None = None,
        include_nested_detections: bool | None = False,
    ) -> dict[str, Any]:
        """Search for detections generated by a specific curated rule.

        Args:
            rule_id: ID of the curated rule to search detections for
            start_time: The time to start searching detections from (inclusive)
            end_time: The time to end searching detections to (exclusive)
            list_basis: Basis for applying time filters. Can be
                ListBasis enum or string. Valid values:
                ListBasis.LIST_BASIS_UNSPECIFIED,
                ListBasis.DETECTION_TIME, ListBasis.CREATED_TIME
            alert_state: Filter by alert state. Can be
                AlertState enum or string. Valid values:
                AlertState.UNSPECIFIED, AlertState.NOT_ALERTING,
                AlertState.ALERTING
            page_size: Maximum detections to return (max 1000)
            page_token: Token for pagination
            max_resp_size_bytes: Maximum response size in bytes
            include_nested_detections: Include nested detections

        Returns:
            Dictionary containing detection results with keys:
                - curatedDetections or nestedDetectionSamples
                - nextPageToken
                - respTooLargeDetectionsTruncated

        Raises:
            APIError: If the API request fails
            ValueError: If invalid alert_state or list_basis provided
        """
        return _search_curated_detections(
            self,
            rule_id,
            start_time,
            end_time,
            list_basis,
            alert_state,
            page_size,
            page_token,
            max_resp_size_bytes,
            include_nested_detections,
        )

    def validate_rule(self, rule_text: str):
        """Validates a YARA-L2 rule against the Chronicle API.

        Args:
            rule_text: Content of the rule to validate

        Returns:
            ValidationResult containing:
                - success: Whether the rule is valid
                - message: Error message if validation failed,
                    None if successful
                - position: Dictionary containing position information for
                    errors, if available

        Raises:
            APIError: If the API request fails
        """
        return _validate_rule(self, rule_text)

    def translate_nl_to_udm(self, text: str) -> str:
        """Translate natural language query to UDM search syntax.

        Args:
            text: Natural language query text

        Returns:
            UDM search query string

        Raises:
            APIError: If the API request fails
                or no valid query can be generated
        """
        return translate_nl_to_udm(self, text)

    def gemini(
        self,
        query: str,
        conversation_id: str | None = None,
        context_uri: str = "/search",
        context_body: dict[str, Any] | None = None,
    ) -> GeminiResponse:
        """Query Chronicle Gemini with a prompt.

        This method provides access to Chronicle's Gemini conversational
        AI interface, which can answer security questions, generate detection
        rules, explain CVEs, and provide other security insights.

        Args:
            query: The text query to send to Gemini
            conversation_id: Optional conversation ID. If not provided,
                a new conversation will be created
            context_uri: URI context for the query (default: "/search")
            context_body: Optional additional context as a dictionary

        Returns:
            A GeminiResponse object with structured content blocks
            (text, code, HTML) and suggested actions if applicable

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            # Ask about a security concept
            response = chronicle.gemini("What is Windows event ID 4625?")

            # Get explanatory text
            print(response.get_text_content())

            # Get code blocks separately (for rule generation, etc.)
            for code_block in response.get_code_blocks():
                print(f"Code: {code_block.content}")
            ```
        """
        return _query_gemini(
            self,
            query=query,
            conversation_id=conversation_id,
            context_uri=context_uri,
            context_body=context_body,
        )

    def opt_in_to_gemini(self) -> bool:
        """Opt the user into Gemini (Duet AI) in Chronicle.

        This method updates the user's preferences to enable Duet AI chat,
        which is required before using the Gemini functionality. The Gemini
        method will attempt to do this automatically if needed, but this method
        allows for explicit opt-in.

        Returns:
            True if successful, False if permission error

        Raises:
            APIError: If the API request fails for a reason other
                than permissions

        Example:
            ```python
            # Explicitly opt in to Gemini before using it
            chronicle.opt_in_to_gemini()

            # Now use Gemini
            response = chronicle.gemini("What is Windows event ID 4625?")
            ```
        """
        # Set the opt-in attempted flag
        self._gemini_opt_in_attempted = True
        return _opt_in_to_gemini(self)

    def nl_search(
        self,
        text: str,
        start_time: datetime,
        end_time: datetime,
        max_events: int = 10000,
        case_insensitive: bool = True,
        max_attempts: int = 30,
    ) -> dict[str, Any]:
        """Perform a search using natural language that is translated to UDM.

        Args:
            text: Natural language query text
            start_time: Search start time
            end_time: Search end time
            max_events: Maximum events to return
            case_insensitive: Whether to perform case-insensitive search
            max_attempts: Maximum number of polling attempts

        Returns:
            Dict containing the search results with events

        Raises:
            APIError: If the API request fails
        """
        return _nl_search(
            self,
            text=text,
            start_time=start_time,
            end_time=end_time,
            max_events=max_events,
            case_insensitive=case_insensitive,
            max_attempts=max_attempts,
        )

    def ingest_log(
        self,
        log_type: str,
        log_message: str,
        log_entry_time: datetime | None = None,
        collection_time: datetime | None = None,
        forwarder_id: str | None = None,
        force_log_type: bool = False,
        namespace: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Ingest a log into Chronicle.

        Args:
            log_type: Chronicle log type (e.g., "OKTA", "WINDOWS", etc.)
            log_message: The raw log message to ingest
            log_entry_time: The time the log entry was created
                (defaults to current time)
            collection_time: The time the log was collected
                (defaults to current time)
            forwarder_id: ID of the forwarder to use
                (creates or uses default if None)
            force_log_type: Whether to force using the log type even
                if not in the valid list

        Returns:
            Dictionary containing the operation details for the ingestion

        Raises:
            ValueError: If the log type is invalid or timestamps are invalid
            APIError: If the API request fails
        """
        return _ingest_log(
            self,
            log_type=log_type,
            log_message=log_message,
            log_entry_time=log_entry_time,
            collection_time=collection_time,
            forwarder_id=forwarder_id,
            force_log_type=force_log_type,
            namespace=namespace,
            labels=labels,
        )

    def import_entities(
        self,
        entities: dict[str, Any] | list[dict[str, Any]],
        log_type: str,
    ) -> dict[str, Any]:
        """Import entities into Chronicle.

        Args:
            client: ChronicleClient instance
            entities: An entity dictionary or a list of entity dictionaries
            log_type: The log type of the log from which this entity is created

        Returns:
            Dictionary containing the operation details for the ingestion

        Raises:
            ValueError: If any required fields are missing or entities malformed
            APIError: If the API request fails
        """
        return _import_entities(
            self,
            entities=entities,
            log_type=log_type,
        )

    def create_forwarder(
        self,
        display_name: str,
        metadata: dict[str, Any] | None = None,
        upload_compression: bool = False,
        enable_server: bool = False,
        regex_filters: list[dict[str, Any]] | None = None,
        graceful_timeout: str | None = None,
        drain_timeout: str | None = None,
        http_settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new forwarder in Chronicle.

        Args:
            display_name: User-specified name for the forwarder
            metadata: Optional forwarder metadata (asset_namespace, labels)
            upload_compression: Whether uploaded data should be compressed
            enable_server: Whether server functionality is enabled on
                the forwarder
            regex_filters: Regex filters applied at the forwarder level
            graceful_timeout: Timeout, after which the forwarder returns a bad
                readiness/health check and still accepts new connections
            drain_timeout: Timeout, after which the forwarder waits for active
                connections to successfully close on their own before being
                closed by the server
            http_settings: HTTP-specific server settings

        Returns:
            Dictionary containing the created forwarder details

        Raises:
            APIError: If the API request fails
        """
        return _create_forwarder(
            self,
            display_name=display_name,
            metadata=metadata,
            upload_compression=upload_compression,
            enable_server=enable_server,
            regex_filters=regex_filters,
            graceful_timeout=graceful_timeout,
            drain_timeout=drain_timeout,
            http_settings=http_settings,
        )

    def list_forwarders(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List forwarders in Chronicle.

        Args:
            page_size: Maximum number of forwarders to return (1-1000)
            page_token: Token for pagination

        Returns:
            Dictionary containing list of forwarders and next page token

        Raises:
            APIError: If the API request fails
        """
        return _list_forwarders(
            self,
            page_size=page_size,
            page_token=page_token,
        )

    def get_forwarder(self, forwarder_id: str) -> dict[str, Any]:
        """Get a forwarder by ID.

        Args:
            forwarder_id: ID of the forwarder to retrieve

        Returns:
            Dictionary containing the forwarder details

        Raises:
            APIError: If the API request fails
        """
        return _get_forwarder(self, forwarder_id=forwarder_id)

    def update_forwarder(
        self,
        forwarder_id: str,
        display_name: str | None = None,
        metadata: dict[str, Any] | None = None,
        upload_compression: bool | None = None,
        enable_server: bool | None = None,
        regex_filters: list[dict[str, Any]] | None = None,
        graceful_timeout: str | None = None,
        drain_timeout: str | None = None,
        http_settings: dict[str, Any] | None = None,
        update_mask: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update a forwarder in Chronicle.

        Args:
            forwarder_id: ID of the forwarder to update
            display_name: New display name for the forwarder
            metadata: New metadata key-value pairs for the forwarder
            upload_compression: New upload compression setting
            enable_server: New server enabled setting
            regex_filters: New regex filter patterns and actions
            graceful_timeout: New graceful timeout duration for server
            drain_timeout: New drain timeout duration for server
            http_settings: New HTTP server settings
            update_mask: List of field paths to update.
                If not provided, all fields with non-None values
                will be updated.

        Returns:
            Dictionary containing the updated forwarder details

        Raises:
            APIError: If the API request fails
        """
        return _update_forwarder(
            self,
            forwarder_id=forwarder_id,
            display_name=display_name,
            metadata=metadata,
            upload_compression=upload_compression,
            enable_server=enable_server,
            regex_filters=regex_filters,
            graceful_timeout=graceful_timeout,
            drain_timeout=drain_timeout,
            http_settings=http_settings,
            update_mask=update_mask,
        )

    def delete_forwarder(self, forwarder_id: str) -> dict[str, Any]:
        """Delete a forwarder from Chronicle.

        Args:
            forwarder_id: ID of the forwarder to delete

        Returns:
            Dictionary containing the empty response (usually {})

        Raises:
            APIError: If the API request fails
        """
        return _delete_forwarder(self, forwarder_id=forwarder_id)

    def get_or_create_forwarder(
        self, display_name: str = "Wrapper-SDK-Forwarder"
    ) -> dict[str, Any]:
        """Get an existing forwarder by name or create a new one if none exists.

        Args:
            display_name: Name of the forwarder to find or create

        Returns:
            Dictionary containing the forwarder details

        Raises:
            APIError: If the API request fails
        """
        return _get_or_create_forwarder(self, display_name=display_name)

    def get_all_log_types(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all available Chronicle log types.

        Args:
            page_size: Number of results per page (fetches single page)
            page_token: Page token for pagination

        Returns:
            List of log types
        """
        return _get_all_log_types(
            client=self,
            page_size=page_size,
            page_token=page_token,
        )

    def is_valid_log_type(self, log_type_id: str) -> bool:
        """Check if a log type ID is valid by querying.

        Args:
            log_type_id: The log type ID to validate

        Returns:
            True if the log type exists, False otherwise
        """
        return _is_valid_log_type(client=self, log_type_id=log_type_id)

    def get_log_type_description(self, log_type_id: str) -> str | None:
        """Get the display name for a log type ID.

        Args:
            log_type_id: The log type ID to get the description for

        Returns:
            Display name if the log type exists, None otherwise
        """
        return _get_log_type_description(log_type_id, client=self)

    def search_log_types(
        self,
        search_term: str,
        case_sensitive: bool = False,
        search_in_description: bool = True,
    ) -> list[dict[str, Any]]:
        """Search log types by ID or description.

        Args:
            search_term: Term to search for
            case_sensitive: Whether the search should be case sensitive
            search_in_description: Whether to search in descriptions
                as well as IDs

        Returns:
            List of matching log types
        """
        return _search_log_types(
            search_term,
            case_sensitive,
            search_in_description,
            client=self,
        )

    def ingest_udm(
        self,
        udm_events: dict[str, Any] | list[dict[str, Any]],
        add_missing_ids: bool = True,
    ) -> dict[str, Any]:
        """Ingest UDM events directly into Chronicle.

        Args:
            udm_events: A single UDM event dictionary or a list of UDM
                event dictionaries
            add_missing_ids: Whether to automatically add unique IDs to
                events missing them

        Returns:
            Dictionary containing the operation details for the ingestion

        Raises:
            ValueError: If any required fields are missing or events are
                malformed
            APIError: If the API request fails
        """
        return _ingest_udm(
            self, udm_events=udm_events, add_missing_ids=add_missing_ids
        )

    def get_data_export(self, data_export_id: str) -> dict[str, Any]:
        """Get information about a specific data export.

        Args:
            data_export_id: ID of the data export to retrieve

        Returns:
            Dictionary containing data export details

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            export = chronicle.get_data_export("export123")
            print(f"Export status: {export['data_export_status']['stage']}")
            ```
        """
        return _get_data_export(self, data_export_id)

    def create_data_export(
        self,
        gcs_bucket: str,
        start_time: datetime,
        end_time: datetime,
        log_type: str | None = None,
        log_types: list[str] | None = None,
        export_all_logs: bool = False,
    ) -> dict[str, Any]:
        """Create a new data export job.

        Args:
            gcs_bucket: GCS bucket path in format
                "projects/{project}/buckets/{bucket}"
            start_time: Start time for the export (inclusive)
            end_time: End time for the export (exclusive)
            log_type: Optional specific log type to export (deprecated).
                Use log_types instead.
            log_types: Optional list of log types to export.
                If None and export_all_logs is False, no logs will be exported
            export_all_logs: Whether to export all log types

        Returns:
            Dictionary containing details of the created data export

        Raises:
            APIError: If the API request fails
            ValueError: If invalid parameters are provided

        Example:
            ```python
            from datetime import datetime, timedelta

            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)

            # Export specific log types
            export = chronicle.create_data_export(
                gcs_bucket="projects/my-project/buckets/my-bucket",
                start_time=start_time,
                end_time=end_time,
                log_types=["WINDOWS", "LINUX"]
            )

            # Export a single log type (legacy method)
            export = chronicle.create_data_export(
                gcs_bucket="projects/my-project/buckets/my-bucket",
                start_time=start_time,
                end_time=end_time,
                log_type="WINDOWS"
            )

            # Export all logs
            export = chronicle.create_data_export(
                gcs_bucket="projects/my-project/buckets/my-bucket",
                start_time=start_time,
                end_time=end_time,
                export_all_logs=True
            )
            ```
        """
        return _create_data_export(
            self,
            gcs_bucket=gcs_bucket,
            start_time=start_time,
            end_time=end_time,
            log_type=log_type,
            log_types=log_types,
            export_all_logs=export_all_logs,
        )

    def cancel_data_export(self, data_export_id: str) -> dict[str, Any]:
        """Cancel an in-progress data export.

        Args:
            data_export_id: ID of the data export to cancel

        Returns:
            Dictionary containing details of the cancelled data export

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            result = chronicle.cancel_data_export("export123")
            print("Export cancellation request submitted")
            ```
        """
        return _cancel_data_export(self, data_export_id)

    def fetch_available_log_types(
        self,
        start_time: datetime,
        end_time: datetime,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Fetch available log types for export within a time range.

        Args:
            start_time: Start time for the time range (inclusive)
            end_time: End time for the time range (exclusive)
            page_size: Optional maximum number of results to return
            page_token: Optional page token for pagination

        Returns:
            Dictionary containing:
                - available_log_types: List of AvailableLogType objects
                - next_page_token: Token for fetching the next page of results

        Raises:
            APIError: If the API request fails
            ValueError: If invalid parameters are provided

        Example:
            ```python
            from datetime import datetime, timedelta

            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)

            result = chronicle.fetch_available_log_types(
                start_time=start_time,
                end_time=end_time
            )

            for log_type in result["available_log_types"]:
                print(f"{log_type.display_name} ({log_type.log_type})")
                print(
                    f"  Available from {log_type.start_time} to "
                    f"{log_type.end_time}"
                )
            ```
        """
        return _fetch_available_log_types(
            self,
            start_time=start_time,
            end_time=end_time,
            page_size=page_size,
            page_token=page_token,
        )

    def update_data_export(
        self,
        data_export_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        gcs_bucket: str | None = None,
        log_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing data export job.

        Note: The job must be in the "IN_QUEUE" state to be updated.

        Args:
            data_export_id: ID of the data export to update
            start_time: Optional new start time for the export
            end_time: Optional new end time for the export
            gcs_bucket: Optional new GCS bucket path
            log_types: Optional new list of log types to export

        Returns:
            Dictionary containing details of the updated data export

        Raises:
            APIError: If the API request fails
            ValueError: If invalid parameters are provided
        """
        return _update_data_export(
            self,
            data_export_id=data_export_id,
            start_time=start_time,
            end_time=end_time,
            gcs_bucket=gcs_bucket,
            log_types=log_types,
        )

    def list_data_export(
        self,
        filters: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List data export jobs.

        Args:
            filters: Filter string
            page_size: Page size
            page_token: Page token

        Returns:
            Dictionary containing data export list

        Raises:
            APIError: If the API request fails

        Example:
            ```python
            export = chronicle.list_data_export()
            ```
        """
        return _list_data_export(
            self,
            filters=filters,
            page_size=page_size,
            page_token=page_token,
        )

    # Data Table methods

    def create_data_table(
        self,
        name: str,
        description: str,
        header: dict[str, DataTableColumnType | str],
        column_options: dict[str, dict[str, Any]] | None = None,
        rows: list[list[str]] | None = None,
        scopes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new data table.

        Args:
            name: The name for the new data table
            description: A user-provided description of the data table
            header: A dictionary mapping column names to column types
            rows: Optional list of rows for the data table
            scopes: Optional list of scopes for the data table

        Returns:
            Dictionary containing the created data table

        Raises:
            APIError: If the API request fails
            SecOpsError: If the data table name is invalid
                or CIDR validation fails
        """
        return _create_data_table(
            self, name, description, header, column_options, rows, scopes
        )

    def get_data_table(self, name: str) -> dict[str, Any]:
        """Get data table details.

        Args:
            name: The name of the data table to get

        Returns:
            Dictionary containing the data table

        Raises:
            APIError: If the API request fails
        """
        return _get_data_table(self, name)

    def list_data_tables(
        self, order_by: str | None = None
    ) -> list[dict[str, Any]]:
        """List data tables.

        Args:
            order_by: Configures ordering of DataTables in the response.
                      Note: The API only supports "createTime asc".

        Returns:
            List of data tables

        Raises:
            APIError: If the API request fails
        """
        return _list_data_tables(self, order_by)

    def delete_data_table(
        self, name: str, force: bool = False
    ) -> dict[str, Any]:
        """Delete a data table.

        Args:
            name: The name of the data table to delete
            force: If set to true, any rows under this data table will
                also be deleted. (Otherwise, the request will only work
                if the data table has no rows).

        Returns:
            Dictionary containing the deleted data table or empty dict

        Raises:
            APIError: If the API request fails
        """
        return _delete_data_table(self, name, force)

    def create_data_table_rows(
        self, name: str, rows: list[list[str]]
    ) -> list[dict[str, Any]]:
        """Create data table rows, chunking if necessary.

        Args:
            name: The name of the data table
            rows: A list of rows for the data table

        Returns:
            List of responses containing the created data table rows

        Raises:
            APIError: If the API request fails
            SecOpsError: If a row is too large to process
        """
        return _create_data_table_rows(self, name, rows)

    def list_data_table_rows(
        self, name: str, order_by: str | None = None
    ) -> list[dict[str, Any]]:
        """List data table rows.

        Args:
            name: The name of the data table to list rows from
            order_by: Configures ordering of DataTableRows in the response.
                      Note: The API only supports "createTime asc".

        Returns:
            List of data table rows

        Raises:
            APIError: If the API request fails
        """
        return _list_data_table_rows(self, name, order_by)

    def delete_data_table_rows(
        self, name: str, row_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Delete data table rows.

        Args:
            name: The name of the data table to delete rows from
            row_ids: The IDs of the rows to delete

        Returns:
            List of dictionaries containing the deleted data table rows

        Raises:
            APIError: If the API request fails
        """
        return _delete_data_table_rows(self, name, row_ids)

    def replace_data_table_rows(
        self, name: str, rows: list[list[str]]
    ) -> list[dict[str, Any]]:
        """Replace all data table rows with new rows, chunking if necessary.

        This method replaces all existing rows in a data table with the provided
        new rows. It handles chunking to stay within API limits.

        Args:
            name: Data table name
            rows: List of rows where each row is a list of string values

        Returns:
            List of response objects, one per chunk

        Raises:
            APIError: If the API request fails
            SecOpsError: If a row is too large to process
        """
        return _replace_data_table_rows(self, name, rows)

    def update_data_table(
        self,
        name: str,
        description: str | None = None,
        row_time_to_live: str | None = None,
        update_mask: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update a data table using the PATCH method.

        Args:
            name: The name of the data table to update
            description: Description for the data table
            row_time_to_live: TTL for the data table rows
            update_mask: list of fields to update.
                        When no field mask is supplied, all non-empty fields
                        will be updated.
                        Supported fields include:
                            'description', 'row_time_to_live'.

        Returns:
            Dictionary containing the updated data table

        Raises:
            APIError: If the API request fails
            SecOpsError: If validation fails
        """
        return _update_data_table(
            self, name, description, row_time_to_live, update_mask
        )

    def update_data_table_rows(
        self,
        name: str,
        row_updates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Update multiple data table rows in bulk.

        This method updates existing rows in a data table using their
        full resource names. It supports chunking to handle large batches
        and respects API limits (max 1000 rows or 2MB per request).

        Args:
            name: The name of the data table
            row_updates: List of row update specifications.
                Each dict must contain:
                - 'name': str - Full resource name of the row to update
                  (format: projects/{project}/locations/{location}/
                  instances/{instance}/dataTables/{table}/
                  dataTableRows/{row_id})
                - 'values': List[str] - The new values for the row
                - 'update_mask': str (optional) - Comma-separated list
                  of fields to update (e.g., 'values'). If not specified,
                  all fields are updated.

        Returns:
            List of response dictionaries from the API, one per chunk

        Raises:
            APIError: If the API request fails
            SecOpsError: If a row is too large or validation fails

        Example:
            ```python
            # First, get the rows to obtain their full resource names
            rows = chronicle.list_data_table_rows('my_table')

            # Update multiple rows
            updates = [
                {
                    'name': rows[0]['name'],
                    'values': ['new-val1', 'new-val2', 'new-val3']
                },
                {
                    'name': rows[1]['name'],
                    'values': ['updated-val1', 'updated-val2', 'updated-val3'],
                    'update_mask': 'values'
                }
            ]
            responses = chronicle.update_data_table_rows(
                'my_table',
                updates
            )
            ```
        """
        return _update_data_table_rows(self, name, row_updates)

    # Rule Exclusion methods

    def list_rule_exclusions(
        self, page_size: int = 100, page_token: str | None = None
    ) -> dict[str, Any]:
        """List rule exclusions.

        Args:
            page_size: Maximum number of rule exclusions to return per page
            page_token: Page token for pagination

        Returns:
            Dictionary containing the list of rule exclusions

        Raises:
            APIError: If the API request fails
        """
        return _list_rule_exclusions(self, page_size, page_token)

    def get_rule_exclusion(self, exclusion_id: str) -> dict[str, Any]:
        """Get a rule exclusion by name.

        Args:
            exclusion_id: Id of the rule exclusion to retrieve.
                Can be the ID or full resource name.

        Returns:
            Dictionary containing rule exclusion information

        Raises:
            APIError: If the API request fails
        """
        return _get_rule_exclusion(self, exclusion_id=exclusion_id)

    def create_rule_exclusion(
        self, display_name: str, refinement_type: str, query: str
    ) -> dict[str, Any]:
        """Creates a new rule exclusion.

        Args:
            display_name: The display name to use for the rule exclusion
            refinement_type: The type of the Findings refinement
                    Must be one of:
                    - DETECTION_EXCLUSION
                    - FINDINGS_REFINEMENT_TYPE_UNSPECIFIED
            query: The query for the findings refinement.

        Returns:
            Dictionary containing the created rule exclusion

        Raises:
            APIError: If the API request fails
        """
        return _create_rule_exclusion(
            self,
            display_name=display_name,
            refinement_type=RuleExclusionType[refinement_type],
            query=query,
        )

    def patch_rule_exclusion(
        self,
        exclusion_id: str,
        display_name: str | None = None,
        refinement_type: str | None = None,
        query: str | None = None,
        update_mask: str | None = None,
    ) -> dict[str, Any]:
        """Updates a rule exclusion.

        Args:
            exclusion_id: Id of the rule exclusion to update
            display_name: The display name to use for the rule exclusion
            refinement_type: The type of the Findings refinement
                    Must be one of:
                    - DETECTION_EXCLUSION
                    - FINDINGS_REFINEMENT_TYPE_UNSPECIFIED
            query: The query for the findings refinement.
            update_mask: Comma-separated list of fields to update

        Returns:
            Dictionary containing the updated rule exclusion

        Raises:
            APIError: If the API request fails
        """
        return _patch_rule_exclusion(
            self,
            exclusion_id=exclusion_id,
            display_name=display_name,
            refinement_type=(
                RuleExclusionType[refinement_type] if refinement_type else None
            ),
            query=query,
            update_mask=update_mask,
        )

    def compute_rule_exclusion_activity(
        self,
        exclusion_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Compute activity statistics for rule exclusions.

        Args:
            exclusion_id: Id of a specific rule exclusion
            start_time: Optional start of the time window
            end_time: Optional end of the time window

        Returns:
            Dictionary containing activity statistics

        Raises:
            APIError: If the API request fails
        """
        return _compute_rule_exclusion_activity(
            self,
            exclusion_id=exclusion_id,
            start_time=start_time,
            end_time=end_time,
        )

    def get_rule_exclusion_deployment(
        self, exclusion_id: str
    ) -> dict[str, Any]:
        """Get deployment information for a rule exclusion.

        Args:
            exclusion_id: Id of the rule exclusion

        Returns:
            Dictionary containing deployment information

        Raises:
            APIError: If the API request fails
        """
        return _get_rule_exclusion_deployment(self, exclusion_id=exclusion_id)

    def update_rule_exclusion_deployment(
        self,
        exclusion_id: str,
        enabled: bool | None = None,
        archived: bool | None = None,
        detection_exclusion_application: None | (str | dict[str, Any]) = None,
        update_mask: str | None = None,
    ) -> dict[str, Any]:
        """Update deployment settings for a rule exclusion.

        Args:
            exclusion_id: Id of the rule exclusion
            enabled: Whether the rule exclusion should be enabled
            archived: Whether the rule exclusion should be archived
            detection_exclusion_application: The resources which the detection
                exclusion is applied to.
                Must be either valid JSON or JSON string
            update_mask: Comma-separated list of fields to update

        Returns:
            Dictionary containing updated deployment information

        Raises:
            APIError: If the API request fails
        """
        deployment_update_details = UpdateRuleDeployment(
            enabled=enabled,
            archived=archived,
            detection_exclusion_application=detection_exclusion_application,
        )
        return _update_rule_exclusion_deployment(
            self,
            exclusion_id=exclusion_id,
            deployment_details=deployment_update_details,
            update_mask=update_mask,
        )

    # Reference List methods

    def create_reference_list(
        self,
        name: str,
        description: str = "",
        entries: list[str] = None,
        syntax_type: ReferenceListSyntaxType = ReferenceListSyntaxType.STRING,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Create a new reference list.

        Args:
            name: The name for the new reference list
            description: A user-provided description of the reference list
            entries: A list of entries for the reference list
            syntax_type: The syntax type of the reference list
            api_version: Preferred API version to use. Defaults to V1

        Returns:
            Dictionary containing the created reference list

        Raises:
            APIError: If the API request fails
            SecOpsError: If the reference list name is invalid or
                a CIDR entry is invalid
        """
        # Defaulting to empty string
        if entries is None:
            entries = []

        return _create_reference_list(
            self, name, description, entries, syntax_type, api_version
        )

    def get_reference_list(
        self,
        name: str,
        view: ReferenceListView = ReferenceListView.FULL,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Get a single reference list.

        Args:
            name: The name of the reference list
            view: How much of the ReferenceList to view.
                Defaults to REFERENCE_LIST_VIEW_FULL.
            api_version: Preferred API version to use. Defaults to V1

        Returns:
            Dictionary containing the reference list

        Raises:
            APIError: If the API request fails
        """
        return _get_reference_list(self, name, view, api_version)

    def list_reference_lists(
        self,
        view: ReferenceListView = ReferenceListView.BASIC,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> list[dict[str, Any]]:
        """List reference lists.

        Args:
            view: How much of each ReferenceList to view.
                Defaults to REFERENCE_LIST_VIEW_BASIC.
            api_version: Preferred API version to use. Defaults to V1

        Returns:
            List of reference lists, ordered in ascending
            alphabetical order by name

        Raises:
            APIError: If the API request fails
        """
        return _list_reference_lists(self, view, api_version)

    def update_reference_list(
        self,
        name: str,
        description: str | None = None,
        entries: list[str] | None = None,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """Update a reference list.

        Args:
            name: The name of the reference list
            description: A user-provided description of the reference list
            entries: A list of entries for the reference list
            api_version: Preferred API version to use. Defaults to V1

        Returns:
            Dictionary containing the updated reference list

        Raises:
            APIError: If the API request fails
            SecOpsError: If no description or entries are provided to be updated
        """
        return _update_reference_list(
            self, name, description, entries, api_version
        )

    def generate_udm_key_value_mappings(
        self,
        log_format: str,
        log: str,
        use_array_bracket_notation: bool | None = None,
        compress_array_fields: bool | None = None,
    ) -> dict[str, Any]:
        """Generate UDM key-value mappings for provided row log

        Args:
            log_format: The format of the log (JSON, CSV, XML)
            log: The log to retrieve unique values from
            use_array_bracket_notation: Whether to use array bracket notation
            compress_array_fields: Whether to compress array fields

        Returns:
            Dictionary containing the generated key-value mappings

        Raises:
            APIError: If the API request fails
        """

        return _generate_udm_key_value_mappings(
            self,
            RowLogFormat(log_format),
            log,
            use_array_bracket_notation,
            compress_array_fields,
        )

    # Dashboard Methods
    def create_dashboard(
        self,
        display_name: str,
        access_type: str,
        description: str | None = None,
        filters: list[dict[str, Any]] | str | None = None,
        charts: list[dict[str, Any]] | str | None = None,
    ) -> dict[str, Any]:
        """Create a new native dashboard.

        Args:
            display_name: Name of the dashboard to create
            access_type: Access type for the dashboard (Public or Private)
            description: Description for the dashboard
            filters: List of filters to apply to the dashboard
                (JSON or JSON string)
            charts: List of charts to include in the dashboard
                (JSON or JSON string)

        Returns:
            Dictionary containing the created dashboard details

        Raises:
            APIError: If the API request fails
        """
        try:
            access_type = DashboardAccessType[access_type.upper()]
        except ValueError as e:
            raise SecOpsError(f"Invalid access type: {access_type}") from e

        return _create_dashboard(
            self,
            display_name=display_name,
            access_type=access_type,
            description=description,
            filters=filters,
            charts=charts,
        )

    def import_dashboard(self, dashboard: dict[str, Any]) -> dict[str, Any]:
        """Create a new native dashboard.

        Args:
            dashboard: ImportNativeDashboardsInlineSource

        Returns:
            Dictionary containing the created dashboard details

        Raises:
            APIError: If the API request fails
        """

        return _import_dashboard(self, dashboard=dashboard)

    def export_dashboard(self, dashboard_names: list[str]) -> dict[str, Any]:
        """Export native dashboards.

        Args:
            dashboard_names: List of dashboard resource names to export.

        Returns:
            Dictionary containing the exported dashboards.

        Raises:
            APIError: If the API request fails
        """

        return _export_dashboard(self, dashboard_names=dashboard_names)

    def list_dashboards(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List all available dashboards.

        Args:
            page_size: Maximum number of results to return
            page_token: Token for pagination

        Returns:
            Dictionary containing dashboard list and pagination info
        """
        return _list_dashboards(
            self,
            page_size=page_size,
            page_token=page_token,
        )

    def get_dashboard(
        self,
        dashboard_id: str,
        view: str | None = None,
    ) -> dict[str, Any]:
        """Get information about a specific dashboard.

        Args:
            dashboard_id: ID of the dashboard to retrieve
            view: Level of detail to include in the response
                Defaults to BASIC

        Returns:
            Dictionary containing dashboard details
        """
        if view:
            try:
                view = DashboardView[view.upper()]
            except ValueError as e:
                raise SecOpsError(f"Invalid view: {view}") from e

        return _get_dashboard(
            self,
            dashboard_id=dashboard_id,
            view=view,
        )

    def update_dashboard(
        self,
        dashboard_id: str,
        display_name: str | None = None,
        description: str | None = None,
        filters: list[dict[str, Any]] | str | None = None,
        charts: list[dict[str, Any]] | str | None = None,
    ) -> dict[str, Any]:
        """Update an existing dashboard.

        Args:
            dashboard_id: ID of the dashboard to update
            display_name: New name for the dashboard (optional)
            description: New description for the dashboard (optional)
            filters: New filters for the dashboard (optional)
            charts: New charts for the dashboard (optional)

        Returns:
            Dictionary containing the updated dashboard details
        """
        return _update_dashboard(
            self,
            dashboard_id=dashboard_id,
            display_name=display_name,
            description=description,
            filters=filters,
            charts=charts,
        )

    def delete_dashboard(self, dashboard_id: str) -> dict[str, Any]:
        """Delete an existing dashboard.

        Args:
            dashboard_id: ID of the dashboard to delete
        """
        return _delete_dashboard(self, dashboard_id=dashboard_id)

    def add_chart(
        self,
        dashboard_id: str,
        display_name: str,
        chart_layout: dict[str, Any] | str,
        tile_type: str | None = None,
        chart_datasource: dict[str, Any] | str | None = None,
        visualization: dict[str, Any] | str | None = None,
        drill_down_config: dict[str, Any] | str | None = None,
        description: str | None = None,
        query: str | None = None,
        interval: InputInterval | dict[str, Any] | str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Add a chart to an existing dashboard.

        Args:
            dashboard_id: ID of the dashboard to add the chart to
            display_name: Display name for the chart
            chart_layout: Layout for the chart
            tile_type: Type of the tile
                (expected values: VISUALIZATION, BUTTON)
                Defaults to VISUALIZATION
            chart_datasource: Query and datasource used in the chart
                (Should be empty for Button type)
            visualization: Visualization for the chart.
            drill_down_config: Drill down configuration.
            description: Description for the chart
            query: Query for the chart
            interval: Query input interval for the chart
            **kwargs: Additional keyword arguments
                (Will be added to request payload)

        Returns:
            Dictionary containing the updated dashboard details
        """
        if tile_type:
            try:
                tile_type = TileType[tile_type.upper()]
            except ValueError as e:
                raise SecOpsError(f"Invalid tile type: {tile_type}") from e

        return _add_chart(
            self,
            dashboard_id=dashboard_id,
            display_name=display_name,
            chart_layout=chart_layout,
            tile_type=tile_type,
            chart_datasource=chart_datasource,
            visualization=visualization,
            drill_down_config=drill_down_config,
            description=description,
            query=query,
            interval=interval,
            **kwargs,
        )

    def duplicate_dashboard(
        self,
        dashboard_id: str,
        display_name: str,
        access_type: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Duplicate an existing dashboard.

        Args:
            dashboard_id: Id of the dashboard to duplicate
            display_name: Display name for the new dashboard
            access_type: Access type for the new dashboard (PRIVATE or PUBLIC)
            description: Description for the new dashboard

        Returns:
            Dictionary containing the updated dashboard details
        """
        try:
            access_type = DashboardAccessType[access_type.upper()]
        except ValueError as e:
            raise SecOpsError(f"Invalid access type: {access_type}") from e

        return _duplicate_dashboard(
            self,
            dashboard_id=dashboard_id,
            display_name=display_name,
            access_type=access_type,
            description=description,
        )

    def remove_chart(
        self,
        dashboard_id: str,
        chart_id: str,
    ) -> dict[str, Any]:
        """Remove a chart from a dashboard.

        Args:
            dashboard_id: ID of the dashboard containing the chart
            chart_id: ID of the chart to remove

        Returns:
            Dictionary containing the updated dashboard

        Raises:
            APIError: If the API request fails
        """
        return _remove_chart(
            self,
            dashboard_id=dashboard_id,
            chart_id=chart_id,
        )

    def get_chart(self, chart_id: str) -> dict[str, Any]:
        """Get information about a specific chart.

        Args:
            chart_id: ID of the chart to retrieve

        Returns:
            Dictionary containing chart details
        """
        return _get_chart(self, chart_id)

    def edit_chart(
        self,
        dashboard_id: str,
        dashboard_chart: None | (dict[str, Any] | DashboardChart | str) = None,
        dashboard_query: None | (dict[str, Any] | DashboardQuery | str) = None,
    ) -> dict[str, Any]:
        """Edit an existing chart in a dashboard.

        Args:
            dashboard_id: ID of the dashboard containing the chart
            dashboard_chart: Chart to edit in JSON or JSON string
                eg:{
                    "name": "<chart_id>"
                    "displayName": "<chart display name>",
                    "description": "<chart description>",
                    "visualization": {},
                    "chartDatasource": { "dataSources":[]},
                    "etag": "123131231321321"
                }

            dashboard_query: Chart Query to edit in JSON or JSON String
                eg:{
                    "name": "<query_id>",
                    "query": "<chart query>",
                    "input": {},
                    "etag":"123131231321321"
                }
        Returns:
            Dictionary containing the updated dashboard with edited chart
        """

        return _edit_chart(
            self,
            dashboard_id=dashboard_id,
            dashboard_chart=dashboard_chart,
            dashboard_query=dashboard_query,
        )

    def execute_dashboard_query(
        self,
        query: str,
        interval: InputInterval | dict[str, Any] | str,
        filters: list[dict[str, Any]] | str | None = None,
        clear_cache: bool | None = None,
    ) -> dict[str, Any]:
        """Execute a query for a dashboard.

        Args:
            dashboard_id: Id of the dashboard to execute the query for
            query: Query to execute
            interval: The time interval for the query
            filters: Filters to apply to the query
            clear_cache: Flag to read from database instead of cache

        Returns:
            Dictionary containing the query results
        """
        return _execute_dashboard_query(
            self,
            query=query,
            interval=interval,
            filters=filters,
            clear_cache=clear_cache,
        )

    def get_dashboard_query(self, query_id: str) -> dict[str, Any]:
        """Get the dashboard query details.

        Args:
            query_id: Id of the dashboard query

        Returns:
            Dictionary containing the query details
        """
        return _get_execute_query(self, query_id=query_id)

    def get_rule_deployment(
        self, rule_id: str, api_version: APIVersion | None = APIVersion.V1
    ) -> dict[str, Any]:
        """Get the current deployment for a rule.

        Args:
            rule_id: Unique ID of the detection rule (e.g., "ru_<UUID>")
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing the rule deployment information

        Raises:
            APIError: If the API request fails
        """
        return _get_rule_deployment(self, rule_id, api_version)

    def list_rule_deployments(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
        filter_query: str | None = None,
        api_version: APIVersion | None = APIVersion.V1,
    ) -> dict[str, Any]:
        """List rule deployments for the instance.

        Args:
            page_size: Maximum number of deployments to return per page
            page_token: Token for the next page of results, if available
            filter_query: Optional filter query to restrict results
            api_version: (Optional) Preferred API version to use.

        Returns:
            Dictionary containing rule deployments and pagination info

        Raises:
            APIError: If the API request fails
        """
        return _list_rule_deployments(
            self,
            page_size=page_size,
            page_token=page_token,
            filter_query=filter_query,
            api_version=api_version,
        )

    def set_rule_alerting(
        self, rule_id: str, enabled: bool = True
    ) -> dict[str, Any]:
        """Enable or disable alerting for a rule deployment.

        Args:
            rule_id: Unique ID of the detection rule (e.g., "ru_<UUID>")
            enabled: Whether to enable (True) or disable (False) alerting

        Returns:
            Dictionary containing the updated deployment information

        Raises:
            APIError: If the API request fails
        """
        return _set_rule_alerting(self, rule_id, alerting_enabled=enabled)

    def update_rule_deployment(
        self,
        rule_id: str,
        *,
        enabled: bool | None = None,
        alerting: bool | None = None,
        archived: bool | None = None,
        run_frequency: str | None = None,
    ) -> dict[str, Any]:
        """Generic updateDeployment wrapper.

        See RuleDeployment fields: enabled, alerting, archived, runFrequency.
        """
        return _update_rule_deployment(
            self,
            rule_id,
            enabled=enabled,
            alerting=alerting,
            archived=archived,
            run_frequency=run_frequency,
        )
