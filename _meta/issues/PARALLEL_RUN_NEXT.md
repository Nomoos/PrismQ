# PARALLEL_RUN_NEXT - MVP Sprint Execution (Iterative Co-Improvement)

**Sprint**: Sprint 1-3 (6 weeks) - MVP Iterative Workflow  
**Date**: 2025-11-21  
**Status**: Planning  
**Goal**: Build MVP with **iterative title-script co-improvement cycle** following: **Idea → Title v1 → Script v1 → Cross-Reviews → Title v2 ← Script v2 → Reviews v2 → Refinements v3 → Acceptance Gates → Readability Checks → Publish**

---

## Enhanced MVP Approach

### Why Iterative Co-Improvement?
- **Higher quality**: Title and script validated against each other
- **Coherent output**: Changes to one element trigger re-validation of other
- **Explicit gates**: Acceptance checks before proceeding
- **Final validation**: Readability checks ensure publishing quality
- **Trade-off**: +2 weeks (6 vs 4) for significantly better quality

### Iterative Co-Improvement Workflow (16 Stages)

**Reference**: See `T/TITLE_SCRIPT_WORKFLOW.md` and `MVP_WORKFLOW.md` for complete documentation.

**Iterative Path** (16 stages with co-dependent improvement cycles):

```
1. PrismQ.T.Idea.Creation
       ↓
2. PrismQ.T.Title.Draft (v1) ← from Idea
       ↓
3. PrismQ.T.Script.Draft (v1) ← from Idea + Title v1
       ↓
4. PrismQ.T.Rewiew.Title.ByScript ← Review Title v1 by Script v1 + Idea
       ↓
5. PrismQ.T.Rewiew.Script.ByTitle ← Review Script v1 by Title v1 + Idea
       ↓
6. PrismQ.T.Title.Improvements (v2) ← Using reviews + title v1, script v1
       ↓
7. PrismQ.T.Script.Improvements (v2) ← Using reviews + new title v2, script v1
       ↓
8. PrismQ.T.Rewiew.Title.ByScript (v2) ←──────────┐
       ↓                                           │
9. PrismQ.T.Title.Refinement (v3)                 │
       ↓                                           │
10. PrismQ.T.Rewiew.Script.ByTitle (v2) ←─────┐   │
        ↓                                      │   │
11. PrismQ.T.Script.Refinement (v3)            │   │
        ↓                                      │   │
12. Title Acceptance Check ─NO─────────────────┘   │
        ↓ YES                                      │
13. Script Acceptance Check ─NO────────────────────┘
        ↓ YES
14. PrismQ.T.Rewiew.Title.Readability (Voiceover) ←──────┐
        ↓                                                │
        ├─FAILS─→ Return to step 9 ──────────────────────┘
        ↓ PASSES
15. PrismQ.T.Rewiew.Script.Readability (Voiceover) ←─────┐
        ↓                                                 │
        ├─FAILS─→ Return to step 11 ─────────────────────┘
        ↓ PASSES
16. PrismQ.T.Publishing.Finalization
```

**Key Innovations**:
- **Co-dependent improvement**: Title reviewed by script context, script by title context
- **Version tracking**: v1 (initial), v2 (first improvements), v3+ (refinements)
- **Explicit acceptance gates**: Must pass checks before proceeding (steps 12-13)
- **Final readability validation**: Ensures publishing quality (steps 14-15)
- **Context preservation**: Original versions kept for reference throughout

**Folder Paths:**
- `T/Idea/Creation/` - Idea creation
- `T/Title/Draft/` - Title v1 drafting
- `T/Script/Draft/` - Script v1 drafting
- `T/Rewiew/Idea/` - Title reviews (steps 4, 8, 12, 14)
- `T/Rewiew/Script/` - Script reviews (steps 5, 10, 13, 15)
- `T/Title/Improvements/` - Title v2 improvements (step 6)
- `T/Script/Improvements/` - Script v2 improvements + v3 refinements (steps 7, 11)
- `T/Title/Refinement/` - Title v3+ refinements (step 9)
- `T/Rewiew/Readability/` - Readability validation (steps 14-15)
- `T/Publishing/Finalization/` - Publishing (step 16)

---

## Sprint 1: Initial Drafts + Cross-Reviews (Weeks 1-2)

### Week 1: Foundation - Initial Drafts

**Goal**: Idea → Title v1 → Script v1 created  
**Active Workers**: 3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-001 | 2d | Idea Creation |
| **Worker13** | #MVP-002 | 2d | Title Draft v1 (from Idea) |
| **Worker02** | #MVP-003 | 3d | Script Draft v1 (from Idea + Title v1) |
| **Worker15** | Documentation | 2d | MVP workflow docs |
| **Worker04** | Test Setup | 2d | Test framework for iterative workflow |

**Commands**:
```
Worker02: Implement #MVP-001 in T/Idea/Creation/
- Module: PrismQ.T.Idea.Creation
- Dependencies: None
- Priority: Critical
- Effort: 2 days
- Deliverable: Basic idea capture and storage

Worker13: Implement #MVP-002 in T/Title/Draft/
- Module: PrismQ.T.Title.Draft
- Dependencies: #MVP-001 (can start in parallel)
- Priority: Critical
- Effort: 2 days
- Deliverable: Generate 3-5 title variants (v1) from idea only

Worker02: Implement #MVP-003 in T/Script/Draft/
- Module: PrismQ.T.Script.Draft
- Dependencies: #MVP-002
- Priority: Critical
- Effort: 3 days
- Deliverable: Generate initial script (v1) from idea + title v1
```

**Week 1 Deliverable**: ✅ Idea → Title v1 → Script v1 pipeline working

---

### Week 2: Cross-Review Cycle

**Goal**: Title and script reviewed in context of each other  
**Active Workers**: 2

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker10** | #MVP-004 | 1d | Title Review by Script & Idea |
| **Worker10** | #MVP-005 | 1d | Script Review by Title & Idea |

**Commands**:
```
Worker10: Implement #MVP-004 in T/Rewiew/Idea/
- Module: PrismQ.T.Rewiew.Title.ByScript
- Dependencies: #MVP-003 (need both title v1 and script v1)
- Priority: Critical
- Effort: 1 day
- Deliverable: Review title v1 against script v1 and idea - generate feedback

Worker10: Implement #MVP-005 in T/Rewiew/Script/
- Module: PrismQ.T.Rewiew.Script.ByTitle
- Dependencies: #MVP-003
- Priority: Critical
- Effort: 1 day
- Deliverable: Review script v1 against title v1 and idea - generate feedback
```

**Week 2 Deliverable**: ✅ Cross-validation reviews for both title and script complete

---

## Sprint 2: Improvement Cycle v2 + Refinements v3 (Weeks 3-4)

### Week 3: Generate v2 Versions with Cross-Context

**Goal**: Create improved v2 versions using cross-reviews  
**Active Workers**: 3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker13** | #MVP-006 | 2d | Title Improvements v2 (using both reviews + title v1, script v1) |
| **Worker02** | #MVP-007 | 2d | Script Improvements v2 (using both reviews + new title v2, script v1) |
| **Worker10** | #MVP-008 | 1d | Title Review v2 (review title v2 by script v2) |

**Commands**:
```
Worker13: Implement #MVP-006 in T/Title/Improvements/
- Module: PrismQ.T.Title.Improvements
- Dependencies: #MVP-004, #MVP-005 (need both reviews)
- Priority: Critical
- Effort: 2 days
- Deliverable: Generate title v2 using:
  - Title review feedback (step 4)
  - Script review feedback (step 5)
  - Title v1
  - Script v1

Worker02: Implement #MVP-007 in T/Script/Improvements/
- Module: PrismQ.T.Script.Improvements
- Dependencies: #MVP-006 (needs new title v2)
- Priority: Critical
- Effort: 2 days
- Deliverable: Generate script v2 using:
  - Script review feedback (step 5)
  - Title review feedback (step 4)
  - Script v1
  - **New title v2** (from step 6)

Worker10: Implement #MVP-008 in T/Rewiew/Idea/
- Module: PrismQ.T.Rewiew.Title.ByScript (v2)
- Dependencies: #MVP-007 (need both v2 versions)
- Priority: Critical
- Effort: 1 day
- Deliverable: Review title v2 against script v2 - generate feedback
```

**Week 3 Deliverable**: ✅ Title v2 and script v2 generated with cross-context, title v2 reviewed

---

### Week 4: Refinements to v3

**Goal**: Refine both title and script to v3 based on v2 reviews  
**Active Workers**: 3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker13** | #MVP-009 | 1d | Title Refinement v3 (based on v2 review) |
| **Worker10** | #MVP-010 | 1d | Script Review v2 by Title v3 |
| **Worker02** | #MVP-011 | 2d | Script Refinement v3 (based on review + title v3) |

**Commands**:
```
Worker13: Implement #MVP-009 in T/Title/Refinement/
- Module: PrismQ.T.Title.Refinement
- Dependencies: #MVP-008 (need v2 review feedback)
- Priority: Critical
- Effort: 1 day
- Deliverable: Refine title from v2 to v3 using feedback from step 8

Worker10: Implement #MVP-010 in T/Rewiew/Script/
- Module: PrismQ.T.Rewiew.Script.ByTitle (v2)
- Dependencies: #MVP-009 (need title v3)
- Priority: Critical
- Effort: 1 day
- Deliverable: Review script v2 against newest title v3 - generate feedback

Worker02: Implement #MVP-011 in T/Script/Improvements/
- Module: PrismQ.T.Script.Refinement
- Dependencies: #MVP-010
- Priority: Critical
- Effort: 2 days
- Deliverable: Refine script from v2 to v3 using feedback + ensure alignment with title v3
```

**Week 4 Deliverable**: ✅ Title v3 and script v3 refined and ready for acceptance gates

---

## Sprint 3: Validation & Publishing (Weeks 5-6)

### Week 5: Acceptance Gates + Readability Checks

**Goal**: Validate quality through acceptance gates and readability checks  
**Active Workers**: 2-3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker10** | #MVP-012 | 0.5d | Title Acceptance Gate |
| **Worker10** | #MVP-013 | 0.5d | Script Acceptance Gate |
| **Worker10** | #MVP-014 | 0.5d | Title Readability Review |
| **Worker10** | #MVP-015 | 0.5d | Script Readability/Voiceover Review |
| **Worker04** | E2E Tests | 3d | Test all paths including loops |

**Commands**:
```
Worker10: Implement #MVP-012 in T/Rewiew/Idea/
- Module: PrismQ.T.Rewiew.Title.Acceptance
- Dependencies: #MVP-011 (need title v3)
- Priority: Critical
- Effort: 0.5 days
- Deliverable: Acceptance check for title v3
  - If ACCEPTED: proceed to #MVP-013
  - If NOT ACCEPTED: loop back to #MVP-008 (review again → refine to v4)

Worker10: Implement #MVP-013 in T/Rewiew/Script/
- Module: PrismQ.T.Rewiew.Script.Acceptance
- Dependencies: #MVP-012 (title must be accepted first)
- Priority: Critical
- Effort: 0.5 days
- Deliverable: Acceptance check for script v3
  - If ACCEPTED: proceed to #MVP-014
  - If NOT ACCEPTED: loop back to #MVP-010 (review again → refine to v4)

Worker10: Implement #MVP-014 in T/Rewiew/Readability/
- Module: PrismQ.T.Rewiew.Title.Readability
- Dependencies: #MVP-013 (both must be accepted)
- Priority: Critical
- Effort: 0.5 days
- Deliverable: Readability check for title
  - If PASSES: proceed to #MVP-015
  - If FAILS: return to #MVP-009 (refine with readability feedback)

Worker10: Implement #MVP-015 in T/Rewiew/Readability/
- Module: PrismQ.T.Rewiew.Script.Readability
- Dependencies: #MVP-014 (title readability passed)
- Priority: Critical
- Effort: 0.5 days
- Deliverable: Readability/voiceover check for script
  - If PASSES: proceed to #MVP-016
  - If FAILS: return to #MVP-011 (refine with readability feedback)

Worker04: Complete E2E testing with all iteration paths
- Dependencies: All MVP features
- Priority: High
- Effort: 3 days
- Deliverable: Full test suite covering:
  - Happy path (all pass first time)
  - Title acceptance loop (fails once, then passes)
  - Script acceptance loop (fails once, then passes)
  - Readability loops (title fails, script fails)
  - Multiple iterations (v4, v5, etc.)
```

**Week 5 Deliverable**: ✅ All acceptance gates and readability checks implemented + tested

**Buffer**: Week 5 allows time for iteration loops if acceptance checks fail in testing

---

### Week 6: Publishing + Final Validation

**Goal**: End-to-end flow complete with published content  
**Active Workers**: 3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-016 | 2d | Publishing |
| **Worker15** | User Guide | 2d | Complete documentation with iteration examples |
| **Worker04** | Final Validation | 2d | Validate all scenarios work correctly |

**Commands**:
```
Worker02: Implement #MVP-016 in T/Publishing/Finalization/
- Module: PrismQ.T.Publishing.Finalization
- Dependencies: #MVP-015 (all checks passed)
- Priority: Critical
- Effort: 2 days
- Deliverable: Publish approved + validated content
  - Mark as "published"
  - Export to output format
  - Store published version with all versions tracked

Worker15: Complete user guide with iteration loop documentation
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Deliverable: Complete documentation including:
  - How to handle review feedback
  - How iteration loops work
  - Examples of acceptance gate failures
  - How to trigger readability re-checks
  - Version tracking explanation (v1, v2, v3, etc.)

Worker04: Final MVP validation of all paths
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Deliverable: Validate that:
  - Happy path works (no loops)
  - All loop paths work (acceptance gates, readability)
  - Version tracking works correctly
  - Published content includes correct final versions
```

**Week 6 Deliverable**: ✅ Complete MVP with iterative co-improvement workflow fully functional

---

## MVP Issues Summary

| Issue | Module | Stage | Worker | Effort | Description |
|-------|--------|-------|--------|--------|-------------|
| #MVP-001 | PrismQ.T.Idea.Creation | Idea | Worker02 | 2d | Basic idea capture |
| #MVP-002 | PrismQ.T.Title.Draft | Title v1 | Worker13 | 2d | Title generation from idea |
| #MVP-003 | PrismQ.T.Script.Draft | Script v1 | Worker02 | 3d | Script generation from idea + title v1 |
| #MVP-004 | PrismQ.T.Rewiew.Title.ByScript | **Title Review by Script** | Worker10 | 1d | Review title v1 against script v1 + idea |
| #MVP-005 | PrismQ.T.Rewiew.Script.ByTitle | **Script Review by Title** | Worker10 | 1d | Review script v1 against title v1 + idea |
| #MVP-006 | PrismQ.T.Title.Improvements | Title v2 | Worker13 | 2d | Title v2 using cross-reviews + title v1, script v1 |
| #MVP-007 | PrismQ.T.Script.Improvements | Script v2 | Worker02 | 2d | Script v2 using cross-reviews + new title v2, script v1 |
| #MVP-008 | PrismQ.T.Rewiew.Title.ByScript | **Title Review v2** | Worker10 | 1d | Review title v2 against script v2 |
| #MVP-009 | PrismQ.T.Title.Refinement | Title v3 | Worker13 | 1d | Refine title v2 → v3 |
| #MVP-010 | PrismQ.T.Rewiew.Script.ByTitle | **Script Review v2** | Worker10 | 1d | Review script v2 against title v3 |
| #MVP-011 | PrismQ.T.Script.Refinement | Script v3 | Worker02 | 2d | Refine script v2 → v3 |
| #MVP-012 | PrismQ.T.Rewiew.Title.Acceptance | **Acceptance Gate** | Worker10 | 0.5d | Check if title v3 is accepted (loop if not) |
| #MVP-013 | PrismQ.T.Rewiew.Script.Acceptance | **Acceptance Gate** | Worker10 | 0.5d | Check if script v3 is accepted (loop if not) |
| #MVP-014 | PrismQ.T.Rewiew.Title.Readability | **Readability Check** | Worker10 | 0.5d | Final title readability/voiceover validation |
| #MVP-015 | PrismQ.T.Rewiew.Script.Readability | **Readability Check** | Worker10 | 0.5d | Final script readability/voiceover validation |
| #MVP-016 | PrismQ.T.Publishing.Finalization | Publish | Worker02 | 2d | Publishing approved + validated content |

**Total**: 16 issues, 20 days of work, 6 weeks calendar time with 3-4 workers

**Key Features**:
- **Co-dependent improvement**: Title and script reviewed against each other (steps 4-5, 8, 10)
- **Version tracking**: v1 (initial), v2 (improved), v3+ (refined)
- **Explicit acceptance gates**: Must pass before proceeding (steps 12-13)
- **Final readability validation**: Ensures publishing quality (steps 14-15)
- **Iteration loops**: Return to refinement if acceptance/readability fails

**Folder Paths:**
- `T/Idea/Creation/` (step 1)
- `T/Title/Draft/` (step 2)
- `T/Script/Draft/` (step 3)
- `T/Rewiew/Idea/` (steps 4, 8, 12, 14)
- `T/Rewiew/Script/` (steps 5, 10, 13, 15)
- `T/Title/Improvements/` (step 6)
- `T/Script/Improvements/` (steps 7, 11)
- `T/Title/Refinement/` (step 9)
- `T/Rewiew/Readability/` (steps 14-15)
- `T/Publishing/Finalization/` (step 16)

---

## Workflow State Machine (Iterative Co-Improvement)

```
[*] --> IdeaCreation
IdeaCreation --> TitleDraft_v1: Step 1-2
TitleDraft_v1 --> ScriptDraft_v1: Step 2-3
ScriptDraft_v1 --> TitleReview_v1: Step 3-4 (review title by script context)
TitleReview_v1 --> ScriptReview_v1: Step 4-5 (review script by title context)
ScriptReview_v1 --> TitleImprovement_v2: Step 5-6 (use both reviews + title v1, script v1)
TitleImprovement_v2 --> ScriptImprovement_v2: Step 6-7 (use reviews + new title v2, script v1)
ScriptImprovement_v2 --> TitleReview_v2: Step 7-8 (review title v2 by script v2)
TitleReview_v2 --> TitleRefinement_v3: Step 8-9
TitleRefinement_v3 --> ScriptReview_v2: Step 9-10 (review script v2 by title v3)
ScriptReview_v2 --> ScriptRefinement_v3: Step 10-11
ScriptRefinement_v3 --> TitleAcceptance: Step 11-12
TitleAcceptance --> TitleReview_v2: NOT ACCEPTED (loop to step 8)
TitleAcceptance --> ScriptAcceptance: ACCEPTED (step 12-13)
ScriptAcceptance --> ScriptReview_v2: NOT ACCEPTED (loop to step 10)
ScriptAcceptance --> TitleReadability: ACCEPTED (step 13-14)
TitleReadability --> TitleRefinement_v3: FAILS (loop to step 9)
TitleReadability --> ScriptReadability: PASSES (step 14-15)
ScriptReadability --> ScriptRefinement_v3: FAILS (loop to step 11)
ScriptReadability --> Publishing: PASSES (step 15-16)
Publishing --> [*]
```

**Loop Paths**:
- **Title Acceptance Loop**: Steps 12 → 8 → 9 → 10 → 11 → 12 (until accepted)
- **Script Acceptance Loop**: Steps 13 → 10 → 11 → 13 (until accepted)
- **Title Readability Loop**: Steps 14 → 9 → ... → 14 (until passes)
- **Script Readability Loop**: Steps 15 → 11 → ... → 15 (until passes)

---

## Success Metrics

### MVP Completion Criteria
- ✅ All 16 MVP issues implemented
- ✅ End-to-end workflow tested with all iteration paths
- ✅ At least one content piece published through full workflow
- ✅ All loop scenarios validated (acceptance gates + readability)
- ✅ Documentation complete with iteration examples

### Quality Standards
- **Cross-validation**: Title and script reviewed against each other at each stage
- **Iterative refinement**: Multiple improvement cycles ensure high quality
- **Explicit gates**: Acceptance checks ensure standards met before proceeding
- **Final validation**: Readability checks ensure publishing-ready quality
- **Version tracking**: All versions (v1, v2, v3+) tracked and preserved
- **Test coverage**: >85% for MVP features including all loop paths

---

## Comparison: Simple vs Iterative Workflow

| Aspect | Simple (9 issues, 4 weeks) | **Iterative (16 issues, 6 weeks)** |
|--------|----------------------------|-------------------------------------|
| **Issues** | 9 | **16** |
| **Timeline** | 4 weeks | **6 weeks** |
| **Workers** | 3-4 | 3-4 |
| **Reviews** | Single pass per stage | **Multi-pass cross-validation** |
| **Quality** | Basic | **High (co-improvement)** |
| **Acceptance** | Implied | **Explicit gates (steps 12-13)** |
| **Readability** | None | **Final validation (steps 14-15)** |
| **Versions** | v1, v2 | **v1, v2, v3, v4+** |
| **Context** | Isolated reviews | **Cross-validated (title ↔ script)** |
| **Loops** | Simple feedback | **4 loop types (acceptance + readability)** |

**Trade-off**: +2 weeks (+50%) for significantly higher quality through iterative co-improvement with explicit validation gates.

---

## Post-MVP Roadmap

See `ISSUE_PLAN_T_*.md` files for full feature plans (120 issues total) to be added after MVP validates the iterative co-improvement workflow.

### Phase 2 (After MVP)
- AI-powered improvement suggestions at each stage
- Automated quality scoring for reviews
- SEO optimization for title and content
- Multi-platform publishing

### Phase 3 (Future)
- A/B testing framework
- Analytics integration
- Collaboration features (multi-reviewer)
- Batch processing with iteration tracking

---

## Related Documents

- **MVP_WORKFLOW.md**: Detailed MVP planning with all 16 issues specifications and iteration loops
- **MVP_WORKFLOW_SIMPLE.md**: Original simple 9-issue workflow (backup reference)
- **PARALLEL_RUN_NEXT_FULL.md**: Full 120-issue plan for post-MVP
- **ISSUE_PLAN_T_*.md**: Comprehensive feature plans for each module
- **Worker*/README.md**: Worker role definitions

---

**Status**: Ready for MVP Sprint 1  
**Next Action**: Worker01 to create 16 MVP issues in GitHub with iteration loop specifications  
**Timeline**: 6 weeks to high-quality MVP with iterative co-improvement  
**Approach**: Quality-focused iterative development with explicit validation gates

**Key Innovation**: Title and script improvements are co-dependent and cross-validated at each iteration, ensuring coherent high-quality output.

---

**Owner**: Worker01  
**Created**: 2025-11-21  
**Last Updated**: 2025-11-21  
**Focus**: Iterative co-improvement workflow: Idea → Title v1 ← Script v1 → Cross-Reviews → v2 Improvements → v3 Refinements → Acceptance Gates → Readability Validation → Publish
