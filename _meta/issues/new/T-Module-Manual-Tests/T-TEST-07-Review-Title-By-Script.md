# T-TEST-07: PrismQ.T.Review.Title.By.Script Manual Test

**Module**: PrismQ.T.Review.Title.By.Script  
**Script**: `_meta/scripts/07_PrismQ.T.Review.Title.By.Script/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Review Title against Script for final alignment. This is a decision point - if not accepted, loops back for title refinement.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.By.Script - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Title and Script IDs
4. **User provides** the two IDs or pastes objects
5. **AI performs review** with decision:
   - Analyze title-script alignment
   - Generate accept/reject decision
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `title_id`: Reviewed Title reference
   - `script_id`: Script reference
   - `alignment_score`: 0-100
   - `decision`: "ACCEPTED" or "REJECTED"
   - `feedback`: Detailed feedback
   - `rejection_reasons`: List (if rejected)
7. **Decision branch**:
   - **ACCEPTED**: State set to `PrismQ.T.Review.Script.By.Title`
   - **REJECTED**: State set to `PrismQ.T.Title.From.Script.Review.Title`
8. **Database write** - Review object saved
9. **Decision displayed** with next steps
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.By.Script - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Title and Script
5. **User provides** the inputs
6. **AI performs review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Title Review Decision
   
   Title: "[title-text]"
   Alignment Score: XX/100
   
   *** DECISION: [ACCEPTED/REJECTED] ***
   
   Feedback:
   [detailed feedback text]
   
   [If REJECTED:]
   Rejection Reasons:
   1. [reason 1]
   2. [reason 2]
   
   Next State: [based on decision]
   - If ACCEPTED: PrismQ.T.Review.Script.By.Title
   - If REJECTED: PrismQ.T.Title.From.Script.Review.Title
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\07_PrismQ.T.Review.Title.By.Script

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Review analyzes Title against Script
- [ ] Alignment score is calculated (0-100)
- [ ] Accept/Reject decision is made
- [ ] If rejected, rejection reasons are provided
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows decision without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-07 Review.Title.By.Script
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Title: "[title]"
Script: [brief description]

### Review Result:
Alignment Score: XX/100
Decision: [ACCEPTED/REJECTED]

### Rejection Reasons (if applicable):
1. [reason]
...

### Next State:
[state name]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
