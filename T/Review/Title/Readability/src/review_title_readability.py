#!/usr/bin/env python3
"""PrismQ.T.Review.Title.Readability - Title readability review module.

This module implements the title readability review workflow stage that:
1. Selects the oldest Story with state 'PrismQ.T.Review.Title.Readability'
2. Reviews the title for readability (voiceover suitability)
3. Outputs a Review model (simple: text, score, created_at)
4. Updates the Story state based on review acceptance

State Transitions:
- If review doesn't accept title → 'PrismQ.T.Script.From.Title.Review.Script' (return to script refinement)
- If review accepts title → 'PrismQ.T.Story.Review' (proceed to story review)

Review Model Output:
    Review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        score INTEGER CHECK (score >= 0 AND score <= 100),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

Usage:
    from T.Review.Title.Readability.src.review_title_readability import (
        process_review_title_readability,
        ReviewResult
    )
    
    # Using database connection
    result = process_review_title_readability(conn)
    if result:
        print(f"Review created with score: {result.review.score}")
        print(f"Story state changed to: {result.new_state}")
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from T.Database.models.review import Review
from T.Database.models.story import Story
from T.Database.repositories.story_repository import StoryRepository
from T.State.constants.state_names import StateNames


# Score threshold for accepting a title readability review
ACCEPTANCE_THRESHOLD = 70

# State constants
STATE_REVIEW_TITLE_READABILITY = StateNames.REVIEW_TITLE_READABILITY
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_STORY_REVIEW = StateNames.STORY_REVIEW


@dataclass
class ReviewResult:
    """Result of the review title readability process.
    
    Attributes:
        story: The Story that was reviewed
        review: The Review that was created
        new_state: The new state the story was transitioned to
        accepted: Whether the title was accepted
    """
    story: Story
    review: Review
    new_state: str
    accepted: bool


def get_oldest_story_for_review(
    story_repository: StoryRepository
) -> Optional[Story]:
    """Get the oldest Story with state 'PrismQ.T.Review.Title.Readability'.
    
    Args:
        story_repository: Repository for Story database operations
        
    Returns:
        Oldest Story in the review state, or None if none found
    """
    stories = story_repository.find_by_state_ordered_by_created(
        state=STATE_REVIEW_TITLE_READABILITY,
        ascending=True  # Oldest first
    )
    
    if stories:
        return stories[0]
    return None


def determine_next_state(accepted: bool) -> str:
    """Determine the next state based on review outcome.
    
    Args:
        accepted: Whether the title was accepted
        
    Returns:
        The next state name:
        - STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT if not accepted (return to script refinement)
        - STATE_STORY_REVIEW if accepted (proceed to story review)
    """
    if not accepted:
        # Title not accepted - return to script refinement
        return STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    # Title accepted - proceed to story review
    return STATE_STORY_REVIEW


def create_review(score: int, text: str) -> Review:
    """Create a Review model instance.
    
    Args:
        score: Review score (0-100)
        text: Review text content
        
    Returns:
        Review instance
        
    Raises:
        TypeError: If score is not an integer
        ValueError: If score is not in valid range (0-100)
    """
    # Validate score type before creating Review
    if not isinstance(score, int):
        raise TypeError("score must be an integer value")
    if score < 0 or score > 100:
        raise ValueError(f"score must be between 0 and 100, got {score}")
    
    return Review(
        text=text,
        score=score,
        created_at=datetime.now()
    )


def evaluate_title_readability(title_text: str) -> Tuple[int, str]:
    """Evaluate a title for voiceover readability.
    
    This evaluation checks:
    - Length appropriateness
    - Pronunciation difficulty (difficult consonant clusters)
    - Word complexity
    - Flow and rhythm
    
    In production, this could be replaced with AI-powered review.
    
    Args:
        title_text: The title content to review
        
    Returns:
        Tuple of (score, review_text)
    """
    # Base score
    score = 75
    review_points = []
    
    # Check title length (word count)
    words = title_text.split()
    word_count = len(words)
    
    if word_count < 2:
        score -= 15
        review_points.append("Title is too short for effective voiceover.")
    elif word_count > 10:
        score -= 10
        review_points.append("Title is quite long, may be hard to read aloud naturally.")
    elif word_count > 15:
        score -= 20
        review_points.append("Title is too long for smooth voiceover delivery.")
    else:
        score += 5
        review_points.append("Title length is appropriate for voiceover.")
    
    # Check character length
    char_count = len(title_text)
    if char_count > 100:
        score -= 10
        review_points.append("Title character count is too high for easy reading.")
    elif char_count > 60:
        score -= 5
        review_points.append("Title is slightly long but manageable.")
    
    # Check for difficult consonant clusters
    difficult_patterns = ['sths', 'ngths', 'tchsk', 'rchd']
    title_lower = title_text.lower()
    for pattern in difficult_patterns:
        if pattern in title_lower:
            score -= 10
            review_points.append(f"Contains difficult consonant cluster '{pattern}' that may cause pronunciation issues.")
            break
    
    # Check for complex/hard-to-pronounce words (simple heuristic: long words)
    long_words = [w for w in words if len(w) > 10]
    if long_words:
        score -= 5 * len(long_words)
        review_points.append(f"Contains {len(long_words)} long word(s) that may be hard to pronounce.")
    
    # Check for alliteration issues (consecutive words starting with same sound)
    first_letters = [w[0].lower() for w in words if w]
    consecutive_same = 0
    for i in range(1, len(first_letters)):
        if first_letters[i] == first_letters[i-1]:
            consecutive_same += 1
    
    if consecutive_same >= 3:
        score -= 10
        review_points.append("Contains tongue-twister-like alliteration that may be difficult to speak.")
    elif consecutive_same >= 2:
        score -= 5
        review_points.append("Contains some alliteration, may need careful pronunciation.")
    
    # Check for clear engagement elements
    engagement_words = ['mystery', 'secret', 'discover', 'amazing', 'incredible', 
                        'shocking', 'ultimate', 'best', 'worst', 'hidden', 'revealed']
    has_engagement = any(word.lower() in engagement_words for word in words)
    if has_engagement:
        score += 5
        review_points.append("Contains engaging words that work well for voiceover.")
    
    # Ensure score is in valid range
    score = max(0, min(100, score))
    
    # Build review text
    review_text = "Title Readability Review: " + " ".join(review_points)
    
    return score, review_text


def process_review_title_readability(
    connection: sqlite3.Connection,
    title_text: Optional[str] = None
) -> Optional[ReviewResult]:
    """Process the title readability review workflow stage.
    
    This function:
    1. Finds the oldest Story with state 'PrismQ.T.Review.Title.Readability'
    2. Evaluates the title for voiceover readability
    3. Creates a Review record
    4. Updates the Story state based on review outcome
    
    Args:
        connection: SQLite database connection
        title_text: Optional title text override (for testing)
        
    Returns:
        ReviewResult if a story was processed, None if no stories found
    """
    # Set up row factory for proper dict-like access
    connection.row_factory = sqlite3.Row
    
    story_repository = StoryRepository(connection)
    
    # Get oldest story in review state
    story = get_oldest_story_for_review(story_repository)
    
    if story is None:
        return None
    
    # Get title text (use override if provided, for testing)
    # In production, this would come from the Title table
    actual_title_text = title_text or "Sample Title for Review"
    
    # Evaluate the title for readability
    score, review_text = evaluate_title_readability(actual_title_text)
    
    # Create review
    review = create_review(score=score, text=review_text)
    
    # Determine if accepted
    accepted = score >= ACCEPTANCE_THRESHOLD
    
    # Determine next state
    new_state = determine_next_state(accepted=accepted)
    
    # Update story state
    story.update_state(new_state)
    story_repository.update(story)
    
    return ReviewResult(
        story=story,
        review=review,
        new_state=new_state,
        accepted=accepted
    )


def process_all_pending_reviews(connection: sqlite3.Connection) -> list:
    """Process all pending title readability reviews.
    
    Args:
        connection: SQLite database connection
        
    Returns:
        List of ReviewResult for all processed stories
    """
    results = []
    
    while True:
        result = process_review_title_readability(connection=connection)
        
        if result is None:
            break
            
        results.append(result)
    
    return results


__all__ = [
    "ReviewResult",
    "process_review_title_readability",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "determine_next_state",
    "create_review",
    "evaluate_title_readability",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_TITLE_READABILITY",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_STORY_REVIEW",
]
