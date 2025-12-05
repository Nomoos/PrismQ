"""Title model for PrismQ content workflow.

Title versions with direct review FK relationship.
Implements IModel interface following Dependency Inversion Principle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from Model.entities.base import IModel


@dataclass
class Title(IModel[int]):
    """Title version model.
    
    Stores versioned title content with optional review reference.
    Each story can have multiple title versions, each potentially
    with a review.
    
    Attributes:
        id: Primary key (auto-generated)
        story_id: FK to Story
        version: Title version number (>= 0, UINT simulation)
        text: Title text content
        review_id: FK to Review (optional, 1:1 per version)
        created_at: Timestamp of creation
    
    Note:
        - UNIQUE constraint on (story_id, version)
        - version >= 0 (simulates UINT)
        - Use repository's find_latest_version() to find current version
    
    Schema:
        ```sql
        Title (
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
        >>> title = Title(
        ...     story_id=1,
        ...     version=0,
        ...     text="10 Tips for Better Python Code"
        ... )
        >>> print(f"v{title.version}: {title.text}")
        v0: 10 Tips for Better Python Code
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
        
        if not self.text:
            raise ValueError("Title text cannot be empty")
    
    # === IReadable Implementation ===
    
    def get_id(self) -> Optional[int]:
        """Return the unique identifier of this title.
        
        Returns:
            Optional[int]: The title ID, or None if not persisted yet.
        """
        return self.id
    
    def exists(self) -> bool:
        """Check if the title exists in the database.
        
        Returns:
            bool: True if the title has been persisted (has an ID).
        """
        return self.id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp of this title.
        
        Returns:
            Optional[datetime]: The creation timestamp.
        """
        return self.created_at
    
    # === IModel Implementation ===
    
    def save(self) -> bool:
        """Persist the title to the database.
        
        Note:
            Actual database operations are handled by TitleRepository.
            This method is for interface compliance. Use repository.insert()
            for actual persistence.
        
        Returns:
            bool: True (placeholder - actual save via repository).
        """
        # Actual persistence handled by repository
        return True
    
    def refresh(self) -> bool:
        """Check if the title can be refreshed from the database.
        
        Note:
            Actual database refresh operations are handled by TitleRepository.
            This method provides interface compliance and returns whether
            a refresh would succeed (i.e., if the entity exists).
            
            Use repository.find_by_id(title.get_id()) to actually reload
            data from the database.
        
        Returns:
            bool: True if the title exists (refresh possible), False otherwise.
        """
        return self.exists()
    
    # === Serialization ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the title.
        """
        return {
            "id": self.id,
            "story_id": self.story_id,
            "version": self.version,
            "text": self.text,
            "review_id": self.review_id,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Title":
        """Create Title from dictionary.
        
        Args:
            data: Dictionary containing title field values.
                Required: story_id, version, text
                Optional: id, review_id, created_at
        
        Returns:
            Title: New Title instance.
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
    
    def create_next_version(self, new_text: str, review_id: Optional[int] = None) -> "Title":
        """Create a new version of this title with updated text.
        
        This method follows the INSERT+READ only architecture - instead of
        updating the current title, it creates a new version with incremented
        version number.
        
        Args:
            new_text: The new title text for the next version.
            review_id: Optional review reference for the new version.
        
        Returns:
            Title: A new Title instance with version incremented by 1.
            
        Example:
            >>> title_v0 = Title(story_id=1, version=0, text="Original Title")
            >>> title_v1 = title_v0.create_next_version("Improved Title", review_id=5)
            >>> print(title_v1.version)
            1
        """
        return Title(
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
            >>> title = Title(story_id=1, version=2, text="Title")
            >>> print(title.get_version_info())
            v2 (story_id=1)
        """
        return f"v{self.version} (story_id={self.story_id})"
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for this model.
        
        Returns:
            SQL statement to create the Title table with all
            constraints (CHECK, UNIQUE, FOREIGN KEY) and performance indexes.
        """
        return """
        CREATE TABLE IF NOT EXISTS Title (
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
        CREATE INDEX IF NOT EXISTS idx_title_story_id ON Title(story_id);
        CREATE INDEX IF NOT EXISTS idx_title_story_version ON Title(story_id, version);
        """
