# Database Guide

Complete guide for database operations with PrismQ.Idea.Model.

## Setup

### Quick Setup

Run the appropriate script for your platform:

**Linux/macOS:**
```bash
./setup_db.sh
```

**Windows PowerShell:**
```powershell
.\setup_db.ps1
```

**Windows Command Prompt:**
```cmd
setup_db.bat
```

This creates `idea.db` with proper schema and indexes.

## Database Schema

### Tables

**`ideas`** - Stores all Idea instances (30 columns)
**`idea_inspirations`** - Junction table for M:N relationships

### Key Indexes

- `idx_ideas_status` - Filter by workflow status
- `idx_ideas_genre` - Filter by content genre
- `idx_idea_inspirations_idea` - Lookup inspirations for an idea
- `idx_idea_inspirations_inspiration` - Lookup ideas from an inspiration

## Basic Operations

### Connect and Initialize

```python
from idea_db import IdeaDatabase

db = IdeaDatabase("idea.db")
db.connect()

# First time only
db.create_tables()
```

### Insert Idea

```python
from idea import Idea, ContentGenre

idea = Idea(
    title="My First Idea",
    concept="A great concept",
    target_platforms=["youtube"],
    target_formats=["video"],
    genre=ContentGenre.EDUCATIONAL
)

# Save to database
idea_id = db.insert_idea(idea.to_dict())
print(f"Saved with ID: {idea_id}")
```

### Retrieve Idea

```python
# By ID
idea_dict = db.get_idea(idea_id)
idea = Idea.from_dict(idea_dict)

print(f"Title: {idea.title}")
print(f"Status: {idea.status}")
```

### Update Idea

```python
# Create new version
updated = idea.create_new_version(
    concept="Updated concept",
    status="validated"
)

# Update in database
db.update_idea(idea_id, updated.to_dict())
```

### Delete Idea

```python
# Delete idea and all relationships
db.delete_idea(idea_id)
```

### Close Connection

```python
db.close()
```

## Query Operations

### By Status

```python
# Get all draft ideas
drafts = db.get_ideas_by_status("draft")

for idea_dict in drafts:
    idea = Idea.from_dict(idea_dict)
    print(f"- {idea.title}")
```

### By Genre

```python
# Get all educational ideas
educational = db.get_ideas_by_genre("educational")

print(f"Found {len(educational)} educational ideas")
```

### By Inspiration

```python
# Find all ideas derived from specific inspiration
ideas = db.get_ideas_from_inspiration("insp-001")

print(f"Found {len(ideas)} ideas from inspiration insp-001")
```

### All Ideas

```python
# Get all ideas (use with caution on large databases)
cursor = db.conn.cursor()
cursor.execute("SELECT id FROM ideas")
all_ids = [row[0] for row in cursor.fetchall()]

for idea_id in all_ids:
    idea_dict = db.get_idea(idea_id)
    print(f"- {idea_dict['title']}")
```

## Relationship Management

### Link Idea to Inspirations

Relationships are automatically created when using `from_inspirations()`:

```python
# Create idea from inspirations
idea = Idea.from_inspirations(
    inspirations=[insp1, insp2, insp3],
    title="Fused Concept",
    concept="Combined from sources",
    target_platforms=["youtube"],
    target_formats=["video"],
    genre=ContentGenre.DOCUMENTARY
)

# Save - relationships stored automatically
idea_id = db.insert_idea(idea.to_dict())

# Links are in inspiration_ids field
print(idea.inspiration_ids)  # ['insp-1', 'insp-2', 'insp-3']
```

### Query Relationships

```python
# Find all ideas from a specific inspiration
related_ideas = db.get_ideas_from_inspiration("insp-123")

print(f"Ideas derived from insp-123:")
for idea_dict in related_ideas:
    print(f"  - {idea_dict['title']}")
```

### Manual Relationship (Advanced)

If you need to add relationships manually:

```python
# After inserting idea
cursor = db.conn.cursor()
cursor.execute("""
    INSERT INTO idea_inspirations (idea_id, inspiration_id)
    VALUES (?, ?)
""", (idea_id, "insp-456"))
db.conn.commit()
```

## Advanced Queries

### Custom SQL Queries

```python
cursor = db.conn.cursor()

# Count ideas by status
cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM ideas
    GROUP BY status
    ORDER BY count DESC
""")

for row in cursor.fetchall():
    print(f"{row['status']}: {row['count']}")
```

### Ideas by Platform

```python
# Note: target_platforms is stored as JSON string
cursor.execute("""
    SELECT id, title, target_platforms
    FROM ideas
    WHERE target_platforms LIKE ?
""", ('%youtube%',))

for row in cursor.fetchall():
    print(f"- {row['title']}")
```

### Recent Ideas

```python
# Get 10 most recent ideas
cursor.execute("""
    SELECT id, title, created_at
    FROM ideas
    ORDER BY created_at DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row['created_at']}: {row['title']}")
```

### Ideas Ready for Production

```python
# Find approved ideas not yet in production
cursor.execute("""
    SELECT id, title, genre
    FROM ideas
    WHERE status = 'approved'
    ORDER BY created_at ASC
""")

print("Ready for production:")
for row in cursor.fetchall():
    print(f"  - [{row['genre']}] {row['title']}")
```

## Data Types and JSON

### JSON Fields

Several fields are stored as JSON strings:
- `target_platforms` - List of platforms
- `target_formats` - List of formats
- `target_demographics` - Demographics dict
- `potential_scores` - Scores dict
- `keywords` - List of keywords
- `themes` - List of themes
- `metadata` - Custom metadata dict

These are automatically serialized/deserialized by `to_dict()` and `from_dict()`.

### Working with JSON

```python
import json

# Query JSON fields
cursor.execute("SELECT keywords FROM ideas WHERE id = ?", (idea_id,))
keywords_json = cursor.fetchone()['keywords']
keywords = json.loads(keywords_json)

print(f"Keywords: {', '.join(keywords)}")
```

## Backup and Migration

### Backup Database

```bash
# Simple copy
cp idea.db idea_backup_$(date +%Y%m%d).db

# SQLite backup
sqlite3 idea.db ".backup idea_backup.db"
```

### Export to JSON

```python
import json

db = IdeaDatabase("idea.db")
db.connect()

# Get all ideas
cursor = db.conn.cursor()
cursor.execute("SELECT id FROM ideas")
all_ideas = [db.get_idea(row[0]) for row in cursor.fetchall()]

# Export
with open("ideas_export.json", "w") as f:
    json.dump(all_ideas, f, indent=2)

db.close()
```

### Import from JSON

```python
import json

with open("ideas_export.json", "r") as f:
    ideas = json.load(f)

db = IdeaDatabase("idea.db")
db.connect()

for idea_dict in ideas:
    # Create Idea object to validate
    idea = Idea.from_dict(idea_dict)
    db.insert_idea(idea.to_dict())

db.close()
```

## Best Practices

### 1. Always Close Connections

```python
# Use try-finally
db = IdeaDatabase("idea.db")
try:
    db.connect()
    # ... operations ...
finally:
    db.close()
```

### 2. Use Transactions for Multiple Operations

```python
db.connect()
try:
    # Multiple inserts
    for idea in ideas:
        db.insert_idea(idea.to_dict())
    db.conn.commit()
except Exception as e:
    db.conn.rollback()
    print(f"Error: {e}")
finally:
    db.close()
```

### 3. Version Instead of Update

```python
# Don't modify existing idea
# Instead, create new version
v2 = idea.create_new_version(concept="New concept")
db.insert_idea(v2.to_dict())  # New row, version = 2
```

### 4. Track Creators

```python
idea = Idea(
    title="New Idea",
    concept="Concept",
    created_by="user@example.com",  # Always set this
    target_platforms=["youtube"],
    target_formats=["video"],
    genre=ContentGenre.EDUCATIONAL
)
```

### 5. Use Indexes Effectively

Filter by indexed fields for better performance:
```python
# Fast (uses index)
db.get_ideas_by_status("draft")
db.get_ideas_by_genre("educational")

# Slower (no index on title)
cursor.execute("SELECT * FROM ideas WHERE title LIKE ?", ('%tutorial%',))
```

## Troubleshooting

### Database Locked

**Problem:** `sqlite3.OperationalError: database is locked`

**Solutions:**
- Close all connections: `db.close()`
- Only one write at a time
- Use WAL mode: `db.conn.execute("PRAGMA journal_mode=WAL")`

### JSON Parsing Errors

**Problem:** `json.JSONDecodeError`

**Solutions:**
- Ensure valid JSON: use `json.dumps()` before storing
- Check for escape sequences
- Validate with `json.loads()` after retrieval

### Foreign Key Violations

**Problem:** Error when deleting idea

**Solution:** CASCADE is enabled, but ensure no circular references

## See Also

- **[Quick Start](QUICK_START.md)** - Get started quickly
- **[Fields Reference](FIELDS.md)** - Field documentation
- Setup scripts: `setup_db.sh`, `setup_db.ps1`, `setup_db.bat`
