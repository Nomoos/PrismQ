"""Story Content Service - Generate content for stories from Idea and Title.

This module provides a service that:
1. Selects the oldest Story where state is PrismQ.T.Content.From.Idea.Title
2. Generates scripts using the ContentGenerator from Idea and Title
3. Updates the Story with the generated Content
4. Changes state to PrismQ.T.Review.Title.From.Content

This is the main entry point for automated content generation in the workflow.

Usage:
    >>> import sqlite3
    >>> from T.Content.From.Idea.Title.src.story_content_service import StoryContentService
    >>>
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> service = StoryContentService(conn)
    >>>
    >>> # Process oldest story needing script (by state)
    >>> result = service.process_oldest_story()
    >>> if result:
    ...     print(f"Generated script for story {result.story_id}")
    >>>
    >>> # Process all stories needing scripts
    >>> results = service.process_stories_needing_contents()
    >>> print(f"Generated {len(results)} scripts")
"""

import json
import logging
import sqlite3

# Import Idea from Idea module
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from Model.Database.models.content import Content as ScriptModel
from Model.Database.models.story import Story
from Model.Database.repositories.content_repository import ContentRepository
from Model.Database.repositories.story_repository import StoryRepository
from Model.Database.repositories.title_repository import TitleRepository
from Model import StateNames

# Import ContentGenerator from local module
from .content_generator import (
    PlatformTarget,
    ContentGenerator,
    ContentGeneratorConfig,
    ContentStructure,
    ContentTone,
    ContentV1,
)

logger = logging.getLogger(__name__)

_current_file = Path(__file__)
# Navigate: src -> Title -> Idea -> From -> Content -> T
# Path: T/Content/From/Idea/Title/src/story_content_service.py
# Up 6 levels to T/, then into Idea/Model/src
_t_module_dir = _current_file.parent.parent.parent.parent.parent.parent
_idea_model_path = _t_module_dir / "Idea" / "Model" / "src"
sys.path.insert(0, str(_idea_model_path))

from idea import ContentGenre, Idea


@dataclass
class ContentGenerationResult:
    """Result of content generation for a story.

    Attributes:
        story_id: ID of the story processed
        content_id: ID of the generated script (if successful)
        success: Whether content generation was successful
        error: Error message if generation failed
        script_v1: The generated ContentV1 object (if successful)
    """

    story_id: int
    content_id: Optional[int] = None
    success: bool = False
    error: Optional[str] = None
    script_v1: Optional[ContentV1] = None


class StoryContentService:
    """Service for generating scripts for stories from Idea and Title.

    This service implements the workflow step:
        Story (state=PrismQ.T.Content.From.Idea.Title) → Content Generation
        → Story (state=PrismQ.T.Review.Title.From.Content)

    Primary workflow (state-based):
        - Selects the oldest Story where state is PrismQ.T.Content.From.Idea.Title
        - Generates a Content (version 0) from Idea and Title
        - Updates Story state to PrismQ.T.Review.Title.From.Content

    Legacy workflow (content-based):
        - Queries for stories that have idea_json and title_id but no content_id
        - Generates scripts and updates stories

    Attributes:
        story_repo: Repository for Story operations
        content_repo: Repository for Content operations
        title_repo: Repository for Title operations
        content_generator: Generator for creating scripts

    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> service = StoryContentService(conn)
        >>>
        >>> # Process oldest story by state (primary workflow)
        >>> result = service.process_oldest_story()
        >>> if result and result.success:
        ...     print(f"Generated script for story {result.story_id}")
        >>>
        >>> # Process all stories (legacy workflow)
        >>> results = service.process_stories_needing_contents()
        >>> successful = [r for r in results if r.success]
        >>> print(f"Successfully generated {len(successful)} scripts")
    """
    
    # State constant for this service
    CURRENT_STATE = StateNames.CONTENT_FROM_IDEA_TITLE

    def __init__(
        self,
        connection: sqlite3.Connection,
        content_generator_config: Optional[ContentGeneratorConfig] = None,
    ):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection with row_factory = sqlite3.Row
            content_generator_config: Optional configuration for content generation
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.content_repo = ContentRepository(connection)
        self.title_repo = TitleRepository(connection)

        config = content_generator_config or ContentGeneratorConfig(
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            target_duration_seconds=90,
            structure_type=ContentStructure.HOOK_DELIVER_CTA,
            include_cta=True,
            tone=ContentTone.ENGAGING,
        )
        self.content_generator = ContentGenerator(config)

    def count_stories_needing_contents(self) -> int:
        """Count stories that need content generation.

        Returns:
            Number of stories ready for content generation.
        """
        return self.story_repo.count_needing_content()

    def get_stories_needing_contents(self) -> List[Story]:
        """Get all stories that need content generation.

        Returns:
            List of Story objects ready for content generation.
        """
        return self.story_repo.find_needing_content()

    # === State-based workflow methods (Primary) ===

    def get_oldest_story_by_state(self) -> Optional[Story]:
        """Get the oldest story where state is PrismQ.T.Content.From.Idea.Title.

        This is the primary method for the state-based workflow.
        Selects the oldest story (by created_at) with the correct state.

        Returns:
            The oldest Story with state PrismQ.T.Content.From.Idea.Title,
            or None if no such stories exist.

        Example:
            >>> story = service.get_oldest_story_by_state()
            >>> if story:
            ...     print(f"Found story {story.id} created at {story.created_at}")
        """
        stories = self.story_repo.find_by_state_ordered_by_created(
            StateNames.SCRIPT_FROM_IDEA_TITLE, ascending=True  # Oldest first
        )
        return stories[0] if stories else None

    def count_stories_by_state(self) -> int:
        """Count stories where state is PrismQ.T.Content.From.Idea.Title.

        Returns:
            Number of stories with state PrismQ.T.Content.From.Idea.Title.
        """
        return self.story_repo.count_by_state(StateNames.SCRIPT_FROM_IDEA_TITLE)

    def process_oldest_story(self) -> Optional[ContentGenerationResult]:
        """Process the oldest story with state PrismQ.T.Content.From.Idea.Title.

        This is the primary entry point for the state-based workflow.
        It:
        1. Selects the oldest Story where state is PrismQ.T.Content.From.Idea.Title
        2. Generates a Content (version 0) from Idea and Title
        3. Updates Story state to PrismQ.T.Review.Title.From.Content

        Returns:
            ContentGenerationResult if a story was processed, None if no stories found.

        Example:
            >>> result = service.process_oldest_story()
            >>> if result and result.success:
            ...     print(f"Generated script {result.content_id} for story {result.story_id}")
            >>> elif result:
            ...     print(f"Failed: {result.error}")
            >>> else:
            ...     print("No stories to process")
        """
        story = self.get_oldest_story_by_state()
        if not story:
            return None

        return self._generate_content_with_state_transition(story)

    def _generate_content_with_state_transition(self, story: Story) -> ContentGenerationResult:
        """Generate script and transition state to PrismQ.T.Review.Title.From.Content.

        Internal method that handles the state-based workflow content generation.
        Includes idempotency checks to prevent duplicate processing.

        Args:
            story: Story object with state PrismQ.T.Content.From.Idea.Title

        Returns:
            ContentGenerationResult with success status and details
        """
        result = ContentGenerationResult(story_id=story.id)

        # Idempotency check: If story already has content, don't regenerate
        if story.has_content():
            result.error = f"Story {story.id} already has content_id={story.content_id}. Skipping duplicate generation."
            logger.warning(result.error)
            return result

        # Validate story has required content
        if not story.has_idea():
            result.error = "Story does not have idea_json set"
            logger.error(f"Story {story.id}: {result.error}")
            return result

        if not story.has_title():
            result.error = "Story does not have title_id set"
            logger.error(f"Story {story.id}: {result.error}")
            return result

        try:
            logger.info(f"Starting content generation for story {story.id}")
            
            # Parse the Idea from JSON
            idea_data = json.loads(story.idea_json)
            idea = Idea.from_dict(idea_data)
            logger.debug(f"Story {story.id}: Parsed idea successfully")

            # Get the Title text
            title = self.title_repo.find_by_id(story.title_id)
            if not title:
                result.error = f"Title with id {story.title_id} not found"
                logger.error(f"Story {story.id}: {result.error}")
                return result

            title_text = title.text
            logger.debug(f"Story {story.id}: Retrieved title '{title_text}'")

            # Generate the script
            logger.info(f"Story {story.id}: Generating content with AI")
            script_v1 = self.content_generator.generate_content_v1(idea=idea, title=title_text)
            logger.info(f"Story {story.id}: Content generated successfully ({len(script_v1.full_text)} chars)")

            # Create Content model for database
            script_model = ScriptModel(
                story_id=story.id, version=0, text=script_v1.full_text  # First version
            )

            # Save to database
            logger.debug(f"Story {story.id}: Saving content to database")
            saved_content = self.content_repo.insert(script_model)
            logger.info(f"Story {story.id}: Content saved with id={saved_content.id}")

            # Update the story with script reference and transition state
            story.content_id = saved_content.id
            story.update_state(StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA)
            self.story_repo.update(story)
            logger.info(f"Story {story.id}: State updated to {StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA}")

            # Populate result
            result.success = True
            result.content_id = saved_content.id
            result.script_v1 = script_v1

        except json.JSONDecodeError as e:
            result.error = f"Failed to parse idea_json: {str(e)}"
            logger.error(f"Story {story.id}: {result.error}")
        except ValueError as e:
            result.error = f"Invalid idea or title: {str(e)}"
            logger.error(f"Story {story.id}: {result.error}")
        except Exception as e:
            result.error = f"Content generation failed: {str(e)}"
            logger.exception(f"Story {story.id}: Unexpected error during content generation")

        return result

    # === Legacy workflow methods (content-based) ===

    def generate_content_for_story(self, story: Story) -> ContentGenerationResult:
        """Generate a script for a single story (legacy workflow).

        NOTE: This is the legacy method that uses content-based detection
        (idea_json + title_id + no content_id). For the state-based workflow,
        use process_oldest_story() instead.

        This method:
        1. Retrieves the Idea from story.idea_json
        2. Retrieves the Title from story.title_id
        3. Generates a script using ContentGenerator
        4. Saves the script to the database
        5. Updates the story with the content_id (sets state to 'SCRIPT')

        Args:
            story: Story object with idea_json and title_id set

        Returns:
            ContentGenerationResult with success status and details
        """
        result = ContentGenerationResult(story_id=story.id)

        # Validate story is ready for content generation
        if not story.needs_content():
            result.error = "Story does not need script (missing idea, title, or already has script)"
            return result

        try:
            # Parse the Idea from JSON
            idea_data = json.loads(story.idea_json)
            idea = Idea.from_dict(idea_data)

            # Get the Title text
            title = self.title_repo.find_by_id(story.title_id)
            if not title:
                result.error = f"Title with id {story.title_id} not found"
                return result

            title_text = title.text

            # Generate the script
            script_v1 = self.content_generator.generate_content_v1(idea=idea, title=title_text)

            # Create Content model for database
            script_model = ScriptModel(
                story_id=story.id,
                version=0,  # Initial version for legacy service
                text=script_v1.full_text,
            )

            # Save to database
            saved_content = self.content_repo.insert(script_model)

            # Update the story with the script reference
            story.set_content(saved_content.id)
            self.story_repo.update(story)

            # Populate result
            result.success = True
            result.content_id = saved_content.id
            result.script_v1 = script_v1

        except json.JSONDecodeError as e:
            result.error = f"Failed to parse idea_json: {str(e)}"
        except ValueError as e:
            result.error = f"Invalid idea or title: {str(e)}"
        except Exception as e:
            result.error = f"Content generation failed: {str(e)}"

        return result

    def process_stories_needing_contents(
        self, limit: Optional[int] = None
    ) -> List[ContentGenerationResult]:
        """Process all stories that need content generation (legacy workflow).

        NOTE: This is the legacy method that uses content-based detection.
        For the state-based workflow, use process_oldest_story() instead.

        This method queries for all stories needing scripts and generates
        scripts for each of them.

        Args:
            limit: Optional maximum number of stories to process

        Returns:
            List of ContentGenerationResult objects with results for each story
        """
        stories = self.get_stories_needing_contents()

        if limit is not None:
            stories = stories[:limit]

        results = []
        for story in stories:
            result = self.generate_content_for_story(story)
            results.append(result)

        return results

    def get_processing_summary(self, results: List[ContentGenerationResult]) -> dict:
        """Get a summary of content generation results.

        Args:
            results: List of ContentGenerationResult from process_stories_needing_contents

        Returns:
            Dictionary with summary statistics
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "successful_story_ids": [r.story_id for r in successful],
            "failed_story_ids": [r.story_id for r in failed],
            "errors": {r.story_id: r.error for r in failed},
        }


def process_all_pending_stories(
    connection: sqlite3.Connection, limit: Optional[int] = None
) -> dict:
    """Convenience function to process all stories needing scripts.

    This is the main entry point for the content generation workflow.

    Args:
        connection: SQLite database connection
        limit: Optional maximum number of stories to process

    Returns:
        Dictionary with processing summary

    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> summary = process_all_pending_stories(conn)
        >>> print(f"Processed {summary['total_processed']} stories")
        >>> print(f"Success rate: {summary['success_rate']:.1%}")
    """
    service = StoryContentService(connection)
    results = service.process_stories_needing_contents(limit=limit)
    return service.get_processing_summary(results)


# =============================================================================
# State-Based Processing for PrismQ.T.Content.From.Idea.Title
# =============================================================================

# State constants following StateNames convention
STATE_CONTENT_FROM_IDEA_TITLE = "PrismQ.T.Content.From.Idea.Title"
STATE_REVIEW_TITLE_FROM_CONTENT_IDEA = "PrismQ.T.Review.Title.From.Content.Idea"

# Version constant for initial script creation
INITIAL_CONTENT_VERSION = 0


@dataclass
class StateBasedContentResult:
    """Result of state-based content generation.

    Attributes:
        story_id: ID of the processed story
        content_id: ID of the generated script (if successful)
        previous_state: The state before processing
        new_state: The state after processing
        success: Whether the operation succeeded
        error: Error message if failed
        script_v1: Generated ContentV1 object (if successful)
    """

    story_id: Optional[int] = None
    content_id: Optional[int] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    script_v1: Optional[ContentV1] = None


class ContentFromIdeaTitleService:
    """Service for PrismQ.T.Content.From.Idea.Title workflow state.

    This service implements the workflow step that:
    1. Selects the oldest Story where state is PrismQ.T.Content.From.Idea.Title
    2. Generates a Content from the Idea and Title
    3. Updates the Story state to PrismQ.T.Review.Title.From.Content.Idea

    The service processes stories in FIFO order (oldest first) to ensure
    fair processing of the backlog.

    Attributes:
        story_repo: Repository for Story operations
        content_repo: Repository for Content operations
        title_repo: Repository for Title operations
        content_generator: Generator for creating scripts

    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> service = ContentFromIdeaTitleService(conn)
        >>>
        >>> # Process the oldest story in the state
        >>> result = service.process_oldest_story()
        >>> if result.success:
        ...     print(f"Generated script {result.content_id} for story {result.story_id}")
        ... else:
        ...     print(f"No stories to process or error: {result.error}")
    """
    
    # State constants for this service
    CURRENT_STATE = StateNames.CONTENT_FROM_IDEA_TITLE
    INPUT_STATE = STATE_CONTENT_FROM_IDEA_TITLE
    OUTPUT_STATE = STATE_REVIEW_TITLE_FROM_CONTENT_IDEA

    def __init__(
        self,
        connection: sqlite3.Connection,
        content_generator_config: Optional[ContentGeneratorConfig] = None,
    ):
        """Initialize the service with database connection.

        Args:
            connection: SQLite database connection with row_factory = sqlite3.Row
            content_generator_config: Optional configuration for content generation
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.content_repo = ContentRepository(connection)
        self.title_repo = TitleRepository(connection)

        config = content_generator_config or ContentGeneratorConfig(
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            target_duration_seconds=90,
            structure_type=ContentStructure.HOOK_DELIVER_CTA,
            include_cta=True,
            tone=ContentTone.ENGAGING,
        )
        self.content_generator = ContentGenerator(config)

    def count_pending(self) -> int:
        """Count stories waiting in the input state.

        Returns:
            Number of stories with state PrismQ.T.Content.From.Idea.Title.
        """
        return self.story_repo.count_by_state(self.INPUT_STATE)

    def get_oldest_story(self) -> Optional[Story]:
        """Get the oldest story in the input state.

        Returns:
            The oldest Story in state PrismQ.T.Content.From.Idea.Title,
            or None if no stories are in this state.
        """
        return self.story_repo.find_oldest_by_state(self.INPUT_STATE)

    def process_oldest_story(self) -> StateBasedContentResult:
        """Process the oldest story in the input state.

        This method:
        1. Finds the oldest Story with state PrismQ.T.Content.From.Idea.Title
        2. Generates a Content from the Story's Idea and Title
        3. Saves the Content to the database
        4. Updates the Story state to PrismQ.T.Review.Title.From.Content.Idea
        
        Includes idempotency checks and comprehensive logging.

        Returns:
            StateBasedContentResult with processing details.
            If no stories are pending, returns result with success=False.
        """
        result = StateBasedContentResult()

        # Find the oldest story in the input state
        story = self.get_oldest_story()

        if story is None:
            result.error = "No stories found in state PrismQ.T.Content.From.Idea.Title"
            logger.debug(result.error)
            return result

        result.story_id = story.id
        result.previous_state = story.state
        logger.info(f"Processing story {story.id} in state {story.state}")

        # Idempotency check: If story already has content, don't regenerate
        if story.content_id:
            result.error = f"Story {story.id} already has content_id={story.content_id}. Skipping duplicate generation."
            logger.warning(result.error)
            return result

        # Validate story has required data
        if not story.idea_json:
            result.error = f"Story {story.id} has no idea_json"
            logger.error(result.error)
            return result

        if not story.title_id:
            result.error = f"Story {story.id} has no title_id"
            logger.error(result.error)
            return result

        try:
            logger.debug(f"Story {story.id}: Parsing idea from JSON")
            # Parse the Idea from JSON
            idea_data = json.loads(story.idea_json)
            idea = Idea.from_dict(idea_data)

            # Get the Title text
            logger.debug(f"Story {story.id}: Fetching title with id={story.title_id}")
            title = self.title_repo.find_by_id(story.title_id)
            if not title:
                result.error = f"Title with id {story.title_id} not found"
                logger.error(f"Story {story.id}: {result.error}")
                return result

            title_text = title.text
            logger.info(f"Story {story.id}: Generating content for title '{title_text}'")

            # Generate the script
            script_v1 = self.content_generator.generate_content_v1(idea=idea, title=title_text)
            logger.info(f"Story {story.id}: Content generated successfully ({len(script_v1.full_text)} chars)")

            # Create Content model for database
            script_model = ScriptModel(
                story_id=story.id, version=INITIAL_CONTENT_VERSION, text=script_v1.full_text
            )

            # Save to database
            logger.debug(f"Story {story.id}: Saving content to database")
            saved_content = self.content_repo.insert(script_model)
            logger.info(f"Story {story.id}: Content saved with id={saved_content.id}")

            # Update the story with the script reference and new state
            story.content_id = saved_content.id
            story.state = self.OUTPUT_STATE
            story.updated_at = datetime.now()
            self.story_repo.update(story)
            logger.info(f"Story {story.id}: State updated to {self.OUTPUT_STATE}")

            # Populate result
            result.success = True
            result.content_id = saved_content.id
            result.new_state = self.OUTPUT_STATE
            result.script_v1 = script_v1

        except json.JSONDecodeError as e:
            result.error = f"Failed to parse idea_json: {str(e)}"
            logger.error(f"Story {story.id}: {result.error}")
        except ValueError as e:
            result.error = f"Invalid idea or title: {str(e)}"
            logger.error(f"Story {story.id}: {result.error}")
        except Exception as e:
            result.error = f"Content generation failed: {str(e)}"
            logger.exception(f"Story {story.id}: Unexpected error during content generation")

        return result

            # Save to database
            saved_content = self.content_repo.insert(script_model)

            # Update the story with the script reference and new state
            story.content_id = saved_content.id
            story.state = self.OUTPUT_STATE
            story.updated_at = datetime.now()
            self.story_repo.update(story)

            # Populate result
            result.success = True
            result.content_id = saved_content.id
            result.new_state = self.OUTPUT_STATE
            result.script_v1 = script_v1

        except json.JSONDecodeError as e:
            result.error = f"Failed to parse idea_json: {str(e)}"
        except ValueError as e:
            result.error = f"Invalid idea or title: {str(e)}"
        except Exception as e:
            result.error = f"Content generation failed: {str(e)}"

        return result

    def process_all_pending(self, limit: Optional[int] = None) -> List[StateBasedContentResult]:
        """Process all stories in the input state.

        This method processes stories in FIFO order (oldest first) until
        all are processed or the limit is reached.

        Args:
            limit: Optional maximum number of stories to process.

        Returns:
            List of StateBasedContentResult for each processed story.
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

    def get_processing_summary(self, results: List[StateBasedContentResult]) -> dict:
        """Get a summary of processing results.

        Args:
            results: List of StateBasedContentResult from processing.

        Returns:
            Dictionary with summary statistics.
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success and r.story_id is not None]

        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "successful_story_ids": [r.story_id for r in successful],
            "failed_story_ids": [r.story_id for r in failed],
            "errors": {r.story_id: r.error for r in failed if r.story_id is not None},
            "input_state": self.INPUT_STATE,
            "output_state": self.OUTPUT_STATE,
        }


def process_oldest_from_idea_title(connection: sqlite3.Connection) -> StateBasedContentResult:
    """Process the oldest story in PrismQ.T.Content.From.Idea.Title state.

    This is the main entry point for the PrismQ.T.Content.From.Idea.Title module.
    It finds the oldest story in the state, generates a script, and updates
    the story state to PrismQ.T.Review.Title.From.Content.Idea.

    Args:
        connection: SQLite database connection.

    Returns:
        StateBasedContentResult with processing details.

    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> result = process_oldest_from_idea_title(conn)
        >>> if result.success:
        ...     print(f"Generated script {result.content_id}")
        ...     print(f"Story state changed to {result.new_state}")
        ... else:
        ...     print(f"Error: {result.error}")
    """
    service = ContentFromIdeaTitleService(connection)
    return service.process_oldest_story()
