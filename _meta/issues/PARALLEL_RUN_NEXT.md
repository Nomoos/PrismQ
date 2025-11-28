# PARALLEL_RUN_NEXT - Active Sprint Execution

> **Purpose**: This document tracks **ONLY** Work In Progress (WIP) and unblocked issues that can run in parallel.  
> **Completed Work**: See `_meta/issues/done/` for completed issues (MVP-001 through MVP-024 ✅, DB-001 through DB-005 ✅)  
> **Full Roadmap**: See `PARALLEL_RUN_NEXT_FULL.md` for complete Post-MVP roadmap (POST-001 through POST-048)  
> **Post-MVP Issues**: See `T/_meta/issues/new/POST-MVP-Enhancements/` for detailed Text Pipeline issue specifications  
> **Story Generation**: See `_meta/issues/new/STORY_GENERATION_PLAN.md` for Story workflow implementation (STORY-001 to STORY-020)

**Date**: 2025-11-28 (Updated)  
**Current Sprint**: Sprint 4 - Integration Phase  
**Status**: 🎯 Integration Issues UNBLOCKED  
**Timeline**: Weeks 9-10 (2 weeks)

---

## 📋 ACTIVE ISSUES (Ordered by Workflow Priority)

| Priority | Issue | Status | Effort | Depends On |
|----------|-------|--------|--------|------------|
| 1 | INT-001: State-Database Integration | 🆕 UNBLOCKED | 1 day | - |
| 2 | INT-002: Migration Script | 🆕 UNBLOCKED | 1 day | - |
| 3 | POST-001: SEO Keywords | 🆕 Ready | 2 days | Independent |
| 4 | POST-003: Blog Format | 🆕 Ready | 2 days | Independent |
| 5 | POST-005: Batch Processing | 🆕 Ready | 2 days | Independent |

---

## 🚀 COMMANDS FOR WORKERS - START HERE

### Priority 1-2: Integration Issues (HIGH PRIORITY)
> These issues integrate the completed State and Database layers.

```bash
# === INT-001: State-Database Integration ===
# Priority: 1 | Worker: Any
cd /home/runner/work/PrismQ/PrismQ
git checkout -b int-001-state-db-integration
# Create: T/Integration/state_persistence.py
# - Connect state machine to database models
# - Use repository pattern for data access
# Tests: T/Integration/_meta/tests/test_state_persistence.py

# === INT-002: Migration Script ===
# Priority: 2 | Worker: Any (parallel with INT-001)
cd /home/runner/work/PrismQ/PrismQ
git checkout -b int-002-migration
# Create: T/Database/migrations/001_initial_schema.py
# - Migrate existing data to new schema
# - Idempotent migration (can run multiple times safely)
# Tests: T/Database/_meta/tests/test_migration.py
```

### Priority 3-5: Enhancement Issues (Independent)
> These can run in parallel with Integration issues.

```bash
# === POST-001: SEO Keywords ===
# Priority: 3 | Worker: Worker17 + Worker13
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-001-seo-keywords
# Create: T/Publishing/SEO/Keywords/
# Follow spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md

# === POST-003: Blog Format ===
# Priority: 4 | Worker: Worker12
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-003-blog-format
# Create: T/Script/Formatter/Blog/
# Follow spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md

# === POST-005: Batch Processing ===
# Priority: 5 | Worker: Worker02
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-005-batch-processing
# Create: T/Idea/Batch/
# Follow spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md
```

---

## 🔥 ISSUE DETAILS

### INT-001: State-Database Integration
**Priority**: 1 | **Effort**: 1 day | **Status**: 🆕 UNBLOCKED  
**SOLID**: Dependency Inversion Principle

**Acceptance Criteria**:
- [ ] Create `T/Integration/state_persistence.py`
- [ ] Connect state machine to database models
- [ ] Use repository pattern for data access
- [ ] Unit tests with 100% coverage

---

### INT-002: Migration Script
**Priority**: 2 | **Effort**: 1 day | **Status**: 🆕 UNBLOCKED  
**SOLID**: Single Responsibility Principle

**Acceptance Criteria**:
- [ ] Create `T/Database/migrations/001_initial_schema.py`
- [ ] Migrate existing data to new schema
- [ ] Idempotent migration (can run multiple times safely)
- [ ] Unit tests verify migration correctness

---

### POST-001: SEO Keywords
**Priority**: 3 | **Effort**: 2 days | **Status**: 🆕 Ready  
**Independent**: Can run in parallel with any issue

**Acceptance Criteria**:
- [ ] Follow spec: `T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md`
- [ ] Create `T/Publishing/SEO/Keywords/`
- [ ] Unit tests with 100% coverage

---

### POST-003: Blog Format
**Priority**: 4 | **Effort**: 2 days | **Status**: 🆕 Ready  
**Independent**: Can run in parallel with any issue

**Acceptance Criteria**:
- [ ] Follow spec: `T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md`
- [ ] Create `T/Script/Formatter/Blog/`
- [ ] Unit tests with 100% coverage

---

### POST-005: Batch Processing
**Priority**: 5 | **Effort**: 2 days | **Status**: 🆕 Ready  
**Independent**: Can run in parallel with any issue

**Acceptance Criteria**:
- [ ] Follow spec: `T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md`
- [ ] Create `T/Idea/Batch/`
- [ ] Unit tests with 100% coverage

---

## 📊 State Naming Convention Reference

All process states follow the pattern: `PrismQ.T.<Output>.From.<Input1>.<Input2>...`

| State | Description |
|-------|-------------|
| `PrismQ.T.Idea.Creation` | Creating initial idea |
| `PrismQ.T.Title.From.Idea` | Creating title from idea |
| `PrismQ.T.Script.From.Title.Idea` | Creating script from title + idea |
| `PrismQ.T.Review.Title.By.Script.Idea` | Reviewing title by script |
| `PrismQ.T.Review.Script.By.Title.Idea` | Reviewing script by title |
| `PrismQ.T.Title.From.Script.Review.Title` | Iterating title using review |
| `PrismQ.T.Script.From.Title.Review.Script` | Iterating script using review |
| `PrismQ.T.Story.Review` | Expert story review |
| `PrismQ.T.Story.Polish` | Story polishing |
| `PrismQ.T.Publishing` | Publishing completed content |

---

## 📈 PROGRESS TRACKING

### Current Sprint Progress
| Issue | Status |
|-------|--------|
| INT-001: State-Database Integration | 🆕 UNBLOCKED |
| INT-002: Migration Script | 🆕 UNBLOCKED |
| POST-001: SEO Keywords | 🆕 Ready |
| POST-003: Blog Format | 🆕 Ready |
| POST-005: Batch Processing | 🆕 Ready |

### Quality Gates
- [ ] All new code has >80% test coverage
- [ ] Unit tests pass for new features
- [ ] Integration tests pass for new features
- [ ] Documentation updated
- [ ] Code review completed
- [ ] No security vulnerabilities introduced

---

## 🎉 COMPLETED WORK

**Completed Issues** (moved to `_meta/issues/done/`):
- MVP-001 through MVP-024 ✅
- STATE-001, STATE-002, STATE-003 ✅
- DB-001 through DB-005 ✅ (175 tests passing)

---

## 📚 RELATED DOCUMENTS

| Document | Location | Purpose |
|----------|----------|---------|
| Database Design | `T/_meta/docs/DATABASE_DESIGN.md` | Full schema documentation |
| POST Issues | `T/_meta/issues/new/POST-MVP-Enhancements/` | Enhancement specifications |
| Story Generation | `_meta/issues/new/STORY_GENERATION_PLAN.md` | Story workflow (STORY-001 to STORY-020) |
| Full Roadmap | `_meta/issues/PARALLEL_RUN_NEXT_FULL.md` | All 48 POST issues |
| Completed Issues | `_meta/issues/done/` | All completed issues |

---

**Status**: Sprint 4 - Integration Phase  
**Priority Order**: INT-001 → INT-002 → POST-001 → POST-003 → POST-005  
**Updated**: 2025-11-28  
**Owner**: Worker01 (Project Manager)
