"""Unit tests for the SecOps CLI."""

from unittest.mock import patch, MagicMock
from argparse import Namespace
import sys
import inspect
from pathlib import Path
import tempfile

from secops.cli import main, setup_client
from secops.cli.utils.time_utils import parse_datetime, get_time_range
from secops.cli.utils.config_utils import load_config, save_config
from secops.cli.utils.formatters import output_formatter


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
    args = Namespace(
        start_time=None, end_time="2023-01-02T00:00:00Z", time_window=24
    )
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


def test_setup_client(monkeypatch):
    # Uses monkeypatch to mock SecOpsClient and sys.exit
    # If the real SecOpsClient is imported SystemExit may
    # be called during tests

    # Locate the module object that contains setup_client
    setup_mod = inspect.getmodule(setup_client)

    # Fake chronicle object returned by FakeClient.chronicle()
    fake_chronicle = MagicMock(name="Chronicle")

    class FakeClient:
        def __init__(self, service_account_path):
            self.service_account_path = service_account_path

        def chronicle(self, customer_id, project_id, region):
            self.called_with = (customer_id, project_id, region)
            return fake_chronicle

    # Replace all possible references to SecOpsClient
    monkeypatch.setattr("secops.SecOpsClient", FakeClient, raising=False)
    if setup_mod is not None:
        monkeypatch.setattr(
            setup_mod, "SecOpsClient", FakeClient, raising=False
        )

    # Neutralise sys.exit so any lingering call does not kill the test
    monkeypatch.setattr(
        "sys.exit",
        lambda code=0: (_ for _ in ()).throw(RuntimeError(f"sys.exit({code})")),
        raising=False,
    )

    args = Namespace(
        service_account="path/to/service_account.json",
        customer_id="test-customer",
        project_id="test-project",
        region="us",
    )

    client, chronicle = setup_client(args)

    assert isinstance(client, FakeClient)
    assert client.service_account_path == "path/to/service_account.json"
    assert client.called_with == ("test-customer", "test-project", "us")
    assert chronicle is fake_chronicle


def test_main_command_dispatch(monkeypatch):
    # Use monkeypatch to mock sys.exit and argparse behavior

    # Make sys.exit a no-op
    monkeypatch.setattr("sys.exit", lambda code=0: None, raising=False)
    monkeypatch.setattr(
        "argparse.ArgumentParser.error", lambda self, msg: None, raising=False
    )
    monkeypatch.setattr(
        "argparse.ArgumentParser.exit",
        lambda self, status=0, message=None: None,
        raising=False,
    )

    client_mock = MagicMock()
    chronicle_mock = MagicMock()

    # Patch every lookup of setup_client
    import inspect, secops.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "setup_client",
        lambda a: (client_mock, chronicle_mock),
        raising=True,
    )
    main_mod = inspect.getmodule(main)
    if main_mod is not None:
        monkeypatch.setattr(
            main_mod,
            "setup_client",
            lambda a: (client_mock, chronicle_mock),
            raising=False,
        )

    captured = {}

    def fake_handler(a, chronicle):
        captured["args"] = a
        captured["chronicle"] = chronicle

    # Provide all required args
    args = Namespace(
        command="test",
        func=fake_handler,
        service_account="path/to/service.json",
        customer_id="test-customer",
        project_id="test-project",
        region="us",
        output_format="text",
        verbose=False,
    )

    # Force parser to return our Namespace
    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args", lambda self: args, raising=True
    )
    monkeypatch.setattr(sys, "argv", ["secops", "test"])

    main()

    # Verify patched setup_client used
    assert captured["chronicle"] is chronicle_mock
    assert captured["args"] is args


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
        with patch("secops.cli.constants.CONFIG_FILE", config_file):
            save_config(test_config)

            # Load config
            loaded_config = load_config()

            # Verify values
            assert loaded_config.get("start_time") == "2023-01-01T00:00:00Z"
            assert loaded_config.get("end_time") == "2023-01-02T00:00:00Z"
            assert loaded_config.get("time_window") == 48