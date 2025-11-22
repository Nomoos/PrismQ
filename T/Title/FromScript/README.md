# T/Title/FromScript - Title Improvements from Script Review

**Namespace**: `PrismQ.T.Title.FromScript`

Generate improved title (v2) based on feedback from script and title reviews.

## Purpose

Create the second version (v2) of the title using insights from both the title review (by script context) and script review (by title context).

## Workflow Position

**Stage 6** in MVP workflow: `PrismQ.T.Title.Improvements (v2)`

```
PrismQ.T.Rewiew.Title.ByScript (v1)
    ↓
PrismQ.T.Rewiew.Script.ByTitle (v1)
    ↓
PrismQ.T.Title.FromScript (v2) ← Improvements using both reviews
    ↓
PrismQ.T.Script.Improvements (v2)
```

## Input

- Title v1 (from FromIdea)
- Script v1 (from Script.FromIdea)
- Title review feedback (from Rewiew.Title.ByScript)
- Script review feedback (from Rewiew.Script.ByTitle)
- Original idea (for context)

## Process

1. Analyze feedback from both reviews
2. Identify title-script alignment issues
3. Consider script content and structure
4. Generate improved title variants
5. Ensure title matches script promises

## Output

- Title v2 (improved version)
- Change rationale
- Alignment notes with script v1

## Key Principle

Uses **both reviews** + **v1 versions** for context to create title that better aligns with script content.

## Next Stage

Title v2 is used in:
- **Stage 7**: Script.FromTitle (script improvements use new title v2)
- **Stage 8**: Rewiew.Title.ByScript (v2) (review of improved title)

## Module Metadata

**[→ View FromScript/_meta/docs/](./_meta/docs/)**
**[→ View FromScript/_meta/examples/](./_meta/examples/)**
**[→ View FromScript/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../README.md)** | **[→ Title/_meta](../_meta/)**
