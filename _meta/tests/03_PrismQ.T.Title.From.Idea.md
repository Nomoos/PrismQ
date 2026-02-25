# Manual Test: 03 - PrismQ.T.Title.From.Idea

**Module**: PrismQ.T.Title.From.Idea  
**Script**: `_meta/scripts/03_PrismQ.T.Title.From.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

AI-generate title variants for Story objects using a two-stage quality evaluation (rule-based scoring + AI scoring 0-100). The best title variant is selected and saved; the Story advances to the `PrismQ.T.Content.From.Idea.Title` state.

---

## Prerequisites

- Step 02 (PrismQ.T.Story.From.Idea) has been run and Story records in state `PrismQ.T.Title.From.Idea` exist in the database
- Ollama is running with the `qwen2.5:14b-instruct` model (or configured model)
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Idea - CONTINUOUS MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Ollama starts** if not already running
4. **Database query** - Loads Stories in state `PrismQ.T.Title.From.Idea` along with their parent Idea text
5. **For each Story**:
   1. **AI generates 10 title variants** with random temperature (0.6–0.8) for creative diversity
   2. **Rule-based scoring** applied to each variant (TitleScorer):
      - Ideal length 40-60 chars → 0.95
      - Good length 35-65 chars → 0.90
      - Short titles → 0.80
      - Acceptable 66-69 chars → 0.82
      - Too long 70+ chars → 0.75
   3. **AI scoring** applied to each variant using `title_scoring.txt` prompt template (temperature=0.1), evaluating: readability, keywords, emotional impact, SEO, literary quality → score 0-100 normalized to 0.0–1.0
   4. **Combined score** = 50% rule-based + 50% AI score; variants ranked highest first
   5. **Best variant selected** accounting for sibling Story title similarity (Jaccard similarity, threshold 0.7)
6. **Database write** - New `Title` record inserted (`story_id`, `version=0`, `text`); Story state updated to `PrismQ.T.Content.From.Idea.Title`
7. **Continuous loop** - processes next Story immediately or waits if none available

---

## Expected Behavior (Preview Mode)

> **Note**: Step 03 runs `Run.bat` only (no separate `Preview.bat`). Use `Run.bat` for testing.

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\03_PrismQ.T.Title.From.Idea

REM Run in production mode (saves to database)
Run.bat

REM Optionally specify database path
Run.bat C:\path\to\db.s3db
```

---

## Test Input Examples

This module reads directly from the database. Ensure Story records in the correct state exist before running.

### Verify Stories in Correct State (SQLite)
```sql
SELECT s.id, s.state, i.text
FROM Story s
JOIN Idea i ON s.idea_id = i.id
WHERE s.state = 'PrismQ.T.Title.From.Idea'
LIMIT 5;
```

### Verify Titles Created (SQLite)
```sql
SELECT t.id, t.story_id, t.version, t.text
FROM Title t
ORDER BY t.rowid DESC
LIMIT 10;
```

---

## Success Criteria

- [ ] 10 title variants are generated per Story using AI
- [ ] Each variant has a rule-based score applied
- [ ] Each variant has an AI quality score applied (0-100)
- [ ] Combined score = 50% rule-based + 50% AI score
- [ ] Best variant is selected considering sibling similarity (Jaccard threshold 0.7)
- [ ] Title record saved to `Title` table with `version=0`
- [ ] Story state updated to `PrismQ.T.Content.From.Idea.Title`
- [ ] Next module (04 - PrismQ.T.Content.From.Idea.Title) can pick up updated Stories
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 03_PrismQ.T.Title.From.Idea
### Mode: Run
### Date: YYYY-MM-DD

### Input (Story processed):
Story ID: [id]
Idea Text: [first sentence]

### Title Generated:
Title Text: "[generated title]"
Version: 0
Combined Score: [e.g. 0.87]

### Database Written:
[confirm title was saved and story state updated]
Story New State: [expected: PrismQ.T.Content.From.Idea.Title]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
