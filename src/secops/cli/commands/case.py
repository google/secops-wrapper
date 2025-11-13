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
"""Google SecOps CLI case commands"""

import sys

from secops.cli.utils.formatters import output_formatter


def setup_case_command(subparsers):
    """Set up the case command parser."""
    case_parser = subparsers.add_parser("case", help="Manage cases")
    case_parser.add_argument("--ids", help="Comma-separated list of case IDs")
    case_parser.set_defaults(func=handle_case_command)


def handle_case_command(args, chronicle):
    """Handle case command."""
    try:
        if args.ids:
            case_ids = [id.strip() for id in args.ids.split(",")]
            result = chronicle.get_cases(case_ids)

            # Convert CaseList to dictionary for output
            cases_dict = {
                "cases": [
                    {
                        "id": case.id,
                        "display_name": case.display_name,
                        "stage": case.stage,
                        "priority": case.priority,
                        "status": case.status,
                        "soar_platform_info": (
                            {
                                "case_id": case.soar_platform_info.case_id,
                                "platform_type": case.soar_platform_info.platform_type,  # pylint: disable=line-too-long
                            }
                            if case.soar_platform_info
                            else None
                        ),
                        "alert_ids": case.alert_ids,
                    }
                    for case in result.cases
                ]
            }
            output_formatter(cases_dict, args.output)
        else:
            print("Error: No case IDs provided", file=sys.stderr)
            sys.exit(1)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
