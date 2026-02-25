# Manual Test: 01 - PrismQ.T.Idea.From.User

**Module**: PrismQ.T.Idea.From.User  
**Script**: `_meta/scripts/01_PrismQ.T.Idea.From.User/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Create structured Idea records from user-provided text input using AI with flavor variants (weighted random selection, 40% dual-flavor). This is the first stage of the T pipeline.

---

## Prerequisites

- Ollama is running with the required model
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Idea.From.User - Continuous Mode"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking user for idea input (text, title, concept, or JSON)
4. **User enters text** and presses Enter to submit
5. **AI selects** flavor variants (FlavorSelector, default 10, weighted random, 40% dual-flavor)
6. **AI processes** the input for each flavor and generates a 5-sentence refined idea
7. **For each flavor variant (1-10)**:
   - Idea object created with fields:
     - `id`: Unique identifier
     - `text`: AI-generated refined idea text (5 sentences)
     - `version`: 1
     - `created_at`: Timestamp
8. **Database write** - All Idea objects saved to `Idea` table immediately after each variant
9. **Success message** displayed with Idea IDs
10. **Continuous loop** - prompts for next idea or accepts "quit" to exit

---

## Expected Behavior (Preview Mode)

> **Note**: Step 01 runs `Run.bat` only (no separate `Preview.bat`). Use `Run.bat` for testing.

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Idea.From.User - Continuous Mode"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking user for idea input
4. **User enters text** and presses Enter to submit
5. **AI processes** the input and generates structured Idea objects
6. **Idea objects displayed** with generated content
7. **Database write** - Ideas are saved (Run mode saves to database)
8. **Continuous loop** - prompts for next idea or "quit"

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\01_PrismQ.T.Idea.From.User

REM Run in production mode (saves to database)
Run.bat
```

---

## Test Input Examples

### Simple Text Input
```
A story about a teenager who discovers she can control the weather
```

### Title + Description
```
The Weather Girl: A coming-of-age story about a 16-year-old who wakes up one day with the ability to control weather patterns
```

### JSON Input
```json
{
  "title": "The Weather Girl",
  "concept": "Teen discovers weather control powers",
  "target_audience": "Young adults 13-18",
  "content_goals": ["Entertainment", "Coming-of-age themes"]
}
```

---

## SQL Verification (db.s3db)

Run these queries after the script to confirm records were written to the correct tables.

### Ověření – naposledy přidané záznamy Idea
```sql
SELECT id, version, created_at, substr(text, 1, 80) AS text_preview
FROM Idea
ORDER BY created_at DESC
LIMIT 10;
```

### Ověření – naposledy přidané záznamy Inspiration (zdroj: user)
```sql
SELECT id, source, source_id, title, created_at
FROM Inspiration
WHERE source = 'user'
ORDER BY created_at DESC
LIMIT 10;
```

### Ověření – propojení IdeaInspiration (naposledy přidané)
```sql
SELECT ii.id, ii.idea_id, ii.inspiration_id, ii.created_at
FROM IdeaInspiration ii
ORDER BY ii.created_at DESC
LIMIT 10;
```

### Ověření – kompletní přehled (Idea + Inspiration dohromady)
```sql
SELECT
    i.id        AS idea_id,
    i.version,
    i.created_at AS idea_created_at,
    insp.source,
    insp.source_id,
    substr(i.text, 1, 80) AS text_preview
FROM Idea i
JOIN IdeaInspiration ii ON ii.idea_id = i.id
JOIN Inspiration insp ON insp.id = ii.inspiration_id
ORDER BY i.created_at DESC
LIMIT 10;
```

---

## Success Criteria

- [ ] 10 Idea objects are generated from a single input (one per flavor variant)
- [ ] Each Idea object contains a 5-sentence AI-refined idea text
- [ ] Each Idea has `version=1` and a unique `id`
- [ ] All Idea objects are saved to the `Idea` table in the database
- [ ] Next module (02 - PrismQ.T.Story.From.Idea) can pick up created Ideas
- [ ] Continuous loop prompts for next idea after completion
- [ ] "quit" command exits the loop cleanly
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 01_PrismQ.T.Idea.From.User
### Mode: Run
### Date: YYYY-MM-DD

### Input Used:
[paste input text]

### Ideas Generated:
Count: [number]
Sample Idea ID: [id]
Sample Idea Text: [first sentence of generated idea]

### Database Written:
Idea rows inserted:        [count, expected 10]
Inspiration rows inserted: [count, expected 1]
IdeaInspiration rows:      [count, expected 10]

### SQL Verification Results:
[paste output of the "kompletní přehled" query above]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
