#!/usr/bin/env python3
"""PrismQ.T.Review.Content.Editing - Content editing review service module.

This module implements the script editing review workflow stage that:
1. Selects the Story with state 'PrismQ.T.Review.Content.Editing' that has
   the Content with the lowest current version number (current = MAX(version) for that story_id)
2. Gets the latest Content version for that Story
3. Reviews the Content for editing quality (clarity, flow, redundancy)
4. Creates a Review model and links it to the Content via review_id FK
5. Updates the Story state based on review acceptance

Selection Logic:
- Prioritizes Stories whose Scripts have fewer iterations (lowest max version)
- Stories with version 0 scripts are processed before those with version 1, etc.
- Tie-breaker: oldest creation date
- After selecting the Story, always retrieves the **latest Content version** for it

State Transitions:
- If review accepts script → 'PrismQ.T.Review.Title.Readability'
- If review doesn't accept script → 'PrismQ.T.Content.From.Title.Review.Content' (Content Refinement)

Review Model Output:
    Review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        score INTEGER CHECK (score >= 0 AND score <= 100),
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

Content-Review Relationship:
    The Review is linked to the Content via the Content.review_id FK field.
    This allows tracking which review was created for which script version.

Usage:
    from T.Review.Content.Editing.src.review_content_editing_service import (
        process_review_content_editing,
        ReviewResult
    )

    # Using database connection
    result = process_review_content_editing(conn)
    if result:
        print(f"Review created with score: {result.review.score}")
        print(f"Content reviewed: {result.script.id}")
        print(f"Story state changed to: {result.new_state}")
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.State.constants.state_names import StateNames

# Score threshold for accepting an editing review
ACCEPTANCE_THRESHOLD = 75

# State constants
STATE_REVIEW_SCRIPT_EDITING = StateNames.REVIEW_SCRIPT_EDITING
STATE_REVIEW_TITLE_READABILITY = StateNames.REVIEW_TITLE_READABILITY
# Content Refinement state (Stage 8/11) - Content.From.Title.Review.Content
STATE_SCRIPT_REFINEMENT = "PrismQ.T.Content.From.Title.Review.Content"


@dataclass
class ReviewResult:
    """Result of the review script editing process.

    Attributes:
        story: The Story that contains the script
        script: The Content that was reviewed
        review: The Review that was created (linked to script via review_id)
        new_state: The new state the story was transitioned to
        accepted: Whether the script was accepted
    """

    story: Story
    script: Content
    review: Review
    new_state: str
    accepted: bool


def get_story_with_lowest_content_version(
    connection: sqlite3.Connection, state: str
) -> Optional[Story]:
    """Get the Story with state that has the Content with lowest current version.

    Selection logic:
    1. Find all Stories with the specified state
    2. For each Story, find the highest version number of its Scripts
    3. Select the Story whose Content has the lowest highest-version number

    This prioritizes Stories with fewer script iterations (less revised scripts).

    Args:
        connection: SQLite database connection
        state: The state to filter Stories by

    Returns:
        Story with lowest script version, or None if none found
    """
    # Query to find the Story with the lowest max script version
    # This joins Story with Content, groups by story_id to find max version,
    # then orders by that max version ascending to get the lowest one first
    cursor = connection.execute(
        """
        SELECT s.id, s.idea_id, s.idea_json, s.title_id, s.content_id, 
               s.state, s.created_at, s.updated_at,
               COALESCE(MAX(sc.version), 0) as max_version
        FROM Story s
        LEFT JOIN Content sc ON s.id = sc.story_id
        WHERE s.state = ?
        GROUP BY s.id
        ORDER BY max_version ASC, s.created_at ASC
        LIMIT 1
        """,
        (state,),
    )
    row = cursor.fetchone()

    if row is None:
        return None

    # Convert row to Story model
    created_at = row["created_at"]
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    updated_at = row["updated_at"]
    if isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)

    return Story(
        id=row["id"],
        idea_id=row["idea_id"],
        idea_json=row["idea_json"],
        title_id=row["title_id"],
        content_id=row["content_id"],
        state=row["state"],
        created_at=created_at,
        updated_at=updated_at,
    )


def get_oldest_story_for_review(
    story_repository: StoryRepository, connection: Optional[sqlite3.Connection] = None
) -> Optional[Story]:
    """Get Story with state 'PrismQ.T.Review.Content.Editing' that has lowest script version.

    Selection logic:
    - Selects Story whose Content has the lowest current version number
    - "Current version" = highest version number for that story_id
    - Prioritizes Stories with fewer script iterations

    Args:
        story_repository: Repository for Story database operations
        connection: Optional SQLite connection for version-based query

    Returns:
        Story with lowest script version in the review state, or None if none found
    """
    if connection is not None:
        # Use new version-based selection
        return get_story_with_lowest_content_version(
            connection=connection, state=STATE_REVIEW_SCRIPT_EDITING
        )

    # Fallback to old behavior if no connection provided
    stories = story_repository.find_by_state_ordered_by_created(
        state=STATE_REVIEW_SCRIPT_EDITING, ascending=True  # Oldest first
    )

    if stories:
        return stories[0]
    return None


def determine_next_state(accepted: bool) -> str:
    """Determine the next state based on review outcome.

    Args:
        accepted: Whether the script editing review was accepted

    Returns:
        The next state name:
        - If accepted: PrismQ.T.Review.Title.Readability
        - If not accepted: PrismQ.T.Content.From.Title.Review.Content (Content Refinement)
    """
    if accepted:
        return STATE_REVIEW_TITLE_READABILITY
    else:
        return STATE_SCRIPT_REFINEMENT


def create_review(score: int, text: str) -> Review:
    """Create a Review model instance.

    Args:
        score: Review score (0-100)
        text: Review text content

    Returns:
        Review instance

    Raises:
        ValueError: If score is not in valid range (0-100)
        TypeError: If score is not an integer
    """
    # Validate score type before creating Review
    if not isinstance(score, int):
        raise TypeError("score must be an integer value")
    if score < 0 or score > 100:
        raise ValueError(f"score must be between 0 and 100, got {score}")

    return Review(text=text, score=score, created_at=datetime.now())


def evaluate_content(content_text: str) -> Tuple[int, str]:
    """Evaluate a script for editing quality.

    This is a simple evaluation that checks basic editing quality.
    In production, this could be replaced with AI-powered editing review.

    Checks for:
    - Wordiness and redundancy
    - Clarity and readability
    - Flow and structure
    - Transitions

    Args:
        content_text: The script content to review

    Returns:
        Tuple of (score, review_text)
    """
    # Base score
    score = 75
    review_points: List[str] = []

    # Check script length
    word_count = len(content_text.split())
    if word_count < 50:
        score -= 15
        review_points.append("Content is too short for meaningful editing review.")
    elif word_count < 100:
        score -= 5
        review_points.append("Content could be more developed.")
    else:
        score += 5
        review_points.append("Content length is appropriate for editing review.")

    # Check for wordy phrases (simplified check)
    wordy_phrases = [
        "in order to",
        "due to the fact that",
        "at this point in time",
        "for the purpose of",
        "in the event that",
        "with regard to",
        "in close proximity",
        "make a decision",
        "give consideration to",
    ]

    script_lower = content_text.lower()
    wordiness_issues = sum(1 for phrase in wordy_phrases if phrase in script_lower)

    if wordiness_issues == 0:
        score += 10
        review_points.append("Good concise writing, no wordy phrases detected.")
    elif wordiness_issues <= 2:
        score -= 5
        review_points.append(f"Found {wordiness_issues} wordy phrase(s) that could be simplified.")
    else:
        score -= 15
        review_points.append(
            f"Found {wordiness_issues} wordy phrases. Content needs editing for conciseness."
        )

    # Check for redundant phrases
    redundant_phrases = [
        "very unique",
        "completely finished",
        "past history",
        "future plans",
        "close proximity",
        "exact same",
        "absolutely essential",
    ]

    redundancy_issues = sum(1 for phrase in redundant_phrases if phrase in script_lower)

    if redundancy_issues == 0:
        score += 5
        review_points.append("No redundant phrases detected.")
    else:
        score -= redundancy_issues * 5
        review_points.append(f"Found {redundancy_issues} redundant phrase(s) to remove.")

    # Check structure (paragraphs)
    paragraphs = [p.strip() for p in content_text.split("\n\n") if p.strip()]
    if len(paragraphs) >= 3:
        score += 5
        review_points.append("Good paragraph structure for flow.")
    elif len(paragraphs) < 2:
        score -= 5
        review_points.append("Consider adding paragraph breaks for better flow.")

    # Check for repeated consecutive words (simple check)
    words = content_text.lower().split()
    repeated_word_count = 0
    for i in range(len(words) - 1):
        if words[i] == words[i + 1] and len(words[i]) > 3:
            repeated_word_count += 1

    if repeated_word_count > 0:
        score -= repeated_word_count * 3
        review_points.append(
            f"Found {repeated_word_count} instance(s) of repeated consecutive words."
        )

    # Check for very long sentences (simplified)
    sentences = content_text.replace("!", ".").replace("?", ".").split(".")
    long_sentences = sum(1 for s in sentences if len(s.split()) > 30)

    if long_sentences > 0:
        score -= long_sentences * 3
        review_points.append(
            f"Found {long_sentences} very long sentence(s) that could be split for clarity."
        )

    # Ensure score is in valid range
    score = max(0, min(100, score))

    # Build review text
    prefix = "Editing review for clarity, flow, and conciseness. "
    review_text = prefix + " ".join(review_points)

    return score, review_text


def process_review_content_editing(
    connection: sqlite3.Connection, content_text: Optional[str] = None
) -> Optional[ReviewResult]:
    """Process the script editing review workflow stage.

    This function:
    1. Finds the Story with state 'PrismQ.T.Review.Content.Editing' that has
       the Content with the lowest current version number (current = MAX(version) for that story_id)
    2. Gets the latest Content version for that Story
    3. Evaluates the script for editing quality
    4. Creates a Review record and persists it
    5. Links the Review to the Content via script.review_id FK
    6. Updates the Story state based on review outcome:
       - If accepted: PrismQ.T.Review.Title.Readability
       - If not accepted: PrismQ.T.Content.From.Title.Review.Content

    Args:
        connection: SQLite database connection
        content_text: Optional script text override (for testing)

    Returns:
        ReviewResult if a story was processed, None if no stories found
    """
    # Set up row factory for proper dict-like access
    connection.row_factory = sqlite3.Row

    story_repository = StoryRepository(connection)
    content_repository = ContentRepository(connection)
    review_repository = ReviewRepository(connection)

    # Get story with lowest script version in editing review state
    story = get_oldest_story_for_review(story_repository, connection)

    if story is None:
        return None

    # Get the latest Content version for this Story
    # Always retrieve the latest version, not just the one referenced by story.content_id
    script = None
    if story.id is not None:
        script = content_repository.find_latest_version(story.id)

    # Fallback: if no script found via find_latest_version, try story.content_id
    if script is None and story.content_id is not None:
        script = content_repository.find_by_id(story.content_id)

    # Get script text (use override if provided, for testing)
    # In production, this comes from the Content model
    if content_text is not None:
        actual_content_text = content_text
    elif script is not None:
        actual_content_text = script.text
    else:
        actual_content_text = "Sample script content for editing review"

    # Evaluate the script for editing quality
    score, review_text = evaluate_content(content_text=actual_content_text)

    # Create and persist review
    review = create_review(score=score, text=review_text)
    review = review_repository.insert(review)

    # If no Content exists but we have a Story, create one for testing/demo purposes
    # This ensures the review can be linked to a Content
    if script is None and story.id is not None:
        script = Content(story_id=story.id, version=0, text=actual_content_text, review_id=review.id)
        script = content_repository.insert(script)
        # Update story to reference this script
        story.content_id = script.id
    elif script is not None and script.id is not None and review.id is not None:
        # Link the Review to existing Content via review_id FK
        content_repository.update_review_id(script.id, review.id)
        script.review_id = review.id  # Update local object

    # Determine if accepted
    accepted = score >= ACCEPTANCE_THRESHOLD

    # Determine next state
    new_state = determine_next_state(accepted=accepted)

    # Update story state
    story.update_state(new_state)
    story_repository.update(story)

    return ReviewResult(
        story=story, script=script, review=review, new_state=new_state, accepted=accepted
    )


def process_all_pending_reviews(connection: sqlite3.Connection) -> List[ReviewResult]:
    """Process all pending script editing reviews.

    Args:
        connection: SQLite database connection

    Returns:
        List of ReviewResult for all processed stories
    """
    results: List[ReviewResult] = []

    while True:
        result = process_review_content_editing(connection=connection)

        if result is None:
            break

        results.append(result)

    return results


__all__ = [
    "ReviewResult",
    "process_review_content_editing",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "get_story_with_lowest_content_version",
    "determine_next_state",
    "create_review",
    "evaluate_content",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_EDITING",
    "STATE_SCRIPT_REFINEMENT",
    "STATE_REVIEW_TITLE_READABILITY",
]
