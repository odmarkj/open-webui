"""
Example: Score calculation module.

This is an example of a shared module that can be imported by your functions.
"""

from typing import Dict, List


class Score:
    """
    Example class for scoring/rating functionality.

    This demonstrates how to create reusable classes in the lib/ directory
    that can be imported by multiple functions.
    """

    def __init__(self, max_score: float = 100.0):
        """
        Initialize scorer.

        Args:
            max_score: Maximum possible score
        """
        self.max_score = max_score
        self.scores: Dict[str, float] = {}

    def add_score(self, name: str, score: float) -> None:
        """
        Add or update a score.

        Args:
            name: Name/identifier for the score
            score: Score value
        """
        if score < 0 or score > self.max_score:
            raise ValueError(f"Score must be between 0 and {self.max_score}")

        self.scores[name] = score

    def get_score(self, name: str) -> float:
        """
        Get a score by name.

        Args:
            name: Name of the score to retrieve

        Returns:
            float: The score value

        Raises:
            KeyError: If score name not found
        """
        return self.scores[name]

    def get_average(self) -> float:
        """
        Calculate average of all scores.

        Returns:
            float: Average score, or 0.0 if no scores
        """
        if not self.scores:
            return 0.0

        return sum(self.scores.values()) / len(self.scores)

    def get_all_scores(self) -> Dict[str, float]:
        """
        Get all scores.

        Returns:
            dict: Dictionary of all scores
        """
        return self.scores.copy()

    def get_rating(self, score: float = None) -> str:
        """
        Convert a score to a rating.

        Args:
            score: Score to rate (uses average if not provided)

        Returns:
            str: Rating (A, B, C, D, F)
        """
        if score is None:
            score = self.get_average()

        percentage = (score / self.max_score) * 100

        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

    def __repr__(self) -> str:
        avg = self.get_average()
        return f"Score(average={avg:.2f}, rating={self.get_rating(avg)})"
