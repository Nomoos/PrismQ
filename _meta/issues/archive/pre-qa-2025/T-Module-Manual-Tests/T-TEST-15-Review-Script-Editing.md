# T-TEST-15: PrismQ.T.Review.Script.Editing Manual Test

**Module**: PrismQ.T.Review.Script.Editing  
**Script**: `_meta/scripts/15_PrismQ.T.Review.Script.Editing/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Final editing pass for polish. Focuses on readability improvements and final cleanup.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Editing - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script ID
4. **User provides** Script ID or pastes object
5. **AI performs editing review**:
   - Sentence flow optimization
   - Word choice improvements
   - Paragraph structure
   - Transition quality
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `editing_score`: 0-100
   - `flow_issues`: Sentence flow problems
   - `suggestions`: Editorial suggestions
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Review.Title.Readability`
   - **FAIL**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Editing suggestions** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Editing - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script
5. **User provides** the input
6. **AI performs editing review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Editing Review Results
   
   Script: [script-id]
   Editing Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Flow Issues:
   1. [Paragraph X]: Abrupt transition
   2. [Sentence Y]: Awkward phrasing
   ...
   
   Editorial Suggestions:
   1. "[original]" → "[improved]"
   2. "[original]" → "[improved]"
   ...
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Review.Title.Readability
   - If FAIL: PrismQ.T.Script.From.Title.Review.Script
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\15_PrismQ.T.Review.Script.Editing

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Flow issues are detected
- [ ] Editorial suggestions are meaningful
- [ ] Editing score reflects quality (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows suggestions without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-15 Review.Script.Editing
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Script: [script-id]

### Editing Review:
Score: XX/100
Decision: [PASS/FAIL]
Flow Issues: [count]
Suggestions: [count]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
