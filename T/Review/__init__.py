"""PrismQ.T.Review - AI-powered review module for scripts and titles.

This module provides the parent namespace for all review-related functionality
in the PrismQ ecosystem. It includes a unified severity enum used across all
review types and a consolidated story picking function.

Review Types:
    - Consistency: Character, timeline, and location consistency
    - Content: Narrative coherence, plot logic, and character motivation
    - Editing: Clarity, flow, and structure improvements
    - Grammar: Grammar, punctuation, and spelling validation
    - Readability: Voiceover flow and spoken-word suitability
    - Tone: Style, voice, and emotional intensity validation

Common Components:
    - ReviewSeverity: Unified severity levels used across all review types
    - pick_story_by_module: Consolidated story picking by module name

Example:
    >>> from T.Review import ReviewSeverity, pick_story_by_module
    >>> severity = ReviewSeverity.HIGH
    >>> print(severity.value)
    'high'
    
    >>> # Pick a story for processing by module name
    >>> story = pick_story_by_module(
    ...     connection=conn,
    ...     module_name="PrismQ.T.Review.Script.Readability"
    ... )
"""

import sqlite3
from enum import Enum
from typing import Optional

from T.Database.models.story import Story
from T.Database.repositories.story_repository import StoryRepository


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


def pick_story_by_module(
    connection: sqlite3.Connection,
    module_name: str,
    story_repository: Optional[StoryRepository] = None
) -> Optional[Story]:
    """Pick the oldest Story where state matches the given module name.
    
    This is a consolidated story picking function that selects Stories
    based on their state matching a module name. Stories are picked in
    FIFO order (oldest first by created_at).
    
    The module name directly corresponds to the Story state. For example:
    - module_name="PrismQ.T.Review.Script.Readability" picks Stories
      with state="PrismQ.T.Review.Script.Readability"
    
    Args:
        connection: SQLite database connection
        module_name: The module name which equals the Story state to match.
            Examples:
            - "PrismQ.T.Review.Script.Readability"
            - "PrismQ.T.Review.Script.Tone"
            - "PrismQ.T.Review.Script.Editing"
            - "PrismQ.T.Review.Script.Content"
            - "PrismQ.T.Review.Script.Grammar"
            - "PrismQ.T.Review.Script.Consistency"
        story_repository: Optional StoryRepository instance. If not provided,
            one will be created using the connection.
    
    Returns:
        The oldest Story with state matching module_name, or None if no
        Stories found in that state.
    
    Example:
        >>> import sqlite3
        >>> from T.Review import pick_story_by_module
        >>> 
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> 
        >>> # Pick oldest story ready for readability review
        >>> story = pick_story_by_module(
        ...     connection=conn,
        ...     module_name="PrismQ.T.Review.Script.Readability"
        ... )
        >>> if story:
        ...     print(f"Processing story {story.id}")
        
        >>> # Using with existing repository
        >>> from T.Database.repositories.story_repository import StoryRepository
        >>> repo = StoryRepository(conn)
        >>> story = pick_story_by_module(
        ...     connection=conn,
        ...     module_name="PrismQ.T.Review.Script.Tone",
        ...     story_repository=repo
        ... )
    """
    # Ensure row_factory is set for proper dict-like access
    if connection.row_factory is None:
        connection.row_factory = sqlite3.Row
    
    # Use provided repository or create a new one
    repo = story_repository if story_repository is not None else StoryRepository(connection)
    
    # Use the repository's existing find_oldest_by_state method
    return repo.find_oldest_by_state(module_name)


def count_stories_by_module(
    connection: sqlite3.Connection,
    module_name: str,
    story_repository: Optional[StoryRepository] = None
) -> int:
    """Count Stories where state matches the given module name.
    
    This function counts how many Stories are waiting to be processed
    by a specific module.
    
    Args:
        connection: SQLite database connection
        module_name: The module name which equals the Story state to match.
        story_repository: Optional StoryRepository instance.
    
    Returns:
        Number of Stories with state matching module_name.
    
    Example:
        >>> from T.Review import count_stories_by_module
        >>> 
        >>> count = count_stories_by_module(
        ...     connection=conn,
        ...     module_name="PrismQ.T.Review.Script.Readability"
        ... )
        >>> print(f"{count} stories waiting for readability review")
    """
    # Ensure row_factory is set
    if connection.row_factory is None:
        connection.row_factory = sqlite3.Row
    
    # Use provided repository or create a new one
    repo = story_repository if story_repository is not None else StoryRepository(connection)
    
    return repo.count_by_state(module_name)


__all__ = [
    "ReviewSeverity",
    "pick_story_by_module",
    "count_stories_by_module",
]
