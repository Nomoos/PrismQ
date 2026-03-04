# T-TEST-11: PrismQ.T.Review.Script.Grammar Manual Test

**Module**: PrismQ.T.Review.Script.Grammar  
**Script**: `_meta/scripts/11_PrismQ.T.Review.Script.Grammar/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Grammar and syntax validation of the script. First stage of the Local AI Quality Reviews.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Grammar - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script ID
4. **User provides** Script ID or pastes object
5. **AI performs grammar review**:
   - Spelling check
   - Grammar validation
   - Punctuation check
   - Sentence structure analysis
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `grammar_score`: 0-100
   - `issues`: List of grammar issues found
   - `corrections`: Suggested corrections
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Review.Script.Tone`
   - **FAIL**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Issues summary** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Grammar - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script
5. **User provides** the input
6. **AI performs grammar review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Grammar Review Results
   
   Script: [script-id]
   Grammar Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Issues Found: [count]
   
   1. [Line X]: "[original]"
      Issue: [description]
      Correction: "[corrected]"
   
   2. [Line X]: "[original]"
      Issue: [description]
      Correction: "[corrected]"
   ...
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Review.Script.Tone
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
cd _meta\scripts\11_PrismQ.T.Review.Script.Grammar

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Grammar issues are detected accurately
- [ ] Corrections are meaningful and correct
- [ ] Grammar score reflects quality (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows issues without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-11 Review.Script.Grammar
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Script: [script-id]

### Grammar Review:
Score: XX/100
Decision: [PASS/FAIL]
Issues Found: [count]

### Sample Issues:
1. [issue description]
2. [issue description]
...

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
