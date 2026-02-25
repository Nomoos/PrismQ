# Manual Test: 02 - PrismQ.T.Story.From.Idea

**Module**: PrismQ.T.Story.From.Idea  
**Script**: `_meta/scripts/02_PrismQ.T.Story.From.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Create 10 Story objects from unprocessed Idea records in the database. Each Story is assigned the `PrismQ.T.Title.From.Idea` state, making it ready for title generation in the next step.

---

## Prerequisites

- Step 01 (PrismQ.T.Idea.From.User) has been run and Idea records exist in the database
- Database (`db.s3db`) is accessible with read and write permissions
- Ollama is **not** required for this step (no AI processing)

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.From.Idea - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Database query** - Loads the oldest unprocessed Idea (without Story references) from the `Idea` table
4. **10 Story objects created** for the selected Idea with fields:
   - `id`: Unique identifier
   - `idea_id`: Reference to the parent Idea
   - `state`: `PrismQ.T.Title.From.Idea`
   - `created_at`: Timestamp
   - `updated_at`: Timestamp
5. **Database write** - All 10 Story objects inserted into the `Story` table, transaction committed
6. **Success message** displayed with Story IDs
7. **Continuous loop** - waits 30 seconds if no new Ideas are available, otherwise 1ms before processing the next Idea
8. **Script ends** when stopped (Ctrl+C or close window)

---

## Expected Behavior (Preview Mode)

> **Note**: Step 02 runs `Run.bat` only (no separate `Preview.bat`). Use `Run.bat` for testing.

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\02_PrismQ.T.Story.From.Idea

REM Run in production mode (saves to database)
Run.bat
```

---

## Test Input Examples

This module reads directly from the database. Ensure Idea records exist before running.

### Verify Ideas Exist (SQLite)
```sql
SELECT id, text, created_at FROM Idea ORDER BY created_at ASC LIMIT 5;
```

### Verify Stories Created (SQLite)
```sql
SELECT id, idea_id, state, created_at FROM Story ORDER BY created_at DESC LIMIT 10;
```

---

## Success Criteria

- [ ] Module reads unprocessed Idea records from the database
- [ ] Exactly 10 Story objects are created per Idea
- [ ] Each Story has `idea_id` set to the parent Idea's `id`
- [ ] Each Story has `state="PrismQ.T.Title.From.Idea"`
- [ ] All 10 Story objects are inserted into the `Story` table
- [ ] Next module (03 - PrismQ.T.Title.From.Idea) can pick up created Stories
- [ ] Continuous loop waits 30s when no new Ideas are available
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 02_PrismQ.T.Story.From.Idea
### Mode: Run
### Date: YYYY-MM-DD

### Input (Idea processed):
Idea ID: [id]
Idea Text: [first sentence]

### Stories Generated:
Count: [number, expected 10]
Sample Story IDs: [id1, id2, ...]
Story State: [expected: PrismQ.T.Title.From.Idea]

### Database Written:
[confirm stories were saved, e.g. "10 rows inserted into Story table"]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
