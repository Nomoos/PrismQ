# Manual Test: 08 - PrismQ.T.Title.From.Title.Review.Content

**Module**: PrismQ.T.Title.From.Script.Review.Title  
**Script**: `_meta/scripts/08_PrismQ.T.Title.From.Title.Review.Content/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Refine the Title (creating v2+) based on the Content and review feedback. This step is reached when step 07 rejects the current title. The AI analyzes the review feedback, applies high-impact improvements, and generates an improved title version.

---

## Prerequisites

- Step 07 (PrismQ.T.Review.Title.From.Content) has rejected a Title and Stories are routed to this step
- Ollama is running with the required model
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Script.Review.Title - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Database query** - Loads records requiring title improvement (previous title + content + review feedback)
4. **For each record**:
   1. **AI processes** the review feedback from step 07
   2. **High-impact improvements identified** and prioritized
   3. **New title (v2+) generated** incorporating the improvements
   4. **Improved title object created** with:
      - `version`: 2 (or higher if multiple iterations)
      - `text`: New improved title text
      - `improvements_applied`: List of improvements from feedback
      - `alignment_score`: Updated score
      - `rationale`: Explanation of changes made
5. **Title record saved** to database with incremented version
6. **Story state updated** to re-enter the review loop (loops back toward step 05 or 07)
7. **Continuous loop** - processes next record or waits if none available

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Script.Review.Title - PREVIEW MODE"
2. **Preview mode** with extensive logging enabled
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Database query** - Loads records requiring title improvement
5. **AI generates** improved title from review feedback
6. **New state displayed**:
   ```
   ========================================
   PrismQ.T.Title.From.Script.Review.Title - PREVIEW MODE
   ========================================
   Preview mode with extensive logging enabled

   Previous Title (v1):
   "[old-title-text]"

   New Title (v2):
   "[new-title-text]"

   Improvements Applied:
   1. [improvement 1] - Impact: HIGH
   2. [improvement 2] - Impact: MEDIUM
   ...

   Score Improvement:
   - Alignment: [old] → [new] (+X)
   - Engagement: [old] → [new] (+X)

   Rationale:
   [explanation of changes]
   ========================================
   ```
7. **Log file written** with detailed processing info (check log file for detailed output)
8. **Script ends** (no database changes)

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\08_PrismQ.T.Title.From.Title.Review.Content

REM Run in Preview Mode (recommended for testing - no database save)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

This module reads directly from the database. Ensure records routed from step 07 (rejected titles) exist before running.

### Verify Records Requiring Title Improvement (SQLite)
```sql
SELECT s.id, s.state, t.text as current_title, substr(c.text, 1, 100) as content_preview
FROM Story s
JOIN Title t ON t.story_id = s.id
JOIN Content c ON c.story_id = s.id
WHERE s.state LIKE '%Title%Review%'
LIMIT 5;
```

### Verify New Title Version Created (SQLite)
```sql
SELECT id, story_id, version, text
FROM Title
ORDER BY version DESC, rowid DESC
LIMIT 10;
```

---

## Success Criteria

- [ ] Module reads records requiring title improvement from the database
- [ ] AI processes review feedback from the previous review step
- [ ] High-impact improvements are identified and prioritized
- [ ] New title version (v2+) is generated incorporating improvements
- [ ] Rationale explains the changes made
- [ ] Version number is incremented correctly (v1 → v2, v2 → v3, etc.)
- [ ] New Title record saved to the database (Run mode only)
- [ ] Story state is updated to re-enter the review loop (Run mode only)
- [ ] Preview mode shows title comparison (old vs new) without saving to database
- [ ] Log file is written with detailed output (Preview mode)
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 08_PrismQ.T.Title.From.Title.Review.Content
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (record processed):
Story ID: [id]
Previous Title (v1): "[old title]"
Review Feedback Summary: [brief description of what was rejected]

### Output:
New Title (v2): "[new title]"
Version: [expected: 2]

### Improvements Applied:
1. [improvement 1]
2. [improvement 2]

### Score Changes:
- Alignment: [old] → [new]
- Engagement: [old] → [new]

### Rationale:
[brief explanation]

### Database Written (Run mode only):
[confirm new title version was saved and story state updated]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
