# PrismQ.T Database Design Document

This document outlines the database design decisions, model structures, and implementation plan for the PrismQ Text Generation Pipeline.

## Table of Contents
- [Design Decisions](#design-decisions)
- [Chosen Approach: Hybrid Model](#chosen-approach-hybrid-model)
- [Database Schema](#database-schema)
- [Process State Machine](#process-state-machine)
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
| **Current Version Access** | Implicit via `ORDER BY version DESC LIMIT 1` query on indexed INTEGER column |
| **Full History** | Separate version tables preserve complete history |
| **Query Simplicity** | Simple queries without maintaining redundant FK columns |
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

### Core Tables (5 Tables)

```sql
-- Idea: Simple prompt-based idea data (Story references Idea via FK in Story.idea_id)
-- Text field contains prompt-like content for content generation
-- Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
Idea (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,                                      -- Prompt-like text describing the idea
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),  -- Version tracking (UINT simulation)
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)

-- Main Story table with state (next process name) and idea_id FK
-- State is stored as a string following the pattern: PrismQ.T.<Output>.From.<Input1>.<Input2>...
-- Note: current_title_version_id and current_script_version_id are removed
-- Current versions are now implicit - determined by highest version integer
-- in Title/Script tables via ORDER BY version DESC LIMIT 1
Story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER FK NULL REFERENCES Idea(id),  -- Reference to Idea
    state TEXT NOT NULL DEFAULT 'PrismQ.T.Idea.From.User',  -- Next process name
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (idea_id) REFERENCES Idea(id)
)

-- Title versions with full history
-- Each title version directly references its review (if any)
-- Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
Title (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER FK NOT NULL REFERENCES Story(id),
    version INTEGER NOT NULL CHECK (version >= 0),  -- Version tracking (UINT simulation)
    text TEXT NOT NULL,
    review_id INTEGER FK NULL REFERENCES Review(id),  -- Direct FK to review
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version)
)

-- Script/Text versions with full history
-- Each script version directly references its review (if any)
-- Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
Script (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER FK NOT NULL REFERENCES Story(id),
    version INTEGER NOT NULL CHECK (version >= 0),  -- Version tracking (UINT simulation)
    text TEXT NOT NULL,
    review_id INTEGER FK NULL REFERENCES Review(id),  -- Direct FK to review
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version)
)

-- Review: Simple review content without version tracking
-- Title/Script reference Review directly via FK
-- Story references Review via StoryReview linking table
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)

-- StoryReview: Linking table for Story reviews (many-to-many)
-- Allows one Story to have multiple reviews with different types
-- Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
-- UNIQUE(story_id, version, review_type) prevents duplicate reviews of same type for same version
StoryReview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER FK NOT NULL REFERENCES Story(id),
    review_id INTEGER FK NOT NULL REFERENCES Review(id),
    version INTEGER NOT NULL CHECK (version >= 0),    -- Story version being reviewed (UINT simulation)
    review_type TEXT NOT NULL CHECK (review_type IN ('grammar', 'tone', 'content', 'consistency', 'editing')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version, review_type)
)
```

### Entity Relationship

```
┌──────────┐         ┌──────────┐
│   Idea   │◄────FK──│  Story   │
└──────────┘         └────┬─────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────┐
│    Title     │  │    Script    │  │ StoryReview │
│  review_id───┼──┼──review_id───┼──┼──►┌────────┐│
└──────────────┘  └──────────────┘  │   │ Review ││
                                    │   └────────┘│
                                    └─────────────┘
```

### Review Relationship Types

| Content Type | Review Relationship | Multiple Reviews? |
|--------------|---------------------|-------------------|
| Title | Direct FK (`title.review_id → review.id`) | No (1:1 per version) |
| Script | Direct FK (`script.review_id → review.id`) | No (1:1 per version) |
| Story | Linking table (`StoryReview`) | Yes (many reviews per story) |

### StoryReview Types (for Story-level reviews)

| review_type | Description |
|-------------|-------------|
| `grammar` | Grammar and spelling review |
| `tone` | Tone and voice consistency |
| `content` | Content quality and accuracy |
| `consistency` | Internal consistency check |
| `editing` | Editorial improvements |

### Design Benefits

1. **Title/Script**: Direct FK relationship is simple and efficient
2. **Story**: Linking table allows multiple reviews with different types (grammar, tone, etc.)
3. **Clean Review table**: Review only contains review content, no relationship tracking
4. **Extensible**: New review types can be added to StoryReview without schema changes

---

## Process State Machine

The `Story.state` field stores the **next process name** to be executed, following the naming convention:

```
PrismQ.T.<Output>.From.<Input1>.<Input2>...
```

Where:
- `<Output>` = The entity being created/modified
- `From` = Indicates input sources follow
- `<Input1>.<Input2>...` = Input dependencies that create the output

### Workflow State Diagram

```
                    ┌─────────────────────────────────────────────┐
                    │   PrismQ.T.Idea.From.User (Initial)          │
                    └───────────────────┬─────────────────────────┘
                                        │ create_idea
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │ PrismQ.T.Title.From.Idea                    │
                    └───────────────────┬─────────────────────────┘
                                        │ generate_title
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │ PrismQ.T.Content.From.Idea.Title             │
                    └───────────────────┬─────────────────────────┘
                                        │ generate_script
                                        ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │ PrismQ.T.Content.From.Title.Review.Script               │◄──┐
                    └───────────────────┬─────────────────────────────────────┘   │ (unlimited)
                                        │                                          │
                                        └──────────────────────────────────────────┘
                                        │ export
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │    PrismQ.T.Publishing                      │
                    └─────────────────────────────────────────────┘
```

### Process State Values
| State | Description | Next Action |
|-------|-------------|-------------|
| `PrismQ.T.Idea.From.User` | Initial state, awaiting idea creation | Create idea |
| `PrismQ.T.Title.From.Idea` | Idea created, awaiting title | Generate title from idea |
| `PrismQ.T.Content.From.Idea.Title` | Title generated, awaiting script | Generate script from idea + title |
| `PrismQ.T.Review.Title.From.Script` | Generate title review from script | Review title |
| `PrismQ.T.Review.Script.From.Title` | Generate script review from title | Review script |
| `PrismQ.T.Title.From.Script.Review.Title` | Iterate title using review | Create new title version |
| `PrismQ.T.Content.From.Title.Review.Script` | Script iteration (unlimited) | Continue iterating or export |
| `PrismQ.T.Publishing` | Content exported, ready for publishing | Complete |

### Batch Script to Process State Mapping
| Batch Script | State After Execution |
|--------------|----------------------|
| `step1_create_idea.bat` | `PrismQ.T.Title.From.Idea` |
| `step2_generate_title.bat` | `PrismQ.T.Content.From.Idea.Title` |
| `step3_generate_script.bat` | `PrismQ.T.Content.From.Title.Review.Script` |
| `step4_iterate_script.bat` | `PrismQ.T.Content.From.Title.Review.Script` |
| `step5_export.bat` | `PrismQ.T.Publishing` |

### Persistence Between Processes

When running steps as separate processes (via batch scripts), the state is preserved in the `Story.state` field. Each batch script:
1. Loads current state from database
2. Validates allowed transitions
3. Performs the action
4. Updates status and saves

---

## Implementation Plan

### Phase 1: Core Models
- [x] Create `Idea` model with simplified schema (PR #138)
- [x] Create `Story` model with state machine and implicit version tracking (PR #139)
- [ ] Create `Title` model
- [ ] Create `Script` model
- [x] Create `Review` model with discriminator and single reviewed_version field

### Phase 2: Relationships & Constraints
- [x] Set up foreign key relationships (Story → Idea FK)
- [x] Add CHECK constraints for Review types (review_type IN ('title', 'script', 'story'))
- [ ] Create indexes for common queries
- [ ] ~~Add database triggers for `updated_at`~~ (Not needed - timestamps immutable after creation)

### Phase 3: State Machine Integration
- [x] Implement state transition logic
- [ ] Add validation for allowed transitions
- [x] Integrate with batch script workflow
- [x] ~~Update `text_client_state.json` to use database~~ (Now using SQLite: `text_client_state.db`)

### Phase 4: Migration & Testing
- [ ] Create database migration scripts
- [x] Write unit tests for models (SimpleIdea tests added in PR #138)
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
CREATE INDEX idx_title_story ON Title(story_id, version DESC);
CREATE INDEX idx_script_story ON Script(story_id, version DESC);
CREATE INDEX idx_review_story ON Review(story_id, review_type);
```

#### 4. Connection Pooling
For SQLite (S3DB - SQLite):
- Use `sqlite3` with `check_same_thread=False` for multi-process access
- Consider WAL mode for better concurrency: `PRAGMA journal_mode=WAL;`

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

**Note**: Story → Idea FK relationship is now implemented in the Core Tables section.

### Implemented: Simple Idea Model

The Idea model has been simplified to a prompt-based structure:

```sql
-- IMPLEMENTED: Simple Idea model for prompt-based storage
Idea (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,                                      -- Prompt-like text describing the idea
    version INTEGER NOT NULL DEFAULT 1,             -- Version tracking for iterations
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

This simplified schema stores idea content as prompt-like text, enabling:
- Direct storage of structured prompts using templates (horror_story, mystery_story, etc.)
- Version tracking via `create_new_version()` method
- Flexible prompt text format for various content types

### Future: Inspiration Sources

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
-- Empty when Idea created via Idea.From.User
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
| `Idea.From.User` | None (empty) | `COUNT(idea_inspirations WHERE idea_id = ?) = 0` |
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
| `<role>_<type>` | `reviewed_version` | Role-specific field with discriminator |
| `current_<table>_id` | `current_title_version_id` | Current/active reference (deprecated - use implicit lookup) |

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
  - [ ] Issue created for Title model
  - [ ] Issue created for Script model
  - [ ] Issue created for Review model
  - [ ] Issue created for Idea model
  - [ ] Issue created for IdeaInspiration model
  - [ ] Issue created for idea_inspirations junction table
  - [ ] All issues linked to this design document
  - [ ] Issues include approach, pros/cons from this doc

### Model Implementation Issues

1. **Create Story Model** ✅ IMPLEMENTED (PR #139)
   - Implement base Story model with state machine
   - Add status transitions and validation
   - Implicit version tracking via `ORDER BY version DESC LIMIT 1`
   - Add `idea_id` FK reference (nullable)

2. **Create Title Model**
   - Version tracking for titles
   - Link to Story via `story_id` FK
   - Unique constraint on (story_id, version)

3. **Create Script Model**
   - Version tracking for scripts
   - Link to Story via `story_id` FK
   - Unique constraint on (story_id, version)

4. **Create Review Model** ✅ IMPLEMENTED
   - Discriminator pattern for review types (`title`, `script`, `story`)
   - Single `reviewed_version` field (INTEGER) for universal version tracking
   - Implicit version identification: `review_type` + `reviewed_version` = target content
   - CHECK constraints for review_type validation
   - Score range validation (0-100)

5. **Create Idea Model** ✅ IMPLEMENTED (PR #138)
   - Simplified schema: `(id, text, version, created_at)`
   - Prompt-like text format for content generation
   - Version tracking via `create_new_version()` method
   - Prompt templates: `IdeaPromptTemplates` class

6. **Create IdeaInspiration Model** (Future)
   - Source material storage
   - title, source, content, notes fields
   - Timestamps and audit fields

7. **Create idea_inspirations Junction Table** (Future)
   - Many-to-many between Idea and IdeaInspiration
   - `idea_id` FK with CASCADE delete
   - `inspiration_id` FK with CASCADE delete
   - Unique constraint on (idea_id, inspiration_id)
   - Note: Empty = Idea.From.User, populated = Idea.Fusion

---

*Last Updated: 2025-11-26*
*Part of PrismQ Content Production Platform*
