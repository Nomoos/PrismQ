# T/Title/FromReviewAndPreviousTitleAndScript - Title v2 Improvements

**Namespace**: `PrismQ.T.Title.FromReviewAndPreviousTitleAndScript`

Generate improved title (v2) using comprehensive context from both reviews and both v1 versions.

## Purpose

Create the second version (v2) of the title by analyzing feedback from **both** reviews (title and script) and considering **both** v1 versions (title and script).

## Workflow Position

**Stage 6** in MVP workflow: `PrismQ.T.Title.Improvements (v2)`

```
Stage 4: PrismQ.T.Rewiew.Title.ByScript (v1) ← Title review
    ↓
Stage 5: PrismQ.T.Rewiew.Script.ByTitle (v1) ← Script review
    ↓
Stage 6: PrismQ.T.Title.FromReviewAndPreviousTitleAndScript (v2) ← THIS STATE
    ↓
Stage 7: PrismQ.T.Script.FromReviewAndNewTitleAndPreviousScript (v2)
```

## Input Components

### Primary Inputs
- **Previous Title v1** (from Title.FromIdea)
- **Previous Script v1** (from Script.FromIdeaAndTitle)

### Review Feedback
- **Title Review Feedback** (from Stage 4: Rewiew.Title.ByScript)
  - Title-script alignment issues
  - Title accuracy vs script content
  - Engagement and clarity notes
  
- **Script Review Feedback** (from Stage 5: Rewiew.Script.ByTitle)
  - Script promise vs title expectations
  - Content delivery issues
  - Quality and flow notes

### Context
- **Original Idea** (for intent preservation)

## Process

1. **Analyze both review feedbacks**:
   - Identify title-specific issues from title review
   - Extract title-relevant insights from script review
   - Find cross-cutting themes

2. **Review previous versions**:
   - Study title v1 strengths and weaknesses
   - Understand script v1 content and structure
   - Identify alignment gaps

3. **Generate improvements**:
   - Create improved title variants
   - Ensure alignment with script v1 content
   - Address specific review feedback
   - Maintain idea intent

4. **Validate improvements**:
   - Check title accurately represents script
   - Verify engagement and clarity
   - Ensure SEO considerations

## Output

- **Title v2** (improved version)
- **Change Rationale** (why changes were made)
- **Alignment Notes** (how it matches script v1)
- **Review Response** (how feedback was addressed)

## Key Principle

Uses **both reviews** + **both v1 versions** + **original idea** for comprehensive context.

## Next Stage

Title v2 flows to:
- **Stage 7**: Script.FromReviewAndNewTitleAndPreviousScript (script improvements use new title v2)
- **Stage 8**: Rewiew.Title.ByScript (v2) (review of improved title against improved script)

## Example Transformation

**Input:**
- Title v1: "The Mystery of the Abandoned House"
- Script v1: 145-second horror narrative
- Title Review: "Title feels generic, doesn't capture the unique twist"
- Script Review: "Strong paranormal angle not reflected in title"

**Process:**
- Identify unique twist: time-loop paranormal element
- Extract key script elements: recurring midnight visitor
- Improve engagement and specificity

**Output:**
- Title v2: "The House That Remembers: A Midnight Visitor Returns"
- Change Rationale: "Captures paranormal time-loop element and creates intrigue"
- Alignment Notes: "Reflects the recurring midnight visitor from script"

## Module Metadata

**[→ View FromReviewAndPreviousTitleAndScript/_meta/docs/](./_meta/docs/)**
**[→ View FromReviewAndPreviousTitleAndScript/_meta/examples/](./_meta/examples/)**
**[→ View FromReviewAndPreviousTitleAndScript/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../README.md)** | **[→ Title/_meta](../_meta/)**
