# T/Title/FromOriginalReviewAndScript - Title Refinement from Reviews

**Namespace**: `PrismQ.T.Title.FromOriginalReviewAndScript`

Refine title to v3+ based on iterative review feedback and updated script versions.

## Purpose

Create refined title versions (v3, v4, v5, etc.) through iterative improvement cycles based on ongoing reviews against the latest script version.

## Workflow Position

**Stage 9** in MVP workflow: `PrismQ.T.Title.Refinement (v3+)`

```
PrismQ.T.Rewiew.Title.ByScript (v2) ←──────────────┐
    ↓                                              │
PrismQ.T.Title.FromOriginalReviewAndScript (v3+)   │
    ↓                                              │
PrismQ.T.Rewiew.Script.ByTitle (v2)                │
    ↓                                              │
Check: Is Title Accepted? ─NO──────────────────────┘
    ↓ YES
(Continue to Script acceptance check)
```

## Input

- Title v2 or latest version (from FromScript or previous refinement)
- Script v2 or latest version (current script state)
- Review feedback from latest Rewiew.Title.ByScript
- Original idea (for context preservation)
- Previous versions (for comparison)

## Process

1. Apply latest review feedback
2. Ensure alignment with current script version
3. Refine title based on acceptance criteria
4. Preserve original intent from idea
5. Generate next version (v3, v4, v5, v6, v7, etc.)

## Output

- Title vN (next refined version)
- Refinement notes
- Version comparison data
- Acceptance readiness assessment

## Key Principle

**Always uses the newest versions**: If title is at v7 and script at v6, uses those versions - not hardcoded v3.

## Iterative Loop

This stage can iterate multiple times:
- Review → Refine → Review → Refine → ...
- Continues until title passes acceptance check (Stage 12)
- Each iteration increments version number

## Next Stage

After refinement:
- **Stage 10**: Rewiew.Script.ByTitle (v2) - Review script against refined title
- **Stage 12**: Title Acceptance Check - Verify if title is ready to proceed
- **If NOT accepted**: Return to Stage 8 (Rewiew.Title.ByScript) → back here for next version

## Module Metadata

**[→ View FromOriginalReviewAndScript/_meta/docs/](./_meta/docs/)**
**[→ View FromOriginalReviewAndScript/_meta/examples/](./_meta/examples/)**
**[→ View FromOriginalReviewAndScript/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../README.md)** | **[→ Title/_meta](../_meta/)**
