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
"""Google SecOps CLI log processing pipeline commands"""

import sys

from secops.cli.utils.formatters import output_formatter
from secops.cli.utils.input_utils import load_json_or_file


def setup_log_processing_command(subparsers):
    """Set up the log-processing command parser."""
    log_processing_parser = subparsers.add_parser(
        "log-processing", help="Manage log processing pipelines"
    )
    log_processing_subparsers = log_processing_parser.add_subparsers(
        dest="log_processing_command", help="Log processing command"
    )
    log_processing_parser.set_defaults(
        func=lambda args, _: log_processing_parser.print_help()
    )

    # List pipelines command
    list_parser = log_processing_subparsers.add_parser(
        "list", help="List log processing pipelines"
    )
    list_parser.add_argument(
        "--page-size",
        "--page_size",
        dest="page_size",
        type=int,
        help="Maximum number of pipelines to return",
    )
    list_parser.add_argument(
        "--page-token",
        "--page_token",
        dest="page_token",
        help="Page token for pagination",
    )
    list_parser.add_argument(
        "--filter", help="Filter expression to restrict results"
    )
    list_parser.set_defaults(func=handle_list_command)

    # Get pipeline command
    get_parser = log_processing_subparsers.add_parser(
        "get", help="Get a log processing pipeline"
    )
    get_parser.add_argument("--id", required=True, help="Pipeline ID")
    get_parser.set_defaults(func=handle_get_command)

    # Create pipeline command
    create_parser = log_processing_subparsers.add_parser(
        "create", help="Create a log processing pipeline"
    )
    create_parser.add_argument(
        "--pipeline",
        required=True,
        help="Pipeline config as JSON string or file path",
    )
    create_parser.add_argument("--id", help="Optional pipeline ID")
    create_parser.set_defaults(func=handle_create_command)

    # Update pipeline command
    update_parser = log_processing_subparsers.add_parser(
        "update", help="Update a log processing pipeline"
    )
    update_parser.add_argument("--id", required=True, help="Pipeline ID")
    update_parser.add_argument(
        "--pipeline",
        required=True,
        help="Pipeline config as JSON string or file path",
    )
    update_parser.add_argument(
        "--update-mask",
        "--update_mask",
        dest="update_mask",
        help="Comma-separated list of fields to update",
    )
    update_parser.set_defaults(func=handle_update_command)

    # Delete pipeline command
    delete_parser = log_processing_subparsers.add_parser(
        "delete", help="Delete a log processing pipeline"
    )
    delete_parser.add_argument("--id", required=True, help="Pipeline ID")
    delete_parser.add_argument(
        "--etag", help="Optional etag for concurrency control"
    )
    delete_parser.set_defaults(func=handle_delete_command)

    # Associate streams command
    associate_streams_parser = log_processing_subparsers.add_parser(
        "associate-streams", help="Associate streams with a pipeline"
    )
    associate_streams_parser.add_argument(
        "--id", required=True, help="Pipeline ID"
    )
    associate_streams_parser.add_argument(
        "--streams",
        required=True,
        help="JSON array of stream objects or file path",
    )
    associate_streams_parser.set_defaults(func=handle_associate_streams_command)

    # Dissociate streams command
    dissociate_streams_parser = log_processing_subparsers.add_parser(
        "dissociate-streams", help="Dissociate streams from a pipeline"
    )
    dissociate_streams_parser.add_argument(
        "--id", required=True, help="Pipeline ID"
    )
    dissociate_streams_parser.add_argument(
        "--streams",
        required=True,
        help="JSON array of stream objects or file path",
    )
    dissociate_streams_parser.set_defaults(
        func=handle_dissociate_streams_command
    )

    # Fetch associated pipeline command
    fetch_associated_parser = log_processing_subparsers.add_parser(
        "fetch-associated", help="Fetch pipeline associated with a stream"
    )
    fetch_associated_parser.add_argument(
        "--stream",
        required=True,
        help="Stream object as JSON string or file path",
    )
    fetch_associated_parser.set_defaults(func=handle_fetch_associated_command)

    # Fetch sample logs command
    fetch_sample_logs_parser = log_processing_subparsers.add_parser(
        "fetch-sample-logs", help="Fetch sample logs by streams"
    )
    fetch_sample_logs_parser.add_argument(
        "--streams",
        required=True,
        help="JSON array of stream objects or file path",
    )
    fetch_sample_logs_parser.add_argument(
        "--count", type=int, help="Number of sample logs per stream (max 1000)"
    )
    fetch_sample_logs_parser.set_defaults(func=handle_fetch_sample_logs_command)

    # Test pipeline command
    test_parser = log_processing_subparsers.add_parser(
        "test", help="Test a pipeline with input logs"
    )
    test_parser.add_argument(
        "--pipeline",
        required=True,
        help="Pipeline config as JSON or file path",
    )
    test_parser.add_argument(
        "--input-logs",
        "--input_logs",
        dest="input_logs",
        required=True,
        help="Input logs as JSON array or file path",
    )
    test_parser.set_defaults(func=handle_test_command)


def handle_list_command(args, chronicle):
    """Handle list log processing pipelines command."""
    try:
        result = chronicle.list_log_processing_pipelines(
            page_size=args.page_size,
            page_token=args.page_token,
            filter_expr=args.filter,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get_command(args, chronicle):
    """Handle get log processing pipeline command."""
    try:
        result = chronicle.get_log_processing_pipeline(args.id)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_create_command(args, chronicle):
    """Handle create log processing pipeline command."""
    try:
        pipeline_config = load_json_or_file(args.pipeline)

        if not isinstance(pipeline_config, dict):
            print("Error: pipeline must be a JSON object", file=sys.stderr)
            sys.exit(1)

        result = chronicle.create_log_processing_pipeline(
            pipeline=pipeline_config, pipeline_id=args.id
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_update_command(args, chronicle):
    """Handle update log processing pipeline command."""
    try:
        pipeline_config = load_json_or_file(args.pipeline)

        if not isinstance(pipeline_config, dict):
            print("Error: pipeline must be a JSON object", file=sys.stderr)
            sys.exit(1)

        result = chronicle.update_log_processing_pipeline(
            pipeline_id=args.id,
            pipeline=pipeline_config,
            update_mask=args.update_mask,
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_delete_command(args, chronicle):
    """Handle delete log processing pipeline command."""
    try:
        result = chronicle.delete_log_processing_pipeline(
            pipeline_id=args.id, etag=args.etag
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_associate_streams_command(args, chronicle):
    """Handle associate streams command."""
    try:
        streams = load_json_or_file(args.streams)

        if not isinstance(streams, list):
            print("Error: streams must be a JSON array", file=sys.stderr)
            sys.exit(1)

        result = chronicle.associate_streams(
            pipeline_id=args.id, streams=streams
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_dissociate_streams_command(args, chronicle):
    """Handle dissociate streams command."""
    try:
        streams = load_json_or_file(args.streams)

        if not isinstance(streams, list):
            print("Error: streams must be a JSON array", file=sys.stderr)
            sys.exit(1)

        result = chronicle.dissociate_streams(
            pipeline_id=args.id, streams=streams
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_fetch_associated_command(args, chronicle):
    """Handle fetch associated pipeline command."""
    try:
        stream = load_json_or_file(args.stream)

        if not isinstance(stream, dict):
            print("Error: stream must be a JSON object", file=sys.stderr)
            sys.exit(1)

        result = chronicle.fetch_associated_pipeline(stream=stream)
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_fetch_sample_logs_command(args, chronicle):
    """Handle fetch sample logs by streams command."""
    try:
        streams = load_json_or_file(args.streams)

        if not isinstance(streams, list):
            print("Error: streams must be a JSON array", file=sys.stderr)
            sys.exit(1)

        result = chronicle.fetch_sample_logs_by_streams(
            streams=streams, sample_logs_count=args.count
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_test_command(args, chronicle):
    """Handle test pipeline command."""
    try:
        pipeline = load_json_or_file(args.pipeline)
        input_logs = load_json_or_file(args.input_logs)

        if not isinstance(pipeline, dict):
            print("Error: pipeline must be a JSON object", file=sys.stderr)
            sys.exit(1)

        if not isinstance(input_logs, list):
            print("Error: input_logs must be a JSON array", file=sys.stderr)
            sys.exit(1)

        result = chronicle.test_pipeline(
            pipeline=pipeline, input_logs=input_logs
        )
        output_formatter(result, args.output)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
