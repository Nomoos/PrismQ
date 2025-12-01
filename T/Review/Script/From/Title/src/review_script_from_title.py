#!/usr/bin/env python3
"""PrismQ.T.Review.Script.From.Title - Script review module.

This module implements the script review workflow stage that:
1. Selects the oldest Story with state 'PrismQ.T.Review.Script.From.Title'
2. Reviews the script against the title
3. Outputs a Review model (simple: text, score, created_at)
4. Updates the Story state based on review acceptance

State Transitions:
- If review is first (iteration 1) → 'PrismQ.T.Review.Title.From.Script'
- If review doesn't accept script → 'PrismQ.T.Review.Script.From.Title' (stays for re-review)
- If review accepts script and it's not first review → 'PrismQ.T.Review.Script.Grammar'

Usage:
    from T.Review.Script.From.Title.src.review_script_from_title import (
        process_review_script_from_title,
        ReviewResult
    )
    
    # Using database connection
    result = process_review_script_from_title(conn)
    if result:
        print(f"Review created with score: {result.review.score}")
        print(f"Story state changed to: {result.new_state}")
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple, Any

from T.Database.models.review import Review
from T.Database.models.story import Story
from T.Database.repositories.story_repository import StoryRepository
from T.State.constants.state_names import StateNames


# Score threshold for accepting a script review
ACCEPTANCE_THRESHOLD = 70

# State constants
STATE_REVIEW_SCRIPT_FROM_TITLE = StateNames.REVIEW_SCRIPT_FROM_TITLE
STATE_REVIEW_TITLE_FROM_SCRIPT = StateNames.REVIEW_TITLE_FROM_SCRIPT
STATE_REVIEW_SCRIPT_GRAMMAR = StateNames.REVIEW_SCRIPT_GRAMMAR


@dataclass
class ReviewResult:
    """Result of the review script from title process.
    
    Attributes:
        story: The Story that was reviewed
        review: The Review that was created
        new_state: The new state the story was transitioned to
        accepted: Whether the script was accepted
        is_first_review: Whether this is the first review iteration
    """
    story: Story
    review: Review
    new_state: str
    accepted: bool
    is_first_review: bool


def get_oldest_story_for_review(
    story_repository: StoryRepository
) -> Optional[Story]:
    """Get the oldest Story with state 'PrismQ.T.Review.Script.From.Title'.
    
    Args:
        story_repository: Repository for Story database operations
        
    Returns:
        Oldest Story in the review state, or None if none found
    """
    stories = story_repository.find_by_state_ordered_by_created(
        state=STATE_REVIEW_SCRIPT_FROM_TITLE,
        ascending=True  # Oldest first
    )
    
    if stories:
        return stories[0]
    return None


def determine_next_state(
    accepted: bool,
    is_first_review: bool
) -> str:
    """Determine the next state based on review outcome.
    
    Args:
        accepted: Whether the script was accepted
        is_first_review: Whether this is the first review iteration
        
    Returns:
        The next state name
    """
    if is_first_review:
        # First review always goes to title review
        return STATE_REVIEW_TITLE_FROM_SCRIPT
    
    if not accepted:
        # Script not accepted - stay in same state for re-review
        return STATE_REVIEW_SCRIPT_FROM_TITLE
    
    # Script accepted and not first review - proceed to grammar check
    return STATE_REVIEW_SCRIPT_GRAMMAR


def create_review(
    score: int,
    text: str
) -> Review:
    """Create a Review model instance.
    
    Args:
        score: Review score (0-100)
        text: Review text content
        
    Returns:
        Review instance
    """
    return Review(
        text=text,
        score=score,
        created_at=datetime.now()
    )


def evaluate_script(
    script_text: str,
    title_text: str,
    is_first_review: bool
) -> Tuple[int, str]:
    """Evaluate a script against its title.
    
    This is a simple evaluation that checks basic alignment.
    In production, this could be replaced with AI-powered review.
    
    Args:
        script_text: The script content to review
        title_text: The title to review against
        is_first_review: Whether this is the first review
        
    Returns:
        Tuple of (score, review_text)
    """
    # Basic evaluation logic
    score = 70  # Base score
    review_points = []
    
    # Check if title words appear in script
    title_words = set(word.lower() for word in title_text.split() if len(word) > 3)
    script_lower = script_text.lower()
    
    words_found = sum(1 for word in title_words if word in script_lower)
    word_coverage = (words_found / len(title_words) * 100) if title_words else 100
    
    if word_coverage >= 50:
        score += 10
        review_points.append("Good alignment between title and script content.")
    elif word_coverage >= 30:
        review_points.append("Some title elements present in script.")
    else:
        score -= 10
        review_points.append("Title concepts not well-reflected in script.")
    
    # Check script length
    word_count = len(script_text.split())
    if word_count < 50:
        score -= 15
        review_points.append("Script is too short.")
    elif word_count < 100:
        score -= 5
        review_points.append("Script could be more developed.")
    elif word_count > 3000:
        score -= 5
        review_points.append("Script may be too long for the format.")
    else:
        score += 5
        review_points.append("Script length is appropriate.")
    
    # Check structure (paragraphs)
    paragraphs = [p.strip() for p in script_text.split('\n\n') if p.strip()]
    if len(paragraphs) >= 3:
        score += 5
        review_points.append("Good paragraph structure.")
    elif len(paragraphs) < 2:
        score -= 5
        review_points.append("Consider adding more structure with paragraphs.")
    
    # Ensure score is in valid range
    score = max(0, min(100, score))
    
    # Build review text
    if is_first_review:
        prefix = "Initial script review. "
    else:
        prefix = "Follow-up script review. "
    
    review_text = prefix + " ".join(review_points)
    
    return score, review_text


def process_review_script_from_title(
    connection: sqlite3.Connection,
    is_first_review: bool = True,
    script_text: Optional[str] = None,
    title_text: Optional[str] = None
) -> Optional[ReviewResult]:
    """Process the script review from title workflow stage.
    
    This function:
    1. Finds the oldest Story with state 'PrismQ.T.Review.Script.From.Title'
    2. Evaluates the script against the title
    3. Creates a Review record
    4. Updates the Story state based on review outcome
    
    Args:
        connection: SQLite database connection
        is_first_review: Whether this is the first review iteration
        script_text: Optional script text override (for testing)
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
    
    # Get script and title text (use overrides if provided, for testing)
    # In production, these would come from the Script and Title tables
    actual_script_text = script_text or "Sample script content for review"
    actual_title_text = title_text or "Sample Title"
    
    # Evaluate the script
    score, review_text = evaluate_script(
        script_text=actual_script_text,
        title_text=actual_title_text,
        is_first_review=is_first_review
    )
    
    # Create review
    review = create_review(score=score, text=review_text)
    
    # Determine if accepted
    accepted = score >= ACCEPTANCE_THRESHOLD
    
    # Determine next state
    new_state = determine_next_state(
        accepted=accepted,
        is_first_review=is_first_review
    )
    
    # Update story state
    story.update_state(new_state)
    story_repository.update(story)
    
    return ReviewResult(
        story=story,
        review=review,
        new_state=new_state,
        accepted=accepted,
        is_first_review=is_first_review
    )


def process_all_pending_reviews(
    connection: sqlite3.Connection,
    is_first_review: bool = True
) -> list:
    """Process all pending script reviews.
    
    Args:
        connection: SQLite database connection
        is_first_review: Whether these are first review iterations
        
    Returns:
        List of ReviewResult for all processed stories
    """
    results = []
    
    while True:
        result = process_review_script_from_title(
            connection=connection,
            is_first_review=is_first_review
        )
        
        if result is None:
            break
            
        results.append(result)
    
    return results


__all__ = [
    "ReviewResult",
    "process_review_script_from_title",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "determine_next_state",
    "create_review",
    "evaluate_script",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_FROM_TITLE",
    "STATE_REVIEW_TITLE_FROM_SCRIPT",
    "STATE_REVIEW_SCRIPT_GRAMMAR",
]
