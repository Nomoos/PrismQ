# T/Script/FromReviewAndNewTitleAndPreviousScript - Script v2 Improvements

**Namespace**: `PrismQ.T.Script.FromReviewAndNewTitleAndPreviousScript`

Generate improved script (v2) using comprehensive context from both reviews, new title v2, and previous script v1.

## Purpose

Create the second version (v2) of the script by incorporating feedback from **both** reviews, aligning with the **new improved title v2**, and building on **previous script v1**.

## Workflow Position

**Stage 7** in MVP workflow: `PrismQ.T.Script.Improvements (v2)`

```
Stage 4: PrismQ.T.Rewiew.Title.ByScript (v1) ← Title review
    ↓
Stage 5: PrismQ.T.Rewiew.Script.ByTitle (v1) ← Script review
    ↓
Stage 6: PrismQ.T.Title.FromReviewAndPreviousTitleAndScript (v2) ← New improved title
    ↓
Stage 7: PrismQ.T.Script.FromReviewAndNewTitleAndPreviousScript (v2) ← THIS STATE
    ↓
Stage 8: PrismQ.T.Rewiew.Title.ByScript (v2)
```

## Input Components

### Primary Inputs
- **Previous Script v1** (from Script.FromIdeaAndTitle)
- **New Title v2** (from Title.FromReviewAndPreviousTitleAndScript)

### Review Feedback
- **Script Review Feedback** (from Stage 5: Rewiew.Script.ByTitle)
  - Script quality issues
  - Title promise delivery gaps
  - Content structure problems
  - Pacing and flow notes
  - Engagement concerns

- **Title Review Feedback** (from Stage 4: Rewiew.Title.ByScript)
  - Title-script alignment issues
  - Content expectations from title
  - Script-relevant insights

### Context
- **Original Idea** (for intent preservation)
- **Previous Title v1** (for comparison)

## Process

1. **Analyze all inputs**:
   - Study new title v2 and its changes
   - Review script v1 strengths and weaknesses
   - Extract actionable feedback from both reviews
   - Identify cross-cutting improvement themes

2. **Align with new title**:
   - Ensure script matches new title promises
   - Update opening hook if title changed significantly
   - Adjust content focus to match title angle
   - Verify conclusion supports title

3. **Apply review feedback**:
   - Fix content structure issues
   - Improve pacing and flow
   - Enhance engagement
   - Address quality concerns
   - Optimize length if needed

4. **Preserve strengths**:
   - Keep what worked in v1
   - Maintain idea intent
   - Don't lose good elements while improving

5. **Generate v2**:
   - Create improved script
   - Document all changes
   - Validate alignment with new title

## Output

- **Script v2** (improved version)
- **Change Rationale** (why changes were made)
- **Title Alignment Notes** (how it matches new title v2)
- **Review Response** (how feedback was addressed)
- **Updated Metadata**:
  - New timing estimates
  - Structure improvements
  - Quality metrics

## Key Principle

Uses **new title v2** so script aligns with the improved title, plus feedback from **both reviews** and building on **previous script v1**.

## Next Stage

Script v2 flows to:
- **Stage 8**: Rewiew.Title.ByScript (v2) (review improved title against improved script)
- **Stage 10**: Rewiew.Script.ByTitle (v2) (after title refinement cycle)

## Example Transformation

**Inputs:**
- Script v1: 145-second narrative with weak middle section
- Title v1: "The Mystery of the Abandoned House"
- Title v2 (NEW): "The House That Remembers"
- Script Review: "Too long (145s), middle drags, needs stronger paranormal angle"
- Title Review: "Title change emphasizes memory/time-loop - script should too"

**Process:**
1. Analyze new title focus: "remembers" implies memory/time-loop
2. Review v1 issues: length, pacing, paranormal underplayed
3. Restructure content:
   - Cut 30s from middle investigation
   - Strengthen memory/time-loop elements
   - Enhance paranormal atmosphere
   - Tighten pacing throughout

**Output:**
- Script v2: 115-second narrative focused on time-loop
- Change Rationale: "Aligned with title's memory theme, cut investigation bloat, strengthened paranormal elements"
- Title Alignment: "Script now emphasizes the house 'remembering' events"
- Review Response: "Reduced to 115s, improved pacing, enhanced paranormal angle"

## Module Metadata

**[→ View FromReviewAndNewTitleAndPreviousScript/_meta/docs/](./_meta/docs/)**
**[→ View FromReviewAndNewTitleAndPreviousScript/_meta/examples/](./_meta/examples/)**
**[→ View FromReviewAndNewTitleAndPreviousScript/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../README.md)** | **[→ Script/_meta](../_meta/)**
