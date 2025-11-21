# MVP Workflow - Iterative Title-Script Co-Improvement

**Created**: 2025-11-21  
**Updated**: 2025-11-21  
**Status**: Planning  
**Approach**: Iterative Co-Improvement Workflow

---

## Overview

This document defines the **enhanced MVP workflow** with **iterative title-script co-improvement cycles** where title and script are refined together through multiple review and improvement stages, each validating against the other.

**Key Innovation**: Title and script improvements are **co-dependent** - each is reviewed and refined based on the other, creating a quality improvement cycle.

---

## MVP Workflow Sequence (14 Stages + Loops)

### Using Real Folder Names with Iterative Co-Improvement:

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
6. PrismQ.T.Title.Improvements (v2) ← Using reviews + original script + original title
       ↓
7. PrismQ.T.Script.Improvements (v2) ← Using reviews + original script + new title v2
       ↓
8. PrismQ.T.Rewiew.Title.ByScript (v2) ←──────────────────────┐
       ↓                                                       │
9. PrismQ.T.Title.Refinement (v3) ← Improve by review         │
       ↓                                                       │
10. PrismQ.T.Rewiew.Script.ByTitle (v2) ←─────────────┐       │
        ↓                                              │       │
11. PrismQ.T.Script.Refinement (v3) ← Improve by review       │
        ↓                                              │       │
12. Check: Is Title Accepted? ─NO──────────────────────┘       │
        ↓ YES                                                  │
13. Check: Is Script Accepted? ─NO─────────────────────────────┘
        ↓ YES
14. PrismQ.T.Rewiew.Title.Readability ←──────────┐
        ↓                                         │
        ├─FAILS─→ Return to Title.Refinement ────┘
        ↓ PASSES
15. PrismQ.T.Rewiew.Script.Readability (Voiceover) ←─┐
        ↓                                             │
        ├─FAILS─→ Return to Script.Refinement ───────┘
        ↓ PASSES
16. PrismQ.T.Publishing.Finalization
```

---

## Key Principles

### 1. Co-Dependent Improvement
- **Title reviewed by script**: Title is evaluated in context of script content
- **Script reviewed by title**: Script is evaluated in context of title promise
- **Cross-validation**: Each element validated against the other + original idea

### 2. Version Tracking
- **v1**: Initial drafts (from idea)
- **v2**: First improvement cycle (using initial reviews)
- **v3**: Second refinement cycle (using v2 reviews)
- **v4+**: Additional cycles if acceptance checks fail

### 3. Explicit Acceptance Gates
- **Title acceptance check** (step 12): Must pass before checking script
- **Script acceptance check** (step 13): Must pass before readability
- **Readability validation** (steps 14-15): Final quality gates

### 4. Context Preservation
- Original versions preserved throughout
- Reviews reference originals for context
- Improvements build on previous versions

---

## Detailed Stage Definitions

### Stage 1: PrismQ.T.Idea.Creation
**Goal**: Capture initial content idea  
**Folder**: `T/Idea/Creation/`  
**Worker**: Worker02  
**Effort**: 2 days

**MVP Issue: #MVP-001 - Idea Creation**
- **Input**: Text description of idea
- **Output**: Idea object with unique ID
- **Validation**: Not empty, basic format check
- **Storage**: Database with timestamp

---

### Stage 2: PrismQ.T.Title.Draft (v1)
**Goal**: Generate first title from idea  
**Folder**: `T/Title/Draft/`  
**Worker**: Worker13 (Prompt Master)  
**Effort**: 2 days

**MVP Issue: #MVP-002 - Title Draft v1**
- **Input**: Idea object
- **Output**: 3-5 title variants (v1)
- **Process**: AI generation using simple prompt
- **Context**: Based on idea only
- **Version**: v1 (initial)

---

### Stage 3: PrismQ.T.Script.Draft (v1)
**Goal**: Generate first script from idea and title v1  
**Folder**: `T/Script/Draft/`  
**Worker**: Worker02  
**Effort**: 3 days

**MVP Issue: #MVP-003 - Script Draft v1**
- **Input**: Idea + Title v1
- **Output**: Initial script (v1)
- **Structure**: Intro, body, conclusion
- **Context**: Based on idea + title v1
- **Version**: v1 (initial)

---

### Stage 4: PrismQ.T.Rewiew.Title.ByScript (v1)
**Goal**: Review title v1 against script v1 and original idea  
**Folder**: `T/Rewiew/Idea/`  
**Worker**: Worker10 (Review Master)  
**Effort**: 1 day

**MVP Issue: #MVP-004 - Title Review by Script & Idea**
- **Input**: Title v1, Script v1, Idea
- **Review Criteria**:
  - Does title match script content?
  - Does title reflect idea intent?
  - Is title engaging for script context?
  - Does title set correct expectations?
- **Output**: Review feedback for title
- **Next**: Used in stage 6 (Title Improvements v2)

**Cross-Validation**: Title evaluated with script as context, not in isolation.

---

### Stage 5: PrismQ.T.Rewiew.Script.ByTitle (v1)
**Goal**: Review script v1 against title v1 and original idea  
**Folder**: `T/Rewiew/Script/`  
**Worker**: Worker10 (Review Master)  
**Effort**: 1 day

**MVP Issue: #MVP-005 - Script Review by Title & Idea**
- **Input**: Script v1, Title v1, Idea
- **Review Criteria**:
  - Does script deliver on title promise?
  - Does script match idea intent?
  - Is script quality appropriate for title?
  - Does script support title claims?
- **Output**: Review feedback for script
- **Next**: Used in stage 7 (Script Improvements v2)

**Cross-Validation**: Script evaluated with title as context, not in isolation.

---

### Stage 6: PrismQ.T.Title.Improvements (v2)
**Goal**: Generate title v2 using reviews + original script + original title  
**Folder**: `T/Title/Improvements/`  
**Worker**: Worker13 (Prompt Master)  
**Effort**: 2 days

**MVP Issue: #MVP-006 - Title Improvements v2**
- **Input**: 
  - Title review feedback (from stage 4)
  - Script review feedback (from stage 5)
  - Original script v1
  - Original title v1
- **Process**: 
  - Analyze feedback on title
  - Consider script content and its review
  - Generate improved title variants
- **Output**: Title v2
- **Version**: v2 (first improvement)

**Key**: Uses **both reviews** + **original versions** for context.

---

### Stage 7: PrismQ.T.Script.Improvements (v2)
**Goal**: Generate script v2 using reviews + original script + new title v2  
**Folder**: `T/Script/Improvements/`  
**Worker**: Worker02  
**Effort**: 2 days

**MVP Issue: #MVP-007 - Script Improvements v2**
- **Input**:
  - Script review feedback (from stage 5)
  - Title review feedback (from stage 4)
  - Original script v1
  - **New title v2** (from stage 6)
- **Process**:
  - Analyze feedback on script
  - Consider new title v2 and its improvements
  - Revise script to match new title
- **Output**: Script v2
- **Version**: v2 (first improvement)

**Key**: Uses **new title v2** so script aligns with improved title.

---

### Stage 8: PrismQ.T.Rewiew.Title.ByScript (v2)
**Goal**: Review title v2 against script v2  
**Folder**: `T/Rewiew/Idea/`  
**Worker**: Worker10  
**Effort**: 1 day

**MVP Issue: #MVP-008 - Title Review v2**
- **Input**: Title v2, Script v2
- **Review**: Same criteria as stage 4, but for v2 versions
- **Output**: Feedback for title v2
- **Next**: Used in stage 9 (Title Refinement v3)

**Loop Point**: If title needs more work, cycles back here after stage 12.

---

### Stage 9: PrismQ.T.Title.Refinement (v3)
**Goal**: Refine title to v3 based on v2 review  
**Folder**: `T/Title/Refinement/`  
**Worker**: Worker13  
**Effort**: 1 day

**MVP Issue: #MVP-009 - Title Refinement v3**
- **Input**: Title v2, Review feedback (from stage 8)
- **Process**: Apply review feedback to refine title
- **Output**: Title v3
- **Version**: v3 (refinement)

**Return Path**: If stage 12 (acceptance check) fails, returns here for v4, v5, etc.

---

### Stage 10: PrismQ.T.Rewiew.Script.ByTitle (v2)
**Goal**: Review script v2 against newest title (v3)  
**Folder**: `T/Rewiew/Script/`  
**Worker**: Worker10  
**Effort**: 1 day

**MVP Issue: #MVP-010 - Script Review v2 by Title v3**
- **Input**: Script v2, Title v3 (latest)
- **Review**: Same criteria as stage 5, but with v2 script + v3 title
- **Output**: Feedback for script v2
- **Next**: Used in stage 11 (Script Refinement v3)

**Loop Point**: If script needs more work, cycles back here after stage 13.

---

### Stage 11: PrismQ.T.Script.Refinement (v3)
**Goal**: Refine script to v3 based on v2 review  
**Folder**: `T/Script/Improvements/` (refinement path)  
**Worker**: Worker02  
**Effort**: 2 days

**MVP Issue: #MVP-011 - Script Refinement v3**
- **Input**: Script v2, Review feedback (from stage 10), Title v3
- **Process**: Apply review feedback, ensure alignment with title v3
- **Output**: Script v3
- **Version**: v3 (refinement)

**Return Path**: If stage 13 (acceptance check) fails, returns here for v4, v5, etc.

---

### Stage 12: Title Acceptance Check
**Goal**: Verify title is ready to proceed  
**Folder**: `T/Rewiew/Idea/` (acceptance gate)  
**Worker**: Worker10  
**Effort**: 0.5 days

**MVP Issue: #MVP-012 - Title Acceptance Gate**
- **Input**: Title v3 (current version)
- **Check**: Is title accepted?
  - Quality meets standard
  - Aligns with script
  - No further changes needed
- **Output**: 
  - **ACCEPTED**: Proceed to stage 13
  - **NOT ACCEPTED**: Return to stage 8 (review v3 again → refine to v4)

**Critical Gate**: Must pass before checking script.

---

### Stage 13: Script Acceptance Check
**Goal**: Verify script is ready to proceed  
**Folder**: `T/Rewiew/Script/` (acceptance gate)  
**Worker**: Worker10  
**Effort**: 0.5 days

**MVP Issue: #MVP-013 - Script Acceptance Gate**
- **Input**: Script v3 (current version), Title v3 (accepted)
- **Check**: Is script accepted?
  - Quality meets standard
  - Delivers on title promise
  - No further changes needed
- **Output**:
  - **ACCEPTED**: Proceed to stage 14
  - **NOT ACCEPTED**: Return to stage 10 (review v3 again → refine to v4)

**Critical Gate**: Must pass before readability checks.

---

### Stage 14: PrismQ.T.Rewiew.Title.Readability
**Goal**: Final readability validation for title  
**Folder**: `T/Rewiew/Readability/`  
**Worker**: Worker10  
**Effort**: 0.5 days

**MVP Issue: #MVP-014 - Title Readability Review**
- **Input**: Title v3 (accepted version)
- **Check**: Readability validation
  - Clear and understandable
  - Appropriate length
  - No grammar/spelling issues
  - Engaging and scannable
- **Output**:
  - **PASSES**: Proceed to stage 15
  - **FAILS**: Return to stage 9 (Title Refinement) with readability feedback

**Final Quality Gate** for title before publishing.

---

### Stage 15: PrismQ.T.Rewiew.Script.Readability (Voiceover)
**Goal**: Final readability validation for script (voiceover quality)  
**Folder**: `T/Rewiew/Readability/`  
**Worker**: Worker10  
**Effort**: 0.5 days

**MVP Issue: #MVP-015 - Script Readability/Voiceover Review**
- **Input**: Script v3 (accepted version)
- **Check**: Readability and voiceover validation
  - Flows naturally when read aloud
  - Appropriate pacing
  - No tongue-twisters or awkward phrasing
  - Clear pronunciation
  - Natural speech patterns
- **Output**:
  - **PASSES**: Proceed to stage 16
  - **FAILS**: Return to stage 11 (Script Refinement) with readability feedback

**Final Quality Gate** for script before publishing.

---

### Stage 16: PrismQ.T.Publishing.Finalization
**Goal**: Publish approved and validated content  
**Folder**: `T/Publishing/Finalization/`  
**Worker**: Worker02  
**Effort**: 2 days

**MVP Issue: #MVP-016 - Publishing**
- **Input**: Title v3 (accepted + readable), Script v3 (accepted + readable)
- **Process**:
  - Mark as "published"
  - Record publication timestamp
  - Export to output format
  - Store published version
- **Output**: Published content
- **Status**: draft → published

---

## MVP Sprint Breakdown

### Sprint 1: Initial Drafts + Cross-Reviews (2 weeks)

#### Week 1: Foundation
- #MVP-001: Idea Creation (Worker02, 2d)
- #MVP-002: Title Draft v1 (Worker13, 2d)
- #MVP-003: Script Draft v1 (Worker02, 3d)

**Deliverable**: Idea → Title v1 → Script v1 working

#### Week 2: Cross-Review Cycle
- #MVP-004: Title Review by Script & Idea (Worker10, 1d)
- #MVP-005: Script Review by Title & Idea (Worker10, 1d)

**Deliverable**: Both title and script reviewed in context of each other

---

### Sprint 2: Improvement Cycle v2 (2 weeks)

#### Week 3: Generate v2 Versions
- #MVP-006: Title Improvements v2 (Worker13, 2d)
- #MVP-007: Script Improvements v2 (Worker02, 2d)
- #MVP-008: Title Review v2 (Worker10, 1d)

**Deliverable**: Title v2 + Script v2 generated and title v2 reviewed

#### Week 4: Refinement to v3
- #MVP-009: Title Refinement v3 (Worker13, 1d)
- #MVP-010: Script Review v2 by Title v3 (Worker10, 1d)
- #MVP-011: Script Refinement v3 (Worker02, 2d)

**Deliverable**: Title v3 + Script v3 refined

---

### Sprint 3: Validation & Publishing (2 weeks)

#### Week 5: Acceptance Gates + Readability
- #MVP-012: Title Acceptance Check (Worker10, 0.5d)
- #MVP-013: Script Acceptance Check (Worker10, 0.5d)
- #MVP-014: Title Readability (Worker10, 0.5d)
- #MVP-015: Script Readability/Voiceover (Worker10, 0.5d)

**Deliverable**: All acceptance gates + readability checks passing

**Buffer**: Allow time for iteration loops if acceptance checks fail

#### Week 6: Publishing
- #MVP-016: Publishing (Worker02, 2d)
- Testing: E2E validation of all paths (Worker04, 2d)
- Documentation: Complete user guide (Worker15, 2d)

**Deliverable**: Complete MVP with published content

---

## Iteration Loop Examples

### Example 1: Title Needs One More Pass
```
Stages 1-11: Complete
Stage 12: Title Acceptance Check → NOT ACCEPTED
  ↓ Loop back
Stage 8: Title Review v2 (now reviewing v3 as v3.1)
Stage 9: Title Refinement (v3 → v4)
Stage 12: Title Acceptance Check → ACCEPTED
Stage 13: Continue...
```

### Example 2: Script Needs Multiple Passes
```
Stages 1-12: Complete (Title accepted)
Stage 13: Script Acceptance Check → NOT ACCEPTED
  ↓ Loop back
Stage 10: Script Review (now reviewing v3 as v3.1)
Stage 11: Script Refinement (v3 → v4)
Stage 13: Script Acceptance Check → NOT ACCEPTED again
  ↓ Loop back again
Stage 10: Script Review (reviewing v4 as v4.1)
Stage 11: Script Refinement (v4 → v5)
Stage 13: Script Acceptance Check → ACCEPTED
Stage 14: Continue...
```

### Example 3: Readability Fails
```
Stages 1-13: Complete (Both accepted)
Stage 14: Title Readability → FAILS
  ↓ Loop back
Stage 9: Title Refinement (v3 → v3-readable)
Stage 14: Title Readability → PASSES
Stage 15: Script Readability → FAILS
  ↓ Loop back
Stage 11: Script Refinement (v3 → v3-readable)
Stage 15: Script Readability → PASSES
Stage 16: Publishing
```

---

## Worker Allocation

| Worker | Role | Stages | Effort |
|--------|------|--------|--------|
| **Worker02** | Python Dev | 1, 3, 7, 11, 16 | 11d |
| **Worker13** | Prompt Master | 2, 6, 9 | 5d |
| **Worker10** | Review Master | 4, 5, 8, 10, 12, 13, 14, 15 | 6d |
| **Worker04** | QA/Testing | Testing all paths | 4d |
| **Worker15** | Documentation | User guide, API docs | 4d |

**Total**: 30 days of work, ~6 weeks calendar time with 3-4 active workers

---

## Success Metrics

### MVP Completion Criteria
- ✅ All 16 MVP issues implemented
- ✅ At least one content piece through complete workflow
- ✅ All iteration loops tested (acceptance gates + readability)
- ✅ Documentation complete with loop examples

### Quality Standards
- Title and script validated against each other at each stage
- Multiple improvement cycles ensure high quality
- Acceptance gates ensure standards met
- Readability checks ensure publishing-ready quality

---

## Comparison: Simple vs Iterative Workflow

| Aspect | Simple (9 issues) | Iterative (16 issues) |
|--------|-------------------|------------------------|
| **Issues** | 9 | 16 |
| **Timeline** | 4 weeks | 6 weeks |
| **Reviews** | Single pass | Multi-pass cross-validation |
| **Quality** | Basic | High (co-improvement) |
| **Acceptance** | Implied | Explicit gates |
| **Readability** | None | Final validation |
| **Versions** | v1, v2 | v1, v2, v3, v4+ |
| **Context** | Isolated | Cross-validated |

**Trade-off**: +2 weeks for significantly higher quality through iterative co-improvement.

---

## Folder Structure (Verified)

All stages use real verified folders:
- ✅ `T/Idea/Creation/`
- ✅ `T/Title/Draft/` (v1)
- ✅ `T/Script/Draft/` (v1)
- ✅ `T/Rewiew/Idea/` (title reviews + acceptance)
- ✅ `T/Rewiew/Script/` (script reviews + acceptance)
- ✅ `T/Title/Improvements/` (v2)
- ✅ `T/Script/Improvements/` (v2, v3+)
- ✅ `T/Title/Refinement/` (v3+)
- ✅ `T/Rewiew/Readability/` (final quality gates)
- ✅ `T/Publishing/Finalization/`

---

## Post-MVP Enhancements

After MVP validates iterative workflow, add:
- AI-powered improvement suggestions
- Automated quality scoring
- SEO optimization
- Multi-format support
- Collaboration features
- Analytics and tracking

See `ISSUE_PLAN_T_*.md` for full feature roadmap (120 additional issues).

---

**Status**: Ready for MVP Sprint 1  
**Timeline**: 6 weeks to high-quality MVP  
**Approach**: Iterative co-improvement with explicit quality gates  
**Key Innovation**: Title and script refined together through cross-validation

---

**Owner**: Worker01  
**Created**: 2025-11-21  
**Updated**: 2025-11-21  
**Focus**: Quality through iteration
