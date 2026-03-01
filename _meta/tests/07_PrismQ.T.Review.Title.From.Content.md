# Manual Test: 07 - PrismQ.T.Review.Title.From.Content

**Module**: PrismQ.T.Review.Title.From.Content  
**Script**: `_meta/scripts/07_PrismQ.T.Review.Title.From.Content/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Review the Title against the Content for final alignment. This is a decision point — if the title is accepted, the workflow proceeds to content refinement; if rejected, the workflow loops back to title improvement (step 08).

---

## Prerequisites

- Steps 05 and 06 have completed and Stories are in the correct state for final title review
- Ollama is running with the required model
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.From.Content - CONTINUOUS MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Ollama starts** if not already running
4. **Database query** - Loads Title records ready for final review against their Content
5. **For each record**:
   1. **AI performs review** analyzing title-content alignment
   2. **Decision generated**: ACCEPTED or REJECTED
   3. **Review object created** with:
      - `alignment_score`: 0-100
      - `decision`: "ACCEPTED" or "REJECTED"
      - `feedback`: Detailed feedback
      - `rejection_reasons`: List of reasons (if rejected)
6. **Review record saved** to database
7. **Story state updated** based on decision:
   - **ACCEPTED**: Story advances to content refinement state
   - **REJECTED**: Story routes back to title improvement (step 08)
8. **Continuous loop** - processes next record or waits if none available

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.From.Script - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Database query** - Loads Title records ready for review
5. **AI performs review** of Title against Content
6. **New state displayed**:
   ```
   ========================================
   PrismQ.T.Review.Title.From.Script - PREVIEW MODE
   ========================================
   This mode is for TESTING. Reviews will NOT be saved.

   Title: "[title-text]"
   Alignment Score: XX/100

   *** DECISION: [ACCEPTED/REJECTED] ***

   Feedback:
   [detailed feedback text]

   [If REJECTED:]
   Rejection Reasons:
   1. [reason 1]
   2. [reason 2]

   Next State:
   - If ACCEPTED: [next accepted state]
   - If REJECTED: PrismQ.T.Title.From.Script.Review.Title (step 08)
   ========================================
   ```
7. **Log file written** with detailed processing info (check log file for detailed output)
8. **Script ends** (no database changes)

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\07_PrismQ.T.Review.Title.From.Content

REM Run in Preview Mode (recommended for testing - no database save)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

This module reads directly from the database. Ensure records in the correct state exist before running.

### Verify Records Ready for Final Title Review (SQLite)
```sql
SELECT s.id, s.state, t.text as title, substr(c.text, 1, 100) as content_preview
FROM Story s
JOIN Title t ON t.story_id = s.id
JOIN Content c ON c.story_id = s.id
WHERE s.state LIKE '%Review%Title%Content%'
LIMIT 5;
```

---

## Success Criteria

- [ ] Module reads Title records ready for final review from the database
- [ ] AI reviews Title against Content
- [ ] Alignment score is calculated (0-100)
- [ ] A clear ACCEPTED or REJECTED decision is produced
- [ ] If rejected, specific rejection reasons are provided
- [ ] Review record is saved to the database (Run mode only)
- [ ] Story state transitions correctly based on decision (Run mode only):
  - ACCEPTED → content refinement state
  - REJECTED → step 08 (title improvement)
- [ ] Preview mode shows decision without saving to database
- [ ] Log file is written with detailed output (Preview mode)
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 07_PrismQ.T.Review.Title.From.Content
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (record processed):
Story ID: [id]
Title: "[title text]"
Content Preview: [first 100 chars]

### Review Result:
Alignment Score: XX/100
Decision: [ACCEPTED/REJECTED]

### Rejection Reasons (if applicable):
1. [reason]
2. [reason]

### Next State:
[state name based on decision]

### Database Written (Run mode only):
[confirm review was saved and story state updated]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
