# PrismQ Database Objects Documentation

**Document Type**: Technical Reference  
**Scope**: Database Architecture  
**Last Updated**: 2025-12-01

## Overview

PrismQ uses SQLite for data persistence following a dual-pattern architecture:

| Pattern | Tables | Operations | Use Case |
|---------|--------|------------|----------|
| **INSERT+READ Only** | Title, Script, Review, StoryReview | Insert, Read | Immutable versioned content |
| **Full CRUD** | Story | Create, Read, Update | State machine transitions |

## Database Location

The database file is stored in the PrismQ working directory:
- **Windows**: `C:\PrismQ\db.s3db`
- **Unix-like**: `~/PrismQ/db.s3db`

## Database Models

All database models are located in the **[T/Database/](../../T/Database/)** module.

### Story

**File**: `T/Database/models/story.py`

The central entity in PrismQ that ties together Ideas, Titles, Scripts, and Reviews.

```sql
Story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_json TEXT NULL,
    title_id INTEGER NULL,
    script_id INTEGER NULL,
    state TEXT NOT NULL DEFAULT 'CREATED',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (title_id) REFERENCES Title(id),
    FOREIGN KEY (script_id) REFERENCES Script(id)
)

-- Performance indexes
CREATE INDEX idx_story_state ON Story(state);
CREATE INDEX idx_story_title_id ON Story(title_id);
CREATE INDEX idx_story_script_id ON Story(script_id);
```

**Fields:**
- `id`: Primary key (auto-generated)
- `idea_json`: Serialized Idea data (JSON string)
- `title_id`: FK to latest Title version (optional)
- `script_id`: FK to latest Script version (optional)
- `state`: Current workflow state (module-based state name)
- `created_at`: Creation timestamp
- `updated_at`: Last state change timestamp

**States:** States represent the processing module and follow the pattern `PrismQ.T.<Module>.From.<Input>` or `PrismQ.T.<Action>.<Target>`. Valid states include:
- `PrismQ.T.Idea.Creation` - Initial idea creation
- `PrismQ.T.Title.From.Idea` - Title generation from idea
- `PrismQ.T.Script.From.Idea.Title` - Script generation from idea and title
- `PrismQ.T.Review.Title.ByScriptAndIdea` - Title review using script and idea
- `PrismQ.T.Title.From.Title.Review.Script` - Title refinement from review
- `PrismQ.T.Script.From.Script.Review.Title` - Script refinement from review
- `PrismQ.T.Review.Script.Grammar` - Grammar review
- `PrismQ.T.Story.Review` - Expert story review
- `PrismQ.T.Story.Polish` - Story polishing
- `PrismQ.T.Publishing` - Publishing (terminal state)

See `T/State/constants/state_names.py` for the complete list of states.

---

### Title

**File**: `T/Database/models/title.py`

Versioned title content with optional review reference.

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

-- Performance indexes
CREATE INDEX idx_title_story_id ON Title(story_id);
CREATE INDEX idx_title_story_version ON Title(story_id, version);
```

**Fields:**
- `id`: Primary key (auto-generated)
- `story_id`: FK to Story
- `version`: Title version number (>= 0)
- `text`: Title text content
- `review_id`: FK to Review (optional, 1:1 per version)
- `created_at`: Timestamp of creation

**Constraints:**
- `UNIQUE(story_id, version)` - prevents duplicate versions
- `version >= 0` - simulates unsigned integer

---

### Script

**File**: `T/Database/models/script.py`

Versioned script content with optional review reference.

```sql
Script (
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

-- Performance indexes
CREATE INDEX idx_script_story_id ON Script(story_id);
CREATE INDEX idx_script_story_version ON Script(story_id, version);
```

**Fields:**
- `id`: Primary key (auto-generated)
- `story_id`: FK to Story
- `version`: Script version number (>= 0)
- `text`: Script content text
- `review_id`: FK to Review (optional)
- `created_at`: Timestamp of creation

---

### Review

**File**: `T/Database/models/review.py`

Review content with score for evaluating Title/Script content.

```sql
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

**Fields:**
- `id`: Primary key (auto-generated)
- `text`: Review text content
- `score`: Integer score (0 to 100)
- `created_at`: Timestamp of creation

---

### StoryReview

**File**: `T/Database/models/story_review.py`

Linking table for Story-Review relationships with review type categorization.

```sql
StoryReview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    review_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),
    review_type TEXT NOT NULL CHECK (review_type IN 
        ('grammar', 'tone', 'content', 'consistency', 'editing')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES Story(id),
    FOREIGN KEY (review_id) REFERENCES Review(id),
    UNIQUE(story_id, version, review_type)
)

-- Performance indexes
CREATE INDEX idx_storyreview_story_id ON StoryReview(story_id);
CREATE INDEX idx_storyreview_review_id ON StoryReview(review_id);
CREATE INDEX idx_storyreview_story_version ON StoryReview(story_id, version);
```

**Fields:**
- `id`: Primary key (auto-generated)
- `story_id`: FK to Story
- `review_id`: FK to Review
- `version`: Story version being reviewed (>= 0)
- `review_type`: Type of review (`grammar`, `tone`, `content`, `consistency`, `editing`)
- `created_at`: Timestamp of creation

**Review Types:**
- `grammar`: Grammar and spelling review
- `tone`: Tone and voice consistency
- `content`: Content quality and accuracy
- `consistency`: Internal consistency check
- `editing`: Editorial improvements

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                    Entity Relationship Diagram                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Idea (external)                                               │
│      │                                                          │
│      │ 1:N (one idea spawns 10 stories)                        │
│      ▼                                                          │
│   ┌─────────┐                                                   │
│   │  Story  │                                                   │
│   └────┬────┘                                                   │
│        │                                                        │
│   ┌────┴────────────────┐                                       │
│   │                     │                                       │
│   │ 1:N               1:N                                       │
│   ▼                     ▼                                       │
│ ┌───────┐           ┌────────┐                                  │
│ │ Title │           │ Script │                                  │
│ └───┬───┘           └───┬────┘                                  │
│     │                   │                                       │
│     │ N:1 (FK)          │ N:1 (FK)                              │
│     ▼                   ▼                                       │
│   ┌────────┐       ┌────────┐                                   │
│   │ Review │◄──────│ Review │                                   │
│   └────────┘       └────────┘                                   │
│                         ▲                                       │
│                         │                                       │
│                         │ N:1 (FK)                              │
│   ┌─────────┐           │                                       │
│   │  Story  │───────────┘                                       │
│   └────┬────┘                                                   │
│        │                                                        │
│        │ N:M (via StoryReview)                                  │
│        ▼                                                        │
│   ┌─────────────┐                                               │
│   │ StoryReview │                                               │
│   └─────────────┘                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Repository Pattern

PrismQ uses the Repository Pattern to separate domain models from data access logic.

### Base Interfaces

**File**: `T/Database/models/base.py`

- **IReadable**: Read-only operations (get_id, exists, get_created_at)
- **IModel**: Full persistence operations (extends IReadable with save, refresh)

### Repository Interfaces

**File**: `T/Database/repositories/base.py`

- **IRepository**: Base interface with find_by_id, find_all, exists, insert
- **IVersionedRepository**: Extended for versioned entities (Title, Script) with find_latest_version, find_versions
- **IUpdatableRepository**: Extended for updatable entities (Story) with update method

### Concrete Repositories

| Repository | Entity | Location |
|------------|--------|----------|
| TitleRepository | Title | `T/Database/repositories/title_repository.py` |
| ScriptRepository | Script | `T/Database/repositories/script_repository.py` |
| StoryRepository | Story | `T/Database/repositories/story_repository.py` |
| StoryReviewRepository | StoryReview | `T/Database/repositories/story_review_repository.py` |

### Version Query Methods

All repositories that handle versioned entities provide consistent methods for querying the current (latest) version:

**TitleRepository & ScriptRepository:**
- `find_latest_version(story_id)` - Returns the entity with the highest version number (using `ORDER BY version DESC LIMIT 1`)
- `get_current_title(story_id)` / `get_current_script(story_id)` - Convenience aliases for `find_latest_version()`

**StoryReviewRepository:**
- `find_latest_version(story_id)` - Returns the highest version number for a story's reviews
- `find_latest_reviews(story_id)` - Returns all reviews for the latest version
- `find_latest_review_by_type(story_id, review_type)` - Returns the latest review of a specific type
- `get_current_story_reviews(story_id)` - Convenience alias for `find_latest_reviews()`
- `get_current_story_review(story_id, review_type)` - Convenience alias for `find_latest_review_by_type()`

## Usage Examples

### Creating and Saving a Title

```python
from T.Database.models.title import Title
from T.Database.repositories.title_repository import TitleRepository

# Initialize repository with connection
repo = TitleRepository(db_connection)

# Create new title (version 0)
title = Title(story_id=1, version=0, text="10 Tips for Better Python Code")
saved_title = repo.insert(title)
print(f"Saved with ID: {saved_title.id}")

# Create next version (instead of updating)
title_v1 = saved_title.create_next_version("10 Essential Tips for Python Excellence")
repo.insert(title_v1)

# Get current (latest) title for a story
current_title = repo.get_current_title(story_id=1)
print(f"Current title: {current_title.text}")
```

### Working with Story State

```python
from T.Database.models.story import Story, StoryState
from T.Database.repositories.story_repository import StoryRepository

repo = StoryRepository(db_connection)

# Create new story
story = Story(idea_id="idea-123", state=StoryState.CREATED)
saved = repo.insert(story)

# Update state (Story is the only entity that supports UPDATE)
saved.transition_to(StoryState.TITLE_V0)
repo.update(saved)
```

### Working with Story Reviews

```python
from T.Database.models.story_review import StoryReviewModel, ReviewType
from T.Database.repositories.story_review_repository import StoryReviewRepository

repo = StoryReviewRepository(db_connection)

# Get all current reviews for a story
current_reviews = repo.get_current_story_reviews(story_id=1)

# Get the latest grammar review for a story
grammar_review = repo.get_current_story_review(story_id=1, review_type=ReviewType.GRAMMAR)
```

## Testing

Run all database tests:

```bash
pytest T/Database/_meta/tests/ -v
```

## Related Documentation

- **[T/Database/README.md](../../T/Database/README.md)** - Database module overview
- **[Repository Pattern Documentation](../../T/Database/_meta/docs/REPOSITORY_PATTERN.md)** - Detailed repository pattern guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Overall platform architecture
- **[WORKFLOW.md](../WORKFLOW.md)** - Workflow state machine documentation

---

*For questions about database design, refer to the model source files in `T/Database/models/`.*
