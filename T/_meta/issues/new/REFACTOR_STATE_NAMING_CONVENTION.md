# Refactor: State Naming Convention for Review Processes

## Summary
Refactor the process state naming convention to better reflect the input/output relationships and include Review-related processes that are currently missing from the folder structure.

## Current State
The current state names follow folder structure but lack Review-related processes:
- `PrismQ.T.Idea.Creation`
- `PrismQ.T.Title.From.Idea`
- `PrismQ.T.Title.From.Title.Review.Script`
- `PrismQ.T.Content.FromIdeaAndTitle`
- `PrismQ.T.Content.FromOriginalScriptAndReviewAndTitle`
- `PrismQ.T.Publishing`

## Problem
1. **Missing Review processes** - There are no explicit states for Review generation
2. **Naming pattern inconsistency** - Current pattern doesn't clearly show input dependencies
3. **Review workflow gaps** - No states for:
   - Title review from Script content
   - Script review from Title content

## Proposed Refactoring

### Naming Convention Pattern
```
PrismQ.T.<Output>.From.<Input1>.<Input2>...
```

Where:
- `<Output>` = The entity being created/modified (Idea, Title, Script, Review)
- `From` = Indicates input sources follow
- `<Input1>.<Input2>...` = Input dependencies that create the output

### New State Names (Proposed)
| Process | Proposed State Name | Inputs → Output |
|---------|---------------------|-----------------|
| Create Idea | `PrismQ.T.Idea.Creation` | ∅ → Idea |
| Create Title from Idea | `PrismQ.T.Title.From.Idea` | Idea → Title |
| Create Script from Idea+Title | `PrismQ.T.Content.From.Idea.Title` | Idea, Title → Script |
| Review Title (using Script) | `PrismQ.T.Review.Title.From.Script` | Script → TitleReview |
| Review Script (using Title) | `PrismQ.T.Review.Script.From.Title` | Title → ScriptReview |
| Iterate Title (from original + script + review) | `PrismQ.T.Title.From.Script.Review.Title` | Title, Script, TitleReview → Title v2 |
| Iterate Script (from original + title + review) | `PrismQ.T.Content.From.Title.Review.Script` | Script, Title, ScriptReview → Script v2 |
| Publishing | `PrismQ.T.Publishing` | Title, Script → Published |

### Key Examples
```
PrismQ.T.Title.From.Idea
  → Creating a new title from the idea

PrismQ.T.Content.From.Idea.Title
  → Creating a new script from idea and title

PrismQ.T.Review.Title.From.Script
  → Creating a title review based on the script

PrismQ.T.Title.From.Script.Review.Title
  → Creating a new title version from the original title, script, and title review

PrismQ.T.Content.From.Title.Review.Script
  → Creating a new script version from the original script, title, and script review
```

## Tasks

### Phase 1: Folder Structure
- [ ] Create `T/Title/From/Idea/`
- [ ] Create `T/Title/From/Script/Review/Title/`
- [ ] Create `T/Script/From/Idea/Title/`
- [ ] Create `T/Script/From/Title/Review/Script/`
- [ ] Create `T/Review/Title/From/Script/`
- [ ] Create `T/Review/Script/From/Title/`

### Phase 2: Update State Names
- [ ] Update `DATABASE_DESIGN.md` with new state names
- [ ] Update `run_text_client.py` state constants
- [ ] Update batch scripts if needed
- [ ] Update `PARALLEL_RUN_NEXT.md` documentation

### Phase 3: Migration
- [ ] Create migration script for existing Story records
- [ ] Update state transition logic in client

## Benefits
1. **Clearer dependencies** - Input sources are explicit in the name with `From`
2. **Complete workflow** - Review processes are now included
3. **Consistent pattern** - All states follow `Output.From.Input` pattern
4. **Self-documenting** - State names describe what they produce from what inputs

## Related Files
- `T/_meta/docs/DATABASE_DESIGN.md`
- `T/_meta/scripts/run_text_client.py`
- `T/_meta/scripts/README.md`
- `_meta/issues/PARALLEL_RUN_NEXT.md`

## Priority
Medium - Non-blocking for current implementation but improves maintainability

## Labels
- `refactor`
- `naming-convention`
- `documentation`
