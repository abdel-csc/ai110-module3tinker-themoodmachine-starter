# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

from typing import List, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.
        - Strips leading and trailing whitespace
        - Converts everything to lowercase
        - Splits on spaces
        """
        cleaned = text.strip().lower()
        tokens = cleaned.split()
        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric mood score for the given text.
        Positive words increase the score.
        Negative words decrease the score.
        Handles simple negation: "not happy" flips the score.
        """
        tokens = self.preprocess(text)
        score = 0
        negate = False
        negation_words = {"not", "never", "no",
                          "don't", "doesn't", "isn't", "wasn't"}

        for token in tokens:
            if token in negation_words:
                negate = True
            elif token in self.positive_words:
                score += -1 if negate else 1
                negate = False
            elif token in self.negative_words:
                score += 1 if negate else -1
                negate = False

        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score into a mood label.
          - score >= 2  -> "positive"
          - score <= -2 -> "negative"
          - score == 0  -> "neutral"
          - anything else -> "mixed"
        """
        score = self.score_text(text)

        if score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        else:
            return "neutral"

    # ---------------------------------------------------------------------
    # Explanations
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining why the model chose its label.
        Shows which words counted as positive or negative and the final score.
        Example: 'Score = 2 (positive: ["love", "great"]; negative: [])'
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
