# T-TEST-16: PrismQ.T.Review.Title.Readability Manual Test

**Module**: PrismQ.T.Review.Title.Readability  
**Script**: `_meta/scripts/16_PrismQ.T.Review.Title.Readability/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Title readability and clarity check. Ensures the title is easy to understand and remember.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.Readability - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Title ID
4. **User provides** Title ID or pastes object
5. **AI performs readability review**:
   - Length appropriateness
   - Word complexity
   - Clarity assessment
   - Memorability check
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `title_id`: Reviewed Title reference
   - `readability_score`: 0-100
   - `length_assessment`: Short/Optimal/Long
   - `complexity_issues`: Complex words
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Review.Script.Readability`
   - **FAIL**: State set to `PrismQ.T.Title.From.Script.Review.Title`
8. **Database write** - Review object saved
9. **Readability analysis** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.Readability - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Title
5. **User provides** the input
6. **AI performs readability review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Title Readability Results
   
   Title: "[title-text]"
   Readability Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Analysis:
   - Length: [X chars] - [Short/Optimal/Long]
   - Word Count: [X words]
   - Average Word Length: [X chars]
   
   Complexity Issues:
   1. "[complex-word]" - Consider simpler alternative
   ...
   
   Memorability: [High/Medium/Low]
   Clarity: [High/Medium/Low]
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Review.Script.Readability
   - If FAIL: PrismQ.T.Title.From.Script.Review.Title
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\16_PrismQ.T.Review.Title.Readability

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Readability is assessed accurately
- [ ] Complex words are identified
- [ ] Length is evaluated appropriately
- [ ] Readability score reflects clarity (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows analysis without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-16 Review.Title.Readability
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Title: "[title]"

### Readability Review:
Score: XX/100
Decision: [PASS/FAIL]
Length: [X chars]
Complexity Issues: [count]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
