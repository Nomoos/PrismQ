# T-TEST-09: PrismQ.T.Script.From.Title.Review.Script Manual Test

**Module**: PrismQ.T.Script.From.Title.Review.Script  
**Script**: `_meta/scripts/09_PrismQ.T.Script.From.Title.Review.Script/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Refine Script (v2+) based on Title and review feedback. This is used extensively throughout the workflow when script refinement is needed.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Script.From.Title.Review.Script - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for previous Script, Title, and Review feedback
4. **User provides** IDs or pastes objects
5. **AI processes** review feedback and generates improved script:
   - Analyzes all review feedback
   - Prioritizes improvements by impact
   - Preserves working elements
6. **Script v2 object created** with fields:
   - `id`: Unique identifier
   - `version`: 2 (or higher)
   - `previous_version_id`: Reference to v1
   - `content`: Improved script text
   - `improvements_applied`: List of improvements
   - `word_count`: Updated count
   - `changelog`: Summary of changes
7. **State set** to `PrismQ.T.Review.Title.By.Script`
8. **Database write** - New Script version saved
9. **Comparison displayed** (v1 vs v2 diff)
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Script.From.Title.Review.Script - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Improvements will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script, Title, and Review
5. **User provides** the inputs
6. **AI generates** improved script
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Script Improvement: v1 → v2
   
   Title: "[title-text]"
   
   Word Count: [old] → [new]
   
   Improvements Applied:
   1. [improvement 1] - Section: [section name]
   2. [improvement 2] - Section: [section name]
   ...
   
   Changelog:
   - [change 1]
   - [change 2]
   ...
   
   Preview of Changes:
   [section with changes highlighted]
   
   Next State: PrismQ.T.Review.Title.By.Script
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Full diff** available in debug log
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\09_PrismQ.T.Script.From.Title.Review.Script

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] New script version is generated from feedback
- [ ] Improvements are clearly documented
- [ ] Version tracking is correct
- [ ] Changelog summarizes changes
- [ ] State transitions to `PrismQ.T.Review.Title.By.Script`
- [ ] Preview mode shows improvements without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-09 Script.From.Title.Review.Script
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Previous Script (v1): [word count] words
Title: "[title]"
Review Feedback: [summary]

### Output:
New Script (v2): [word count] words
Version: 2

### Improvements Applied:
1. [improvement 1]
2. [improvement 2]
...

### Changelog:
- [change 1]
- [change 2]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
