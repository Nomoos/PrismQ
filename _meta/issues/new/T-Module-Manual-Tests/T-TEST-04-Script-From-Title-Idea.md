# T-TEST-04: PrismQ.T.Script.From.Title.Idea Manual Test

**Module**: PrismQ.T.Script.From.Title.Idea  
**Script**: `_meta/scripts/04_PrismQ.T.Script.From.Title.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Generate initial script (v1) from a Title and Idea combination. Creates the first draft of the content.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Script.From.Title.Idea - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Title and Idea (IDs or content)
4. **User provides** Title ID + Idea ID or pastes objects
5. **AI processes** the inputs and generates script structure:
   - Introduction/Hook
   - Main content sections
   - Conclusion
6. **Script object created** with fields:
   - `id`: Unique identifier
   - `title_id`: Reference to Title
   - `idea_id`: Reference to Idea
   - `version`: 1
   - `content`: Full script text
   - `sections`: Array of sections
   - `word_count`: Total words
7. **State set** to `PrismQ.T.Review.Title.By.Script.Idea`
8. **Database write** - Script object saved
9. **Success message** displayed with script preview
10. **Script ends** with word count summary

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Script.From.Title.Idea - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Scripts will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Title and Idea
5. **User provides** Title ID + Idea ID or pastes objects
6. **AI processes** and generates script
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Script v1 Generated
   
   Title: "[title-text]"
   Word Count: [count]
   
   --- INTRODUCTION ---
   [intro content preview...]
   
   --- SECTION 1 ---
   [section content preview...]
   
   --- CONCLUSION ---
   [conclusion content preview...]
   
   Next State: PrismQ.T.Review.Title.By.Script.Idea
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Full script** can be viewed in debug log
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\04_PrismQ.T.Script.From.Title.Idea

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

### By IDs
```
Title ID: title_12345
Idea ID: idea_12345
```

### By Content
```json
{
  "title": "The Weather Girl: How a Teenager Changed the Climate",
  "idea": {
    "concept": "A 16-year-old discovers she can control weather patterns",
    "target_audience": "Young adults 13-18"
  }
}
```

---

## Success Criteria

- [ ] Script v1 is generated from Title + Idea
- [ ] Script has proper structure (intro, sections, conclusion)
- [ ] Word count is appropriate (typically 800-2000 words)
- [ ] Script references Title and Idea IDs
- [ ] State transitions to `PrismQ.T.Review.Title.By.Script.Idea`
- [ ] Preview mode shows script preview without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-04 Script.From.Title.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Title: "[title]"
Idea: "[concept]"

### Script Generated:
Version: 1
Word Count: [count]

### Sections:
1. Introduction: [word count]
2. [Section name]: [word count]
...

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
