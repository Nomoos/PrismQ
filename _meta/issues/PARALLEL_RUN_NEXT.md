# PARALLEL_RUN_NEXT - Parallel Execution Commands

> **Purpose**: Groups of commands for parallel implementation of workflow steps.  
> **Completed Work**: `_meta/issues/done/` | **Full Roadmap**: `PARALLEL_RUN_NEXT_FULL.md`

**Updated**: 2025-11-28 | **Sprint**: 4 - Integration Phase

---

## 🚀 PARALLEL GROUP 1: Integration (Run Together)

> INT-001 and INT-002 can run in parallel. Complete these first.

```bash
# === INT-001: State-Database Integration ===
# Worker: Any | Effort: 1 day
cd /home/runner/work/PrismQ/PrismQ
git checkout -b int-001-state-db-integration
# Create: T/Integration/state_persistence.py
# - Connect state machine to database models
# - Use repository pattern for data access
# Tests: T/Integration/_meta/tests/test_state_persistence.py

# === INT-002: Migration Script ===
# Worker: Any | Effort: 1 day
cd /home/runner/work/PrismQ/PrismQ
git checkout -b int-002-migration
# Create: T/Database/migrations/001_initial_schema.py
# - Migrate existing data to new schema
# - Idempotent migration (can run multiple times safely)
# Tests: T/Database/_meta/tests/test_migration.py
```

---

## 🚀 PARALLEL GROUP 2: Enhancements (Run Together, Independent)

> POST-001, POST-003, POST-005 can run in parallel. Independent of Group 1.

```bash
# === POST-001: SEO Keywords ===
# Worker: Worker17 + Worker13 | Effort: 2 days
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-001-seo-keywords
# Create: T/Publishing/SEO/Keywords/
# Spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md

# === POST-003: Blog Format ===
# Worker: Worker12 | Effort: 2 days
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-003-blog-format
# Create: T/Script/Formatter/Blog/
# Spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md

# === POST-005: Batch Processing ===
# Worker: Worker02 | Effort: 2 days
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-005-batch-processing
# Create: T/Idea/Batch/
# Spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md
```

---

## 📋 PARALLELIZATION OVERVIEW

| Group | Issues | Can Run With | Status |
|-------|--------|--------------|--------|
| **Group 1** | INT-001, INT-002 | Each other | 🆕 UNBLOCKED |
| **Group 2** | POST-001, POST-003, POST-005 | Each other + Group 1 | 🆕 Ready |

```
Parallel Execution:
┌─────────────────────────────────────────────────────────┐
│ Group 1: INT-001 ──────────────────────┐               │
│          INT-002 ──────────────────────┘ (parallel)    │
├─────────────────────────────────────────────────────────┤
│ Group 2: POST-001 ─────────────────────┐               │
│          POST-003 ─────────────────────┤ (parallel)    │
│          POST-005 ─────────────────────┘               │
└─────────────────────────────────────────────────────────┘
Groups 1 and 2 can also run in parallel (independent)
```

---

## 🎉 COMPLETED WORK

- MVP-001 through MVP-024 ✅
- STATE-001, STATE-002, STATE-003 ✅
- DB-001 through DB-005 ✅ (175 tests passing)

See `_meta/issues/done/` for details.
