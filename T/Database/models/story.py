"""Story model for PrismQ content workflow.

Story represents the central entity in the PrismQ workflow that ties together
Ideas, Titles, Scripts, and Reviews. Unlike versioned entities (Title, Script),
Story uses UPDATE for state transitions while maintaining immutable core data.

Implements IModel interface following Dependency Inversion Principle.

Relationship Pattern:
    - Idea 1:N Story (one idea spawns 10 stories)
    - Story 1:N Title (one story has many title versions)
    - Story 1:N Script (one story has many script versions)
    - Story N:M Review (through StoryReview linking table)

State Management:
    Story is the only updatable entity in PrismQ. State transitions are:
    - CREATED: Initial state when Story is first created
    - TITLE_V0: First title generated from Idea
    - SCRIPT_V0: First script generated
    - ... (following the workflow stages)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class StoryState(str, Enum):
    """Workflow states for Story progression.
    
    Each state represents a stage in the content creation workflow.
    States are ordered to track progress through the pipeline.
    """
    CREATED = "created"
    TITLE_V0 = "title_v0"
    SCRIPT_V0 = "script_v0"
    REVIEW_TITLE = "review_title"
    TITLE_V1 = "title_v1"
    REVIEW_SCRIPT = "review_script"
    SCRIPT_V1 = "script_v1"
    TITLE_V2 = "title_v2"
    SCRIPT_V2 = "script_v2"
    TITLE_V3 = "title_v3"
    SCRIPT_V3 = "script_v3"
    QUALITY_REVIEW = "quality_review"
    EXPERT_REVIEW = "expert_review"
    POLISH = "polish"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Import base after defining enums to avoid circular imports
from .base import IModel


@dataclass
class Story(IModel[int]):
    """Story model - central entity linking Ideas to content versions.
    
    Story is the main workflow entity that:
    - References the source Idea (FK to Idea table or Idea ID)
    - Owns multiple Title versions (1:N relationship)
    - Owns multiple Script versions (1:N relationship)
    - Has a mutable state field for workflow progression
    - Tracks creation and update timestamps
    
    Attributes:
        id: Primary key (auto-generated)
        idea_id: Reference to the source Idea (can be string UUID or int)
        state: Current workflow state
        created_at: Timestamp of creation
        updated_at: Timestamp of last state change
    
    Note:
        - Story is created when Title.From.Idea generates content
        - 10 Stories are created from one Idea (as per workflow)
        - State is the only mutable field
        - Stories are never deleted
    
    Schema:
        ```sql
        Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN (...)),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        
        CREATE INDEX idx_story_idea_id ON Story(idea_id);
        CREATE INDEX idx_story_state ON Story(state);
        ```
    
    Example:
        >>> story = Story(
        ...     idea_id="idea-123",
        ...     state=StoryState.CREATED
        ... )
        >>> print(f"Story from idea {story.idea_id}, state: {story.state.value}")
        Story from idea idea-123, state: created
        
        >>> # Progress to next state
        >>> story.state = StoryState.TITLE_V0
        >>> print(story.state.value)
        title_v0
    """
    
    idea_id: str
    state: StoryState = StoryState.CREATED
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate and convert state if needed."""
        if isinstance(self.state, str):
            self.state = StoryState(self.state)
        
        if not self.idea_id:
            raise ValueError("idea_id cannot be empty")
    
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
            for actual persistence.
        
        Returns:
            bool: True (placeholder - actual save via repository).
        """
        return True
    
    def refresh(self) -> bool:
        """Check if the story can be refreshed from the database.
        
        Note:
            Actual database refresh operations are handled by StoryRepository.
            This method provides interface compliance and returns whether
            a refresh would succeed (i.e., if the entity exists).
        
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
            "state": self.state.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Story":
        """Create Story from dictionary.
        
        Args:
            data: Dictionary containing story field values.
                Required: idea_id
                Optional: id, state, created_at, updated_at
        
        Returns:
            Story: New Story instance.
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        state = data.get("state", StoryState.CREATED)
        if isinstance(state, str):
            state = StoryState(state)
        
        return cls(
            id=data.get("id"),
            idea_id=data["idea_id"],
            state=state,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
        )
    
    # === State Management ===
    
    def transition_to(self, new_state: StoryState) -> "Story":
        """Transition to a new workflow state.
        
        This updates the state and updated_at timestamp.
        Note: Use StoryRepository.update() to persist the change.
        
        Args:
            new_state: The new state to transition to.
        
        Returns:
            Story: Self for method chaining.
            
        Example:
            >>> story = Story(idea_id="idea-123")
            >>> story.transition_to(StoryState.TITLE_V0)
            >>> print(story.state.value)
            title_v0
        """
        self.state = new_state
        self.updated_at = datetime.now()
        return self
    
    def get_state_info(self) -> str:
        """Get a formatted string with state information.
        
        Returns:
            str: State info in format "Story #{id} - {state}".
            
        Example:
            >>> story = Story(idea_id="idea-123")
            >>> story.id = 1
            >>> print(story.get_state_info())
            Story #1 - created
        """
        id_str = f"#{self.id}" if self.id else "(new)"
        return f"Story {id_str} - {self.state.value}"
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for this model.
        
        Returns:
            SQL statement to create the Story table with all
            constraints and performance indexes.
        
        Note:
            The state CHECK constraint is generated dynamically from
            the StoryState enum to maintain consistency.
        """
        state_values = ", ".join(f"'{s.value}'" for s in StoryState)
        
        return f"""
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NOT NULL,
            state TEXT NOT NULL CHECK (state IN ({state_values})),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_story_idea_id ON Story(idea_id);
        CREATE INDEX IF NOT EXISTS idx_story_state ON Story(state);
        """
