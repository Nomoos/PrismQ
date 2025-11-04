# Model Module - User Guide

## Overview

The `IdeaInspiration` data model provides a unified structure for representing content ideas from various sources (text, video, audio) with factory methods for easy creation.

## Features

- 🎯 **Unified Data Model** - Single structure for text, video, and audio content
- 🏭 **Factory Methods** - Easy creation from different sources (text, YouTube, Reddit, etc.)
- 🔀 **Blending Support** - Combine multiple inspirations by topic, trend, or platform
- 📦 **Serialization** - Convert to/from dictionaries for storage and transmission
- 🔌 **Zero Dependencies** - Pure Python with no external requirements
- 🧪 **Well Tested** - Comprehensive test coverage
- 📝 **Type Hints** - Full type annotation support

## Quick Start

```python
from idea_inspiration import IdeaInspiration, ContentType

# Create from text content
idea = IdeaInspiration.from_text(
    title="Introduction to Python",
    description="Learn Python basics",
    text_content="Python is a high-level programming language...",
    keywords=["python", "programming", "tutorial"]
)

# Create from video with subtitles
video_idea = IdeaInspiration.from_video(
    title="Python Tutorial",
    description="Video tutorial",
    subtitle_text="Welcome to this tutorial...",
    keywords=["python", "video", "tutorial"]
)

# Create from audio with transcription
audio_idea = IdeaInspiration.from_audio(
    title="Python Podcast",
    description="Episode 1",
    transcription="Today we discuss Python...",
    keywords=["python", "podcast"]
)
```

## Usage Examples

### Basic Creation

```python
from idea_inspiration import IdeaInspiration, ContentType

# Manual creation
idea = IdeaInspiration(
    title="My Article",
    description="Article description",
    content="Full article text",
    keywords=["article", "example"],
    source_type=ContentType.TEXT,
    metadata={"author": "John Doe", "publish_date": "2025-01-15"},
    source_id="article-123",
    source_url="https://example.com/article"
)
```

### Serialization

```python
from idea_inspiration import IdeaInspiration

# Create an idea
idea = IdeaInspiration.from_text(
    title="Test Article",
    text_content="Article content",
    keywords=["test"]
)

# Convert to dictionary
data = idea.to_dict()

# Create from dictionary
restored = IdeaInspiration.from_dict(data)
assert restored.title == idea.title
```

### Scoring and Category Fields

The model supports scoring and categorization fields for content evaluation:

```python
from idea_inspiration import IdeaInspiration

# Create with scoring and category information
idea = IdeaInspiration.from_text(
    title="True Crime Documentary",
    text_content="A gripping investigation into...",
    keywords=["true crime", "mystery", "thriller"],
    score=85,
    category="true_crime",
    subcategory_relevance={
        "true_crime": 92,
        "psychological_thriller": 81,
        "mystery": 88
    }
)
```

## Blending Multiple IdeaInspiration Objects

Multiple `IdeaInspiration` instances can be blended together to create new `Idea` objects. See the main documentation for blending strategies:

1. **Topic-based blending** - Combine ideas around a theme
2. **Trend-based blending** - Mix trending content
3. **Multi-platform blending** - Combine cross-platform content
4. **Temporal blending** - Mix content from different time periods

## Data Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | Content title or headline |
| `description` | `str` | Brief description or summary |
| `content` | `str` | Main text content |
| `keywords` | `List[str]` | Relevant keywords or tags |
| `source_type` | `ContentType` | Type of content source |
| `metadata` | `Dict[str, str]` | Additional metadata |
| `source_id` | `Optional[str]` | Source platform identifier |
| `source_url` | `Optional[str]` | URL to original content |
| `score` | `Optional[float]` | Content quality score |
| `category` | `Optional[str]` | Primary category |
| `subcategory_relevance` | `Optional[Dict]` | Subcategory scores |

## ContentType Enum

```python
class ContentType(Enum):
    TEXT = "text"       # Text-based content
    VIDEO = "video"     # Video with subtitles
    AUDIO = "audio"     # Audio with transcription
    UNKNOWN = "unknown" # Unknown type
```

## Factory Methods

- `from_text()` - Create from text content
- `from_video()` - Create from video with subtitles
- `from_audio()` - Create from audio with transcription
- `from_dict()` - Create from dictionary

## Integration

The `IdeaInspiration` model is used by:
- **[Classification Module](../../Classification/)** - Content categorization
- **[Scoring Module](../../Scoring/)** - Content scoring
- **[Sources Module](../../Sources/)** - Content source integrations
- **PrismQ.Idea.Model** - Content generation (M:N relationship)

## Support

For questions or issues, see the GitHub repository.
