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
"""Google SecOps CLI curated rule commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.common_args import add_pagination_args


def setup_curated_rules_command(subparsers):
    """Set up the curated-rule command group."""
    top = subparsers.add_parser(
        "curated-rule", help="Manage curated rules and rule sets"
    )
    lvl1 = top.add_subparsers(dest="curated_cmd", required=True)

    # ---- rules ----
    rules = lvl1.add_parser("rule", help="Manage curated rules")
    rules_sp = rules.add_subparsers(dest="rule_cmd", required=True)

    rules_list = rules_sp.add_parser("list", help="List curated rules")
    add_pagination_args(rules_list)
    rules_list.set_defaults(func=handle_curated_rules_rules_list_command)

    rules_get = rules_sp.add_parser("get", help="Get a curated rule")
    rg = rules_get.add_mutually_exclusive_group(required=True)
    rg.add_argument("--id", help="Rule UUID (e.g., ur_abc...)")
    rg.add_argument("--name", help="Rule display name")
    rules_get.set_defaults(func=handle_curated_rules_rules_get_command)

    # ---- rule-set ----
    rule_set = lvl1.add_parser("rule-set", help="Manage curated rule sets")
    rule_set_subparser = rule_set.add_subparsers(dest="rset_cmd", required=True)

    rule_set_list = rule_set_subparser.add_parser(
        "list", help="List curated rule sets"
    )
    add_pagination_args(rule_set_list)
    rule_set_list.set_defaults(func=handle_curated_rules_rule_set_list_command)

    rule_set_get = rule_set_subparser.add_parser(
        "get", help="Get a curated rule set"
    )
    rule_set_get.add_argument(
        "--id", required=True, help="Curated rule set UUID)"
    )
    rule_set_get.set_defaults(func=handle_curated_rules_rule_set_get_command)

    # ---- rule-set-category ----
    rule_set_cat = lvl1.add_parser(
        "rule-set-category", help="Manage curated rule set categories"
    )
    rule_set_cat_subparser = rule_set_cat.add_subparsers(
        dest="rcat_cmd", required=True
    )

    rule_set_cat_list = rule_set_cat_subparser.add_parser(
        "list", help="List curated rule set categories"
    )
    add_pagination_args(rule_set_cat_list)
    rule_set_cat_list.set_defaults(
        func=handle_curated_rules_rule_set_category_list_command
    )

    rule_set_cat_get = rule_set_cat_subparser.add_parser(
        "get", help="Get a curated rule set category"
    )
    rule_set_cat_get.add_argument("--id", required=True, help="Category UUID")
    rule_set_cat_get.set_defaults(
        func=handle_curated_rules_rule_set_category_get_command
    )

    # ---- rule-set-deployment ----
    rule_set_deployment = lvl1.add_parser(
        "rule-set-deployment", help="Manage curated rule set deployments"
    )
    rule_set_deployment_subparser = rule_set_deployment.add_subparsers(
        dest="rdep_cmd", required=True
    )

    rule_set_deployment_list = rule_set_deployment_subparser.add_parser(
        "list", help="List curated rule set deployments"
    )
    rule_set_deployment_list.add_argument(
        "--only-enabled", dest="only_enabled", action="store_true"
    )
    rule_set_deployment_list.add_argument(
        "--only-alerting", dest="only_alerting", action="store_true"
    )
    add_pagination_args(rule_set_deployment_list)
    rule_set_deployment_list.set_defaults(
        func=handle_curated_rules_rule_set_deployment_list_command
    )

    rule_set_deployment_get = rule_set_deployment_subparser.add_parser(
        "get", help="Get a curated rule set deployment"
    )
    get_group = rule_set_deployment_get.add_mutually_exclusive_group(
        required=True
    )
    get_group.add_argument("--id", help="Curated rule set ID (crs_...)")
    get_group.add_argument(
        "--name", help="Curated rule set display name (case-insensitive)"
    )
    rule_set_deployment_get.add_argument(
        "--precision", choices=["precise", "broad"], default="precise"
    )
    rule_set_deployment_get.set_defaults(
        func=handle_curated_rules_rule_set_deployment_get_command
    )

    rule_set_deployment_update = rule_set_deployment_subparser.add_parser(
        "update", help="Update a curated rule set deployment"
    )
    rule_set_deployment_update.add_argument(
        "--category-id", required=True, dest="category_id"
    )
    rule_set_deployment_update.add_argument(
        "--rule-set-id", required=True, dest="rule_set_id"
    )
    rule_set_deployment_update.add_argument(
        "--precision", choices=["precise", "broad"], required=True
    )
    rule_set_deployment_update.add_argument(
        "--enabled", choices=["true", "false"], required=True
    )
    rule_set_deployment_update.add_argument(
        "--alerting", choices=["true", "false"], help="Enable/disable alerting"
    )
    rule_set_deployment_update.set_defaults(
        func=handle_curated_rules_rule_set_deployment_update_command
    )


def handle_curated_rules_rules_list_command(args, chronicle):
    """List curated rules."""
    try:
        out = chronicle.list_curated_rules(
            page_size=getattr(args, "page_size", None),
            page_token=getattr(args, "page_token", None),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing curated rules: {e}", file=sys.stderr)
        sys.exit(1)


def handle_curated_rules_rules_get_command(args, chronicle):
    """Get curated rule by ID or display name."""
    try:
        if args.id:
            out = chronicle.get_curated_rule(args.id)
        else:
            # by display name
            out = chronicle.get_curated_rule_by_name(args.name)
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule: {e}", file=sys.stderr)
        sys.exit(1)


def handle_curated_rules_rule_set_list_command(args, chronicle):
    """List all curated rule sets"""
    try:
        out = chronicle.list_curated_rule_sets(
            page_size=getattr(args, "page_size", None),
            page_token=getattr(args, "page_token", None),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error listing curated rule sets: {e}", file=sys.stderr)
        sys.exit(1)


def handle_curated_rules_rule_set_get_command(args, chronicle):
    """Get curated rule set by ID."""
    try:
        out = chronicle.get_curated_rule_set(args.id)
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule set: {e}", file=sys.stderr)
        sys.exit(1)


def handle_curated_rules_rule_set_category_list_command(args, chronicle):
    """List all curated rule set categories."""
    try:
        out = chronicle.list_curated_rule_set_categories(
            page_size=getattr(args, "page_size", None),
            page_token=getattr(args, "page_token", None),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error listing curated rule set categories: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_curated_rules_rule_set_category_get_command(args, chronicle):
    """Get curated rule set category by ID."""
    try:
        out = chronicle.get_curated_rule_set_category(args.id)
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error getting curated rule set category: {e}", file=sys.stderr)
        sys.exit(1)


def handle_curated_rules_rule_set_deployment_list_command(args, chronicle):
    try:
        out = chronicle.list_curated_rule_set_deployments(
            only_enabled=bool(args.only_enabled),
            only_alerting=bool(args.only_alerting),
            page_size=getattr(args, "page_size", None),
            page_token=getattr(args, "page_token", None),
        )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error listing curated rule set deployments: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_curated_rules_rule_set_deployment_get_command(args, chronicle):
    try:
        if args.name:
            out = chronicle.get_curated_rule_set_deployment_by_name(
                args.name, precision=args.precision
            )
        else:
            out = chronicle.get_curated_rule_set_deployment(
                args.id, precision=args.precision
            )
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error getting curated rule set deployment: {e}", file=sys.stderr
        )
        sys.exit(1)


def handle_curated_rules_rule_set_deployment_update_command(args, chronicle):
    """Update curated rule set deployment fields."""
    try:

        def _convert_bool(s):
            """Convert "true"/"false" to bool."""
            return None if s is None else str(s).lower() == "true"

        payload = {
            "category_id": args.category_id,
            "rule_set_id": args.rule_set_id,
            "precision": args.precision,
            "enabled": _convert_bool(args.enabled),
        }
        if args.alerting is not None:
            payload["alerting"] = _convert_bool(args.alerting)
        out = chronicle.update_curated_rule_set_deployment(payload)
        output_formatter(out, getattr(args, "output", "json"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"Error updating curated rule set deployment: {e}", file=sys.stderr
        )
        sys.exit(1)
