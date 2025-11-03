"""
title: Score Example Pipe
description: Demonstrates importing from lib/ modules
"""

# Import from shared lib modules
from lib.score import Score
from lib.utils import extract_user_message, format_response


class Pipe:
    """
    Example pipe that demonstrates importing shared modules from lib/.

    This shows how to use custom classes and utilities that are shared
    across multiple functions.
    """

    def __init__(self):
        self.name = "Score Example"
        self.scorer = Score(max_score=10.0)

    def pipe(self, body: dict, __user__: dict) -> dict:
        """
        Rate user messages using the Score class from lib/.

        Args:
            body: Request body
            __user__: User information

        Returns:
            dict: Response with score information
        """
        # Extract the user's message
        user_message = extract_user_message(body)

        if not user_message:
            return format_response("No message to score")

        # Calculate a simple score based on message length
        # (just for demonstration)
        score_value = min(len(user_message.split()) / 10 * 10, 10.0)

        # Add score using the Score class
        self.scorer.add_score("latest", score_value)

        # Get rating
        rating = self.scorer.get_rating(score_value)

        # Build response
        response_text = (
            f"Message score: {score_value:.1f}/10.0\n"
            f"Rating: {rating}\n"
            f"Average score: {self.scorer.get_average():.2f}\n\n"
            f"Your message: {user_message}"
        )

        return format_response(
            response_text,
            metadata={
                "score": score_value,
                "rating": rating,
                "average": self.scorer.get_average()
            }
        )
