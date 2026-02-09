"""Tests for Chronicle retrohunt functionality."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from secops.chronicle.models import APIVersion
from secops.chronicle.rule_retrohunt import (
    create_retrohunt,
    get_retrohunt,
    list_retrohunts,
)


@pytest.fixture
def client() -> Mock:
    return Mock()


def test_create_retrohunt_calls_chronicle_request(client: Mock) -> None:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)

    expected = {"name": "operations/op_123"}

    with patch(
        "secops.chronicle.rule_retrohunt.chronicle_request",
        return_value=expected,
    ) as req:
        result = create_retrohunt(
            client=client,
            rule_id="ru_abc123",
            start_time=start,
            end_time=end,
        )

    assert result == expected

    req.assert_called_once()
    _, kwargs = req.call_args

    assert kwargs["method"] == "POST"
    assert kwargs["endpoint_path"] == "rules/ru_abc123/retrohunts"
    assert kwargs["api_version"] == APIVersion.V1

    body = kwargs["json"]
    assert body["process_interval"]["start_time"] == start.isoformat()
    assert body["process_interval"]["end_time"] == end.isoformat()


def test_get_retrohunt_calls_chronicle_request(client: Mock) -> None:
    expected = {
        "name": "operations/op_123",
        "done": False,
    }

    with patch(
        "secops.chronicle.rule_retrohunt.chronicle_request",
        return_value=expected,
    ) as req:
        result = get_retrohunt(
            client=client,
            rule_id="ru_abc123",
            operation_id="op_123",
        )

    assert result == expected

    req.assert_called_once()
    _, kwargs = req.call_args

    assert kwargs["method"] == "GET"
    assert kwargs["endpoint_path"] == "rules/ru_abc123/retrohunts/op_123"
    assert kwargs["api_version"] == APIVersion.V1


def test_list_retrohunts_dict_response(client: Mock) -> None:
    expected = {
        "retrohunts": [{"name": "rh1"}, {"name": "rh2"}],
        "nextPageToken": "token123",
    }

    with patch(
        "secops.chronicle.rule_retrohunt.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        result = list_retrohunts(
            client=client,
            rule_id="ru_abc123",
            page_size=50,
            page_token="token123",
        )

    assert result == expected

    paged.assert_called_once()
    _, kwargs = paged.call_args

    assert kwargs["api_version"] == APIVersion.V1
    assert kwargs["path"] == "rules/ru_abc123/retrohunts"
    assert kwargs["items_key"] == "retrohunts"
    assert kwargs["page_size"] == 50
    assert kwargs["page_token"] == "token123"
    assert kwargs["as_list"] is False


def test_list_retrohunts_list_response(client: Mock) -> None:
    expected = [{"name": "rh1"}, {"name": "rh2"}]

    with patch(
        "secops.chronicle.rule_retrohunt.chronicle_paginated_request",
        return_value=expected,
    ) as paged:
        result = list_retrohunts(
            client=client,
            rule_id="ru_abc123",
            as_list=True,
        )

    assert result == expected

    paged.assert_called_once()
    _, kwargs = paged.call_args

    assert kwargs["path"] == "rules/ru_abc123/retrohunts"
    assert kwargs["items_key"] == "retrohunts"
    assert kwargs["as_list"] is True


def test_list_retrohunts_propagates_api_error(client: Mock) -> None:
    with patch(
        "secops.chronicle.rule_retrohunt.chronicle_paginated_request",
        side_effect=Exception("boom"),
    ):
        with pytest.raises(Exception, match="boom"):
            list_retrohunts(client=client, rule_id="ru_abc123")
