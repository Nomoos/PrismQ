# Refactor: State Naming Convention for Review Processes

## Summary
Refactor the process state naming convention to better reflect the input/output relationships and include Review-related processes that are currently missing from the folder structure.

## Current State
The current state names follow folder structure but lack Review-related processes:
- `PrismQ.T.Idea.Creation`
- `PrismQ.T.Title.FromIdea`
- `PrismQ.T.Title.FromOriginalTitleAndReviewAndScript`
- `PrismQ.T.Script.FromIdeaAndTitle`
- `PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle`
- `PrismQ.T.Publishing`

## Problem
1. **Missing Review processes** - There are no explicit states for Review generation
2. **Naming pattern inconsistency** - Current pattern doesn't clearly show input dependencies
3. **Review workflow gaps** - No states for:
   - Title review by Script content
   - Combined Title review by Script and Idea

## Proposed Refactoring

### New State Names (Proposed)
| Process | Proposed State Name | Inputs → Output |
|---------|---------------------|-----------------|
| Create Idea | `PrismQ.T.Idea.Creation` | ∅ → Idea |
| Create Title from Idea | `PrismQ.T.Title.By.Idea` | Idea → Title |
| Create Script from Title+Idea | `PrismQ.T.Script.By.Title.Idea` | Title, Idea → Script |
| Review Title by Script | `PrismQ.T.Review.Title.By.Script` | Script → TitleReview |
| Review Title by Script+Idea | `PrismQ.T.Review.Title.By.Script.Idea` | Script, Idea → TitleReview |
| Review Script by Title | `PrismQ.T.Review.Script.By.Title` | Title → ScriptReview |
| Iterate Title with Review | `PrismQ.T.Title.By.Review.Title` | TitleReview → Title |
| Iterate Script with Review | `PrismQ.T.Script.By.Review.Script` | ScriptReview → Script |
| Publishing | `PrismQ.T.Publishing` | Title, Script → Published |

### Naming Convention Pattern
```
PrismQ.T.<Output>.<Action>.By.<Input1>.<Input2>...
```

Where:
- `<Output>` = The entity being created/modified (Idea, Title, Script, Review)
- `<Action>` = Optional action type (Creation, Publishing)
- `<Input1>.<Input2>...` = Input dependencies in order of importance

## Tasks

### Phase 1: Folder Structure
- [ ] Create `T/Review/Title/` folder structure
- [ ] Create `T/Review/Title/By.Script/`
- [ ] Create `T/Review/Title/By.Script.Idea/`
- [ ] Create `T/Review/Script/By.Title/`

### Phase 2: Update State Names
- [ ] Update `DATABASE_DESIGN.md` with new state names
- [ ] Update `run_text_client.py` state constants
- [ ] Update batch scripts if needed
- [ ] Update `PARALLEL_RUN_NEXT.md` documentation

### Phase 3: Migration
- [ ] Create migration script for existing Story records
- [ ] Update state transition logic in client

## Benefits
1. **Clearer dependencies** - Input sources are explicit in the name
2. **Complete workflow** - Review processes are now included
3. **Consistent pattern** - All states follow `Output.By.Input` pattern
4. **Self-documenting** - State names describe what they do

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
