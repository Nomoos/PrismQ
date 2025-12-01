"""Story creation service from Idea objects for PrismQ.

This module provides functionality to create Story objects from Idea objects
that don't yet have references in the Story table.

The module:
1. Loads Idea objects that have no references in the Story table
2. Creates 10 Story objects per Idea, each with just a reference to the Idea
3. Stories are created in CREATED state (without Title or Script)

Workflow Position: Early stage before Title generation
    PrismQ.T.Idea.Creation
        ↓
    PrismQ.T.Story.From.Idea (creates Stories only) ← This module
        ↓
    PrismQ.T.Title.From.Idea (generates Titles for Stories)

Example:
    >>> from T.Story.From.Idea.src.story_from_idea_service import StoryFromIdeaService
    >>> 
    >>> service = StoryFromIdeaService(story_connection, idea_db)
    >>> 
    >>> # Get unreferenced ideas and create stories
    >>> results = service.process_unreferenced_ideas()
    >>> print(f"Created stories for {len(results)} ideas")
"""

import sqlite3
from dataclasses import dataclass, field
from typing import List, Optional, Set
from pathlib import Path
import sys

# Add parent directories to path for imports
# This follows the established pattern in T/Title/From/Idea/src/story_title_service.py
def _find_t_module_dir() -> Path:
    """Find the T module directory by walking up from current file."""
    current = Path(__file__).resolve()
    while current.name != 'T' and current.parent != current:
        current = current.parent
    if current.name == 'T':
        return current
    # Fallback to counting parents (src -> Idea -> From -> Story -> T)
    return Path(__file__).resolve().parent.parent.parent.parent.parent


t_module_dir = _find_t_module_dir()
idea_model_path = t_module_dir / 'Idea' / 'Model'
database_path = t_module_dir / 'Database'

# Ensure paths are available
if str(idea_model_path / 'src') not in sys.path:
    sys.path.insert(0, str(idea_model_path / 'src'))
if str(idea_model_path) not in sys.path:
    sys.path.insert(0, str(idea_model_path))
if str(database_path) not in sys.path:
    sys.path.insert(0, str(database_path))
if str(t_module_dir) not in sys.path:
    sys.path.insert(0, str(t_module_dir))

# Import database models and repositories
from T.Database.models.story import Story, StoryState
from T.Database.repositories.story_repository import StoryRepository

# Import SimpleIdea model and database
from simple_idea import SimpleIdea
from simple_idea_db import SimpleIdeaDatabase


@dataclass
class StoryCreationResult:
    """Result of creating Stories from an Idea.
    
    Attributes:
        idea_id: The source idea identifier (integer ID from Idea table)
        stories: List of created Story objects
    """
    idea_id: int
    stories: List[Story] = field(default_factory=list)
    
    @property
    def count(self) -> int:
        """Number of stories created."""
        return len(self.stories)


class StoryFromIdeaService:
    """Service for creating Story objects from Idea objects.
    
    This service implements the PrismQ.T.Story.From.Idea workflow stage,
    which creates 10 Story objects from a single Idea. Unlike the
    T.Title.From.Idea module, this service creates Stories only,
    without generating Titles.
    
    The service:
    1. Can find Ideas that don't have Story references yet
    2. Creates 10 Story objects for each Idea
    3. Each Story is in CREATED state (no Title, no Script)
    
    Attributes:
        _story_conn: SQLite database connection for Story table
        _story_repo: Story repository
        _idea_db: SimpleIdea database manager
    
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> idea_db = SimpleIdeaDatabase("idea.db")
        >>> idea_db.connect()
        >>> 
        >>> service = StoryFromIdeaService(conn, idea_db)
        >>> 
        >>> # Create stories from a specific idea
        >>> result = service.create_stories_from_idea(idea_id=1)
        >>> print(f"Created {result.count} stories")
        >>> 
        >>> # Process all unreferenced ideas
        >>> results = service.process_unreferenced_ideas()
        >>> print(f"Processed {len(results)} ideas")
    """
    
    NUM_STORIES = 10  # Number of stories to create from each Idea
    
    def __init__(
        self,
        story_connection: sqlite3.Connection,
        idea_db: SimpleIdeaDatabase
    ):
        """Initialize the service.
        
        Args:
            story_connection: SQLite connection for Story table.
            idea_db: SimpleIdeaDatabase instance for querying Ideas.
        """
        self._story_conn = story_connection
        self._story_repo = StoryRepository(story_connection)
        self._idea_db = idea_db
    
    def get_referenced_idea_ids(self) -> Set[int]:
        """Get all Idea IDs that already have Story references.
        
        Returns:
            Set of Idea IDs (integers) that have at least one Story.
        """
        cursor = self._story_conn.execute(
            "SELECT DISTINCT idea_id FROM Story"
        )
        # idea_id is stored as TEXT in Story, so we need to convert
        referenced_ids = set()
        for row in cursor.fetchall():
            try:
                referenced_ids.add(int(row[0]))
            except (ValueError, TypeError):
                # Skip non-integer idea_ids (legacy or external IDs)
                pass
        return referenced_ids
    
    def get_unreferenced_ideas(self) -> List[SimpleIdea]:
        """Get all Ideas that don't have Story references.
        
        Returns:
            List of SimpleIdea objects that are not referenced by any Story.
        """
        # Get all ideas from database
        all_ideas_dict = self._idea_db.get_all_ideas()
        
        # Get referenced idea IDs
        referenced_ids = self.get_referenced_idea_ids()
        
        # Filter to unreferenced ideas
        unreferenced = []
        for idea_dict in all_ideas_dict:
            idea_id = idea_dict.get("id")
            if idea_id is not None and idea_id not in referenced_ids:
                unreferenced.append(SimpleIdea.from_dict(idea_dict))
        
        return unreferenced
    
    def idea_has_stories(self, idea_id: int) -> bool:
        """Check if an Idea already has Stories in the database.
        
        Args:
            idea_id: The Idea's database ID (integer).
            
        Returns:
            True if the Idea already has Stories, False otherwise.
        """
        count = self._story_repo.count_by_idea_id(str(idea_id))
        return count > 0
    
    def create_stories_from_idea(
        self,
        idea_id: int,
        skip_if_exists: bool = True
    ) -> Optional[StoryCreationResult]:
        """Create 10 Story objects from an Idea.
        
        This method creates 10 Story objects referencing the given Idea ID.
        Each Story is created in CREATED state without Title or Script.
        
        Args:
            idea_id: The Idea's database ID (integer).
            skip_if_exists: If True (default), returns None if the Idea
                already has Stories in the database.
        
        Returns:
            StoryCreationResult containing created Stories,
            or None if skip_if_exists=True and Idea already has Stories.
        """
        # Check if Idea already has Stories (skip if exists)
        if skip_if_exists and self.idea_has_stories(idea_id):
            return None
        
        # Create Stories
        stories: List[Story] = []
        
        for _ in range(self.NUM_STORIES):
            # Create Story with reference to Idea
            story = Story(
                idea_id=str(idea_id),  # Story.idea_id is TEXT
                state=StoryState.CREATED
            )
            
            # Persist Story
            story = self._story_repo.insert(story)
            stories.append(story)
        
        return StoryCreationResult(
            idea_id=idea_id,
            stories=stories
        )
    
    def process_unreferenced_ideas(self) -> List[StoryCreationResult]:
        """Process all unreferenced Ideas and create Stories for each.
        
        This method:
        1. Finds all Ideas that don't have Story references
        2. Creates 10 Stories for each unreferenced Idea
        
        Returns:
            List of StoryCreationResult objects for each processed Idea.
        """
        results: List[StoryCreationResult] = []
        
        # Get unreferenced ideas
        unreferenced_ideas = self.get_unreferenced_ideas()
        
        for idea in unreferenced_ideas:
            if idea.id is not None:
                result = self.create_stories_from_idea(
                    idea_id=idea.id,
                    skip_if_exists=False  # We already filtered
                )
                if result:
                    results.append(result)
        
        return results
    
    def ensure_tables_exist(self) -> None:
        """Ensure Story table exists in the database.
        
        Call this method to create the required tables if they don't exist.
        """
        # Create Story table
        self._story_conn.executescript(Story.get_sql_schema())
        self._story_conn.commit()


def create_stories_from_idea(
    story_connection: sqlite3.Connection,
    idea_db: SimpleIdeaDatabase,
    idea_id: int,
    skip_if_exists: bool = True
) -> Optional[StoryCreationResult]:
    """Convenience function to create Stories from an Idea.
    
    Args:
        story_connection: SQLite connection for Story table.
        idea_db: SimpleIdeaDatabase instance.
        idea_id: The Idea's database ID (integer).
        skip_if_exists: If True (default), returns None if the Idea
            already has Stories.
        
    Returns:
        StoryCreationResult containing created Stories,
        or None if skip_if_exists=True and Idea already has Stories.
        
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> idea_db = SimpleIdeaDatabase("idea.db")
        >>> idea_db.connect()
        >>> 
        >>> result = create_stories_from_idea(conn, idea_db, idea_id=1)
        >>> if result:
        ...     print(f"Created {result.count} stories")
        ... else:
        ...     print("Idea already has stories")
    """
    service = StoryFromIdeaService(story_connection, idea_db)
    return service.create_stories_from_idea(idea_id, skip_if_exists)


def get_unreferenced_ideas(
    story_connection: sqlite3.Connection,
    idea_db: SimpleIdeaDatabase
) -> List[SimpleIdea]:
    """Convenience function to get Ideas without Story references.
    
    Args:
        story_connection: SQLite connection for Story table.
        idea_db: SimpleIdeaDatabase instance.
        
    Returns:
        List of SimpleIdea objects that have no Story references.
        
    Example:
        >>> conn = sqlite3.connect("prismq.db")
        >>> conn.row_factory = sqlite3.Row
        >>> idea_db = SimpleIdeaDatabase("idea.db")
        >>> idea_db.connect()
        >>> 
        >>> unreferenced = get_unreferenced_ideas(conn, idea_db)
        >>> print(f"Found {len(unreferenced)} ideas without stories")
    """
    service = StoryFromIdeaService(story_connection, idea_db)
    return service.get_unreferenced_ideas()


__all__ = [
    "StoryFromIdeaService",
    "StoryCreationResult",
    "create_stories_from_idea",
    "get_unreferenced_ideas",
]
