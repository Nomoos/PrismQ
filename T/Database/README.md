# PrismQ Database Models

Database models for PrismQ content workflow following SOLID principles.

> **📚 For comprehensive database documentation including all models and schemas, see the [Database Objects Documentation](../../_meta/docs/DATABASE.md).**

## Principles

- **Interface Segregation**: Small, focused `IModel` interface with essential CRUD methods
- **Dependency Inversion**: Models depend on `IModel` abstraction, not concrete database
- **Single Responsibility**: Each model handles one entity

## Models

### Title

Versioned title content with optional review reference.

**Fields:**
- `id`: Primary key (auto-generated)
- `story_id`: FK to Story
- `version`: Title version number (>= 0, UINT simulation)
- `text`: Title text content
- `review_id`: FK to Review (optional, 1:1 per version)
- `created_at`: Timestamp of creation

**Constraints:**
- `UNIQUE(story_id, version)` - prevents duplicate versions
- `version >= 0` - simulates unsigned integer

**Usage:**
```python
from T.Database.models.title import Title

# Create new title
title = Title(
    story_id=1,
    version=0,
    text="10 Tips for Better Python Code"
)

# With review reference
title_v1 = Title(
    story_id=1,
    version=1,
    text="Improved Title",
    review_id=5  # FK to Review table
)

# Convert to/from dictionary
data = title.to_dict()
title_copy = Title.from_dict(data)
```

## Database Schema

```sql
Title (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),
    text TEXT NOT NULL,
    review_id INTEGER NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version),
    FOREIGN KEY (story_id) REFERENCES Story(id),
    FOREIGN KEY (review_id) REFERENCES Review(id)
)
```

## Related Issues

- **DB-001**: Create Base Model Interface (IModel)
- **DB-002**: Implement Title Model (this module)
- **DB-003**: Implement Script Model
- **DB-004**: Implement Review Model
- **DB-005**: Implement StoryReview Linking Table

## Related Documentation

- **[Database Objects Documentation](../../_meta/docs/DATABASE.md)** - Comprehensive database reference
- **[Repository Pattern](./_meta/docs/REPOSITORY_PATTERN.md)** - Repository pattern guide

## Testing

```bash
pytest T/Database/_meta/tests/ -v
```
