# T/Script/FromOriginalReviewAndTitle - Script Refinement from Reviews

**Namespace**: `PrismQ.T.Script.FromOriginalReviewAndTitle`

Refine script to v3+ based on iterative review feedback and updated title versions.

## Purpose

Create refined script versions (v3, v4, v5, etc.) through iterative improvement cycles based on ongoing reviews against the latest title version.

## Workflow Position

**Stage 11** in MVP workflow: `PrismQ.T.Script.Refinement (v3+)`

```
PrismQ.T.Title.FromOriginalReviewAndScript (v3+)
    ↓
PrismQ.T.Rewiew.Script.ByTitle (v2) ←──────────────┐
    ↓                                              │
PrismQ.T.Script.FromOriginalReviewAndTitle (v3+)   │
    ↓                                              │
Check: Is Title Accepted? (Stage 12)               │
    ↓ YES                                          │
Check: Is Script Accepted? ─NO─────────────────────┘
    ↓ YES
(Continue to quality reviews)
```

## Input

- Script v2 or latest version (from FromTitle or previous refinement)
- Title v3+ or latest version (current title state)
- Review feedback from latest Rewiew.Script.ByTitle
- Original idea (for context preservation)
- Previous versions (for comparison)

## Process

1. Apply latest review feedback
2. Ensure alignment with current title version
3. Refine script based on acceptance criteria
4. Preserve original intent from idea
5. Optimize for target platform (length, pacing)
6. Generate next version (v3, v4, v5, v6, v7, etc.)

## Output

- Script vN (next refined version)
- Refinement notes
- Version comparison data
- Acceptance readiness assessment
- Updated timing/structure metadata

## Key Principle

**Always uses the newest versions**: If script is at v6 and title at v7, uses those versions - not hardcoded v3.

## Iterative Loop

This stage can iterate multiple times:
- Review → Refine → Review → Refine → ...
- Continues until script passes acceptance check (Stage 13)
- Each iteration increments version number

## Next Stage

After refinement:
- **Stage 12**: Title Acceptance Check - Verify title is ready
- **Stage 13**: Script Acceptance Check - Verify if script is ready to proceed
- **If NOT accepted**: Return to Stage 10 (Rewiew.Script.ByTitle) → back here for next version
- **If accepted**: Proceed to quality reviews (Grammar, Tone, Content, etc.)

## Module Metadata

**[→ View FromOriginalReviewAndTitle/_meta/docs/](./_meta/docs/)**
**[→ View FromOriginalReviewAndTitle/_meta/examples/](./_meta/examples/)**
**[→ View FromOriginalReviewAndTitle/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../README.md)** | **[→ Script/_meta](../_meta/)**
