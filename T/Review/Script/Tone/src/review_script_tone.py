#!/usr/bin/env python3
"""PrismQ.T.Review.Script.Tone - Script tone review module.

This module implements the script tone review workflow stage that:
1. Selects the oldest Story with state 'PrismQ.T.Review.Script.Tone'
2. Reviews the script for tone and style consistency
3. Outputs a Review model (simple: text, score, created_at)
4. Links the Review to the Script via Script.review_id FK
5. Updates the Story state based on review acceptance

State Transitions:
- If review doesn't accept script → 'PrismQ.T.Script.From.Title.Review.Script' (for rewrite)
- If review accepts script → 'PrismQ.T.Review.Script.Editing' (proceed to editing review)

Usage:
    from T.Review.Script.Tone.src.review_script_tone import (
        process_review_script_tone,
        ReviewResult
    )
    
    # Using database connection
    result = process_review_script_tone(conn)
    if result:
        print(f"Review created with score: {result.review.score}")
        print(f"Script reviewed: {result.script.id}")
        print(f"Story state changed to: {result.new_state}")
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from T.Database.models.review import Review
from T.Database.models.story import Story
from T.Database.models.script import Script
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.State.constants.state_names import StateNames


# Score threshold for accepting a script review
ACCEPTANCE_THRESHOLD = 70

# State constants
STATE_REVIEW_SCRIPT_TONE = StateNames.REVIEW_SCRIPT_TONE
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_REVIEW_SCRIPT_EDITING = StateNames.REVIEW_SCRIPT_EDITING


@dataclass
class ReviewResult:
    """Result of the review script tone process.
    
    Attributes:
        story: The Story that was reviewed
        script: The Script that was reviewed
        review: The Review that was created
        new_state: The new state the story was transitioned to
        accepted: Whether the script was accepted
    """
    story: Story
    script: Script
    review: Review
    new_state: str
    accepted: bool


def get_oldest_story_for_review(
    story_repository: StoryRepository
) -> Optional[Story]:
    """Get the oldest Story with state 'PrismQ.T.Review.Script.Tone'.
    
    Args:
        story_repository: Repository for Story database operations
        
    Returns:
        Oldest Story in the review state, or None if none found
    """
    stories = story_repository.find_by_state_ordered_by_created(
        state=STATE_REVIEW_SCRIPT_TONE,
        ascending=True  # Oldest first
    )
    
    if stories:
        return stories[0]
    return None


def determine_next_state(accepted: bool) -> str:
    """Determine the next state based on review outcome.
    
    Args:
        accepted: Whether the script was accepted
        
    Returns:
        The next state name
    """
    if not accepted:
        # Script not accepted - send back for rewrite
        return STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    # Script accepted - proceed to editing review
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
    
    return Review(
        text=text,
        score=score,
        created_at=datetime.now()
    )


def evaluate_tone(
    script_text: str,
    target_tone: str = ""
) -> Tuple[int, str]:
    """Evaluate a script's tone and style consistency.
    
    This is a simple evaluation that checks basic tone aspects.
    In production, this could be replaced with AI-powered review.
    
    Args:
        script_text: The script content to review
        target_tone: Optional target tone description (e.g., "dark", "suspense")
        
    Returns:
        Tuple of (score, review_text)
    """
    # Base score
    score = 70
    review_points = []
    
    # Word count analysis
    word_count = len(script_text.split())
    
    if word_count < 50:
        score -= 15
        review_points.append("Script is too short for meaningful tone assessment.")
    elif word_count < 100:
        score -= 5
        review_points.append("Script could be more developed for better tone assessment.")
    else:
        score += 5
        review_points.append("Script has adequate length for tone assessment.")
    
    script_lower = script_text.lower()
    
    # Check for tone-related keywords (emotional intensity)
    positive_tone_words = {"happy", "joy", "excited", "wonderful", "amazing", "great", "love", "beautiful"}
    negative_tone_words = {"sad", "dark", "fear", "horror", "terrible", "awful", "hate", "ugly", "scary"}
    
    positive_count = sum(1 for word in positive_tone_words if word in script_lower)
    negative_count = sum(1 for word in negative_tone_words if word in script_lower)
    
    # Check for tone consistency
    if positive_count > 2 and negative_count < 2:
        review_points.append("Script maintains consistent positive tone.")
        score += 10
    elif negative_count > 2 and positive_count < 2:
        review_points.append("Script maintains consistent dark/dramatic tone.")
        score += 10
    elif positive_count <= 2 and negative_count <= 2:
        review_points.append("Script maintains neutral/informative tone.")
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
    first_person = padded_text.count(" i ") + padded_text.count(" i'm ") + padded_text.count(" my ") + padded_text.count(" me ")
    second_person = padded_text.count(" you ") + padded_text.count(" your ") + padded_text.count(" yours ")
    third_person = padded_text.count(" he ") + padded_text.count(" she ") + padded_text.count(" they ") + padded_text.count(" his ") + padded_text.count(" her ") + padded_text.count(" their ")
    
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
        (review.text, review.score, review.created_at.isoformat())
    )
    connection.commit()
    review.id = cursor.lastrowid
    return review


def get_script_for_story(
    script_repository: ScriptRepository,
    story: Story
) -> Optional[Script]:
    """Get the current Script for a Story.
    
    Args:
        script_repository: Repository for Script database operations
        story: The Story to get Script for
        
    Returns:
        The Script if found, None otherwise
    """
    if story.script_id is not None:
        return script_repository.find_by_id(story.script_id)
    # If no script_id, try to find latest version for story
    return script_repository.find_latest_version(story.id)


def process_review_script_tone(
    connection: sqlite3.Connection,
    script_text: Optional[str] = None,
    target_tone: Optional[str] = None
) -> Optional[ReviewResult]:
    """Process the script tone review workflow stage.
    
    This function:
    1. Finds the oldest Story with state 'PrismQ.T.Review.Script.Tone'
    2. Gets the Script associated with the Story
    3. Evaluates the script's tone consistency
    4. Creates a Review record and saves it to database
    5. Creates a new Script version with the review_id set (linking Review to Script)
    6. Updates the Story state based on review outcome
    
    Args:
        connection: SQLite database connection
        script_text: Optional script text override (for testing)
        target_tone: Optional target tone description (for testing)
        
    Returns:
        ReviewResult if a story was processed, None if no stories found
    """
    # Set up row factory for proper dict-like access
    connection.row_factory = sqlite3.Row
    
    story_repository = StoryRepository(connection)
    script_repository = ScriptRepository(connection)
    
    # Get oldest story in review state
    story = get_oldest_story_for_review(story_repository)
    
    if story is None:
        return None
    
    # Get the script for this story
    script = get_script_for_story(script_repository, story)
    
    # Get script text from the Script entity, or use override if provided (for testing)
    if script_text is not None:
        actual_script_text = script_text
    elif script is not None:
        actual_script_text = script.text
    else:
        actual_script_text = "Sample script content for tone review"
    
    actual_target_tone = target_tone or ""
    
    # Evaluate the script tone
    score, review_text = evaluate_tone(
        script_text=actual_script_text,
        target_tone=actual_target_tone
    )
    
    # Create and save review to database
    review = create_review(score=score, text=review_text)
    review = save_review(connection, review)
    
    # Determine if accepted
    accepted = score >= ACCEPTANCE_THRESHOLD
    
    # Create a new Script version with the review_id set (linking Review to Script)
    if script is not None:
        new_script = script.create_next_version(
            new_text=script.text,  # Keep same text, just adding review reference
            review_id=review.id
        )
        new_script = script_repository.insert(new_script)
        # Update story to point to new script version
        story.script_id = new_script.id
    else:
        # If no script exists, create a minimal one for testing purposes
        new_script = Script(
            story_id=story.id,
            version=0,
            text=actual_script_text,
            review_id=review.id
        )
        new_script = script_repository.insert(new_script)
        story.script_id = new_script.id
    
    # Determine next state
    new_state = determine_next_state(accepted=accepted)
    
    # Update story state
    story.update_state(new_state)
    story_repository.update(story)
    
    return ReviewResult(
        story=story,
        script=new_script,
        review=review,
        new_state=new_state,
        accepted=accepted
    )


def process_all_pending_reviews(
    connection: sqlite3.Connection,
    target_tone: Optional[str] = None
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
        result = process_review_script_tone(
            connection=connection,
            target_tone=target_tone
        )
        
        if result is None:
            break
            
        results.append(result)
    
    return results


__all__ = [
    "ReviewResult",
    "process_review_script_tone",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "get_script_for_story",
    "save_review",
    "determine_next_state",
    "create_review",
    "evaluate_tone",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_TONE",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_REVIEW_SCRIPT_EDITING",
]
