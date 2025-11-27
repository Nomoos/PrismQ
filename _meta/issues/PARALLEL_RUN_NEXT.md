# PARALLEL_RUN_NEXT - Active Sprint Execution

> **Purpose**: This document tracks **ONLY** Work In Progress (WIP) and unblocked issues that can run in parallel.  
> **Completed Work**: See `_meta/issues/done/` for completed issues (MVP-001 through MVP-024 ✅)  
> **Full Roadmap**: See `PARALLEL_RUN_NEXT_FULL.md` for complete Post-MVP roadmap (POST-001 through POST-048)  
> **Post-MVP Issues**: See `T/_meta/issues/new/POST-MVP-Enhancements/` for detailed Text Pipeline issue specifications  
> **Story Generation**: See `_meta/issues/new/STORY_GENERATION_PLAN.md` for Story workflow implementation (STORY-001 to STORY-020)

**Date**: 2025-11-27 (Updated)  
**Current Sprint**: Sprint 4 - State Refactoring + Database Models  
**Status**: 🎯 Group 2 (Database) COMPLETED  
**Timeline**: Weeks 9-10 (2 weeks)

---

## 🚀 COMMANDS FOR WORKERS - START HERE

### Parallel Group 1: State Refactoring (HIGH PRIORITY - RUN FIRST)
> All issues in this group can run in parallel. Complete before Group 2.

```bash
# === STATE-001: Define State Interface (Single Responsibility) ===
# Worker: Any
cd /home/runner/work/PrismQ/PrismQ
git checkout -b state-001-state-interface
# Create: T/State/interfaces/state_interface.py
# - Define IState interface with single responsibility
# - Methods: get_name(), get_next_states(), can_transition_to()
# Tests: T/State/_meta/tests/test_state_interface.py

# === STATE-002: Create State Constants Module (Open/Closed) ===
# Worker: Any (parallel with STATE-001)
cd /home/runner/work/PrismQ/PrismQ
git checkout -b state-002-state-constants
# Create: T/State/constants/state_names.py
# - Define all state name constants following pattern: PrismQ.T.<Output>.From.<Input>
# - Extensible for new states without modifying existing code
# Tests: T/State/_meta/tests/test_state_constants.py

# === STATE-003: Create State Transition Validator (Liskov Substitution) ===
# Worker: Any (parallel with STATE-001, STATE-002)
cd /home/runner/work/PrismQ/PrismQ
git checkout -b state-003-transition-validator
# Create: T/State/validators/transition_validator.py
# - Validate state transitions
# - All validators interchangeable via IValidator interface
# Tests: T/State/_meta/tests/test_transition_validator.py
```

### Parallel Group 2: Database Models ✅ COMPLETED
> All issues in this group have been completed and verified with passing tests.

**Status**: All 5 issues completed (175 tests passing)

| Issue | Status | File | Tests |
|-------|--------|------|-------|
| DB-001: Base Model Interface | ✅ Done | `T/Database/models/base.py` | `test_base_model.py` |
| DB-002: Title Model | ✅ Done | `T/Database/models/title.py` | `test_title_model.py` |
| DB-003: Script Model | ✅ Done | `T/Database/models/script.py` | `test_script_model.py` |
| DB-004: Review Model | ✅ Done | `T/Database/models/review.py` | `test_review_model.py` |
| DB-005: StoryReview Linking Table | ✅ Done | `T/Database/models/story_review.py` | `test_story_review_model.py` |

### Parallel Group 3: Integration (After Group 2)
> Integrate state and database layers. Requires Group 2 complete.

```bash
# === INT-001: State-Database Integration ===
# Worker: Any
cd /home/runner/work/PrismQ/PrismQ
git checkout -b int-001-state-db-integration
# Create: T/Integration/state_persistence.py
# - Connect state machine to database models
# - Use repository pattern for data access
# Tests: T/Integration/_meta/tests/test_state_persistence.py

# === INT-002: Migration Script ===
# Worker: Any (parallel with INT-001)
cd /home/runner/work/PrismQ/PrismQ
git checkout -b int-002-migration
# Create: T/Database/migrations/001_initial_schema.py
# - Migrate existing data to new schema
# - Idempotent migration (can run multiple times safely)
# Tests: T/Database/_meta/tests/test_migration.py
```

### Parallel Group 4: Enhancement Issues (After Group 3 OR Independent)
> These can run in parallel with each other. Some independent of Groups 1-3.

```bash
# === POST-001: SEO Keywords (Independent) ===
# Worker: Worker17 + Worker13
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-001-seo-keywords
# Create: T/Publishing/SEO/Keywords/
# Follow spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md

# === POST-003: Blog Format (Independent) ===
# Worker: Worker12
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-003-blog-format
# Create: T/Script/Formatter/Blog/
# Follow spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md

# === POST-005: Batch Processing (Independent) ===
# Worker: Worker02
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-005-batch-processing
# Create: T/Idea/Batch/
# Follow spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md
```

---

## 📋 PARALLEL GROUPS OVERVIEW

| Group | Issues | Status | Depends On | SOLID Principle |
|-------|--------|--------|------------|-----------------|
| **Group 1** | STATE-001, STATE-002, STATE-003 | ✅ All 3 parallel | None | S, O, L |
| **Group 2** | DB-001, DB-002, DB-003, DB-004, DB-005 | ✅ **COMPLETED** | Group 1 | I, D, S |
| **Group 3** | INT-001, INT-002 | 🆕 UNBLOCKED | Group 2 | D |
| **Group 4** | POST-001, POST-003, POST-005 | ✅ All 3 parallel | None (Independent) | - |

### Execution Timeline
```
Week 1:
├─ Day 1-2: Group 1 (STATE-001, STATE-002, STATE-003) [PARALLEL]
├─ Day 2-4: Group 2 (DB-001, DB-002, DB-003, DB-004, DB-005) [PARALLEL]
└─ Day 1-4: Group 4 (POST-001, POST-003, POST-005) [PARALLEL, Independent]

Week 2:
├─ Day 5-6: Group 3 (INT-001, INT-002) [PARALLEL]
├─ Day 6-8: POST-002, POST-004, POST-006 [After POST-001, POST-003]
└─ Day 7-10: Testing, Documentation, Review
```

---

## 🔥 PRIORITY 1: State Refactoring Issues

### STATE-001: Define State Interface
**Priority**: 🔴 CRITICAL | **Effort**: 0.5 day | **Status**: 🆕 UNBLOCKED  
**SOLID**: Single Responsibility Principle

**Acceptance Criteria**:
- [ ] Create `IState` interface in `T/State/interfaces/state_interface.py`
- [ ] Interface has single responsibility: define state behavior contract
- [ ] Methods: `get_name() -> str`, `get_next_states() -> List[str]`, `can_transition_to(state: str) -> bool`
- [ ] Unit tests with 100% coverage

**File Structure**:
```
T/State/
├── __init__.py
├── interfaces/
│   ├── __init__.py
│   └── state_interface.py      # IState interface
└── _meta/
    └── tests/
        └── test_state_interface.py
```

---

### STATE-002: Create State Constants Module
**Priority**: 🔴 CRITICAL | **Effort**: 0.5 day | **Status**: 🆕 UNBLOCKED  
**SOLID**: Open/Closed Principle (extensible without modification)

**Acceptance Criteria**:
- [ ] Create `T/State/constants/state_names.py`
- [ ] Define all state constants following pattern: `PrismQ.T.<Output>.From.<Input>`
- [ ] States are extensible - new states can be added without modifying existing code
- [ ] Unit tests verify all state names follow convention

**State Names to Define**:
```python
IDEA_CREATION = "PrismQ.T.Idea.Creation"
TITLE_FROM_IDEA = "PrismQ.T.Title.From.Idea"
SCRIPT_FROM_IDEA_TITLE = "PrismQ.T.Script.From.Idea.Title"
REVIEW_TITLE_FROM_SCRIPT = "PrismQ.T.Review.Title.From.Script"
REVIEW_SCRIPT_FROM_TITLE = "PrismQ.T.Review.Script.From.Title"
TITLE_FROM_SCRIPT_REVIEW = "PrismQ.T.Title.From.Script.Review.Title"
SCRIPT_FROM_TITLE_REVIEW = "PrismQ.T.Script.From.Title.Review.Script"
PUBLISHING = "PrismQ.T.Publishing"
```

---

### STATE-003: Create State Transition Validator
**Priority**: 🔴 CRITICAL | **Effort**: 1 day | **Status**: 🆕 UNBLOCKED  
**SOLID**: Liskov Substitution Principle (validators interchangeable)

**Acceptance Criteria**:
- [ ] Create `IValidator` interface in `T/State/interfaces/validator_interface.py`
- [ ] Create `TransitionValidator` implementing `IValidator`
- [ ] Validates state transitions against allowed transition map
- [ ] All validators can be substituted without affecting correctness
- [ ] Unit tests cover all valid/invalid transitions

**Transition Map**:
```python
TRANSITIONS = {
    IDEA_CREATION: [TITLE_FROM_IDEA],
    TITLE_FROM_IDEA: [SCRIPT_FROM_IDEA_TITLE],
    SCRIPT_FROM_IDEA_TITLE: [REVIEW_SCRIPT_FROM_TITLE, PUBLISHING],
    REVIEW_SCRIPT_FROM_TITLE: [SCRIPT_FROM_TITLE_REVIEW],
    SCRIPT_FROM_TITLE_REVIEW: [REVIEW_SCRIPT_FROM_TITLE, PUBLISHING],
    # ... etc
}
```

---

## ✅ PRIORITY 2: Database Model Issues - COMPLETED

> **Status**: All 5 database model issues completed and verified (175 tests passing)  
> **Completed**: 2025-11-27

### DB-001: Create Base Model Interface ✅
**Priority**: 🟠 HIGH | **Effort**: 0.5 day | **Status**: ✅ COMPLETED  
**SOLID**: Interface Segregation Principle (small, focused interface)  
**File**: `T/Database/models/base.py` | **Tests**: `T/Database/_meta/tests/test_base_model.py`

**Acceptance Criteria**:
- [x] Created `IReadable` and `IModel` interfaces in `T/Database/models/base.py`
- [x] Small interface: `get_id()`, `exists()`, `get_created_at()`, `save()`, `refresh()`
- [x] No fat interface - only essential persistence operations
- [x] INSERT+READ only architecture (no update/delete - immutable data)

---

### DB-002: Implement Title Model ✅
**Priority**: 🟠 HIGH | **Effort**: 1 day | **Status**: ✅ COMPLETED  
**SOLID**: Dependency Inversion Principle (depend on IModel, not SQLite)  
**File**: `T/Database/models/title.py` | **Tests**: `T/Database/_meta/tests/test_title_model.py`

**Acceptance Criteria**:
- [x] Created `Title` dataclass implementing `IModel` interface
- [x] Fields: `id`, `story_id`, `version` (INTEGER >= 0), `text`, `review_id` (FK), `created_at`
- [x] Version validation (must be >= 0)
- [x] `to_dict()`/`from_dict()` for serialization
- [x] `create_next_version()` for versioning support

---

### DB-003: Implement Script Model ✅
**Priority**: 🟠 HIGH | **Effort**: 1 day | **Status**: ✅ COMPLETED  
**SOLID**: Dependency Inversion Principle  
**File**: `T/Database/models/script.py` | **Tests**: `T/Database/_meta/tests/test_script_model.py`

**Acceptance Criteria**:
- [x] Created `Script` dataclass implementing `IModel` interface
- [x] Fields: `id`, `story_id`, `version` (INTEGER >= 0), `text`, `review_id` (FK), `created_at`
- [x] Version validation (must be >= 0)
- [x] Same structure as Title for consistency
- [x] `create_next_version()` for versioning support

---

### DB-004: Implement Review Model ✅
**Priority**: 🟠 HIGH | **Effort**: 1 day | **Status**: ✅ COMPLETED  
**SOLID**: Single Responsibility (only review data, no business logic)  
**File**: `T/Database/models/review.py` | **Tests**: `T/Database/_meta/tests/test_review_model.py`

**Acceptance Criteria**:
- [x] Created `Review` dataclass implementing `IModel` interface
- [x] Simple content storage: `id`, `text`, `score`, `created_at`
- [x] Score validation (0-100 integer range)
- [x] No relationship tracking - Title/Script reference Review via FK

---

### DB-005: Implement StoryReview Linking Table ✅
**Priority**: 🟠 HIGH | **Effort**: 0.5 day | **Status**: ✅ COMPLETED  
**SOLID**: Single Responsibility (only linking Story to Reviews)  
**File**: `T/Database/models/story_review.py` | **Tests**: `T/Database/_meta/tests/test_story_review_model.py`

**Acceptance Criteria**:
- [x] Created `StoryReviewModel` dataclass implementing `IModel` interface
- [x] Fields: `id`, `story_id`, `review_id`, `version` (INTEGER >= 0), `review_type`, `created_at`
- [x] `ReviewType` enum: grammar, tone, content, consistency, editing
- [x] `get_sql_schema()` generates CREATE TABLE with all constraints

---

## 📊 State Naming Convention Reference

All process states follow the pattern: `PrismQ.T.<Output>.From.<Input1>.<Input2>...`

| State | Description |
|-------|-------------|
| `PrismQ.T.Idea.Creation` | Creating initial idea |
| `PrismQ.T.Title.From.Idea` | Creating title from idea |
| `PrismQ.T.Script.From.Idea.Title` | Creating script from idea + title |
| `PrismQ.T.Title.From.Script.Review.Title` | Iterating title using review |
| `PrismQ.T.Script.From.Title.Review.Script` | Iterating script using review |
| `PrismQ.T.Publishing` | Publishing completed content |

---

## 📊 DATABASE SCHEMA REFERENCE

**SQLite State Schema** (version uses INTEGER with CHECK >= 0 to simulate UINT):
```sql
-- Idea: Simple prompt-based idea data (Story references Idea via FK in Story.idea_id)
Idea (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,                                      -- Prompt-like text describing the idea
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),  -- UINT simulation
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)

-- Story: Main table with state (next process name) and idea_id FK
Story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NULL,
    state TEXT NOT NULL DEFAULT 'PrismQ.T.Idea.Creation',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (idea_id) REFERENCES Idea(id)
)

-- Review: Simple review content (no relationship tracking)
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)

-- Title versions with direct review FK
Title (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),  -- UINT simulation
    text TEXT NOT NULL,
    review_id INTEGER NULL,                         -- Direct FK to Review
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version),
    FOREIGN KEY (story_id) REFERENCES Story(id),
    FOREIGN KEY (review_id) REFERENCES Review(id)
)

-- Script versions with direct review FK
Script (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),  -- UINT simulation
    text TEXT NOT NULL,
    review_id INTEGER NULL,                         -- Direct FK to Review
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(story_id, version),
    FOREIGN KEY (story_id) REFERENCES Story(id),
    FOREIGN KEY (review_id) REFERENCES Review(id)
)

-- StoryReview: Linking table for Story reviews (many-to-many)
-- Allows one Story to have multiple reviews with different types
-- UNIQUE(story_id, version, review_type) prevents duplicate reviews of same type for same version
StoryReview (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    story_id INTEGER NOT NULL,
    review_id INTEGER NOT NULL,
    version INTEGER NOT NULL CHECK (version >= 0),  -- UINT simulation
    review_type TEXT NOT NULL CHECK (review_type IN ('grammar', 'tone', 'content', 'consistency', 'editing')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (story_id) REFERENCES Story(id),
    FOREIGN KEY (review_id) REFERENCES Review(id),
    UNIQUE(story_id, version, review_type)
)
```

### Review Relationships

| Content Type | Review Relationship | Multiple Reviews? |
|--------------|---------------------|-------------------|
| Title | Direct FK (`title.review_id`) | No (1:1 per version) |
| Script | Direct FK (`script.review_id`) | No (1:1 per version) |
| Story | Linking table (`StoryReview`) | Yes (many per story) |

**Version Lookup**: Use `ORDER BY version DESC LIMIT 1` to get current version.

See [T/_meta/docs/DATABASE_DESIGN.md](../../../T/_meta/docs/DATABASE_DESIGN.md) for full schema.

---

## 🎉 COMPLETED WORK

**MVP Status**: ✅ ALL COMPLETE (MVP-001 through MVP-024)  
**Location**: `_meta/issues/done/`

---

## 📈 PROGRESS TRACKING

### Current Sprint Progress
| Group | Issues | Status |
|-------|--------|--------|
| Group 1 (State) | STATE-001, STATE-002, STATE-003 | ✅ COMPLETED |
| Group 2 (Database) | DB-001, DB-002, DB-003, DB-004, DB-005 | ✅ COMPLETED (175 tests passing) |
| Group 3 (Integration) | INT-001, INT-002 | 🆕 UNBLOCKED |
| Group 4 (Enhancement) | POST-001, POST-003, POST-005 | 🆕 Ready (Independent) |

### Quality Gates
- [x] All new code has >80% test coverage
- [x] Unit tests pass for new features (175 tests)
- [ ] Integration tests pass for new features
- [x] Documentation updated
- [ ] Code review completed
- [ ] No security vulnerabilities introduced

---

## 📚 RELATED DOCUMENTS

| Document | Location | Purpose |
|----------|----------|---------|
| Database Design | `T/_meta/docs/DATABASE_DESIGN.md` | Full schema documentation |
| POST Issues | `T/_meta/issues/new/POST-MVP-Enhancements/` | Enhancement specifications |
| Story Generation | `_meta/issues/new/STORY_GENERATION_PLAN.md` | Story workflow (STORY-001 to STORY-020) |
| Full Roadmap | `_meta/issues/PARALLEL_RUN_NEXT_FULL.md` | All 48 POST issues |
| Completed MVPs | `_meta/issues/done/MVP-*.md` | Issues 001-024 |

---

**Status**: Sprint 4 - State Refactoring COMPLETED, Database Models COMPLETED, Integration UNBLOCKED  
**Priority Order**: Group 1 (State) ✅ → Group 2 (Database) ✅ → Group 3 (Integration) 🆕  
**Independent**: Group 4 (Enhancement) can run in parallel with any group  
**Updated**: 2025-11-27  
**Owner**: Worker01 (Project Manager)
