# T-TEST-19: PrismQ.T.Story.Polish Manual Test

**Module**: PrismQ.T.Story.Polish  
**Script**: `_meta/scripts/19_PrismQ.T.Story.Polish/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Expert-level GPT polish based on Story.Review feedback. Applies professional improvements to both Title and Script.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.Polish - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Story and Review feedback
4. **User provides** Story ID + Review ID or pastes objects
5. **GPT applies polish**:
   - Address all weaknesses from review
   - Enhance identified strengths
   - Improve overall quality
   - Maintain author voice
6. **Polish object created** with fields:
   - `id`: Unique identifier
   - `story_id`: Original Story reference
   - `review_id`: Review reference
   - `polished_title`: Improved title
   - `polished_script`: Improved script
   - `changes_made`: List of changes
   - `version`: Polish iteration number
7. **State set** to `PrismQ.T.Story.Review` (loops back for validation)
8. **Database write** - Polish object saved
9. **Changes summary** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.Polish - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Polish will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Story and Review
5. **User provides** the inputs
6. **GPT applies polish**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Story Polish Results
   
   Original Story: [story-id]
   Polish Version: [X]
   
   Title Changes:
   - Before: "[original-title]"
   - After: "[polished-title]"
   
   Script Changes Summary:
   - Total Changes: [count]
   - Word Count: [before] → [after]
   
   Changes Made:
   1. [Section X]: [change description]
   2. [Section Y]: [change description]
   ...
   
   Weaknesses Addressed:
   1. [weakness 1] - [how addressed]
   2. [weakness 2] - [how addressed]
   
   Next State: PrismQ.T.Story.Review (validation)
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Full diff** available in debug log
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\19_PrismQ.T.Story.Polish

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Polish addresses review weaknesses
- [ ] Changes are documented clearly
- [ ] Version tracking is correct
- [ ] Author voice is maintained
- [ ] State transitions to `PrismQ.T.Story.Review`
- [ ] Preview mode shows changes without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-19 Story.Polish
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Story: [story-id]
Review: [review-id]

### Polish Results:
Version: [X]
Total Changes: [count]

### Title:
- Before: "[title]"
- After: "[title]"

### Weaknesses Addressed:
1. [weakness] - [solution]
...

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
