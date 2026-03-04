# T-TEST-13: PrismQ.T.Review.Script.Content Manual Test

**Module**: PrismQ.T.Review.Script.Content  
**Script**: `_meta/scripts/13_PrismQ.T.Review.Script.Content/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Content accuracy and relevance validation. Ensures the script delivers on the original idea promises.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Content - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script and Idea IDs
4. **User provides** IDs or pastes objects
5. **AI performs content review**:
   - Idea alignment check
   - Content completeness
   - Factual accuracy (if applicable)
   - Value delivery assessment
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `idea_id`: Original Idea reference
   - `content_score`: 0-100
   - `alignment_gaps`: Missing elements from idea
   - `accuracy_issues`: Factual concerns
   - `decision`: "PASS" or "FAIL"
7. **Decision branch**:
   - **PASS**: State set to `PrismQ.T.Review.Script.Consistency`
   - **FAIL**: State set to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - Review object saved
9. **Content analysis** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.Content - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script and Idea
5. **User provides** the inputs
6. **AI performs content review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Content Review Results
   
   Script: [script-id]
   Idea: [idea-id]
   Content Score: XX/100
   
   *** DECISION: [PASS/FAIL] ***
   
   Idea Alignment:
   - Concept Coverage: XX%
   - Goal Achievement: XX%
   - Audience Fit: XX%
   
   Alignment Gaps:
   1. [missing element from idea]
   2. [missing element from idea]
   
   Accuracy Issues:
   1. [issue description]
   ...
   
   Next State: [based on decision]
   - If PASS: PrismQ.T.Review.Script.Consistency
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
cd _meta\scripts\13_PrismQ.T.Review.Script.Content

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Content is validated against original Idea
- [ ] Alignment gaps are identified
- [ ] Accuracy issues are flagged
- [ ] Content score reflects quality (0-100)
- [ ] Pass/Fail decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows analysis without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-13 Review.Script.Content
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Script: [script-id]
Idea: [idea-id]

### Content Review:
Score: XX/100
Decision: [PASS/FAIL]
Concept Coverage: XX%
Alignment Gaps: [count]
Accuracy Issues: [count]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
