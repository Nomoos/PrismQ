# T-TEST-18: PrismQ.T.Story.Review Manual Test

**Module**: PrismQ.T.Story.Review  
**Script**: `_meta/scripts/18_PrismQ.T.Story.Review/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Expert-level GPT review of the complete story (Title + Script + Context). Final quality gate before publishing.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.Review - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Story ID (Title + Script)
4. **User provides** Story ID or pastes complete story object
5. **GPT performs expert review**:
   - Holistic quality assessment
   - Professional standards check
   - Publication readiness evaluation
   - Audience impact prediction
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `story_id`: Reviewed Story reference
   - `expert_score`: 0-100
   - `quality_assessment`: Detailed assessment
   - `strengths`: List of strengths
   - `weaknesses`: List of weaknesses
   - `decision`: "ACCEPTED" or "NEEDS_POLISH"
7. **Decision branch**:
   - **ACCEPTED**: State set to `PrismQ.T.Publishing`
   - **NEEDS_POLISH**: State set to `PrismQ.T.Story.Polish`
8. **Database write** - Review object saved
9. **Expert assessment** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.Review - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Story
5. **User provides** the input
6. **GPT performs expert review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Expert Story Review
   
   Story: [story-id]
   Title: "[title-text]"
   Expert Score: XX/100
   
   *** DECISION: [ACCEPTED/NEEDS_POLISH] ***
   
   Quality Assessment:
   [detailed professional assessment]
   
   Strengths:
   1. [strength 1]
   2. [strength 2]
   3. [strength 3]
   
   Weaknesses (if any):
   1. [weakness 1]
   2. [weakness 2]
   
   Publication Readiness: [Ready/Needs Work]
   Audience Impact: [High/Medium/Low]
   
   Next State: [based on decision]
   - If ACCEPTED: PrismQ.T.Publishing
   - If NEEDS_POLISH: PrismQ.T.Story.Polish
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\18_PrismQ.T.Story.Review

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Expert review provides holistic assessment
- [ ] Strengths and weaknesses are identified
- [ ] Expert score is meaningful (0-100)
- [ ] Accept/Polish decision is appropriate
- [ ] State transitions correctly based on decision
- [ ] Preview mode shows assessment without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-18 Story.Review
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input:
Story: [story-id]
Title: "[title]"

### Expert Review:
Score: XX/100
Decision: [ACCEPTED/NEEDS_POLISH]
Strengths: [count]
Weaknesses: [count]

### Assessment Summary:
[key points from assessment]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
