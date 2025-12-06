"""Review model for PrismQ content review workflow.

This module defines a simple Review data model with essential fields:
- id: Unique identifier
- text: Review text content
- score: Integer score for the review (0 to 100)
- created_at: Timestamp of creation

The Review model follows single responsibility principle - it stores review
content without relationship tracking. Title/Script entities reference Review
via foreign key (FK) relationships managed at the database level.

Implements IModel interface following Dependency Inversion Principle.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

from Model.entities.base import IModel


# Score range constants (integer 0-100)
MIN_SCORE = 0
MAX_SCORE = 100


@dataclass
class Review(IModel[int]):
    """Simple Review model for content review storage.
    
    This model represents a review with text content and an integer score.
    It is designed to be referenced by Title/Script entities via foreign key
    relationships, keeping the Review model focused on a single responsibility.
    
    Implements IModel interface for database persistence.
    
    Schema:
        Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    
    Attributes:
        id: Unique identifier (auto-generated in database)
        text: Review text content
        score: Integer score for the review (0 to 100)
        created_at: Timestamp of creation
    
    Example:
        >>> review = Review(
        ...     text="Great story structure, but the pacing needs work in Act 2.",
        ...     score=75
        ... )
        >>> print(review.score)
        75
    """
    
    text: str
    score: int
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize timestamps and validate fields."""
        if not isinstance(self.score, int):
            raise TypeError("score must be an integer value")
        if self.score < MIN_SCORE or self.score > MAX_SCORE:
            raise ValueError(f"score must be between {MIN_SCORE} and {MAX_SCORE}, got {self.score}")
    
    # === IReadable Implementation ===
    
    def get_id(self) -> Optional[int]:
        """Return the unique identifier of this review.
        
        Returns:
            Optional[int]: The review ID, or None if not persisted yet.
        """
        return self.id
    
    def exists(self) -> bool:
        """Check if the review exists in the database.
        
        Returns:
            bool: True if the review has been persisted (has an ID).
        """
        return self.id is not None
    
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp of this review.
        
        Returns:
            Optional[datetime]: The creation timestamp.
        """
        return self.created_at
    
    # === IModel Implementation ===
    
    def save(self) -> bool:
        """Persist the review to the database.
        
        Note:
            Actual database operations would be handled by a repository.
            This method is for interface compliance.
        
        Returns:
            bool: True (placeholder - actual save via repository).
        """
        return True
    
    def refresh(self) -> bool:
        """Check if the review can be refreshed from the database.
        
        Returns:
            bool: True if the review exists (refresh possible), False otherwise.
        """
        return self.exists()
    
    # === Serialization ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Review to dictionary representation.
        
        Returns:
            Dictionary containing all fields
        """
        return {
            "id": self.id,
            "text": self.text,
            "score": self.score,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        """Create Review from dictionary.
        
        Args:
            data: Dictionary containing Review fields
            
        Returns:
            Review instance
        """
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id"),
            text=data.get("text", ""),
            score=data.get("score", 0),
            created_at=created_at or datetime.now(),
        )
    
    def __repr__(self) -> str:
        """String representation of Review."""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Review(id={self.id}, score={self.score}, text='{text_preview}')"
    
    @classmethod
    def get_sql_schema(cls) -> str:
        """Get the SQL CREATE TABLE statement for this model.
        
        Returns:
            SQL statement to create the Review table with all
            constraints (CHECK) for score validation.
        """
        return """
        CREATE TABLE IF NOT EXISTS Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score INTEGER CHECK (score >= 0 AND score <= 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """


__all__ = [
    "Review",
    "MIN_SCORE",
    "MAX_SCORE",
]
