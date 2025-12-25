# PrismQ.T Workflow Visual Guide

**Quick Visual Reference for the Text Generation Pipeline**

## Simplified Workflow Overview

This document provides a visual guide to the PrismQ.T workflow, showing the main stages and decision points.

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 1: Idea Creation                       │
│                  PrismQ.T.Idea.From.User                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STAGE 1.5: Story from Idea                      │
│                  PrismQ.T.Story.From.Idea                        │
│              (Creates 10 Story objects per Idea)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 2: Title from Idea                      │
│                  PrismQ.T.Title.From.Idea                        │
│                          (v1)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               STAGE 3: Content from Title + Idea                │
│              PrismQ.T.Content.From.Idea.Title                    │
│                          (v1)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│          ╔══════════════════════════════════════════╗            │
│          ║  Title-Content Alignment Loop (4-9)     ║            │
│          ╚══════════════════════════════════════════╝            │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 4: Review Title From Content + Idea                 │  │
│  │   (Always proceeds to Stage 5 - no conditional)           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 5: Review Content From Title + Idea                 │  │
│  │   (Always proceeds to Stage 6 - no conditional)           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 6: Review Title From Content                        │  │
│  │   ├─ Not Accepted? → Stage 7: Refine Title               │  │
│  │   │                  ↓                                     │  │
│  │   │               Stage 8: Refine Content                 │  │
│  │   │                  ↓                                     │  │
│  │   │               Return to Stage 6                       │  │
│  │   └─ Accepted? → Continue to Stage 9                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 9: Review Content From Title                        │  │
│  │   ├─ Not Accepted? → Stage 8: Refine Content             │  │
│  │   │                  ↓                                     │  │
│  │   │               Return to Stage 6 (Title Review)        │  │
│  │   └─ Accepted? → Continue to Quality Reviews              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│          ╔══════════════════════════════════════════╗            │
│          ║  Local AI Quality Reviews (10-16)       ║            │
│          ║  Fast, automated quality checks          ║            │
│          ╚══════════════════════════════════════════╝            │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 10: Grammar Review                                  │  │
│  │   └─ Fails? → Content Refine (8) → Title Review (6)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 11: Tone Review                                     │  │
│  │   └─ Fails? → Content Refine (8) → Title Review (6)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 12: Content Review                                  │  │
│  │   └─ Fails? → Content Refine (8) → Title Review (6)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 13: Consistency Review                              │  │
│  │   └─ Fails? → Content Refine (8) → Title Review (6)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 14: Editing Review                                  │  │
│  │   └─ Fails? → Content Refine (8) → Title Review (6)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 15: Title Readability Review                        │  │
│  │   └─ Fails? → Title Refine (7) → Content Refine (8)      │  │
│  │                  → Title Review (6)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 16: Content Readability Review                      │  │
│  │   └─ Fails? → Content Refine (8) → Title Review (6)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│          ╔══════════════════════════════════════════╗            │
│          ║  GPT Expert Review Loop (17-18)         ║            │
│          ║  Final quality gate before publishing   ║            │
│          ╚══════════════════════════════════════════╝            │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 17: Story Review (GPT-based)                        │  │
│  │   ├─ Accepted? → Continue to Publishing                   │  │
│  │   └─ Not Accepted? → Stage 18: Story Polish              │  │
│  │                                                            │  │
│  │ Stage 18: Story Polish                                    │  │
│  │   └─ Returns to Stage 17 for re-review                   │  │
│  │                                                            │  │
│  │ [Loop continues until Story Review accepts]               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Publishing                                 │
│                  PrismQ.T.Publishing                             │
│                                                                  │
│  - SEO Optimization                                              │
│  - Metadata Finalization                                         │
│  - Platform-specific Formatting                                  │
│  - Publication Execution                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Stages Summary

### Creation Stages (1-3)
| Stage | Name | Purpose |
|-------|------|---------|
| 1 | Idea.From.User | Initial idea capture |
| 1.5 | Story.From.Idea | Create 10 Story objects per Idea |
| 2 | Title.From.Idea | Generate initial title (v1) |
| 3 | Content.From.Idea.Title | Generate initial content (v1) |

### Alignment Loop (4-9)
| Stage | Name | Purpose |
|-------|------|---------|
| 4 | Review.Title.From.Content.Idea | Review title (always proceeds to Stage 5) |
| 5 | Review.Content.From.Title.Idea | Review content (always proceeds to Stage 6) |
| 6 | Review.Title.From.Content | Re-review title (may loop through 7→8→6) |
| 7 | Title.From.Title.Review.Content | Refine title (conditional) |
| 8 | Content.From.Title.Review.Content | Refine content (conditional, used extensively) |
| 9 | Review.Content.From.Title | Final content review (may loop through 8→6) |

### Quality Reviews (10-16)
| Stage | Name | Focus |
|-------|------|-------|
| 10 | Review.Content.Grammar | Grammar and syntax |
| 11 | Review.Content.Tone | Tone consistency |
| 12 | Review.Content.Content | Content accuracy |
| 13 | Review.Content.Consistency | Style consistency |
| 14 | Review.Content.Editing | Editing polish |
| 15 | Review.Title.Readability | Title clarity |
| 16 | Review.Content.Readability | Content clarity |

### Expert Review (17-18)
| Stage | Name | Purpose |
|-------|------|---------|
| 17 | Story.Review | GPT-based holistic review |
| 18 | Story.Polish | Expert-level improvements |

## Key Decision Points

### 🔍 Review Decisions (Stages 4, 6, 8, 10)
Each review stage can:
- ✅ **Accept**: Skip refinement, move to next stage
- ❌ **Reject**: Go to refinement stage

### 🔬 Quality Checks (Stages 10-16)
Each quality review can:
- ✅ **Pass**: Continue to next quality check
- ❌ **Fail**: Return to appropriate refinement stage

### 🎓 Expert Review (Stage 17)
- ✅ **Accepted**: Proceed to Publishing
- 🔄 **Improvements Needed**: Go to Polish (Stage 18), then loop back

## Iteration Patterns

### Pattern 1: Ideal Flow (Minimal Iterations)
```
1 → 1.5 → 2 → 3 → 4 → 5 → 6(accept) → 9(accept) 
→ 10(pass) → 11(pass) → 12(pass) → 13(pass) → 14(pass) 
→ 15(pass) → 16(pass) → 17(accept) → Publishing
```
**Total Stages**: 16 (stages 7 and 8 are skipped when all reviews pass)

**Note**: In the ideal flow, refinement stages 7 and 8 are not executed because all reviews accept on the first attempt.

### Pattern 2: Typical Flow (Some Refinements)
```
1 → 1.5 → 2 → 3 → 4 → 5 → 6(reject) → 7 → 8 → 6(accept) 
→ 9(reject) → 8 → 6 → 9(accept) 
→ 10(pass) → 11(fail) → 8 → 6 → 9(accept) → 10(pass) → 11(pass)
→ 12(pass) → 13(pass) → 14(pass) 
→ 15(fail) → 7 → 8 → 6 → 9(accept) → 10 → 11 → 12 → 13 → 14 → 15(pass)
→ 16(pass) → 17(reject) → 18 → 17(accept) → Publishing
```
**Total Stages**: ~28

### Pattern 3: High-Iteration Flow
Multiple rejections lead to more refinement cycles, but the workflow eventually converges to acceptable quality.

## Refinement Stages

### Stage 7: Title Refinement
**Called from**:
- Stage 6 (Review.Title.From.Content fails)
- Stage 15 (Review.Title.Readability fails)

**Returns to**: Stage 8 (Content Refinement) → Stage 6 (Review.Title.From.Content)

### Stage 8: Content Refinement
**Called from**:
- Stage 6 (as part of title failure loop, after Stage 7)
- Stage 9 (Review.Content.From.Title fails)
- Stages 10-14, 16 (if any content quality review fails)
- Stage 15 (as part of title readability failure loop, after Stage 7)

**Returns to**: Stage 6 (Review.Title.From.Content)

**Note**: This is the most frequently used refinement stage, serving as the central hub for all content improvements

### Stage 18: Story Polish
**Called from**: Stage 17 (if expert review rejects)

**Returns to**: Stage 17 (for re-review)

## Quality Gates

### Gate 1: Initial Reviews
**Stages**: 4-5  
**Purpose**: Collect initial feedback on title and content alignment with idea  
**Iterations**: Always executed once (no conditional branching)

### Gate 2: Title-Content Mutual Alignment
**Stages**: 6-9  
**Purpose**: Ensure title and content are coherent through iterative refinement  
**Iterations**: 1-4 typical

### Gate 3: Local AI Quality
**Stages**: 10-16  
**Purpose**: Automated quality checks on multiple dimensions  
**Iterations**: 1-3 typical per dimension (all loop through Content Refinement → Title Review)

### Gate 4: Expert Review
**Stages**: 17-18  
**Purpose**: Professional-grade holistic review  
**Iterations**: 1-2 typical

## Best Practices

### Starting Strong (Stages 1-3)
✅ Create clear, well-defined ideas  
✅ Accept rough drafts - refinement comes later  
✅ Focus on core message and structure  

### Review Cycles (Stages 4-10)
✅ Trust the review feedback  
✅ Make targeted improvements based on feedback  
✅ Don't skip reviews even if content seems good  

### Quality Reviews (Stages 10-16)
✅ Fix issues early to avoid cascading problems  
✅ Each dimension is independent but interconnected  
✅ All must pass before expert review  

### Expert Review (Stages 17-18)
✅ Final opportunity for high-level improvements  
✅ GPT-based review provides professional perspective  
✅ Loop until publication-ready  

## Integration Points

### Before This Workflow
- Inspiration collection (optional)
- Idea selection and prioritization

### After This Workflow
- **PrismQ.T.Publishing**: SEO, formatting, publication
- **PrismQ.A**: Audio production from published text
- **PrismQ.V**: Video production from published audio

## Related Documentation

- **[Detailed Workflow](./WORKFLOW_DETAILED.md)** - Complete stage-by-stage documentation
- **[State Machine Diagram](./WORKFLOW_STATE_MACHINE.md)** - Mermaid state diagram
- **[T Module Overview](./README.md)** - Text pipeline overview
- **[Ultra-Clean Pipeline](../_meta/docs/workflow/ultra-clean-pipeline.md)** - Simplified notation

---

**Version:** 1.0  
**Created:** 2025-11-24  
**Part of:** PrismQ.T Text Generation Pipeline
