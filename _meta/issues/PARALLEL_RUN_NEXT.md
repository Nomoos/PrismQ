# PARALLEL_RUN_NEXT - MVP Sprint Execution (Iterative Co-Improvement)

**Sprint**: Sprint 1-3 (7-8 weeks) - MVP Iterative Workflow  
**Date**: 2025-11-21  
**Updated**: 2025-11-22  
**Status**: Planning  
**Goal**: Build MVP with **iterative title-script co-improvement cycle** following: **Idea → Title v1 → Script v1 → Cross-Reviews → Title v2 ← Script v2 → Reviews v2 → Refinements v3 → Acceptance Gates → Quality Reviews (Grammar, Tone, Content, Consistency, Editing) → Readability Checks → GPT Expert Review → Publish**

---

## Enhanced MVP Approach

### Why Iterative Co-Improvement?
- **Higher quality**: Title and script validated against each other
- **Coherent output**: Changes to one element trigger re-validation of other
- **Explicit gates**: Acceptance checks before proceeding
- **Final validation**: Readability checks ensure publishing quality
- **Trade-off**: +2 weeks (6 vs 4) for significantly better quality

### Iterative Co-Improvement Workflow (26 Stages + Loops)

**Reference**: See `MVP_WORKFLOW.md` for complete documentation.

**Iterative Path** (26 stages with co-dependent improvement cycles and quality gates):

```
1. PrismQ.T.Idea.Creation
       ↓
2. PrismQ.T.Title.FromIdea (v1) ← from Idea
       ↓
3. PrismQ.T.Script.FromIdeaAndTitle (v1) ← from Idea + Title v1
       ↓
4. PrismQ.T.Review.Title.ByScript ← Review Title v1 by Script v1 + Idea
       ↓
5. PrismQ.T.Review.Script.ByTitle ← Review Script v1 by Title v1 + Idea
       ↓
6. PrismQ.T.Title.Improvements (v2) ← Using reviews + title v1, script v1
       ↓
7. PrismQ.T.Script.Improvements (v2) ← Using reviews + new title v2, script v1
       ↓
8. PrismQ.T.Review.Title.ByScript (v2) ←──────────────────────┐
       ↓                                                       │
9. PrismQ.T.Title.Refinement (v3) ← Improve by review         │
       ↓                                                       │
10. PrismQ.T.Review.Script.ByTitle (v2) ←─────────────┐       │
        ↓                                              │       │
11. PrismQ.T.Script.Refinement (v3) ← Improve by review       │
        ↓                                              │       │
12. Check: Is Title Accepted? ─NO──────────────────────┘       │
        ↓ YES                                                  │
13. Check: Is Script Accepted? ─NO─────────────────────────────┘
        ↓ YES
        
    ━━━━ Local AI Reviews (Stages 14-20) ━━━━
        
14. PrismQ.T.Review.Script.Grammar ←──────────────┐
        ↓                                         │
        ├─FAILS─→ Return to Script.Refinement ───┘
        ↓ PASSES
15. PrismQ.T.Review.Script.Tone ←────────────────┐
        ↓                                        │
        ├─FAILS─→ Return to Script.Refinement ──┘
        ↓ PASSES
16. PrismQ.T.Review.Script.Content ←─────────────┐
        ↓                                        │
        ├─FAILS─→ Return to Script.Refinement ──┘
        ↓ PASSES
17. PrismQ.T.Review.Script.Consistency ←─────────┐
        ↓                                        │
        ├─FAILS─→ Return to Script.Refinement ──┘
        ↓ PASSES
18. PrismQ.T.Review.Script.Editing ←─────────────┐
        ↓                                        │
        ├─FAILS─→ Return to Script.Refinement ──┘
        ↓ PASSES
19. PrismQ.T.Review.Title.Readability ←──────────┐
        ↓                                         │
        ├─FAILS─→ Return to Title.Refinement ────┘
        ↓ PASSES
20. PrismQ.T.Review.Script.Readability (Voiceover) ←─┐
        ↓                                             │
        ├─FAILS─→ Return to Script.Refinement ───────┘
        ↓ PASSES (All Local AI Reviews Complete)
        
    ━━━━ GPT Expert Review Loop (Stages 21-22) ━━━━
        
21. PrismQ.T.Story.ExpertReview (GPT-based) ←────────────┐
        ↓                                                 │
        ├─ Improvements Needed ─→ 22. Story.ExpertPolish ┘
        ↓ Ready for Publishing
23. PrismQ.T.Publishing.Finalization
```

**Key Innovations**:
- **Co-dependent improvement**: Title reviewed by script context, script by title context
- **Version tracking**: v1 (initial), v2 (first improvements), v3+ (refinements - can reach v4, v5, v6, v7, etc.)
- **Explicit acceptance gates**: Must pass checks before proceeding (steps 12-13)
- **Local AI quality reviews**: Grammar, Tone, Content, Consistency, Editing, Readability (steps 14-20)
- **GPT Expert review**: Final expert-level review and polish using GPT-4/GPT-5 (steps 21-22)
- **Context preservation**: Original versions preserved throughout
- **Latest version principle**: All loops use the newest/latest version of title and script, not hardcoded versions

**Folder Paths:**
- `T/Idea/Creation/` - Idea creation (step 1)
- `T/Title/FromIdea/` - Title v1 drafting (step 2)
- `T/Script/FromIdeaAndTitle/` - Script v1 drafting (step 3)
- `T/Review/Idea/` - Title reviews (steps 4, 8, 12, 19)
- `T/Review/Script/` - Script reviews (steps 5, 10, 13, 20)
- `T/Title/Improvements/` - Title v2 improvements (step 6)
- `T/Script/Improvements/` - Script v2 improvements + v3 refinements (steps 7, 11)
- `T/Title/Refinement/` - Title v3+ refinements (step 9)
- `T/Review/Grammar/` - Grammar review (step 14)
- `T/Review/Tone/` - Tone review (step 15)
- `T/Review/Content/` - Content review (step 16)
- `T/Review/Consistency/` - Consistency review (step 17)
- `T/Review/Editing/` - Editing review (step 18)
- `T/Review/Readability/` - Readability validation (steps 19-20)
- `T/Story/ExpertReview/` - GPT expert review (step 21)
- `T/Story/ExpertPolish/` - GPT expert polish (step 22)
- `T/Publishing/Finalization/` - Publishing (step 23)

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

Worker13: Implement #MVP-002 in T/Title/FromIdea/
- Module: PrismQ.T.Title.FromIdea
- Dependencies: #MVP-001 (can start in parallel)
- Priority: Critical
- Effort: 2 days
- Deliverable: Generate 3-5 title variants (v1) from idea only

Worker02: Implement #MVP-003 in T/Script/FromIdeaAndTitle/
- Module: PrismQ.T.Script.FromIdeaAndTitle
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
Worker10: Implement #MVP-004 in T/Review/Idea/
- Module: PrismQ.T.Review.Title.ByScript
- Dependencies: #MVP-003 (need both title v1 and script v1)
- Priority: Critical
- Effort: 1 day
- Deliverable: Review title v1 against script v1 and idea - generate feedback

Worker10: Implement #MVP-005 in T/Review/Script/
- Module: PrismQ.T.Review.Script.ByTitle
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

Worker10: Implement #MVP-008 in T/Review/Idea/
- Module: PrismQ.T.Review.Title.ByScript (v2)
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

Worker10: Implement #MVP-010 in T/Review/Script/
- Module: PrismQ.T.Review.Script.ByTitle (v2)
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

## Sprint 3: Validation & Quality Reviews (Weeks 5-6)

### Week 5: Acceptance Gates + Local AI Quality Reviews

**Goal**: Validate quality through acceptance gates and comprehensive AI quality reviews  
**Active Workers**: 2-3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker10** | #MVP-012 | 0.5d | Title Acceptance Gate |
| **Worker10** | #MVP-013 | 0.5d | Script Acceptance Gate |
| **Worker10** | #MVP-014 | 0.5d | Script Grammar Review |
| **Worker10** | #MVP-015 | 0.5d | Script Tone Review |
| **Worker10** | #MVP-016 | 0.5d | Script Content Review |
| **Worker10** | #MVP-017 | 0.5d | Script Consistency Review |
| **Worker10** | #MVP-018 | 0.5d | Script Editing Review |
| **Worker10** | #MVP-019 | 0.5d | Title Readability Review |
| **Worker10** | #MVP-020 | 0.5d | Script Readability/Voiceover Review |
| **Worker04** | Quality Tests | 2d | Test all quality review paths |

**Commands**:
```
Worker10: Implement #MVP-012 in T/Review/Idea/
- Module: PrismQ.T.Review.Title.Acceptance
- Dependencies: #MVP-011 (need latest title version)
- Priority: Critical
- Effort: 0.5 days
- Deliverable: Acceptance check for title (latest version - v3, v4, v5, v6, v7, etc.)
  - If ACCEPTED: proceed to #MVP-013
  - If NOT ACCEPTED: loop back to #MVP-008 (review newest version → refine to next version)
  - **Always uses newest title version**

Worker10: Implement #MVP-013 in T/Review/Script/
- Module: PrismQ.T.Review.Script.Acceptance
- Dependencies: #MVP-012 (title must be accepted first)
- Priority: Critical
- Effort: 0.5 days
- Deliverable: Acceptance check for script (latest version - v3, v4, v5, v6, v7, etc.)
  - If ACCEPTED: proceed to #MVP-014
  - If NOT ACCEPTED: loop back to #MVP-010 (review newest version → refine to next version)
  - **Always uses newest script version**

Worker10: Implement #MVP-014 in T/Review/Grammar/
- Module: PrismQ.T.Review.Script.Grammar
- Dependencies: #MVP-013 (script must be accepted)
- Priority: High
- Effort: 0.5 days
- Deliverable: Grammar and technical correctness review
  - Check grammar, punctuation, spelling, syntax, tense
  - If PASSES: proceed to #MVP-015
  - If FAILS: return to Script.FromQualityReviewAndPreviousScript with feedback

Worker10: Implement #MVP-015 in T/Review/Tone/
- Module: PrismQ.T.Review.Script.Tone
- Dependencies: #MVP-014 (grammar must pass)
- Priority: High
- Effort: 0.5 days
- Deliverable: Emotional and stylistic tone review
  - Check emotional intensity, style alignment, voice consistency
  - If PASSES: proceed to #MVP-016
  - If FAILS: return to Script.FromQualityReviewAndPreviousScript with feedback

Worker10: Implement #MVP-016 in T/Review/Content/
- Module: PrismQ.T.Review.Script.Content
- Dependencies: #MVP-015 (tone must pass)
- Priority: High
- Effort: 0.5 days
- Deliverable: Narrative logic and story coherence review
  - Check for logic gaps, plot issues, character motivation, pacing
  - If PASSES: proceed to #MVP-017
  - If FAILS: return to Script.FromQualityReviewAndPreviousScript with feedback

Worker10: Implement #MVP-017 in T/Review/Consistency/
- Module: PrismQ.T.Review.Script.Consistency
- Dependencies: #MVP-016 (content must pass)
- Priority: High
- Effort: 0.5 days
- Deliverable: Internal continuity and logic review
  - Check character names, timeline, locations, repeated details
  - If PASSES: proceed to #MVP-018
  - If FAILS: return to Script.FromQualityReviewAndPreviousScript with feedback

Worker10: Implement #MVP-018 in T/Review/Editing/
- Module: PrismQ.T.Review.Script.Editing
- Dependencies: #MVP-017 (consistency must pass)
- Priority: High
- Effort: 0.5 days
- Deliverable: Clarity, flow, and readability polish
  - Sentence rewrites, structural fixes, redundancy removal
  - If PASSES: proceed to #MVP-019
  - If FAILS: return to Script.FromQualityReviewAndPreviousScript with feedback

Worker10: Implement #MVP-019 in T/Review/Readability/
- Module: PrismQ.T.Review.Title.Readability
- Dependencies: #MVP-018 (editing must pass)
- Priority: High
- Effort: 0.5 days
- Deliverable: Title readability/voiceover validation
  - Check clarity, length, engagement
  - If PASSES: proceed to #MVP-020
  - If FAILS: return to Title.FromReadabilityReviewAndPreviousTitle with feedback

Worker10: Implement #MVP-020 in T/Review/Readability/
- Module: PrismQ.T.Review.Script.Readability
- Dependencies: #MVP-019 (title readability must pass)
- Priority: High
- Effort: 0.5 days
- Deliverable: Script readability/voiceover validation
  - Check natural flow, pronunciation, pacing for voiceover
  - If PASSES: proceed to #MVP-021 (GPT Expert Review)
  - If FAILS: return to Script.FromOriginalScriptAndReviewAndTitle with feedback

Worker04: Quality review path testing
- Dependencies: #MVP-014 through #MVP-020
- Priority: High
- Effort: 2 days
- Deliverable: Test all quality review scenarios:
  - All reviews pass (happy path)
  - Individual review failures and recovery
  - Multiple failures in sequence
  - Loop back to refinement and re-review
```

**Week 5 Deliverable**: ✅ All acceptance gates and local AI quality reviews implemented + tested

---

### Week 6: GPT Expert Review + Publishing

**Goal**: GPT expert review loop and final publishing  
**Active Workers**: 3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker10** | #MVP-021 | 0.5d | GPT Expert Story Review |
| **Worker10** | #MVP-022 | 0.5d | GPT Expert Story Polish |
| **Worker02** | #MVP-023 | 2d | Publishing |
| **Worker04** | E2E Tests | 2d | Test complete workflow paths |
| **Worker15** | Documentation | 2d | Complete user guide with all stages |

**Commands**:
```
Worker10: Implement #MVP-021 in T/Story/ExpertReview/
- Module: PrismQ.T.Story.ExpertReview
- Dependencies: #MVP-020 (all local AI reviews passed)
- Priority: High
- Effort: 0.5 days
- Deliverable: GPT-based expert review of complete story
  - Holistic assessment using GPT-4/GPT-5
  - Generate structured feedback (JSON format)
  - If READY: proceed to #MVP-023 (Publishing)
  - If IMPROVEMENTS NEEDED: proceed to #MVP-022 (Expert Polish)

Worker10: Implement #MVP-022 in T/Story/ExpertPolish/
- Module: PrismQ.T.Story.ExpertPolish
- Dependencies: #MVP-021 (expert review with improvements needed)
- Priority: High
- Effort: 0.5 days
- Deliverable: Apply GPT-based expert improvements
  - Surgical changes for maximum impact
  - Return to #MVP-021 for verification (max 2 iterations)

Worker02: Implement #MVP-023 in T/Publishing/Finalization/
- Module: PrismQ.T.Publishing.Finalization
- Dependencies: #MVP-021 (expert review ready) or #MVP-020 (if skipping expert review)
- Priority: Critical
- Effort: 2 days
- Deliverable: Publish approved and validated content
  - Mark as "published"
  - Export to output format
  - Store published version with all versions tracked

Worker04: Complete E2E testing with all paths
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Deliverable: Full test suite covering:
  - Happy path (all pass first time)
  - Title/script acceptance loops
  - Quality review failures and recoveries
  - Readability loops
  - GPT expert review loop
  - Multiple iterations through complete workflow

Worker15: Complete user guide with all stages
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Deliverable: Complete documentation including:
  - All 26 workflow stages explained
  - Quality review criteria and feedback handling
  - GPT expert review process
  - Iteration loop examples
  - Version tracking explanation (v1, v2, v3, v4, v5, v6, v7, etc.)
```

**Week 6 Deliverable**: ✅ Complete MVP with 26-stage iterative co-improvement workflow fully functional

---

## MVP Issues Summary

| Issue | Module | Stage | Worker | Effort | Description |
|-------|--------|-------|--------|--------|-------------|
| #MVP-001 | PrismQ.T.Idea.Creation | Idea | Worker02 | 2d | Basic idea capture |
| #MVP-002 | PrismQ.T.Title.FromIdea | Title v1 | Worker13 | 2d | Title generation from idea |
| #MVP-003 | PrismQ.T.Script.FromIdeaAndTitle | Script v1 | Worker02 | 3d | Script generation from idea + title v1 |
| #MVP-004 | PrismQ.T.Review.Title.ByScript | **Title Review by Script** | Worker10 | 1d | Review title v1 against script v1 + idea |
| #MVP-005 | PrismQ.T.Review.Script.ByTitle | **Script Review by Title** | Worker10 | 1d | Review script v1 against title v1 + idea |
| #MVP-006 | PrismQ.T.Title.Improvements | Title v2 | Worker13 | 2d | Title v2 using cross-reviews + title v1, script v1 |
| #MVP-007 | PrismQ.T.Script.Improvements | Script v2 | Worker02 | 2d | Script v2 using cross-reviews + new title v2, script v1 |
| #MVP-008 | PrismQ.T.Review.Title.ByScript | **Title Review v2** | Worker10 | 1d | Review title v2 against script v2 |
| #MVP-009 | PrismQ.T.Title.Refinement | Title v3+ | Worker13 | 1d | Refine title to v3, v4, v5, v6, v7, etc. (newest version) |
| #MVP-010 | PrismQ.T.Review.Script.ByTitle | **Script Review v2+** | Worker10 | 1d | Review script (latest) against title (latest) |
| #MVP-011 | PrismQ.T.Script.Refinement | Script v3+ | Worker02 | 2d | Refine script to v3, v4, v5, v6, v7, etc. (newest version) |
| #MVP-012 | PrismQ.T.Review.Title.Acceptance | **Acceptance Gate** | Worker10 | 0.5d | Check if title (latest version) is accepted (loop if not) |
| #MVP-013 | PrismQ.T.Review.Script.Acceptance | **Acceptance Gate** | Worker10 | 0.5d | Check if script (latest version) is accepted (loop if not) |
| #MVP-014 | PrismQ.T.Review.Script.Grammar | **Grammar Review** | Worker10 | 0.5d | Verify grammar and technical correctness |
| #MVP-015 | PrismQ.T.Review.Script.Tone | **Tone Review** | Worker10 | 0.5d | Verify emotional and stylistic tone |
| #MVP-016 | PrismQ.T.Review.Script.Content | **Content Review** | Worker10 | 0.5d | Verify narrative logic and coherence |
| #MVP-017 | PrismQ.T.Review.Script.Consistency | **Consistency Review** | Worker10 | 0.5d | Verify internal continuity |
| #MVP-018 | PrismQ.T.Review.Script.Editing | **Editing Review** | Worker10 | 0.5d | Polish clarity and flow |
| #MVP-019 | PrismQ.T.Review.Title.Readability | **Title Readability** | Worker10 | 0.5d | Final title readability/voiceover validation |
| #MVP-020 | PrismQ.T.Review.Script.Readability | **Script Readability** | Worker10 | 0.5d | Final script readability/voiceover validation |
| #MVP-021 | PrismQ.T.Story.ExpertReview | **GPT Expert Review** | Worker10 | 0.5d | GPT-based expert story review |
| #MVP-022 | PrismQ.T.Story.ExpertPolish | **GPT Expert Polish** | Worker10 | 0.5d | Apply GPT-based expert improvements |
| #MVP-023 | PrismQ.T.Publishing.Finalization | **Publish** | Worker02 | 2d | Publishing approved + validated content |

**Total**: 23 issues, 24 days of work, 6-7 weeks calendar time with 3-4 workers

**Key Features**:
- **Co-dependent improvement**: Title and script reviewed against each other (steps 4-5, 8, 10)
- **Version tracking**: v1 (initial), v2 (improved), v3+ (refined - can reach v4, v5, v6, v7, etc.)
- **Explicit acceptance gates**: Must pass before proceeding (steps 12-13)
- **Local AI quality reviews**: Grammar, Tone, Content, Consistency, Editing (steps 14-18)
- **Final readability validation**: Ensures publishing quality (steps 19-20)
- **GPT expert review**: Holistic expert-level assessment and polish (steps 21-22)
- **Iteration loops**: Return to refinement if any check fails
- **Latest version principle**: All loops always use the newest version
- **Iteration loops**: Return to refinement if acceptance/readability fails
- **Latest version principle**: All loops always use the newest/latest version of title and script

**Folder Paths:**
- `T/Idea/Creation/` (step 1)
- `T/Title/FromIdea/` (step 2)
- `T/Script/FromIdeaAndTitle/` (step 3)
- `T/Review/Idea/` (steps 4, 8, 12, 19)
- `T/Review/Script/` (steps 5, 10, 13, 20)
- `T/Title/Improvements/` (step 6)
- `T/Script/Improvements/` (steps 7, 11)
- `T/Title/Refinement/` (step 9)
- `T/Review/Grammar/` (step 14)
- `T/Review/Tone/` (step 15)
- `T/Review/Content/` (step 16)
- `T/Review/Consistency/` (step 17)
- `T/Review/Editing/` (step 18)
- `T/Review/Readability/` (steps 19-20)
- `T/Story/ExpertReview/` (step 21)
- `T/Story/ExpertPolish/` (step 22)
- `T/Publishing/Finalization/` (step 23)

---

## Workflow State Machine (Enhanced Iterative Co-Improvement)

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
ScriptAcceptance --> GrammarReview: ACCEPTED (step 13-14)
GrammarReview --> ScriptRefinement_v3: FAILS (loop to step 11)
GrammarReview --> ToneReview: PASSES (step 14-15)
ToneReview --> ScriptRefinement_v3: FAILS (loop to step 11)
ToneReview --> ContentReview: PASSES (step 15-16)
ContentReview --> ScriptRefinement_v3: FAILS (loop to step 11)
ContentReview --> ConsistencyReview: PASSES (step 16-17)
ConsistencyReview --> ScriptRefinement_v3: FAILS (loop to step 11)
ConsistencyReview --> EditingReview: PASSES (step 17-18)
EditingReview --> ScriptRefinement_v3: FAILS (loop to step 11)
EditingReview --> TitleReadability: PASSES (step 18-19)
TitleReadability --> TitleRefinement_v3: FAILS (loop to step 9)
TitleReadability --> ScriptReadability: PASSES (step 19-20)
ScriptReadability --> ScriptRefinement_v3: FAILS (loop to step 11)
ScriptReadability --> ExpertReview: PASSES (step 20-21)
ExpertReview --> ExpertPolish: IMPROVEMENTS NEEDED (step 21-22)
ExpertPolish --> ExpertReview: POLISHED (re-check at step 21, max 2 iterations)
ExpertReview --> Publishing: READY (step 21-23)
Publishing --> [*]
```

**Loop Paths**:
- **Title Acceptance Loop**: Steps 12 → 8 → 9 → 10 → 11 → 12 (until accepted) - versions increment: v3 → v4 → v5 → v6 → v7, etc.
- **Script Acceptance Loop**: Steps 13 → 10 → 11 → 13 (until accepted) - versions increment: v3 → v4 → v5 → v6 → v7, etc.
- **Quality Review Loops**: Steps 14-18 → 11 (script refinement) → re-test quality review (until passes)
- **Title Readability Loop**: Steps 19 → 9 (title refinement) → ... → 19 (until passes)
- **Script Readability Loop**: Steps 20 → 11 (script refinement) → ... → 20 (until passes)
- **GPT Expert Loop**: Steps 21 → 22 (polish) → 21 (re-check, max 2 iterations)
- **Important**: All loops use the newest/latest version of title and script, not hardcoded versions

---

## Success Metrics

### MVP Completion Criteria
- ✅ All 23 MVP issues implemented
- ✅ End-to-end workflow tested with all iteration paths
- ✅ At least one content piece published through full workflow
- ✅ All loop scenarios validated (acceptance gates + quality reviews + readability + GPT expert)
- ✅ Documentation complete with all 26 stages and iteration examples

### Quality Standards
- **Cross-validation**: Title and script reviewed against each other at each stage
- **Iterative refinement**: Multiple improvement cycles ensure high quality
- **Explicit gates**: Acceptance checks ensure standards met before proceeding
- **Local AI quality reviews**: Grammar, Tone, Content, Consistency, Editing validated (steps 14-18)
- **Final validation**: Title and script readability checks ensure publishing-ready quality (steps 19-20)
- **GPT expert review**: Holistic expert-level assessment and polish using GPT-4/GPT-5 (steps 21-22)
- **Version tracking**: All versions (v1, v2, v3+) tracked and preserved
- **Test coverage**: >85% for MVP features including all loop paths

---

## Comparison: Simple vs Iterative Workflow

| Aspect | Simple (9 issues, 4 weeks) | **Enhanced Iterative (23 issues, 7-8 weeks)** |
|--------|----------------------------|------------------------------------------------|
| **Issues** | 9 | **23** |
| **Timeline** | 4 weeks | **7-8 weeks** |
| **Workers** | 3-4 | 3-4 |
| **Reviews** | Single pass per stage | **Multi-pass cross-validation** |
| **Quality** | Basic | **Highest (co-improvement + AI + GPT expert)** |
| **Acceptance** | Implied | **Explicit gates (steps 12-13)** |
| **Quality Reviews** | None | **5 AI dimensions (Grammar, Tone, Content, Consistency, Editing)** |
| **Readability** | None | **Final validation (steps 19-20)** |
| **Expert Review** | None | **GPT-4/GPT-5 expert review + polish (steps 21-22)** |
| **Versions** | v1, v2 | **v1, v2, v3, v4+** |
| **Context** | Isolated reviews | **Cross-validated (title ↔ script)** |
| **Loops** | Simple feedback | **7 loop types (acceptance + 5 quality + readability + expert)** |

**Trade-off**: +3-4 weeks (+75-100%) for significantly higher quality through iterative co-improvement with explicit validation gates, comprehensive AI quality reviews, and GPT expert assessment.

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
**Next Action**: Worker01 to create 23 MVP issues in GitHub with complete specifications including quality review and GPT expert stages  
**Timeline**: 7-8 weeks to highest-quality MVP with iterative co-improvement, AI quality reviews, and GPT expert assessment  
**Approach**: Quality-focused iterative development with explicit validation gates and comprehensive review layers

**Key Innovation**: Title and script improvements are co-dependent and cross-validated at each iteration, with comprehensive AI quality reviews (Grammar, Tone, Content, Consistency, Editing), final readability validation, and GPT expert review ensuring coherent highest-quality output.

---

**Owner**: Worker01  
**Created**: 2025-11-21  
**Last Updated**: 2025-11-22  
**Focus**: Enhanced iterative co-improvement workflow: Idea → Title v1 ← Script v1 → Cross-Reviews → v2 Improvements → v3 Refinements → Acceptance Gates → AI Quality Reviews → Readability Validation → GPT Expert Review → Publish
