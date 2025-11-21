# MVP Workflow - Minimal Viable Product Issue Plan

**Created**: 2025-11-21  
**Updated**: 2025-11-21  
**Status**: Planning  
**Approach**: Iterative MVP Development

---

## MVP Workflow Overview

This document defines the **Minimum Viable Product (MVP)** workflow for the Text (T) pipeline, focusing on a streamlined, iterative approach to content creation.

**Reference**: See `T/TITLE_SCRIPT_WORKFLOW.md` for complete detailed workflow documentation.

### MVP Workflow Sequence

**Using Real Folder Names (Simplified for MVP):**

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.Draft
    ↓
PrismQ.T.Script.Draft
    ↓
PrismQ.T.Rewiew.Script (Initial Review)
    ↓
PrismQ.T.Script.Improvements
    ↓
PrismQ.T.Title.Refinement (Title Improvements)
    ↓
PrismQ.T.Rewiew.Content (Final Review)
    ↓
PrismQ.T.Publishing.Finalization
```

**Relationship to Full Workflow:**

The MVP simplifies the full workflow documented in `T/TITLE_SCRIPT_WORKFLOW.md`:
- **Idea Composite State** (Creation → Outline → Skeleton → Title) is simplified to:
  - MVP: Direct Creation → Title.Draft (skipping Outline & Skeleton for MVP)
  - Post-MVP: Add Idea.Outline and Idea.Skeleton stages
- **Script Review** uses existing `T/Rewiew` modules (Script, Content, etc.)
- **Script Improvements** maps to iterative Script.Draft → Review cycle
- **Publishing** uses `T/Publishing/Finalization` with SEO modules

**Folder Structure:**
- `T/Idea/Creation/` - Idea creation and capture
- `T/Title/Draft/` - Title generation
- `T/Script/Draft/` - Script drafting
- `T/Rewiew/Script/` - Script review
- `T/Script/Improvements/` - Script improvements
- `T/Title/Refinement/` - Title refinement
- `T/Rewiew/Content/` - Content review
- `T/Publishing/Finalization/` - Publishing

---

## MVP Philosophy

### Key Principles
1. **Start Simple**: Build minimal working features first
2. **Iterative Improvement**: Multiple review and improvement cycles
3. **Sequential Flow**: Clear progression through states
4. **Quick Feedback**: Fast iteration loops
5. **Incremental Value**: Each stage adds value

### MVP vs Full Feature Set
- **MVP**: Core workflow that produces publishable content
- **Full Features**: Advanced features added after MVP validates workflow
- **Focus**: Speed to first published content

### MVP Simplifications from Full Workflow

Based on `T/TITLE_SCRIPT_WORKFLOW.md`, the MVP simplifies:

1. **Idea Composite State**:
   - Full: Idea.Creation → Idea.Outline → Idea.Skeleton → Idea.Title
   - MVP: Idea.Creation → Title.Draft (direct path)
   - Deferred: Idea.Outline and Idea.Skeleton stages

2. **Review Stages**:
   - Full: Multiple review modules (Grammar, Readability, Tone, Content, Consistency, Editing)
   - MVP: Simplified review at Script and Content stages
   - Deferred: Granular review dimensions (grammar, readability, tone separately)

3. **Script Approval**:
   - Full: ScriptDraft → ScriptReview → ScriptApproved → TextPublishing
   - MVP: ScriptDraft → Review → Improvements → Review → Publishing
   - Deferred: Formal "approved" state with version locking

4. **Publishing Process**:
   - Full: SEO (Keywords, Tags, Categories) + Finalization
   - MVP: Basic finalization only
   - Deferred: Comprehensive SEO optimization modules

**Post-MVP Enhancement Path**:
After MVP validates the basic workflow, expand with:
- Idea.Outline creation for better structure
- Idea.Skeleton framework development
- Granular review modules (T/Rewiew/Grammar, Readability, Tone, etc.)
- Formal approval states and version locking
- Comprehensive SEO optimization (T/Publishing/SEO with Keywords, Tags, Categories)

---

## Phase 1: MVP Core Workflow (Sprint 1-2)

### Stage 1: PrismQ.T.Idea.Creation
**Goal**: Create basic idea from inspiration  
**Folder**: `T/Idea/Creation/`  
**Owner**: Worker02, Worker12  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 1

#### MVP Issue: #MVP-001 - Basic Idea Creation
- **Worker**: Worker02 (Python)
- **Effort**: 2 days
- **Module**: PrismQ.T.Idea.Creation
- **Description**: Create simple idea capture and storage
- **Acceptance Criteria**:
  - Input: Text description of idea
  - Store idea in database
  - Assign unique ID
  - Basic validation (not empty)
  - CLI interface for testing

**Deferred to Post-MVP**:
- AI-powered expansion
- Multi-source inspiration
- Quality scoring
- Batch processing

---

### Stage 2: PrismQ.T.Title.Draft
**Goal**: Generate initial title options  
**Folder**: `T/Title/Draft/`  
**Owner**: Worker12, Worker13  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 1

#### MVP Issue: #MVP-002 - Basic Title Generator
- **Worker**: Worker13 (Prompt Master)
- **Effort**: 2 days
- **Module**: PrismQ.T.Title.Draft
- **Description**: Simple AI title generation
- **Acceptance Criteria**:
  - Input: Idea object
  - Generate 3-5 title variants
  - Basic prompt template
  - Store in database
  - Return titles as list

**Deferred to Post-MVP**:
- SEO optimization
- A/B testing
- Platform-specific variants
- Performance tracking
- Advanced scoring

---

### Stage 3: PrismQ.T.Script.Draft
**Goal**: Generate initial script from idea and title  
**Folder**: `T/Script/Draft/`  
**Owner**: Worker02, Worker13  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 2

#### MVP Issue: #MVP-003 - Basic Script Generator
- **Worker**: Worker02 (Python)
- **Effort**: 3 days
- **Module**: PrismQ.T.Script.Draft
- **Description**: Simple script generation from idea
- **Acceptance Criteria**:
  - Input: Idea + selected title
  - Generate basic script structure (intro, body, conclusion)
  - Use simple prompt template
  - Store in database
  - Basic formatting (paragraphs)

**Deferred to Post-MVP**:
- Multi-format support
- Style transfer
- Advanced templates
- Section rewriter
- Collaboration features

---

### Stage 4: PrismQ.T.Rewiew.Script (Initial Review)
**Goal**: Basic review and feedback collection  
**Folder**: `T/Rewiew/Script/`  
**Owner**: Worker10, Worker12  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 2

#### MVP Issue: #MVP-004 - Simple Review System
- **Worker**: Worker10 (Review Master)
- **Effort**: 2 days
- **Module**: PrismQ.T.Rewiew.Script
- **Description**: Basic manual review workflow
- **Acceptance Criteria**:
  - Review status: pending/approved/changes_requested
  - Simple feedback text field
  - Reviewer can approve or request changes
  - State transitions tracked
  - Notification to author

**Deferred to Post-MVP**:
- Inline comments
- Automated checks (grammar, plagiarism)
- Multi-reviewer support
- Review criteria framework
- Review analytics

---

### Stage 5: PrismQ.T.Script.Improvements
**Goal**: Apply reviewer feedback to script  
**Folder**: `T/Script/Improvements/`  
**Owner**: Worker02, Worker12  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 1

#### MVP Issue: #MVP-005 - Manual Script Editing
- **Worker**: Worker02 (Python)
- **Effort**: 2 days
- **Module**: PrismQ.T.Script.Improvements
- **Description**: Simple script editing interface
- **Acceptance Criteria**:
  - Edit script content
  - Save changes as new version
  - Link to review feedback
  - Mark as "ready for re-review"
  - Version history (simple list)

**Deferred to Post-MVP**:
- AI-powered improvements
- Automatic section rewrite
- Change tracking/diff
- Collaborative editing
- Real-time updates

---

### Stage 6: PrismQ.T.Title.Refinement (Title Improvements)
**Goal**: Refine title based on script changes  
**Folder**: `T/Title/Refinement/`  
**Owner**: Worker12, Worker13  
**Priority**: High  
**Timeline**: Sprint 2, Week 1

#### MVP Issue: #MVP-006 - Title Update
- **Worker**: Worker13 (Prompt Master)
- **Effort**: 1 day
- **Module**: PrismQ.T.Title.Refinement
- **Description**: Simple title regeneration
- **Acceptance Criteria**:
  - Input: Updated script
  - Generate new title variants
  - Keep previous titles for comparison
  - Select best title
  - Update content record

**Deferred to Post-MVP**:
- Advanced optimization
- SEO analysis
- A/B testing
- Performance tracking

---

### Stage 7: PrismQ.T.Rewiew.Content (Final Review)
**Goal**: Final approval before publishing  
**Folder**: `T/Rewiew/Content/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 1

#### MVP Issue: #MVP-007 - Final Review Approval
- **Worker**: Worker10 (Review Master)
- **Effort**: 1 day
- **Module**: PrismQ.T.Rewiew.Content
- **Description**: Final approval gate
- **Acceptance Criteria**:
  - Reviewer marks as "approved" or "needs changes"
  - Simple checklist (quality, completeness)
  - If approved: move to publish queue
  - If rejected: return to improvements
  - Approval timestamp recorded

**Deferred to Post-MVP**:
- Multi-level approvals
- Automated quality gates
- Publishing checklist
- Analytics integration

---

### Stage 8: PrismQ.T.Publishing.Finalization
**Goal**: Publish approved content  
**Folder**: `T/Publishing/Finalization/`  
**Owner**: Worker02, Worker14  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-008 - Basic Publishing
- **Worker**: Worker02 (Python)
- **Effort**: 2 days
- **Module**: PrismQ.T.Publishing.Finalization
- **Description**: Simple content publishing
- **Acceptance Criteria**:
  - Mark content as "published"
  - Record publication timestamp
  - Generate simple output (markdown file)
  - Store published version
  - Status: draft → published

**Deferred to Post-MVP**:
- Multi-platform publishing
- SEO metadata
- CMS integration
- Scheduling
- Analytics tracking

---

## MVP Sprint Breakdown

### Sprint 1: Core Creation Flow (2 weeks)

#### Week 1: Foundation
**Active Workers**: 3-4  
**Issues**: #MVP-001, #MVP-002  
**Deliverable**: Idea → Title generation working

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-001: Idea Creation | Worker02 | 2d | Planned |
| #MVP-002: Title Generator | Worker13 | 2d | Planned |

**Parallel Work**:
- Worker15: Document MVP workflow
- Worker04: Setup test framework

#### Week 2: Script & Review
**Active Workers**: 3-4  
**Issues**: #MVP-003, #MVP-004  
**Deliverable**: Script generation + basic review

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-003: Script Generator | Worker02 | 3d | Planned |
| #MVP-004: Review System | Worker10 | 2d | Planned |

**Parallel Work**:
- Worker15: API documentation
- Worker04: Integration tests

---

### Sprint 2: Iteration & Publishing (2 weeks)

#### Week 1: Improvements
**Active Workers**: 3-4  
**Issues**: #MVP-005, #MVP-006, #MVP-007  
**Deliverable**: Improvement cycle working

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-005: Script Editing | Worker02 | 2d | Planned |
| #MVP-006: Title Update | Worker13 | 1d | Planned |
| #MVP-007: Final Review | Worker10 | 1d | Planned |

#### Week 2: Publishing
**Active Workers**: 2-3  
**Issues**: #MVP-008  
**Deliverable**: End-to-end flow complete

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-008: Publishing | Worker02 | 2d | Planned |

**Parallel Work**:
- Worker15: User guide
- Worker04: E2E tests

---

## MVP Success Criteria

### Must Have (MVP)
- ✅ Create idea from text input
- ✅ Generate title variants
- ✅ Generate basic script
- ✅ Review and provide feedback
- ✅ Edit script based on feedback
- ✅ Update title if needed
- ✅ Final approval gate
- ✅ Publish content

### Nice to Have (Post-MVP)
- ⏳ AI-powered idea expansion
- ⏳ SEO optimization
- ⏳ Automated quality checks
- ⏳ Multi-platform publishing
- ⏳ Analytics and tracking
- ⏳ Collaboration features
- ⏳ A/B testing

---

## Testing Strategy

### MVP Testing Focus
1. **Happy Path**: Complete workflow from idea to publish
2. **Basic Validation**: Required fields, data types
3. **State Transitions**: Correct workflow progression
4. **Data Persistence**: Content saved and retrieved correctly

### Test Coverage Goal
- **MVP Core**: 80%+ coverage
- **Happy Path**: 100% E2E test
- **Critical Paths**: Unit + integration tests

---

## Post-MVP Feature Roadmap

### Phase 2: Enhanced Quality (Sprint 3-4)
- AI-powered script improvements
- Grammar and spelling checks
- Readability scoring
- Plagiarism detection
- SEO analysis

### Phase 3: Optimization (Sprint 5-6)
- A/B testing framework
- Performance tracking
- Analytics integration
- Title optimization
- Multi-format support

### Phase 4: Collaboration (Sprint 7-8)
- Multi-reviewer workflows
- Inline comments
- Real-time editing
- Version control
- Team coordination

### Phase 5: Automation (Sprint 9+)
- Batch processing
- Scheduled publishing
- Multi-platform distribution
- Automated workflows
- Integration with A/V pipelines

---

## MVP vs Full Plan Comparison

### Issue Count Comparison

| Module | MVP Issues | Full Plan | Deferred |
|--------|------------|-----------|----------|
| T.Idea | 1 | 28 | 27 |
| T.Title | 2 | 32 | 30 |
| T.Script | 2 | 29 | 27 |
| T.Review | 2 | 31 | 29 |
| T.Publish | 1 | - | - |
| **Total** | **8** | **120** | **113** |

### Timeline Comparison

| Approach | Issues | Timeline | Workers | Risk |
|----------|--------|----------|---------|------|
| **MVP** | 8 | 4 weeks | 3-4 | Low |
| **Full Plan** | 120 | 7 weeks | 10-12 | Medium |
| **Sequential** | 120 | 10 months | 1 | High |

---

## MVP Benefits

### Speed to Market
- **4 weeks** to working product
- **First content published** in 1 month
- **Validate workflow** before building features

### Reduced Risk
- **Smaller scope**: Less to go wrong
- **Focus**: Core value only
- **Feedback**: Early user testing

### Learning Opportunity
- **Discover issues**: Real-world usage
- **Prioritize features**: Based on actual needs
- **Iterate**: Informed decisions

### Resource Efficiency
- **3-4 workers**: Not 10-12
- **Simple coordination**: Fewer dependencies
- **Lower cost**: Fewer person-hours

---

## Transition to Full Features

### After MVP Launch
1. **Collect Feedback**: From initial users
2. **Measure Usage**: Which features needed most
3. **Prioritize**: Based on data, not assumptions
4. **Iterate**: Add features incrementally

### Feature Addition Criteria
- **User Demand**: Requested by users
- **Value**: Clear benefit to workflow
- **Effort**: Reasonable implementation time
- **Complexity**: Doesn't break MVP

---

## Commands for MVP Sprint 1

### Week 1 Commands

```bash
Worker02: Implement #MVP-001 - Basic Idea Creation
- Context: T/Idea/
- Dependencies: None
- Priority: Critical
- Effort: 2 days
- Deliverable: Idea capture and storage working

Worker13: Implement #MVP-002 - Basic Title Generator
- Context: T/Title/
- Dependencies: #MVP-001 (can start in parallel)
- Priority: Critical
- Effort: 2 days
- Deliverable: Title generation from idea working

Worker15: Document MVP workflow
- Context: _meta/docs/
- Dependencies: None
- Priority: High
- Effort: 2 days
- Deliverable: MVP workflow documentation

Worker04: Setup test framework
- Context: T/_meta/tests/
- Dependencies: None
- Priority: High
- Effort: 2 days
- Deliverable: Test infrastructure ready
```

### Week 2 Commands

```bash
Worker02: Implement #MVP-003 - Basic Script Generator
- Context: T/Script/
- Dependencies: #MVP-001, #MVP-002
- Priority: Critical
- Effort: 3 days
- Deliverable: Script generation from idea+title working

Worker10: Implement #MVP-004 - Simple Review System
- Context: T/Rewiew/
- Dependencies: #MVP-003 (can start in parallel on design)
- Priority: Critical
- Effort: 2 days
- Deliverable: Review workflow functional

Worker15: Create API documentation
- Context: T/*/docs/
- Dependencies: Implementation progress
- Priority: Medium
- Effort: 2 days
- Deliverable: API docs for MVP features

Worker04: Create integration tests
- Context: T/_meta/tests/
- Dependencies: #MVP-001, #MVP-002
- Priority: High
- Effort: 2 days
- Deliverable: Integration test suite
```

---

## Issue Templates for MVP

### MVP Issue Template

```markdown
# Issue #MVP-XXX: [Feature Name]

**Type**: MVP Core Feature
**Worker**: WorkerXX
**Priority**: Critical/High
**Effort**: X days
**Sprint**: Sprint X, Week X

## Description
[Simple description of MVP feature]

## MVP Scope
[What's included in MVP]

## Deferred to Post-MVP
[What's NOT in MVP but planned later]

## Acceptance Criteria
- [ ] Criterion 1 (must be simple and testable)
- [ ] Criterion 2
- [ ] Criterion 3

## Dependencies
- Issue #XXX (if any)

## Test Requirements
- [ ] Unit tests
- [ ] Integration test
- [ ] Happy path E2E test

## Documentation
- [ ] API documentation
- [ ] User guide section
```

---

**Status**: Ready for MVP Sprint 1  
**Next Action**: Worker01 to create 8 MVP issues  
**Timeline**: 4 weeks to working product  
**Approach**: Iterative, value-focused, risk-minimized

---

**Owner**: Worker01  
**Created**: 2025-11-21  
**Last Updated**: 2025-11-21  
**Approach**: MVP-First Development
