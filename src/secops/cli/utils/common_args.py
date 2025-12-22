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
"""Google SecOps CLI common argument helpers"""

import argparse

from secops.cli.utils.config_utils import load_config


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to a parser.

    Args:
        parser: Parser to add arguments to
    """
    config = load_config()

    parser.add_argument(
        "--service-account",
        "--service_account",
        dest="service_account",
        default=config.get("service_account"),
        help="Path to service account JSON file",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="json",
        help="Output format",
    )


def add_chronicle_args(parser: argparse.ArgumentParser) -> None:
    """Add Chronicle-specific arguments to a parser.

    Args:
        parser: Parser to add arguments to
    """
    config = load_config()

    parser.add_argument(
        "--customer-id",
        "--customer_id",
        dest="customer_id",
        default=config.get("customer_id"),
        help="Chronicle instance ID",
    )
    parser.add_argument(
        "--project-id",
        "--project_id",
        dest="project_id",
        default=config.get("project_id"),
        help="GCP project ID",
    )
    parser.add_argument(
        "--region",
        default=config.get("region", "us"),
        help="Chronicle API region",
    )
    parser.add_argument(
        "--api-version",
        "--api_version",
        dest="api_version",
        choices=["v1", "v1beta", "v1alpha"],
        default=config.get("api_version", "v1alpha"),
        help=(
            "Default API version for Chronicle requests " "(default: v1alpha)"
        ),
    )


def add_time_range_args(parser: argparse.ArgumentParser) -> None:
    """Add time range arguments to a parser.

    Args:
        parser: Parser to add arguments to
    """
    config = load_config()

    parser.add_argument(
        "--start-time",
        "--start_time",
        dest="start_time",
        default=config.get("start_time"),
        help="Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)",
    )
    parser.add_argument(
        "--end-time",
        "--end_time",
        dest="end_time",
        default=config.get("end_time"),
        help="End time in ISO format (YYYY-MM-DDTHH:MM:SSZ)",
    )
    parser.add_argument(
        "--time-window",
        "--time_window",
        dest="time_window",
        type=int,
        default=config.get("time_window", 24),
        help="Time window in hours (alternative to start/end time)",
    )


def add_pagination_args(parser: argparse.ArgumentParser) -> None:
    """Add pagination arguments to a parser.

    Args:
        parser: Parser to add arguments to
    """
    parser.add_argument(
        "--page-size",
        "--page_size",
        type=int,
        dest="page_size",
        help="The number of results to return per page.",
    )
    parser.add_argument(
        "--page-token",
        "--page_token",
        type=str,
        dest="page_token",
        help="A page token, received from a previous `list` call.",
    )
