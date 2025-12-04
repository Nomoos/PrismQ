# T-TEST-14: PrismQ.T.Review.Script.Consistency Manual Test

**Module**: PrismQ.T.Review.Script.Consistency  
**Script**: `_meta/scripts/14_PrismQ.T.Review.Script.Consistency/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Style and consistency validation. Ensures uniform formatting, terminology, and style throughout the script.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Consistency - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script ID
4. **User provides** Script ID or pastes object
5. **AI performs consistency review**:
   - Terminology consistency
   - Formatting uniformity
   - Style guide adherence
   - Internal references check
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `consistency_score`: 0-100
   - `terminology_issues`: Inconsistent terms
   - `style_issues`: Style deviations
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Review.Script.Editing`
   - **FAIL**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Consistency analysis** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Consistency - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script
5. **User provides** the input
6. **AI performs consistency review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Consistency Review Results
   
   Script: [script-id]
   Consistency Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Terminology Issues:
   1. "[term1]" vs "[term2]" - used interchangeably
   2. "[term1]" - different capitalization
   ...
   
   Style Issues:
   1. [Section X]: Different heading style
   2. [Section Y]: Inconsistent list format
   ...
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Review.Script.Editing
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
cd _meta\scripts\14_PrismQ.T.Review.Script.Consistency

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Terminology inconsistencies are detected
- [ ] Style deviations are identified
- [ ] Consistency score reflects quality (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows issues without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-14 Review.Script.Consistency
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Script: [script-id]

### Consistency Review:
Score: XX/100
Decision: [PASS/FAIL]
Terminology Issues: [count]
Style Issues: [count]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
