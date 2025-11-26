# PrismQ.Review.Model

Core data models for content reviews in the PrismQ ecosystem.

## Overview

This module provides models for storing and managing content reviews:

- **Review**: Simple review content (text, score)
- **StoryReview**: Linking table for Story reviews with review types

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from review import Review
from story_review import StoryReview, ReviewType

# Create a simple review
review = Review(
    text="Great title! Clear and engaging.",
    score=85
)

# Create a story review link
story_review = StoryReview(
    story_id=1,
    review_id=5,
    version=2,
    review_type=ReviewType.GRAMMAR
)
```

## Models

### Review

Simple review content without relationship tracking.

```python
@dataclass
class Review:
    text: str
    score: Optional[int]  # 0-100
    id: Optional[int]
    created_at: datetime
```

**Relationships**:
- Title/Script have direct FK to Review (1:1 per version)
- Story uses StoryReview linking table (many reviews per story)

### StoryReview

Linking table for Story reviews.

```python
@dataclass
class StoryReview:
    story_id: int
    review_id: int
    version: int  # >= 0 (UINT simulation)
    review_type: ReviewType
    id: Optional[int]
    created_at: datetime
```

**Review Types**:
- `grammar`: Grammar and spelling review
- `tone`: Tone and voice consistency
- `content`: Content quality and accuracy
- `consistency`: Internal consistency check
- `editing`: Editorial improvements

## Database Schema

```sql
-- Review: Simple review content
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)

-- StoryReview: Linking table for Story reviews
StoryReview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL REFERENCES Story(id),
    review_id INTEGER NOT NULL REFERENCES Review(id),
    version INTEGER NOT NULL CHECK (version >= 0),
    review_type TEXT NOT NULL CHECK (review_type IN ('grammar', 'tone', 'content', 'consistency', 'editing')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version, review_type)
)
```

## Related

- **[T/_meta/docs/DATABASE_DESIGN.md](../../_meta/docs/DATABASE_DESIGN.md)**: Full database schema
- **[T/Idea/Model](../Idea/Model)**: Idea model reference
