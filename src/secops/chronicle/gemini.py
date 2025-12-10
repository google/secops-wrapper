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
"""Chronicle Gemini API interaction module.

Provides access to Chronicle's Gemini conversational AI interface.
"""
import re
from typing import Any

from secops.exceptions import APIError


class Block:
    """Represents a block in the Gemini response.

    Blocks are discrete chunks of content with different types
    (text, code, HTML, etc.) returned in a Gemini conversation response.
    """

    def __init__(self, block_type: str, content: str, title: str | None = None):
        """Initialize a response block.

        Args:
            block_type: The type of the block ('TEXT', 'CODE', 'HTML', etc.)
            content: The content of the block
            title: Optional title for the block (may be present in CODE blocks)
        """
        self.block_type = block_type
        self.content = content
        self.title = title

    def __repr__(self) -> str:
        """Return string representation of the block.

        Returns:
            String representation of the block with its type
            and title if present
        """
        if self.title:
            return f"Block(type={self.block_type}, title={self.title})"
        return f"Block(type={self.block_type})"


class NavigationAction:
    """Represents a navigation action for a suggested action."""

    def __init__(self, target_uri: str):
        """Initialize a navigation action.

        Args:
            target_uri: The target URI for the navigation action
        """
        self.target_uri = target_uri

    def __repr__(self) -> str:
        """Return string representation of the navigation action.

        Returns:
            String representation with the target URI
        """
        return f"NavigationAction(target_uri={self.target_uri})"


class SuggestedAction:
    """Represents a suggested action in the Gemini response."""

    def __init__(
        self,
        display_text: str,
        action_type: str,
        use_case_id: str | None = None,
        navigation: NavigationAction | None = None,
    ):
        """Initialize a suggested action.

        Args:
            display_text: The text to display for the action
            action_type: The type of action (e.g., 'NAVIGATION')
            use_case_id: Optional ID for the use case
            navigation: Optional navigation object for NAVIGATION type actions
        """
        self.display_text = display_text
        self.action_type = action_type
        self.use_case_id = use_case_id
        self.navigation = navigation

    def __repr__(self) -> str:
        """Return string representation of the suggested action.

        Returns:
            String representation with action type and display text
        """
        return (
            f"SuggestedAction(type={self.action_type}, "
            f"text={self.display_text})"
        )


class GeminiResponse:
    """Represents a complete response from the Gemini API."""

    def __init__(
        self,
        name: str,
        input_query: str,
        create_time: str,
        blocks: list[Block],
        suggested_actions: list[SuggestedAction] | None = None,
        references: list[Block] | None = None,
        groundings: list[str] | None = None,
        raw_response: dict[str, Any] | None = None,
    ):
        """Initialize a Gemini response.

        Args:
            name: The name of the message (full resource path)
            input_query: The original query that was sent
            create_time: The time when the response was created
            blocks: List of content blocks in the response
            suggested_actions: Optional list of suggested actions
            references: Optional list of reference blocks
            groundings: Optional list of grounding texts
            raw_response: Optional raw API response for debugging
        """
        self.name = name
        self.input_query = input_query
        self.create_time = create_time
        self.blocks = blocks
        self.suggested_actions = suggested_actions or []
        self.references = references or []
        self.groundings = groundings or []
        self.raw_response = raw_response

    def __repr__(self) -> str:
        """Return string representation of the Gemini response.

        Returns:
            String representation with key details
        """
        return (
            f"GeminiResponse(blocks={len(self.blocks)}, "
            f"actions={len(self.suggested_actions)})"
        )

    @classmethod
    def from_api_response(cls, response: dict[str, Any]) -> "GeminiResponse":
        """Create a GeminiResponse object from an API response.

        Args:
            response: The raw API response dictionary

        Returns:
            A GeminiResponse object
        """
        # Extract the key elements from the API response
        name = response.get("name", "")
        create_time = response.get("createTime", "")
        input_data = response.get("input", {})
        input_query = input_data.get("body", "") if input_data else ""

        blocks = []
        suggested_actions = []
        references = []
        groundings = []

        # Process the response blocks
        for resp in response.get("responses", []):
            # Process content blocks
            for block_data in resp.get("blocks", []):
                block_type = block_data.get("blockType", "")
                content = ""

                # Handle different content types
                if block_type == "TEXT":
                    content = block_data.get("content", "")
                elif block_type == "CODE":
                    content = block_data.get("content", "")
                elif block_type == "HTML":
                    # Extract HTML content from the wrapper
                    html_content = block_data.get("htmlContent", {})
                    content = html_content.get(
                        "privateDoNotAccessOrElseSafeHtmlWrappedValue", ""
                    )

                blocks.append(
                    Block(
                        block_type=block_type,
                        content=content,
                        title=block_data.get("title", None),
                    )
                )

            # Process reference blocks (which also have blocks inside)
            for ref_data in resp.get("references", []):
                ref_block_type = ref_data.get("blockType", "")
                ref_content = ""

                if ref_block_type == "HTML":
                    html_content = ref_data.get("htmlContent", {})
                    ref_content = html_content.get(
                        "privateDoNotAccessOrElseSafeHtmlWrappedValue", ""
                    )

                references.append(
                    Block(block_type=ref_block_type, content=ref_content)
                )

            # Process groundings
            groundings.extend(resp.get("groundings", []))

            # Process suggested actions
            for action_data in resp.get("suggestedActions", []):
                navigation = None
                if "navigation" in action_data:
                    navigation = NavigationAction(
                        target_uri=action_data["navigation"].get(
                            "targetUri", ""
                        )
                    )

                suggested_actions.append(
                    SuggestedAction(
                        display_text=action_data.get("displayText", ""),
                        action_type=action_data.get("actionType", ""),
                        use_case_id=action_data.get("useCaseId", ""),
                        navigation=navigation,
                    )
                )

        return cls(
            name=name,
            input_query=input_query,
            create_time=create_time,
            blocks=blocks,
            suggested_actions=suggested_actions,
            references=references,
            groundings=groundings,
            raw_response=response,
        )

    def get_text_content(self) -> str:
        """Get concatenated content from all TEXT and HTML blocks.

        For HTML blocks, HTML tags are stripped to extract just
        the text content.

        Returns:
            A string with all text content concatenated
        """

        # Function to strip HTML tags
        def strip_html_tags(html_content):
            # Remove HTML tags
            text = re.sub(r"<[^>]+>", " ", html_content)
            # Replace multiple spaces with single space
            text = re.sub(r"\s+", " ", text)
            # Remove leading/trailing whitespace
            return text.strip()

        # Collect text from TEXT blocks
        text_content = [
            block.content for block in self.blocks if block.block_type == "TEXT"
        ]

        # Add stripped text from HTML blocks
        html_content = [
            strip_html_tags(block.content)
            for block in self.blocks
            if block.block_type == "HTML"
        ]

        # Combine all content
        all_content = text_content + html_content

        return "\n\n".join(all_content) if all_content else ""

    def get_code_blocks(self) -> list[Block]:
        """Get all CODE blocks.

        Returns:
            A list of Block objects with block_type == "CODE"
        """
        return [block for block in self.blocks if block.block_type == "CODE"]

    def get_html_blocks(self) -> list[Block]:
        """Get all HTML blocks.

        Returns:
            A list of Block objects with block_type == "HTML"
        """
        return [block for block in self.blocks if block.block_type == "HTML"]

    def get_raw_response(self) -> dict[str, Any]:
        """Get the raw API response as a dictionary.

        This provides access to the complete, unprocessed API response for
        advanced use cases or debugging.

        Returns:
            The raw API response dictionary or an empty dictionary if None
        """
        return self.raw_response or {}


def create_conversation(client, display_name: str = "New chat") -> str:
    """Create a new conversation in Chronicle Gemini.

    Args:
        client: The Chronicle client instance
        display_name: Display name for the conversation

    Returns:
        The conversation ID

    Raises:
        APIError: If the API request fails
    """
    url = (
        f"{client.base_url}/projects/{client.project_id}/locations/"
        f"{client.region}/instances/{client.customer_id}/users/me/conversations"
    )

    # Include the required request body with displayName
    payload = {"displayName": display_name}

    try:
        response = client.session.post(url, json=payload)
        response.raise_for_status()
        conversation_data = response.json()

        # Extract conversation ID from the name field (last part of the path)
        conversation_id = conversation_data.get("name", "").split("/")[-1]
        return conversation_id

    except Exception as e:
        error_message = f"Failed to create conversation: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            error_message += (
                f" - Status: {e.response.status_code}, Body: {e.response.text}"
            )
        raise APIError(error_message) from e


def opt_in_to_gemini(client) -> bool:
    """Opt the user into Gemini (Duet AI) in Chronicle.

    This function updates the user's preferences to enable Duet AI chat,
    which is required before using the Gemini functionality.

    Args:
        client: The Chronicle client instance

    Returns:
        True if successful, False otherwise

    Raises:
        APIError: If the API request fails (except for permission errors)
    """
    # Construct the URL for updating the user's preference set
    url = (
        f"{client.base_url}/projects/{client.project_id}/locations/"
        f"{client.region}/instances/{client.customer_id}/users/me/preferenceSet"
    )

    # Set up the request body to enable Duet AI chat
    payload = {"ui_preferences": {"enable_duet_ai_chat": True}}

    # Set the update mask to only update the specific field
    params = {"updateMask": "ui_preferences.enable_duet_ai_chat"}

    try:
        response = client.session.patch(url, json=payload, params=params)
        response.raise_for_status()
        return True
    except Exception as e:
        # For permission errors, we'll log but not raise to allow
        # graceful fallback
        if (
            hasattr(e, "response")
            and e.response is not None
            and e.response.status_code in [403, 401]
        ):
            error_message = (
                f"Unable to opt in to Gemini due to permissions: {str(e)}"
            )
            print(f"Warning: {error_message}")
            return False

        # For other errors, raise so the calling function can handle
        # appropriately
        error_message = f"Failed to opt in to Gemini: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            error_message += (
                f" - Status: {e.response.status_code}, Body: {e.response.text}"
            )
        raise APIError(error_message) from e


def query_gemini(
    client,
    query: str,
    conversation_id: str | None = None,
    context_uri: str = "/search",
    context_body: dict[str, Any] | None = None,
    attempt_opt_in: bool = True,
) -> GeminiResponse:
    """Query Chronicle Gemini with a prompt.

    Args:
        client: The Chronicle client instance
        query: The text query to send to Gemini
        conversation_id: Optional conversation ID. If not provided,
            a new conversation will be created
        context_uri: URI context for the query (default: "/search")
        context_body: Optional additional context as a dictionary
        attempt_opt_in: Whether to attempt to opt-in to Gemini
            if the request fails due to opt-in requirements

    Returns:
        A GeminiResponse object with the structured response

    Raises:
        APIError: If the API request fails
    """
    # Check if the client has a flag tracking if we've attempted opt-in
    # If not, add this attribute to the client instance
    if not hasattr(client, "_gemini_opt_in_attempted"):
        client._gemini_opt_in_attempted = (  # pylint: disable=protected-access
            False
        )

    try:
        # Create a new conversation if one wasn't provided
        if not conversation_id:
            conversation_id = create_conversation(client)

        url = (
            f"{client.base_url}/projects/{client.project_id}/locations/"
            f"{client.region}/instances/{client.customer_id}/users/me/"
            f"conversations/{conversation_id}/messages"
        )

        payload = {
            "input": {
                "body": query,
                "context": {"uri": context_uri, "body": context_body or {}},
            }
        }

        response = client.session.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()

        return GeminiResponse.from_api_response(response_data)

    except Exception as e:
        error_message = f"Failed to query Gemini: {str(e)}"
        error_response_body = ""

        if hasattr(e, "response") and e.response is not None:
            error_response_body = e.response.text
            error_message += (
                f" - Status: {e.response.status_code}, "
                f"Body: {error_response_body}"
            )

        # Check if this is an opt-in required error and
        # we haven't tried to opt-in yet
        if (
            attempt_opt_in
            and not client._gemini_opt_in_attempted  # pylint: disable=protected-access
            and "opt-in" in error_message.lower()
            or (
                "error_response_body"
                and "users must opt-in before using Gemini"
                in error_response_body
            )
        ):

            # Mark that we've attempted opt-in to avoid infinite loops
            client._gemini_opt_in_attempted = (  # pylint: disable=protected-access
                True
            )

            # Try to opt in
            successful = opt_in_to_gemini(client)

            if successful:
                # Try the query again with attempt_opt_in=False to
                # avoid recursion
                return query_gemini(
                    client,
                    query,
                    conversation_id,
                    context_uri,
                    context_body,
                    attempt_opt_in=False,  # Prevent infinite recursion
                )

        # If we get here, either the error wasn't an opt-in error,
        # opt-in failed, or this is our second attempt after trying to opt-in.
        raise APIError(error_message) from e
