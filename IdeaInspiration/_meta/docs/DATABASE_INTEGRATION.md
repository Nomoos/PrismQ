# Database Integration Architecture

## Overview

The PrismQ.IdeaInspiration ecosystem uses a **dual-save architecture** for database persistence. This design allows each Source module to maintain detailed domain-specific data while also contributing to a unified central database for cross-source queries.

## Architecture Principles

This architecture follows several key SOLID principles:

### Single Responsibility Principle (SRP)
- Each table has one clear purpose:
  - `lyric_snippets` - Stores lyric-specific data (pageviews, genius metadata)
  - `signals` - Stores signal-specific data (temporal trends, velocity)
  - `events` - Stores event-specific data (dates, recurrence patterns)
  - `IdeaInspiration` - Stores normalized content for unified access

### Open/Closed Principle (OCP)
- The central IdeaInspiration model is open for extension (new sources can add to it)
- But closed for modification (adding new sources doesn't change existing structure)

### Interface Segregation Principle (ISP)
- Each source has minimal, focused interfaces for their specific domain
- Sources aren't forced to conform to a single rigid interface

## Dual-Save Pattern

### Concept

Each Source module implements a dual-save pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    Source Module                         │
│                  (e.g., LyricSnippets)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │   Plugin scrapes│
                 │  and returns    │
                 │ IdeaInspiration │
                 └─────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
┌──────────────────────┐        ┌──────────────────────┐
│ Source-Specific DB   │        │   Central Database   │
│  (lyric_snippets)    │        │  (IdeaInspiration)   │
│                      │        │                      │
│ Detailed domain data │        │ Normalized content   │
│ - pageviews          │        │ - title              │
│ - score_dictionary   │        │ - description        │
│ - tags               │        │ - content            │
│ - processed flag     │        │ - keywords           │
└──────────────────────┘        │ - metadata           │
                                │ - source_type        │
                                └──────────────────────┘
```

### Benefits

1. **Domain-Specific Data Preservation**: Each source maintains its unique fields
2. **Unified Access**: All sources can be queried together via IdeaInspiration table
3. **Backward Compatibility**: Existing source-specific queries still work
4. **Analytics**: Cross-source analysis becomes possible
5. **Flexibility**: Sources can evolve independently

## Implementation Guide

### For Source Modules

Here's how to implement dual-save in a Source module:

#### Step 1: Import Central Database Utilities

```python
# In your CLI file (e.g., src/cli.py)
import sys
from pathlib import Path

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path
```

#### Step 2: Initialize Both Databases

```python
# Initialize databases (source-specific AND central)
db = Database(config.database_path, interactive=not no_interactive)
central_db_path = get_central_database_path()
central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
```

#### Step 3: Implement Dual-Save Logic

```python
total_saved_source = 0
total_saved_central = 0

for idea in ideas:  # ideas are IdeaInspiration objects
    # Save to source-specific database
    source_saved = db.insert_resource(
        source='your_source',
        source_id=idea.source_id,
        title=idea.title,
        # ... other source-specific fields
    )
    
    if source_saved:
        total_saved_source += 1
    
    # Save to central IdeaInspiration database (DUAL-SAVE)
    central_saved = central_db.insert(idea)
    if central_saved:
        total_saved_central += 1
```

#### Step 4: Report Both Save Counts

```python
click.echo(f"\nScraping complete!")
click.echo(f"Total items found: {total_scraped}")
click.echo(f"Saved to source database: {total_saved_source}")
click.echo(f"Saved to central database: {total_saved_central}")
click.echo(f"Source database: {config.database_path}")
click.echo(f"Central database: {central_db_path}")
```

### Examples by Source Type

#### Creative Sources (e.g., LyricSnippets)

Creative sources already return `IdeaInspiration` objects:

```python
# Plugin returns List[IdeaInspiration]
ideas = genius_plugin.scrape(search_query=search_query)

for idea in ideas:
    # Source-specific save
    db.insert_resource(
        source='genius',
        source_id=idea.source_id,
        title=idea.title,
        content=idea.content,
        tags=','.join(idea.keywords),
        score=creative_metrics.inspiration_value,
        score_dictionary=json.dumps(creative_metrics.to_dict())
    )
    
    # Central save
    central_db.insert(idea)
```

#### Signal Sources (e.g., GoogleTrends)

Signal sources also return `IdeaInspiration` objects:

```python
# Plugin returns List[IdeaInspiration]
ideas = trends_plugin.scrape(keywords=keyword_list)

for idea in ideas:
    # Extract signal-specific data from metadata
    signal_type = idea.metadata.get('signal_type', 'trend')
    temporal = idea.metadata.get('temporal', {})
    
    # Source-specific save
    db.insert_signal(
        source='google_trends',
        source_id=idea.source_id,
        signal_type=signal_type,
        name=idea.title,
        description=idea.description,
        tags=','.join(idea.keywords),
        metrics=idea.metadata.get('metrics', {}),
        temporal=temporal,
        universal_metrics=universal_metrics.to_dict()
    )
    
    # Central save
    central_db.insert(idea)
```

#### Event Sources (e.g., CalendarHolidays)

Event sources may return dictionaries - convert to IdeaInspiration:

```python
# Plugin returns List[Dict]
holidays_data = holidays_plugin.scrape(country=country_code, year=year_val)

for holiday_data in holidays_data:
    # Process to event format
    event_signal = EventProcessor.process_holiday(holiday_data)
    
    # Source-specific save
    db.insert_event(
        source=event_signal['source'],
        source_id=event_signal['source_id'],
        name=event_signal['event']['name'],
        # ... other event fields
    )
    
    # Convert to IdeaInspiration for central save
    idea = IdeaInspiration.from_text(
        title=event_signal['event']['name'],
        description=f"{event_signal['event']['type']} event in {country_code}",
        keywords=[event_signal['event']['type'], country_code, 'holiday'],
        metadata={
            'event_type': event_signal['event']['type'],
            'date': event_signal['event']['date'],
            **event_signal['metadata']
        },
        source_id=event_signal['source_id'],
        source_created_at=event_signal['event']['date'],
        category='event'
    )
    
    # Central save
    central_db.insert(idea)
```

## Central Database Schema

The central `IdeaInspiration` table includes:

```sql
CREATE TABLE IdeaInspiration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core content fields
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,
    keywords TEXT,  -- JSON array
    
    -- Source tracking
    source_type TEXT,  -- 'text', 'video', 'audio'
    source_id TEXT,
    source_url TEXT,
    source_created_by TEXT,
    source_created_at TEXT,
    
    -- Metadata
    metadata TEXT,  -- JSON object for source-specific data
    
    -- Scoring and classification
    score INTEGER,
    category TEXT,
    subcategory_relevance TEXT,  -- JSON object
    contextual_category_scores TEXT,  -- JSON object
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_source_id ON IdeaInspiration(source_id);
CREATE INDEX idx_source_type ON IdeaInspiration(source_type);
CREATE INDEX idx_category ON IdeaInspiration(category);
```

## Querying Across Sources

The central database enables unified queries:

```python
from idea_inspiration_db import IdeaInspirationDatabase

db = IdeaInspirationDatabase("db.s3db")

# Get all ideas from the last week
recent_ideas = db.get_all(limit=100)

# Filter by category
tech_ideas = db.get_all(category="technology")

# Filter by source type
text_ideas = db.get_all(source_type="text")
video_ideas = db.get_all(source_type="video")

# Count by category
tech_count = db.count(category="technology")
```

## Metadata Strategy

Each source type uses the `metadata` field differently:

### Creative Sources
```python
metadata = {
    'song_id': '12345',
    'artist_id': '678',
    'artist_name': 'Artist Name',
    'pageviews': '1000000',
    'language': 'en'
}
```

### Signal Sources
```python
metadata = {
    'signal_type': 'trend',
    'temporal': {
        'peak_date': '2025-01-15',
        'velocity': 0.85
    },
    'metrics': {
        'search_volume': 1000000,
        'growth_rate': 0.45
    }
}
```

### Event Sources
```python
metadata = {
    'event_type': 'holiday',
    'date': '2025-12-25',
    'country': 'US',
    'scope': 'national',
    'importance': 'major'
}
```

## Migration Guide

To migrate an existing Source module to use dual-save:

1. **Add imports** for central database utilities
2. **Initialize central database** alongside source database
3. **Ensure plugins return IdeaInspiration** (or convert dictionaries)
4. **Add dual-save logic** after source-specific save
5. **Update CLI output** to report both save counts
6. **Test** that both databases receive data

## Testing

Test both saves independently:

```python
def test_dual_save():
    # Setup
    source_db = Database("test_source.db")
    central_db = IdeaInspirationDatabase("test_central.db")
    
    # Create test idea
    idea = IdeaInspiration.from_text(
        title="Test",
        text_content="Content",
        source_id="test-123"
    )
    
    # Test source save
    source_saved = source_db.insert_resource(
        source='test',
        source_id=idea.source_id,
        title=idea.title,
        content=idea.content
    )
    assert source_saved
    
    # Test central save
    central_saved = central_db.insert(idea)
    assert central_saved is not None
    
    # Verify both
    assert source_db.count_by_source('test') == 1
    assert central_db.count() == 1
```

## Performance Considerations

### Batch Operations

For bulk imports, use batch operations:

```python
# Collect all ideas first
ideas = []
for item in large_dataset:
    idea = convert_to_idea(item)
    ideas.append(idea)

# Batch save to central database
inserted_count = central_db.insert_batch(ideas)
```

### Database Location

Both databases should use the same working directory:

```python
# Source-specific database
config.database_path  # e.g., /path/to/working/lyric_snippets.db

# Central database
get_central_database_path()  # e.g., /path/to/working/db.s3db
```

## Troubleshooting

### Import Errors

If you get import errors for `idea_inspiration_db`:

```python
# Verify the path calculation
model_path = Path(__file__).resolve().parents[6] / 'Model'
print(f"Model path: {model_path}")
print(f"Exists: {model_path.exists()}")
```

For Event sources (one less parent level):
```python
model_path = Path(__file__).resolve().parents[5] / 'Model'
```

### Duplicate Records

The central database doesn't enforce `UNIQUE` constraints by design. If you need to prevent duplicates:

```python
# Check before inserting
existing = central_db.get_by_source_id(idea.source_id)
if not existing:
    central_db.insert(idea)
```

### Metadata Serialization

Ensure metadata is a dictionary with string values:

```python
metadata = {
    'views': str(views),  # Convert numbers to strings
    'date': date.isoformat(),  # Use ISO format for dates
    'active': str(is_active)  # Convert booleans to strings
}
```

## Future Enhancements

Potential improvements to the dual-save architecture:

1. **Automatic Sync**: Background process to sync source DBs to central DB
2. **Conflict Resolution**: Handle updates when source data changes
3. **Deduplication**: Smart detection of duplicate content across sources
4. **Versioning**: Track changes to IdeaInspiration records over time
5. **Analytics**: Built-in cross-source analytics queries

## Summary

The dual-save architecture provides:
- ✅ Domain-specific data preservation
- ✅ Unified cross-source access
- ✅ SOLID principle compliance
- ✅ Backward compatibility
- ✅ Flexibility for future enhancements

By implementing this pattern consistently across all Source modules, the PrismQ ecosystem maintains both specialized functionality and unified access to all idea inspirations.
