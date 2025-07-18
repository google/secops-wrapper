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
"""Unit tests for Chronicle Gemini API."""
import pytest
from unittest.mock import Mock, patch
from secops.chronicle.gemini import (
    Block,
    NavigationAction,
    SuggestedAction,
    GeminiResponse,
    create_conversation,
    query_gemini,
    opt_in_to_gemini,
)
from secops.exceptions import APIError
import requests


@pytest.fixture
def mock_chronicle_client():
    """Create a mock Chronicle client."""
    client = Mock()
    client.project_id = "test-project"
    client.customer_id = "test-customer"
    client.region = "us"
    client.base_url = "https://us-chronicle.googleapis.com/v1alpha"
    client.session = Mock()
    return client


@pytest.fixture
def sample_gemini_response():
    """Create a sample Gemini API response for testing."""
    return {
        "name": "projects/test-project/locations/us/instances/test-customer/users/me/conversations/test-conv/messages/test-message",
        "input": {
            "body": "What is Windows event ID 4625?",
            "context": {"uri": "/search", "body": {}},
        },
        "responses": [
            {
                "blocks": [
                    {
                        "blockType": "TEXT",
                        "content": "Windows Event ID 4625 signifies a failed logon attempt on a Windows system.",
                    },
                    {
                        "blockType": "CODE",
                        "content": "# Example code to detect failed logon attempts\nrule detect_failed_logons {\n  ...\n}",
                        "title": "Detection Rule",
                    },
                    {
                        "blockType": "HTML",
                        "htmlContent": {
                            "privateDoNotAccessOrElseSafeHtmlWrappedValue": "<p>Additional details about Event ID 4625:</p><ul><li>Item 1</li><li>Item 2</li></ul>"
                        },
                    },
                ],
                "references": [
                    {
                        "blockType": "HTML",
                        "htmlContent": {
                            "privateDoNotAccessOrElseSafeHtmlWrappedValue": '<ol><li><a href="https://example.com">Example reference</a></li></ol>'
                        },
                    }
                ],
                "groundings": ["Windows event ID 4625"],
                "suggestedActions": [
                    {
                        "displayText": "Open in Rule Editor",
                        "actionType": "NAVIGATION",
                        "useCaseId": "test-use-case",
                        "navigation": {"targetUri": "/rulesEditor?rule=example"},
                    }
                ],
            }
        ],
        "createTime": "2025-04-11T12:59:18.269363Z",
    }


def test_block_init():
    """Test Block class initialization."""
    block = Block("TEXT", "Some content", "Optional title")
    assert block.block_type == "TEXT"
    assert block.content == "Some content"
    assert block.title == "Optional title"


def test_block_repr():
    """Test Block string representation."""
    block1 = Block("TEXT", "Content")
    assert repr(block1) == "Block(type=TEXT)"

    block2 = Block("CODE", "Code content", "Example Code")
    assert repr(block2) == "Block(type=CODE, title=Example Code)"


def test_navigation_action_init():
    """Test NavigationAction class initialization."""
    nav = NavigationAction("/test/uri")
    assert nav.target_uri == "/test/uri"
    assert "target_uri=/test/uri" in repr(nav)


def test_suggested_action_init():
    """Test SuggestedAction class initialization."""
    nav = NavigationAction("/test/uri")
    action = SuggestedAction("Test Action", "NAVIGATION", "test-case", nav)

    assert action.display_text == "Test Action"
    assert action.action_type == "NAVIGATION"
    assert action.use_case_id == "test-case"
    assert action.navigation == nav
    assert "type=NAVIGATION" in repr(action)
    assert "text=Test Action" in repr(action)


def test_gemini_response_init():
    """Test GeminiResponse class initialization."""
    blocks = [Block("TEXT", "Text content"), Block("CODE", "Code content", "Example")]
    actions = [
        SuggestedAction("Action", "NAVIGATION", "test-case", NavigationAction("/uri"))
    ]
    references = [Block("HTML", "<p>Reference</p>")]

    response = GeminiResponse(
        name="test-name",
        input_query="test query",
        create_time="2025-01-01T00:00:00Z",
        blocks=blocks,
        suggested_actions=actions,
        references=references,
        groundings=["test query"],
        raw_response={"raw": "data"},
    )

    assert response.name == "test-name"
    assert response.input_query == "test query"
    assert response.create_time == "2025-01-01T00:00:00Z"
    assert response.blocks == blocks
    assert response.suggested_actions == actions
    assert response.references == references
    assert response.groundings == ["test query"]
    assert response.raw_response == {"raw": "data"}

    # Test with default values
    basic_response = GeminiResponse(
        name="test", input_query="query", create_time="2025-01-01T00:00:00Z", blocks=[]
    )
    assert basic_response.suggested_actions == []
    assert basic_response.references == []
    assert basic_response.groundings == []
    assert basic_response.raw_response is None


def test_gemini_response_from_api_response(sample_gemini_response):
    """Test creating GeminiResponse from API response."""
    response = GeminiResponse.from_api_response(sample_gemini_response)

    # Check basic fields
    assert response.name == sample_gemini_response["name"]
    assert response.input_query == "What is Windows event ID 4625?"
    assert response.create_time == sample_gemini_response["createTime"]

    # Check blocks are properly parsed
    assert len(response.blocks) == 3

    # Text block
    text_block = response.blocks[0]
    assert text_block.block_type == "TEXT"
    assert (
        text_block.content
        == "Windows Event ID 4625 signifies a failed logon attempt on a Windows system."
    )

    # Code block
    code_block = response.blocks[1]
    assert code_block.block_type == "CODE"
    assert "# Example code" in code_block.content
    assert code_block.title == "Detection Rule"

    # HTML block
    html_block = response.blocks[2]
    assert html_block.block_type == "HTML"
    assert "<p>Additional details" in html_block.content

    # Check references
    assert len(response.references) == 1
    assert response.references[0].block_type == "HTML"
    assert "<ol><li><a href=" in response.references[0].content

    # Check groundings
    assert response.groundings == ["Windows event ID 4625"]

    # Check suggested actions
    assert len(response.suggested_actions) == 1
    action = response.suggested_actions[0]
    assert action.display_text == "Open in Rule Editor"
    assert action.action_type == "NAVIGATION"
    assert action.use_case_id == "test-use-case"
    assert action.navigation.target_uri == "/rulesEditor?rule=example"


def test_gemini_response_helper_methods():
    """Test GeminiResponse helper methods."""
    blocks = [
        Block("TEXT", "Text content 1"),
        Block("TEXT", "Text content 2"),
        Block("CODE", "Code content", "Example"),
        Block("HTML", "<p>HTML <strong>formatted</strong> content</p>"),
    ]

    response = GeminiResponse(
        name="test",
        input_query="query",
        create_time="2025-01-01T00:00:00Z",
        blocks=blocks,
    )

    # Test get_text_content (should include both TEXT and stripped HTML content)
    text_content = response.get_text_content()
    assert "Text content 1" in text_content
    assert "Text content 2" in text_content
    assert "HTML formatted content" in text_content
    assert "<p>" not in text_content  # HTML tags should be stripped
    assert "<strong>" not in text_content  # HTML tags should be stripped

    # Test get_code_blocks
    code_blocks = response.get_code_blocks()
    assert len(code_blocks) == 1
    assert code_blocks[0].content == "Code content"

    # Test get_html_blocks
    html_blocks = response.get_html_blocks()
    assert len(html_blocks) == 1
    assert html_blocks[0].content == "<p>HTML <strong>formatted</strong> content</p>"

    # Test get_raw_response
    raw_data = {"test": "data"}
    response_with_raw = GeminiResponse(
        name="test",
        input_query="query",
        create_time="2025-01-01T00:00:00Z",
        blocks=[],
        raw_response=raw_data,
    )
    assert response_with_raw.get_raw_response() == raw_data


def test_create_conversation_success(mock_chronicle_client):
    """Test successful conversation creation."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/users/me/conversations/test-conv-id",
        "displayName": "Test Chat",
        "createTime": "2025-01-01T00:00:00Z",
    }

    mock_chronicle_client.session.post.return_value = mock_response

    # Test with default display name
    conv_id = create_conversation(mock_chronicle_client)
    assert conv_id == "test-conv-id"

    # Check API call
    mock_chronicle_client.session.post.assert_called_once()
    call_args = mock_chronicle_client.session.post.call_args

    # Check URL
    assert (
        call_args[0][0]
        == "https://us-chronicle.googleapis.com/v1alpha/projects/test-project/locations/us/instances/test-customer/users/me/conversations"
    )

    # Check payload
    assert call_args[1]["json"] == {"displayName": "New chat"}

    # Test with custom display name
    mock_chronicle_client.session.post.reset_mock()
    conv_id = create_conversation(mock_chronicle_client, "Custom Chat")
    assert conv_id == "test-conv-id"
    assert mock_chronicle_client.session.post.call_args[1]["json"] == {
        "displayName": "Custom Chat"
    }


def test_create_conversation_error(mock_chronicle_client):
    """Test conversation creation error handling."""
    # Simulate a request failure
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")

    mock_chronicle_client.session.post.return_value = mock_response

    with pytest.raises(APIError) as excinfo:
        create_conversation(mock_chronicle_client)

    assert "Failed to create conversation" in str(excinfo.value)


def test_query_gemini_new_conversation(mock_chronicle_client, sample_gemini_response):
    """Test querying Gemini with a new conversation."""
    # Mock create_conversation
    with patch("secops.chronicle.gemini.create_conversation") as mock_create_conv:
        mock_create_conv.return_value = "test-conv-id"

        # Mock the API response
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample_gemini_response
        mock_chronicle_client.session.post.return_value = mock_resp

        # Call the function
        response = query_gemini(
            mock_chronicle_client, query="What is Windows event ID 4625?"
        )

        # Check that create_conversation was called
        mock_create_conv.assert_called_once_with(mock_chronicle_client)

        # Check API call
        mock_chronicle_client.session.post.assert_called_once()
        call_args = mock_chronicle_client.session.post.call_args

        # Check URL
        assert "test-conv-id/messages" in call_args[0][0]

        # Check payload
        payload = call_args[1]["json"]
        assert payload["input"]["body"] == "What is Windows event ID 4625?"
        assert payload["input"]["context"]["uri"] == "/search"

        # Check response
        assert isinstance(response, GeminiResponse)
        assert len(response.blocks) == 3
        assert response.blocks[0].block_type == "TEXT"


def test_query_gemini_existing_conversation(
    mock_chronicle_client, sample_gemini_response
):
    """Test querying Gemini with an existing conversation."""
    # Mock the API response
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = sample_gemini_response
    mock_chronicle_client.session.post.return_value = mock_resp

    # Call the function with an existing conversation ID
    response = query_gemini(
        mock_chronicle_client,
        query="What is Windows event ID 4625?",
        conversation_id="existing-conv-id",
        context_uri="/custom-context",
        context_body={"custom": "data"},
    )

    # Check API call
    mock_chronicle_client.session.post.assert_called_once()
    call_args = mock_chronicle_client.session.post.call_args

    # Check URL contains the existing conversation ID
    assert "existing-conv-id/messages" in call_args[0][0]

    # Check payload contains context
    payload = call_args[1]["json"]
    assert payload["input"]["context"]["uri"] == "/custom-context"
    assert payload["input"]["context"]["body"] == {"custom": "data"}


def test_query_gemini_error(mock_chronicle_client):
    """Test error handling in query_gemini."""
    # Simulate a request failure
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")

    mock_chronicle_client.session.post.return_value = mock_response

    # Mock create_conversation to avoid testing that part
    with patch("secops.chronicle.gemini.create_conversation") as mock_create_conv:
        mock_create_conv.return_value = "test-conv-id"

        with pytest.raises(APIError) as excinfo:
            query_gemini(mock_chronicle_client, "test query")

        assert "Failed to query Gemini" in str(excinfo.value)


def test_opt_in_to_gemini_success(mock_chronicle_client):
    """Test successful Gemini opt-in."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "projects/test-project/locations/us/instances/test-customer/users/me/preferenceSet",
        "ui_preferences": {"enable_duet_ai_chat": True},
    }

    mock_chronicle_client.session.patch.return_value = mock_response

    # Call the function
    result = opt_in_to_gemini(mock_chronicle_client)

    # Verify the result
    assert result is True

    # Verify the API call
    mock_chronicle_client.session.patch.assert_called_once()
    call_args = mock_chronicle_client.session.patch.call_args

    # Check URL
    assert "preferenceSet" in call_args[0][0]

    # Check payload
    assert call_args[1]["json"]["ui_preferences"]["enable_duet_ai_chat"] is True

    # Check update mask parameter
    assert call_args[1]["params"]["updateMask"] == "ui_preferences.enable_duet_ai_chat"


def test_opt_in_to_gemini_permission_error(mock_chronicle_client):
    """Test Gemini opt-in with permission error."""
    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.text = "Permission denied"

    # Simulate a permission error
    error = requests.exceptions.HTTPError("Permission denied")
    error.response = mock_response
    mock_chronicle_client.session.patch.side_effect = error

    # Call the function - should not raise but return False
    result = opt_in_to_gemini(mock_chronicle_client)

    # Verify the result
    assert result is False


def test_opt_in_to_gemini_other_error(mock_chronicle_client):
    """Test Gemini opt-in with other error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"

    # Simulate an error
    error = requests.exceptions.HTTPError("Bad request")
    error.response = mock_response
    mock_chronicle_client.session.patch.side_effect = error

    # Call the function - should raise APIError
    with pytest.raises(APIError) as excinfo:
        opt_in_to_gemini(mock_chronicle_client)

    assert "Failed to opt in to Gemini" in str(excinfo.value)


def test_query_gemini_auto_opt_in(mock_chronicle_client, sample_gemini_response):
    """Test automatic opt-in when querying Gemini."""
    # First create a mock for the conversation creation method
    with patch("secops.chronicle.gemini.create_conversation") as mock_create_conv:
        mock_create_conv.return_value = "test-conv-id"

        # Setup the session post to first fail with an opt-in error, then succeed
        mock_opt_in_response = Mock()
        mock_opt_in_response.status_code = 200
        mock_opt_in_response.json.return_value = {
            "ui_preferences": {"enable_duet_ai_chat": True}
        }

        # First request fails with opt-in error
        first_response = Mock()
        first_response.status_code = 400
        first_response.text = (
            '{"error":{"message":"users must opt-in before using Gemini"}}'
        )
        first_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error", response=first_response
        )

        # Second request succeeds
        second_response = Mock()
        second_response.status_code = 200
        second_response.json.return_value = sample_gemini_response

        # Set up the sequence of responses
        mock_chronicle_client.session.post.side_effect = [
            first_response,
            second_response,
        ]
        mock_chronicle_client.session.patch.return_value = mock_opt_in_response

        # Call the function - this should trigger opt-in and retry
        response = query_gemini(mock_chronicle_client, "What is Windows event ID 4625?")

        # Verify the result is a proper GeminiResponse
        assert isinstance(response, GeminiResponse)
        assert len(response.blocks) == 3

        # Verify opt-in was attempted
        mock_chronicle_client.session.patch.assert_called_once()

        # Verify two POST calls were made (first failed, second succeeded)
        assert mock_chronicle_client.session.post.call_count == 2


def test_query_gemini_opt_in_flag(mock_chronicle_client, sample_gemini_response):
    """Test that the opt-in flag is properly set on the client."""
    # First create a mock for the conversation creation method
    with patch("secops.chronicle.gemini.create_conversation") as mock_create_conv:
        mock_create_conv.return_value = "test-conv-id"

        # Set up responses
        mock_opt_in_response = Mock()
        mock_opt_in_response.status_code = 200
        mock_opt_in_response.json.return_value = {
            "ui_preferences": {"enable_duet_ai_chat": True}
        }

        opt_in_error = Mock()
        opt_in_error.status_code = 400
        opt_in_error.text = (
            '{"error":{"message":"users must opt-in before using Gemini"}}'
        )
        opt_in_error.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error", response=opt_in_error
        )

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = sample_gemini_response

        # First call - opt-in error, then success
        mock_chronicle_client.session.post.side_effect = [
            opt_in_error,
            success_response,
        ]
        mock_chronicle_client.session.patch.return_value = mock_opt_in_response

        # Call the function - this should trigger opt-in and retry
        response1 = query_gemini(mock_chronicle_client, "Test query 1")

        # Verify opt-in was attempted once
        assert mock_chronicle_client.session.patch.call_count == 1

        # Second call - should not trigger opt-in again
        mock_chronicle_client.session.post.side_effect = [success_response]
        mock_chronicle_client.session.patch.reset_mock()

        response2 = query_gemini(mock_chronicle_client, "Test query 2")

        # Verify opt-in was not attempted again
        assert mock_chronicle_client.session.patch.call_count == 0

        # Check that the flag was set on the client
        assert hasattr(mock_chronicle_client, "_gemini_opt_in_attempted")
        assert mock_chronicle_client._gemini_opt_in_attempted is True
