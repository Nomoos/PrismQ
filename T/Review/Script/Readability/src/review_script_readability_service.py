#!/usr/bin/env python3
"""PrismQ.T.Review.Script.Readability - Script readability review service.

This module implements the script readability review workflow stage that:
1. Selects the oldest Story with state 'PrismQ.T.Review.Script.Readability'
2. Reviews the script for voiceover readability
3. Outputs a Review model (simple: text, score, created_at)
4. Updates the Story state based on review acceptance

State Transitions:
- If review doesn't accept script → 'PrismQ.T.Script.From.Script.Review.Title' (for script refinement)
- If review accepts script → 'PrismQ.T.Story.Review' (proceed to expert review)

Usage:
    from T.Review.Script.Readability.src.review_script_readability_service import (
        process_review_script_readability,
        ReviewResult
    )
    
    # Using database connection
    result = process_review_script_readability(conn)
    if result:
        print(f"Review created with score: {result.review.score}")
        print(f"Story state changed to: {result.new_state}")
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List

from Model.Database.models.review import Review
from Model.Database.models.story import Story
from Model.Database.models.script import Script
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.script_repository import ScriptRepository
from Model.State.constants.state_names import StateNames

# Direct import to avoid circular import through T.Review.Script.__init__
import importlib.util
from pathlib import Path

# Load the script_readability_review module directly with error handling
_module_dir = Path(__file__).parent.parent
_module_path = _module_dir / "script_readability_review.py"

try:
    if not _module_path.exists():
        raise FileNotFoundError(f"Required module not found: {_module_path}")
    
    _spec = importlib.util.spec_from_file_location("script_readability_review", _module_path)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Could not load module spec for: {_module_path}")
    
    _readability_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_readability_module)
    
    review_script_readability = _readability_module.review_script_readability
    ReadabilityReview = _readability_module.ReadabilityReview
except (FileNotFoundError, ImportError, SyntaxError, AttributeError) as e:
    raise ImportError(
        f"Failed to load script_readability_review module from {_module_path}: {e}"
    ) from e


# Score threshold for accepting a script readability review
ACCEPTANCE_THRESHOLD = 75

# State constants
STATE_REVIEW_SCRIPT_READABILITY = StateNames.REVIEW_SCRIPT_READABILITY
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE
STATE_STORY_REVIEW = StateNames.STORY_REVIEW


@dataclass
class ReviewResult:
    """Result of the review script readability process.
    
    Attributes:
        story: The Story that was reviewed
        review: The Review that was created
        new_state: The new state the story was transitioned to
        accepted: Whether the script was accepted (passes readability)
        readability_review: The detailed ReadabilityReview from the checker
    """
    story: Story
    review: Review
    new_state: str
    accepted: bool
    readability_review: Optional[ReadabilityReview] = None


def get_story_for_review(
    story_repository: StoryRepository,
    script_repository: ScriptRepository
) -> Optional[Story]:
    """Get the Story whose script has the lowest current version number.
    
    Selection criteria:
    1. Get all stories with state 'PrismQ.T.Review.Script.Readability'
    2. For each story, get its script via story.script_id
    3. Skip stories without scripts (invalid state - should not be in review)
    4. For each script, get its current (highest) version number for the same story_id
    5. Return the story whose script has the lowest current version number
    
    Args:
        story_repository: Repository for Story database operations
        script_repository: Repository for Script database operations
        
    Returns:
        Story with the lowest current script version, or None if none found
    """
    # Get all stories in the readability review state
    stories = story_repository.find_by_state(STATE_REVIEW_SCRIPT_READABILITY)
    
    if not stories:
        return None
    
    # Find the story whose script has the lowest current version number
    # "Current version" = the highest version number among all scripts for a story
    story_with_lowest_version = None
    lowest_version = float('inf')
    
    for story in stories:
        if story.script_id is None:
            # Story without a script - skip (invalid state for readability review)
            continue
        
        # Get the script by ID to find the story_id
        script = script_repository.find_by_id(story.script_id)
        if script is None:
            # Script not found - skip (invalid state)
            continue
        
        # Get the current (highest) version for this story's scripts
        # This is the "current version" - the most recent version of the script
        latest_script = script_repository.find_latest_version(script.story_id)
        if latest_script is None:
            # No scripts found - skip (invalid state)
            continue
            
        current_version = latest_script.version
        
        if current_version < lowest_version:
            lowest_version = current_version
            story_with_lowest_version = story
    
    return story_with_lowest_version


# Keep the old function for backward compatibility but mark as deprecated
def get_oldest_story_for_review(
    story_repository: StoryRepository
) -> Optional[Story]:
    """DEPRECATED: Get the oldest Story with state 'PrismQ.T.Review.Script.Readability'.
    
    This function is deprecated. Use get_story_for_review() instead, which selects
    stories based on the lowest current script version number.
    
    Args:
        story_repository: Repository for Story database operations
        
    Returns:
        Oldest Story in the readability review state, or None if none found
    """
    stories = story_repository.find_by_state_ordered_by_created(
        state=STATE_REVIEW_SCRIPT_READABILITY,
        ascending=True  # Oldest first
    )
    
    if stories:
        return stories[0]
    return None


def determine_next_state(accepted: bool) -> str:
    """Determine the next state based on review outcome.
    
    Args:
        accepted: Whether the script passed readability review
        
    Returns:
        The next state name
    """
    if not accepted:
        # Script not accepted - return to script refinement
        return STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    # Script accepted - proceed to story expert review
    return STATE_STORY_REVIEW


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
    
    return Review(
        text=text,
        score=score,
        created_at=datetime.now()
    )


def evaluate_script_readability(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3"
) -> Tuple[int, str, ReadabilityReview]:
    """Evaluate a script for voiceover readability.
    
    Uses the ScriptReadabilityChecker to perform comprehensive readability
    analysis including pronunciation, pacing, flow, and mouthfeel.
    
    Args:
        script_text: The script content to review
        script_id: Identifier for the script
        script_version: Version of the script
        
    Returns:
        Tuple of (score, review_text, readability_review)
    """
    # Use the existing readability checker
    readability_review = review_script_readability(
        script_text=script_text,
        script_id=script_id,
        script_version=script_version,
        pass_threshold=ACCEPTANCE_THRESHOLD
    )
    
    # Build review text from the readability review
    review_parts = [readability_review.summary]
    
    if readability_review.primary_concerns:
        review_parts.append("Concerns: " + "; ".join(readability_review.primary_concerns))
    
    if readability_review.voiceover_notes:
        review_parts.append("Notes: " + "; ".join(readability_review.voiceover_notes))
    
    # Add score breakdown
    score_details = (
        f"Scores - Pronunciation: {readability_review.pronunciation_score}, "
        f"Pacing: {readability_review.pacing_score}, "
        f"Flow: {readability_review.flow_score}, "
        f"Mouthfeel: {readability_review.mouthfeel_score}"
    )
    review_parts.append(score_details)
    
    review_text = " ".join(review_parts)
    
    return readability_review.overall_score, review_text, readability_review


def process_review_script_readability(
    connection: sqlite3.Connection,
    script_text: Optional[str] = None,
    script_id: Optional[str] = None,
    script_version: Optional[str] = None
) -> Optional[ReviewResult]:
    """Process the script readability review workflow stage.
    
    This function:
    1. Finds the Story with the lowest current script version in state 'PrismQ.T.Review.Script.Readability'
    2. Retrieves the Script associated with the Story via story.script_id
    3. Evaluates the script for voiceover readability
    4. Creates a Review record
    5. Updates the Story state based on review outcome
    
    Args:
        connection: SQLite database connection
        script_text: Optional script text override (for testing)
        script_id: Optional script ID override (for testing)
        script_version: Optional script version override (for testing)
        
    Returns:
        ReviewResult if a story was processed, None if no stories found
    """
    # Set up row factory for proper dict-like access
    connection.row_factory = sqlite3.Row
    
    story_repository = StoryRepository(connection)
    script_repository = ScriptRepository(connection)
    
    # Get story with lowest current script version in readability review state
    story = get_story_for_review(story_repository, script_repository)
    
    if story is None:
        return None
    
    # Get script text from database if not provided
    actual_script_text = script_text
    actual_script_id = script_id
    actual_script_version = script_version
    
    if actual_script_text is None and story.script_id is not None:
        # Get the script from the database
        script = script_repository.find_by_id(story.script_id)
        if script is not None:
            actual_script_text = script.text
            actual_script_id = str(script.id)
            actual_script_version = f"v{script.version}"
    
    # Fallback values for testing or if no script found
    actual_script_text = actual_script_text or "Sample script content for readability review"
    actual_script_id = actual_script_id or f"script-{story.script_id}" if story.script_id else "script-001"
    actual_script_version = actual_script_version or "v3"
    
    # Evaluate the script for readability
    score, review_text, readability_review = evaluate_script_readability(
        script_text=actual_script_text,
        script_id=actual_script_id,
        script_version=actual_script_version
    )
    
    # Create review
    review = create_review(score=score, text=review_text)
    
    # Determine if accepted (passes readability threshold)
    accepted = readability_review.passes
    
    # Determine next state
    new_state = determine_next_state(accepted=accepted)
    
    # Update story state
    story.update_state(new_state)
    story_repository.update(story)
    
    return ReviewResult(
        story=story,
        review=review,
        new_state=new_state,
        accepted=accepted,
        readability_review=readability_review
    )


def process_all_pending_reviews(
    connection: sqlite3.Connection
) -> List[ReviewResult]:
    """Process all pending script readability reviews.
    
    Args:
        connection: SQLite database connection
        
    Returns:
        List of ReviewResult for all processed stories
    """
    results = []
    
    while True:
        result = process_review_script_readability(connection=connection)
        
        if result is None:
            break
            
        results.append(result)
    
    return results


__all__ = [
    "ReviewResult",
    "process_review_script_readability",
    "process_all_pending_reviews",
    "get_oldest_story_for_review",
    "determine_next_state",
    "create_review",
    "evaluate_script_readability",
    "get_story_for_review",
    "ACCEPTANCE_THRESHOLD",
    "STATE_REVIEW_SCRIPT_READABILITY",
    "STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT",
    "STATE_STORY_REVIEW",
]
