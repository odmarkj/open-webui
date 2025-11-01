"""
title: Chat Logger
description: Logs chat messages to a file for auditing
requirements: python-dateutil
"""

import logging
from datetime import datetime
from pathlib import Path


class Action:
    """
    An action that logs chat messages to a file.

    This demonstrates:
    - Using the Action function type
    - Asynchronous operations
    - File I/O operations
    - Working with timestamps
    """

    def __init__(self):
        self.name = "Chat Logger"

        # Set up logging
        log_dir = Path("./logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / "chat_messages.log"

        # Configure logger
        self.logger = logging.getLogger("chat_logger")
        self.logger.setLevel(logging.INFO)

        # Create file handler if not already exists
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    async def action(self, body: dict, __user__: dict) -> None:
        """
        Log the chat message.

        Args:
            body: The chat request body
            __user__: User information dictionary
        """
        messages = body.get("messages", [])

        if not messages:
            return

        # Get the last message
        last_message = messages[-1]
        role = last_message.get("role", "unknown")
        content = last_message.get("content", "")

        # Get user info
        user_name = __user__.get("name", "unknown")
        user_email = __user__.get("email", "unknown")

        # Log the message
        self.logger.info(
            f"User: {user_name} ({user_email}) | "
            f"Role: {role} | "
            f"Message: {content[:100]}..."  # Truncate long messages
        )
