"""Story model for PrismQ content workflow.

Story represents a content piece that progresses through the workflow.
It references versioned Title and Script content, along with an Idea.
Implements IModel interface following Dependency Inversion Principle.

Relationship Pattern:
    - Story 1:N Title (one story has many title versions)
    - Story 1:N Script (one story has many script versions)
    - Story stores idea_id as reference to Idea table

Note:
    Story is the only model that supports UPDATE operations
    (for state transitions). Other models use INSERT-only pattern.
    
    Current title/script versions are implicit - determined by highest version
    in Title/Script tables via ORDER BY version DESC LIMIT 1.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING

from Model.Entities.base import IModel

# Import StoryState from the unified state constants module
from Model.state import StoryState

if TYPE_CHECKING:
    from Model.Repositories.title_repository import TitleRepository
    from Model.Repositories.script_repository import ScriptRepository


@dataclass
class Story(IModel[int]):
    """Story model for content workflow management.
    
    Represents a content piece in the PrismQ workflow. Story maintains
    reference to Idea and tracks workflow state. Current title/script
    versions are implicit - determined by highest version in Title/Script
    tables via ORDER BY version DESC LIMIT 1.
    
    Attributes:
        id: Primary key (auto-generated)
        idea_id: Reference to Idea table (TEXT for flexibility)
        state: Current workflow state (next process name)
        created_at: Timestamp of creation
    
    Note:
        - idea_id can be a string or numeric ID for flexibility
        - state stores the next process name (pattern: PrismQ.T.<Output>.From.<Input1>.<Input2>...)
        - Current title/script versions are implicit (highest version in respective tables)
        - state can be updated (UPDATE operation allowed)
    
    Schema:
        ```sql
        Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NULL,
            state TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        ```
    
    Example:
        >>> story = Story(
        ...     idea_id="1",
        ...     state=StoryState.TITLE_FROM_IDEA
        ... )
        >>> print(f"Story state: {story.state}")
        Story state: PrismQ.T.Title.From.Idea
    """
    
    idea_id: Optional[str] = None
    state: str = "CREATED"
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # === IReadable Implementation ===
    
    def get_id(self) -> Optional[int]:
        """Return the unique identifier of this story.
        
        Returns:
            Optional[int]: The story ID, or None if not persisted yet.
        """
        return self.id
    
    def exists(self) -> bool:
        """Check if the story exists in the database.
        
        Returns:
            bool: True if the story has been persisted (has an ID).
        """
        return self.id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp of this story.
        
        Returns:
            Optional[datetime]: The creation timestamp.
        """
        return self.created_at
    
    # === IModel Implementation ===
    
    def save(self) -> bool:
        """Persist the story to the database.
        
        Note:
            Actual database operations are handled by StoryRepository.
            This method is for interface compliance. Use repository.insert()
            or repository.update() for actual persistence.
        
        Returns:
            bool: True (placeholder - actual save via repository).
        """
        # Actual persistence handled by repository
        return True
    
    def refresh(self) -> bool:
        """Check if the story can be refreshed from the database.
        
        Note:
            Actual database refresh operations are handled by StoryRepository.
            This method provides interface compliance and returns whether
            a refresh would succeed (i.e., if the entity exists).
            
            Use repository.find_by_id(story.get_id()) to actually reload
            data from the database.
        
        Returns:
            bool: True if the story exists (refresh possible), False otherwise.
        """
        return self.exists()
    
    # === Serialization ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the story.
        """
        return {
            "id": self.id,
            "idea_id": self.idea_id,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Story":
        """Create Story from dictionary.
        
        Args:
            data: Dictionary containing story field values.
                Optional: id, idea_id, state, created_at, updated_at
        
        Returns:
            Story: New Story instance.
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id"),
            idea_id=data.get("idea_id"),
            state=data.get("state", "CREATED"),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
        )
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for this model.
        
        Returns:
            SQL statement to create the Story table with all
            constraints and performance indexes.
        
        Note:
            - idea_id is INTEGER FK to Idea(id)
            - state stores the next process name (pattern: PrismQ.T.<Output>.From.<Input1>.<Input2>...)
            - Current title/script versions are implicit - determined by highest version
              in Title/Script tables via ORDER BY version DESC LIMIT 1
        """
        return """
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'PrismQ.T.Idea.Creation',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (idea_id) REFERENCES Idea(id)
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_story_state ON Story(state);
        CREATE INDEX IF NOT EXISTS idx_story_idea_id ON Story(idea_id);
        """
    
    # === Query Helpers ===
    
    def has_idea(self) -> bool:
        """Check if this story has an idea set.
        
        Returns:
            bool: True if idea_id is set.
        """
        return bool(self.idea_id)
    
    def has_title(self, title_repo: "TitleRepository") -> bool:
        """Check if this story has a title generated.
        
        Queries the Title table to check if any title exists for this story.
        
        Args:
            title_repo: TitleRepository instance to query titles.
            
        Returns:
            bool: True if at least one title exists for this story.
        """
        if self.id is None:
            return False
        return title_repo.find_latest_version(self.id) is not None
    
    def has_script(self, script_repo: "ScriptRepository") -> bool:
        """Check if this story has a script generated.
        
        Queries the Script table to check if any script exists for this story.
        
        Args:
            script_repo: ScriptRepository instance to query scripts.
            
        Returns:
            bool: True if at least one script exists for this story.
        """
        if self.id is None:
            return False
        return script_repo.find_latest_version(self.id) is not None
    
    def needs_script(
        self,
        title_repo: "TitleRepository",
        script_repo: "ScriptRepository"
    ) -> bool:
        """Check if this story needs a script to be generated.
        
        A story needs a script if:
        - It has an idea (idea_id is set)
        - It has a title (title exists in Title table)
        - It does not have a script (no script in Script table)
        
        Args:
            title_repo: TitleRepository instance to check for titles.
            script_repo: ScriptRepository instance to check for scripts.
            
        Returns:
            bool: True if story is ready for script generation.
        """
        return (
            self.has_idea() and
            self.has_title(title_repo) and
            not self.has_script(script_repo)
        )
    
    def update_state(self, new_state: str) -> None:
        """Update the workflow state.
        
        Args:
            new_state: The new state value.
        """
        self.state = new_state
        self.updated_at = datetime.now()
    
    def transition_to(self, new_state: "StoryState") -> None:
        """Transition to a new workflow state.
        
        Args:
            new_state: The StoryState to transition to.
            
        Raises:
            TypeError: If new_state is not a StoryState enum value.
        """
        if not isinstance(new_state, StoryState):
            raise TypeError(f"new_state must be a StoryState enum value, got {type(new_state).__name__}")
        self.state = new_state.value
        self.updated_at = datetime.now()
