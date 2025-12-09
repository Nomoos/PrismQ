"""Script Grammar Review Service - Process stories in PrismQ.T.Review.Script.Grammar state.

This module implements the workflow step that:
1. Selects the oldest Story where state is PrismQ.T.Review.Script.Grammar
2. Reviews the script for grammar issues
3. Creates a Review record with the results
4. Links the Review to Script directly via FK (Script.review_id)
5. Updates the Story state based on review outcome:
   - If review passes: PrismQ.T.Review.Script.Consistency
   - If review fails: PrismQ.T.Script.From.Title.Review.Script

Note: This module reviews Scripts, not Stories. The Review is linked directly
to Script via Script.review_id FK. StoryReview linking table is not used here
as it is reserved for Story-level reviews only.

This is the main entry point for grammar review in the quality review workflow.

Usage:
    >>> import sqlite3
    >>> from T.Review.Script.Grammar.script_grammar_service import ScriptGrammarReviewService
    >>>
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> service = ScriptGrammarReviewService(conn)
    >>>
    >>> # Process oldest story in grammar review state
    >>> result = service.process_oldest_story()
    >>> if result.success:
    ...     print(f"Review score: {result.score}")
    ...     print(f"Review passed: {result.passes}")
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from Model.Database.models.review import Review
from Model.Database.models.story import Story
from Model.Database.repositories.review_repository import ReviewRepository
from Model.Database.repositories.script_repository import ScriptRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.State.constants.state_names import StateNames

# Import the grammar checker from the same package
from .script_grammar_review import (
    ScriptGrammarChecker,
    get_grammar_feedback,
    review_script_grammar,
)

# State constants for this module
INPUT_STATE = StateNames.REVIEW_SCRIPT_GRAMMAR  # PrismQ.T.Review.Script.Grammar
OUTPUT_STATE_PASS = StateNames.REVIEW_SCRIPT_CONSISTENCY  # PrismQ.T.Review.Script.Consistency
OUTPUT_STATE_FAIL = (
    StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT
)  # PrismQ.T.Script.From.Title.Review.Script

# Default pass threshold for grammar review
DEFAULT_PASS_THRESHOLD = 85


@dataclass
class GrammarReviewResult:
    """Result of grammar review processing.

    Attributes:
        story_id: ID of the processed story
        script_id: ID of the script that was reviewed
        review_id: ID of the created review (if successful)
        previous_state: The state before processing
        new_state: The state after processing
        success: Whether the operation succeeded
        passes: Whether the script passed grammar review
        score: Grammar review score (0-100)
        error: Error message if failed
        summary: Summary of review feedback
        issues_count: Number of grammar issues found
    """

    story_id: Optional[int] = None
    script_id: Optional[int] = None
    review_id: Optional[int] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    success: bool = False
    passes: bool = False
    score: int = 0
    error: Optional[str] = None
    summary: str = ""
    issues_count: int = 0


class ScriptGrammarReviewService:
    """Service for PrismQ.T.Review.Script.Grammar workflow state.

    This service implements the grammar review step that:
    1. Selects the oldest Story where state is PrismQ.T.Review.Script.Grammar
    2. Reviews the script for grammar, spelling, punctuation, and tense issues
    3. Creates a Review record with the results
    4. Links the Review to Script directly via FK (Script.review_id)
    5. Updates the Story state based on review outcome:
       - PASS: PrismQ.T.Review.Script.Consistency
       - FAIL: PrismQ.T.Script.From.Title.Review.Script

    Note: This reviews Scripts, not Stories. StoryReview linking table is not
    used here as it is reserved for Story-level reviews only.

    The service processes stories in FIFO order (oldest first) to ensure
    fair processing of the backlog.

    Attributes:
        story_repo: Repository for Story operations
        script_repo: Repository for Script operations
        review_repo: Repository for Review operations
        grammar_checker: Grammar checker for reviewing scripts

    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> service = ScriptGrammarReviewService(conn)
        >>>
        >>> # Process the oldest story in grammar review state
        >>> result = service.process_oldest_story()
        >>> if result.success:
        ...     print(f"Story {result.story_id}: Score={result.score}, Passes={result.passes}")
        ... else:
        ...     print(f"Error: {result.error}")
    """

    def __init__(
        self, connection: sqlite3.Connection, pass_threshold: int = DEFAULT_PASS_THRESHOLD
    ):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection with row_factory = sqlite3.Row
            pass_threshold: Minimum score (0-100) required to pass grammar review
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.script_repo = ScriptRepository(connection)
        self.review_repo = ReviewRepository(connection)
        self.grammar_checker = ScriptGrammarChecker(pass_threshold=pass_threshold)
        self.pass_threshold = pass_threshold

    def count_pending(self) -> int:
        """Count stories waiting in the grammar review state.

        Returns:
            Number of stories with state PrismQ.T.Review.Script.Grammar.
        """
        return self.story_repo.count_by_state(INPUT_STATE)

    def get_oldest_story(self) -> Optional[Story]:
        """Get the oldest story in the grammar review state.

        Returns:
            The oldest Story in state PrismQ.T.Review.Script.Grammar,
            or None if no stories are in this state.
        """
        return self.story_repo.find_oldest_by_state(INPUT_STATE)

    def process_oldest_story(self) -> GrammarReviewResult:
        """Process the oldest story in the grammar review state.

        This method:
        1. Finds the oldest Story with state PrismQ.T.Review.Script.Grammar
        2. Gets the current script for the story
        3. Performs grammar review on the script
        4. Creates a Review record with the results
        5. Links the Review to Script via FK (Script.review_id)
        6. Updates the Story state:
           - PASS: PrismQ.T.Review.Script.Consistency
           - FAIL: PrismQ.T.Script.From.Title.Review.Script

        Returns:
            GrammarReviewResult with processing details.
            If no stories are pending, returns result with success=False.
        """
        result = GrammarReviewResult()

        # Find the oldest story in the input state
        story = self.get_oldest_story()

        if story is None:
            result.error = "No stories found in state PrismQ.T.Review.Script.Grammar"
            return result

        result.story_id = story.id
        result.previous_state = story.state

        # Get the current script for the story
        try:
            scripts = self.script_repo.find_by_story_id(story.id)
            if not scripts:
                result.error = f"Story {story.id} has no scripts"
                return result

            # Get the latest script (highest version)
            current_script = max(scripts, key=lambda s: s.version)
            result.script_id = current_script.id

            # Perform grammar review
            grammar_review = self.grammar_checker.review_script(
                script_text=current_script.text,
                script_id=str(current_script.id),
                script_version=f"v{current_script.version}",
            )

            # Get structured feedback
            feedback = get_grammar_feedback(grammar_review)

            # Create review text from feedback
            review_text = self._format_review_text(grammar_review, feedback)

            # Create and save Review record
            review = Review(text=review_text, score=grammar_review.overall_score)
            saved_review = self.review_repo.insert(review)
            result.review_id = saved_review.id

            # Link Review to Script directly via FK (Script.review_id)
            # Note: StoryReview linking table is not used for Script reviews
            self.script_repo.update_review_id(current_script.id, saved_review.id)

            # Update result with review outcome
            result.score = grammar_review.overall_score
            result.passes = grammar_review.passes
            result.issues_count = len(grammar_review.issues)
            result.summary = grammar_review.summary

            # Determine next state based on review outcome
            if grammar_review.passes:
                new_state = OUTPUT_STATE_PASS
            else:
                new_state = OUTPUT_STATE_FAIL

            # Update story state
            story.state = new_state
            story.updated_at = datetime.now()
            self.story_repo.update(story)

            result.new_state = new_state
            result.success = True

        except Exception as e:
            result.error = f"Grammar review failed: {str(e)}"

        return result

    def _format_review_text(self, grammar_review, feedback: dict) -> str:
        """Format grammar review results into review text.

        Args:
            grammar_review: GrammarReview object with review details
            feedback: Structured feedback dictionary

        Returns:
            Formatted review text string
        """
        lines = []
        lines.append(f"Grammar Review - Score: {grammar_review.overall_score}/100")
        lines.append(f"Status: {'PASS' if grammar_review.passes else 'FAIL'}")
        lines.append("")
        lines.append(f"Summary: {grammar_review.summary}")
        lines.append("")

        if grammar_review.primary_concerns:
            lines.append("Primary Concerns:")
            for concern in grammar_review.primary_concerns:
                lines.append(f"  - {concern}")
            lines.append("")

        if grammar_review.quick_fixes:
            lines.append("Quick Fixes:")
            for fix in grammar_review.quick_fixes:
                lines.append(f"  - {fix}")
            lines.append("")

        if grammar_review.issues:
            lines.append(f"Issues Found ({len(grammar_review.issues)}):")
            for issue in grammar_review.issues[:10]:  # Limit to first 10 issues
                lines.append(
                    f"  Line {issue.line_number} [{issue.severity.value}]: {issue.explanation}"
                )
            if len(grammar_review.issues) > 10:
                lines.append(f"  ... and {len(grammar_review.issues) - 10} more issues")

        return "\n".join(lines)

    def process_all_pending(self, limit: Optional[int] = None) -> List[GrammarReviewResult]:
        """Process all stories in the grammar review state.

        This method processes stories in FIFO order (oldest first) until
        all are processed or the limit is reached.

        Args:
            limit: Optional maximum number of stories to process.

        Returns:
            List of GrammarReviewResult for each processed story.
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

    def get_processing_summary(self, results: List[GrammarReviewResult]) -> dict:
        """Get a summary of processing results.

        Args:
            results: List of GrammarReviewResult from processing.

        Returns:
            Dictionary with summary statistics.
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success and r.story_id is not None]
        passed = [r for r in results if r.success and r.passes]
        not_passed = [r for r in results if r.success and not r.passes]

        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "passed_review": len(passed),
            "failed_review": len(not_passed),
            "success_rate": len(successful) / len(results) if results else 0,
            "pass_rate": len(passed) / len(successful) if successful else 0,
            "average_score": (
                sum(r.score for r in successful) / len(successful) if successful else 0
            ),
            "total_issues": sum(r.issues_count for r in successful),
            "successful_story_ids": [r.story_id for r in successful],
            "failed_story_ids": [r.story_id for r in failed],
            "passed_story_ids": [r.story_id for r in passed],
            "not_passed_story_ids": [r.story_id for r in not_passed],
            "errors": {r.story_id: r.error for r in failed if r.story_id is not None},
            "input_state": INPUT_STATE,
            "output_state_pass": OUTPUT_STATE_PASS,
            "output_state_fail": OUTPUT_STATE_FAIL,
        }


def process_oldest_grammar_review(
    connection: sqlite3.Connection, pass_threshold: int = DEFAULT_PASS_THRESHOLD
) -> GrammarReviewResult:
    """Process the oldest story in PrismQ.T.Review.Script.Grammar state.

    This is the main entry point for the PrismQ.T.Review.Script.Grammar module.
    It finds the oldest story in the state, performs grammar review, and updates
    the story state based on the review outcome.

    Args:
        connection: SQLite database connection.
        pass_threshold: Minimum score required to pass (default 85).

    Returns:
        GrammarReviewResult with processing details.

    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> result = process_oldest_grammar_review(conn)
        >>> if result.success:
        ...     print(f"Score: {result.score}")
        ...     print(f"Passes: {result.passes}")
        ...     print(f"New state: {result.new_state}")
        ... else:
        ...     print(f"Error: {result.error}")
    """
    service = ScriptGrammarReviewService(connection, pass_threshold)
    return service.process_oldest_story()
