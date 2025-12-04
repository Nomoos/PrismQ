# T-TEST-10: PrismQ.T.Review.Script.By.Title Manual Test

**Module**: PrismQ.T.Review.Script.By.Title  
**Script**: `_meta/scripts/10_PrismQ.T.Review.Script.By.Title/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Final review of Script against finalized Title. This is a decision point for entering the quality review stages.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.By.Title - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script and Title IDs
4. **User provides** the two IDs or pastes objects
5. **AI performs review** with decision:
   - Analyze script-title alignment
   - Check content completeness
   - Generate accept/reject decision
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `title_id`: Title reference
   - `alignment_score`: 0-100
   - `completeness_score`: 0-100
   - `decision`: "ACCEPTED" or "REJECTED"
   - `feedback`: Detailed feedback
7. **Decision branch**:
   - **ACCEPTED**: State set to `PrismQ.T.Review.Script.Grammar`
   - **REJECTED**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Decision displayed** with next steps
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.By.Title - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script and Title
5. **User provides** the inputs
6. **AI performs review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Script Review Decision
   
   Title: "[title-text]"
   Script Version: [version]
   
   Scores:
   - Alignment: XX/100
   - Completeness: XX/100
   
   *** DECISION: [ACCEPTED/REJECTED] ***
   
   Feedback:
   [detailed feedback text]
   
   Next State: [based on decision]
   - If ACCEPTED: PrismQ.T.Review.Script.Grammar
   - If REJECTED: PrismQ.T.Script.From.Title.Review.Script
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\10_PrismQ.T.Review.Script.By.Title

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Review analyzes Script against Title
- [ ] Alignment and completeness scores are calculated
- [ ] Accept/Reject decision is made
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows decision without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-10 Review.Script.By.Title
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Script: [version] - [word count] words
Title: "[title]"

### Review Result:
- Alignment: XX/100
- Completeness: XX/100
Decision: [ACCEPTED/REJECTED]

### Next State:
[state name]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
