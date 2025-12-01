"""Script Consistency Review Service - Process stories for consistency review.

This module implements PrismQ.T.Review.Script.Consistency workflow step.
It:
1. Selects the oldest Story where state is PrismQ.T.Review.Script.Consistency
2. Performs consistency review on the script content
3. Creates a Review record with text and score
4. Links the Review to Story via StoryReview table
5. Updates Story state based on review result:
   - If NOT accepted: PrismQ.T.Script.From.Title.Review.Script
   - If accepted: PrismQ.T.Review.Script.Content

Usage:
    >>> import sqlite3
    >>> from T.Review.Script.Consistency.src.script_consistency_review_service import (
    ...     ScriptConsistencyReviewService,
    ...     process_oldest_consistency_review
    ... )
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> service = ScriptConsistencyReviewService(conn)
    >>> 
    >>> # Process oldest story in consistency review state
    >>> result = service.process_oldest_story()
    >>> if result.success:
    ...     print(f"Review completed for story {result.story_id}")
    ...     print(f"Score: {result.score}, Passes: {result.passes}")
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.review_repository import ReviewRepository
from T.Database.repositories.story_review_repository import StoryReviewRepository
from T.Database.models.story import Story
from T.Database.models.review import Review
from T.Database.models.story_review import StoryReviewModel, ReviewType
from T.State.constants.state_names import StateNames

# Import consistency review functionality using direct path to avoid circular import
from T.Review.Script.Consistency.consistency_review import (
    ScriptConsistencyChecker,
    ConsistencyReview,
    get_consistency_feedback
)


# State constants
STATE_REVIEW_SCRIPT_CONSISTENCY = StateNames.REVIEW_SCRIPT_CONSISTENCY
STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT = StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
STATE_REVIEW_SCRIPT_CONTENT = StateNames.REVIEW_SCRIPT_CONTENT

# Default pass threshold for consistency review
DEFAULT_PASS_THRESHOLD = 80


@dataclass
class ConsistencyReviewResult:
    """Result of script consistency review processing.
    
    Attributes:
        story_id: ID of the processed story
        review_id: ID of the created Review record (if successful)
        script_id: ID of the reviewed script
        previous_state: Story state before processing
        new_state: Story state after processing
        success: Whether the operation succeeded
        passes: Whether the consistency review passed
        score: Consistency review score (0-100)
        error: Error message if failed
        consistency_review: The ConsistencyReview object with details
    """
    story_id: Optional[int] = None
    review_id: Optional[int] = None
    script_id: Optional[int] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    success: bool = False
    passes: bool = False
    score: int = 0
    error: Optional[str] = None
    consistency_review: Optional[ConsistencyReview] = None


class ScriptConsistencyReviewService:
    """Service for PrismQ.T.Review.Script.Consistency workflow state.
    
    This service implements the workflow step that:
    1. Selects the oldest Story where state is PrismQ.T.Review.Script.Consistency
    2. Performs consistency review on the script
    3. Creates a Review record
    4. Links Review to Story via StoryReview table
    5. Updates Story state based on review result:
       - NOT accepted: PrismQ.T.Script.From.Title.Review.Script
       - Accepted: PrismQ.T.Review.Script.Content
    
    The service processes stories in FIFO order (oldest first) to ensure
    fair processing of the backlog.
    
    Attributes:
        story_repo: Repository for Story operations
        script_repo: Repository for Script operations
        review_repo: Repository for Review operations
        story_review_repo: Repository for StoryReview operations
        consistency_checker: Checker for performing consistency review
        pass_threshold: Minimum score required to pass (default 80)
    
    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> service = ScriptConsistencyReviewService(conn)
        >>> 
        >>> # Process the oldest story in the state
        >>> result = service.process_oldest_story()
        >>> if result.success:
        ...     print(f"Review completed: score={result.score}, passes={result.passes}")
        ...     print(f"New state: {result.new_state}")
    """
    
    INPUT_STATE = STATE_REVIEW_SCRIPT_CONSISTENCY
    OUTPUT_STATE_PASS = STATE_REVIEW_SCRIPT_CONTENT
    OUTPUT_STATE_FAIL = STATE_SCRIPT_FROM_TITLE_REVIEW_SCRIPT
    
    def __init__(
        self,
        connection: sqlite3.Connection,
        pass_threshold: int = DEFAULT_PASS_THRESHOLD
    ):
        """Initialize the service with database connection.
        
        Args:
            connection: SQLite database connection with row_factory = sqlite3.Row
            pass_threshold: Minimum score (0-100) required to pass review
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.script_repo = ScriptRepository(connection)
        self.review_repo = ReviewRepository(connection)
        self.story_review_repo = StoryReviewRepository(connection)
        self.pass_threshold = pass_threshold
        self.consistency_checker = ScriptConsistencyChecker(pass_threshold=pass_threshold)
    
    def count_pending(self) -> int:
        """Count stories waiting in the input state.
        
        Returns:
            Number of stories with state PrismQ.T.Review.Script.Consistency.
        """
        return self.story_repo.count_by_state(self.INPUT_STATE)
    
    def get_oldest_story(self) -> Optional[Story]:
        """Get the oldest story in the input state.
        
        Returns:
            The oldest Story in state PrismQ.T.Review.Script.Consistency,
            or None if no stories are in this state.
        """
        return self.story_repo.find_oldest_by_state(self.INPUT_STATE)
    
    def process_oldest_story(self) -> ConsistencyReviewResult:
        """Process the oldest story in the input state.
        
        This method:
        1. Finds the oldest Story with state PrismQ.T.Review.Script.Consistency
        2. Retrieves the script content
        3. Performs consistency review
        4. Creates a Review record
        5. Links Review to Story via StoryReview table
        6. Updates Story state based on review result
        
        Returns:
            ConsistencyReviewResult with processing details.
            If no stories are pending, returns result with success=False.
        """
        result = ConsistencyReviewResult()
        
        # Find the oldest story in the input state
        story = self.get_oldest_story()
        
        if story is None:
            result.error = f"No stories found in state {self.INPUT_STATE}"
            return result
        
        result.story_id = story.id
        result.previous_state = story.state
        
        # Validate story has script_id
        if not story.script_id:
            result.error = f"Story {story.id} has no script_id"
            return result
        
        result.script_id = story.script_id
        
        try:
            # Get the script content
            script = self.script_repo.find_by_id(story.script_id)
            if not script:
                result.error = f"Script with id {story.script_id} not found"
                return result
            
            script_text = script.text
            
            # Perform consistency review
            consistency_review = self.consistency_checker.review_script(
                script_text=script_text,
                script_id=f"script-{story.script_id}",
                script_version=f"v{script.version}"
            )
            
            result.consistency_review = consistency_review
            result.score = consistency_review.overall_score
            result.passes = consistency_review.passes
            
            # Get feedback for review text
            feedback = get_consistency_feedback(consistency_review)
            review_text = self._format_review_text(consistency_review, feedback)
            
            # Create Review record
            review = Review(
                text=review_text,
                score=consistency_review.overall_score
            )
            saved_review = self.review_repo.insert(review)
            result.review_id = saved_review.id
            
            # Link Review to Story via StoryReview
            story_review = StoryReviewModel(
                story_id=story.id,
                review_id=saved_review.id,
                version=script.version,
                review_type=ReviewType.CONSISTENCY
            )
            self.story_review_repo.insert(story_review)
            
            # Update story state based on review result
            if consistency_review.passes:
                new_state = self.OUTPUT_STATE_PASS
            else:
                new_state = self.OUTPUT_STATE_FAIL
            
            story.state = new_state
            story.updated_at = datetime.now()
            self.story_repo.update(story)
            
            result.new_state = new_state
            result.success = True
            
        except Exception as e:
            result.error = f"Consistency review failed: {str(e)}"
        
        return result
    
    def _format_review_text(
        self,
        consistency_review: ConsistencyReview,
        feedback: dict
    ) -> str:
        """Format the review text from consistency review results.
        
        Args:
            consistency_review: The ConsistencyReview object
            feedback: Feedback dictionary from get_consistency_feedback
            
        Returns:
            Formatted review text string
        """
        lines = [
            f"Consistency Review - Score: {consistency_review.overall_score}/100",
            f"Status: {'PASS' if consistency_review.passes else 'FAIL'}",
            "",
            f"Summary: {consistency_review.summary}",
            "",
            f"Character Score: {consistency_review.character_score}/100",
            f"Timeline Score: {consistency_review.timeline_score}/100",
            f"Location Score: {consistency_review.location_score}/100",
            f"Detail Score: {consistency_review.detail_score}/100",
        ]
        
        if consistency_review.primary_concerns:
            lines.append("")
            lines.append("Primary Concerns:")
            for concern in consistency_review.primary_concerns:
                lines.append(f"  - {concern}")
        
        if consistency_review.issues:
            lines.append("")
            lines.append(f"Issues Found: {len(consistency_review.issues)}")
            for issue in consistency_review.issues[:5]:  # Limit to first 5
                lines.append(f"  [{issue.severity.value.upper()}] {issue.location}: {issue.description}")
        
        lines.append("")
        lines.append(f"Next Action: {feedback.get('next_action', 'N/A')}")
        
        return "\n".join(lines)
    
    def process_all_pending(
        self,
        limit: Optional[int] = None
    ) -> List[ConsistencyReviewResult]:
        """Process all stories in the input state.
        
        This method processes stories in FIFO order (oldest first) until
        all are processed or the limit is reached.
        
        Args:
            limit: Optional maximum number of stories to process.
            
        Returns:
            List of ConsistencyReviewResult for each processed story.
        """
        results = []
        processed = 0
        
        while True:
            if limit is not None and processed >= limit:
                break
            
            result = self.process_oldest_story()
            
            # Stop if no more stories to process
            if result.story_id is None:
                break
            
            results.append(result)
            processed += 1
        
        return results
    
    def get_processing_summary(
        self,
        results: List[ConsistencyReviewResult]
    ) -> dict:
        """Get a summary of processing results.
        
        Args:
            results: List of ConsistencyReviewResult from processing.
            
        Returns:
            Dictionary with summary statistics.
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success and r.story_id is not None]
        passed = [r for r in successful if r.passes]
        not_passed = [r for r in successful if not r.passes]
        
        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "reviews_passed": len(passed),
            "reviews_not_passed": len(not_passed),
            "success_rate": len(successful) / len(results) if results else 0,
            "pass_rate": len(passed) / len(successful) if successful else 0,
            "average_score": sum(r.score for r in successful) / len(successful) if successful else 0,
            "successful_story_ids": [r.story_id for r in successful],
            "failed_story_ids": [r.story_id for r in failed],
            "errors": {r.story_id: r.error for r in failed if r.story_id is not None},
            "input_state": self.INPUT_STATE,
            "output_state_pass": self.OUTPUT_STATE_PASS,
            "output_state_fail": self.OUTPUT_STATE_FAIL,
        }


def process_oldest_consistency_review(
    connection: sqlite3.Connection,
    pass_threshold: int = DEFAULT_PASS_THRESHOLD
) -> ConsistencyReviewResult:
    """Process the oldest story in PrismQ.T.Review.Script.Consistency state.
    
    This is the main entry point for the PrismQ.T.Review.Script.Consistency module.
    It finds the oldest story in the state, performs consistency review,
    and updates the story state based on the result.
    
    Args:
        connection: SQLite database connection.
        pass_threshold: Minimum score (0-100) required to pass review.
        
    Returns:
        ConsistencyReviewResult with processing details.
        
    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> result = process_oldest_consistency_review(conn)
        >>> if result.success:
        ...     print(f"Review completed: score={result.score}")
        ...     print(f"Story state changed to {result.new_state}")
        ... else:
        ...     print(f"Error: {result.error}")
    """
    service = ScriptConsistencyReviewService(connection, pass_threshold=pass_threshold)
    return service.process_oldest_story()


def process_all_consistency_reviews(
    connection: sqlite3.Connection,
    pass_threshold: int = DEFAULT_PASS_THRESHOLD,
    limit: Optional[int] = None
) -> dict:
    """Process all stories in PrismQ.T.Review.Script.Consistency state.
    
    Args:
        connection: SQLite database connection.
        pass_threshold: Minimum score (0-100) required to pass review.
        limit: Optional maximum number of stories to process.
        
    Returns:
        Dictionary with processing summary.
        
    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> summary = process_all_consistency_reviews(conn)
        >>> print(f"Processed {summary['total_processed']} stories")
        >>> print(f"Pass rate: {summary['pass_rate']:.1%}")
    """
    service = ScriptConsistencyReviewService(connection, pass_threshold=pass_threshold)
    results = service.process_all_pending(limit=limit)
    return service.get_processing_summary(results)
