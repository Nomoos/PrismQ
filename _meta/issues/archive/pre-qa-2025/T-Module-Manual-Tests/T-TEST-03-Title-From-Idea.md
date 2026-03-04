# T-TEST-03: PrismQ.T.Title.From.Idea Manual Test

**Module**: PrismQ.T.Title.From.Idea  
**Script**: `_meta/scripts/03_PrismQ.T.Title.From.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Generate initial title variants (v1) from an Idea. Produces multiple title options with SEO considerations.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Idea - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Idea ID or content
4. **User provides** Idea ID or pastes Idea object
5. **AI processes** the Idea using 10 generation strategies:
   - Direct, Question, How-to, Curiosity, Authoritative
   - Listicle, Problem-Solution, Comparison, Ultimate-Guide, Benefit
6. **Title variants generated** (3-10 variants) with fields:
   - `text`: Title text
   - `style`: Generation strategy used
   - `length`: Character count
   - `keywords`: Extracted keywords
   - `score`: Engagement score
7. **State set** to `PrismQ.T.Script.From.Title.Idea`
8. **Database write** - Title object with variants saved
9. **Best title selected** and displayed
10. **Script ends** with summary of all variants

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Title.From.Idea - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Titles will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Idea ID or content
5. **User provides** Idea ID or pastes Idea object
6. **AI processes** and generates title variants
7. **New state displayed** for each variant:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Title Variants for Idea: [idea-id]
   
   Variant 1 [Direct]:
     Text: "[title-text]"
     Score: 8.5/10
     Keywords: [keyword1, keyword2]
   
   Variant 2 [Question]:
     Text: "[title-text]"
     Score: 7.8/10
     Keywords: [keyword1, keyword2]
   
   ... (all variants)
   
   Best Title: "[selected-title]"
   Next State: PrismQ.T.Script.From.Title.Idea
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written to file
10. **Script ends**

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\03_PrismQ.T.Title.From.Idea

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

### By Idea ID
```
idea_12345
```

### By Idea Content
```json
{
  "id": "idea_12345",
  "title": "The Weather Girl",
  "concept": "A 16-year-old discovers she can control weather patterns"
}
```

---

## Success Criteria

- [ ] 3-10 title variants are generated
- [ ] Each variant uses a different strategy
- [ ] Titles meet length constraints (20-100 chars)
- [ ] Keywords are extracted from idea
- [ ] Scores reflect engagement potential
- [ ] Preview mode shows all variants without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-03 Title.From.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (Idea):
[paste idea id or content]

### Title Variants Generated:
1. [Direct]: "[title]" (Score: X.X)
2. [Question]: "[title]" (Score: X.X)
...

### Best Title Selected:
"[title]"

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
