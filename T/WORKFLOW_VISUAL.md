# PrismQ.T Workflow Visual Guide

**Quick Visual Reference for the Text Generation Pipeline**

## Simplified Workflow Overview

This document provides a visual guide to the PrismQ.T workflow, showing the main stages and decision points.

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 1: Idea Creation                       │
│                  PrismQ.T.Idea.Creation                          │
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
│               STAGE 3: Script from Title + Idea                  │
│              PrismQ.T.Script.From.Title.Idea                     │
│                          (v1)                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│          ╔══════════════════════════════════════════╗            │
│          ║  Title-Script Alignment Loop (4-10)     ║            │
│          ╚══════════════════════════════════════════╝            │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 4: Review Title by Script + Idea                    │  │
│  │   ├─ Accepted? → Skip to Stage 6                          │  │
│  │   └─ Not Accepted? → Stage 5: Refine Title               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 6: Review Script by Title + Idea                    │  │
│  │   ├─ Accepted? → Skip to Stage 8                          │  │
│  │   └─ Not Accepted? → Stage 7: Refine Script              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 8: Review Title by Script                           │  │
│  │   ├─ Accepted? → Skip to Stage 10                         │  │
│  │   └─ Not Accepted? → Stage 5: Refine Title (repeat)      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 10: Review Script by Title                          │  │
│  │   ├─ Accepted? → Continue to Quality Reviews              │  │
│  │   └─ Not Accepted? → Stage 7: Refine Script (repeat)     │  │
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
│  │   └─ Fails? → Back to Script Refinement (Stage 7)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 11: Tone Review                                     │  │
│  │   └─ Fails? → Back to Script Refinement (Stage 7)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 12: Content Review                                  │  │
│  │   └─ Fails? → Back to Script Refinement (Stage 7)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 13: Consistency Review                              │  │
│  │   └─ Fails? → Back to Script Refinement (Stage 7)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 14: Editing Review                                  │  │
│  │   └─ Fails? → Back to Script Refinement (Stage 7)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 15: Title Readability Review                        │  │
│  │   └─ Fails? → Back to Title Refinement (Stage 5)         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                          ↓                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Stage 16: Script Readability Review                       │  │
│  │   └─ Fails? → Back to Script Refinement (Stage 7)        │  │
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
| 1 | Idea.Creation | Initial idea capture |
| 2 | Title.From.Idea | Generate initial title (v1) |
| 3 | Script.From.Title.Idea | Generate initial script (v1) |

### Alignment Loop (4-10)
| Stage | Name | Purpose |
|-------|------|---------|
| 4 | Review.Title.By.Script.Idea | Review title against script and idea |
| 5 | Title.From.Script.Review.Title | Refine title (conditional) |
| 6 | Review.Script.By.Title.Idea | Review script against title and idea |
| 7 | Script.From.Title.Review.Script | Refine script (conditional) |
| 8 | Review.Title.By.Script | Re-review title against script |
| 10 | Review.Script.By.Title | Final script review against title |

### Quality Reviews (10-16)
| Stage | Name | Focus |
|-------|------|-------|
| 10 | Review.Script.Grammar | Grammar and syntax |
| 11 | Review.Script.Tone | Tone consistency |
| 12 | Review.Script.Content | Content accuracy |
| 13 | Review.Script.Consistency | Style consistency |
| 14 | Review.Script.Editing | Editing polish |
| 15 | Review.Title.Readability | Title clarity |
| 16 | Review.Script.Readability | Script clarity |

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
1 → 2 → 3 → 4(accept) → 6(accept) → 8(accept) → 9(accept) 
→ 10(pass) → 11(pass) → 12(pass) → 13(pass) → 14(pass) 
→ 15(pass) → 16(pass) → 17(accept) → Publishing
```
**Total Stages**: 14

### Pattern 2: Typical Flow (Some Refinements)
```
1 → 2 → 3 → 4(reject) → 5 → 6(accept) → 8(accept) 
→ 9(reject) → 7 → 9(accept) 
→ 10(pass) → 11(fail) → 7 → 9(accept) → 10(pass) → 11(pass)
→ 12(pass) → 13(pass) → 14(pass) → 15(pass) → 16(pass)
→ 17(reject) → 18 → 17(accept) → Publishing
```
**Total Stages**: ~21

### Pattern 3: High-Iteration Flow
Multiple rejections lead to more refinement cycles, but the workflow eventually converges to acceptable quality.

## Refinement Stages

### Stage 5: Title Refinement
**Called from**:
- Stage 4 (if title review fails)
- Stage 8 (if title re-review fails)
- Stage 16 (if title readability fails)

**Returns to**: Next review stage in sequence

### Stage 7: Script Refinement
**Called from**:
- Stage 6 (if script review fails)
- Stage 10 (if script final review fails)
- Stages 10-14, 16 (if any quality review fails)

**Returns to**: Next review stage in sequence

### Stage 18: Story Polish
**Called from**: Stage 17 (if expert review rejects)

**Returns to**: Stage 17 (for re-review)

## Quality Gates

### Gate 1: Title-Script Mutual Alignment
**Stages**: 4-10  
**Purpose**: Ensure title and script are coherent and aligned with idea  
**Iterations**: 1-3 typical

### Gate 2: Local AI Quality
**Stages**: 10-16  
**Purpose**: Automated quality checks on multiple dimensions  
**Iterations**: 1-2 typical per dimension

### Gate 3: Expert Review
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
