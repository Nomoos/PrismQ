# T-TEST-12: PrismQ.T.Review.Script.Tone Manual Test

**Module**: PrismQ.T.Review.Script.Tone  
**Script**: `_meta/scripts/12_PrismQ.T.Review.Script.Tone/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Tone and voice consistency check. Ensures the script maintains consistent voice throughout.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Tone - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script ID
4. **User provides** Script ID or pastes object
5. **AI performs tone review**:
   - Voice consistency analysis
   - Tone appropriateness for audience
   - Emotional resonance check
   - Language level consistency
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `tone_score`: 0-100
   - `detected_tones`: List of tones found
   - `inconsistencies`: Tone shifts or issues
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Review.Script.Content`
   - **FAIL**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Tone analysis** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Tone - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script
5. **User provides** the input
6. **AI performs tone review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Tone Review Results
   
   Script: [script-id]
   Tone Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Detected Tones:
   - Primary: [tone] (XX%)
   - Secondary: [tone] (XX%)
   
   Tone Consistency:
   - Section 1: [tone]
   - Section 2: [tone]
   - Section 3: [tone]
   
   Inconsistencies Found: [count]
   1. [Section X]: Shifts from [tone1] to [tone2]
   ...
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Review.Script.Content
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
cd _meta\scripts\12_PrismQ.T.Review.Script.Tone

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Tone is detected accurately
- [ ] Inconsistencies are identified
- [ ] Tone score reflects consistency (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows analysis without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-12 Review.Script.Tone
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Script: [script-id]

### Tone Review:
Score: XX/100
Decision: [PASS/FAIL]
Primary Tone: [tone]
Inconsistencies: [count]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
