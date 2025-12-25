# Ultra-Clean Pipeline Pattern

**Simplified representation of the PrismQ execution flow**

> 📚 **See also**: 
> - [Detailed T Workflow](../../T/WORKFLOW_DETAILED.md) - Complete stage-by-stage documentation with all review cycles
> - [T Workflow State Machine](../../T/WORKFLOW_STATE_MACHINE.md) - Visual state diagram with all workflow paths

## Overview

The Ultra-Clean Pipeline is a simplified, readable representation of the core iterative workflow in PrismQ's Text Generation Pipeline (T module). It shows the essential flow of data and dependencies between stages in a clean, dot-notation format.

## Pattern Structure

```
Idea.From.User 
→ Title.From.Idea 
→ Content.From.Idea.Title 
→ Review.Title.From.Content.Idea 
→ Title.From.Title.Review.Content 
→ Review.Content.From.Title.Idea 
→ Content.From.Title.Review.Content 
→ Review.Idea.From.Title.Content 
→ Idea.From.Title.Content.Review.Idea
```

## Pattern Explanation

### Stage 1: `Idea.From.User`
**Purpose**: Initial idea creation  
**Inputs**: None (starting point)  
**Outputs**: `Idea`

Creates the foundational idea for the content piece.

---

### Stage 2: `Title.From.Idea`
**Purpose**: Generate initial title from idea  
**Inputs**: `Idea`  
**Outputs**: `Title` (v1)

Creates the first version of the title based solely on the idea.

---

### Stage 3: `Content.From.Idea.Title`
**Purpose**: Generate initial content  
**Inputs**: `Title`, `Idea`  
**Outputs**: `Content` (v1)

Creates the first version of the content using both the title and original idea as context.

---

### Stage 4: `Review.Title.From.Content.Idea`
**Purpose**: Review title against content and idea  
**Inputs**: `Title`, `Content`, `Idea`  
**Outputs**: `Review.Title` (feedback)

Evaluates whether the title is well-aligned with the content and original idea.

---

### Stage 5: `Title.From.Title.Review.Content`
**Purpose**: Improve title based on content and review  
**Inputs**: `Content`, `Review.Title`, (previous) `Title`  
**Outputs**: `Title` (v2)

Generates an improved version of the title using insights from the content and the review feedback.

---

### Stage 6: `Review.Content.From.Title.Idea`
**Purpose**: Review content against title and idea  
**Inputs**: `Content`, `Title`, `Idea`  
**Outputs**: `Review.Content` (feedback)

Evaluates whether the content aligns well with the updated title and original idea.

---

### Stage 7: `Content.From.Title.Review.Content`
**Purpose**: Improve content based on title and review  
**Inputs**: `Title`, `Review.Content`, (previous) `Content`  
**Outputs**: `Content` (v2)

Generates an improved version of the content using the updated title and review feedback.

---

### Stage 8: `Review.Idea.From.Title.Content`
**Purpose**: Validate complete alignment  
**Inputs**: `Idea`, `Title`, `Content`  
**Outputs**: `Review.Idea` (validation)

Final validation that all components (idea, title, content) are cohesively aligned.

---

### Stage 9: `Idea.From.Title.Content.Review.Idea`
**Purpose**: Finalize or refine idea representation  
**Inputs**: `Title`, `Content`, `Review.Idea`  
**Outputs**: `Idea` (refined/finalized)

Updates or confirms the idea representation based on the fully developed title, content, and validation feedback.

---

## Key Characteristics

### 1. **Dot Notation**
Each stage is represented in the format `Entity.Action.Context`:
- **Entity**: The primary artifact being created or modified (Idea, Title, Content, Review)
- **Action**: The operation being performed (Creation, From, By)
- **Context**: The inputs informing the operation (Idea, Title, Content, Review)

### 2. **Explicit Dependencies**
The notation explicitly shows what each stage depends on:
- `Title.From.Idea` → Title depends on Idea
- `Content.From.Idea.Title` → Content depends on both Idea and Title
- `Review.Title.From.Content.Idea` → Review evaluates Title using Content and Idea

### 3. **Iterative Refinement**
The pattern shows how artifacts are iteratively improved:
- Title v1 → Review → Title v2
- Content v1 → Review → Content v2
- Multiple cross-reviews ensure alignment

### 4. **Co-Improvement Cycle**
The pattern demonstrates the co-dependent improvement methodology:
- Title is reviewed against Content
- Content is reviewed against Title
- Both are continuously refined based on mutual feedback

## Mapping to Full Workflow

The Ultra-Clean Pipeline is a simplified view of 9 conceptual stages. Here's how it maps to the complete 26-stage MVP workflow:

**Note**: The "Ultra-Clean Stage" numbers (1-9) represent the sequential stages in the simplified pattern, which may map to multiple or non-sequential stages in the full MVP workflow.

| Ultra-Clean Stage | MVP Stages | Description |
|-------------------|------------|-------------|
| `Idea.From.User` | Stage 1 | PrismQ.T.Idea.From.User |
| `Title.From.Idea` | Stage 2 | PrismQ.T.Title.From.Idea (v1) |
| `Content.From.Idea.Title` | Stage 3 | PrismQ.T.Content.From.Idea.Title (v1) |
| `Review.Title.From.Content.Idea` | Stage 4 | PrismQ.T.Review.Title.From.Content (v1) |
| `Title.From.Title.Review.Content` | Stage 6 | PrismQ.T.Title.From.Title.Review.Content (v2) |
| `Review.Content.From.Title.Idea` | Stage 5, 10 | PrismQ.T.Review.Content.From.Title (v1, v2) |
| `Content.From.Title.Review.Content` | Stage 7, 11 | PrismQ.T.Content.Improvements (v2, v3) |
| `Review.Idea.From.Title.Content` | Stages 12-13 | Title & Content Acceptance Checks |
| `Idea.From.Title.Content.Review.Idea` | Stages 14-23 | Quality reviews, expert review, publishing |

## Benefits of Ultra-Clean Notation

### 1. **Readability**
Clean, human-readable format that quickly conveys the workflow essence.

### 2. **Dependency Clarity**
Immediately visible what each stage depends on, making data flow transparent.

### 3. **Communication**
Easy to discuss and explain the workflow to stakeholders, developers, and content creators.

### 4. **Documentation**
Serves as a concise reference for the core iterative process.

### 5. **Simplification**
Abstracts away implementation details while preserving the conceptual flow.

## Usage in Documentation

### Quick Reference
Use the Ultra-Clean Pipeline as a quick reference at the top of detailed workflow documentation to give readers immediate context.

### Conceptual Discussions
Use it when discussing the workflow philosophy and iterative improvement methodology.

### Onboarding
Use it to introduce new team members to the PrismQ workflow before diving into detailed stages.

### Architecture Diagrams
Incorporate it into high-level architecture diagrams to show the core content creation loop.

## Related Documentation

- **[MVP Stages](./mvp-stages.md)** - Complete 26-stage workflow with detailed implementation
- **[State Machine](./state-machine.md)** - Full state machine documentation
- **[Transitions](./transitions.md)** - State transition rules and logic
- **[Title & Content Workflow](../../T/TITLE_SCRIPT_WORKFLOW.md)** - Detailed T module workflow

---

**Version:** 1.0  
**Last Updated:** 2025-11-24  
**Part of:** PrismQ Workflow Documentation
