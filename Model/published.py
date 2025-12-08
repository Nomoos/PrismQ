"""Published model for PrismQ multi-platform content distribution.

This module defines the Published model which tracks publishing status
for Stories across different languages and platforms.

Relationships:
    - Published N:1 Story (many published entries per story)
    - Published N:1 Language (one language per entry)
    - Published N:1 Platform (one platform per entry)

The model provides flags to track completion and publishing status
for text, audio, and video content types.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Language(str, Enum):
    """Supported languages for content publishing."""

    ENGLISH = "en"
    CZECH = "cs"
    GERMAN = "de"
    SPANISH = "es"
    FRENCH = "fr"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


class Platform(str, Enum):
    """Supported publishing platforms."""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    PODCAST = "podcast"


@dataclass
class Published:
    """Publishing status model for multi-platform content distribution.

    Tracks the publishing status of a Story for a specific language
    and platform combination. Includes flags for completion and
    publishing status of text, audio, and video content.

    Attributes:
        id: Primary key (auto-generated)
        story_id: FK to Story table
        language_id: Language code (e.g., 'en', 'cs')
        platform_id: Platform code (e.g., 'youtube', 'tiktok')
        is_published: Overall publishing status
        is_completed: Overall completion status
        is_text_completed: Text content completion status
        is_audio_completed: Audio content completion status
        is_video_completed: Video content completion status
        is_text_published: Text content publishing status
        is_audio_published: Audio content publishing status
        is_video_published: Video content publishing status
        created_at: Timestamp of creation
        updated_at: Timestamp of last update

    Schema:
        ```sql
        Published (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            language_id TEXT NOT NULL,
            platform_id TEXT NOT NULL,
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
            FOREIGN KEY (story_id) REFERENCES Story(id),
            UNIQUE(story_id, language_id, platform_id)
        )
        ```

    Example:
        >>> published = Published(
        ...     story_id=1,
        ...     language_id=Language.ENGLISH.value,
        ...     platform_id=Platform.YOUTUBE.value,
        ...     is_text_completed=True
        ... )
    """

    story_id: int
    language_id: str
    platform_id: str
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

    def get_id(self) -> Optional[int]:
        """Return the unique identifier."""
        return self.id

    def exists(self) -> bool:
        """Check if the record exists in the database."""
        return self.id is not None

    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp."""
        return self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "story_id": self.story_id,
            "language_id": self.language_id,
            "platform_id": self.platform_id,
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
    def from_dict(cls, data: Dict[str, Any]) -> "Published":
        """Create Published from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            story_id=data["story_id"],
            language_id=data["language_id"],
            platform_id=data["platform_id"],
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
        CREATE TABLE IF NOT EXISTS Published (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            language_id TEXT NOT NULL,
            platform_id TEXT NOT NULL,
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
            FOREIGN KEY (story_id) REFERENCES Story(id),
            UNIQUE(story_id, language_id, platform_id)
        );
        
        -- Performance indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_published_story_id ON Published(story_id);
        CREATE INDEX IF NOT EXISTS idx_published_language ON Published(language_id);
        CREATE INDEX IF NOT EXISTS idx_published_platform ON Published(platform_id);
        CREATE INDEX IF NOT EXISTS idx_published_status ON Published(is_published, is_completed);
        """

    # === Status Helpers ===

    def is_fully_completed(self) -> bool:
        """Check if all content types are completed."""
        return self.is_text_completed and self.is_audio_completed and self.is_video_completed

    def is_fully_published(self) -> bool:
        """Check if all content types are published."""
        return self.is_text_published and self.is_audio_published and self.is_video_published

    def update_completion_status(self) -> None:
        """Update is_completed based on individual completion flags."""
        self.is_completed = self.is_fully_completed()
        self.updated_at = datetime.now()

    def update_publish_status(self) -> None:
        """Update is_published based on individual publish flags."""
        self.is_published = self.is_fully_published()
        self.updated_at = datetime.now()
