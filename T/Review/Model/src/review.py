"""Review model for PrismQ content feedback.

Simple review content model without relationship tracking.
Title/Script reference Review directly via FK.
Story references Review via StoryReview linking table.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Review:
    """Simple review content model.
    
    Attributes:
        id: Primary key (auto-generated)
        text: Review feedback text
        score: Review score (0-100)
        created_at: Timestamp of creation
    
    Note:
        - Title/Script have direct FK to Review (1:1 per version)
        - Story uses StoryReview linking table (many reviews per story)
    
    Example:
        >>> review = Review(
        ...     text="Great title! Clear and engaging.",
        ...     score=85
        ... )
        >>> print(f"Score: {review.score}")
        Score: 85
    """
    
    text: str
    score: Optional[int] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate score range."""
        if self.score is not None:
            if not (0 <= self.score <= 100):
                raise ValueError(f"Score must be 0-100, got {self.score}")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "text": self.text,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Review":
        """Create Review from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get("id"),
            text=data["text"],
            score=data.get("score"),
            created_at=created_at or datetime.now(),
        )
