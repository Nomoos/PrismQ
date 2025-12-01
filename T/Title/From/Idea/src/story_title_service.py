"""Story and Title Creation Service for PrismQ.T.Title.From.Idea.

This module provides functionality to create 10 Story objects from an Idea
and generate the first Title (v0) for each Story based on the Idea content.

Workflow Position: Stage 2 in MVP workflow
    PrismQ.T.Idea.Creation
        ↓
    PrismQ.T.Title.From.Idea (creates Stories + Title v0) ← This module
        ↓
    PrismQ.T.Script.Draft (v0)

The service:
1. Takes an Idea object as input
2. Creates 10 Story objects, each referencing the Idea
3. Generates the first Title (version 0) for each Story
4. Updates each Story's state to TITLE_V0
5. Returns the created Stories with their Titles

Example:
    >>> from T.Title.From.Idea.src.story_title_service import StoryTitleService
    >>> from T.Idea.Model.src.idea import Idea
    >>> 
    >>> # With database connection
    >>> service = StoryTitleService(db_connection)
    >>> 
    >>> idea = Idea(title="The Future of AI", concept="AI trends")
    >>> result = service.create_stories_with_titles(idea)
    >>> 
    >>> print(f"Created {len(result.stories)} stories")
    >>> for story, title in zip(result.stories, result.titles):
    ...     print(f"Story {story.id}: {title.text}")
"""

import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import sys

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent
model_path = t_module_dir / 'Idea' / 'Model'
database_path = t_module_dir / 'Database'

# Ensure paths are available
if str(model_path / 'src') not in sys.path:
    sys.path.insert(0, str(model_path / 'src'))
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))
if str(database_path) not in sys.path:
    sys.path.insert(0, str(database_path))
if str(t_module_dir) not in sys.path:
    sys.path.insert(0, str(t_module_dir))

# Also add the src directory itself for title_generator imports
src_dir = current_file.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from idea import Idea

# Import TitleGenerator from same directory
from title_generator import TitleGenerator, TitleVariant, TitleConfig

# Import database models and repositories
from T.Database.models.story import Story, StoryState
from T.Database.models.title import Title
from T.Database.repositories.story_repository import StoryRepository
from T.Database.repositories.title_repository import TitleRepository


@dataclass
class StoryTitleResult:
    """Result of creating Stories with Titles from an Idea.
    
    Attributes:
        idea_id: The source idea identifier
        stories: List of created Story objects
        titles: List of created Title objects (one per story)
        title_variants: Original title variants used
    """
    idea_id: str
    stories: List[Story] = field(default_factory=list)
    titles: List[Title] = field(default_factory=list)
    title_variants: List[TitleVariant] = field(default_factory=list)
    
    @property
    def count(self) -> int:
        """Number of stories created."""
        return len(self.stories)
    
    def get_story_title_pairs(self) -> List[Tuple[Story, Title]]:
        """Get pairs of (Story, Title) for convenient iteration."""
        return list(zip(self.stories, self.titles))


class StoryTitleService:
    """Service for creating Stories with initial Titles from Ideas.
    
    This service implements the PrismQ.T.Title.From.Idea workflow stage,
    which creates 10 Story objects from a single Idea and generates
    the first Title (version 0) for each Story.
    
    The service can work in two modes:
    1. With database persistence (when connection is provided)
    2. Without persistence (returns in-memory objects only)
    
    Attributes:
        _conn: Optional SQLite database connection
        _story_repo: Story repository (if connection provided)
        _title_repo: Title repository (if connection provided)
        _title_generator: TitleGenerator for creating title variants
    
    Example:
        >>> # With database
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> service = StoryTitleService(conn)
        >>> result = service.create_stories_with_titles(idea)
        
        >>> # Without database (in-memory only)
        >>> service = StoryTitleService()
        >>> result = service.create_stories_with_titles(idea)
    """
    
    NUM_STORIES = 10  # Number of stories to create from each Idea
    
    def __init__(
        self, 
        connection: Optional[sqlite3.Connection] = None,
        title_config: Optional[TitleConfig] = None
    ):
        """Initialize the service.
        
        Args:
            connection: Optional SQLite connection for persistence.
                If provided, Stories and Titles will be persisted to database.
                If None, objects are created in-memory only.
            title_config: Optional configuration for title generation.
        """
        self._conn = connection
        self._story_repo = StoryRepository(connection) if connection else None
        self._title_repo = TitleRepository(connection) if connection else None
        self._title_generator = TitleGenerator(title_config)
    
    def idea_has_stories(self, idea: Idea, idea_id: Optional[str] = None) -> bool:
        """Check if an Idea already has Stories in the database.
        
        Args:
            idea: The Idea object to check.
            idea_id: Optional explicit idea identifier.
            
        Returns:
            True if the Idea already has Stories, False otherwise.
            Always returns False if no database connection is available.
        """
        if not self._story_repo:
            return False
        
        effective_idea_id = idea_id or self._get_idea_id(idea)
        count = self._story_repo.count_by_idea_id(effective_idea_id)
        return count > 0
    
    def create_stories_with_titles(
        self, 
        idea: Idea,
        idea_id: Optional[str] = None,
        skip_if_exists: bool = True
    ) -> Optional[StoryTitleResult]:
        """Create 10 Stories from an Idea, each with a first Title.
        
        This method:
        1. Checks if Idea already has Stories (if skip_if_exists=True)
        2. Generates 10 title variants from the Idea
        3. Creates 10 Story objects, each referencing the Idea
        4. Creates the first Title (v0) for each Story using a variant
        5. Updates each Story's state to TITLE_V0
        6. Persists to database if connection was provided
        
        Args:
            idea: The source Idea object containing concept, title, etc.
            idea_id: Optional explicit idea identifier. If not provided,
                uses idea.title as a simple identifier (for ideas without
                database persistence).
            skip_if_exists: If True (default), returns None if the Idea
                already has Stories in the database. This ensures the module
                only picks Ideas that aren't referenced by Story table rows yet.
        
        Returns:
            StoryTitleResult containing created Stories and Titles,
            or None if skip_if_exists=True and Idea already has Stories.
            
        Raises:
            ValueError: If idea is None or has no title/concept.
        """
        if not idea:
            raise ValueError("Idea cannot be None")
        
        if not idea.title and not idea.concept:
            raise ValueError("Idea must have at least a title or concept")
        
        # Determine idea ID
        effective_idea_id = idea_id or self._get_idea_id(idea)
        
        # Check if Idea already has Stories (skip if exists)
        if skip_if_exists and self.idea_has_stories(idea, effective_idea_id):
            return None
        
        # Generate title variants using existing TitleGenerator
        title_variants = self._title_generator.generate_from_idea(
            idea, 
            num_variants=self.NUM_STORIES
        )
        
        # Create Stories and Titles
        stories: List[Story] = []
        titles: List[Title] = []
        
        for i, variant in enumerate(title_variants):
            # Create Story
            story = Story(
                idea_id=effective_idea_id,
                state=StoryState.CREATED
            )
            
            # Persist Story if we have a connection
            if self._story_repo:
                story = self._story_repo.insert(story)
            else:
                # Assign a temporary ID for in-memory usage
                story.id = i + 1
            
            # Create Title (version 0) for this Story
            title = Title(
                story_id=story.id,
                version=0,
                text=variant.text
            )
            
            # Persist Title if we have a connection
            if self._title_repo:
                title = self._title_repo.insert(title)
            else:
                # Assign a temporary ID for in-memory usage
                title.id = i + 1
            
            # Update Story state to TITLE_V0
            story.transition_to(StoryState.TITLE_V0)
            if self._story_repo:
                self._story_repo.update(story)
            
            stories.append(story)
            titles.append(title)
        
        return StoryTitleResult(
            idea_id=effective_idea_id,
            stories=stories,
            titles=titles,
            title_variants=title_variants
        )
    
    def _get_idea_id(self, idea: Idea) -> str:
        """Extract or generate an identifier for the Idea.
        
        Args:
            idea: The Idea object.
            
        Returns:
            A string identifier for the Idea.
        """
        # Try to use existing ID if available
        if hasattr(idea, 'id') and idea.id:
            return str(idea.id)
        
        # Use title as a simple identifier
        if idea.title:
            # Create a simple slug from title
            return idea.title.lower().replace(' ', '-')[:50]
        
        # Use deterministic hash of concept as fallback (hashlib for stability)
        import hashlib
        concept_hash = hashlib.md5(idea.concept.encode()).hexdigest()[:8]
        return f"idea-{concept_hash}"
    
    def ensure_tables_exist(self) -> None:
        """Ensure Story and Title tables exist in the database.
        
        Call this method to create the required tables if they don't exist.
        Only works when a database connection was provided.
        
        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._conn:
            raise RuntimeError("No database connection available")
        
        # Create Story table
        self._conn.executescript(Story.get_sql_schema())
        
        # Create Title table using Title model's schema
        self._conn.executescript(Title.get_sql_schema())
        self._conn.commit()


def create_stories_from_idea(
    idea: Idea,
    connection: Optional[sqlite3.Connection] = None,
    idea_id: Optional[str] = None,
    title_config: Optional[TitleConfig] = None,
    skip_if_exists: bool = True
) -> Optional[StoryTitleResult]:
    """Convenience function to create Stories with Titles from an Idea.
    
    This is a simpler interface to StoryTitleService.create_stories_with_titles().
    The module will only pick Ideas that aren't already referenced by Story table rows.
    
    Args:
        idea: The source Idea object.
        connection: Optional SQLite connection for persistence.
        idea_id: Optional explicit idea identifier.
        title_config: Optional configuration for title generation.
        skip_if_exists: If True (default), returns None if the Idea
            already has Stories in the database.
        
    Returns:
        StoryTitleResult containing created Stories and Titles,
        or None if skip_if_exists=True and Idea already has Stories.
        
    Example:
        >>> idea = Idea(title="AI Future", concept="Exploring AI trends")
        >>> result = create_stories_from_idea(idea)
        >>> if result:
        ...     print(f"Created {result.count} stories")
        ... else:
        ...     print("Idea already has stories")
        Created 10 stories
    """
    service = StoryTitleService(connection, title_config)
    return service.create_stories_with_titles(idea, idea_id, skip_if_exists)
