"""Review model for PrismQ content review workflow.

This module defines a simple Review data model with essential fields:
- id: Unique identifier
- text: Review text content
- score: Numeric score for the review
- created_at: Timestamp of creation

The Review model follows single responsibility principle - it stores review
content without relationship tracking. Title/Script entities reference Review
via foreign key (FK) relationships managed at the database level.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Review:
    """Simple Review model for content review storage.
    
    This model represents a review with text content and a numeric score.
    It is designed to be referenced by Title/Script entities via foreign key
    relationships, keeping the Review model focused on a single responsibility.
    
    Schema:
        Review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            score REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    
    Attributes:
        id: Unique identifier (auto-generated in database)
        text: Review text content
        score: Numeric score for the review (e.g., 0.0 to 10.0)
        created_at: Timestamp of creation
    
    Example:
        >>> review = Review(
        ...     text="Great story structure, but the pacing needs work in Act 2.",
        ...     score=7.5
        ... )
        >>> print(review.score)
        7.5
    """
    
    text: str
    score: float
    id: Optional[int] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps and validate fields."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if not isinstance(self.score, (int, float)):
            raise TypeError("score must be an int or float value")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Review to dictionary representation.
        
        Returns:
            Dictionary containing all fields
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        """Create Review from dictionary.
        
        Args:
            data: Dictionary containing Review fields
            
        Returns:
            Review instance
        """
        return cls(
            id=data.get("id"),
            text=data.get("text", ""),
            score=data.get("score", 0.0),
            created_at=data.get("created_at"),
        )
    
    def __repr__(self) -> str:
        """String representation of Review."""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Review(id={self.id}, score={self.score}, text='{text_preview}')"


__all__ = [
    "Review",
]
