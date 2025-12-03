"""Story model for PrismQ content workflow.

Story represents a content piece that progresses through the workflow.
It references versioned Title and Script content, along with an Idea.

This is the top-level Story model that includes publishing status flags
derived from the Published table.

Relationship Pattern:
    - Story 1:N Title (one story has many title versions)
    - Story 1:N Script (one story has many script versions)
    - Story 1:N Published (one story can be published to many platforms/languages)
    - Story stores idea_id as reference to Idea table
    - Story stores idea_json as serialized Idea data (optional)

Note:
    Story is the only model that supports UPDATE operations
    (for state transitions). Other models use INSERT-only pattern.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from Model.state import StoryState

if TYPE_CHECKING:
    from Model.published import Published


@dataclass
class Story:
    """Story model for content workflow management.
    
    Represents a content piece in the PrismQ workflow. Story maintains
    references to Title and Script versions, stores serialized Idea data,
    and tracks workflow state.
    
    Publishing status flags are derived from the Published table and
    indicate the overall completion/publishing status across all
    platforms and languages.
    
    Attributes:
        id: Primary key (auto-generated)
        idea_id: FK to Idea table (TEXT for flexibility)
        idea_json: Serialized Idea data (JSON string)
        title_id: FK to latest Title version
        script_id: FK to latest Script version
        state: Current workflow state
        is_published: Any platform has published content
        is_completed: All content is completed
        is_text_completed: Text content is completed
        is_audio_completed: Audio content is completed
        is_video_completed: Video content is completed
        is_text_published: Text content is published somewhere
        is_audio_published: Audio content is published somewhere
        is_video_published: Video content is published somewhere
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    
    Schema:
        ```sql
        Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NULL,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            is_published INTEGER NOT NULL DEFAULT 0,
            is_completed INTEGER NOT NULL DEFAULT 0,
            is_text_completed INTEGER NOT NULL DEFAULT 0,
            is_audio_completed INTEGER NOT NULL DEFAULT 0,
            is_video_completed INTEGER NOT NULL DEFAULT 0,
            is_text_published INTEGER NOT NULL DEFAULT 0,
            is_audio_published INTEGER NOT NULL DEFAULT 0,
            is_video_published INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (title_id) REFERENCES Title(id),
            FOREIGN KEY (script_id) REFERENCES Script(id)
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
    idea_json: Optional[str] = None
    title_id: Optional[int] = None
    script_id: Optional[int] = None
    state: str = "CREATED"
    # Publishing status flags (derived from Published table)
    is_published: bool = False
    is_completed: bool = False
    is_text_completed: bool = False
    is_audio_completed: bool = False
    is_video_completed: bool = False
    is_text_published: bool = False
    is_audio_published: bool = False
    is_video_published: bool = False
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # === IReadable Implementation ===
    
    def get_id(self) -> Optional[int]:
        """Return the unique identifier of this story."""
        return self.id
    
    def exists(self) -> bool:
        """Check if the story exists in the database."""
        return self.id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp of this story."""
        return self.created_at
    
    # === IModel Implementation ===
    
    def save(self) -> bool:
        """Persist the story to the database.
        
        Note:
            Actual database operations are handled by StoryRepository.
            Use repository.insert() or repository.update() for actual persistence.
        """
        return True
    
    def refresh(self) -> bool:
        """Check if the story can be refreshed from the database."""
        return self.exists()
    
    # === Serialization ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "idea_id": self.idea_id,
            "idea_json": self.idea_json,
            "title_id": self.title_id,
            "script_id": self.script_id,
            "state": self.state,
            "is_published": int(self.is_published),
            "is_completed": int(self.is_completed),
            "is_text_completed": int(self.is_text_completed),
            "is_audio_completed": int(self.is_audio_completed),
            "is_video_completed": int(self.is_video_completed),
            "is_text_published": int(self.is_text_published),
            "is_audio_published": int(self.is_audio_published),
            "is_video_published": int(self.is_video_published),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Story":
        """Create Story from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id"),
            idea_id=data.get("idea_id"),
            idea_json=data.get("idea_json"),
            title_id=data.get("title_id"),
            script_id=data.get("script_id"),
            state=data.get("state", "CREATED"),
            is_published=bool(data.get("is_published", False)),
            is_completed=bool(data.get("is_completed", False)),
            is_text_completed=bool(data.get("is_text_completed", False)),
            is_audio_completed=bool(data.get("is_audio_completed", False)),
            is_video_completed=bool(data.get("is_video_completed", False)),
            is_text_published=bool(data.get("is_text_published", False)),
            is_audio_published=bool(data.get("is_audio_published", False)),
            is_video_published=bool(data.get("is_video_published", False)),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
        )
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for this model."""
        return """
        CREATE TABLE IF NOT EXISTS Story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT NULL,
            idea_json TEXT NULL,
            title_id INTEGER NULL,
            script_id INTEGER NULL,
            state TEXT NOT NULL DEFAULT 'CREATED',
            is_published INTEGER NOT NULL DEFAULT 0,
            is_completed INTEGER NOT NULL DEFAULT 0,
            is_text_completed INTEGER NOT NULL DEFAULT 0,
            is_audio_completed INTEGER NOT NULL DEFAULT 0,
            is_video_completed INTEGER NOT NULL DEFAULT 0,
            is_text_published INTEGER NOT NULL DEFAULT 0,
            is_audio_published INTEGER NOT NULL DEFAULT 0,
            is_video_published INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (title_id) REFERENCES Title(id),
            FOREIGN KEY (script_id) REFERENCES Script(id)
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_story_state ON Story(state);
        CREATE INDEX IF NOT EXISTS idx_story_idea_id ON Story(idea_id);
        CREATE INDEX IF NOT EXISTS idx_story_title_id ON Story(title_id);
        CREATE INDEX IF NOT EXISTS idx_story_script_id ON Story(script_id);
        CREATE INDEX IF NOT EXISTS idx_story_published ON Story(is_published, is_completed);
        """
    
    # === Query Helpers ===
    
    def has_idea(self) -> bool:
        """Check if this story has an idea set."""
        return bool(self.idea_id) or bool(self.idea_json)
    
    def has_title(self) -> bool:
        """Check if this story has a title generated."""
        return self.title_id is not None
    
    def has_script(self) -> bool:
        """Check if this story has a script generated."""
        return self.script_id is not None
    
    def needs_script(self) -> bool:
        """Check if this story needs a script to be generated."""
        return self.has_idea() and self.has_title() and not self.has_script()
    
    def update_state(self, new_state: str) -> None:
        """Update the workflow state."""
        self.state = new_state
        self.updated_at = datetime.now()
    
    def set_script(self, script_id: int) -> None:
        """Set the script reference and update state."""
        self.script_id = script_id
        self.state = "SCRIPT"
        self.updated_at = datetime.now()
    
    def set_title(self, title_id: int) -> None:
        """Set the title reference and update state."""
        self.title_id = title_id
        self.state = "TITLE"
        self.updated_at = datetime.now()
    
    def transition_to(self, new_state: "StoryState") -> None:
        """Transition to a new workflow state."""
        if not isinstance(new_state, StoryState):
            raise TypeError(f"new_state must be a StoryState enum value, got {type(new_state).__name__}")
        self.state = new_state.value
        self.updated_at = datetime.now()
    
    # === Publishing Status Methods ===
    
    def update_from_published(self, published_records: List["Published"]) -> None:
        """Update publishing flags from a list of Published records.
        
        This method aggregates the publishing status from all Published
        records associated with this Story.
        
        Args:
            published_records: List of Published records for this story
        """
        if not published_records:
            return
        
        # Aggregate flags - any True means True for the story
        self.is_published = any(p.is_published for p in published_records)
        self.is_completed = all(p.is_completed for p in published_records)
        self.is_text_completed = any(p.is_text_completed for p in published_records)
        self.is_audio_completed = any(p.is_audio_completed for p in published_records)
        self.is_video_completed = any(p.is_video_completed for p in published_records)
        self.is_text_published = any(p.is_text_published for p in published_records)
        self.is_audio_published = any(p.is_audio_published for p in published_records)
        self.is_video_published = any(p.is_video_published for p in published_records)
        self.updated_at = datetime.now()
    
    def is_fully_published(self) -> bool:
        """Check if all content types have been published."""
        return self.is_text_published and self.is_audio_published and self.is_video_published
    
    def is_fully_completed(self) -> bool:
        """Check if all content types have been completed."""
        return self.is_text_completed and self.is_audio_completed and self.is_video_completed
