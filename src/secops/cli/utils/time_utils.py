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
"""Google SecOps CLI datetime utils"""

import argparse
from datetime import datetime, timedelta, timezone


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string in ISO format.

    Args:
        dt_str: ISO formatted datetime string

    Returns:
        Parsed datetime object
    """
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def get_time_range(args: argparse.Namespace) -> tuple[datetime, datetime]:
    """Get start and end time from arguments.

    Args:
        args: Command line arguments

    Returns:
        Tuple of (start_time, end_time)
    """
    end_time = (
        parse_datetime(args.end_time)
        if args.end_time
        else datetime.now(timezone.utc)
    )

    if args.start_time:
        start_time = parse_datetime(args.start_time)
    else:
        start_time = end_time - timedelta(hours=args.time_window)

    return start_time, end_time
