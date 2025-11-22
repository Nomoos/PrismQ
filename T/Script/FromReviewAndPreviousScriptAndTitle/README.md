# T/Script/FromReviewAndPreviousScriptAndTitle - Script v3+ Refinement

**Namespace**: `PrismQ.T.Script.FromReviewAndPreviousScriptAndTitle`

Refine script to v3+ through iterative cycles using review feedback, previous script version, and current title.

## Purpose

Create refined script versions (v3, v4, v5, v6, v7...) by applying review feedback to the previous version in an iterative improvement loop, ensuring alignment with the current title.

## Workflow Position

**Stage 11** in MVP workflow: `PrismQ.T.Script.Refinement (v3+)`

```
Stage 9: PrismQ.T.Title.FromReviewAndPreviousTitle (v3+)
    ↓
Stage 10: PrismQ.T.Rewiew.Script.ByTitle (v2) ←─────────┐
    ↓                                                    │
Stage 11: PrismQ.T.Script.FromReviewAndPreviousScriptAndTitle (v3+) │ ← THIS STATE
    ↓                                                    │
Stage 12: Title Acceptance Check ✓                      │
    ↓                                                    │
Stage 13: Check: Is Script Accepted? ─NO────────────────┘
    ↓ YES
(Continue to quality reviews)
```

## Input Components

### Primary Inputs
- **Previous Script Version** (v2, v3, v4, v5, v6... whatever is latest)
- **Current Title Version** (v3, v4, v5... whatever is latest and accepted)

### Review Feedback (Always Present)
- **Latest Script Review** (from Stage 10: Rewiew.Script.ByTitle)
  - Script-title alignment issues
  - Content quality problems
  - Pacing and structure notes
  - Specific refinement suggestions
  - Acceptance criteria gaps

### Context
- **Original Idea** (for intent preservation)
- **All Previous Script Versions** (for comparison and learning)
- **Version History** (to avoid repeated mistakes)
- **Title Context** (current accepted title)

## Process

1. **Analyze review feedback** (always present):
   - Extract actionable improvements
   - Identify critical vs nice-to-have changes
   - Understand acceptance criteria gaps
   - Note title-alignment issues

2. **Study previous version**:
   - Review what worked in previous script
   - Identify what needs refinement
   - Check version progression history
   - Avoid repeating past mistakes

3. **Ensure title alignment**:
   - Verify script delivers on title promises
   - Check opening hook matches title
   - Confirm content matches title expectations
   - Validate conclusion supports title

4. **Apply refinements**:
   - Make targeted improvements
   - Preserve successful elements
   - Address specific review concerns
   - Optimize length and pacing
   - Maintain idea intent

5. **Increment version**:
   - Create next version (v3 → v4 → v5 → v6 → v7...)
   - Document changes made
   - Track refinement rationale

## Output

- **Script vN** (next version: v3, v4, v5, v6, v7...)
- **Refinement Notes** (specific changes and why)
- **Version Diff** (comparison to previous version)
- **Title Alignment Check** (verification of promise delivery)
- **Acceptance Readiness** (assessment for passing gate)

## Key Principle

**Review is always present**: Every refinement is driven by review feedback. **Always uses newest versions**: If currently at v7 script and v8 title, refines script v7 to create v8 - not hardcoded v3.

## Iterative Loop

This state can be entered multiple times:

1. **First iteration**: v2 → v3
2. **Second iteration**: v3 → v4 (if v3 not accepted)
3. **Third iteration**: v4 → v5 (if v4 not accepted)
4. **...continues until accepted**

Each iteration:
- Title must be accepted first (Stage 12)
- Returns to Stage 10 for script review
- Comes back here for refinement with review feedback
- Increments version number

## Acceptance Path

After refinement:
1. Goes back to Stage 12 (Title Acceptance Check - must remain accepted)
2. Proceeds to Stage 13 (Script Acceptance Check)
3. **If ACCEPTED**: Continue to quality reviews (Grammar, Tone, etc.)
4. **If NOT ACCEPTED**: Loop back to Stage 10 with review → back here for next version

## Example Progression

**Iteration 1 (v2 → v3):**
- Input: v2 (115-second script)
- Title: v3 "The House That Remembers"
- Review: "Good length, needs stronger climax at 85-90s mark"
- Output: v3 (115s with enhanced climax sequence)

**Iteration 2 (v3 → v4):**
- Input: v3 (115s enhanced)
- Title: v4 "The House That Remembers—And Hunts"
- Review: "Title changed to add danger element, script needs hunting/threat imagery"
- Output: v4 (115s with added threat/danger elements)

**Iteration 3 (v4 → v5):**
- Input: v4 (115s with threat)
- Title: v5 "The House That Remembers—And Hunts"
- Review: "Excellent alignment, minor pacing tweak at transition"
- Output: v5 (115s with smooth transition)
- **ACCEPTED** ✓

## Module Metadata

**[→ View FromReviewAndPreviousScriptAndTitle/_meta/docs/](./_meta/docs/)**
**[→ View FromReviewAndPreviousScriptAndTitle/_meta/examples/](./_meta/examples/)**
**[→ View FromReviewAndPreviousScriptAndTitle/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../README.md)** | **[→ Script/_meta](../_meta/)**
