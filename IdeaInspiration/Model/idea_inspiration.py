"""IdeaInspiration model for PrismQ content processing.

This module defines the core IdeaInspiration data model used across
PrismQ.IdeaInspiration.Scoring, PrismQ.IdeaInspiration.Classification,
and other PrismQ modules.

The model provides a unified structure for representing content ideas
from various sources (text, video, audio) and includes factory methods
for creating instances from different content types.

Note: PrismQ.Idea.Model maintains an M:N (many-to-many) relationship with
this model. Multiple IdeaInspiration instances can be blended together to
create new Idea objects for scripts, content generation, and other creative
purposes.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class ContentType(Enum):
    """Type of content source."""

    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


@dataclass
class IdeaInspiration:
    """Core data model for content ideas across different media types.

    This model represents content ideas that can originate from text articles,
    video content (with subtitles/transcriptions), or audio content (with
    transcriptions). It provides a unified structure for processing and analyzing
    content across the PrismQ ecosystem.

    Attributes:
        title: The title or headline of the content
        description: A brief description or summary
        content: The main text content (body text, subtitles, or transcription)
        keywords: List of relevant keywords or tags
        source_type: Type of content source (text/video/audio)
        metadata: Additional source-specific metadata (string key-value pairs for
                  SQLite compatibility)
        source_id: Optional unique identifier from the source platform
        source_url: Optional URL to the original content
        source_created_by: Optional creator/author of the source content
        source_created_at: Optional creation timestamp of the source content
        score: Optional numerical score value for the content
        category: Optional primary category classification for the content
        subcategory_relevance: Relevance scores for secondary categories/subcategories
                               (e.g., {'true_crime': 92, 'psychological_thriller': 81,
                               'mystery': 88, 'horror': 75})
        contextual_category_scores: Contextual performance scores as percentages of base
                                    for different contexts (e.g., {'language:english': 145,
                                    'region:us': 160, 'age:18-24': 142, 'gender:female': 135})

    Example:
        >>> idea = IdeaInspiration(
        ...     title="Introduction to Python",
        ...     description="Learn Python basics",
        ...     content="Python is a high-level programming language...",
        ...     keywords=["python", "programming", "tutorial"],
        ...     source_type=ContentType.TEXT
        ... )
    """

    title: str
    description: str = ""
    content: str = ""
    keywords: List[str] = field(default_factory=list)
    source_type: ContentType = ContentType.UNKNOWN
    metadata: Dict[str, str] = field(default_factory=dict)
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    source_created_by: Optional[str] = None
    source_created_at: Optional[str] = None
    score: Optional[int] = None
    category: Optional[str] = None
    subcategory_relevance: Dict[str, int] = field(default_factory=dict)
    contextual_category_scores: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert IdeaInspiration to dictionary representation.

        Returns:
            Dictionary containing all fields with ContentType converted to string
        """
        data = asdict(self)
        data["source_type"] = self.source_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IdeaInspiration":
        """Create IdeaInspiration from dictionary.

        Args:
            data: Dictionary containing IdeaInspiration fields

        Returns:
            IdeaInspiration instance
        """
        # Handle source_type conversion
        source_type_value = data.get("source_type", "unknown")
        if isinstance(source_type_value, str):
            try:
                source_type = ContentType(source_type_value)
            except ValueError:
                source_type = ContentType.UNKNOWN
        else:
            source_type = source_type_value

        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            content=data.get("content", ""),
            keywords=data.get("keywords", []),
            source_type=source_type,
            metadata=data.get("metadata", {}),
            source_id=data.get("source_id"),
            source_url=data.get("source_url"),
            source_created_by=data.get("source_created_by"),
            source_created_at=data.get("source_created_at"),
            score=data.get("score"),
            category=data.get("category"),
            subcategory_relevance=data.get("subcategory_relevance", {}),
            contextual_category_scores=data.get("contextual_category_scores", {}),
        )

    @classmethod
    def from_text(
        cls,
        title: str,
        description: str = "",
        text_content: str = "",
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        source_id: Optional[str] = None,
        source_url: Optional[str] = None,
        source_created_by: Optional[str] = None,
        source_created_at: Optional[str] = None,
        score: Optional[int] = None,
        category: Optional[str] = None,
        subcategory_relevance: Optional[Dict[str, int]] = None,
        contextual_category_scores: Optional[Dict[str, int]] = None,
    ) -> "IdeaInspiration":
        """Create IdeaInspiration from text content.

        Args:
            title: Article or post title
            description: Brief description or summary
            text_content: Full text content
            keywords: List of keywords or tags
            metadata: Additional metadata (string key-value pairs for SQLite compatibility)
            source_id: Optional source identifier
            source_url: Optional source URL
            source_created_by: Optional creator/author of the source content
            source_created_at: Optional creation timestamp of the source content
            score: Optional numerical score value
            category: Optional primary category classification
            subcategory_relevance: Optional relevance scores for subcategories
            contextual_category_scores: Optional contextual scores (language, region, age, gender)

        Returns:
            IdeaInspiration instance with ContentType.TEXT
        """
        return cls(
            title=title,
            description=description,
            content=text_content,
            keywords=keywords or [],
            source_type=ContentType.TEXT,
            metadata=metadata or {},
            source_id=source_id,
            source_url=source_url,
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=score,
            category=category,
            subcategory_relevance=subcategory_relevance or {},
            contextual_category_scores=contextual_category_scores or {},
        )

    @classmethod
    def from_video(
        cls,
        title: str,
        description: str = "",
        subtitle_text: str = "",
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        source_id: Optional[str] = None,
        source_url: Optional[str] = None,
        source_created_by: Optional[str] = None,
        source_created_at: Optional[str] = None,
        score: Optional[int] = None,
        category: Optional[str] = None,
        subcategory_relevance: Optional[Dict[str, int]] = None,
        contextual_category_scores: Optional[Dict[str, int]] = None,
    ) -> "IdeaInspiration":
        """Create IdeaInspiration from video content with subtitles.

        Args:
            title: Video title
            description: Video description
            subtitle_text: Subtitles or transcription text
            keywords: List of keywords or tags
            metadata: Additional video metadata
                      (string key-value pairs, e.g., views="1000", likes="50")
            source_id: Optional video identifier
            source_url: Optional video URL
            source_created_by: Optional creator/author of the source content
            source_created_at: Optional creation timestamp of the source content
            score: Optional numerical score value
            category: Optional primary category classification
            subcategory_relevance: Optional relevance scores for subcategories
            contextual_category_scores: Optional contextual scores (language, region, age, gender)

        Returns:
            IdeaInspiration instance with ContentType.VIDEO
        """
        return cls(
            title=title,
            description=description,
            content=subtitle_text,
            keywords=keywords or [],
            source_type=ContentType.VIDEO,
            metadata=metadata or {},
            source_id=source_id,
            source_url=source_url,
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=score,
            category=category,
            subcategory_relevance=subcategory_relevance or {},
            contextual_category_scores=contextual_category_scores or {},
        )

    @classmethod
    def from_audio(
        cls,
        title: str,
        description: str = "",
        transcription: str = "",
        keywords: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        source_id: Optional[str] = None,
        source_url: Optional[str] = None,
        source_created_by: Optional[str] = None,
        source_created_at: Optional[str] = None,
        score: Optional[int] = None,
        category: Optional[str] = None,
        subcategory_relevance: Optional[Dict[str, int]] = None,
        contextual_category_scores: Optional[Dict[str, int]] = None,
    ) -> "IdeaInspiration":
        """Create IdeaInspiration from audio content with transcription.

        Args:
            title: Audio title or episode name
            description: Audio description
            transcription: Transcribed audio text
            keywords: List of keywords or tags
            metadata: Additional audio metadata
                      (string key-value pairs, e.g., duration="3600", format="mp3")
            source_id: Optional audio identifier
            source_url: Optional audio URL
            source_created_by: Optional creator/author of the source content
            source_created_at: Optional creation timestamp of the source content
            score: Optional numerical score value
            category: Optional primary category classification
            subcategory_relevance: Optional relevance scores for subcategories
            contextual_category_scores: Optional contextual scores (language, region, age, gender)

        Returns:
            IdeaInspiration instance with ContentType.AUDIO
        """
        return cls(
            title=title,
            description=description,
            content=transcription,
            keywords=keywords or [],
            source_type=ContentType.AUDIO,
            metadata=metadata or {},
            source_id=source_id,
            source_url=source_url,
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=score,
            category=category,
            subcategory_relevance=subcategory_relevance or {},
            contextual_category_scores=contextual_category_scores or {},
        )

    def __repr__(self) -> str:
        """String representation of IdeaInspiration."""
        return (
            f"IdeaInspiration(title='{self.title[:50]}...', "
            f"source_type={self.source_type.value}, "
            f"keywords={len(self.keywords)} items)"
        )
