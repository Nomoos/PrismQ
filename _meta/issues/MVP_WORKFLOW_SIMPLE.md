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

**Using Real Folder Names with Feedback Loops:**

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.Draft
    ↓
PrismQ.T.Review.Title (Title Review) ←────┐
    ↓                                      │
    ├─→ If changes needed ─────────────────┘
    ↓ (Flag as ready)
PrismQ.T.Script.Draft
    ↓
PrismQ.T.Review.Script (Script Review) ←──┐
    ↓                                      │
    ├─→ If changes needed → T.Script.Improvements ─┘
    ↓ (Flag as ready)
PrismQ.T.Review.Content (Final Content Review) ←─┐
    ↓                                             │
    ├─→ If changes needed → T.Script.Improvements ─┘
    │   (or back to T.Title.Refinement if title needs update)
    ↓ (Flag as ready)
PrismQ.T.Publishing.Finalization
```

**Feedback Loop Details:**

1. **Title Review Loop**: 
   - Title.Draft → Review.Title
   - If changes needed: return to Title.Draft
   - If ready: proceed to Script.Draft

2. **Script Review Loop**:
   - Script.Draft → Review.Script
   - If changes needed: Script.Improvements → Review.Script (loop)
   - If ready: proceed to Review.Content

3. **Final Content Review Loop**:
   - Review.Content reviews both script and title together
   - If script changes needed: Script.Improvements → Review.Content (loop)
   - If title changes needed: Title.Refinement → Review.Content (loop)
   - If ready: proceed to Publishing.Finalization

**Relationship to Full Workflow:**

The MVP simplifies the full workflow documented in `T/TITLE_SCRIPT_WORKFLOW.md`:
- **Idea Composite State** (Creation → Outline → Skeleton → Title) is simplified to:
  - MVP: Direct Creation → Title.Draft (skipping Outline & Skeleton for MVP)
  - Post-MVP: Add Idea.Outline and Idea.Skeleton stages
- **Review Stages** now include explicit feedback loops:
  - Title Review (new explicit stage)
  - Script Review with feedback loop
  - Content Review with feedback loops for both script and title
- **Script Improvements** maps to iterative Script.Draft → Review cycle
- **Publishing** uses `T/Publishing/Finalization` with SEO modules

**Folder Structure:**
- `T/Idea/Creation/` - Idea creation and capture
- `T/Title/Draft/` - Title generation
- `T/Review/Idea/` - Title review (reviews title quality)
- `T/Script/Draft/` - Script drafting
- `T/Review/Script/` - Script review (reviews script quality)
- `T/Script/Improvements/` - Script improvements
- `T/Title/Refinement/` - Title refinement
- `T/Review/Content/` - Final content review (script + title together)
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
   - MVP: ✅ **NOW INCLUDED** - Granular review dimensions after acceptance gates (Stages 14-20)
   - Script quality reviews (Grammar, Tone, Content, Consistency, Editing) + Final Readability

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
- Granular review modules (T/Review/Grammar, Readability, Tone, etc.)
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

### Stage 3: PrismQ.T.Review.Idea (Title Review)
**Goal**: Review title quality and flag as ready or request changes  
**Folder**: `T/Review/Idea/`  
**Owner**: Worker10, Worker12  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 1

#### MVP Issue: #MVP-003 - Title Review with Feedback Loop
- **Worker**: Worker10 (Review Master)
- **Effort**: 1 day
- **Module**: PrismQ.T.Review.Idea
- **Description**: Review title and provide feedback loop
- **Acceptance Criteria**:
  - Input: Title variants from Title.Draft
  - Review for clarity, engagement, accuracy
  - Status: approved / changes_requested
  - If changes_requested: return to Title.Draft with feedback
  - If approved: flag as ready, proceed to Script.Draft
  - Track review iterations

**Feedback Loop**:
- **Return path**: Review.Idea → Title.Draft (if changes needed)
- **Forward path**: Review.Idea → Script.Draft (if approved)

**Deferred to Post-MVP**:
- SEO scoring
- A/B test recommendations
- Platform-specific validation
- CTR prediction

---

### Stage 4: PrismQ.T.Script.Draft
**Goal**: Generate initial script from idea and approved title  
**Folder**: `T/Script/Draft/`  
**Owner**: Worker02, Worker13  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 2

#### MVP Issue: #MVP-004 - Basic Script Generator
- **Worker**: Worker02 (Python)
- **Effort**: 3 days
- **Module**: PrismQ.T.Script.Draft
- **Description**: Simple script generation from idea and approved title
- **Acceptance Criteria**:
  - Input: Idea + approved title
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

### Stage 5: PrismQ.T.Review.Script (Script Review with Feedback Loop)
**Goal**: Review script quality and flag as ready or request improvements  
**Folder**: `T/Review/Script/`  
**Owner**: Worker10, Worker12  
**Priority**: Critical  
**Timeline**: Sprint 1, Week 2

#### MVP Issue: #MVP-005 - Script Review with Feedback Loop
- **Worker**: Worker10 (Review Master)
- **Effort**: 2 days
- **Module**: PrismQ.T.Review.Script
- **Description**: Review script with feedback loop for improvements
- **Acceptance Criteria**:
  - Input: Script from Script.Draft
  - Review for: grammar, readability, tone, accuracy
  - Status: approved / changes_requested
  - If changes_requested: send to Script.Improvements with feedback
  - If approved: flag as ready, proceed to Review.Content
  - Track review iterations

**Feedback Loop**:
- **Return path**: Review.Script → Script.Improvements → Review.Script (loop until approved)
- **Forward path**: Review.Script → Review.Content (if approved)

**Deferred to Post-MVP**:
- Automated quality checks
- Multi-reviewer support
- Review analytics

**MVP Enhancement**: Granular review dimensions (Grammar, Readability, Tone, Content, Consistency, Editing) are now INCLUDED in MVP after acceptance gates.

---

### Stage 6: PrismQ.T.Script.Improvements
**Goal**: Apply reviewer feedback to script  
**Folder**: `T/Script/Improvements/`  
**Owner**: Worker02, Worker12  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 1

#### MVP Issue: #MVP-006 - Script Improvements
- **Worker**: Worker02 (Python)
- **Effort**: 2 days
- **Module**: PrismQ.T.Script.Improvements
- **Description**: Edit script based on review feedback
- **Acceptance Criteria**:
  - Input: Script + review feedback
  - Edit script content based on feedback
  - Save changes as new version
  - Link to review feedback
  - Mark as "ready for re-review"
  - Return to Review.Script for re-approval

**Feedback Loop**:
- **Return path**: Script.Improvements → Review.Script (for re-review)

**Deferred to Post-MVP**:
- AI-powered improvements
- Automatic section rewrite
- Change tracking/diff
- Collaborative editing
- Real-time updates

---

### Stage 7: PrismQ.T.Review.Content (Final Content Review)
**Goal**: Final review of script and title together before publishing  
**Folder**: `T/Review/Content/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 1

#### MVP Issue: #MVP-007 - Final Content Review with Feedback Loops
- **Worker**: Worker10 (Review Master)
- **Effort**: 1 day
- **Module**: PrismQ.T.Review.Content
- **Description**: Final approval gate with feedback loops
- **Acceptance Criteria**:
  - Input: Approved script + approved title
  - Review entire content package
  - Status: approved / script_needs_changes / title_needs_changes
  - If script_needs_changes: send to Script.Improvements
  - If title_needs_changes: send to Title.Refinement
  - If approved: flag as ready, proceed to Publishing
  - Final quality checklist (quality, completeness, consistency)

**Feedback Loops**:
- **Script changes**: Review.Content → Script.Improvements → Review.Script → Review.Content
- **Title changes**: Review.Content → Title.Refinement → Review.Idea → Review.Content
- **Forward path**: Review.Content → Publishing.Finalization (if approved)

**Deferred to Post-MVP**:
- Multi-level approvals
- Automated quality gates
- Publishing checklist templates
- Analytics integration

---

### Stage 8: PrismQ.T.Title.Refinement (Title Improvements)
**Goal**: Refine title based on final content review feedback  
**Folder**: `T/Title/Refinement/`  
**Owner**: Worker12, Worker13  
**Priority**: High  
**Timeline**: Sprint 2, Week 1 (if needed)

#### MVP Issue: #MVP-008 - Title Refinement
- **Worker**: Worker13 (Prompt Master)
- **Effort**: 1 day
- **Module**: PrismQ.T.Title.Refinement
- **Description**: Update title based on final review feedback
- **Acceptance Criteria**:
  - Input: Current title + feedback from Review.Content
  - Generate new title variants
  - Keep previous titles for comparison
  - Select best title
  - Return to Review.Idea for approval
  - Then to Review.Content for final check

**Feedback Loop**:
- **Return path**: Title.Refinement → Review.Idea → Review.Content

**Deferred to Post-MVP**:
- Advanced optimization
- SEO analysis
- A/B testing
- Performance tracking

---

### Quality Review Stages (After Acceptance Gates)

After content passes acceptance checks (Title and Script), it goes through multiple quality dimensions before final readability and publishing.

---

### Stage 9A: PrismQ.T.Review.Script.Grammar
**Goal**: Verify script grammar and technical correctness  
**Folder**: `T/Review/Grammar/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009A - Script Grammar Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Grammar
- **Description**: Grammar and language correctness check
- **Acceptance Criteria**:
  - Input: Accepted script
  - Check: Grammar, punctuation, spelling, syntax
  - Output: PASS → Tone Review / FAIL → Script.FromOriginalScriptAndReviewAndTitle

---

### Stage 9B: PrismQ.T.Review.Script.Tone
**Goal**: Verify emotional and stylistic tone consistency  
**Folder**: `T/Review/Tone/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009B - Script Tone Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Tone
- **Description**: Tone and emotional consistency check
- **Acceptance Criteria**:
  - Input: Grammar-approved script
  - Check: Emotional intensity, style alignment, voice consistency
  - Output: PASS → Content Review / FAIL → Script.FromOriginalScriptAndReviewAndTitle

---

### Stage 9C: PrismQ.T.Review.Script.Content
**Goal**: Verify narrative logic and story coherence  
**Folder**: `T/Review/Content/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009C - Script Content Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Content
- **Description**: Content logic and narrative quality check
- **Acceptance Criteria**:
  - Input: Tone-approved script
  - Check: Logic gaps, plot issues, character motivation, pacing, structure
  - Output: PASS → Consistency Review / FAIL → Script.FromOriginalScriptAndReviewAndTitle

---

### Stage 9D: PrismQ.T.Review.Script.Consistency
**Goal**: Verify internal continuity and logic  
**Folder**: `T/Review/Consistency/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009D - Script Consistency Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Consistency
- **Description**: Internal consistency and continuity check
- **Acceptance Criteria**:
  - Input: Content-approved script
  - Check: Character names, timeline, locations, detail matching, fact alignment
  - Output: PASS → Editing Review / FAIL → Script.FromOriginalScriptAndReviewAndTitle

---

### Stage 9E: PrismQ.T.Review.Script.Editing
**Goal**: Polish clarity, flow, and readability  
**Folder**: `T/Review/Editing/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009E - Script Editing Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Editing
- **Description**: Clarity and flow improvements check
- **Acceptance Criteria**:
  - Input: Consistency-approved script
  - Check: Sentence clarity, structure, redundancy, transitions, smooth readability
  - Output: PASS → Title Readability / FAIL → Script.FromOriginalScriptAndReviewAndTitle

---

### Stage 9F: PrismQ.T.Review.Title.Readability
**Goal**: Final readability validation for title  
**Folder**: `T/Review/Readability/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009F - Title Readability Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Readability
- **Description**: Title readability and voiceover validation
- **Acceptance Criteria**:
  - Input: Accepted title
  - Check: Clarity, scannability, grammar, length, engagement
  - Output: PASS → Script Readability / FAIL → Title.FromOriginalTitleAndReviewAndScript

---

### Stage 9G: PrismQ.T.Review.Script.Readability
**Goal**: Final voiceover readability validation for script  
**Folder**: `T/Review/Readability/`  
**Owner**: Worker10  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-009G - Script Readability Review
- **Worker**: Worker10 (Review Master)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Review.Readability
- **Description**: Script voiceover readability validation
- **Acceptance Criteria**:
  - Input: Editing-approved script
  - Check: Voiceover flow, pronunciation, natural speech, pacing, dramatic delivery
  - Output: PASS → Publishing / FAIL → Script.FromOriginalScriptAndReviewAndTitle

**Final Quality Gate**: This is the LAST review before GPT expert review!

---

### GPT Expert Review & Polish (Post Local-AI)

After all local AI reviews pass (Stages 9A-9G), content goes through a final GPT-based expert review and polish cycle:

---

### Stage 10A: PrismQ.T.Story.ExpertReview
**Goal**: GPT-based expert review of complete story  
**Folder**: `T/Story/ExpertReview/`  
**Owner**: Worker10 (GPT-4/GPT-5)  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-010A - GPT Expert Story Review
- **Worker**: Worker10 (with GPT Expert)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Story.ExpertReview
- **Description**: Holistic GPT-based expert review of complete story
- **Acceptance Criteria**:
  - Input: Title + Script + Audience + All local review results
  - GPT expert review (GPT-4 or GPT-5)
  - Holistic assessment: story coherence, audience fit, professional quality
  - Output: JSON with scores and improvement suggestions
  - Decision: Ready for publish OR needs expert polish

**GPT Expert Loop**: Uses advanced AI for final expert-level assessment.

---

### Stage 10B: PrismQ.T.Story.ExpertPolish
**Goal**: Apply GPT-based expert improvements  
**Folder**: `T/Story/ExpertPolish/`  
**Owner**: Worker10 (GPT-4/GPT-5)  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2 (if needed)

#### MVP Issue: #MVP-010B - GPT Expert Story Polish
- **Worker**: Worker10 (with GPT Expert)
- **Effort**: 0.5 days
- **Module**: PrismQ.T.Story.ExpertPolish
- **Description**: Apply expert-level improvements using GPT
- **Acceptance Criteria**:
  - Input: Current title/script + Expert review JSON
  - Apply high-priority improvements via GPT
  - Generate polished versions
  - Return to Stage 10A for verification
  - Max 2 iterations

**GPT Expert Polish**: Surgical improvements for professional quality.

---

### Stage 11: PrismQ.T.Publishing.Finalization
**Goal**: Publish approved content  
**Folder**: `T/Publishing/Finalization/`  
**Owner**: Worker02, Worker14  
**Priority**: Critical  
**Timeline**: Sprint 2, Week 2

#### MVP Issue: #MVP-011 - Basic Publishing
- **Worker**: Worker02 (Python)
- **Effort**: 2 days
- **Module**: PrismQ.T.Publishing.Finalization
- **Description**: Publish approved content
- **Acceptance Criteria**:
  - Input: Final approved script + title
  - Mark content as "published"
  - Record publication timestamp
  - Generate simple output (markdown file)
  - Store published version
  - Status: draft → published

**Deferred to Post-MVP**:
- Multi-platform publishing
- SEO metadata (Keywords, Tags, Categories)
- CMS integration
- Scheduling
- Analytics tracking

---

## MVP Sprint Breakdown

### Sprint 1: Core Creation Flow with Review Loops (2 weeks)

#### Week 1: Foundation + Title Review Loop
**Active Workers**: 3-4  
**Issues**: #MVP-001, #MVP-002, #MVP-003  
**Deliverable**: Idea → Title → Title Review (with feedback loop) working

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-001: Idea Creation | Worker02 | 2d | Planned |
| #MVP-002: Title Generator | Worker13 | 2d | Planned |
| #MVP-003: Title Review Loop | Worker10 | 1d | Planned |

**Parallel Work**:
- Worker15: Document MVP workflow with feedback loops
- Worker04: Setup test framework

**Feedback Loop Testing**:
- Test Title.Draft → Review.Idea → Title.Draft (revision cycle)
- Test Title.Draft → Review.Idea → Approved (happy path)

#### Week 2: Script Generation + Script Review Loop
**Active Workers**: 3-4  
**Issues**: #MVP-004, #MVP-005, #MVP-006  
**Deliverable**: Script generation + review with feedback loop working

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-004: Script Generator | Worker02 | 3d | Planned |
| #MVP-005: Script Review Loop | Worker10 | 2d | Planned |
| #MVP-006: Script Improvements | Worker02 | 2d | Planned |

**Parallel Work**:
- Worker15: API documentation
- Worker04: Integration tests for review loops

**Feedback Loop Testing**:
- Test Script.Draft → Review.Script → Script.Improvements → Review.Script (revision cycle)
- Test Script.Draft → Review.Script → Approved (happy path)

---

### Sprint 2: Final Review & Publishing (2 weeks)

#### Week 1: Final Content Review with Multi-path Feedback
**Active Workers**: 3-4  
**Issues**: #MVP-007, #MVP-008 (if needed)  
**Deliverable**: Final content review with script/title feedback loops

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-007: Final Content Review | Worker10 | 1d | Planned |
| #MVP-008: Title Refinement | Worker13 | 1d | As needed |

**Parallel Work**:
- Worker04: E2E tests with full feedback loops

**Feedback Loop Testing**:
- Test Review.Content → Script.Improvements → Review.Script → Review.Content (script revision)
- Test Review.Content → Title.Refinement → Review.Idea → Review.Content (title revision)
- Test Review.Content → Approved → Publishing (happy path)

#### Week 2: Publishing
**Active Workers**: 2-3  
**Issues**: #MVP-009  
**Deliverable**: End-to-end flow complete with all feedback loops

| Issue | Worker | Days | Status |
|-------|--------|------|--------|
| #MVP-009: Publishing | Worker02 | 2d | Planned |

**Parallel Work**:
- Worker15: User guide with feedback loop documentation
- Worker04: Final testing of all paths (happy + revision paths)

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
- ✅ **Review title with feedback loop** (NEW)
- ✅ Generate basic script
- ✅ **Review script with feedback loop** (NEW)
- ✅ Edit script based on feedback
- ✅ **Final content review with multi-path feedback** (NEW)
- ✅ Update title if needed (during final review)
- ✅ **Quality review stages** (NEW - Grammar, Tone, Content, Consistency, Editing)
- ✅ **Final readability reviews** (NEW - Title and Script voiceover validation)
- ✅ **GPT expert review and polish** (NEW - Final professional-level quality gate)
- ✅ Publish content

**Key MVP Features**: 
- **Local AI Loop**: Fast iterations through comprehensive quality reviews (Grammar → Tone → Content → Consistency → Editing → Readability)
- **GPT Expert Loop**: Final professional-level review and polish using GPT-4/GPT-5
- **Two-Tier Quality**: Cost-effective local AI for most improvements, premium GPT for final polish

### Nice to Have (Post-MVP)
- ⏳ AI-powered idea expansion
- ⏳ SEO optimization
- ⏳ Multi-platform publishing
- ⏳ Analytics and tracking
- ⏳ Collaboration features
- ⏳ A/B testing

---

## Testing Strategy

### MVP Testing Focus
1. **Happy Path**: Complete workflow from idea to publish (no revisions)
2. **Feedback Loop Paths**: Test all review → revision → re-review cycles
3. **Basic Validation**: Required fields, data types, review statuses
4. **State Transitions**: Correct workflow progression with loops
5. **Data Persistence**: Content saved and retrieved correctly through revisions

### Critical Test Scenarios
1. **Title Review Loop**: Title.Draft → Review.Idea (changes) → Title.Draft → Review.Idea (approved)
2. **Script Review Loop**: Script.Draft → Review.Script (changes) → Script.Improvements → Review.Script (approved)
3. **Final Review - Script Path**: Review.Content (script changes) → Script.Improvements → Review.Script → Review.Content (approved)
4. **Final Review - Title Path**: Review.Content (title changes) → Title.Refinement → Review.Idea → Review.Content (approved)
5. **Happy Path**: All stages approved on first review

### Test Coverage Goal
- **MVP Core**: 80%+ coverage
- **Happy Path**: 100% E2E test
- **Feedback Loop Paths**: 100% coverage for all loops
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
| T.Title | 3 (Draft + Review + Refinement) | 32 | 29 |
| T.Script | 3 (Draft + Improvements + Review) | 29 | 26 |
| T.Review | 2 (Script Review + Content Review) | 31 | 29 |
| T.Publish | 1 | - | - |
| **Total** | **9** (was 8) | **120** | **111** |

**MVP Enhancement**: Added explicit Title Review (#MVP-003) with feedback loop

### Timeline Comparison

| Approach | Issues | Timeline | Workers | Risk |
|----------|--------|----------|---------|------|
| **MVP** | 9 | 4 weeks | 3-4 | Low |
| **Full Plan** | 120 | 7 weeks | 10-12 | Medium |
| **Sequential** | 120 | 10 months | 1 | High |

**MVP includes feedback loops**: Each review stage can iterate multiple times before approval.

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
- Context: T/Review/
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
