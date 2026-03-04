# T-TEST-02: PrismQ.T.Story.From.Idea Manual Test

**Module**: PrismQ.T.Story.From.Idea  
**Script**: `_meta/scripts/02_PrismQ.T.Story.From.Idea/`  
**Type**: Manual Testing  
**Status**: 🧪 READY FOR TESTING

---

## Purpose

Generate 10 Story objects from an existing Idea. Each Story is a variation on the original concept.

---

## Expected Behavior (Run Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.From.Idea - RUN MODE"
2. **Environment setup** occurs (creates/activates virtual environment if needed)
3. **Prompt appears** asking for Idea ID or Idea content
4. **User provides** Idea ID or pastes Idea object
5. **AI processes** the Idea and generates 10 Story variations
6. **For each Story (1-10)**:
   - Story object created with fields:
     - `id`: Unique identifier
     - `idea_id`: Reference to parent Idea
     - `variation_number`: 1-10
     - `premise`: Story premise
     - `hook`: Opening hook
     - `conflict`: Main conflict
     - `resolution_hint`: Resolution direction
7. **State set** to `PrismQ.T.Title.From.Idea` for each Story
8. **Database write** - All 10 Story objects saved to database
9. **Success message** displayed with list of Story IDs
10. **Script ends** with summary

---

## Expected Behavior (Preview Mode)

### Numbered Steps

1. **Script starts** and displays header "PrismQ.T.Story.From.Idea - PREVIEW MODE"
2. **Warning displayed**: "This mode is for TESTING. Stories will NOT be saved to database."
3. **Environment setup** occurs (creates/activates virtual environment if needed)
4. **Prompt appears** asking for Idea ID or Idea content
5. **User provides** Idea ID or pastes Idea object
6. **AI processes** the Idea and generates 10 Story variations
7. **New state displayed** for each Story:
   ```
   ========================================
   NEW STATE (Preview - Not Saved)
   ========================================
   Story 1 of 10
   Story ID: [generated-id]
   Idea ID: [parent-idea-id]
   Premise: [story-premise]
   Hook: [opening-hook]
   Conflict: [main-conflict]
   Next State: PrismQ.T.Title.From.Idea
   ========================================
   Press any key for next story...
   ```
8. **Wait for keystroke** after each Story display
9. **After Story 10** - Summary displayed
10. **Final keystroke wait** - "All stories generated. Press any key to exit..."

---

## Test Commands

```batch
REM Navigate to script directory
cd _meta\scripts\02_PrismQ.T.Story.From.Idea

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
  "concept": "Teen discovers weather control powers",
  "target_audience": "Young adults 13-18"
}
```

---

## Success Criteria

- [ ] 10 Story objects are generated
- [ ] Each Story has unique variation
- [ ] Each Story references parent Idea ID
- [ ] State transitions correctly to `PrismQ.T.Title.From.Idea`
- [ ] Preview mode shows each state without saving
- [ ] Preview mode waits for keystroke after each story
- [ ] No errors in execution

---

## Log Submission

After testing, provide logs in this format:

```
### Test: T-TEST-02 Story.From.Idea
### Mode: [Preview/Run]
### Date: YYYY-MM-DD

### Input (Idea ID):
[paste idea id or content]

### Stories Generated:
Story 1: [brief description]
Story 2: [brief description]
...
Story 10: [brief description]

### Status: [PASS/FAIL]
### Notes:
[any observations]
```

---

**Created**: 2025-12-04
