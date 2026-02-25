# Manual Test: 04 - PrismQ.T.Content.From.Idea.Title

**Module**: PrismQ.T.Content.From.Idea.Title  
**Script**: `_meta/scripts/04_PrismQ.T.Content.From.Idea.Title/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Generate the initial content (script/article draft) from a Story's Title and parent Idea. This creates the first version of the content that will proceed through the review pipeline.

---

## Prerequisites

- Step 03 (PrismQ.T.Title.From.Idea) has been run and Stories in state `PrismQ.T.Content.From.Idea.Title` exist in the database
- Ollama is running with the required model
- Database (`db.s3db`) is accessible

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Content.From.Idea.Title - CONTINUOUS MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Ollama starts** if not already running
4. **Database query** - Loads Stories in state `PrismQ.T.Content.From.Idea.Title` along with their Title and Idea records
5. **For each Story**:
   1. **AI generates content** using the Title and Idea as context
   2. **Content object created** with structured sections:
      - Introduction/Hook
      - Main content sections
      - Conclusion
6. **Content record saved** to database with fields:
   - `story_id`: Reference to Story
   - `title_id`: Reference to Title
   - `version`: initial version
   - `text`: Full generated content
7. **Story state updated** to next review state
8. **Continuous loop** - processes next Story or waits if none available

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Content.From.Idea.Title - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Content will NOT be saved."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Database query** - Loads Stories in the correct state
5. **AI generates content** using Title and Idea
6. **New state displayed**:
   ```
   ========================================
   PrismQ.T.Content.From.Idea.Title - PREVIEW MODE
   ========================================
   This mode is for TESTING. Content will NOT be saved.

   [Generated content preview...]

   ========================================
   ```
7. **Log file written** with detailed processing info
8. **Script ends** (no database changes)

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\04_PrismQ.T.Content.From.Idea.Title

REM Run in Preview Mode (recommended for testing - no database save)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

This module reads directly from the database. Ensure Story records in the correct state exist before running.

### Verify Stories in Correct State (SQLite)
```sql
SELECT s.id, s.state, t.text as title, i.text as idea
FROM Story s
JOIN Title t ON t.story_id = s.id
JOIN Idea i ON s.idea_id = i.id
WHERE s.state = 'PrismQ.T.Content.From.Idea.Title'
LIMIT 5;
```

### Verify Content Created (SQLite)
```sql
SELECT id, story_id, version, substr(text, 1, 100) as preview
FROM Content
ORDER BY rowid DESC
LIMIT 5;
```

---

## Success Criteria

- [ ] Module reads Stories in state `PrismQ.T.Content.From.Idea.Title` from the database
- [ ] Content is generated using both the Title and Idea as context
- [ ] Content has a proper structure (introduction, main sections, conclusion)
- [ ] Content record is saved to the `Content` table (Run mode only)
- [ ] Story state is updated to the next state (Run mode only)
- [ ] Preview mode shows generated content without saving to database
- [ ] Log file is written with detailed output (Preview mode)
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: 04_PrismQ.T.Content.From.Idea.Title
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (Story processed):
Story ID: [id]
Title: "[title text]"
Idea: [first sentence of idea]

### Content Generated:
Word Count: [approximate]
Sections: [list sections found, e.g. Introduction, Section 1, Conclusion]
Preview (first 200 chars): "[content preview]"

### Database Written (Run mode only):
[confirm content was saved and story state updated]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2026-02-25
