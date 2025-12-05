"""Script model for PrismQ content versioning.

Script stores versioned script text content for each story.
Each script can optionally reference a Review for feedback tracking.
Implements IModel interface following Dependency Inversion Principle.

Relationship Pattern:
    - Story 1:N Script (one story has many script versions)
    - Script N:1 Review (each script version can have one review via FK)

Dependency Inversion:
    Script implements the IModel interface, allowing services to
    depend on the abstraction rather than concrete implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from Model.entities.base import IModel


@dataclass
class Script(IModel[int]):
    """Script model for versioned content storage.
    
    Stores script text content with version tracking. Each script
    belongs to a story and can reference a review for feedback.
    Implements IModel interface for consistent persistence operations.
    
    Attributes:
        id: Primary key (auto-generated)
        story_id: FK to Story (required)
        version: Version number (INTEGER >= 0, UINT simulation)
        text: Script content text
        review_id: Optional FK to Review for feedback
        created_at: Timestamp of creation
    
    Constraints:
        - UNIQUE(story_id, version): One version per story
        - version >= 0: Non-negative version numbers
        - review_id: Optional FK to Review table
    
    Schema:
        ```sql
        Script (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version),
            FOREIGN KEY (story_id) REFERENCES Story(id),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        )
        ```
    
    Example:
        >>> script = Script(
        ...     story_id=1,
        ...     version=0,
        ...     text="Once upon a time..."
        ... )
        >>> print(f"Story {script.story_id}, v{script.version}")
        Story 1, v0
        
        >>> # With review
        >>> script_v1 = Script(
        ...     story_id=1,
        ...     version=1,
        ...     text="Revised content...",
        ...     review_id=5
        ... )
    """
    
    story_id: int
    version: int
    text: str
    review_id: Optional[int] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate version is non-negative (UINT simulation)."""
        if self.version < 0:
            raise ValueError(f"Version must be >= 0, got {self.version}")
    
    # === IReadable Implementation ===
    
    def get_id(self) -> Optional[int]:
        """Return the unique identifier of this script.
        
        Returns:
            Optional[int]: The script ID, or None if not persisted yet.
        """
        return self.id
    
    def exists(self) -> bool:
        """Check if the script exists in the database.
        
        Returns:
            bool: True if the script has been persisted (has an ID).
        """
        return self.id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp of this script.
        
        Returns:
            Optional[datetime]: The creation timestamp.
        """
        return self.created_at
    
    # === IModel Implementation ===
    
    def save(self) -> bool:
        """Persist the script to the database.
        
        Note:
            Actual database operations are handled by ScriptRepository.
            This method is for interface compliance. Use repository.insert()
            for actual persistence.
        
        Returns:
            bool: True (placeholder - actual save via repository).
        """
        # Actual persistence handled by repository
        return True
    
    def refresh(self) -> bool:
        """Check if the script can be refreshed from the database.
        
        Note:
            Actual database refresh operations are handled by ScriptRepository.
            This method provides interface compliance and returns whether
            a refresh would succeed (i.e., if the entity exists).
            
            Use repository.find_by_id(script.get_id()) to actually reload
            data from the database.
        
        Returns:
            bool: True if the script exists (refresh possible), False otherwise.
        """
        return self.exists()
    
    # === Serialization ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation with all fields
                serialized for database storage (datetime as ISO string).
        """
        return {
            "id": self.id,
            "story_id": self.story_id,
            "version": self.version,
            "text": self.text,
            "review_id": self.review_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Script":
        """Create Script from dictionary.
        
        Args:
            data: Dictionary containing script data. Required keys:
                story_id, version, text. Optional: id, review_id, created_at.
                
        Returns:
            Script: New Script instance populated with data.
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id"),
            story_id=data["story_id"],
            version=data["version"],
            text=data["text"],
            review_id=data.get("review_id"),
            created_at=created_at or datetime.now(),
        )
    
    # === Version Management ===
    
    def create_next_version(self, new_text: str, review_id: Optional[int] = None) -> "Script":
        """Create a new version of this script with updated text.
        
        This method follows the INSERT+READ only architecture - instead of
        updating the current script, it creates a new version with incremented
        version number.
        
        Args:
            new_text: The new script text for the next version.
            review_id: Optional review reference for the new version.
        
        Returns:
            Script: A new Script instance with version incremented by 1.
            
        Example:
            >>> script_v0 = Script(story_id=1, version=0, text="Original content")
            >>> script_v1 = script_v0.create_next_version("Improved content", review_id=5)
            >>> print(script_v1.version)
            1
        """
        return Script(
            story_id=self.story_id,
            version=self.version + 1,
            text=new_text,
            review_id=review_id,
            created_at=datetime.now(),  # Ensure distinct creation time
        )
    
    def get_version_info(self) -> str:
        """Get a formatted string with version information.
        
        Returns:
            str: Version info in format "v{version} (story_id={story_id})".
            
        Example:
            >>> script = Script(story_id=1, version=2, text="Content")
            >>> print(script.get_version_info())
            v2 (story_id=1)
        """
        return f"v{self.version} (story_id={self.story_id})"
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for this model.
        
        Returns:
            SQL statement to create the Script table with all
            constraints (CHECK, UNIQUE, FOREIGN KEY) and performance indexes.
        """
        return """
        CREATE TABLE IF NOT EXISTS Script (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            version INTEGER NOT NULL CHECK (version >= 0),
            text TEXT NOT NULL,
            review_id INTEGER NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(story_id, version),
            FOREIGN KEY (story_id) REFERENCES Story(id),
            FOREIGN KEY (review_id) REFERENCES Review(id)
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_script_story_id ON Script(story_id);
        CREATE INDEX IF NOT EXISTS idx_script_story_version ON Script(story_id, version);
        """
