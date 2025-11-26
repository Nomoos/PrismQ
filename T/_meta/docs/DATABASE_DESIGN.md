# PrismQ.T Database Design Document

This document outlines the database design decisions, model structures, and implementation plan for the PrismQ Text Generation Pipeline.

## Table of Contents
- [Design Decisions](#design-decisions)
- [Chosen Approach: Hybrid Model](#chosen-approach-hybrid-model)
- [Database Schema](#database-schema)
- [State Machine Integration](#state-machine-integration)
- [Implementation Plan](#implementation-plan)
- [Best Practices Research](#best-practices-research)
- [Future Improvements](#future-improvements)

---

## Design Decisions

### Approach Selection
After evaluating multiple database model variants, we chose the **Hybrid Approach** combined with a **Single Table with Discriminator** pattern for reviews.

#### Why Hybrid Approach?
| Aspect | Benefit |
|--------|---------|
| **Current Version Access** | Direct FK references make accessing current versions O(1) |
| **Full History** | Separate version tables preserve complete history |
| **Query Simplicity** | Avoids complex subqueries for common operations |
| **Flexibility** | Easy to add new content types |

#### Why Single Table Discriminator for Reviews?
| Aspect | Benefit |
|--------|---------|
| **Query Simplicity** | Single table for all review types |
| **No Extra Joins** | Avoids class table inheritance joins |
| **Easy Filtering** | `review_type` ENUM makes filtering straightforward |
| **CHECK Constraints** | Enforce correct version IDs based on review type |

---

## Chosen Approach: Hybrid Model

### Core Tables

```sql
-- Main Story table with state machine status and current version references
Story (
    id UUID PRIMARY KEY,
    idea_id UUID FK NULL,              -- Reference to Idea model (future)
    status ENUM('draft', 'in_progress', 'review', 'approved', 'published') NOT NULL,
    current_title_version_id UUID FK NULL,
    current_script_version_id UUID FK NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255)
)

-- Title versions with full history
TitleVersion (
    id UUID PRIMARY KEY,
    story_id UUID FK NOT NULL REFERENCES Story(id),
    version INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    UNIQUE(story_id, version)
)

-- Script/Text versions with full history
ScriptVersion (
    id UUID PRIMARY KEY,
    story_id UUID FK NOT NULL REFERENCES Story(id),
    version INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    UNIQUE(story_id, version)
)

-- Reviews with discriminator pattern for different review types
Review (
    id UUID PRIMARY KEY,
    story_id UUID FK NOT NULL REFERENCES Story(id),
    review_type ENUM('title', 'script', 'story') NOT NULL,
    reviewed_title_version_id UUID FK NULL REFERENCES TitleVersion(id),
    reviewed_script_version_id UUID FK NULL REFERENCES ScriptVersion(id),
    feedback TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255),
    
    -- Ensure correct version IDs are set based on review_type
    CONSTRAINT review_type_check CHECK (
        (review_type = 'title' AND reviewed_title_version_id IS NOT NULL AND reviewed_script_version_id IS NULL) OR
        (review_type = 'script' AND reviewed_script_version_id IS NOT NULL AND reviewed_title_version_id IS NULL) OR
        (review_type = 'story' AND reviewed_title_version_id IS NOT NULL AND reviewed_script_version_id IS NOT NULL)
    )
)
```

### Review Types Explained

| Review Type | Description | Version IDs Set |
|-------------|-------------|-----------------|
| `title` | Reviews only the title | `reviewed_title_version_id` only |
| `script` | Reviews only the script | `reviewed_script_version_id` only |
| `story` | Reviews complete story (title + script) | Both version IDs set |

---

## State Machine Integration

The `Story.status` field implements a state machine that tracks workflow progression:

```
                    ┌─────────────┐
                    │   draft     │
                    └──────┬──────┘
                           │ create_idea
                           ▼
                    ┌─────────────┐
                    │ in_progress │◄──────┐
                    └──────┬──────┘       │
                           │ submit       │ revise
                           ▼              │
                    ┌─────────────┐       │
                    │   review    │───────┘
                    └──────┬──────┘
                           │ approve
                           ▼
                    ┌─────────────┐
                    │  approved   │
                    └──────┬──────┘
                           │ publish
                           ▼
                    ┌─────────────┐
                    │  published  │
                    └─────────────┘
```

### State Transitions
| From | To | Trigger |
|------|-----|---------|
| `draft` | `in_progress` | Content creation started |
| `in_progress` | `review` | Submit for review |
| `review` | `in_progress` | Revisions requested |
| `review` | `approved` | Review passed |
| `approved` | `published` | Final publication |

### Persistence Between Processes

When running steps as separate processes (via batch scripts), the state machine status is preserved in the `Story` table. Each batch script:
1. Loads current state from database
2. Validates allowed transitions
3. Performs the action
4. Updates status and saves

---

## Implementation Plan

### Phase 1: Core Models
- [ ] Create `Story` model with state machine
- [ ] Create `TitleVersion` model
- [ ] Create `ScriptVersion` model
- [ ] Create `Review` model with discriminator

### Phase 2: Relationships & Constraints
- [ ] Set up foreign key relationships
- [ ] Add CHECK constraints for Review types
- [ ] Create indexes for common queries
- [ ] Add database triggers for `updated_at`

### Phase 3: State Machine Integration
- [ ] Implement state transition logic
- [ ] Add validation for allowed transitions
- [ ] Integrate with batch script workflow
- [x] ~~Update `text_client_state.json` to use database~~ (Now using SQLite: `text_client_state.db`)

### Phase 4: Migration & Testing
- [ ] Create database migration scripts
- [ ] Write unit tests for models
- [ ] Write integration tests for state machine
- [ ] Performance testing for version history queries

---

## Best Practices Research

### Database Design Best Practices

#### 1. UUID vs Auto-Increment IDs
**Recommendation: UUID**
- Pros: Globally unique, no collision in distributed systems, can be generated client-side
- Cons: Larger storage, slightly slower indexes
- Use case: Better for our multi-process architecture

#### 2. Soft Delete vs Hard Delete
**Recommendation: Soft Delete for Stories**
```sql
Story (
    ...
    deleted_at TIMESTAMP NULL,
    is_deleted BOOLEAN DEFAULT FALSE
)
```
- Preserves history and audit trail
- Allows recovery of accidentally deleted content

#### 3. Indexing Strategy
```sql
-- Primary query patterns
CREATE INDEX idx_story_status ON Story(status);
CREATE INDEX idx_story_created_at ON Story(created_at);
CREATE INDEX idx_titleversion_story ON TitleVersion(story_id, version DESC);
CREATE INDEX idx_scriptversion_story ON ScriptVersion(story_id, version DESC);
CREATE INDEX idx_review_story ON Review(story_id, review_type);
```

#### 4. Connection Pooling
For SQLite (S3DB - SQLite):
- Use `sqlite3` with `check_same_thread=False` for multi-process access
- Consider WAL mode for better concurrency: `PRAGMA journal_mode=WAL;`

For PostgreSQL (future):
- Use connection pooling (e.g., `asyncpg`, `psycopg2.pool`)
- Set appropriate pool size based on concurrent processes

### SQLite (S3DB) Specific Considerations

```python
# Recommended SQLite configuration
import sqlite3

def get_connection():
    conn = sqlite3.connect(
        'prismq.db',
        check_same_thread=False,
        timeout=30.0
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn
```

---

## Future Improvements

### Story Model Enhancement: Idea Reference

```sql
-- Future: Link Story to Idea model
Story (
    id UUID PRIMARY KEY,
    idea_id UUID FK NULL REFERENCES Idea(id),  -- Added reference
    ...
)

-- Future: Idea model structure
-- Note: creation_method is inferred from idea_inspirations relation:
--   - No entries = created via Idea.Creation (from scratch)
--   - One or more entries = created via Idea.Fusion (from inspirations)
Idea (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    concept TEXT NOT NULL,
    premise TEXT,
    logline TEXT,
    hook TEXT,
    skeleton TEXT,
    emotional_arc TEXT,
    twist TEXT,
    climax TEXT,
    genre ENUM(...) NOT NULL,
    target_audience TEXT,
    status ENUM('draft', 'developed', 'approved') NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255)
)

-- IdeaInspiration: Source materials that inspired an Idea
-- Used when Idea is created via Idea.Fusion (combining multiple inspirations)
IdeaInspiration (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    source TEXT,                    -- URL, book reference, etc.
    content TEXT,                   -- The inspiring content/snippet
    notes TEXT,                     -- User notes about the inspiration
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255)
)

-- Junction table: Many-to-many relationship between Idea and IdeaInspiration
-- Following naming convention: <Parent>_<Related> or <Subject>_<Object>
-- Empty when Idea created via Idea.Creation
-- One or more entries when Idea created via Idea.Fusion
idea_inspirations (
    id UUID PRIMARY KEY,
    idea_id UUID FK NOT NULL REFERENCES Idea(id) ON DELETE CASCADE,
    inspiration_id UUID FK NOT NULL REFERENCES IdeaInspiration(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(idea_id, inspiration_id)
)
```

#### Idea Creation Methods (Inferred from Relation)
| Method | idea_inspirations Entries | How to Detect |
|--------|---------------------------|---------------|
| `Idea.Creation` | None (empty) | `COUNT(idea_inspirations WHERE idea_id = ?) = 0` |
| `Idea.Fusion` | One or more | `COUNT(idea_inspirations WHERE idea_id = ?) > 0` |

### Relationship Naming Best Practices

Following established conventions for database relation naming:

#### Junction/Join Table Naming
| Convention | Example | When to Use |
|------------|---------|-------------|
| `<parent>_<child>` | `idea_inspirations` | Standard many-to-many |
| `<subject>_<verb>_<object>` | `user_follows_user` | Self-referential or action-based |
| `<singular>_<singular>` | `story_tag` | Simple associations |

#### Foreign Key Naming
| Convention | Example | Description |
|------------|---------|-------------|
| `<table>_id` | `story_id`, `idea_id` | Standard FK reference |
| `<role>_<table>_id` | `reviewed_title_version_id` | Role-specific reference |
| `current_<table>_id` | `current_title_version_id` | Current/active reference |

#### Relationship Field Naming (ORM)
| Convention | Example | Description |
|------------|---------|-------------|
| Singular for belongs-to | `idea.story` | One-to-one or many-to-one |
| Plural for has-many | `idea.inspirations` | One-to-many or many-to-many |
| Past participle for reverse | `inspiration.ideas_inspired` | Reverse relation |

### Content Type Extensibility

For adding new content types (e.g., `Summary`, `Metadata`):

```sql
-- Option 1: Add new version table
SummaryVersion (
    id UUID PRIMARY KEY,
    story_id UUID FK NOT NULL,
    version INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(story_id, version)
)

-- Update Story table
ALTER TABLE Story ADD COLUMN current_summary_version_id UUID FK NULL;

-- Update Review ENUM
ALTER TYPE review_type ADD VALUE 'summary';
```

### Analytics & Metrics

```sql
-- Future: Track iteration metrics
StoryMetrics (
    id UUID PRIMARY KEY,
    story_id UUID FK NOT NULL,
    total_title_versions INTEGER DEFAULT 0,
    total_script_versions INTEGER DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    avg_review_score DECIMAL(5,2),
    time_to_approval INTERVAL,
    updated_at TIMESTAMP NOT NULL
)
```

---

## Related Documents

- [Text Client Scripts README](../scripts/README.md) - Interactive client documentation
- [Workflow State Machine](../../WORKFLOW_STATE_MACHINE.md) - Visual state diagram
- [Title & Script Workflow](../../TITLE_SCRIPT_WORKFLOW.md) - Complete workflow guide

---

## Issues to Create

### Planning Issue (Worker01)

**📋 Create GitHub Issues for Database Models**
- Priority: High
- Description: Create individual GitHub issues for each model based on this design document
- Acceptance Criteria:
  - [ ] Issue created for Story model
  - [ ] Issue created for TitleVersion model
  - [ ] Issue created for ScriptVersion model
  - [ ] Issue created for Review model
  - [ ] Issue created for Idea model
  - [ ] Issue created for IdeaInspiration model
  - [ ] Issue created for idea_inspirations junction table
  - [ ] All issues linked to this design document
  - [ ] Issues include approach, pros/cons from this doc

### Model Implementation Issues

1. **Create Story Model**
   - Implement base Story model with state machine
   - Add status transitions and validation
   - Include timestamps and audit fields
   - Add `idea_id` FK reference (nullable)

2. **Create TitleVersion Model**
   - Version tracking for titles
   - Link to Story via `story_id` FK
   - Unique constraint on (story_id, version)

3. **Create ScriptVersion Model**
   - Version tracking for scripts
   - Link to Story via `story_id` FK
   - Unique constraint on (story_id, version)

4. **Create Review Model**
   - Discriminator pattern for review types
   - `reviewed_title_version_id` FK (nullable)
   - `reviewed_script_version_id` FK (nullable)
   - CHECK constraints for version ID validation
   - Score range validation

5. **Create Idea Model**
   - Core idea fields from current text client
   - Link to Story for idea-to-story workflow
   - Status tracking for idea lifecycle

6. **Create IdeaInspiration Model**
   - Source material storage
   - title, source, content, notes fields
   - Timestamps and audit fields

7. **Create idea_inspirations Junction Table**
   - Many-to-many between Idea and IdeaInspiration
   - `idea_id` FK with CASCADE delete
   - `inspiration_id` FK with CASCADE delete
   - Unique constraint on (idea_id, inspiration_id)
   - Note: Empty = Idea.Creation, populated = Idea.Fusion

---

*Last Updated: 2024*
*Part of PrismQ Content Production Platform*
