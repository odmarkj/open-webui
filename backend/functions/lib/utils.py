"""
Example: Utility functions for Open WebUI functions.

This module demonstrates reusable utility functions that can be shared
across multiple functions.
"""

from typing import Dict, List, Any
import json
from datetime import datetime


def format_response(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format a response with optional metadata.

    Args:
        content: The main response content
        metadata: Optional metadata to include

    Returns:
        dict: Formatted response
    """
    response = {
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if metadata:
        response["metadata"] = metadata

    return response


def extract_user_message(body: Dict[str, Any]) -> str:
    """
    Extract the last user message from request body.

    Args:
        body: Request body containing messages

    Returns:
        str: Last user message content
    """
    messages = body.get("messages", [])

    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")

    return ""


def get_user_info(user_dict: Dict[str, Any]) -> str:
    """
    Format user information as a string.

    Args:
        user_dict: User dictionary from __user__ parameter

    Returns:
        str: Formatted user info
    """
    name = user_dict.get("name", "Unknown")
    email = user_dict.get("email", "")
    role = user_dict.get("role", "user")

    if email:
        return f"{name} ({email}) [{role}]"
    else:
        return f"{name} [{role}]"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def parse_json_safely(text: str, default: Any = None) -> Any:
    """
    Parse JSON with error handling.

    Args:
        text: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def merge_messages(messages: List[Dict[str, Any]], role: str = "system") -> str:
    """
    Merge all messages of a specific role into one string.

    Args:
        messages: List of message dictionaries
        role: Role to filter by

    Returns:
        str: Combined message content
    """
    filtered = [
        msg.get("content", "")
        for msg in messages
        if msg.get("role") == role
    ]

    return "\n\n".join(filtered)


def count_tokens_estimate(text: str) -> int:
    """
    Rough estimate of token count.

    This is a simple approximation. For accurate counting,
    use a proper tokenizer like tiktoken.

    Args:
        text: Text to count

    Returns:
        int: Estimated token count
    """
    # Very rough: ~4 characters per token on average
    return len(text) // 4


class MessageBuilder:
    """
    Helper class for building message arrays.

    Example:
        builder = MessageBuilder()
        builder.add_system("You are a helpful assistant")
        builder.add_user("Hello!")
        messages = builder.build()
    """

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_system(self, content: str) -> "MessageBuilder":
        """Add a system message."""
        self.messages.append({"role": "system", "content": content})
        return self

    def add_user(self, content: str) -> "MessageBuilder":
        """Add a user message."""
        self.messages.append({"role": "user", "content": content})
        return self

    def add_assistant(self, content: str) -> "MessageBuilder":
        """Add an assistant message."""
        self.messages.append({"role": "assistant", "content": content})
        return self

    def add_message(self, role: str, content: str) -> "MessageBuilder":
        """Add a message with custom role."""
        self.messages.append({"role": role, "content": content})
        return self

    def build(self) -> List[Dict[str, str]]:
        """Build and return the messages list."""
        return self.messages

    def clear(self) -> "MessageBuilder":
        """Clear all messages."""
        self.messages = []
        return self
