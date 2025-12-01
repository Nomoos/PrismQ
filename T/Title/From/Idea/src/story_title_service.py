"""Story and Title Creation Service for PrismQ.T.Title.From.Idea.

This module provides functionality to generate Title (v0) for Stories
that are ready for title generation (state = PrismQ.T.Title.From.Idea)
and don't have Title or Script references yet.

Workflow Position: Stage 2 in MVP workflow
    PrismQ.T.Idea.Creation
        ↓
    PrismQ.T.Story.From.Idea (creates Stories)
        ↓
    PrismQ.T.Title.From.Idea (generates Title v0) ← This module
        ↓
    PrismQ.T.Script.Draft (v0)

The service:
1. Finds Stories with state PrismQ.T.Title.From.Idea
2. Filters to only Stories without Title references
3. Generates the first Title (version 0) for each Story
4. Updates each Story's state to TITLE_V0
5. Returns the created Titles

Example:
    >>> from T.Title.From.Idea.src.story_title_service import StoryTitleService
    >>> 
    >>> # With database connection
    >>> service = StoryTitleService(db_connection)
    >>> 
    >>> # Process stories without titles
    >>> result = service.process_stories_without_titles()
    >>> 
    >>> print(f"Created {len(result.titles)} titles")
    >>> for story, title in result.get_story_title_pairs():
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
    """Service for generating Titles for Stories without Title references.
    
    This service implements the PrismQ.T.Title.From.Idea workflow stage,
    which finds Stories with state TITLE_FROM_IDEA (ready for title generation)
    that don't have Title references yet, and generates Title (version 0) for each.
    
    The service requires a database connection to:
    1. Find Stories with correct state and no titles
    2. Persist generated Titles
    3. Update Story state to TITLE_V0
    
    Attributes:
        _conn: SQLite database connection
        _story_repo: Story repository
        _title_repo: Title repository
        _title_generator: TitleGenerator for creating title variants
    
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> service = StoryTitleService(conn)
        >>> 
        >>> # Process all stories without titles
        >>> result = service.process_stories_without_titles()
        >>> print(f"Created {len(result.titles)} titles")
    """
    
    NUM_STORIES = 10  # Number of stories to create from each Idea (legacy)
    
    def __init__(
        self, 
        connection: Optional[sqlite3.Connection] = None,
        title_config: Optional[TitleConfig] = None
    ):
        """Initialize the service.
        
        Args:
            connection: SQLite connection for persistence.
                Required for new workflow (process_stories_without_titles).
                Optional for backward compatibility (create_stories_with_titles).
            title_config: Optional configuration for title generation.
        """
        self._conn = connection
        self._story_repo = StoryRepository(connection) if connection else None
        self._title_repo = TitleRepository(connection) if connection else None
        self._title_generator = TitleGenerator(title_config)
    
    def get_stories_without_titles(self) -> List[Story]:
        """Get Stories that are ready for title generation but don't have titles.
        
        Finds Stories where:
        1. state = TITLE_FROM_IDEA (ready for title generation)
        2. No Title records exist for the story_id
        
        Returns:
            List of Story objects without Title references.
            
        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._story_repo or not self._title_repo:
            raise RuntimeError("Database connection required for this operation")
        
        # Get stories with TITLE_FROM_IDEA state
        stories_ready = self._story_repo.find_by_state(StoryState.TITLE_FROM_IDEA)
        
        # Filter to only those without titles
        stories_without_titles = []
        for story in stories_ready:
            titles = self._title_repo.find_by_story_id(story.id)
            if not titles:
                stories_without_titles.append(story)
        
        return stories_without_titles
    
    def story_has_title(self, story_id: int) -> bool:
        """Check if a Story already has a Title.
        
        Args:
            story_id: The Story's database ID.
            
        Returns:
            True if the Story has at least one Title, False otherwise.
            Returns False if no database connection.
        """
        if not self._title_repo:
            return False
        titles = self._title_repo.find_by_story_id(story_id)
        return len(titles) > 0
    
    def story_has_script(self, story_id: int) -> bool:
        """Check if a Story has a Script reference.
        
        Note: This is a placeholder - Script repository would be needed
        for full implementation. Currently returns False.
        
        Args:
            story_id: The Story's database ID.
            
        Returns:
            False (placeholder - no Script repository implemented yet).
        """
        # TODO: Implement when Script repository is available
        # scripts = self._script_repo.find_by_story_id(story_id)
        # return len(scripts) > 0
        return False
    
    def generate_title_for_story(
        self,
        story: Story,
        idea: Optional[Idea] = None
    ) -> Optional[Title]:
        """Generate a Title (v0) for a single Story.
        
        Args:
            story: The Story to generate a title for.
            idea: Optional Idea object for context. If not provided,
                  creates a simple title based on story_id.
        
        Returns:
            Created Title object, or None if story already has a title.
            
        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._title_repo or not self._story_repo:
            raise RuntimeError("Database connection required for this operation")
        
        # Check if story already has a title
        if self.story_has_title(story.id):
            return None
        
        # Generate title variant
        if idea:
            variants = self._title_generator.generate_from_idea(idea, num_variants=3)
            title_text = variants[0].text if variants else f"Story {story.id}"
        else:
            # Fallback: generate a simple title
            title_text = f"Story {story.id}: New Content"
        
        # Create Title (version 0)
        title = Title(
            story_id=story.id,
            version=0,
            text=title_text
        )
        
        # Persist Title
        title = self._title_repo.insert(title)
        
        # Update Story state to TITLE_V0
        story.transition_to(StoryState.TITLE_V0)
        self._story_repo.update(story)
        
        return title
    
    def process_stories_without_titles(
        self,
        idea_db=None
    ) -> StoryTitleResult:
        """Process all Stories without titles and generate Title v0 for each.
        
        This method:
        1. Finds all Stories with state TITLE_FROM_IDEA and no Title references
        2. Generates Title (v0) for each Story
        3. Updates each Story's state to TITLE_V0
        
        Args:
            idea_db: Optional SimpleIdeaDatabase to fetch Idea content.
                    If provided, titles will be generated from Idea content.
        
        Returns:
            StoryTitleResult containing processed Stories and created Titles.
            
        Raises:
            RuntimeError: If no database connection is available.
        """
        if not self._story_repo or not self._title_repo:
            raise RuntimeError("Database connection required for this operation")
        
        stories_to_process = self.get_stories_without_titles()
        
        stories: List[Story] = []
        titles: List[Title] = []
        title_variants: List[TitleVariant] = []
        
        for story in stories_to_process:
            idea = None
            
            # Try to get Idea content for better title generation
            if idea_db:
                try:
                    idea_id = int(story.idea_id)
                    idea_dict = idea_db.get_idea(idea_id)
                    if idea_dict:
                        idea = Idea(
                            title=idea_dict.get('text', ''),
                            concept=idea_dict.get('text', '')
                        )
                except (ValueError, TypeError):
                    pass
            
            # Generate title
            title = self.generate_title_for_story(story, idea)
            if title:
                stories.append(story)
                titles.append(title)
        
        # Return result with first idea_id found or empty string
        idea_id = stories[0].idea_id if stories else ""
        
        return StoryTitleResult(
            idea_id=idea_id,
            stories=stories,
            titles=titles,
            title_variants=title_variants
        )
    
    # === Legacy methods for backward compatibility ===
    
    def idea_has_stories(self, idea: Idea, idea_id: Optional[str] = None) -> bool:
        """Check if an Idea already has Stories in the database.
        
        DEPRECATED: Use Story.From.Idea module for creating stories.
        This method is kept for backward compatibility.
        
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
        
        DEPRECATED: Use Story.From.Idea module to create stories first,
        then use process_stories_without_titles() to generate titles.
        This method is kept for backward compatibility.
        
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
    
    DEPRECATED: Use Story.From.Idea module to create stories first,
    then use process_stories_without_titles() to generate titles.
    This function is kept for backward compatibility.
    
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


def process_stories_without_titles(
    connection: sqlite3.Connection,
    idea_db=None,
    title_config: Optional[TitleConfig] = None
) -> StoryTitleResult:
    """Process Stories without Title references and generate Title v0 for each.
    
    This is the main entry point for the PrismQ.T.Title.From.Idea module.
    It finds Stories with state TITLE_FROM_IDEA that don't have Title
    references yet, and generates the first Title (v0) for each.
    
    Args:
        connection: SQLite connection for persistence.
        idea_db: Optional SimpleIdeaDatabase for fetching Idea content.
        title_config: Optional configuration for title generation.
        
    Returns:
        StoryTitleResult containing processed Stories and created Titles.
        
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> result = process_stories_without_titles(conn)
        >>> print(f"Created {len(result.titles)} titles")
    """
    service = StoryTitleService(connection, title_config)
    return service.process_stories_without_titles(idea_db)
