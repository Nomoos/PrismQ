# Manual Test: 06 - PrismQ.T.Review.Content.From.Title.Idea

**Module**: PrismQ.T.Review.Content.From.Title.Idea  
**Script**: `_meta/scripts/06_PrismQ.T.Review.Content.From.Title.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Review the Content against the Title and the original Idea to assess alignment and quality. This is the second cross-review stage — it evaluates whether the content fulfills the promise of the title and stays true to the original concept.

---

## Prerequisites

- Step 05 (PrismQ.T.Review.Title.From.Content.Idea) has completed and Stories are in the correct state for content review
- Ollama is running with the required model
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Content.From.Title.Idea - CONTINUOUS MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Ollama starts** if not already running
4. **Database query** - Loads Content records ready for review (with Title and Idea context)
5. **For each record**:
   1. **AI reviews** the Content against the Title and Idea, analyzing:
      - Title alignment (how well content fulfills the title's promise)
      - Idea alignment (how well content stays true to the original concept)
      - Content quality (engagement, pacing, clarity, structure, impact)
      - Gap analysis (title promises vs content delivery)
   2. **Review object created** with alignment scores, quality scores, gap analysis, and improvement recommendations
6. **Review record saved** to database
7. **Story state updated** to next state
8. **Continuous loop** - processes next record or waits if none available

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.From.Title.Idea - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Database query** - Loads Content records ready for review
5. **AI performs review** of Content against Title and Idea
6. **New state displayed**:
   ```
   ========================================
   PrismQ.T.Review.Script.From.Title.Idea - PREVIEW MODE
   ========================================
   This mode is for TESTING. Reviews will NOT be saved.

   Script ID: [content-id]

   Alignment Scores:
   - Title Alignment: XX/100
   - Idea Alignment: XX/100

   Quality Scores:
   - Engagement: XX/100
   - Pacing: XX/100
   - Clarity: XX/100
   - Structure: XX/100
   - Impact: XX/100

   Gap Analysis:
   [analysis of title promises vs delivery]

   Priority Improvements:
   1. [HIGH] [improvement 1]
   2. [MEDIUM] [improvement 2]
   ...
   ========================================
   ```
7. **Log file written** with detailed processing info (check log file for detailed output)
8. **Script ends** (no database changes)

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\06_PrismQ.T.Review.Content.From.Title.Idea

REM Run in Preview Mode (recommended for testing - no database save)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

This module reads directly from the database. Ensure records in the correct state exist before running.

### Verify Records Ready for Content Review (SQLite)
```sql
SELECT s.id, s.state, t.text as title, substr(c.text, 1, 100) as content_preview
FROM Story s
JOIN Title t ON t.story_id = s.id
JOIN Content c ON c.story_id = s.id
WHERE s.state LIKE '%Review%Content%'
LIMIT 5;
```

---

## Success Criteria

- [ ] Module reads Content records ready for review from the database
- [ ] AI reviews Content against both Title and Idea context
- [ ] Title alignment score is calculated (0-100)
- [ ] Idea alignment score is calculated (0-100)
- [ ] Content quality scores are calculated (engagement, pacing, clarity, structure, impact)
- [ ] Gap analysis identifies title promises vs content delivery issues
- [ ] Improvements are prioritized by impact
- [ ] Review record is saved to the database (Run mode only)
- [ ] Story state is updated to the next state (Run mode only)
- [ ] Preview mode shows full review results without saving to database
- [ ] Log file is written with detailed output (Preview mode)
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 06_PrismQ.T.Review.Content.From.Title.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (record processed):
Story ID: [id]
Title: "[title text]"
Content Preview: [first 100 chars]
Idea: [first sentence]

### Review Results:
Title Alignment: XX/100
Idea Alignment: XX/100
Engagement: XX/100
Pacing: XX/100
Clarity: XX/100
Structure: XX/100
Impact: XX/100

### Gap Analysis Summary:
[main gaps identified]

### Priority Improvements:
1. [improvement]
2. [improvement]

### Database Written (Run mode only):
[confirm review was saved and story state updated]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
