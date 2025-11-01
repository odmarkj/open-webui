"""
title: Echo Pipe
description: A simple pipe that echoes back user messages
"""


class Pipe:
    """
    A basic example pipe that demonstrates the Pipe function type.

    This pipe simply returns the last user message, making it useful
    for testing and understanding how pipes work.
    """

    def __init__(self):
        self.name = "Echo"

    def pipe(self, body: dict, __user__: dict) -> str:
        """
        Process the chat request and return the last user message.

        Args:
            body: The request body containing messages and other data
            __user__: User information dictionary

        Returns:
            The content of the last message
        """
        messages = body.get("messages", [])

        if messages:
            last_message = messages[-1]
            content = last_message.get("content", "")
            return f"Echo: {content}"

        return "No message to echo"
