# PrismQ.T Detailed Workflow Documentation

**Complete Iterative Workflow for Text Content Creation with Review Cycles**

## Overview

This document describes the detailed, iterative workflow for the PrismQ.T (Text Generation Pipeline) module. The workflow includes multiple review and refinement cycles to ensure high-quality text content production.

## Complete Workflow Sequence

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.From.Idea
    ↓
PrismQ.T.Script.From.Title.Idea
    ↓
PrismQ.T.Review.Title.By.Script.Idea
    ↓
PrismQ.T.Review.Script.By.Title.Idea
    ↓
PrismQ.T.Review.Title.By.Script
    ├─ if not accepted → PrismQ.T.Title.From.Script.Review.Title
    │                      ↓
    │                   PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Script.By.Title
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Local AI Quality Reviews
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
PrismQ.T.Review.Script.Grammar
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Script.Tone
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Script.Content
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Script.Consistency
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Script.Editing
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Title.Readability
    ├─ if not accepted → PrismQ.T.Title.From.Script.Review.Title
    │                      ↓
    │                   PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
    └─ if accepted → continue
    ↓
PrismQ.T.Review.Script.Readability
    ├─ if not accepted → PrismQ.T.Script.From.Title.Review.Script
    │                      ↓
    │                   PrismQ.T.Review.Title.By.Script (loop back)
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

**Transitions To**: PrismQ.T.Title.From.Idea

---

### Stage 2: PrismQ.T.Title.From.Idea

**Purpose**: Generate initial title from the idea

**Location**: `T/Title/FromIdea/`

**Input**:
- Idea document from Stage 1

**Output**:
- Title v1
- Multiple title variants
- SEO considerations

**Transitions To**: PrismQ.T.Script.From.Title.Idea

---

### Stage 3: PrismQ.T.Script.From.Title.Idea

**Purpose**: Generate initial script from title and idea

**Location**: `T/Script/FromIdeaAndTitle/`

**Input**:
- Title (v1) from Stage 2
- Idea document from Stage 1

**Output**:
- Script v1
- Narrative structure
- Content outline

**Transitions To**: PrismQ.T.Review.Title.By.Script.Idea

---

### Stage 4: PrismQ.T.Review.Title.By.Script.Idea

**Purpose**: Review title against script and original idea

**Location**: `T/Review/Title/ByScriptIdea/`

**Input**:
- Current Title
- Current Script
- Original Idea

**Output**:
- Review feedback for Title
- Assessment of title quality

**Transitions To**: PrismQ.T.Review.Script.By.Title.Idea (Stage 5)

**Note**: This review is always executed; there is no conditional branching based on acceptance

---

### Stage 5: PrismQ.T.Review.Script.By.Title.Idea

**Purpose**: Review script against current title and original idea

**Location**: `T/Review/Script/ByTitleIdea/`

**Input**:
- Current Script
- Current Title
- Original Idea

**Output**:
- Review feedback for Script
- Assessment of script quality

**Transitions To**: PrismQ.T.Review.Title.By.Script (Stage 6)

**Note**: This review is always executed; there is no conditional branching based on acceptance

---

### Stage 6: PrismQ.T.Review.Title.By.Script

**Purpose**: Review title against refined script

**Location**: `T/Review/Title/ByScript/`

**Input**:
- Current Title
- Current Script

**Output**:
- Review feedback for Title
- Acceptance/Rejection decision

**Decision Point**:
- **If Not Accepted**: Proceed to Title Refinement (Stage 7) → Script Refinement (Stage 8) → Return to Stage 6
- **If Accepted**: Continue to PrismQ.T.Review.Script.By.Title (Stage 9)

---

### Stage 7: PrismQ.T.Title.From.Script.Review.Title

**Purpose**: Refine title based on script and review feedback

**Location**: `T/Title/FromOriginalTitleAndReviewAndScript/`

**Input**:
- Previous Title
- Current Script
- Review feedback from Stage 6

**Output**:
- Title v2 (or higher version)
- Improvements documented

**Transitions To**: PrismQ.T.Script.From.Title.Review.Script (Stage 8)

**Note**: This stage is used later in the workflow when title refinement is needed (from Stage 15 Title.Readability)

---

### Stage 8: PrismQ.T.Script.From.Title.Review.Script

**Purpose**: Refine script based on title and review feedback

**Location**: `T/Script/FromOriginalScriptAndReviewAndTitle/`

**Input**:
- Previous Script
- Current Title
- Review feedback (from various stages)

**Output**:
- Script v2 (or higher version)
- Improvements documented

**Transitions To**: PrismQ.T.Review.Title.By.Script (Stage 6)

**Note**: This stage is used extensively throughout the workflow when script refinement is needed

---

### Stage 9: PrismQ.T.Review.Script.By.Title

**Purpose**: Final review of script against finalized title

**Location**: `T/Review/Script/ByTitle/`

**Input**:
- Current Script
- Current Title

**Output**:
- Review feedback for Script
- Acceptance/Rejection decision

**Decision Point**:
- **If Not Accepted**: Proceed to Script Refinement (Stage 8) → Return to Review.Title.By.Script (Stage 6)
- **If Accepted**: Continue to Grammar Review (Stage 10)

---

### Stages 10-16: Local AI Quality Reviews

These stages perform automated quality reviews on the script and title. Each review checks a specific quality dimension and loops back through script refinement and title review if issues are found.

---

### Stage 10: PrismQ.T.Review.Script.Grammar

**Purpose**: Grammar and syntax validation

**Location**: `T/Review/Grammar/`

**Input**: Current Script

**Output**: Grammar review results

**Decision Point**:
- **If Fails**: Return to Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 11

---

### Stage 11: PrismQ.T.Review.Script.Tone

**Purpose**: Tone and voice consistency check

**Location**: `T/Review/Tone/`

**Input**: Current Script

**Output**: Tone review results

**Decision Point**:
- **If Fails**: Return to Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 12

---

### Stage 12: PrismQ.T.Review.Script.Content

**Purpose**: Content accuracy and relevance validation

**Location**: `T/Review/Content/`

**Input**: 
- Current Script
- Original Idea

**Output**: Content review results

**Decision Point**:
- **If Fails**: Return to Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 13

---

### Stage 13: PrismQ.T.Review.Script.Consistency

**Purpose**: Style and consistency validation

**Location**: `T/Review/Consistency/`

**Input**: Current Script

**Output**: Consistency review results

**Decision Point**:
- **If Fails**: Return to Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 14

---

### Stage 14: PrismQ.T.Review.Script.Editing

**Purpose**: Final editing pass for polish

**Location**: `T/Review/Editing/`

**Input**: Current Script

**Output**: Editing review results

**Decision Point**:
- **If Fails**: Return to Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 15

---

### Stage 15: PrismQ.T.Review.Title.Readability

**Purpose**: Title readability and clarity check

**Location**: `T/Review/Readability/` (Title focus)

**Input**: Current Title

**Output**: Title readability score and feedback

**Decision Point**:
- **If Fails**: Return to Title Refinement (Stage 7) → Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 16

---

### Stage 16: PrismQ.T.Review.Script.Readability

**Purpose**: Script readability and clarity check

**Location**: `T/Review/Readability/` (Script focus)

**Input**: Current Script

**Output**: Script readability score and feedback

**Decision Point**:
- **If Fails**: Return to Script Refinement (Stage 8) → Review.Title.By.Script (Stage 6)
- **If Passes**: Continue to Stage 17

---

### Stages 17-18: GPT Expert Review and Polish Loop

These stages use GPT-based expert review for final quality assurance before publishing.

---

### Stage 17: PrismQ.T.Story.Review

**Purpose**: Expert-level review of complete story (Title + Script + Context)

**Location**: `T/Story/ExpertReview/`

**Input**:
- Final Title
- Final Script
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
- Current Script
- Expert review feedback from Stage 17

**Output**:
- Polished Title
- Polished Script
- Improvements documented

**Transitions To**: PrismQ.T.Story.Review (Stage 17) - Loop back for validation

**Note**: This creates an iterative loop with Story.Review until the content is accepted

---

## Workflow Characteristics

### Conditional Stages

Several stages are conditional and only executed based on review results:
- **PrismQ.T.Title.From.Script.Review.Title**: Only when title review fails
- **PrismQ.T.Script.From.Title.Review.Script**: Only when script review fails

### Iterative Loops

The workflow contains multiple iterative loops:

1. **Title-Script Alignment Loop** (Stages 4-9):
   - Review Title → Refine Title → Review Script → Refine Script
   - Ensures title and script are mutually aligned

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
- Title-Script alignment
- Title-Idea alignment
- Script-Idea alignment
- Mutual consistency

### Mid Stage Gates (Stages 10-16)
- Grammar correctness
- Tone consistency
- Content accuracy
- Style consistency
- Editing quality
- Title readability
- Script readability

### Final Gate (Stages 17-18)
- Expert-level holistic review
- Professional quality standard
- Publication readiness

## Best Practices

### Starting the Workflow
1. Create a well-defined idea in Stage 1
2. Allow the initial title and script to be rough drafts
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
- **[Title & Script Workflow](./TITLE_SCRIPT_WORKFLOW.md)** - Original workflow documentation
- **[Ultra-Clean Pipeline](../_meta/docs/workflow/ultra-clean-pipeline.md)** - Simplified workflow view
- **[MVP Stages](../_meta/docs/workflow/mvp-stages.md)** - Complete 26-stage workflow
- **[State Machine](../_meta/docs/workflow/state-machine.md)** - Full state machine

---

**Version:** 1.0  
**Created:** 2025-11-24  
**Part of:** PrismQ.T Text Generation Pipeline
