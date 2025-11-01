"""
title: External API Pipe
description: Demonstrates calling external APIs with configuration
requirements: requests
"""

import requests
from pydantic import BaseModel, Field


class Pipe:
    """
    A pipe that calls an external API and returns the response.

    This demonstrates:
    - Using Valves for configuration
    - Making HTTP requests
    - Error handling
    - User-specific configuration with UserValves
    """

    class Valves(BaseModel):
        """Global configuration for the pipe (admin-configurable)."""

        api_url: str = Field(
            default="https://api.example.com/chat",
            description="The API endpoint URL"
        )
        api_key: str = Field(
            default="",
            description="API key for authentication"
        )
        timeout: int = Field(
            default=30,
            description="Request timeout in seconds"
        )

    class UserValves(BaseModel):
        """User-specific configuration."""

        model: str = Field(
            default="gpt-4",
            description="Model to use for API requests"
        )
        temperature: float = Field(
            default=0.7,
            description="Temperature for response generation"
        )

    def __init__(self):
        self.name = "API Caller"
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        """
        Call the external API and return the response.

        Args:
            body: The request body containing messages
            __user__: User information including user valves

        Returns:
            API response or error message
        """
        # Get messages
        messages = body.get("messages", [])
        if not messages:
            return "No messages to process"

        # Get user valves
        user_valves = __user__.get("valves", {})
        model = user_valves.get("model", "gpt-4")
        temperature = user_valves.get("temperature", 0.7)

        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.valves.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            # Make API request
            response = requests.post(
                self.valves.api_url,
                headers=headers,
                json=payload,
                timeout=self.valves.timeout
            )

            response.raise_for_status()

            # Parse response
            data = response.json()
            return data.get("message", "No response from API")

        except requests.exceptions.Timeout:
            return f"Request timed out after {self.valves.timeout} seconds"

        except requests.exceptions.RequestException as e:
            return f"API request failed: {str(e)}"

        except Exception as e:
            return f"Unexpected error: {str(e)}"
