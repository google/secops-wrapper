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
"""Google SecOps CLI Gemini commands"""

import sys

from secops.cli.utils.formatters import output_formatter


def setup_gemini_command(subparsers):
    """Set up the Gemini command parser."""
    gemini_parser = subparsers.add_parser(
        "gemini", help="Interact with Gemini AI"
    )
    gemini_parser.add_argument(
        "--query", required=True, help="Query for Gemini"
    )
    gemini_parser.add_argument(
        "--conversation-id",
        "--conversation_id",
        dest="conversation_id",
        help="Continue an existing conversation",
    )
    gemini_parser.add_argument(
        "--raw", action="store_true", help="Output raw API response"
    )
    gemini_parser.add_argument(
        "--opt-in",
        "--opt_in",
        dest="opt_in",
        action="store_true",
        help="Explicitly opt-in to Gemini",
    )
    gemini_parser.set_defaults(func=handle_gemini_command)


def handle_gemini_command(args, chronicle):
    """Handle Gemini command."""
    try:
        if args.opt_in:
            result = chronicle.opt_in_to_gemini()
            print(f'Opt-in result: {"Success" if result else "Failed"}')
            if not result:
                return

        response = chronicle.gemini(
            query=args.query, conversation_id=args.conversation_id
        )

        if args.raw:
            # Output raw API response
            output_formatter(response.get_raw_response(), args.output)
        else:
            # Output formatted text content
            print(response.get_text_content())

            # Print code blocks if any
            code_blocks = response.get_code_blocks()
            if code_blocks:
                print("\nCode blocks:")
                for i, block in enumerate(code_blocks, 1):
                    print(
                        f"\n--- Code Block {i}"
                        + (f" ({block.title})" if block.title else "")
                        + " ---"
                    )
                    print(block.content)

            # Print suggested actions if any
            if response.suggested_actions:
                print("\nSuggested actions:")
                for action in response.suggested_actions:
                    print(f"- {action.display_text}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
