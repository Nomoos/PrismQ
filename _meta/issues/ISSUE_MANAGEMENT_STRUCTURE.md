# Issue Management Structure - November 2025 Refactoring

**Date**: 2025-11-24 (Updated - Archive Cleanup Complete)  
**Purpose**: Document the standardized issue management structure across PrismQ  

---

## Recent Updates (2025-11-24)

### Archive Cleanup Complete ✅
Individual archive files have been merged and removed:
- **41 individual files** → **2 consolidated documents** (95% reduction)
- `mvp-reviews/` directory removed (content in MVP_REVIEWS_CONSOLIDATED.md)
- `planning/` directory removed (content in HISTORICAL_PLANNING_CONSOLIDATED.md)
- All historical data preserved in consolidated documents

### Story Generation Workflow Added
New implementation planning package merged:
- **STORY_GENERATION_PLAN.md**: Master plan with 20 atomic issues (STORY-001 to STORY-020)
- **Worker01/** directory: Complete planning documentation (83KB across 6 files)
- Implements Stages 21-22 (Story.ExpertReview + Story.Polish) from WORKFLOW_DETAILED.md

### Previous Documentation Updates
✅ Replaced PARALLEL_RUN_NEXT_FULL.md with actual POST-001 to POST-048 roadmap  
✅ Updated archive README with quick access links to consolidated documents  
✅ Created done/README.md to document completed issues structure  
✅ Moved MVP-006 specification from new/ to done/

**Impact**: Cleaner structure, faster navigation, complete historical preservation

---

## Summary

Current issue management state:
- **47 issue directories** follow consistent structure
- **2 consolidated archive documents** (formerly 41 individual files)
- **Story Generation** planning package ready for Worker10 review
- **POST-MVP roadmap** complete (48 issues across Sprints 4-11)

---

## Standardized Structure

All `_meta/issues` directories now follow this structure:

```
_meta/issues/
├── new/          # New issues ready for work
│   ├── STORY_GENERATION_PLAN.md    # Story workflow implementation (STORY-001 to STORY-020)
│   ├── Worker01/                   # Story Generation planning package
│   └── POST-MVP-ENHANCEMENTS.md    # Text pipeline enhancements reference
├── wip/          # Work in progress
├── done/         # Recently completed (active retention)
├── blocked/      # Issues awaiting dependencies
└── archive/      # Historical content (consolidated)
    ├── MVP_REVIEWS_CONSOLIDATED.md         # All MVP reviews (21 files merged)
    └── HISTORICAL_PLANNING_CONSOLIDATED.md # All planning docs (20 files merged)
```

---

## Archive Contents (Consolidated)

### Main Issues Archive (`_meta/issues/archive/`)

**2 consolidated documents** containing all historical content:

| Document | Content | Original Files |
|----------|---------|----------------|
| MVP_REVIEWS_CONSOLIDATED.md | MVP-001 through MVP-022 reviews, MODULE_T_STORY_REVIEW, DOCS/TEST reviews | 21 files |
| HISTORICAL_PLANNING_CONSOLIDATED.md | State snapshots, workflows, issue plans, project summaries | 20 files |

**Note**: Original subdirectories (`mvp-reviews/`, `planning/`) have been removed after consolidation.

[Full documentation](./archive/README.md)

### 2. Client Frontend TaskManager Archive
**32 archived files** including:
- Frontend implementation issues (ISSUE-FRONTEND-001 through ISSUE-FRONTEND-018)
- Worker-specific completion reports
- Implementation summaries and review documentation

[Full documentation](./Client/Frontend/TaskManager/_meta/issues/archive/README.md)

### 3. T.Idea.Inspiration Archive
**19 archived files** including:
- TaskManager integration completion summaries
- Worker implementation documentation
- Database optimization and performance tuning investigations

[Full documentation](./T/Idea/Inspiration/_meta/issues/archive/completed-work/README.md)

### 4. T.Idea.Inspiration.Source Archive
**5 archived files** including:
- Developer implementation documentation
- Integration completion reports

[Full documentation](./T/Idea/Inspiration/Source/_meta/issues/archive/README.md)

---

## Archival Policy

Documents are archived when they:

1. **Complete their purpose** - Implementation finished, issues resolved
2. **No longer actively referenced** - Historical context only
3. **Should be preserved** - Valuable for future reference
4. **Would clutter active directories** - Keep active areas focused

---

## Active Issue Tracking

For current work across all modules:

- **[PARALLEL_RUN_NEXT.md](_meta/issues/PARALLEL_RUN_NEXT.md)** - Current sprint execution
- **[PARALLEL_RUN_NEXT_FULL.md](_meta/issues/PARALLEL_RUN_NEXT_FULL.md)** - Complete roadmap
- Module-specific `_meta/issues/new/` directories for component-level issues

---

## Module Structure

All modules (T, A, V, Client) and their subcomponents follow the standardized structure:

### Text Generation (T)
- T/_meta/issues/
- T/Idea/_meta/issues/
- T/Script/_meta/issues/
- T/Title/_meta/issues/
- T/Review/_meta/issues/ (and subcomponents)
- T/Publishing/_meta/issues/ (and subcomponents)

### Audio Generation (A)
- A/_meta/issues/
- A/Narrator/_meta/issues/
- A/Voiceover/_meta/issues/
- A/Publishing/_meta/issues/ (and subcomponents)

### Video Generation (V)
- V/_meta/issues/
- V/Keyframe/_meta/issues/ (and subcomponents)
- V/Scene/_meta/issues/ (and subcomponents)
- V/Video/_meta/issues/

### Client Infrastructure
- Client/_meta/issues/
- Client/Frontend/TaskManager/_meta/issues/
- Client/Backend/TaskManager/_meta/issues/

---

## Benefits of Refactoring

1. **Consistency**: All 47 directories follow same pattern
2. **Clarity**: Clear separation between active and historical work
3. **Preservation**: Historical context maintained with documentation
4. **Focus**: Active directories remain uncluttered
5. **Scalability**: Structure ready for future growth

---

## Maintenance

When archiving future work:

1. Move completed work from `done/` to `archive/` when appropriate
2. Create descriptive subdirectories in archive (e.g., `archive/sprint-5/`)
3. Update archive README to document new content
4. Ensure no active references point to archived files
5. Keep `done/` for recently completed work (current retention period)

---

## Related Documentation

- [Project README](README.md)
- [Meta Documentation](_meta/README.md)
- [Current Sprint Plan](_meta/issues/PARALLEL_RUN_NEXT.md)
