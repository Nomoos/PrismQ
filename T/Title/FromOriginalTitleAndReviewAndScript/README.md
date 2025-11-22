# T/Title/FromOriginalTitleAndReviewAndScript - All Title Improvements

**Namespace**: `PrismQ.T.Title.FromOriginalTitleAndReviewAndScript`

Generate improved title versions (v2, v3, v4, v5...) using review feedback, original title, and script context.

## Purpose

This state handles **ALL** title improvements and refinements after the initial v1. Whether it's the first improvement (v2), iterative refinements (v3+), or readability polish, all review-driven title updates happen here.

## Workflow Positions

This state is used in **multiple stages** throughout the workflow:

### Stage 6: First Improvements (v1 → v2)
**Using reviews from both title and script v1**
```
Stage 4: Rewiew.Title.ByScript (v1) ← Title review
Stage 5: Rewiew.Script.ByTitle (v1) ← Script review
    ↓
Stage 6: Title.FromOriginalTitleAndReviewAndScript (v1 → v2) ← THIS STATE
```

### Stage 9: Iterative Refinements (v2 → v3, v3 → v4, v4 → v5...)
**Using latest review feedback**
```
Stage 8: Rewiew.Title.ByScript (vN) ← Review latest
    ↓
Stage 9: Title.FromOriginalTitleAndReviewAndScript (vN → vN+1) ← THIS STATE
    ↓
Stage 12: Title Acceptance Check
    ↓ if NOT ACCEPTED, loop back to Stage 8 → Stage 9
```

### Stage 19 Feedback: Readability Polish (final version refinement)
**Using readability review feedback**
```
Stage 19: Rewiew.Title.Readability ← Final quality check
    ↓ if FAILS
Title.FromOriginalTitleAndReviewAndScript (polish) ← THIS STATE
```

## Input Components

### Always Present
- **Original Title Version** (v1, v2, v3... whatever is the starting point)
- **Review Feedback** (always present - from title review, script review, or readability review)
- **Current Script Version** (for context and alignment)

### Contextual
- **Original Idea** (for intent preservation)
- **Previous Review History** (for learning from iterations)
- **All Previous Title Versions** (for comparison)

## Review Types Handled

This state processes feedback from:

1. **Title Review by Script** (Stages 4, 8)
   - Title-script alignment
   - Accuracy vs script content
   - Engagement and clarity

2. **Script Review by Title** (Stages 5, 10)
   - Script promise vs title expectations
   - Insights relevant to title

3. **Title Readability Review** (Stage 19)
   - Clarity and scannability
   - Grammar/spelling
   - Length optimization
   - Engagement polish

## Process

### Common Steps (All Iterations)

1. **Analyze review feedback** (always present):
   - Extract specific issues
   - Prioritize critical vs nice-to-have
   - Understand acceptance/quality criteria

2. **Study original title**:
   - Identify what works
   - Understand what needs change
   - Review version history (avoid repeated mistakes)

3. **Ensure script alignment**:
   - Verify title matches script content
   - Check promises are deliverable
   - Maintain consistency with script message

4. **Apply improvements**:
   - Make targeted changes
   - Preserve successful elements
   - Address review concerns
   - Maintain idea intent

5. **Generate next version**:
   - Create improved title (vN+1)
   - Document changes and rationale
   - Prepare for next review cycle

### Variation by Stage

**Stage 6 (v1 → v2)**: Major improvements using both reviews
**Stage 9 (v2 → v3+)**: Iterative refinements until accepted
**Stage 19 Feedback**: Minimal readability polish only

## Output

- **Title vN+1** (next version)
- **Change Rationale** (why changes were made)
- **Script Alignment Notes** (how it matches current script)
- **Review Response** (how feedback was addressed)
- **Version Metadata** (version number, timestamp, iteration count)

## Key Principles

1. **Review Always Present**: Every title improvement is driven by review feedback
2. **Original Title Referenced**: Always builds on original version
3. **Script Alignment**: Always considers current script version
4. **Version Progression**: Clear v1 → v2 → v3 → v4... progression
5. **Iterative**: Can be called multiple times until accepted

## Example Progression

### Stage 6: First Improvement (v1 → v2)
**Inputs:**
- Original Title v1: "The Mystery of the Abandoned House"
- Script v1: Generic horror narrative
- Title Review: "Too generic, doesn't capture unique elements"
- Script Review: "Strong time-loop paranormal angle not in title"

**Process:**
- Extract unique element: time-loop paranormal
- Improve specificity and intrigue
- Align with script's paranormal focus

**Output:**
- Title v2: "The House That Remembers"

### Stage 9: Refinement (v2 → v3)
**Inputs:**
- Original Title v2: "The House That Remembers"
- Script v2: Enhanced with danger/threat elements
- Title Review: "Good memory theme, but script now has danger - add threat"

**Process:**
- Preserve "remembers" concept
- Add danger/threat element from script
- Maintain engagement

**Output:**
- Title v3: "The House That Remembers—And Hunts"

### Stage 9: Refinement (v3 → v4)
**Inputs:**
- Original Title v3: "The House That Remembers—And Hunts"
- Script v3: Polished version
- Title Review: "Excellent - minor preference: use colon not em dash"

**Process:**
- Keep core message
- Minor punctuation adjustment

**Output:**
- Title v4: "The House That Remembers: And Hunts"
- **ACCEPTED** ✓

### Stage 19 Feedback: Readability Polish
**Inputs:**
- Original Title v4: "The House That Remembers: And Hunts"
- Readability Review: "Colon may cause 'And' capitalization debate - consider lowercase"

**Process:**
- Minimal adjustment for clarity
- Maintain accepted version's strengths

**Output:**
- Title v4 (polished): "The House That Remembers: and Hunts"
- **READABILITY PASSED** ✓

## State Naming Logic

`FromOriginalTitleAndReviewAndScript` captures:
- **From Original Title**: Builds on previous version
- **And Review**: Always includes review feedback
- **And Script**: Always considers script context

This single state handles all the complexity of title evolution!

## Module Metadata

**[→ View FromOriginalTitleAndReviewAndScript/_meta/docs/](./_meta/docs/)**
**[→ View FromOriginalTitleAndReviewAndScript/_meta/examples/](./_meta/examples/)**
**[→ View FromOriginalTitleAndReviewAndScript/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../README.md)** | **[→ Title/_meta](../_meta/)**
