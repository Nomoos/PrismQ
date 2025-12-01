"""Script Content Review Service - AI-powered content validation for scripts.

This module provides a service that:
1. Selects the oldest Story where state is PrismQ.T.Review.Script.Content
2. Generates content review using ContentReview model from T.Review.Content
3. Creates Review record and links via StoryReview
4. Updates Story state based on review result:
   - FAIL: PrismQ.T.Script.From.Title.Review.Script
   - PASS: PrismQ.T.Review.Script.Tone

This is the main entry point for automated script content review in the workflow.

Usage:
    >>> import sqlite3
    >>> from T.Review.Script.Content.script_content_review import ScriptContentReviewer
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> service = ScriptContentReviewer(conn)
    >>> 
    >>> # Process oldest story needing content review (by state)
    >>> result = service.process_oldest_story()
    >>> if result:
    ...     print(f"Reviewed story {result.story_id}, passes: {result.passes}")
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.story_review_repository import StoryReviewRepository
from T.Database.models.story import Story
from T.Database.models.review import Review
from T.Database.models.story_review import StoryReviewModel, ReviewType
from T.State.constants.state_names import StateNames

# Import ContentReview model from T.Review.Content directly
from T.Review.Content.content_review import (
    ContentReview,
    ContentIssue,
    ContentIssueType,
    ContentSeverity
)


# State constants for this service
INPUT_STATE = StateNames.REVIEW_SCRIPT_CONTENT  # PrismQ.T.Review.Script.Content
OUTPUT_STATE_PASS = StateNames.REVIEW_SCRIPT_TONE  # PrismQ.T.Review.Script.Tone
OUTPUT_STATE_FAIL = StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE  # PrismQ.T.Script.From.Script.Review.Title


@dataclass
class ContentReviewResult:
    """Result of content review for a story.
    
    Attributes:
        story_id: ID of the story processed
        review_id: ID of the created Review record (if successful)
        passes: Whether the content review passed
        overall_score: Content review score (0-100)
        error: Error message if review failed
        content_review: The ContentReview object with detailed results
        new_state: The state the story was transitioned to
    """
    story_id: int
    review_id: Optional[int] = None
    passes: bool = False
    overall_score: int = 0
    error: Optional[str] = None
    content_review: Optional[ContentReview] = None
    new_state: Optional[str] = None


class ScriptContentReviewer:
    """Service for reviewing script content for stories.
    
    This service implements the workflow step:
        Story (state=PrismQ.T.Review.Script.Content) → Content Review 
        → Story (state=PrismQ.T.Review.Script.Tone) if passes
        → Story (state=PrismQ.T.Script.From.Title.Review.Script) if fails
    
    Workflow:
        - Selects the oldest Story where state is PrismQ.T.Review.Script.Content
        - Retrieves the associated Script content
        - Performs content review (narrative, plot, character, pacing)
        - Creates Review record with score and text
        - Links Review to Story via StoryReview table
        - Updates Story state based on review result
    
    Attributes:
        INPUT_STATE: The state to look for stories needing content review
        OUTPUT_STATE_PASS: State to transition to if review passes
        OUTPUT_STATE_FAIL: State to transition to if review fails
    """
    
    INPUT_STATE = INPUT_STATE
    OUTPUT_STATE_PASS = OUTPUT_STATE_PASS
    OUTPUT_STATE_FAIL = OUTPUT_STATE_FAIL
    
    def __init__(
        self,
        connection: sqlite3.Connection,
        pass_threshold: int = 75,
        max_high_severity_issues: int = 3
    ):
        """Initialize the content reviewer service.
        
        Args:
            connection: SQLite database connection with row_factory = sqlite3.Row
            pass_threshold: Minimum score (0-100) required to pass review
            max_high_severity_issues: Maximum high severity issues before failing
        """
        self._conn = connection
        self.pass_threshold = pass_threshold
        self.max_high_severity_issues = max_high_severity_issues
        
        # Initialize repositories
        self.story_repo = StoryRepository(connection)
        self.script_repo = ScriptRepository(connection)
        self.story_review_repo = StoryReviewRepository(connection)
    
    def get_oldest_story(self) -> Optional[Story]:
        """Get the oldest story in the INPUT_STATE.
        
        Returns:
            The oldest Story entity in PrismQ.T.Review.Script.Content state,
            or None if no stories are found.
        """
        return self.story_repo.find_oldest_by_state(self.INPUT_STATE)
    
    def get_script_content(self, story: Story) -> Optional[str]:
        """Get the script content for a story.
        
        Args:
            story: The Story entity to get script for
            
        Returns:
            The script text content, or None if not found
        """
        if story.script_id is None:
            return None
        
        script = self.script_repo.find_by_id(story.script_id)
        if script is None:
            return None
        
        return script.text
    
    def perform_content_review(
        self,
        script_text: str,
        script_id: str,
        script_version: str = "v3"
    ) -> ContentReview:
        """Perform content review on script text.
        
        This method creates a ContentReview with simulated AI analysis.
        In production, this would integrate with an actual AI reviewer.
        
        Args:
            script_text: The script text to review
            script_id: Identifier for the script
            script_version: Version of the script
            
        Returns:
            ContentReview object with analysis results
        """
        # Create review with analysis scores
        # In production, these would come from AI analysis
        review = ContentReview(
            script_id=script_id,
            script_version=script_version,
            pass_threshold=self.pass_threshold,
            max_high_severity_issues=self.max_high_severity_issues
        )
        
        # Perform basic content analysis
        # (In production, this would use NLP/AI for deep analysis)
        scores = self._analyze_content(script_text)
        
        review.logic_score = scores['logic']
        review.plot_score = scores['plot']
        review.character_score = scores['character']
        review.pacing_score = scores['pacing']
        
        # Calculate overall score as weighted average
        review.overall_score = (
            scores['logic'] * 0.25 +
            scores['plot'] * 0.30 +
            scores['character'] * 0.25 +
            scores['pacing'] * 0.20
        )
        review.overall_score = int(review.overall_score)
        
        # Detect content issues
        issues = self._detect_content_issues(script_text)
        for issue in issues:
            review.add_issue(issue)
        
        # Recalculate pass status after setting scores
        review._recalculate_pass_status()
        
        # Generate summary
        review.summary = self._generate_summary(review)
        
        return review
    
    def _analyze_content(self, script_text: str) -> dict:
        """Analyze script content and return scores.
        
        This is a simplified analysis. In production, this would use
        AI/NLP for deep content analysis.
        
        Args:
            script_text: The script text to analyze
            
        Returns:
            Dictionary with scores for logic, plot, character, pacing
        """
        # Basic heuristic scoring based on text characteristics
        text_length = len(script_text)
        line_count = len(script_text.split('\n'))
        word_count = len(script_text.split())
        
        # Simple heuristics for demonstration
        # In production, these would be sophisticated AI metrics
        base_score = 80
        
        # Adjust based on content length
        if word_count < 100:
            length_penalty = 15
        elif word_count < 500:
            length_penalty = 5
        else:
            length_penalty = 0
        
        # Check for dialogue markers (suggests character development)
        dialogue_markers = script_text.count('"') + script_text.count("'")
        character_bonus = min(10, dialogue_markers // 5)
        
        # Check for scene/section markers (suggests structure)
        scene_markers = (
            script_text.lower().count('scene') +
            script_text.lower().count('act') +
            script_text.lower().count('chapter')
        )
        structure_bonus = min(10, scene_markers * 3)
        
        return {
            'logic': max(0, min(100, base_score - length_penalty + structure_bonus)),
            'plot': max(0, min(100, base_score - length_penalty + structure_bonus)),
            'character': max(0, min(100, base_score - length_penalty + character_bonus)),
            'pacing': max(0, min(100, base_score - length_penalty)),
        }
    
    def _detect_content_issues(self, script_text: str) -> list:
        """Detect content issues in script text.
        
        This is a simplified detection. In production, this would use
        AI/NLP for deep issue detection.
        
        Args:
            script_text: The script text to analyze
            
        Returns:
            List of ContentIssue objects
        """
        issues = []
        
        # Check for very short content (potential structural issue)
        word_count = len(script_text.split())
        if word_count < 50:
            issues.append(ContentIssue(
                issue_type=ContentIssueType.STRUCTURAL,
                severity=ContentSeverity.HIGH,
                section="Overall",
                description="Script content is very short",
                suggestion="Expand the script with more detail and narrative",
                impact="Insufficient content for meaningful story",
                confidence=90
            ))
        
        # Check for missing dialogue (character development)
        dialogue_count = script_text.count('"') + script_text.count("'")
        if dialogue_count < 2 and word_count > 100:
            issues.append(ContentIssue(
                issue_type=ContentIssueType.CHARACTER_MOTIVATION,
                severity=ContentSeverity.MEDIUM,
                section="Dialogue",
                description="Limited or no dialogue detected",
                suggestion="Add dialogue to develop characters and advance plot",
                impact="Character development may feel flat without dialogue",
                confidence=75
            ))
        
        # Check for repetitive content
        lines = script_text.split('\n')
        seen_lines = set()
        for i, line in enumerate(lines):
            stripped = line.strip().lower()
            if stripped and len(stripped) > 20:
                if stripped in seen_lines:
                    issues.append(ContentIssue(
                        issue_type=ContentIssueType.NARRATIVE_COHERENCE,
                        severity=ContentSeverity.LOW,
                        section=f"Line {i+1}",
                        description="Repetitive content detected",
                        suggestion="Remove or rephrase duplicate content",
                        impact="Repetition can disrupt narrative flow",
                        confidence=85
                    ))
                    break  # Only report first instance
                seen_lines.add(stripped)
        
        return issues
    
    def _generate_summary(self, review: ContentReview) -> str:
        """Generate a summary for the content review.
        
        Args:
            review: The ContentReview object
            
        Returns:
            Summary string
        """
        if review.passes:
            return (
                f"Content review PASSED with score {review.overall_score}%. "
                f"Logic: {review.logic_score}%, Plot: {review.plot_score}%, "
                f"Character: {review.character_score}%, Pacing: {review.pacing_score}%. "
                f"Script is ready for tone review."
            )
        else:
            issue_summary = f"{review.critical_count} critical, {review.high_count} high priority issues"
            return (
                f"Content review FAILED with score {review.overall_score}% "
                f"(threshold: {review.pass_threshold}%). "
                f"Issues: {issue_summary}. "
                f"Script needs refinement before proceeding."
            )
    
    def create_review_record(
        self,
        content_review: ContentReview
    ) -> Review:
        """Create a Review record from ContentReview.
        
        Args:
            content_review: The ContentReview with analysis results
            
        Returns:
            Review model instance (not yet persisted)
        """
        return Review(
            text=content_review.summary,
            score=content_review.overall_score
        )
    
    def _insert_review(self, review: Review) -> Review:
        """Insert Review record into database.
        
        Args:
            review: Review model to insert
            
        Returns:
            Review with id populated
        """
        cursor = self._conn.execute(
            "INSERT INTO Review (text, score, created_at) VALUES (?, ?, ?)",
            (review.text, review.score, review.created_at.isoformat())
        )
        self._conn.commit()
        review.id = cursor.lastrowid
        return review
    
    def link_review_to_story(
        self,
        story: Story,
        review: Review,
        version: int = 0
    ) -> StoryReviewModel:
        """Link a Review to a Story via StoryReview table.
        
        Args:
            story: The Story entity
            review: The Review entity (must have id)
            version: Story version being reviewed
            
        Returns:
            The created StoryReviewModel
        """
        story_review = StoryReviewModel(
            story_id=story.id,
            review_id=review.id,
            version=version,
            review_type=ReviewType.CONTENT
        )
        return self.story_review_repo.insert(story_review)
    
    def update_story_state(self, story: Story, passes: bool) -> Story:
        """Update story state based on review result.
        
        Args:
            story: The Story entity to update
            passes: Whether the content review passed
            
        Returns:
            The updated Story entity
        """
        if passes:
            story.state = self.OUTPUT_STATE_PASS
        else:
            story.state = self.OUTPUT_STATE_FAIL
        
        return self.story_repo.update(story)
    
    def process_oldest_story(self) -> Optional[ContentReviewResult]:
        """Process the oldest story needing content review.
        
        This is the main workflow method that:
        1. Finds the oldest story in PrismQ.T.Review.Script.Content state
        2. Retrieves the script content
        3. Performs content review
        4. Creates Review record
        5. Links Review to Story
        6. Updates Story state
        
        Returns:
            ContentReviewResult with processing results, or None if no story found
        """
        # Get oldest story needing content review
        story = self.get_oldest_story()
        if story is None:
            return None
        
        # Get script content
        script_text = self.get_script_content(story)
        if script_text is None:
            return ContentReviewResult(
                story_id=story.id,
                error=f"Script not found for story {story.id}"
            )
        
        # Perform content review
        content_review = self.perform_content_review(
            script_text=script_text,
            script_id=str(story.script_id),
            script_version="v3"
        )
        
        # Create and persist Review record
        review = self.create_review_record(content_review)
        review = self._insert_review(review)
        
        # Link Review to Story
        self.link_review_to_story(story, review)
        
        # Update Story state
        story = self.update_story_state(story, content_review.passes)
        
        return ContentReviewResult(
            story_id=story.id,
            review_id=review.id,
            passes=content_review.passes,
            overall_score=content_review.overall_score,
            content_review=content_review,
            new_state=story.state
        )


def review_oldest_story_content(
    connection: sqlite3.Connection,
    pass_threshold: int = 75
) -> Optional[ContentReviewResult]:
    """Convenience function to review oldest story content.
    
    Creates a ScriptContentReviewer and processes the oldest story.
    
    Args:
        connection: SQLite database connection
        pass_threshold: Minimum score required to pass
        
    Returns:
        ContentReviewResult or None if no story found
        
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> result = review_oldest_story_content(conn)
        >>> if result:
        ...     print(f"Story {result.story_id}: {'PASS' if result.passes else 'FAIL'}")
    """
    service = ScriptContentReviewer(connection, pass_threshold=pass_threshold)
    return service.process_oldest_story()
