"""Title model for PrismQ content workflow.

Title versions with direct review FK relationship.
Implements IModel interface following Dependency Inversion Principle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from .base import IModel


@dataclass
class Title(IModel):
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
        - Use get_current_version() to find latest version
    
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
