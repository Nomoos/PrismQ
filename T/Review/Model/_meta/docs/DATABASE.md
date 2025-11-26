# Database Guide

Complete guide for database operations with PrismQ.Review.Model.

## Database Schema

### Tables

**`reviews`** - Stores all Review instances

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-generated ID |
| text | TEXT NOT NULL | Review feedback text |
| score | INTEGER | Score 0-100 (nullable) |
| created_at | TEXT | ISO timestamp |

**`story_reviews`** - Linking table for Story ↔ Review (many-to-many)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-generated ID |
| story_id | INTEGER FK | Reference to Story |
| review_id | INTEGER FK | Reference to Review |
| version | INTEGER | Story version (>= 0) |
| review_type | TEXT | Type of review |
| created_at | TEXT | ISO timestamp |

### Constraints

- `reviews.score`: CHECK (score >= 0 AND score <= 100)
- `story_reviews.version`: CHECK (version >= 0) - UINT simulation
- `story_reviews.review_type`: CHECK IN ('grammar', 'tone', 'content', 'consistency', 'editing')
- `story_reviews`: UNIQUE(story_id, version, review_type)

## Relationships

### Title/Script → Review (Direct FK)

Each Title/Script version can have one review:

```sql
Title (
    ...
    review_id INTEGER NULL REFERENCES Review(id)
)
```

### Story → Review (Linking Table)

Each Story can have multiple reviews via StoryReview:

```sql
-- Get all reviews for a story
SELECT r.*, sr.version, sr.review_type
FROM Review r
JOIN StoryReview sr ON r.id = sr.review_id
WHERE sr.story_id = ?
ORDER BY sr.version DESC, sr.review_type;
```

## CRUD Operations

### Insert Review

```python
from review import Review

review = Review(
    text="Great content!",
    score=85
)

# Insert and get ID
cursor.execute("""
    INSERT INTO reviews (text, score, created_at)
    VALUES (?, ?, ?)
""", (review.text, review.score, review.created_at.isoformat()))
review_id = cursor.lastrowid
```

### Link Story to Review

```python
from story_review import StoryReview, ReviewType

story_review = StoryReview(
    story_id=1,
    review_id=review_id,
    version=2,
    review_type=ReviewType.GRAMMAR
)

cursor.execute("""
    INSERT INTO story_reviews (story_id, review_id, version, review_type, created_at)
    VALUES (?, ?, ?, ?, ?)
""", (story_review.story_id, story_review.review_id, story_review.version, 
      story_review.review_type.value, story_review.created_at.isoformat()))
```

### Query Reviews for Story

```python
# Get all grammar reviews for story version 2
cursor.execute("""
    SELECT r.id, r.text, r.score, sr.version, sr.review_type
    FROM reviews r
    JOIN story_reviews sr ON r.id = sr.review_id
    WHERE sr.story_id = ? AND sr.version = ? AND sr.review_type = ?
""", (story_id, 2, 'grammar'))
```

## Best Practices

1. **Version is UINT**: Always use non-negative integers for version
2. **One review type per version**: UNIQUE constraint prevents duplicates
3. **Direct FK for Title/Script**: Use direct FK, not linking table
4. **Linking table for Story**: Use StoryReview for multiple review types
