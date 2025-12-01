"""Story Script Service - Generate scripts for stories from Idea and Title.

This module provides a service that:
1. Selects the oldest Story where state is PrismQ.T.Script.From.Idea.Title
2. Generates scripts using the ScriptGenerator from Idea and Title
3. Updates the Story with the generated Script
4. Changes state to PrismQ.T.Review.Title.From.Script

This is the main entry point for automated script generation in the workflow.

Usage:
    >>> import sqlite3
    >>> from T.Script.From.Idea.Title.src.story_script_service import StoryScriptService
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> service = StoryScriptService(conn)
    >>> 
    >>> # Process oldest story needing script (by state)
    >>> result = service.process_oldest_story()
    >>> if result:
    ...     print(f"Generated script for story {result.story_id}")
    >>> 
    >>> # Process all stories needing scripts
    >>> results = service.process_stories_needing_scripts()
    >>> print(f"Generated {len(results)} scripts")
"""

import json
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.script_repository import ScriptRepository
from T.Database.repositories.title_repository import TitleRepository
from T.Database.models.story import Story
from T.Database.models.script import Script as ScriptModel
from T.State.constants.state_names import StateNames

# Import ScriptGenerator from local module
from .script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptV1,
    ScriptStructure,
    PlatformTarget,
    ScriptTone
)

# Import Idea from Idea module
import sys
from pathlib import Path
_current_file = Path(__file__)
# Navigate: src -> Title -> Idea -> From -> Script -> T
# Path: T/Script/From/Idea/Title/src/story_script_service.py
# Up 6 levels to T/, then into Idea/Model/src
_t_module_dir = _current_file.parent.parent.parent.parent.parent.parent
_idea_model_path = _t_module_dir / 'Idea' / 'Model' / 'src'
sys.path.insert(0, str(_idea_model_path))

from idea import Idea, ContentGenre


@dataclass
class ScriptGenerationResult:
    """Result of script generation for a story.
    
    Attributes:
        story_id: ID of the story processed
        script_id: ID of the generated script (if successful)
        success: Whether script generation was successful
        error: Error message if generation failed
        script_v1: The generated ScriptV1 object (if successful)
    """
    story_id: int
    script_id: Optional[int] = None
    success: bool = False
    error: Optional[str] = None
    script_v1: Optional[ScriptV1] = None


class StoryScriptService:
    """Service for generating scripts for stories from Idea and Title.
    
    This service implements the workflow step:
        Story (state=PrismQ.T.Script.From.Idea.Title) → Script Generation 
        → Story (state=PrismQ.T.Review.Title.From.Script)
    
    Primary workflow (state-based):
        - Selects the oldest Story where state is PrismQ.T.Script.From.Idea.Title
        - Generates a Script (version 0) from Idea and Title
        - Updates Story state to PrismQ.T.Review.Title.From.Script
    
    Legacy workflow (content-based):
        - Queries for stories that have idea_json and title_id but no script_id
        - Generates scripts and updates stories
    
    Attributes:
        story_repo: Repository for Story operations
        script_repo: Repository for Script operations
        title_repo: Repository for Title operations
        script_generator: Generator for creating scripts
    
    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> conn.row_factory = sqlite3.Row
        >>> service = StoryScriptService(conn)
        >>> 
        >>> # Process oldest story by state (primary workflow)
        >>> result = service.process_oldest_story()
        >>> if result and result.success:
        ...     print(f"Generated script for story {result.story_id}")
        >>> 
        >>> # Process all stories (legacy workflow)
        >>> results = service.process_stories_needing_scripts()
        >>> successful = [r for r in results if r.success]
        >>> print(f"Successfully generated {len(successful)} scripts")
    """
    
    def __init__(
        self,
        connection: sqlite3.Connection,
        script_generator_config: Optional[ScriptGeneratorConfig] = None
    ):
        """Initialize the service with database connection.
        
        Args:
            connection: SQLite database connection with row_factory = sqlite3.Row
            script_generator_config: Optional configuration for script generation
        """
        self._conn = connection
        self.story_repo = StoryRepository(connection)
        self.script_repo = ScriptRepository(connection)
        self.title_repo = TitleRepository(connection)
        
        config = script_generator_config or ScriptGeneratorConfig(
            platform_target=PlatformTarget.YOUTUBE_MEDIUM,
            target_duration_seconds=90,
            structure_type=ScriptStructure.HOOK_DELIVER_CTA,
            include_cta=True,
            tone=ScriptTone.ENGAGING
        )
        self.script_generator = ScriptGenerator(config)
    
    def count_stories_needing_scripts(self) -> int:
        """Count stories that need script generation.
        
        Returns:
            Number of stories ready for script generation.
        """
        return self.story_repo.count_needing_script()
    
    def get_stories_needing_scripts(self) -> List[Story]:
        """Get all stories that need script generation.
        
        Returns:
            List of Story objects ready for script generation.
        """
        return self.story_repo.find_needing_script()
    
    # === State-based workflow methods (Primary) ===
    
    def get_oldest_story_by_state(self) -> Optional[Story]:
        """Get the oldest story where state is PrismQ.T.Script.From.Idea.Title.
        
        This is the primary method for the state-based workflow.
        Selects the oldest story (by created_at) with the correct state.
        
        Returns:
            The oldest Story with state PrismQ.T.Script.From.Idea.Title,
            or None if no such stories exist.
            
        Example:
            >>> story = service.get_oldest_story_by_state()
            >>> if story:
            ...     print(f"Found story {story.id} created at {story.created_at}")
        """
        stories = self.story_repo.find_by_state_ordered_by_created(
            StateNames.SCRIPT_FROM_IDEA_TITLE,
            ascending=True  # Oldest first
        )
        return stories[0] if stories else None
    
    def count_stories_by_state(self) -> int:
        """Count stories where state is PrismQ.T.Script.From.Idea.Title.
        
        Returns:
            Number of stories with state PrismQ.T.Script.From.Idea.Title.
        """
        return self.story_repo.count_by_state(StateNames.SCRIPT_FROM_IDEA_TITLE)
    
    def process_oldest_story(self) -> Optional[ScriptGenerationResult]:
        """Process the oldest story with state PrismQ.T.Script.From.Idea.Title.
        
        This is the primary entry point for the state-based workflow.
        It:
        1. Selects the oldest Story where state is PrismQ.T.Script.From.Idea.Title
        2. Generates a Script (version 0) from Idea and Title
        3. Updates Story state to PrismQ.T.Review.Title.From.Script
        
        Returns:
            ScriptGenerationResult if a story was processed, None if no stories found.
            
        Example:
            >>> result = service.process_oldest_story()
            >>> if result and result.success:
            ...     print(f"Generated script {result.script_id} for story {result.story_id}")
            >>> elif result:
            ...     print(f"Failed: {result.error}")
            >>> else:
            ...     print("No stories to process")
        """
        story = self.get_oldest_story_by_state()
        if not story:
            return None
        
        return self._generate_script_with_state_transition(story)
    
    def _generate_script_with_state_transition(self, story: Story) -> ScriptGenerationResult:
        """Generate script and transition state to PrismQ.T.Review.Title.From.Script.
        
        Internal method that handles the state-based workflow script generation.
        
        Args:
            story: Story object with state PrismQ.T.Script.From.Idea.Title
            
        Returns:
            ScriptGenerationResult with success status and details
        """
        result = ScriptGenerationResult(story_id=story.id)
        
        # Validate story has required content
        if not story.has_idea():
            result.error = "Story does not have idea_json set"
            return result
        
        if not story.has_title():
            result.error = "Story does not have title_id set"
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
            script_v1 = self.script_generator.generate_script_v1(
                idea=idea,
                title=title_text
            )
            
            # Create Script model for database
            script_model = ScriptModel(
                story_id=story.id,
                version=0,  # First version
                text=script_v1.full_text
            )
            
            # Save to database
            saved_script = self.script_repo.insert(script_model)
            
            # Update the story with script reference and transition state
            story.script_id = saved_script.id
            story.update_state(StateNames.REVIEW_TITLE_FROM_SCRIPT)
            self.story_repo.update(story)
            
            # Populate result
            result.success = True
            result.script_id = saved_script.id
            result.script_v1 = script_v1
            
        except json.JSONDecodeError as e:
            result.error = f"Failed to parse idea_json: {str(e)}"
        except ValueError as e:
            result.error = f"Invalid idea or title: {str(e)}"
        except Exception as e:
            result.error = f"Script generation failed: {str(e)}"
        
        return result
    
    # === Legacy workflow methods (content-based) ===
    
    def generate_script_for_story(self, story: Story) -> ScriptGenerationResult:
        """Generate a script for a single story (legacy workflow).
        
        NOTE: This is the legacy method that uses content-based detection
        (idea_json + title_id + no script_id). For the state-based workflow,
        use process_oldest_story() instead.
        
        This method:
        1. Retrieves the Idea from story.idea_json
        2. Retrieves the Title from story.title_id
        3. Generates a script using ScriptGenerator
        4. Saves the script to the database
        5. Updates the story with the script_id (sets state to 'SCRIPT')
        
        Args:
            story: Story object with idea_json and title_id set
            
        Returns:
            ScriptGenerationResult with success status and details
        """
        result = ScriptGenerationResult(story_id=story.id)
        
        # Validate story is ready for script generation
        if not story.needs_script():
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
            script_v1 = self.script_generator.generate_script_v1(
                idea=idea,
                title=title_text
            )
            
            # Create Script model for database
            script_model = ScriptModel(
                story_id=story.id,
                version=0,  # First version
                text=script_v1.full_text
            )
            
            # Save to database
            saved_script = self.script_repo.insert(script_model)
            
            # Update the story with the script reference
            story.set_script(saved_script.id)
            self.story_repo.update(story)
            
            # Populate result
            result.success = True
            result.script_id = saved_script.id
            result.script_v1 = script_v1
            
        except json.JSONDecodeError as e:
            result.error = f"Failed to parse idea_json: {str(e)}"
        except ValueError as e:
            result.error = f"Invalid idea or title: {str(e)}"
        except Exception as e:
            result.error = f"Script generation failed: {str(e)}"
        
        return result
    
    def process_stories_needing_scripts(
        self,
        limit: Optional[int] = None
    ) -> List[ScriptGenerationResult]:
        """Process all stories that need script generation (legacy workflow).
        
        NOTE: This is the legacy method that uses content-based detection.
        For the state-based workflow, use process_oldest_story() instead.
        
        This method queries for all stories needing scripts and generates
        scripts for each of them.
        
        Args:
            limit: Optional maximum number of stories to process
            
        Returns:
            List of ScriptGenerationResult objects with results for each story
        """
        stories = self.get_stories_needing_scripts()
        
        if limit is not None:
            stories = stories[:limit]
        
        results = []
        for story in stories:
            result = self.generate_script_for_story(story)
            results.append(result)
        
        return results
    
    def get_processing_summary(
        self,
        results: List[ScriptGenerationResult]
    ) -> dict:
        """Get a summary of script generation results.
        
        Args:
            results: List of ScriptGenerationResult from process_stories_needing_scripts
            
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
            "errors": {r.story_id: r.error for r in failed}
        }


def process_all_pending_stories(
    connection: sqlite3.Connection,
    limit: Optional[int] = None
) -> dict:
    """Convenience function to process all stories needing scripts.
    
    This is the main entry point for the script generation workflow.
    
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
    service = StoryScriptService(connection)
    results = service.process_stories_needing_scripts(limit=limit)
    return service.get_processing_summary(results)
