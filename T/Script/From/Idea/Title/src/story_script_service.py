"""Story Script Service - Generate scripts for stories from Idea and Title.

This module provides a service that:
1. Selects Story objects from the database where Script is null and Title and Idea are filled
2. Generates scripts using the ScriptGenerator from Idea and Title
3. Updates the Story with the generated Script

This is the main entry point for automated script generation in the workflow.

Usage:
    >>> import sqlite3
    >>> from T.Script.From.Idea.Title.src.story_script_service import StoryScriptService
    >>> 
    >>> conn = sqlite3.connect("prismq.db")
    >>> conn.row_factory = sqlite3.Row
    >>> service = StoryScriptService(conn)
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
        Story (with Idea + Title) → Script Generation → Story (with Script)
    
    It queries the database for stories that:
    - Have an idea_json set (Idea is filled)
    - Have a title_id set (Title is generated)
    - Do not have a script_id (Script is null)
    
    Then generates scripts using the ScriptGenerator and updates the stories.
    
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
        >>> # Get count of stories needing scripts
        >>> count = service.count_stories_needing_scripts()
        >>> print(f"{count} stories need scripts")
        >>> 
        >>> # Process all stories
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
    
    def generate_script_for_story(self, story: Story) -> ScriptGenerationResult:
        """Generate a script for a single story.
        
        This method:
        1. Retrieves the Idea from story.idea_json
        2. Retrieves the Title from story.title_id
        3. Generates a script using ScriptGenerator
        4. Saves the script to the database
        5. Updates the story with the script_id
        
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
        """Process all stories that need script generation.
        
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
