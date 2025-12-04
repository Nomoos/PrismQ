# T-TEST-08: PrismQ.T.Title.From.Script.Review.Title Manual Test

**Module**: PrismQ.T.Title.From.Script.Review.Title  
**Script**: `_meta/scripts/08_PrismQ.T.Title.From.Script.Review.Title/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Refine Title (v2+) based on Script and review feedback. Addresses issues identified in the review process.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Script.Review.Title - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for previous Title, Script, and Review feedback
4. **User provides** IDs or pastes objects
5. **AI processes** review feedback and generates improved title:
   - Analyzes feedback from both reviews (Title and Script reviews)
   - Identifies high-impact improvements
   - Prioritizes by impact score
6. **Title v2 object created** with fields:
   - `id`: Unique identifier
   - `version`: 2 (or higher)
   - `previous_version_id`: Reference to v1
   - `text`: New title text
   - `improvements_applied`: List of improvements
   - `alignment_score`: Improved score
   - `rationale`: Explanation of changes
7. **State set** to `PrismQ.T.Script.From.Title.Review.Script`
8. **Database write** - New Title version saved
9. **Comparison displayed** (v1 vs v2)
10. **Script ends**

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Script.Review.Title - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Improvements will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Title, Script, and Review
5. **User provides** the inputs
6. **AI generates** improved title
7. **New state displayed**:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Title Improvement: v1 → v2
   
   Previous Title (v1):
   "[old-title-text]"
   
   New Title (v2):
   "[new-title-text]"
   
   Improvements Applied:
   1. [improvement 1] - Impact: HIGH
   2. [improvement 2] - Impact: MEDIUM
   ...
   
   Score Improvement:
   - Alignment: [old] → [new] (+X)
   - Engagement: [old] → [new] (+X)
   
   Rationale:
   [explanation of changes]
   
   Next State: PrismQ.T.Script.From.Title.Review.Script
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\08_PrismQ.T.Title.From.Script.Review.Title

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Success Criteria

- [ ] New title version is generated from feedback
- [ ] High-impact improvements are applied first
- [ ] Version tracking is correct (v1 → v2)
- [ ] Rationale explains changes clearly
- [ ] State transitions to `PrismQ.T.Script.From.Title.Review.Script`
- [ ] Preview mode shows comparison without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-08 Title.From.Script.Review.Title
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Inputs:
Previous Title (v1): "[title]"
Review Feedback: [summary]

### Output:
New Title (v2): "[title]"
Version: 2

### Improvements Applied:
1. [improvement 1]
2. [improvement 2]
...

### Score Changes:
- Alignment: [old] → [new]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
