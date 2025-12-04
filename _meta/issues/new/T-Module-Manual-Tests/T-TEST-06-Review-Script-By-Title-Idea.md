# T-TEST-06: PrismQ.T.Review.Script.By.Title.Idea Manual Test

**Module**: PrismQ.T.Review.Script.By.Title.Idea  
**Script**: `_meta/scripts/06_PrismQ.T.Review.Script.By.Title.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Review the Script against the Title and original Idea to assess alignment and quality.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.By.Title.Idea - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Script, Title, and Idea IDs
4. **User provides** the three IDs or pastes objects
5. **AI performs review** analyzing:
   - Title alignment (25%)
   - Idea alignment (30%)
   - Content quality (45%): Engagement, Pacing, Clarity, Structure, Impact
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `script_id`: Reviewed Script reference
   - `title_id`: Title reference
   - `idea_id`: Idea reference
   - `alignment_scores`: Object with breakdown
   - `quality_scores`: Object with breakdown
   - `gap_analysis`: Title promises vs script delivery
   - `improvements`: Prioritized improvement recommendations
7. **State set** to `PrismQ.T.Review.Title.By.Script`
8. **Database write** - Review object saved
9. **Review summary** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Script.By.Title.Idea - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Script, Title, and Idea
5. **User provides** the inputs
6. **AI performs review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Script Review Results
   
   Script ID: [script-id]
   
   Alignment Scores:
   - Title Alignment: XX/100
   - Idea Alignment: XX/100
   
   Quality Scores:
   - Engagement: XX/100
   - Pacing: XX/100
   - Clarity: XX/100
   - Structure: XX/100
   - Impact: XX/100
   
   Gap Analysis:
   [analysis of title promises vs delivery]
   
   Priority Improvements:
   1. [HIGH] [improvement 1]
   2. [MEDIUM] [improvement 2]
   ...
   
   Next State: PrismQ.T.Review.Title.By.Script
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\06_PrismQ.T.Review.Script.By.Title.Idea

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Review analyzes Script against Title and Idea
- [ ] Alignment and quality scores are populated
- [ ] Gap analysis identifies promise vs delivery issues
- [ ] Improvements are prioritized
- [ ] State transitions to `PrismQ.T.Review.Title.By.Script`
- [ ] Preview mode shows review without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-06 Review.Script.By.Title.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Script: [brief description]
Title: "[title]"
Idea: "[concept]"

### Alignment Scores:
- Title: XX/100
- Idea: XX/100

### Quality Scores:
- Engagement: XX/100
- Pacing: XX/100
- Clarity: XX/100
- Structure: XX/100
- Impact: XX/100

### Gap Analysis Summary:
[main gaps identified]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
