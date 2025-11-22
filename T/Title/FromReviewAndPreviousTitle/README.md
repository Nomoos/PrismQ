# T/Title/FromReviewAndPreviousTitle - Title v3+ Refinement

**Namespace**: `PrismQ.T.Title.FromReviewAndPreviousTitle`

Refine title to v3+ through iterative cycles using latest review feedback and previous title version.

## Purpose

Create refined title versions (v3, v4, v5, v6, v7...) by applying review feedback to the previous version in an iterative improvement loop.

## Workflow Position

**Stage 9** in MVP workflow: `PrismQ.T.Title.Refinement (v3+)`

```
Stage 8: PrismQ.T.Rewiew.Title.ByScript (v2) ←──────────┐
    ↓                                                    │
Stage 9: PrismQ.T.Title.FromReviewAndPreviousTitle (v3+) │ ← THIS STATE
    ↓                                                    │
Stage 10: PrismQ.T.Rewiew.Script.ByTitle (v2)            │
    ↓                                                    │
Stage 12: Check: Is Title Accepted? ─NO─────────────────┘
    ↓ YES
(Continue to script acceptance)
```

## Input Components

### Primary Inputs
- **Previous Title Version** (v2, v3, v4, v5, v6... whatever is latest)
- **Current Script Version** (v2, v3, v4... whatever is latest)

### Review Feedback
- **Latest Title Review** (from Stage 8: Rewiew.Title.ByScript)
  - Specific refinement suggestions
  - Alignment issues with current script
  - Quality improvement areas

### Context
- **Original Idea** (for intent preservation)
- **All Previous Title Versions** (for comparison and learning)
- **Version History** (to avoid repeated mistakes)

## Process

1. **Analyze latest review**:
   - Extract actionable feedback
   - Identify critical vs nice-to-have changes
   - Understand acceptance criteria gaps

2. **Study previous version**:
   - Review what worked in previous title
   - Identify what needs refinement
   - Check version progression history

3. **Apply refinements**:
   - Make targeted improvements
   - Preserve successful elements
   - Address specific review concerns
   - Maintain idea intent

4. **Increment version**:
   - Create next version (v3 → v4 → v5 → v6 → v7...)
   - Document changes made
   - Track refinement rationale

## Output

- **Title vN** (next version: v3, v4, v5, v6, v7...)
- **Refinement Notes** (specific changes and why)
- **Version Diff** (comparison to previous version)
- **Acceptance Readiness** (assessment for passing gate)

## Key Principle

**Always uses newest versions**: If currently at v7, refines v7 to create v8 - not hardcoded v3.

## Iterative Loop

This state can be entered multiple times:

1. **First iteration**: v2 → v3
2. **Second iteration**: v3 → v4 (if v3 not accepted)
3. **Third iteration**: v4 → v5 (if v4 not accepted)
4. **...continues until accepted**

Each iteration:
- Returns to Stage 8 for review
- Comes back here for refinement
- Increments version number

## Acceptance Path

After refinement:
1. Goes to Stage 10 (Script review by refined title)
2. Proceeds to Stage 12 (Title Acceptance Check)
3. **If ACCEPTED**: Continue to script acceptance
4. **If NOT ACCEPTED**: Loop back to Stage 8 → back here for next version

## Example Progression

**Iteration 1 (v2 → v3):**
- Input: v2 "The House That Remembers: A Midnight Visitor Returns"
- Review: "Too long, focus on the time-loop element"
- Output: v3 "The House That Remembers"

**Iteration 2 (v3 → v4):**
- Input: v3 "The House That Remembers"
- Review: "Add intrigue, hint at danger"
- Output: v4 "The House That Remembers... And Hunts"

**Iteration 3 (v4 → v5):**
- Input: v4 "The House That Remembers... And Hunts"
- Review: "Excellent - minor grammar preference"
- Output: v5 "The House That Remembers—And Hunts"
- **ACCEPTED** ✓

## Module Metadata

**[→ View FromReviewAndPreviousTitle/_meta/docs/](./_meta/docs/)**
**[→ View FromReviewAndPreviousTitle/_meta/examples/](./_meta/examples/)**
**[→ View FromReviewAndPreviousTitle/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../README.md)** | **[→ Title/_meta](../_meta/)**
