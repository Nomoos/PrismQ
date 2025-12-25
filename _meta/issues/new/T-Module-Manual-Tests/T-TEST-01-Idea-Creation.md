# T-TEST-01: PrismQ.T.Idea.From.User Manual Test

**Module**: PrismQ.T.Idea.From.User  
**Script**: `_meta/scripts/01_PrismQ.T.Idea.From.User/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Create a new Idea from user-provided inspiration text. This is the first stage of the T pipeline.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Idea.From.User - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking user for idea input (text, title, concept, or JSON)
4. **User enters text** and presses Enter twice to submit
5. **AI processes** the input and generates structured Idea object
6. **Idea object created** with fields:
   - `id`: Unique identifier
   - `title`: Generated title
   - `concept`: Core concept
   - `description`: Detailed description
   - `target_audience`: Audience profile
   - `content_goals`: List of goals
   - `created_at`: Timestamp
7. **State set** to `PrismQ.T.Story.From.Idea`
8. **Database write** - Idea object saved to database
9. **Success message** displayed with Idea ID
10. **Script ends** or prompts for next idea

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Idea.From.User - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Ideas will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking user for idea input (text, title, concept, or JSON)
5. **User enters text** and presses Enter twice to submit
6. **AI processes** the input and generates structured Idea object
7. **New state displayed** - Full Idea object shown in formatted output:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Idea ID: [generated-id]
   Title: [generated-title]
   Concept: [generated-concept]
   Description: [generated-description]
   Target Audience: [audience]
   Content Goals: [goals]
   Next State: PrismQ.T.Story.From.Idea
   ========================================
   ```
8. **Wait for keystroke** - "Press any key to continue..."
9. **Debug log** written to file with detailed processing info
10. **Script ends** or prompts for next idea

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\01_PrismQ.T.Idea.From.User

REM Run in Preview Mode (recommended for testing)
Preview.bat

REM Run in Production Mode (saves to database)
Run.bat
```

---

## Test Input Examples

### Simple Text Input
```
A story about a teenager who discovers she can control the weather
```

### Title + Description
```
The Weather Girl: A coming-of-age story about a 16-year-old who wakes up one day with the ability to control weather patterns
```

### JSON Input
```json
{
  "title": "The Weather Girl",
  "concept": "Teen discovers weather control powers",
  "target_audience": "Young adults 13-18",
  "content_goals": ["Entertainment", "Coming-of-age themes"]
}
```

---

## Success Criteria

- [ ] Idea object is generated from input
- [ ] All required fields are populated
- [ ] State transitions correctly to `PrismQ.T.Story.From.Idea`
- [ ] Preview mode shows state without saving
- [ ] Preview mode waits for keystroke
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-01 Idea.Creation
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input Used:
[paste input text]

### Output:
[paste console output]

### New State Displayed:
[paste state display]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
