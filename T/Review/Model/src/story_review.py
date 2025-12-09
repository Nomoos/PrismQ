"""StoryReview linking table model for PrismQ.

Allows one Story to have multiple reviews with different types:
- grammar: Grammar and spelling review
- tone: Tone and voice consistency
- content: Content quality and accuracy
- consistency: Internal consistency check
- editing: Editorial improvements
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ReviewType(str, Enum):
    """Types of Story reviews."""

    GRAMMAR = "grammar"
    TONE = "tone"
    CONTENT = "content"
    CONSISTENCY = "consistency"
    EDITING = "editing"


@dataclass
class StoryReview:
    """Linking table model for Story reviews.

    Allows many-to-many relationship between Story and Review,
    with additional metadata (version, review_type).

    Attributes:
        id: Primary key (auto-generated)
        story_id: FK to Story
        review_id: FK to Review
        version: Story version being reviewed (>= 0, UINT simulation)
        review_type: Type of review (grammar, tone, content, etc.)
        created_at: Timestamp of creation

    Note:
        UNIQUE(story_id, version, review_type) prevents duplicate
        reviews of the same type for the same version.

    Example:
        >>> story_review = StoryReview(
        ...     story_id=1,
        ...     review_id=5,
        ...     version=2,
        ...     review_type=ReviewType.GRAMMAR
        ... )
    """

    story_id: int
    review_id: int
    version: int
    review_type: ReviewType
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate version is non-negative (UINT simulation)."""
        if self.version < 0:
            raise ValueError(f"Version must be >= 0, got {self.version}")

        # Convert string to enum if needed
        if isinstance(self.review_type, str):
            self.review_type = ReviewType(self.review_type)

    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "story_id": self.story_id,
            "review_id": self.review_id,
            "version": self.version,
            "review_type": (
                self.review_type.value
                if isinstance(self.review_type, ReviewType)
                else self.review_type
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StoryReview":
        """Create StoryReview from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        review_type = data["review_type"]
        if isinstance(review_type, str):
            review_type = ReviewType(review_type)

        return cls(
            id=data.get("id"),
            story_id=data["story_id"],
            review_id=data["review_id"],
            version=data["version"],
            review_type=review_type,
            created_at=created_at or datetime.now(),
        )
