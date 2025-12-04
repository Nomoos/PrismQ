# T-TEST-05: PrismQ.T.Review.Title.By.Script.Idea Manual Test

**Module**: PrismQ.T.Review.Title.By.Script.Idea  
**Script**: `_meta/scripts/05_PrismQ.T.Review.Title.By.Script.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Review the Title against the Script and original Idea to assess alignment. This is the first cross-review stage.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.By.Script.Idea - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Title, Script, and Idea IDs
4. **User provides** the three IDs or pastes objects
5. **AI performs review** analyzing:
   - Title-Script alignment (30%)
   - Title-Idea alignment (25%)
   - Engagement potential (25%)
   - SEO optimization (20%)
6. **Review object created** with fields:
   - `id`: Unique identifier
   - `title_id`: Reviewed Title reference
   - `script_id`: Script reference
   - `idea_id`: Idea reference
   - `alignment_score`: 0-100
   - `feedback`: Detailed feedback
   - `improvements`: List of suggested improvements
   - `keyword_mismatches`: Keywords in title not in script
7. **State set** to `PrismQ.T.Review.Script.By.Title.Idea`
8. **Database write** - Review object saved
9. **Review summary** displayed
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Review.Title.By.Script.Idea - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Reviews will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Title, Script, and Idea
5. **User provides** the inputs
6. **AI performs review**
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Title Review Results
   
   Title: "[title-text]"
   
   Scores:
   - Title-Script Alignment: XX/100
   - Title-Idea Alignment: XX/100
   - Engagement Potential: XX/100
   - SEO Optimization: XX/100
   - OVERALL: XX/100
   
   Feedback:
   [detailed feedback text]
   
   Suggested Improvements:
   1. [improvement 1]
   2. [improvement 2]
   ...
   
   Keyword Mismatches:
   - [keyword not found in script]
   
   Next State: PrismQ.T.Review.Script.By.Title.Idea
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\05_PrismQ.T.Review.Title.By.Script.Idea

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] Review analyzes Title against Script and Idea
- [ ] All score categories are populated (0-100)
- [ ] Feedback is meaningful and actionable
- [ ] Keyword mismatches are identified
- [ ] State transitions to `PrismQ.T.Review.Script.By.Title.Idea`
- [ ] Preview mode shows review without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-05 Review.Title.By.Script.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Title: "[title]"
Script: [brief description]
Idea: "[concept]"

### Review Scores:
- Title-Script: XX/100
- Title-Idea: XX/100
- Engagement: XX/100
- SEO: XX/100
- Overall: XX/100

### Key Feedback:
[main feedback points]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
