# PrismQ.Idea.Model - Setup Guide

Complete guide for setting up and using the Idea Model database.

## Quick Start

### Database Setup

Choose the appropriate script for your platform:

**Linux/macOS:**
```bash
cd Idea/Model
./setup_db.sh
```

**Windows (PowerShell):**
```powershell
cd Idea\Model
.\setup_db.ps1
```

**Windows (Command Prompt):**
```cmd
cd Idea\Model
setup_db.bat
```

This creates an SQLite database file `idea.db` with the following schema:
- `ideas` table - Stores Idea instances
- `idea_inspirations` table - Junction table for M:N relationships with IdeaInspiration
- Indexes for performance optimization

## Database Schema

### Ideas Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| title | TEXT | Idea title (required) |
| concept | TEXT | Core concept (required) |
| purpose | TEXT | Purpose or goal |
| emotional_quality | TEXT | Emotional tone |
| target_audience | TEXT | Target audience description |
| target_demographics | TEXT | JSON string with demographic data |
| target_platform | TEXT | Target platform (youtube, tiktok, etc.) |
| genre | TEXT | Content genre |
| style | TEXT | Content style |
| potential_scores | TEXT | JSON string with potential scores |
| metadata | TEXT | JSON string with additional metadata |
| version | INTEGER | Version number (default: 1) |
| status | TEXT | Workflow status (default: 'draft') |
| notes | TEXT | Development notes |
| created_at | TEXT | ISO timestamp of creation |
| updated_at | TEXT | ISO timestamp of last update |
| created_by | TEXT | Creator identifier |

### Idea-Inspirations Junction Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| idea_id | INTEGER | Foreign key to ideas table |
| inspiration_id | TEXT | IdeaInspiration identifier |
| created_at | TEXT | Timestamp of relationship creation |

**Unique Constraint:** (idea_id, inspiration_id) - Prevents duplicate relationships

## Python Usage

### Basic Database Operations

```python
from src.idea_db import IdeaDatabase
from src.idea import Idea, TargetPlatform, ContentGenre

# Initialize database
db = IdeaDatabase("idea.db")
db.connect()

# Create an idea
idea = Idea(
    title="Mystery Documentary",
    concept="Exploring unsolved mysteries",
    target_platform=TargetPlatform.YOUTUBE,
    genre=ContentGenre.DOCUMENTARY,
    inspiration_ids=["insp-001", "insp-002"]
)

# Save to database
idea_id = db.insert_idea(idea.to_dict())
print(f"Saved idea with ID: {idea_id}")

# Retrieve from database
retrieved = db.get_idea(idea_id)
restored_idea = Idea.from_dict(retrieved)

# Query by status
draft_ideas = db.get_ideas_by_status("draft")

# Query by platform
youtube_ideas = db.get_ideas_by_platform("youtube")

# Find ideas from specific inspiration
related_ideas = db.get_ideas_from_inspiration("insp-001")

# Update an idea
idea_v2 = restored_idea.create_new_version(
    concept="Enhanced concept",
    status="validated"
)
db.update_idea(idea_id, idea_v2.to_dict())

# Clean up
db.close()
```

### Relationship Tracking

```python
# Create idea linked to multiple inspirations
idea = Idea.from_inspirations(
    inspirations=[inspiration1, inspiration2, inspiration3],
    title="Fused Concept",
    concept="Combined from multiple sources"
)

# Save with relationships
idea_id = db.insert_idea(idea.to_dict())

# Later, find all ideas derived from a specific inspiration
ideas = db.get_ideas_from_inspiration("insp-001")
print(f"Found {len(ideas)} ideas derived from inspiration insp-001")
```

## Database Indexes

The following indexes are created for query performance:

- `idx_ideas_status` - Filter by workflow status
- `idx_ideas_platform` - Filter by target platform
- `idx_ideas_genre` - Filter by content genre
- `idx_idea_inspirations_idea` - Fast lookup of inspirations for an idea
- `idx_idea_inspirations_inspiration` - Fast lookup of ideas from an inspiration

## Data Types

### JSON Fields

Several fields store JSON data as TEXT in SQLite:
- `target_demographics`: `{"age_range": "18-35", "regions": "US,UK"}`
- `potential_scores`: `{"platform:youtube": 85, "region:us": 90}`
- `metadata`: `{"custom_key": "custom_value"}`

These are automatically serialized/deserialized by the database layer.

## Migration from Python Objects

If you have Idea objects in memory and want to persist them:

```python
# In-memory Idea
idea = Idea(
    title="Test Idea",
    concept="Test concept",
    target_platform=TargetPlatform.YOUTUBE
)

# Convert to dict
idea_dict = idea.to_dict()

# Save to database
db = IdeaDatabase("idea.db")
db.connect()
idea_id = db.insert_idea(idea_dict)
db.close()
```

## Backup and Export

### Backup Database
```bash
# Create backup
cp idea.db idea_backup_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 idea.db ".backup idea_backup.db"
```

### Export to JSON
```python
import json
from src.idea_db import IdeaDatabase

db = IdeaDatabase("idea.db")
db.connect()

# Export all ideas
cursor = db.conn.cursor()
cursor.execute("SELECT id FROM ideas")
all_ideas = [db.get_idea(row[0]) for row in cursor.fetchall()]

with open("ideas_export.json", "w") as f:
    json.dump(all_ideas, f, indent=2)

db.close()
```

## Troubleshooting

### Database Locked Error
If you get "database is locked" errors:
- Ensure you close connections: `db.close()`
- Only one process should write at a time
- Consider using WAL mode: `PRAGMA journal_mode=WAL;`

### JSON Parsing Errors
If JSON fields fail to parse:
- Verify data is valid JSON
- Check for escape sequences
- Use `json.dumps()` to serialize before storing

### Foreign Key Violations
The junction table has CASCADE delete:
- Deleting an idea automatically removes its inspiration links
- Inspiration IDs are TEXT, not foreign keys (loosely coupled)

## Best Practices

1. **Always close connections**: Use `try-finally` or context managers
2. **Version your ideas**: Use `create_new_version()` instead of modifying
3. **Track creators**: Always set `created_by` for accountability
4. **Index usage**: Filter by status, platform, or genre for best performance
5. **Backup regularly**: Database files can be copied while not in use

## Advanced: Custom Queries

```python
# Raw SQL for complex queries
db = IdeaDatabase("idea.db")
db.connect()

cursor = db.conn.cursor()

# Find most recent ideas per platform
cursor.execute("""
    SELECT target_platform, COUNT(*) as count
    FROM ideas
    GROUP BY target_platform
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    print(f"{row['target_platform']}: {row['count']} ideas")

db.close()
```

## See Also

- [User Guide](USER_GUIDE.md) - Complete feature documentation
- [Contributing](CONTRIBUTING.md) - Development guidelines
- [Main README](../README.md) - Module overview
