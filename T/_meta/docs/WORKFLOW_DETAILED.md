# PrismQ.T Detailed Workflow Documentation

**Complete Iterative Workflow for Text Content Creation with Review Cycles**

## Overview

This document describes the detailed, iterative workflow for the PrismQ.T (Text Generation Pipeline) module. The workflow includes multiple review and refinement cycles to ensure high-quality text content production.

## Complete Workflow Sequence

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Story.From.Idea (creates 10 Story objects per Idea)
    ↓
PrismQ.T.Title.From.Idea
    ↓
PrismQ.T.Content.From.Idea.Title
    ↓
PrismQ.T.Review.Title.From.Content.Idea
    ↓
PrismQ.T.Review.Content.From.Title.Idea
    ↓
PrismQ.T.Review.Title.From.Content
    ├─ if not accepted → PrismQ.T.Title.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Content.From.Title
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Local AI Quality Reviews
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
PrismQ.T.Review.Content.Grammar
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Content.Tone
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Content.Content
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Content.Consistency
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Content.Editing
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Title.Readability
    ├─ if not accepted → PrismQ.T.Title.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Content.Readability
    ├─ if not accepted → PrismQ.T.Content.From.Title.Review.Content
    │                      ↓
    │                   PrismQ.T.Review.Title.From.Content (loop back)
    └─ if accepted → continue
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPT Expert Review and Polish Loop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
PrismQ.T.Story.Review
    ├─ if not accepted → PrismQ.T.Story.Polish
    │                      ↓
    │                   PrismQ.T.Story.Review (loop back)
    └─ if accepted → continue to Publishing
```

## Detailed Stage Descriptions

### Stage 1: PrismQ.T.Idea.Creation

**Purpose**: Initial idea creation and capture

**Location**: `T/Idea/Creation/`

**Input**:
- User-provided concept or inspiration
- Target audience information
- Content goals

**Output**:
- Structured idea document
- Core concept definition
- Target audience profile

**Transitions To**: PrismQ.T.Story.From.Idea

---

### Stage 1.5: PrismQ.T.Story.From.Idea

**Purpose**: Create 10 Story objects from each Idea

**Location**: `T/Story/From/Idea/`

**Input**:
- Idea document from Stage 1

**Output**:
- 10 Story objects per Idea
- Each Story with `idea_id` reference
- State set to `PrismQ.T.Title.From.Idea`

**Transitions To**: PrismQ.T.Title.From.Idea

---

### Stage 2: PrismQ.T.Title.From.Idea

**Purpose**: Generate initial title from the idea

**Location**: `T/Title/From/Idea/`

**Input**:
- Idea document from Stage 1

**Output**:
- Title v1
- Multiple title variants
- SEO considerations

**Transitions To**: PrismQ.T.Content.From.Idea.Title

---

### Stage 3: PrismQ.T.Content.From.Idea.Title

**Purpose**: Generate initial content from title and idea

**Location**: `T/Content/From/Idea/Title/`

**Input**:
- Title (v1) from Stage 2
- Idea document from Stage 1

**Output**:
- Content v1
- Narrative structure
- Content outline

**Transitions To**: PrismQ.T.Review.Title.From.Content.Idea

---

### Stage 4: PrismQ.T.Review.Title.From.Content.Idea

**Purpose**: Review title against content and original idea

**Location**: `T/Review/Title/From/Content/Idea/`

**Input**:
- Current Title
- Current Content
- Original Idea

**Output**:
- Review feedback for Title
- Assessment of title quality

**Transitions To**: PrismQ.T.Review.Content.From.Title.Idea (Stage 5)

**Note**: This review is always executed; there is no conditional branching based on acceptance

---

### Stage 5: PrismQ.T.Review.Content.From.Title.Idea

**Purpose**: Review content against current title and original idea

**Location**: `T/Review/Content/From/Title/Idea/`

**Input**:
- Current Content
- Current Title
- Original Idea

**Output**:
- Review feedback for Content
- Assessment of content quality

**Transitions To**: PrismQ.T.Review.Title.From.Content (Stage 6)

**Note**: This review is always executed; there is no conditional branching based on acceptance

---

### Stage 6: PrismQ.T.Review.Title.From.Content

**Purpose**: Review title against refined content

**Location**: `T/Review/Title/From/Content/`

**Input**:
- Current Title
- Current Content

**Output**:
- Review feedback for Title
- Acceptance/Rejection decision

**Decision Point**:
- **If Not Accepted**: Proceed to Title Refinement (Stage 7) → Content Refinement (Stage 8) → Return to Stage 6
- **If Accepted**: Continue to PrismQ.T.Review.Content.From.Title (Stage 9)

---

### Stage 7: PrismQ.T.Title.From.Title.Review.Content

**Purpose**: Refine title based on content and review feedback

**Location**: `T/Title/From/Title/Review/Content/`

**Input**:
- Previous Title
- Current Content
- Review feedback from Stage 6

**Output**:
- Title v2 (or higher version)
- Improvements documented

**Transitions To**: PrismQ.T.Content.From.Title.Review.Content (Stage 8)

**Note**: This stage is used later in the workflow when title refinement is needed (from Stage 15 Title.Readability)

---

### Stage 8: PrismQ.T.Content.From.Title.Review.Content

**Purpose**: Refine content based on title and review feedback

**Location**: `T/Content/From/Title/Review/Content/`

**Input**:
- Previous Content
- Current Title
- Review feedback (from various stages)

**Output**:
- Content v2 (or higher version)
- Improvements documented

**Transitions To**: PrismQ.T.Review.Title.From.Content (Stage 6)

**Note**: This stage is used extensively throughout the workflow when content refinement is needed

---

### Stage 9: PrismQ.T.Review.Content.From.Title

**Purpose**: Final review of content against finalized title

**Location**: `T/Review/Content/From/Title/`

**Input**:
- Current Content
- Current Title

**Output**:
- Review feedback for Content
- Acceptance/Rejection decision

**Decision Point**:
- **If Not Accepted**: Proceed to Content Refinement (Stage 8) → Return to Review.Title.From.Content (Stage 6)
- **If Accepted**: Continue to Grammar Review (Stage 10)

---

### Stages 10-16: Local AI Quality Reviews

These stages perform automated quality reviews on the content and title. Each review checks a specific quality dimension and loops back through content refinement and title review if issues are found.

---

### Stage 10: PrismQ.T.Review.Content.Grammar

**Purpose**: Grammar and syntax validation

**Location**: `T/Review/Grammar/`

**Input**: Current Content

**Output**: Grammar review results

**Decision Point**:
- **If Fails**: Return to Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 11

---

### Stage 11: PrismQ.T.Review.Content.Tone

**Purpose**: Tone and voice consistency check

**Location**: `T/Review/Tone/`

**Input**: Current Content

**Output**: Tone review results

**Decision Point**:
- **If Fails**: Return to Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 12

---

### Stage 12: PrismQ.T.Review.Content.Content

**Purpose**: Content accuracy and relevance validation

**Location**: `T/Review/Content/`

**Input**: 
- Current Content
- Original Idea

**Output**: Content review results

**Decision Point**:
- **If Fails**: Return to Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 13

---

### Stage 13: PrismQ.T.Review.Content.Consistency

**Purpose**: Style and consistency validation

**Location**: `T/Review/Consistency/`

**Input**: Current Content

**Output**: Consistency review results

**Decision Point**:
- **If Fails**: Return to Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 14

---

### Stage 14: PrismQ.T.Review.Content.Editing

**Purpose**: Final editing pass for polish

**Location**: `T/Review/Editing/`

**Input**: Current Content

**Output**: Editing review results

**Decision Point**:
- **If Fails**: Return to Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 15

---

### Stage 15: PrismQ.T.Review.Title.Readability

**Purpose**: Title readability and clarity check

**Location**: `T/Review/Readability/` (Title focus)

**Input**: Current Title

**Output**: Title readability score and feedback

**Decision Point**:
- **If Fails**: Return to Title Refinement (Stage 7) → Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 16

---

### Stage 16: PrismQ.T.Review.Content.Readability

**Purpose**: Content readability and clarity check

**Location**: `T/Review/Readability/` (Content focus)

**Input**: Current Content

**Output**: Content readability score and feedback

**Decision Point**:
- **If Fails**: Return to Content Refinement (Stage 8) → Review.Title.From.Content (Stage 6)
- **If Passes**: Continue to Stage 17

---

### Stages 17-18: GPT Expert Review and Polish Loop

These stages use GPT-based expert review for final quality assurance before publishing.

---

### Stage 17: PrismQ.T.Story.Review

**Purpose**: Expert-level review of complete story (Title + Content + Context)

**Location**: `T/Story/Review/`

**Input**:
- Final Title
- Final Content
- Audience context
- Original Idea

**Output**:
- Expert review feedback
- Holistic quality assessment
- Acceptance/Rejection decision

**Decision Point**:
- **If Not Accepted**: Proceed to PrismQ.T.Story.Polish (Stage 18)
- **If Accepted**: Continue to Publishing

**Note**: Uses GPT-4 or GPT-5 for professional-grade review

---

### Stage 18: PrismQ.T.Story.Polish

**Purpose**: Apply expert-level improvements based on Story.Review feedback

**Location**: `T/Story/Polish/`

**Input**:
- Current Title
- Current Content
- Expert review feedback from Stage 17

**Output**:
- Polished Title
- Polished Content
- Improvements documented

**Transitions To**: PrismQ.T.Story.Review (Stage 17) - Loop back for validation

**Note**: This creates an iterative loop with Story.Review until the content is accepted

---

## Workflow Characteristics

### Conditional Stages

Several stages are conditional and only executed based on review results:
- **PrismQ.T.Title.From.Title.Review.Content**: Only when title review fails
- **PrismQ.T.Content.From.Title.Review.Content**: Only when content review fails

### Iterative Loops

The workflow contains multiple iterative loops:

1. **Title-Content Alignment Loop** (Stages 4-9):
   - Review Title → Refine Title → Review Content → Refine Content
   - Ensures title and content are mutually aligned

2. **Quality Review Loop** (Stages 10-16):
   - Each quality dimension can send back to refinement
   - Ensures all quality criteria are met

3. **Expert Polish Loop** (Stages 17-18):
   - Story.Review → Story.Polish → Story.Review
   - Continues until expert review passes

### Decision Points

Key decision points that control workflow branching:
- **Accept/Reject decisions** at each review stage
- **Pass/Fail decisions** at each quality review stage
- **Expert approval** at Story.Review stage

## Quality Gates

### Early Stage Gates (Stages 4-10)
- Title-Content alignment
- Title-Idea alignment
- Content-Idea alignment
- Mutual consistency

### Mid Stage Gates (Stages 10-16)
- Grammar correctness
- Tone consistency
- Content accuracy
- Style consistency
- Editing quality
- Title readability
- Content readability

### Final Gate (Stages 17-18)
- Expert-level holistic review
- Professional quality standard
- Publication readiness

## Best Practices

### Starting the Workflow
1. Create a well-defined idea in Stage 1
2. Allow the initial title and content to be rough drafts
3. Trust the iterative review process to improve quality

### During Review Cycles
1. Each review failure is an opportunity for improvement
2. Don't skip review stages even if you think content is good
3. Use review feedback to make targeted improvements

### Quality Reviews
1. Local AI reviews (Stages 10-16) are fast and cost-effective
2. Fix issues early to avoid rework in later stages
3. All quality reviews must pass before expert review

### Expert Review Loop
1. Expert review (Stage 17-18) is the final quality gate
2. May require multiple polish iterations
3. Only proceed to publishing when expert review passes

## Integration with Publishing

After completing all workflow stages (including Story.Review acceptance), the content proceeds to:

**PrismQ.T.Publishing**
- SEO optimization
- Metadata finalization
- Platform-specific formatting
- Publication execution

See [T/Publishing/README.md](./Publishing/README.md) for details.

## Related Documentation

- **[T Module Overview](./README.md)** - Text pipeline overview
- **[T Workflow Visual Guide](./WORKFLOW_VISUAL.md)** - Quick visual reference with diagrams
- **[T Workflow State Machine](./WORKFLOW_STATE_MACHINE.md)** - Mermaid state diagram with all states and transitions
- **[Title & Content Workflow](./TITLE_SCRIPT_WORKFLOW.md)** - Original workflow documentation
- **[Ultra-Clean Pipeline](../_meta/docs/workflow/ultra-clean-pipeline.md)** - Simplified workflow view
- **[MVP Stages](../_meta/docs/workflow/mvp-stages.md)** - Complete 26-stage workflow
- **[State Machine](../_meta/docs/workflow/state-machine.md)** - Full state machine

---

**Version:** 1.0  
**Created:** 2025-11-24  
**Part of:** PrismQ.T Text Generation Pipeline
