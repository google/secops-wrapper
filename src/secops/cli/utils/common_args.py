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

def _add_argument_if_not_exists(
    parser: argparse.ArgumentParser, *args: str, **kwargs
) -> None:
    """Add argument to parser only if it typically doesn't exist.

    Args:
        parser: Parser to add argument to
        *args: Positional arguments (flags)
        **kwargs: Keyword arguments
    """
    for option_string in args:
        if option_string in parser._option_string_actions:
            return
    parser.add_argument(*args, **kwargs)


def add_common_args(
    parser: argparse.ArgumentParser, suppress_defaults: bool = False
) -> None:
    """Add common arguments to a parser.

    Args:
        parser: Parser to add arguments to
        suppress_defaults: If True, do not set default values (let parent parser handle it)
    """
    config = load_config()
    default_base = argparse.SUPPRESS if suppress_defaults else None

    _add_argument_if_not_exists(
        parser,
        "--service-account",
        "--service_account",
        dest="service_account",
        default=default_base or config.get("service_account"),
        help="Path to service account JSON file",
    )
    _add_argument_if_not_exists(
        parser,
        "--output",
        choices=["json", "text"],
        default=default_base or "json",
        help="Output format",
    )


def add_chronicle_args(
    parser: argparse.ArgumentParser, suppress_defaults: bool = False
) -> None:
    """Add Chronicle-specific arguments to a parser.

    Args:
        parser: Parser to add arguments to
        suppress_defaults: If True, set default values to argparse.SUPPRESS
    """
    config = load_config()
    default_base = argparse.SUPPRESS if suppress_defaults else None

    _add_argument_if_not_exists(
        parser,
        "--customer-id",
        "--customer_id",
        dest="customer_id",
        default=default_base or config.get("customer_id"),
        help="Chronicle instance ID",
    )
    _add_argument_if_not_exists(
        parser,
        "--project-id",
        "--project_id",
        dest="project_id",
        default=default_base or config.get("project_id"),
        help="GCP project ID",
    )
    _add_argument_if_not_exists(
        parser,
        "--region",
        default=default_base or config.get("region", "us"),
        help="Chronicle API region",
    )
    _add_argument_if_not_exists(
        parser,
        "--api-version",
        "--api_version",
        dest="api_version",
        choices=["v1", "v1beta", "v1alpha"],
        default=default_base or config.get("api_version", "v1alpha"),
        help=(
            "Default API version for Chronicle requests " "(default: v1alpha)"
        ),
    )


def add_time_range_args(
    parser: argparse.ArgumentParser, required: bool = False
) -> None:
    """Add time range arguments to a parser.

    Args:
        parser: Parser to add arguments to.
        required: Whether a time range is required.
    """
    config = load_config()
    time_window_default = None if required else config.get("time_window", 24)

    group = parser.add_mutually_exclusive_group(required=required)

    group.add_argument(
        "--start-time",
        "--start_time",
        dest="start_time",
        default=config.get("start_time"),
        help="Start time in ISO format "
        "(YYYY-MM-DDTHH:MM:SSZ). "
        "Must be used with --end-time",
    )
    group.add_argument(
        "--time-window",
        "--time_window",
        dest="time_window",
        type=int,
        default=time_window_default,
        help="Time window in hours " "(alternative to start/end time)",
    )

    parser.add_argument(
        "--end-time",
        "--end_time",
        dest="end_time",
        default=config.get("end_time"),
        help="End time in ISO format "
        "(YYYY-MM-DDTHH:MM:SSZ). "
        "Used with --start-time",
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


def add_as_list_arg(parser: argparse.ArgumentParser) -> None:
    """Add as_list argument to a parser.

    Args:
        parser: Parser to add arguments to
    """
    parser.add_argument(
        "--as-list",
        "--as_list",
        dest="as_list",
        action="store_true",
        help=(
            "Return results as a list instead of a dict with pagination "
            "metadata."
        ),
    )
