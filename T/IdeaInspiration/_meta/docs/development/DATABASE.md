# Database Integration

**Last Updated**: November 2025  
**Status**: ✅ CURRENT ARCHITECTURE  
**Migration**: Completed from dual-save to single database

## Overview

PrismQ.IdeaInspiration uses a **single database architecture** where all sources save their data to a central SQLite database with platform identification via the `source_platform` field.

## Current Architecture

All source modules save data to the central `IdeaInspiration` table located at:
```
Model/data/idea_inspirations.db
```

### Key Features

1. **Single Source of Truth**: One database for all content sources
2. **Platform Identification**: `source_platform` field identifies the content source
3. **Unified Schema**: Consistent data structure across all sources
4. **Flexible Content**: JSON fields support source-specific metadata

## Database Schema

The central `IdeaInspiration` table includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `source_id` | TEXT | Unique identifier from source platform |
| `source_platform` | TEXT | Platform identifier (e.g., 'reddit', 'youtube') |
| `category` | TEXT | Primary content category |
| `subcategory` | TEXT | AI-assigned subcategory |
| `title` | TEXT | Content title |
| `content` | TEXT | Main content/description |
| `url` | TEXT | Source URL |
| `score` | REAL | Engagement/quality score (0-100) |
| `metadata` | JSON | Platform-specific additional data |
| `collected_at` | TIMESTAMP | Collection timestamp |

### Indexes

Performance-optimized indexes on:
- `source_id` - Fast lookups by source identifier
- `source_type` - Fast filtering by platform
- `category` - Fast category queries
- `collected_at` - Temporal queries

## Database Operations

### Using IdeaInspirationDatabase Class

```python
from Model.idea_inspiration_db import IdeaInspirationDatabase

# Initialize database connection
db = IdeaInspirationDatabase()

# Save a single idea
idea = IdeaInspiration(
    source_id="reddit_abc123",
    source_platform="reddit",
    category="Technology",
    title="AI Breakthrough",
    content="...",
    score=85.5
)
db.save(idea)

# Query by platform
reddit_ideas = db.get_by_source_type("reddit")

# Query by category
tech_ideas = db.get_by_category("Technology")

# Update an idea
idea.score = 90.0
db.update(idea)

# Delete an idea
db.delete(idea.id)
```

### Batch Operations

```python
# Save multiple ideas efficiently
ideas = [idea1, idea2, idea3, ...]
db.batch_save(ideas)

# Query with filters
filtered_ideas = db.query(
    source_type="youtube",
    category="Entertainment",
    min_score=70.0
)
```

## Migration from Dual-Save Architecture

### What Changed

**Before (Deprecated)**:
- Source modules saved to both source-specific tables AND central table
- Multiple database files per source type
- Complex dual-save logic in each source

**After (Current)**:
- All sources save only to central database
- Single database file for entire system
- Platform identified by `source_platform` field
- Simpler, more maintainable code

### Migration Timeline

- **October 31, 2025**: Migration started
- **November 1, 2025**: Migration completed
- **Status**: All 24 source modules migrated successfully

### For Developers

If you're working with old code that references dual-save:
1. Remove source-specific database saves
2. Use only `IdeaInspirationDatabase.save()` for central database
3. Set `source_platform` field to identify the source
4. Store source-specific metadata in the `metadata` JSON field

## Testing

### Running Database Tests

```bash
cd Model
pytest tests/test_idea_inspiration_db.py -v
```

### Test Coverage

The database module has comprehensive test coverage:
- CRUD operations (Create, Read, Update, Delete)
- Batch operations
- Query filtering
- JSON serialization
- Index performance
- Error handling

## Best Practices

### 1. Use Context Managers

```python
with IdeaInspirationDatabase() as db:
    db.save(idea)
    # Connection automatically closed
```

### 2. Batch Operations for Performance

```python
# Good: Batch save
db.batch_save([idea1, idea2, idea3])

# Avoid: Multiple single saves in a loop
for idea in ideas:
    db.save(idea)  # Slower
```

### 3. Proper Error Handling

```python
try:
    db.save(idea)
except DatabaseError as e:
    logger.error(f"Failed to save idea: {e}")
    # Handle error appropriately
```

### 4. Use Indexes for Queries

```python
# Fast: Uses index
db.get_by_source_type("reddit")

# Slower: Full table scan
db.query(custom_filter=lambda x: x.source_platform == "reddit")
```

## Related Documentation

- [SINGLE_DB_IMPLEMENTATION_SUMMARY.md](../archive/migrations/SINGLE_DB_IMPLEMENTATION_SUMMARY.md) - Detailed implementation
- [SINGLE_DB_MIGRATION_GUIDE.md](../archive/migrations/SINGLE_DB_MIGRATION_GUIDE.md) - Migration guide
- [SINGLE_DB_MIGRATION_COMPLETE.md](../archive/migrations/SINGLE_DB_MIGRATION_COMPLETE.md) - Migration completion report

## Historical Documents (Archived)

The following documents describe the deprecated dual-save architecture:
- [DATABASE_INTEGRATION.md](../archive/DATABASE_INTEGRATION.md) - Old dual-save architecture
- [DATABASE_INTEGRATION_SUMMARY.md](../archive/DATABASE_INTEGRATION_SUMMARY.md) - Old implementation summary

These are kept for historical reference only.

## See Also

- [Model Module README](../../../Model/README.md) - Core data model documentation
- [Architecture Documentation](../ARCHITECTURE.md) - System-wide architecture
