"""Script model for PrismQ content versioning.

Script stores versioned script text content for each story.
Each script can optionally reference a Review for feedback tracking.

Relationship Pattern:
    - Story 1:N Script (one story has many script versions)
    - Script N:1 Review (each script version can have one review via FK)

Dependency Inversion:
    Script implements the IModel protocol, allowing services to
    depend on the abstraction rather than concrete implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Script:
    """Script model for versioned content storage.
    
    Stores script text content with version tracking. Each script
    belongs to a story and can reference a review for feedback.
    
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
