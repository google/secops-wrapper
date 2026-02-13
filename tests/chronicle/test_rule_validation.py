"""Tests for Chronicle rule validation functions."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from secops.chronicle.models import APIVersion
from secops.chronicle.rule_validation import ValidationResult, validate_rule
from secops.exceptions import APIError


@pytest.fixture
def client() -> Mock:
    return Mock()


def test_validate_rule_success(client: Mock) -> None:
    rule_text = """
    rule test_rule {
        meta:
            author = "test"
        events:
            $e.metadata.event_type = "NETWORK_CONNECTION"
        condition:
            $e
    }
    """

    with patch(
        "secops.chronicle.rule_validation.chronicle_request",
        return_value={"success": True},
    ) as req:
        result = validate_rule(client, rule_text)

    assert result == ValidationResult(success=True, message=None, position=None)

    req.assert_called_once()
    _, kwargs = req.call_args

    assert kwargs["method"] == "POST"
    assert kwargs["endpoint_path"] == ":verifyRuleText"
    assert kwargs["api_version"] == APIVersion.V1ALPHA

    # Verify rule text cleanup happened (strip backticks/whitespace)
    body = kwargs["json"]
    assert "rule test_rule" in body["ruleText"]
    assert not body["ruleText"].startswith("`")
    assert not body["ruleText"].endswith("`")


def test_validate_rule_error_without_position(client: Mock) -> None:
    with patch(
        "secops.chronicle.rule_validation.chronicle_request",
        return_value={
            "success": False,
            "compilationDiagnostics": [
                {
                    "message": "semantic analysis: something went wrong",
                    "severity": "ERROR",
                }
            ],
        },
    ):
        result = validate_rule(client, "invalid rule")

    assert result.success is False
    assert "semantic analysis" in (result.message or "")
    assert result.position is None


def test_validate_rule_error_with_position(client: Mock) -> None:
    with patch(
        "secops.chronicle.rule_validation.chronicle_request",
        return_value={
            "success": False,
            "compilationDiagnostics": [
                {
                    "message": 'parsing: error with token: "+"',
                    "position": {
                        "startLine": 27,
                        "startColumn": 8,
                        "endLine": 27,
                        "endColumn": 9,
                    },
                    "severity": "ERROR",
                }
            ],
        },
    ):
        result = validate_rule(client, "invalid rule with position")

    assert result.success is False
    assert "parsing: error with token" in (result.message or "")
    assert result.position == {
        "startLine": 27,
        "startColumn": 8,
        "endLine": 27,
        "endColumn": 9,
    }


def test_validate_rule_unknown_error_when_no_diagnostics(client: Mock) -> None:
    with patch(
        "secops.chronicle.rule_validation.chronicle_request",
        return_value={"success": False, "compilationDiagnostics": []},
    ):
        result = validate_rule(client, "invalid rule")

    assert result.success is False
    assert result.message == "Unknown validation error"
    assert result.position is None


def test_validate_rule_propagates_api_error(client: Mock) -> None:
    with patch(
        "secops.chronicle.rule_validation.chronicle_request",
        side_effect=APIError("API request failed: boom"),
    ):
        with pytest.raises(APIError, match=r"API request failed: boom"):
            validate_rule(client, "rule text")
