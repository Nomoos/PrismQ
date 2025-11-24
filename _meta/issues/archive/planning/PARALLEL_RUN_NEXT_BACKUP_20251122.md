# PARALLEL_RUN_NEXT - MVP Sprint Execution

> **Note**: This is a streamlined sprint-focused document containing only sprints and commands.  
> **Full detailed version**: See `PARALLEL_RUN_NEXT_FULL.md` for comprehensive workflow explanations.  
> **Current state**: See `CURRENT_STATE.md` for implementation status assessment.

**Sprint**: Sprint 1-3 (7-8 weeks) - MVP Development  
**Date**: 2025-11-22  
**Status**: Sprint 1 Complete ✅ | Sprint 2 Ready to Start  
**Goal**: Build MVP with 26-stage iterative co-improvement workflow

**Sprint 1 Achievement**: Foundation complete - Idea → Title v1 → Script v1 → Cross-reviews working ✅  
**Sprint 2 Focus**: Implement improvement modules (v2/v3 generation)  
**Completed Issues Moved**: MVP-001 through MVP-005 + Documentation + Tests → moved to _meta/issues/done/

---

## Sprint 1: Foundation & Cross-Reviews (Weeks 1-2) ✅ COMPLETE

**Goal**: Idea → Title v1 → Script v1 → Cross-validation reviews  
**Timeline**: 2 weeks  
**Active Workers**: Worker02, Worker10, Worker13, Worker15, Worker04  
**Status**: ✅ ALL ISSUES COMPLETE (7/7)

### Completed Issues (Moved to _meta/issues/done/)

All Sprint 1 issues have been completed, reviewed, and moved to the done directory:

- ✅ **MVP-001**: T.Idea.Creation (Worker02) - Review: `done/MVP-001-REVIEW.md`
- ✅ **MVP-002**: T.Title.FromIdea (Worker13) - Review: `done/MVP-002-REVIEW.md`
- ✅ **MVP-003**: T.Script.FromIdeaAndTitle (Worker02) - Review: `done/MVP-003-REVIEW.md`
- ✅ **MVP-004**: T.Review.Title.ByScript (Worker10) - Review: `done/MVP-004-REVIEW.md`
- ✅ **MVP-005**: T.Review.Script.ByTitle (Worker10) - Review: `done/MVP-005-REVIEW.md`
- ✅ **MVP-DOCS**: MVP Workflow Documentation (Worker15) - Review: `done/MVP-DOCS-REVIEW.md`
- ✅ **MVP-TEST**: Test Framework (Worker04) - Review: `done/MVP-TEST-REVIEW.md`

**Achievement Summary**:
- Foundation pipeline working: Idea → Title v1 → Script v1
- Cross-review system complete: Title ↔ Script mutual reviews
- Comprehensive documentation (1033 lines EN + 548 lines CS)
- Test framework ready (49/49 tests passing, 100%)
- All acceptance criteria met
- Sprint 2 unblocked and ready to start

---

## Sprint 2: Improvement Cycle (Weeks 3-4)

**Goal**: Create improved v2 versions using cross-reviews, then refine to v3  
**Timeline**: 2 weeks  
**Active Workers**: Worker02, Worker10, Worker13  
**Status**: READY TO START - All Sprint 1 dependencies met ✅

---

### Week 3: Generate v2 Versions

**Deliverable**: Title v2 and script v2 generated with cross-context

#### Commands

```bash
# MVP-006: Title Improvements v2 (2 days) - READY TO START ✅
Worker13: Implement PrismQ.T.Title.FromOriginalTitleAndReviewAndScript
- Module: PrismQ.T.Title.FromOriginalTitleAndReviewAndScript
- Location: T/Title/FromOriginalTitleAndReviewAndScript/
- Dependencies: MVP-004 ✅, MVP-005 ✅ (needs both reviews - COMPLETE)
- Priority: Critical
- Effort: 2 days
- Status: READY TO START (All dependencies met)
- Acceptance Criteria:
  * Generate title v2 using feedback from both reviews
  * Use title v1, script v1, and both review feedbacks
  * Maintain engagement while improving alignment
  * Store v2 with reference to v1
  * Tests: Verify v2 addresses feedback from v1 reviews

# MVP-007: Script Improvements v2 (2 days)
Worker02: Implement PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle
- Module: PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle
- Location: T/Script/FromOriginalScriptAndReviewAndScript/
- Dependencies: MVP-006 (needs new title v2)
- Priority: Critical
- Effort: 2 days
- Status: BLOCKED (waiting for MVP-006)
- Acceptance Criteria:
  * Generate script v2 using both reviews + new title v2
  * Improve alignment with title v2
  * Address feedback from script review
  * Store v2 with reference to v1
  * Tests: Verify v2 addresses feedback and aligns with title v2

# MVP-008: Title Review v2 (1 day)
Worker10: Implement PrismQ.T.Review.Title.ByScript (v2) in T/Review/Title/
- Module: PrismQ.T.Review.Title.ByScript
- Dependencies: MVP-007 (needs both v2 versions)
- Priority: Critical
- Effort: 1 day
- Status: NOT STARTED
- Acceptance Criteria:
  * Review title v2 against script v2
  * Generate feedback for refinement
  * Compare improvements from v1 to v2
  * Output JSON format with feedback
  * Tests: Review sample v2 title/script pairs
```

---

### Week 4: Refinements to v3

**Deliverable**: ✅ Title v3 and script v3 refined and ready for acceptance gates

#### Commands

```bash
# MVP-009: Title Refinement v3 (1 day)
Worker13: Implement PrismQ.T.Title.FromOriginalTitleAndReviewAndScript (v3)
- Module: PrismQ.T.Title.FromOriginalTitleAndReviewAndScript
- Location: T/Title/FromOriginalTitleAndReviewAndScript/ (same module, handles v2→v3→v4+)
- Dependencies: MVP-008 (needs v2 review feedback)
- Priority: Critical
- Effort: 1 day
- Status: NOT STARTED
- Acceptance Criteria:
  * Refine title from v2 to v3 using feedback
  * Polish for clarity and engagement
  * Store v3 with reference to v2
  * Support versioning (v3, v4, v5, v6, v7, etc.)
  * Tests: Verify v3 incorporates v2 feedback

# MVP-010: Script Review v2 by Title v3 (1 day)
Worker10: Implement PrismQ.T.Review.Script.ByTitle (v2) in T/Review/Script/
- Module: PrismQ.T.Review.Script.ByTitle
- Dependencies: MVP-009 (needs title v3)
- Priority: Critical
- Effort: 1 day
- Status: NOT STARTED
- Acceptance Criteria:
  * Review script v2 against newest title v3
  * Generate feedback for refinement
  * Check alignment with updated title
  * Output JSON format with feedback
  * Tests: Review script v2 against title v3

# MVP-011: Script Refinement v3 (2 days)
Worker02: Implement PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle (v3)
- Module: PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle
- Location: T/Script/FromOriginalScriptAndReviewAndTitle/ (same module, handles v2→v3→v4+)
- Dependencies: MVP-010
- Priority: Critical
- Effort: 2 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Refine script from v2 to v3 using feedback
  * Ensure alignment with title v3
  * Polish narrative flow
  * Store v3 with reference to v2
  * Support versioning (v3, v4, v5, v6, v7, etc.)
  * Tests: Verify v3 incorporates feedback and aligns with title v3
```

---

## Sprint 3: Validation & Quality (Weeks 5-8)

**Goal**: Acceptance gates + comprehensive quality reviews + GPT expert review + publishing  
**Timeline**: 4 weeks  
**Active Workers**: Worker02, Worker10, Worker04, Worker15

---

### Week 5: Acceptance Gates + Quality Reviews (Part 1)

**Deliverable**: ✅ Acceptance gates passed + Grammar, Tone, Content reviews complete

#### Commands

```bash
# MVP-012: Title Acceptance Gate (0.5 days)
Worker10: Implement PrismQ.T.Review.Title.Acceptance in T/Review/Title/
- Module: PrismQ.T.Review.Title.Acceptance
- Dependencies: MVP-011 (needs latest title version)
- Priority: Critical
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check if title (latest version) meets acceptance criteria
  * Criteria: clarity, engagement, alignment with script
  * If ACCEPTED: proceed to MVP-013
  * If NOT ACCEPTED: loop back to MVP-008 (review → refine to next version)
  * Always uses newest title version
  * Tests: Test acceptance and rejection scenarios

# MVP-013: Script Acceptance Gate (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Acceptance in T/Review/Script/
- Module: PrismQ.T.Review.Script.Acceptance
- Dependencies: MVP-012 (title must be accepted first)
- Priority: Critical
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check if script (latest version) meets acceptance criteria
  * Criteria: completeness, coherence, alignment with title
  * If ACCEPTED: proceed to MVP-014
  * If NOT ACCEPTED: loop back to MVP-010 (review → refine to next version)
  * Always uses newest script version
  * Tests: Test acceptance and rejection scenarios

# MVP-014: Grammar Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Grammar in T/Review/Grammar/
- Module: PrismQ.T.Review.Script.Grammar
- Dependencies: MVP-013 (script must be accepted)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check grammar, punctuation, spelling, syntax, tense
  * Generate specific corrections with line references
  * If PASSES: proceed to MVP-015
  * If FAILS: return to Script refinement with feedback
  * Output JSON with issues and suggested fixes
  * Tests: Test with grammatically correct and incorrect scripts

# MVP-015: Tone Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Tone in T/Review/Tone/
- Module: PrismQ.T.Review.Script.Tone
- Dependencies: MVP-014 (grammar must pass)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check emotional intensity, style alignment, voice consistency
  * Evaluate tone appropriateness for content type
  * If PASSES: proceed to MVP-016
  * If FAILS: return to Script refinement with feedback
  * Output JSON with tone analysis
  * Tests: Test with various tone styles

# MVP-016: Content Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Content in T/Review/Content/
- Module: PrismQ.T.Review.Script.Content
- Dependencies: MVP-015 (tone must pass)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check for logic gaps, plot issues, character motivation, pacing
  * Verify narrative coherence
  * If PASSES: proceed to MVP-017
  * If FAILS: return to Script refinement with feedback
  * Output JSON with content issues
  * Tests: Test with coherent and incoherent scripts
```

---

### Week 6: Quality Reviews (Part 2) + Readability

**Deliverable**: ✅ All quality reviews + readability checks passing

#### Commands

```bash
# MVP-017: Consistency Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Consistency in T/Review/Consistency/
- Module: PrismQ.T.Review.Script.Consistency
- Dependencies: MVP-016 (content must pass)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check character names, timeline, locations, repeated details
  * Identify internal contradictions
  * If PASSES: proceed to MVP-018
  * If FAILS: return to Script refinement with feedback
  * Output JSON with consistency issues
  * Tests: Test with consistent and inconsistent scripts

# MVP-018: Editing Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Editing in T/Review/Editing/
- Module: PrismQ.T.Review.Script.Editing
- Dependencies: MVP-017 (consistency must pass)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Sentence rewrites, structural fixes, redundancy removal
  * Improve clarity and flow
  * If PASSES: proceed to MVP-019
  * If FAILS: return to Script refinement with feedback
  * Output JSON with editing suggestions
  * Tests: Test editing quality improvements

# MVP-019: Title Readability Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Title.Readability in T/Review/Readability/
- Module: PrismQ.T.Review.Title.Readability
- Dependencies: MVP-018 (editing must pass)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check clarity, length, engagement for voiceover
  * Evaluate pronunciation and flow
  * If PASSES: proceed to MVP-020
  * If FAILS: return to Title refinement with feedback
  * Output JSON with readability score and issues
  * Tests: Test with readable and difficult titles

# MVP-020: Script Readability Review (0.5 days)
Worker10: Implement PrismQ.T.Review.Script.Readability in T/Review/Readability/
- Module: PrismQ.T.Review.Script.Readability
- Dependencies: MVP-019 (title readability must pass)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Check natural flow, pronunciation, pacing for voiceover
  * Identify difficult passages
  * If PASSES: proceed to MVP-021
  * If FAILS: return to Script refinement with feedback
  * Output JSON with readability score and issues
  * Tests: Test with various script styles

# Quality Path Testing (2 days)
Worker04: Test all quality review paths
- Dependencies: MVP-017 through MVP-020
- Priority: High
- Effort: 2 days
- Status: NOT STARTED
- Deliverable: Comprehensive test suite for quality reviews
- Acceptance Criteria:
  * Test all quality review scenarios
  * Test individual review failures and recovery
  * Test multiple failures in sequence
  * Test loop back to refinement and re-review
  * Verify version tracking through loops
```

---

### Week 7-8: GPT Expert Review + Publishing

**Deliverable**: ✅ Complete MVP with expert review and publishing

#### Commands

```bash
# MVP-021: GPT Expert Story Review (0.5 days)
Worker10: Implement PrismQ.T.Story.ExpertReview in T/Story/ExpertReview/
- Module: PrismQ.T.Story.ExpertReview
- Dependencies: MVP-020 (all quality reviews passed)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Holistic assessment using GPT-4/GPT-5
  * Generate structured feedback (JSON format)
  * Evaluate overall quality and impact
  * If READY: proceed to MVP-023 (Publishing)
  * If IMPROVEMENTS NEEDED: proceed to MVP-022
  * Tests: Test GPT integration and feedback parsing

# MVP-022: GPT Expert Story Polish (0.5 days)
Worker10: Implement PrismQ.T.Story.ExpertPolish in T/Story/ExpertPolish/
- Module: PrismQ.T.Story.ExpertPolish
- Dependencies: MVP-021 (expert review with improvements needed)
- Priority: High
- Effort: 0.5 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Apply GPT-based expert improvements
  * Surgical changes for maximum impact
  * Return to MVP-021 for verification (max 2 iterations)
  * Store polished version
  * Tests: Test polish application and verification loop

# MVP-023: Publishing (2 days)
Worker02: Implement PrismQ.T.Publishing.Finalization in T/Publishing/Finalization/
- Module: PrismQ.T.Publishing.Finalization
- Dependencies: MVP-021 (expert review ready)
- Priority: Critical
- Effort: 2 days
- Status: NOT STARTED
- Acceptance Criteria:
  * Mark content as "published"
  * Export to output format (JSON, Markdown, etc.)
  * Store published version with all versions tracked
  * Generate publishing report
  * Tests: Test publishing workflow end-to-end

# E2E Testing (2 days)
Worker04: Complete end-to-end testing with all paths
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Status: NOT STARTED
- Deliverable: Full E2E test suite
- Acceptance Criteria:
  * Test happy path (all pass first time)
  * Test title/script acceptance loops
  * Test quality review failures and recoveries
  * Test readability loops
  * Test GPT expert review loop
  * Test multiple iterations (v4, v5, v6, v7, etc.)
  * Verify version tracking throughout

# Final Documentation (2 days)
Worker15: Complete user guide with all stages
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Status: NOT STARTED
- Deliverable: Complete user documentation
- Acceptance Criteria:
  * Document all 26 workflow stages
  * Include quality review criteria
  * Document iteration loop examples
  * Explain version tracking (v1-v7+)
  * Provide usage examples and tutorials
```

---

## Issue Quality Standards

All issues must meet these criteria:

### Size
- **Small**: 0.5-2 days maximum effort
- **Focused**: Single responsibility per issue
- **Testable**: Can be verified independently

### Acceptance Criteria
- **Specific**: Clear, measurable outcomes
- **Complete**: All requirements listed
- **Verifiable**: Tests can validate success

### Input/Output
- **Input**: Clearly defined data structures
- **Output**: Expected results documented
- **Examples**: Sample inputs and outputs provided

### Dependencies
- **Explicit**: All dependencies listed
- **Blocking**: Blocked by listed clearly
- **Order**: Execution sequence defined

### Tests
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows

---

## Sprint Summary

### Sprint 1 (Weeks 1-2) ✅ COMPLETE
- **Issues**: MVP-001 through MVP-005 + Documentation + Tests (7 issues)
- **Completed**: All 7 issues ✅
  - MVP-001: Idea Creation ✅
  - MVP-002: Title Generation ✅
  - MVP-003: Script Generation ✅
  - MVP-004: Title Review by Script ✅
  - MVP-005: Script Review by Title ✅
  - MVP-DOCS: Workflow Documentation ✅
  - MVP-TEST: Test Framework ✅
- **Progress**: 100% complete (7 of 7 done)
- **Reviews**: All issues reviewed and moved to _meta/issues/done/

### Sprint 2 (Weeks 3-4)
- **Issues**: MVP-006 through MVP-011 (6 issues)
- **Status**: READY TO START ✅ (MVP-006 unblocked)
- **Dependencies**: All Sprint 1 dependencies met ✅
- **Next Issue**: MVP-006 (Title v2) ready for Worker13

### Sprint 3 (Weeks 5-8)
- **Issues**: MVP-012 through MVP-023 (12 issues)
- **Status**: BLOCKED (waiting for Sprint 2)
- **Dependencies**: Requires all Sprint 2 issues complete

### Overall
- **Total Issues**: 23 MVP issues
- **Completed**: 7 issues (30%) ✅
- **Remaining**: 16 issues (70%)
- **Current Sprint**: Sprint 2 ready to begin
- **Estimated Remaining Time**: ~18 days of work, 5-6 weeks calendar time

---

## Critical Path

```
Sprint 1 ✅ → MVP-006 (ready) → MVP-007 → Sprint 2 complete → Sprint 3
  DONE         2 days            2 days      2 weeks         4 weeks
```

**Current Status**: Sprint 1 COMPLETE ✅ - Sprint 2 READY TO START ✅

---

**Status**: Sprint 1 Complete | Sprint 2 Ready  
**Next Action**: Worker13 begin MVP-006 (Title v2 generation)  
**Updated**: 2025-11-22  
**Owner**: Worker01
