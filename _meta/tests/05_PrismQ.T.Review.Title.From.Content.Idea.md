# Manual Test: 05 - PrismQ.T.Review.Title.From.Content.Idea

**Module**: PrismQ.T.Review.Title.From.Content.Idea  
**Script**: `_meta/scripts/05_PrismQ.T.Review.Title.From.Content.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Review the Title against the generated Content and the original Idea. This is the first cross-review stage — it evaluates how well the Title represents both the content and the original concept.

---

## Prerequisites

- Step 04 (PrismQ.T.Content.From.Idea.Title) has been run and Stories/Content records exist in the correct state
- Ollama is running with the required model
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.From.Content.Idea - CONTINUOUS MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Ollama starts** if not already running
4. **Database query** - Loads records ready for title review (with Idea and Content context)
5. **For each record**:
   1. **AI reviews** the Title against the Content and Idea, analyzing alignment and quality
   2. **Review object created** with review scores and feedback
6. **Review record saved** to database
7. **Story state updated** to next state
8. **Continuous loop** - processes next record or waits if none available

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.From.Idea.Content - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Database query** - Loads records ready for review
5. **AI performs review** of Title against Content and Idea
6. **New state displayed**:
   ```
   ========================================
   PrismQ.T.Review.Title.From.Idea.Content - PREVIEW MODE
   ========================================
   This mode is for TESTING. Reviews will NOT be saved.

   Title: "[title text]"

   [Review scores and feedback...]

   ========================================
   ```
7. **Log file written** with detailed processing info (check log file for detailed output)
8. **Script ends** (no database changes)

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\05_PrismQ.T.Review.Title.From.Content.Idea

REM Run in Preview Mode (recommended for testing - no database save)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

This module reads directly from the database. Ensure records in the correct state exist before running.

### Verify Records Ready for Review (SQLite)
```sql
SELECT s.id, s.state, t.text as title, substr(c.text, 1, 100) as content_preview
FROM Story s
JOIN Title t ON t.story_id = s.id
JOIN Content c ON c.story_id = s.id
WHERE s.state LIKE '%Review%Title%'
LIMIT 5;
```

---

## Success Criteria

- [ ] Module reads records ready for title review from the database
- [ ] AI reviews the Title against both Content and Idea context
- [ ] Review scores are generated and meaningful
- [ ] Feedback is actionable
- [ ] Review record is saved to the database (Run mode only)
- [ ] Story state is updated to the next state (Run mode only)
- [ ] Preview mode shows review results without saving to database
- [ ] Log file is written with detailed output (Preview mode)
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 05_PrismQ.T.Review.Title.From.Content.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (record processed):
Story ID: [id]
Title: "[title text]"
Content Preview: [first 100 chars]
Idea: [first sentence]

### Review Results:
Scores: [list any scores shown]
Key Feedback: [main feedback points]

### Database Written (Run mode only):
[confirm review was saved and story state updated]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
