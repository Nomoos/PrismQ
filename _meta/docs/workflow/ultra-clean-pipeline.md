# Ultra-Clean Pipeline Pattern

**Simplified representation of the PrismQ execution flow**

> 📚 **See also**: 
> - [Detailed T Workflow](../../T/WORKFLOW_DETAILED.md) - Complete stage-by-stage documentation with all review cycles
> - [T Workflow State Machine](../../T/WORKFLOW_STATE_MACHINE.md) - Visual state diagram with all workflow paths

## Overview

The Ultra-Clean Pipeline is a simplified, readable representation of the core iterative workflow in PrismQ's Text Generation Pipeline (T module). It shows the essential flow of data and dependencies between stages in a clean, dot-notation format.

## Pattern Structure

```
Idea.Creation 
→ Title.From.Idea 
→ Script.From.Title.Idea 
→ Review.Title.By.Script.Idea 
→ Title.From.Script.Review.Title 
→ Review.Script.By.Title.Idea 
→ Script.From.Title.Review.Script 
→ Review.Idea.By.Title.Script 
→ Idea.From.Title.Script.Review.Idea
```

## Pattern Explanation

### Stage 1: `Idea.Creation`
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

### Stage 3: `Script.From.Title.Idea`
**Purpose**: Generate initial script  
**Inputs**: `Title`, `Idea`  
**Outputs**: `Script` (v1)

Creates the first version of the script using both the title and original idea as context.

---

### Stage 4: `Review.Title.By.Script.Idea`
**Purpose**: Review title against script and idea  
**Inputs**: `Title`, `Script`, `Idea`  
**Outputs**: `Review.Title` (feedback)

Evaluates whether the title is well-aligned with the script content and original idea.

---

### Stage 5: `Title.From.Script.Review.Title`
**Purpose**: Improve title based on script and review  
**Inputs**: `Script`, `Review.Title`, (previous) `Title`  
**Outputs**: `Title` (v2)

Generates an improved version of the title using insights from the script and the review feedback.

---

### Stage 6: `Review.Script.By.Title.Idea`
**Purpose**: Review script against title and idea  
**Inputs**: `Script`, `Title`, `Idea`  
**Outputs**: `Review.Script` (feedback)

Evaluates whether the script aligns well with the updated title and original idea.

---

### Stage 7: `Script.From.Title.Review.Script`
**Purpose**: Improve script based on title and review  
**Inputs**: `Title`, `Review.Script`, (previous) `Script`  
**Outputs**: `Script` (v2)

Generates an improved version of the script using the updated title and review feedback.

---

### Stage 8: `Review.Idea.By.Title.Script`
**Purpose**: Validate complete alignment  
**Inputs**: `Idea`, `Title`, `Script`  
**Outputs**: `Review.Idea` (validation)

Final validation that all components (idea, title, script) are cohesively aligned.

---

### Stage 9: `Idea.From.Title.Script.Review.Idea`
**Purpose**: Finalize or refine idea representation  
**Inputs**: `Title`, `Script`, `Review.Idea`  
**Outputs**: `Idea` (refined/finalized)

Updates or confirms the idea representation based on the fully developed title, script, and validation feedback.

---

## Key Characteristics

### 1. **Dot Notation**
Each stage is represented in the format `Entity.Action.Context`:
- **Entity**: The primary artifact being created or modified (Idea, Title, Script, Review)
- **Action**: The operation being performed (Creation, From, By)
- **Context**: The inputs informing the operation (Idea, Title, Script, Review)

### 2. **Explicit Dependencies**
The notation explicitly shows what each stage depends on:
- `Title.From.Idea` → Title depends on Idea
- `Script.From.Title.Idea` → Script depends on both Title and Idea
- `Review.Title.By.Script.Idea` → Review evaluates Title using Script and Idea

### 3. **Iterative Refinement**
The pattern shows how artifacts are iteratively improved:
- Title v1 → Review → Title v2
- Script v1 → Review → Script v2
- Multiple cross-reviews ensure alignment

### 4. **Co-Improvement Cycle**
The pattern demonstrates the co-dependent improvement methodology:
- Title is reviewed against Script
- Script is reviewed against Title
- Both are continuously refined based on mutual feedback

## Mapping to Full Workflow

The Ultra-Clean Pipeline is a simplified view of 9 conceptual stages. Here's how it maps to the complete 26-stage MVP workflow:

**Note**: The "Ultra-Clean Stage" numbers (1-9) represent the sequential stages in the simplified pattern, which may map to multiple or non-sequential stages in the full MVP workflow.

| Ultra-Clean Stage | MVP Stages | Description |
|-------------------|------------|-------------|
| `Idea.Creation` | Stage 1 | PrismQ.T.Idea.Creation |
| `Title.From.Idea` | Stage 2 | PrismQ.T.Title.From.Idea (v1) |
| `Script.From.Title.Idea` | Stage 3 | PrismQ.T.Script.FromIdeaAndTitle (v1) |
| `Review.Title.By.Script.Idea` | Stage 4 | PrismQ.T.Review.Title.ByScript (v1) |
| `Title.From.Script.Review.Title` | Stage 6 | PrismQ.T.Title.Improvements (v2) |
| `Review.Script.By.Title.Idea` | Stage 5, 10 | PrismQ.T.Review.Script.ByTitle (v1, v2) |
| `Script.From.Title.Review.Script` | Stage 7, 11 | PrismQ.T.Script.Improvements (v2, v3) |
| `Review.Idea.By.Title.Script` | Stages 12-13 | Title & Script Acceptance Checks |
| `Idea.From.Title.Script.Review.Idea` | Stages 14-23 | Quality reviews, expert review, publishing |

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
- **[Title & Script Workflow](../../T/TITLE_SCRIPT_WORKFLOW.md)** - Detailed T module workflow

---

**Version:** 1.0  
**Last Updated:** 2025-11-24  
**Part of:** PrismQ Workflow Documentation
