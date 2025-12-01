"""Story model for PrismQ content workflow.

Story represents a content piece that progresses through the workflow.
It references versioned Title and Script content, along with an Idea.
Implements IModel interface following Dependency Inversion Principle.

Relationship Pattern:
    - Story 1:N Title (one story has many title versions)
    - Story 1:N Script (one story has many script versions)
    - Story stores idea_json as serialized Idea data

Note:
    Story is the only model that supports UPDATE operations
    (for state transitions). Other models use INSERT-only pattern.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from .base import IModel


@dataclass
class Story(IModel[int]):
    """Story model for content workflow management.
    
    Represents a content piece in the PrismQ workflow. Story maintains
    references to Title and Script versions, stores serialized Idea data,
    and tracks workflow state.
    
    Attributes:
        id: Primary key (auto-generated)
        idea_json: Serialized Idea data (JSON string) - populated when idea is set
        title_id: FK to latest Title version (optional, populated when title is generated)
        script_id: FK to latest Script version (optional, populated when script is generated)
        state: Current workflow state (e.g., 'IDEA', 'TITLE', 'SCRIPT')
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    
    Note:
        - idea_json stores the Idea as JSON to decouple from Idea module
        - title_id and script_id reference the latest versions
        - state can be updated (UPDATE operation allowed)
    
    Schema:
        ```sql
        Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (title_id) REFERENCES Title(id),
            FOREIGN KEY (script_id) REFERENCES Script(id)
        )
        ```
    
    Example:
        >>> story = Story(
        ...     idea_json='{"title": "My Idea", "concept": "A concept"}',
        ...     state='IDEA'
        ... )
        >>> print(f"Story state: {story.state}")
        Story state: IDEA
    """
    
    idea_json: Optional[str] = None
    title_id: Optional[int] = None
    script_id: Optional[int] = None
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
            "idea_json": self.idea_json,
            "title_id": self.title_id,
            "script_id": self.script_id,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Story":
        """Create Story from dictionary.
        
        Args:
            data: Dictionary containing story field values.
                Optional: id, idea_json, title_id, script_id, state,
                          created_at, updated_at
        
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
            idea_json=data.get("idea_json"),
            title_id=data.get("title_id"),
            script_id=data.get("script_id"),
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
        """
        return """
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (title_id) REFERENCES Title(id),
            FOREIGN KEY (script_id) REFERENCES Script(id)
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_story_state ON Story(state);
        CREATE INDEX IF NOT EXISTS idx_story_title_id ON Story(title_id);
        CREATE INDEX IF NOT EXISTS idx_story_script_id ON Story(script_id);
        """
    
    # === Query Helpers ===
    
    def has_idea(self) -> bool:
        """Check if this story has an idea set.
        
        Returns:
            bool: True if idea_json is not None and not empty.
        """
        return bool(self.idea_json)
    
    def has_title(self) -> bool:
        """Check if this story has a title generated.
        
        Returns:
            bool: True if title_id is set.
        """
        return self.title_id is not None
    
    def has_script(self) -> bool:
        """Check if this story has a script generated.
        
        Returns:
            bool: True if script_id is set.
        """
        return self.script_id is not None
    
    def needs_script(self) -> bool:
        """Check if this story needs a script to be generated.
        
        A story needs a script if:
        - It has an idea (idea_json is set)
        - It has a title (title_id is set)
        - It does not have a script (script_id is None)
        
        Returns:
            bool: True if story is ready for script generation.
        """
        return self.has_idea() and self.has_title() and not self.has_script()
    
    def update_state(self, new_state: str) -> None:
        """Update the workflow state.
        
        Args:
            new_state: The new state value.
        """
        self.state = new_state
        self.updated_at = datetime.now()
    
    def set_script(self, script_id: int) -> None:
        """Set the script reference and update state.
        
        Args:
            script_id: ID of the generated script.
        """
        self.script_id = script_id
        self.state = "SCRIPT"
        self.updated_at = datetime.now()
    
    def set_title(self, title_id: int) -> None:
        """Set the title reference and update state.
        
        Args:
            title_id: ID of the generated title.
        """
        self.title_id = title_id
        self.state = "TITLE"
        self.updated_at = datetime.now()
