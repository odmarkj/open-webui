"""
title: Sentiment Filter
description: Adds sentiment analysis to chat messages
requirements: textblob
"""

from textblob import TextBlob


class Filter:
    """
    A filter that analyzes message sentiment and adds it as metadata.

    This filter demonstrates:
    - Using external dependencies (textblob)
    - Modifying messages in the inlet
    - Adding metadata to enhance the conversation
    """

    def __init__(self):
        self.name = "Sentiment Analyzer"

    def inlet(self, body: dict, __user__: dict) -> dict:
        """
        Analyze sentiment of incoming messages.

        Args:
            body: The request body
            __user__: User information

        Returns:
            Modified body with sentiment information
        """
        messages = body.get("messages", [])

        for message in messages:
            if message.get("role") == "user":
                content = message.get("content", "")

                try:
                    # Analyze sentiment
                    blob = TextBlob(content)
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity

                    # Determine sentiment label
                    if polarity > 0.1:
                        sentiment = "positive"
                    elif polarity < -0.1:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"

                    # Add sentiment note
                    note = f"\n\n[Sentiment: {sentiment}, Polarity: {polarity:.2f}]"
                    message["content"] = content + note

                except Exception as e:
                    # Fail gracefully
                    print(f"Sentiment analysis error: {e}")

        return body

    def outlet(self, body: dict, __user__: dict) -> dict:
        """
        Process outgoing messages (pass-through in this example).

        Args:
            body: The response body
            __user__: User information

        Returns:
            Unmodified body
        """
        return body
