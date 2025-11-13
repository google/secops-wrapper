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
"""Google SecOps CLI help commands"""


def setup_help_command(subparsers):
    """Set up the help command parser.

    Args:
        subparsers: Subparsers object to add to
    """
    help_parser = subparsers.add_parser(
        "help", help="Get help with configuration and usage"
    )
    help_parser.add_argument(
        "--topic",
        choices=["config", "customer-id", "project-id"],
        default="config",
        help="Help topic",
    )
    help_parser.set_defaults(func=handle_help_command)


def handle_help_command(args, chronicle=None):
    """Handle help command.

    Args:
        args: Command line arguments
        chronicle: Not used for this command
    """
    # Unused argument
    _ = (chronicle,)

    if args.topic == "config":
        print("Configuration Help:")
        print("------------------")
        print("To use the SecOps CLI with Chronicle, you need to configure:")
        print("  1. Chronicle Customer ID (your Chronicle instance ID)")
        print(
            "  2. GCP Project ID (the Google Cloud project associated with "
            "your Chronicle instance)"
        )
        print("  3. Region (e.g., 'us', 'europe', 'asia-northeast1')")
        print("  4. Optional: Service Account credentials")
        print()
        print("Configuration commands:")
        print(
            "  secops config set --customer-id YOUR_CUSTOMER_ID --project-id "
            "YOUR_PROJECT_ID --region YOUR_REGION"
        )
        print("  secops config view")
        print("  secops config clear")
        print()
        print("For help finding your Customer ID or Project ID, run:")
        print("  secops help --topic customer-id")
        print("  secops help --topic project-id")
