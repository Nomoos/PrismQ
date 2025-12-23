#!/usr/bin/env python3
"""PrismQ.T.Review.Content.Tone - Content tone review module.

This module implements the script tone review workflow stage that:
1. Selects the Story with lowest current script version in state 'PrismQ.T.Review.Content.Tone'
   (current version = highest version number for that story_id)
2. Gets the Content (latest version) for the Story
3. Reviews the script for tone and style consistency
4. Outputs a Review model (simple: text, score, created_at)
5. Links the Review to the Content via Content.review_id FK
6. Updates the Story state based on review acceptance

State Transitions:
- If review doesn't accept script → 'PrismQ.T.Content.From.Title.Review.Content' (for rewrite)
- If review accepts script → 'PrismQ.T.Review.Content.Editing' (proceed to editing review)

Usage:
    from T.Review.Content.Tone.src.review_content_tone import (
        process_review_content_tone,
        ReviewResult
    )

    # Using database connection
    result = process_review_content_tone(conn)
    if result:
        print(f"Review created with score: {result.review.score}")
        print(f"Content reviewed: {result.script.id}")
        print(f"Story state changed to: {result.new_state}")
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from Model.Database.models.review import Review
from Model.Database.models.content import Content
from Model.Database.models.story import Story
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model import StateNames

# Score threshold for accepting a script review
ACCEPTANCE_THRESHOLD = 75

# State constants
CURRENT_STATE = StateNames.REVIEW_CONTENT_TONE
STATE_REVIEW_SCRIPT_TONE = StateNames.REVIEW_SCRIPT_TONE
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_REVIEW_SCRIPT_EDITING = StateNames.REVIEW_SCRIPT_EDITING


@dataclass
class ReviewResult:
    """Result of the review script tone process.

    Attributes:
        story: The Story that was reviewed
        script: The Content that was reviewed
        review: The Review that was created
        new_state: The new state the story was transitioned to
        accepted: Whether the script was accepted
    """

    story: Story
    script: Content
    review: Review
    new_state: str
    accepted: bool


def get_story_with_lowest_content_version(
    connection: sqlite3.Connection, story_repository: StoryRepository
) -> Optional[Story]:
    """Get the Story with the lowest current script version for review.

    Selects from Stories with state 'PrismQ.T.Review.Content.Tone',
    picking the one whose Content has the lowest current version number.
    Current version = highest version number across same story_id.

    Args:
        connection: SQLite database connection
        story_repository: Repository for Story database operations

    Returns:
        Story with lowest current script version, or None if none found
    """
    # Query to find stories in review state, joined with scripts,
    # ordered by the maximum script version (lowest first)
    cursor = connection.execute(
        """
        SELECT s.id as story_id
        FROM Story s
        INNER JOIN Content sc ON s.id = sc.story_id
        WHERE s.state = ?
        GROUP BY s.id
        ORDER BY MAX(sc.version) ASC
        LIMIT 1
        """,
        (STATE_REVIEW_SCRIPT_TONE,),
    )

    row = cursor.fetchone()
    if row is None:
        return None

    story_id = row["story_id"] if isinstance(row, sqlite3.Row) else row[0]
    return story_repository.find_by_id(story_id)


def determine_next_state(accepted: bool) -> str:
    """Determine the next state based on review outcome.

    Args:
        accepted: Whether the script was accepted

    Returns:
        The next state name
    """
    if not accepted:
        # Content not accepted - send back for rewrite
        return STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT

    # Content accepted - proceed to editing review
    return STATE_REVIEW_SCRIPT_EDITING


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
    # Validate score range before creating Review
    if not isinstance(score, int):
        raise TypeError("score must be an integer value")
    if score < 0 or score > 100:
        raise ValueError(f"score must be between 0 and 100, got {score}")

    return Review(text=text, score=score, created_at=datetime.now())


def evaluate_tone(content_text: str, target_tone: str = "") -> Tuple[int, str]:
    """Evaluate a script's tone and style consistency.

    This is a simple evaluation that checks basic tone aspects.
    In production, this could be replaced with AI-powered review.

    Args:
        content_text: The script content to review
        target_tone: Optional target tone description (e.g., "dark", "suspense")

    Returns:
        Tuple of (score, review_text)
    """
    # Base score
    score = 70
    review_points = []

    # Word count analysis
    word_count = len(content_text.split())

    if word_count < 50:
        score -= 15
        review_points.append("Content is too short for meaningful tone assessment.")
    elif word_count < 100:
        score -= 5
        review_points.append("Content could be more developed for better tone assessment.")
    else:
        score += 5
        review_points.append("Content has adequate length for tone assessment.")

    script_lower = content_text.lower()

    # Check for tone-related keywords (emotional intensity)
    positive_tone_words = {
        "happy",
        "joy",
        "excited",
        "wonderful",
        "amazing",
        "great",
        "love",
        "beautiful",
    }
    negative_tone_words = {
        "sad",
        "dark",
        "fear",
        "horror",
        "terrible",
        "awful",
        "hate",
        "ugly",
        "scary",
    }

    positive_count = sum(1 for word in positive_tone_words if word in script_lower)
    negative_count = sum(1 for word in negative_tone_words if word in script_lower)

    # Check for tone consistency
    if positive_count > 2 and negative_count < 2:
        review_points.append("Content maintains consistent positive tone.")
        score += 10
    elif negative_count > 2 and positive_count < 2:
        review_points.append("Content maintains consistent dark/dramatic tone.")
        score += 10
    elif positive_count <= 2 and negative_count <= 2:
        review_points.append("Content maintains neutral/informative tone.")
        score += 5
    else:
        review_points.append("Mixed tone detected - consider making tone more consistent.")
        score -= 5

    # Check for target tone alignment if specified
    if target_tone:
        target_lower = target_tone.lower()
        if "dark" in target_lower or "horror" in target_lower or "suspense" in target_lower:
            if negative_count >= 2:
                score += 10
                review_points.append(f"Good alignment with target tone '{target_tone}'.")
            else:
                score -= 10
                review_points.append(f"Tone doesn't align well with target tone '{target_tone}'.")
        elif "happy" in target_lower or "positive" in target_lower or "upbeat" in target_lower:
            if positive_count >= 2:
                score += 10
                review_points.append(f"Good alignment with target tone '{target_tone}'.")
            else:
                score -= 10
                review_points.append(f"Tone doesn't align well with target tone '{target_tone}'.")

    # Check for voice consistency (POV indicators) - use word boundaries for better matching
    # Pad with spaces for boundary detection
    padded_text = f" {script_lower} "
    first_person = (
        padded_text.count(" i ")
        + padded_text.count(" i'm ")
        + padded_text.count(" my ")
        + padded_text.count(" me ")
    )
    second_person = (
        padded_text.count(" you ") + padded_text.count(" your ") + padded_text.count(" yours ")
    )
    third_person = (
        padded_text.count(" he ")
        + padded_text.count(" she ")
        + padded_text.count(" they ")
        + padded_text.count(" his ")
        + padded_text.count(" her ")
        + padded_text.count(" their ")
    )

    pov_counts = [first_person, second_person, third_person]
    dominant_pov = max(pov_counts)
    other_povs = sum(c for c in pov_counts if c != dominant_pov and c > 0)

    if dominant_pov > 0 and other_povs < dominant_pov * 0.3:
        score += 5
        review_points.append("Consistent voice/POV throughout the script.")
    elif dominant_pov > 0 and other_povs > dominant_pov * 0.5:
        score -= 5
        review_points.append("POV shifts detected - consider maintaining consistent voice.")

    # Ensure score is in valid range
    score = max(0, min(100, score))

    # Build review text
    prefix = "Tone review: "
    review_text = prefix + " ".join(review_points)

    return score, review_text


def save_review(connection: sqlite3.Connection, review: Review) -> Review:
    """Save a Review to the database.

    Args:
        connection: SQLite database connection
        review: Review instance to save

    Returns:
        Review with id populated
    """
    cursor = connection.execute(
        "INSERT INTO Review (text, score, created_at) VALUES (?, ?, ?)",
        (review.text, review.score, review.created_at.isoformat()),
    )
    connection.commit()
    review.id = cursor.lastrowid
    return review


def update_content_review_id(connection: sqlite3.Connection, content_id: int, review_id: int) -> None:
    """Update a Content's review_id to link it to a Review.

    This updates the existing script's review_id without creating a new version,
    since adding a review reference doesn't change the script content.

    Args:
        connection: SQLite database connection
        content_id: ID of the Content to update
        review_id: ID of the Review to link to
    """
    connection.execute("UPDATE Content SET review_id = ? WHERE id = ?", (review_id, content_id))
    connection.commit()


def get_content_for_story(content_repository: ContentRepository, story: Story) -> Optional[Content]:
    """Get the current Content for a Story.

    Args:
        content_repository: Repository for Content database operations
        story: The Story to get Content for

    Returns:
        The Content if found, None otherwise
    """
    if story.content_id is not None:
        return content_repository.find_by_id(story.content_id)
    # If no content_id, try to find latest version for story
    return content_repository.find_latest_version(story.id)


def process_review_content_tone(
    connection: sqlite3.Connection,
    content_text: Optional[str] = None,
    target_tone: Optional[str] = None,
) -> Optional[ReviewResult]:
    """Process the script tone review workflow stage.

    This function:
    1. Finds the Story with lowest current script version in state 'PrismQ.T.Review.Content.Tone'
    2. Gets the Content associated with the Story (latest version)
    3. Evaluates the script's tone consistency
    4. Creates a Review record and saves it to database
    5. Links the Review to the Content via Content.review_id FK
    6. Updates the Story state based on review outcome

    Args:
        connection: SQLite database connection
        content_text: Optional script text override (for testing)
        target_tone: Optional target tone description (for testing)

    Returns:
        ReviewResult if a story was processed, None if no stories found
    """
    # Set up row factory for proper dict-like access
    connection.row_factory = sqlite3.Row

    story_repository = StoryRepository(connection)
    content_repository = ContentRepository(connection)

    # Get story with lowest current script version in review state
    story = get_story_with_lowest_content_version(connection, story_repository)

    if story is None:
        return None

    # Get the script for this story
    script = get_content_for_story(content_repository, story)

    # Get script text from the Content entity, or use override if provided (for testing)
    if content_text is not None:
        actual_content_text = content_text
    elif script is not None:
        actual_content_text = script.text
    else:
        actual_content_text = "Sample script content for tone review"

    actual_target_tone = target_tone or ""

    # Evaluate the script tone
    score, review_text = evaluate_tone(
        content_text=actual_content_text, target_tone=actual_target_tone
    )

    # Create and save review to database
    review = create_review(score=score, text=review_text)
    review = save_review(connection, review)

    # Determine if accepted
    accepted = score >= ACCEPTANCE_THRESHOLD

    # Link Review to Content by updating the script's review_id
    if script is not None:
        # Update existing script's review_id directly (no need to create new version)
        update_content_review_id(connection, script.id, review.id)
        script.review_id = review.id
        reviewed_content = script
    else:
        # If no script exists, create one with the review reference
        reviewed_content = Content(
            story_id=story.id, version=0, text=actual_content_text, review_id=review.id
        )
        reviewed_content = content_repository.insert(reviewed_content)
        story.content_id = reviewed_content.id

    # Determine next state
    new_state = determine_next_state(accepted=accepted)

    # Update story state
    story.update_state(new_state)
    story_repository.update(story)

    return ReviewResult(
        story=story, script=reviewed_content, review=review, new_state=new_state, accepted=accepted
    )


def process_all_pending_reviews(
    connection: sqlite3.Connection, target_tone: Optional[str] = None
) -> list:
    """Process all pending script tone reviews.

    Args:
        connection: SQLite database connection
        target_tone: Optional target tone description

    Returns:
        List of ReviewResult for all processed stories
    """
    results = []

    while True:
        result = process_review_content_tone(connection=connection, target_tone=target_tone)

        if result is None:
            break

        results.append(result)

    return results


__all__ = [
    "ReviewResult",
    "process_review_content_tone",
    "process_all_pending_reviews",
    "get_story_with_lowest_content_version",
    "get_content_for_story",
    "save_review",
    "update_content_review_id",
    "determine_next_state",
    "create_review",
    "evaluate_tone",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_TONE",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_REVIEW_SCRIPT_EDITING",
]
