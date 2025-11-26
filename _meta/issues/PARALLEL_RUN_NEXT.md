# PARALLEL_RUN_NEXT - Active Sprint Execution

> **Purpose**: This document tracks **ONLY** Work In Progress (WIP) and unblocked issues that can run in parallel.  
> **Completed Work**: See `_meta/issues/done/` for completed issues (MVP-001 through MVP-024 ✅)  
> **Full Roadmap**: See `PARALLEL_RUN_NEXT_FULL.md` for complete Post-MVP roadmap (POST-001 through POST-048)  
> **Post-MVP Issues**: See `T/_meta/issues/new/POST-MVP-Enhancements/` for detailed Text Pipeline issue specifications  
> **Story Generation**: See `_meta/issues/new/STORY_GENERATION_PLAN.md` for Story workflow implementation (STORY-001 to STORY-020)

**Date**: 2025-11-25 (Updated)  
**Current Sprint**: Sprint 4 - Text Pipeline Enhancements Part 1 + Story Generation Planning  
**Status**: 🎯 READY FOR EXECUTION  
**Timeline**: Weeks 9-10 (2 weeks)

---

## 🆕 Interactive Text Client with Independent State Processing

**Status**: ✅ IMPLEMENTED  
**Location**: `T/_meta/scripts/`

### Independent State Processing Architecture

Each workflow step runs as an **independent process** with state persisted between executions. This enables:
- Parallel execution of different workflows
- Fault tolerance (crashed steps can be rerun)
- Distributed processing across workers

### State Transformation Batch Scripts

| Batch Script | State Transformation | Description |
|--------------|---------------------|-------------|
| `step1_create_idea.bat` | `∅ → idea_created` | Create new idea from scratch |
| `step2_generate_title.bat` | `idea_created → title_generated` | Generate title variants from idea |
| `step3_generate_script.bat` | `title_generated → script_generated` | Generate script draft from title + idea |
| `step4_iterate_script.bat` | `script_generated → script_iterated` | Apply feedback loop (unlimited iterations) |
| `step5_export.bat` | `* → exported` | Export content to file |
| `load_demo.bat` | `∅ → idea_created` | Load demo idea for testing |
| `show_status.bat` | N/A (read-only) | Display current workflow state |
| `run_all_steps.bat` | `∅ → exported` | Run complete workflow sequentially |

### State Persistence

**State Database**: `T/_meta/scripts/text_client_state.db` (SQLite)

State is persisted to SQLite after each step, enabling:
```bash
# Run steps independently as separate processes
step1_create_idea.bat    # Process 1: Creates idea, saves state to SQLite
# ... time passes ...
step2_generate_title.bat # Process 2: Loads state, generates title, saves state
# ... time passes ...
step3_generate_script.bat # Process 3: Loads state, generates script, saves state
```

**SQLite State Schema**:
```sql
-- Session state table (single row, id=1)
session_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    idea_version INTEGER DEFAULT 0,
    title_version INTEGER DEFAULT 0,
    script_version INTEGER DEFAULT 0,
    current_title TEXT,
    current_script TEXT,
    session_start TEXT,
    updated_at TEXT
)

-- Idea data table (single row, id=1)
idea_data (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    title TEXT,
    concept TEXT,
    premise TEXT,
    logline TEXT,
    hook TEXT,
    skeleton TEXT,
    emotional_arc TEXT,
    twist TEXT,
    climax TEXT,
    tone_guidance TEXT,
    target_audience TEXT,
    genre TEXT
)

-- Action history table
action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT
)
```

### Version Tracking & Next-to-Process Selection

The system tracks version counts for each content type:
- **Idea Version**: Incremented on create/modify
- **Title Version**: Incremented on generation/selection
- **Script Version**: Incremented on generation/iteration

**Next-to-Process Algorithm**: Selects item with lowest version count
- Tie-breaking follows natural workflow order: Idea → Title → Script
- Ensures balanced progression through the workflow

### Database Integration (Future)

When database models are implemented, state will be stored in the `Story` table:

```sql
Story (
    id UUID PRIMARY KEY,
    status ENUM('draft', 'in_progress', 'review', 'approved', 'published'),
    -- State persisted for independent process execution
    idea_version INTEGER DEFAULT 0,
    title_version INTEGER DEFAULT 0,
    script_version INTEGER DEFAULT 0,
    current_title_version_id UUID FK NULL,
    current_script_version_id UUID FK NULL,
    ...
)
```

See [T/_meta/docs/DATABASE_DESIGN.md](../../../T/_meta/docs/DATABASE_DESIGN.md) for full schema.

### Command Line Actions

Python script supports direct action invocation:
```bash
python run_text_client.py --action create_idea
python run_text_client.py --action generate_title
python run_text_client.py --action generate_script
python run_text_client.py --action iterate_script
python run_text_client.py --action export
python run_text_client.py --action status
python run_text_client.py --action load_demo
python run_text_client.py --action reset
```

---

## 🆕 Story Generation Workflow - Implementation Planning

**Status**: ✅ PLANNING COMPLETE - Awaiting Worker10 Review  
**Documentation Package**: 83KB across 6 files  
**Location**: `_meta/issues/new/Worker01/`

### Overview
Story Generation (Stages 21-22) serves as the final quality gate before publishing, using GPT-based expert review and polish.

**Workflow Position**:
```
Stage 1-20: Text Pipeline (Idea → Title → Script → Local Reviews) ✅ COMPLETE
    ↓
Stage 21: Story.ExpertReview (GPT-based holistic review) ⚠️ PLANNING DONE
    ↓
    ├─ If PUBLISH → Stage 23: Publishing.Finalization
    │
    └─ If POLISH → Stage 22: Story.Polish (Apply improvements)
                       ↓
                   Return to Stage 21 (Review again)
```

### Key Documents

| Document | Size | Purpose |
|----------|------|---------|
| [STORY_GENERATION_PLAN.md](new/STORY_GENERATION_PLAN.md) | 10KB | Master implementation plan with 20 atomic issues |
| [STORY_GENERATION_OVERVIEW.md](new/Worker01/STORY_GENERATION_OVERVIEW.md) | 16KB | Complete planning package summary |
| [STORY-001-GPT-Review-API-Integration.md](new/Worker01/STORY-001-GPT-Review-API-Integration.md) | 16KB | Sample atomic issue: GPT API integration |
| [STORY-003-Prompt-Engineering.md](new/Worker01/STORY-003-Prompt-Engineering.md) | 16KB | Sample atomic issue: Prompt engineering |
| [STORY-005-Workflow-Orchestrator.md](new/Worker01/STORY-005-Workflow-Orchestrator.md) | 21KB | Sample atomic issue: Orchestration |
| [TASK_CHECKLIST.md](new/Worker01/TASK_CHECKLIST.md) | 8KB | Verification checklist |
| [WORKER10_REVIEW_REQUEST.md](new/Worker01/WORKER10_REVIEW_REQUEST.md) | 8KB | Review request for Worker10 |

### Story Issues Summary (20 issues across 5 phases)

**Phase 1: GPT Integration (Issues STORY-001 to STORY-004)** - 4 days
- STORY-001: GPT API Integration for ExpertReview
- STORY-002: GPT API Integration for Polish
- STORY-003: Prompt Engineering and Templates
- STORY-004: Response Parsing and Validation

**Phase 2: Workflow Orchestration (Issues STORY-005 to STORY-008)** - 5 days
- STORY-005: Workflow Orchestrator
- STORY-006: Review Loop Controller
- STORY-007: State Management and Persistence
- STORY-008: Error Recovery System

**Phase 3: Database Integration (Issues STORY-009 to STORY-012)** - 4 days
- STORY-009: Review History Repository
- STORY-010: Polish Change Tracking
- STORY-011: Analytics and Metrics
- STORY-012: Caching Layer

**Phase 4: CLI and API (Issues STORY-013 to STORY-016)** - 4 days
- STORY-013: CLI Runner
- STORY-014: REST API Endpoints
- STORY-015: Status Monitoring
- STORY-016: Configuration Management

**Phase 5: Testing and Polish (Issues STORY-017 to STORY-020)** - 5 days
- STORY-017: Integration Test Suite
- STORY-018: Performance Testing
- STORY-019: Documentation
- STORY-020: Production Deployment

**Next Action**: Worker10 review required before execution

---

## 🎉 MVP Complete: All 24 Issues Done!

**MVP Status**: ✅ ALL COMPLETE (MVP-001 through MVP-024)  
**Location**: All MVP issues moved to `_meta/issues/done/`

**Foundation Built**:
- ✅ Idea Creation (MVP-001)
- ✅ Title Generation v1, v2, v3 (MVP-002, MVP-006)
- ✅ Script Generation v1, v2, v3 (MVP-003, MVP-007)
- ✅ Cross-Review System (MVP-004, MVP-005)
- ✅ Acceptance Gates (MVP-012, MVP-013)
- ✅ Quality Reviews: Grammar, Tone, Content, Consistency, Editing (MVP-014-018)
- ✅ Readability Checks (MVP-019, MVP-020)
- ✅ Expert Review & Polish (MVP-021, MVP-022)
- ✅ Publishing Pipeline (MVP-023, MVP-024)

**Next Phase**: Post-MVP Enhancements (48 issues across Sprints 4-11) + Story Generation (20 issues)

---

## Sprint 4: Text Pipeline Enhancement - Part 1 (CURRENT)

**Goal**: Add SEO optimization, multi-format support, and batch processing to T module  
**Timeline**: Weeks 9-10 (2 weeks)  
**Active Workers**: Worker02, Worker12, Worker13, Worker17  
**Status**: 🎯 READY FOR EXECUTION

### Unblocked Issues Ready to Start

#### POST-001: T.Publishing.SEO - Keyword Research & Optimization
**Worker**: Worker17 (Analytics) + Worker13 (Prompt Master)  
**Priority**: High | **Effort**: 2 days | **Status**: 🆕 UNBLOCKED

**Quick Summary**: Implement automated SEO keyword research and optimization for published content.

**Acceptance Criteria**:
- Extract relevant keywords from title and script
- Generate SEO-optimized metadata (title tags, meta descriptions)
- Keyword density analysis
- Store SEO data with published content

**Dependencies**: MVP-024 ✅ (Complete)  
**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md](../../T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md)

---

#### POST-003: T.Script.MultiFormat - Blog Format Optimization
**Worker**: Worker12 (Content Specialist)  
**Priority**: High | **Effort**: 2 days | **Status**: 🆕 UNBLOCKED

**Quick Summary**: Transform scripts into blog-optimized format with heading hierarchy, sections, and formatting.

**Acceptance Criteria**:
- Convert script to blog structure (H1, H2, H3 hierarchy)
- Add paragraph breaks and formatting
- Platform-specific optimizations (Medium, WordPress, Ghost)
- Generate blog metadata (excerpt, reading time)

**Dependencies**: MVP-024 ✅ (Complete)  
**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md](../../T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md)

---

#### POST-005: T.Idea.Batch - Batch Idea Processing
**Worker**: Worker02 (Python Specialist)  
**Priority**: Medium | **Effort**: 2 days | **Status**: 🆕 UNBLOCKED

**Quick Summary**: Process multiple ideas in parallel for efficient content pipeline scaling.

**Acceptance Criteria**:
- Accept list of ideas as input (10-100+ ideas)
- Process ideas concurrently using async/parallel execution
- Track batch processing status
- Handle failures gracefully with retry logic

**Dependencies**: MVP-001 ✅ (Complete)  
**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md](../../T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md)

---

### Blocked Issues (Ready Next)

#### POST-002: T.Publishing.SEO - Tags & Categories
**Worker**: Worker17 (Analytics)  
**Priority**: High | **Effort**: 1.5 days | **Status**: 🔒 BLOCKED

**Blocked By**: POST-001 (SEO Keywords must complete first)  
**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/POST-002-SEO-Taxonomy.md](../../T/_meta/issues/new/POST-MVP-Enhancements/POST-002-SEO-Taxonomy.md)

---

#### POST-004: T.Script.MultiFormat - Social Media Adaptation
**Worker**: Worker12 (Content Specialist)  
**Priority**: High | **Effort**: 2 days | **Status**: 🔒 BLOCKED

**Blocked By**: POST-003 (Blog Format - using shared formatting infrastructure)  
**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/POST-004-Social-Media-Format.md](../../T/_meta/issues/new/POST-MVP-Enhancements/POST-004-Social-Media-Format.md)

---

#### POST-006: T.Title.ABTesting - A/B Testing Framework
**Worker**: Worker17 (Analytics)  
**Priority**: Medium | **Effort**: 2 days | **Status**: 🔒 BLOCKED

**Blocked By**: POST-001, POST-002 (SEO infrastructure needed)  
**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/POST-006-ABTesting.md](../../T/_meta/issues/new/POST-MVP-Enhancements/POST-006-ABTesting.md)

---

## Sprint 4 Execution Plan

### Week 1: Parallel Track (3 workers)
```bash
# Track A: SEO Foundation
Worker17: POST-001 (SEO Keywords) [2 days]
Worker13: Support POST-001 with prompt engineering [2 days]

# Track B: Multi-Format Content
Worker12: POST-003 (Blog Format) [2 days]

# Track C: Scalability
Worker02: POST-005 (Batch Processing) [2 days]
```

### Week 2: Sequential Completion (2-3 workers)
```bash
# After POST-001 completes
Worker17: POST-002 (Tags & Categories) [1.5 days] → POST-006 (A/B Testing) [0.5 days]

# After POST-003 completes
Worker12: POST-004 (Social Media) [2 days]

# Support/Testing
Worker04: Integration testing [2 days]
Worker15: Documentation updates [2 days]
```

**Total Calendar Time**: ~10 days (with weekends: 2 weeks)

---

## Sprint 5: Text Pipeline Enhancement - Part 2 (NEXT)

**Goal**: Add inspiration sources, versioning, and collaboration features  
**Timeline**: Weeks 11-12 (2 weeks)  
**Status**: 🔜 UPCOMING

### Planned Issues (Not Yet Unblocked)
- POST-007: YouTube API Inspiration (Worker08) - 2 days
- POST-008: RSS Feed Inspiration (Worker08) - 1.5 days
- POST-009: Twitter/X API Inspiration (Worker08) - 1.5 days
- POST-010: Script Versioning (Worker06) - 2 days
- POST-011: Multi-Reviewer Workflow (Worker18) - 2 days
- POST-012: Inline Comments (Worker18) - 2 days

**Details**: See [T/_meta/issues/new/POST-MVP-Enhancements/INDEX.md](../../T/_meta/issues/new/POST-MVP-Enhancements/INDEX.md)

---

## Issue State Management

### Issue States
- 🆕 **UNBLOCKED**: Ready to start immediately (no blocking dependencies)
- 🔒 **BLOCKED**: Waiting on dependency completion
- 🔄 **WIP**: Currently being worked on
- ✅ **COMPLETE**: Done and moved to `_meta/issues/done/`

### Moving Issues

**When starting work**:
```bash
# Move issue to WIP folder (when Worker begins)
mv _meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md _meta/issues/wip/
```

**When completing work**:
```bash
# Move issue to done folder (after PR merge and review)
mv _meta/issues/wip/POST-001-SEO-Keywords.md _meta/issues/done/
```

**Unblocking issues**:
```bash
# When POST-001 completes, POST-002 becomes unblocked
# Update this file to move POST-002 to "Unblocked Issues" section
```

---

## Sprint 4 Success Criteria

### Must Complete (Unblocked Issues)
- [ ] POST-001: SEO Keywords functional
- [ ] POST-003: Blog format working for 3+ platforms
- [ ] POST-005: Batch processing handles 50+ ideas

### Should Complete (Blocked Issues)
- [ ] POST-002: Tags & Categories integrated
- [ ] POST-004: Social media formatting for 4+ platforms
- [ ] POST-006: A/B Testing framework operational

### Quality Gates
- [ ] All new code has >80% test coverage
- [ ] Integration tests pass for new features
- [ ] Documentation updated
- [ ] Code review completed by Worker10
- [ ] No security vulnerabilities introduced

---

## Commands for Workers

### Worker17 + Worker13: Start POST-001
```bash
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-001-seo-keywords
# Create implementation in T/Publishing/SEO/Keywords/
# Follow spec in T/_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md
```

### Worker12: Start POST-003
```bash
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-003-blog-format
# Create implementation in T/Script/Formatter/Blog/
# Follow spec in T/_meta/issues/new/POST-MVP-Enhancements/POST-003-Blog-Format.md
```

### Worker02: Start POST-005
```bash
cd /home/runner/work/PrismQ/PrismQ
git checkout -b post-005-batch-processing
# Create implementation in T/Idea/Batch/
# Follow spec in T/_meta/issues/new/POST-MVP-Enhancements/POST-005-Batch-Processing.md
```

---

## Progress Tracking

### Sprint 4 Progress
**Week 1**: 0/3 unblocked issues started  
**Week 2**: 0/3 blocked issues started  
**Overall**: 0/6 issues complete

**Last Updated**: 2025-11-24

---

## Related Documents

### Issue References
- **Completed MVPs**: `_meta/issues/done/MVP-*.md` (001-024)
- **Text Pipeline POST Issues**: `T/_meta/issues/new/POST-MVP-Enhancements/` (POST-001 to POST-012)
- **POST Issue Index**: `T/_meta/issues/new/POST-MVP-Enhancements/INDEX.md`
- **POST Issue Reference**: `_meta/issues/new/POST-MVP-ENHANCEMENTS.md`
- **Story Generation Plan**: `_meta/issues/new/STORY_GENERATION_PLAN.md` (STORY-001 to STORY-020)
- **Story Generation Package**: `_meta/issues/new/Worker01/` (Complete planning documentation)

### Planning Documents
- **Full Roadmap**: `_meta/issues/PARALLEL_RUN_NEXT_FULL.md` (All 48 POST issues)
- **Archive (Consolidated)**: `_meta/issues/archive/` (MVP reviews and historical planning)
  - `MVP_REVIEWS_CONSOLIDATED.md` - All MVP implementation reviews
  - `HISTORICAL_PLANNING_CONSOLIDATED.md` - Historical planning documents
- **Issue Management**: `_meta/issues/ISSUE_MANAGEMENT_STRUCTURE.md`

---

**Status**: Sprint 4 Ready - 3 POST Issues Unblocked + Story Generation Planning Complete  
**Next Action**: Worker17, Worker12, Worker02 begin POST execution; Worker10 review Story Generation  
**Updated**: 2025-11-24  
**Owner**: Worker01 (Project Manager)
