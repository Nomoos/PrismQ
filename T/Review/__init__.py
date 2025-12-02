"""PrismQ.T.Review - AI-powered review module for scripts and titles.

This module provides the parent namespace for all review-related functionality
in the PrismQ ecosystem. It includes a unified severity enum used across all
review types.

Review Types:
    - Consistency: Character, timeline, and location consistency
    - Content: Narrative coherence, plot logic, and character motivation
    - Editing: Clarity, flow, and structure improvements
    - Grammar: Grammar, punctuation, and spelling validation
    - Readability: Voiceover flow and spoken-word suitability
    - Tone: Style, voice, and emotional intensity validation

Common Components:
    - ReviewSeverity: Unified severity levels used across all review types

Example:
    >>> from T.Review import ReviewSeverity
    >>> severity = ReviewSeverity.HIGH
    >>> print(severity.value)
    'high'
"""

from enum import Enum


class ReviewSeverity(Enum):
    """Unified severity levels for all review issues.
    
    This enum provides a common severity classification used across all
    review types (Grammar, Tone, Content, Consistency, Editing, Readability).
    
    Severity Levels:
        CRITICAL: Must be fixed - breaks story logic or has major impact
        HIGH: Should be fixed - significant issue with noticeable impact
        MEDIUM: Recommended to fix - moderate impact, polish level
        LOW: Minor issue - optional improvement
    
    Example:
        >>> from T.Review import ReviewSeverity
        >>> severity = ReviewSeverity.CRITICAL
        >>> print(f"Level: {severity.value}")
        Level: critical
    """
    
    CRITICAL = "critical"  # Must be fixed
    HIGH = "high"  # Should be fixed
    MEDIUM = "medium"  # Recommended to fix
    LOW = "low"  # Minor issue


__all__ = [
    "ReviewSeverity",
]
