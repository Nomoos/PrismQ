# T-TEST-17: PrismQ.T.Review.Script.Readability Manual Test

**Module**: PrismQ.T.Review.Script.Readability  
**Script**: `_meta/scripts/17_PrismQ.T.Review.Script.Readability/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Script readability and clarity check. Last quality review before expert review stage.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Readability - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script ID
4. **User provides** Script ID or pastes object
5. **AI performs readability review**:
   - Flesch-Kincaid analysis
   - Sentence length variety
   - Paragraph structure
   - Target audience fit
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `readability_score`: 0-100
   - `flesch_kincaid_grade`: Grade level
   - `avg_sentence_length`: Words per sentence
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Story.Review`
   - **FAIL**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Readability analysis** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Readability - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script
5. **User provides** the input
6. **AI performs readability review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Script Readability Results
   
   Script: [script-id]
   Readability Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Metrics:
   - Flesch-Kincaid Grade: [X.X]
   - Flesch Reading Ease: [X.X]
   - Average Sentence Length: [X words]
   - Average Word Length: [X chars]
   
   Sentence Length Distribution:
   - Short (< 10 words): XX%
   - Medium (10-20 words): XX%
   - Long (> 20 words): XX%
   
   Target Audience Fit: [Appropriate/Too Complex/Too Simple]
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Story.Review
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
cd _meta\scripts\17_PrismQ.T.Review.Script.Readability

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Readability metrics are calculated
- [ ] Flesch-Kincaid scores are accurate
- [ ] Audience fit is assessed
- [ ] Readability score reflects clarity (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows metrics without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-17 Review.Script.Readability
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Script: [script-id]

### Readability Review:
Score: XX/100
Decision: [PASS/FAIL]
Flesch-Kincaid Grade: [X.X]
Avg Sentence Length: [X words]
Target Audience Fit: [assessment]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
