# PARALLEL_RUN_NEXT - Workflow Implementation Guide

> **Purpose**: Numbered modules and commands for implementing workflow steps after `PrismQ.T.Idea.Creation`.  
> **Completed Work**: `_meta/issues/done/` | **Full Roadmap**: `PARALLEL_RUN_NEXT_FULL.md`

**Updated**: 2025-11-30 | **Sprint**: 4 - Integration Phase

---

## 📍 Current Position: After PrismQ.T.Idea.Creation

The `PrismQ.T.Idea.Creation` module is complete. Below are all numbered modules that can be implemented next, organized by workflow path and priority.

---

## 🔢 NUMBERED MODULES - Pick Your Next Implementation

### Workflow Path A: Core Pipeline (Stages 2-22)

Following the main workflow sequence from WORKFLOW_DETAILED.md:

| # | Module | Stage | Description | Effort | Dependencies |
|---|--------|-------|-------------|--------|--------------|
| **1** | `T.Title.From.Idea` | Stage 2 | Generate initial title variants from idea | 2d | Idea.Creation ✅ |
| **2** | `T.Script.FromIdeaAndTitle` | Stage 3 | Create initial script draft | 3d | #1 |
| **3** | `T.Review.Title.ByScriptIdea` | Stage 4 | Review title against script and idea | 2d | #1, #2 |
| **4** | `T.Review.Script.ByTitleIdea` | Stage 5 | Review script against title and idea | 2d | #1, #2 |
| **5** | `T.Review.Title.ByScript` | Stage 6 | Title-script alignment review | 1d | #3 |
| **6** | `T.Title.From.Script.Review.Title` | Stage 7 | Refine title from review feedback | 2d | #5 |
| **7** | `T.Script.FromOriginalScriptAndReviewAndTitle` | Stage 8 | Refine script from feedback | 2d | #5, #6 |
| **8** | `T.Review.Script.ByTitle` | Stage 9 | Final script-title review | 1d | #7 |
| **9** | `T.Review.Script.Grammar` | Stage 10 | Grammar validation | 1d | #8 |
| **10** | `T.Review.Script.Tone` | Stage 11 | Tone consistency check | 1d | #9 |
| **11** | `T.Review.Script.Content` | Stage 12 | Content accuracy validation | 1d | #10 |
| **12** | `T.Review.Script.Consistency` | Stage 13 | Style consistency check | 1d | #11 |
| **13** | `T.Review.Script.Editing` | Stage 14 | Final editing pass | 1d | #12 |
| **14** | `T.Review.Title.Readability` | Stage 15 | Title readability check | 1d | #13 |
| **15** | `T.Review.Script.Readability` | Stage 16 | Script readability check | 1d | #14 |
| **16** | `T.Story.Review` | Stage 17 | GPT expert review | 3d | #15 |
| **17** | `T.Story.Polish` | Stage 18 | GPT expert polishing | 3d | #16 |

### Workflow Path B: Integration & Infrastructure

| # | Module | Type | Description | Effort | Dependencies |
|---|--------|------|-------------|--------|--------------|
| **18** | `T.Integration.StatePersistence` | Integration | Connect state machine to database | 1d | None |
| **19** | `T.Database.Migrations` | Integration | Database migration scripts | 1d | None |
| **20** | `T.Publishing.Finalization` | Publishing | Final publication preparation | 2d | #17 |

### Workflow Path C: Enhancements (POST-MVP)

| # | Module | Sprint | Description | Effort | Dependencies |
|---|--------|--------|-------------|--------|--------------|
| **21** | `T.Publishing.SEO.Keywords` | Sprint 4 | Keyword research & optimization | 2d | None |
| **22** | `T.Script.Formatter.Blog` | Sprint 4 | Blog format optimization | 2d | None |
| **23** | `T.Idea.Batch` | Sprint 4 | Batch idea processing | 2d | None |
| **24** | `T.Title.ABTesting` | Sprint 4 | A/B testing framework | 2d | #21 |
| **25** | `T.Idea.Inspiration.YouTube` | Sprint 5 | YouTube API integration | 2d | None |
| **26** | `T.Idea.Inspiration.RSS` | Sprint 5 | RSS feed integration | 1.5d | None |
| **27** | `T.Idea.Inspiration.Twitter` | Sprint 5 | Twitter/X API integration | 1.5d | None |
| **28** | `T.Script.Versioning` | Sprint 5 | Version history & rollback | 2d | None |
| **29** | `T.Review.Collaboration` | Sprint 5 | Multi-reviewer workflow | 2d | None |
| **30** | `T.Review.Comments` | Sprint 5 | Inline comments & annotations | 2d | None |

### Workflow Path D: Story Generation (STORY-xxx)

| # | Module | Phase | Description | Effort | Dependencies |
|---|--------|-------|-------------|--------|--------------|
| **31** | GPT API Integration for Review | Phase 1 | Connect GPT for expert review | 3d | None |
| **32** | GPT API Integration for Polish | Phase 1 | Connect GPT for polishing | 3d | #31 |
| **33** | Prompt Engineering Templates | Phase 1 | Create review/polish prompts | 2d | None |
| **34** | Response Parsing & Validation | Phase 1 | Parse GPT responses | 2d | #31, #32 |
| **35** | Story Workflow Orchestrator | Phase 2 | Run Stage 21-22 loop | 3d | #31, #32 |
| **36** | Iteration Loop Management | Phase 2 | Polish→Review cycle | 2d | #35 |
| **37** | DB Integration for Tracking | Phase 2 | Track story workflow state | 2d | #35 |
| **38** | State Machine Implementation | Phase 2 | Story workflow states | 2d | #35 |
| **39** | Error Handling & Retry Logic | Phase 3 | Robust error handling | 2d | #35 |
| **40** | Cost Tracking & Optimization | Phase 3 | GPT API cost management | 2d | #39 |

---

## 👤 USER SELECTION

**To select modules for implementation, enter their numbers:**

Example: `1, 2, 3` or `18, 19` or `21-25`

### Recommended Starting Points:

| Focus Area | Recommended Modules | Notes |
|------------|---------------------|-------|
| **Core Workflow** | 1, 2, 3, 4 | Essential pipeline stages |
| **Integration** | 18, 19 | Quick wins, unblocked |
| **Enhancements** | 21, 22, 23 | Independent features |
| **Story Generation** | 31, 33, 35 | GPT expert review setup |

---

## 🚀 PARALLEL EXECUTION GROUPS

### Group A: Unblocked - Start Immediately

```bash
# === Module #18: State-Database Integration ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-18-state-db-integration
# Create: T/Integration/state_persistence.py
# Tests: T/Integration/_meta/tests/test_state_persistence.py

# === Module #19: Migration Script ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-19-migration
# Create: T/Database/migrations/001_initial_schema.py
# Tests: T/Database/_meta/tests/test_migration.py
```

### Group B: Core Workflow Sequence

```bash
# === Module #1: Title.From.Idea ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-01-title-from-idea
# Location: T/Title/From/Idea/
# Implement: src/title_generator.py
# Tests: _meta/tests/test_title_from_idea.py

# === Module #2: Script.FromIdeaAndTitle ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-02-script-from-idea-title
# Location: T/Script/FromIdeaAndTitle/
# Implement: src/script_generator.py
# Tests: _meta/tests/test_script_generator.py
```

### Group C: Enhancements (Independent)

```bash
# === Module #21: SEO Keywords ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-21-seo-keywords
# Create: T/Publishing/SEO/Keywords/
# Spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md

# === Module #22: Blog Format ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-22-blog-format
# Create: T/Script/Formatter/Blog/
# Spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md

# === Module #23: Batch Processing ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b module-23-batch-processing
# Create: T/Idea/Batch/
# Spec: T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md
```

---

## 📊 DEPENDENCY VISUALIZATION

```
                    ┌──────────────────────────────────────────────────────────────────┐
                    │                    WORKFLOW AFTER Idea.Creation                   │
                    └──────────────────────────────────────────────────────────────────┘
                                                   │
            ┌──────────────────────────────────────┼──────────────────────────────────────┐
            │                                      │                                      │
   ┌────────┴────────┐                  ┌──────────┴──────────┐               ┌───────────┴───────────┐
   │  PATH A: CORE   │                  │  PATH B: INTEGR.    │               │  PATH C: ENHANCE     │
   │  (Sequential)   │                  │  (Unblocked)        │               │  (Independent)       │
   └────────┬────────┘                  └──────────┬──────────┘               └───────────┬───────────┘
            │                                      │                                      │
     ┌──────┴──────┐                        ┌──────┴──────┐                        ┌──────┴──────┐
     │ #1 Title    │                        │ #18 State  │                        │ #21 SEO    │
     │ From.Idea   │                        │ Persist    │                        │ Keywords   │
     └──────┬──────┘                        └────────────┘                        └────────────┘
            │                                      │                                      │
     ┌──────┴──────┐                        ┌──────┴──────┐                        ┌──────┴──────┐
     │ #2 Script   │                        │ #19 DB     │                        │ #22 Blog   │
     │ FromIdea    │                        │ Migration  │                        │ Format     │
     └──────┬──────┘                        └────────────┘                        └────────────┘
            │                                                                            │
     ┌──────┴──────┐                                                              ┌──────┴──────┐
     │ #3-#4       │                                                              │ #23 Batch  │
     │ Reviews     │                                                              │ Processing │
     └──────┬──────┘                                                              └────────────┘
            │
     ┌──────┴──────┐
     │ #5-#8       │
     │ Alignment   │
     └──────┬──────┘
            │
     ┌──────┴──────┐
     │ #9-#15      │
     │ Quality     │
     └──────┬──────┘
            │
     ┌──────┴──────┐
     │ #16-#17     │
     │ Expert GPT  │
     └──────┬──────┘
            │
     ┌──────┴──────┐
     │ #20 Publish │
     │ Final       │
     └─────────────┘
```

---

## 🎉 COMPLETED WORK

- MVP-001 through MVP-024 ✅
- STATE-001, STATE-002, STATE-003 ✅
- DB-001 through DB-005 ✅ (175 tests passing)
- **PrismQ.T.Idea.Creation** ✅ (AI-powered idea generation)

See `_meta/issues/done/` for details.

---

## 📚 RELATED DOCUMENTATION

- **[PARALLEL_RUN_NEXT_FULL.md](PARALLEL_RUN_NEXT_FULL.md)** - Complete 48-issue POST-MVP roadmap
- **[T/WORKFLOW_DETAILED.md](../../T/WORKFLOW_DETAILED.md)** - Complete 18-stage workflow
- **[STORY_GENERATION_PLAN.md](new/STORY_GENERATION_PLAN.md)** - Story Generation implementation (STORY-001 to STORY-020)
- **[POST-MVP-ENHANCEMENTS.md](new/POST-MVP-ENHANCEMENTS.md)** - Enhancement issues reference
