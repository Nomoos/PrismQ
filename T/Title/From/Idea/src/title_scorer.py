"""Title quality scoring for generated titles.

This module handles scoring title variants based on various quality criteria.
Follows Single Responsibility Principle - only responsible for title evaluation.
"""

from dataclasses import dataclass


@dataclass
class ScoringConfig:
    """Configuration for title scoring.
    
    Attributes:
        ideal_length_min: Minimum length for ideal titles (characters)
        ideal_length_max: Maximum length for ideal titles (characters)
        good_length_min: Minimum length for good titles (characters)
        good_length_max: Maximum length for good titles (characters)
        acceptable_length_max: Maximum acceptable title length (characters)
        ideal_score: Score for titles in ideal length range
        good_score: Score for titles in good length range
        short_score: Score for titles that are too short
        acceptable_score: Score for acceptable but long titles
        long_score: Score for titles that are too long
    """
    
    ideal_length_min: int = 40
    ideal_length_max: int = 60
    good_length_min: int = 35
    good_length_max: int = 65
    acceptable_length_max: int = 70
    ideal_score: float = 0.95
    good_score: float = 0.90
    short_score: float = 0.80
    acceptable_score: float = 0.82
    long_score: float = 0.75


class TitleScorer:
    """Score title quality based on various criteria.
    
    This class evaluates generated titles and assigns quality scores based on
    length, style, and other characteristics. Scores range from 0.0 to 1.0.
    """
    
    def __init__(self, config: ScoringConfig = None):
        """Initialize the title scorer.
        
        Args:
            config: Scoring configuration. Uses defaults if not provided.
        """
        self.config = config or ScoringConfig()
    
    def score_by_length(self, title: str) -> float:
        """Score a title based on its character length.
        
        Titles in the ideal range (40-60 chars) get the highest scores.
        Scores decrease for titles that are too short or too long.
        
        Args:
            title: The title text to score
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        length = len(title)
        
        if self.config.ideal_length_min <= length <= self.config.ideal_length_max:
            return self.config.ideal_score  # Ideal length (40-60 chars)
        elif self.config.good_length_min <= length <= self.config.good_length_max:
            return self.config.good_score  # Good length (35-65 chars)
        elif length < self.config.good_length_min:
            return self.config.short_score  # A bit short
        elif length <= self.config.acceptable_length_max:
            return self.config.acceptable_score  # A bit long but acceptable (66-70 chars)
        else:
            return self.config.long_score  # Too long
    
    def infer_style(self, title: str) -> str:
        """Infer the style of a title based on its characteristics.
        
        Args:
            title: The title text to analyze
            
        Returns:
            Style classification ('question', 'how-to', 'listicle', or 'direct')
        """
        title_lower = title.lower()
        
        # Check for question
        if "?" in title or title_lower.startswith(("what", "why", "how", "when", "where", "who")):
            return "question"
        
        # Check for how-to
        if title_lower.startswith("how to"):
            return "how-to"
        
        # Check for listicle (numbers in first 10 characters)
        if any(char.isdigit() for char in title[:10]):
            return "listicle"
        
        # Default to direct style
        return "direct"
