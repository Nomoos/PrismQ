# PARALLEL_RUN_NEXT - MVP Sprint Execution

> **Note**: This is a streamlined sprint-focused document containing only sprints and commands.  
> **Full detailed version**: See `PARALLEL_RUN_NEXT_FULL.md` for comprehensive workflow explanations.  
> **Current state**: See `CURRENT_STATE.md` for implementation status assessment.  
> **Refactored**: 2025-11-22 - Simplified to 22 issues (from 26 stages), applied SOLID principles, MVP-focused

**Sprint**: Sprint 1-3 (7-8 weeks) - MVP Development  
**Date**: 2025-11-22 (Updated)  
**Status**: Sprint 1 Complete ✅ | Sprint 2 Complete ✅ | Sprint 3 Partial (5/11)  
**Goal**: Build MVP with 22-stage iterative co-improvement workflow (simplified from 26)

**Sprint 1 Achievement**: Foundation complete - Idea → Title v1 → Script v1 → Cross-reviews working ✅  
**Sprint 2 Achievement**: Improvement cycle complete - v2 and v3 generation working ✅  
**Sprint 3 Progress**: Acceptance gates + 3 quality reviews complete (5/11 - 45%) ⚠️  
**Completed Issues**: MVP-001 through MVP-016 (16 issues) → reviews in _meta/issues/done/  
**Remaining**: MVP-017 through MVP-022 (6 issues) - Quality reviews, Readability, Final review, Publishing

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

## Sprint 2: Improvement Cycle (Weeks 3-4) ✅ COMPLETE

**Goal**: Create improved v2 versions using cross-reviews, then refine to v3  
**Timeline**: 2 weeks  
**Active Workers**: Worker02, Worker10, Worker13  
**Status**: ✅ ALL ISSUES COMPLETE (6/6)

### Completed Issues (Moved to _meta/issues/done/)

All Sprint 2 issues have been completed and reviewed:

- ✅ **MVP-006**: T.Title v2 Generation (Worker13) - Review: `done/MVP-006-REVIEW.md`
- ✅ **MVP-007**: T.Script v2 Generation (Worker02) - Review: `done/MVP-007-REVIEW.md`
- ✅ **MVP-008**: T.Review.Title.ByScript v2 (Worker10) - Review: `done/MVP-008-REVIEW.md`
- ✅ **MVP-009**: T.Title v3 Refinement (Worker13) - Review: `done/MVP-009-REVIEW.md`
- ✅ **MVP-010**: T.Review.Script.ByTitle v2 (Worker10) - Review: `done/MVP-010-REVIEW.md`
- ✅ **MVP-011**: T.Script v3 Refinement (Worker02) - Review: `done/MVP-011-REVIEW.md`

**Achievement Summary**:
- v2 generation pipeline complete: Title v2 + Script v2
- v3 refinement working: Title v3 + Script v3
- Cross-review v2 system functional
- Iterative improvement cycle (v1→v2→v3→v4+) proven
- All acceptance criteria met
- Sprint 3 unblocked
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

## Sprint 3: Validation & Quality (Weeks 5-8) ⚠️ PARTIAL (5/11 Complete)

**Goal**: Acceptance gates + comprehensive quality reviews + final review + publishing  
**Timeline**: 4 weeks  
**Active Workers**: Worker02, Worker10, Worker04, Worker15  
**Status**: IN PROGRESS - Acceptance gates + 3 quality reviews complete

### Completed Issues (Moved to _meta/issues/done/)

Sprint 3 issues completed so far:

- ✅ **MVP-012**: T.Review.Title.Acceptance (Worker10) - Review: `done/MVP-012-REVIEW.md`
- ✅ **MVP-013**: T.Review.Script.Acceptance (Worker10) - Review: `done/MVP-013-REVIEW.md`
- ✅ **MVP-014**: T.Review.Script.Grammar (Worker10) - Review: `done/MVP-014-REVIEW.md`
- ✅ **MVP-015**: T.Review.Script.Tone (Worker10) - Review: `done/MVP-015-REVIEW.md`
- ✅ **MVP-016**: T.Review.Script.Content (Worker10) - Review: `done/MVP-016-REVIEW.md` (merged from main)

**Achievement Summary**:
- Acceptance gate system working (title + script)
- Grammar review operational
- Tone review operational
- Content review operational (merged from main)
- Loop-back logic implemented
- 5 of 12 Sprint 3 issues complete (42%)

---

### Remaining Sprint 3 Work (6 issues)

#### Quality Reviews (2 remaining)

```bash
# MVP-017: Consistency Review (0.5 days) - NOT STARTED ❌ (NEXT PRIORITY)
Worker10: Implement PrismQ.T.Review.Script.Consistency in T/Review/Consistency/
- Module: PrismQ.T.Review.Script.Consistency
- Dependencies: MVP-016 ✅ (content must pass - COMPLETE)
- Priority: HIGH
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Check character names, timeline, locations, contradictions
- Acceptance Criteria:
  * Validate character name consistency throughout script
  * Check timeline for logical sequence and contradictions
  * Verify location mentions are consistent
  * Detect repeated details and contradictions
  * Output JSON with specific consistency issues found
  * Pass/Fail decision: PASS → MVP-018, FAIL → refinement loop
  * Tests: Consistent and inconsistent script scenarios

# MVP-018: Editing Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Review.Script.Editing in T/Review/Editing/
- Module: PrismQ.T.Review.Script.Editing
- Dependencies: MVP-017 (consistency must pass)
- Priority: HIGH
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Sentence rewrites, structural fixes, redundancy removal
- Acceptance Criteria:
  * Identify sentences needing rewrites for clarity
  * Detect structural issues in script organization
  * Find and flag redundant content
  * Suggest specific editing improvements
  * Output JSON with editing recommendations
  * Pass/Fail decision: PASS → MVP-019, FAIL → refinement loop
  * Tests: Well-edited and poorly-edited script scenarios
```

#### Readability Reviews (2 remaining)

```bash
# MVP-019: Title Readability Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Review.Title.Readability in T/Review/Readability/
- Module: PrismQ.T.Review.Title.Readability
- Dependencies: MVP-018 (editing must pass)
- Priority: MEDIUM
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Check clarity, length, engagement for voiceover
- Acceptance Criteria:
  * Evaluate title clarity and understandability
  * Check title length (optimal for voiceover and platforms)
  * Assess engagement and hook effectiveness
  * Verify pronunciation difficulty
  * Calculate readability scores
  * Output JSON with readability metrics and issues
  * Pass/Fail decision: PASS → MVP-020, FAIL → title refinement loop
  * Tests: Readable and difficult-to-read title scenarios

# MVP-020: Script Readability Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Review.Script.Readability in T/Review/Readability/
- Module: PrismQ.T.Review.Script.Readability
- Dependencies: MVP-019 (title readability must pass)
- Priority: MEDIUM
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Check natural flow, pronunciation, pacing for voiceover
- Acceptance Criteria:
  * Evaluate natural flow for speaking/voiceover
  * Identify difficult-to-pronounce words or phrases
  * Check pacing (too fast/slow sections)
  * Calculate readability scores for audio
  * Detect awkward sentence constructions
  * Output JSON with readability metrics and problematic sections
  * Pass/Fail decision: PASS → MVP-021, FAIL → script refinement loop
  * Tests: Natural-flow and awkward-flow script scenarios
```

#### Final Review & Publishing (2 remaining)

```bash
# MVP-021: Final Story Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Story.FinalReview in T/Story/FinalReview/
- Module: PrismQ.T.Story.FinalReview
- Dependencies: MVP-020 (all quality reviews passed)
- Priority: HIGH
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Holistic final assessment before publishing
- Acceptance Criteria:
  * Perform comprehensive story evaluation (title + script together)
  * Check overall alignment between title and script
  * Verify all quality gates passed successfully
  * Generate final readiness assessment
  * Output JSON with final approval status and any recommendations
  * Pass/Fail decision: PASS → MVP-022 (publishing), FAIL → targeted refinement
  * Tests: Ready-to-publish and needs-improvement scenarios

# MVP-022: Publishing (1.5 days) - NOT STARTED ❌
Worker02: Implement PrismQ.T.Publishing.Finalization in T/Publishing/Finalization/
- Module: PrismQ.T.Publishing.Finalization
- Dependencies: MVP-021 (final review must pass)
- Priority: HIGH
- Effort: 1.5 days
- Status: NOT STARTED
- Purpose: Mark as published, export formats, generate publishing report
- Acceptance Criteria:
  * Mark content status as "published" in database
  * Export to multiple formats (JSON, Markdown, HTML)
  * Generate comprehensive publishing report
  * Store final version with complete version history
  * Record publication timestamp and metadata
  * Output publishing confirmation with export paths
  * Tests: End-to-end publishing workflow with various content types
```

#### Quality Reviews (2 remaining)

```bash
# MVP-017: Consistency Review (0.5 days) - NOT STARTED ❌ (NEXT PRIORITY)
Worker10: Implement PrismQ.T.Review.Script.Consistency in T/Review/Consistency/
- Module: PrismQ.T.Review.Script.Consistency
- Dependencies: MVP-016 ✅ (content must pass - COMPLETE)
- Priority: HIGH
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Check character names, timeline, locations, contradictions
- Acceptance Criteria:
  * Validate character name consistency throughout script
  * Check timeline for logical sequence and contradictions
  * Verify location mentions are consistent
  * Detect repeated details and contradictions
  * Output JSON with specific consistency issues found
  * Pass/Fail decision: PASS → MVP-018, FAIL → refinement loop
  * Tests: Consistent and inconsistent script scenarios

# MVP-018: Editing Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Review.Script.Editing in T/Review/Editing/
- Module: PrismQ.T.Review.Script.Editing
- Dependencies: MVP-017 (consistency must pass)
- Priority: HIGH
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Sentence rewrites, structural fixes, redundancy removal
- Acceptance Criteria:
  * Identify sentences needing rewrites for clarity
  * Detect structural issues in script organization
  * Find and flag redundant content
  * Suggest specific editing improvements
  * Output JSON with editing recommendations
  * Pass/Fail decision: PASS → MVP-019, FAIL → refinement loop
  * Tests: Well-edited and poorly-edited script scenarios
```

#### Readability Reviews (2 remaining)

```bash
# MVP-019: Title Readability Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Review.Title.Readability in T/Review/Readability/
- Module: PrismQ.T.Review.Title.Readability
- Dependencies: MVP-018 (editing must pass)
- Priority: MEDIUM
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Check clarity, length, engagement for voiceover
- Acceptance Criteria:
  * Evaluate title clarity and understandability
  * Check title length (optimal for voiceover and platforms)
  * Assess engagement and hook effectiveness
  * Verify pronunciation difficulty
  * Calculate readability scores
  * Output JSON with readability metrics and issues
  * Pass/Fail decision: PASS → MVP-020, FAIL → title refinement loop
  * Tests: Readable and difficult-to-read title scenarios

# MVP-020: Script Readability Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Review.Script.Readability in T/Review/Readability/
- Module: PrismQ.T.Review.Script.Readability
- Dependencies: MVP-019 (title readability must pass)
- Priority: MEDIUM
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Check natural flow, pronunciation, pacing for voiceover
- Acceptance Criteria:
  * Evaluate natural flow for speaking/voiceover
  * Identify difficult-to-pronounce words or phrases
  * Check pacing (too fast/slow sections)
  * Calculate readability scores for audio
  * Detect awkward sentence constructions
  * Output JSON with readability metrics and problematic sections
  * Pass/Fail decision: PASS → MVP-021, FAIL → script refinement loop
  * Tests: Natural-flow and awkward-flow script scenarios
```

#### Expert Review & Publishing (3 remaining)

```bash
# MVP-021: Final Story Review (0.5 days) - NOT STARTED ❌
Worker10: Implement PrismQ.T.Story.FinalReview in T/Story/FinalReview/
- Module: PrismQ.T.Story.FinalReview
- Dependencies: MVP-020 (all quality reviews passed)
- Priority: HIGH
- Effort: 0.5 days
- Status: NOT STARTED
- Purpose: Holistic final assessment before publishing
- Acceptance Criteria:
  * Perform comprehensive story evaluation (title + script together)
  * Check overall alignment between title and script
  * Verify all quality gates passed successfully
  * Generate final readiness assessment
  * Output JSON with final approval status and any recommendations
  * Pass/Fail decision: PASS → MVP-022 (publishing), FAIL → targeted refinement
  * Tests: Ready-to-publish and needs-improvement scenarios

# MVP-022: Publishing (1.5 days) - NOT STARTED ❌
Worker02: Implement PrismQ.T.Publishing.Finalization in T/Publishing/Finalization/
- Module: PrismQ.T.Publishing.Finalization
- Dependencies: MVP-021 (final review must pass)
- Priority: HIGH
- Effort: 1.5 days
- Status: NOT STARTED
- Purpose: Mark as published, export formats, generate publishing report
- Acceptance Criteria:
  * Mark content status as "published" in database
  * Export to multiple formats (JSON, Markdown, HTML)
  * Generate comprehensive publishing report
  * Store final version with complete version history
  * Record publication timestamp and metadata
  * Output publishing confirmation with export paths
  * Tests: End-to-end publishing workflow with various content types
```

---

## Parallel Execution Opportunities

### Currently Available (Can Start Now)
```bash
# MVP-017: Consistency Review - READY TO START ✅
Worker10: Implement Consistency Review
- All dependencies met (MVP-016 complete)
- Estimated: 0.5 days
- Can start immediately
```

### Blocked (Waiting for Dependencies)
```
MVP-018 → blocked by MVP-017
MVP-019 → blocked by MVP-018
MVP-020 → blocked by MVP-019
MVP-021 → blocked by MVP-020
MVP-022 → blocked by MVP-021
```

### No Parallel Opportunities
Due to sequential quality review dependencies, issues must be completed in order. No parallel work possible in current sprint.

---

## Issue Quality Standards

All issues must meet these criteria:

### Size
- **Small**: 0.5-2 days maximum effort
- **Focused**: Single responsibility per issue
- **Testable**: Can be verified independently

### SOLID Principles Application

Each issue is designed following SOLID principles:

#### Single Responsibility Principle (S)
- Each issue focuses on ONE specific module or feature
- Example: MVP-017 only handles consistency checking, not editing or grammar
- Clear, focused purpose statement for each issue

#### Open/Closed Principle (O)
- Modules are extensible without modification
- Review modules follow consistent patterns
- New review types can be added without changing existing ones

#### Liskov Substitution Principle (L)
- All review modules follow same interface contract
- Any review module can be used interchangeably in the pipeline
- Consistent input/output formats across similar modules

#### Interface Segregation Principle (I)
- Modules expose only necessary functionality
- Clean, minimal public APIs
- No forced dependencies on unused functionality

#### Dependency Inversion Principle (D)
- Modules depend on abstractions (review interface patterns)
- High-level workflow doesn't depend on low-level implementation details
- Loose coupling between pipeline stages

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
- **Reviews**: All issues reviewed in _meta/issues/done/

### Sprint 2 (Weeks 3-4) ✅ COMPLETE
- **Issues**: MVP-006 through MVP-011 (6 issues)
- **Completed**: All 6 issues ✅
  - MVP-006: Title v2 Generation ✅
  - MVP-007: Script v2 Generation ✅
  - MVP-008: Title Review v2 ✅
  - MVP-009: Title v3 Refinement ✅
  - MVP-010: Script Review v2 ✅
  - MVP-011: Script v3 Refinement ✅
- **Progress**: 100% complete (6 of 6 done)
- **Reviews**: All issues reviewed in _meta/issues/done/

### Sprint 3 (Weeks 5-8) ⚠️ PARTIAL (5/11 Complete)
- **Issues**: MVP-012 through MVP-022 (11 issues)
- **Completed**: 5 issues ✅
  - MVP-012: Title Acceptance Gate ✅
  - MVP-013: Script Acceptance Gate ✅
  - MVP-014: Grammar Review ✅
  - MVP-015: Tone Review ✅
  - MVP-016: Content Review ✅ (merged from main)
- **Remaining**: 6 issues ❌
  - MVP-017: Consistency Review (HIGH priority - NEXT)
  - MVP-018: Editing Review (HIGH priority)
  - MVP-019: Title Readability (MEDIUM priority)
  - MVP-020: Script Readability (MEDIUM priority)
  - MVP-021: Final Story Review (HIGH priority)
  - MVP-022: Publishing (HIGH priority)
- **Progress**: 45% complete (5 of 11 done)
- **Reviews**: Completed issues reviewed in _meta/issues/done/

### Overall
- **Total Issues**: 22 MVP issues (reduced from 23 - combined expert review into final review)
- **Completed**: 16 issues (73%) ✅
- **Remaining**: 6 issues (27%)
- **Current Sprint**: Sprint 3 (partial progress)
- **Estimated Remaining Time**: ~4-5 days of work, 1.5-2 weeks calendar time

---

## Critical Path

```
Sprint 1 ✅ → Sprint 2 ✅ → MVP-017 (next) → Quality Reviews → Publishing
  DONE         DONE        0.5 days      2 days           1.5 days
```

**Current Status**: Sprint 1 COMPLETE ✅ | Sprint 2 COMPLETE ✅ | Sprint 3 IN PROGRESS (45%)

**Next Priority**: MVP-017 (Consistency Review) - HIGH priority, blocks remaining quality reviews

---

**Status**: Sprint 3 In Progress (5/11 Complete)  
**Next Action**: Worker10 implement MVP-017 (Consistency Review)  
**Updated**: 2025-11-22 (Refactored - SOLID principles, MVP focus, simplified)  
**Owner**: Worker01  
**Progress Document**: See `PROGRESS_ASSESSMENT_2025-11-22.md` for detailed analysis  
**Integrity Check**: See `INTEGRITY_CHECK_2025-11-22.md` for post-merge verification
