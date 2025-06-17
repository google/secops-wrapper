"""Unit tests for the SecOps CLI."""

import pytest
import json
from unittest.mock import patch, MagicMock
from argparse import Namespace
from datetime import datetime, timezone
import sys
from pathlib import Path
import tempfile

from secops.cli import (
    main,
    parse_datetime,
    setup_client,
    get_time_range,
    output_formatter,
    load_config,
    save_config,
)


def test_parse_datetime():
    """Test datetime parsing."""
    # Test with Z format
    dt_str = "2023-01-01T12:00:00Z"
    result = parse_datetime(dt_str)
    assert result.year == 2023
    assert result.month == 1
    assert result.day == 1
    assert result.hour == 12
    assert result.minute == 0
    assert result.second == 0
    assert result.tzinfo is not None

    # Test with +00:00 format
    dt_str = "2023-01-01T12:00:00+00:00"
    result = parse_datetime(dt_str)
    assert result.year == 2023
    assert result.tzinfo is not None

    # Test with None
    assert parse_datetime(None) is None


def test_get_time_range():
    """Test time range calculation."""
    # Test with explicit start and end time
    args = Namespace(
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z",
        time_window=24,
    )
    start_time, end_time = get_time_range(args)
    assert start_time.day == 1
    assert end_time.day == 2

    # Test with just end time and default window
    args = Namespace(start_time=None, end_time="2023-01-02T00:00:00Z", time_window=24)
    start_time, end_time = get_time_range(args)
    assert start_time.day == 1  # 24 hours before end_time
    assert end_time.day == 2


@patch("sys.stdout")
def test_output_formatter_json(mock_stdout):
    """Test JSON output formatting."""
    data = {"key": "value", "list": [1, 2, 3]}
    with patch("json.dumps") as mock_dumps:
        mock_dumps.return_value = '{"key": "value", "list": [1, 2, 3]}'
        output_formatter(data, "json")
        mock_dumps.assert_called_once()


@patch("builtins.print")
def test_output_formatter_text(mock_print):
    """Test text output formatting."""
    # Test with dict
    data = {"key1": "value1", "key2": "value2"}
    output_formatter(data, "text")
    assert mock_print.call_count == 2

    # Test with list
    mock_print.reset_mock()
    data = ["item1", "item2"]
    output_formatter(data, "text")
    assert mock_print.call_count == 2

    # Test with scalar
    mock_print.reset_mock()
    data = "simple string"
    output_formatter(data, "text")
    mock_print.assert_called_once_with("simple string")


@patch("secops.cli.SecOpsClient")
def test_setup_client(mock_client_class):
    """Test client setup."""
    mock_client = MagicMock()
    mock_chronicle = MagicMock()
    mock_client.chronicle.return_value = mock_chronicle
    mock_client_class.return_value = mock_client

    # Test with service account and Chronicle args
    args = Namespace(
        service_account="path/to/service_account.json",
        customer_id="test-customer",
        project_id="test-project",
        region="us",
    )

    client, chronicle = setup_client(args)

    mock_client_class.assert_called_once_with(
        service_account_path="path/to/service_account.json"
    )
    mock_client.chronicle.assert_called_once_with(
        customer_id="test-customer", project_id="test-project", region="us"
    )
    assert client == mock_client
    assert chronicle == mock_chronicle


@patch("secops.cli.setup_client")
@patch("argparse.ArgumentParser.parse_args")
def test_main_command_dispatch(mock_parse_args, mock_setup_client):
    """Test main function command dispatch."""
    # Mock command handler
    mock_handler = MagicMock()

    # Set up args
    args = Namespace(command="test", func=mock_handler)
    mock_parse_args.return_value = args

    # Mock client setup
    mock_client = MagicMock()
    mock_chronicle = MagicMock()
    mock_setup_client.return_value = (mock_client, mock_chronicle)

    # Call main
    with patch.object(sys, "argv", ["secops", "test"]):
        main()

    # Verify handler was called
    mock_handler.assert_called_once_with(args, mock_chronicle)


def test_time_config():
    """Test saving and loading time-related configuration."""
    # Create temp directory for config file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.json"

        # Test data
        test_config = {
            "customer_id": "test-customer",
            "start_time": "2023-01-01T00:00:00Z",
            "end_time": "2023-01-02T00:00:00Z",
            "time_window": 48,
        }

        # Save config
        with patch("secops.cli.CONFIG_FILE", config_file):
            save_config(test_config)

            # Load config
            loaded_config = load_config()

            # Verify values
            assert loaded_config.get("start_time") == "2023-01-01T00:00:00Z"
            assert loaded_config.get("end_time") == "2023-01-02T00:00:00Z"
            assert loaded_config.get("time_window") == 48
