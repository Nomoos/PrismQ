# Architecture Rule: Continuous Mode for Non-From.User Modules

## Rule Statement

**Only modules with "From.User" in their name should support manual/interactive input modes.**

All other modules must:
1. Run in continuous mode (processing items from database)
2. Wait **1ms between iterations** when processing items
3. Wait **30 seconds** when no items are available (to prevent busy-waiting)
4. NOT have Manual.bat scripts
5. Mark any --manual or --interactive flags as "[DEBUG ONLY]"

## Rationale

- **From.User modules** accept direct user input and are inherently interactive
- **All other modules** process data from previous pipeline steps and should run autonomously
- **1ms wait between iterations** provides high throughput while preventing CPU saturation
- **30-second wait when idle** prevents busy-waiting while allowing responsive processing when new items arrive

## Implementation Pattern

### Service File (`*_service.py`)
```python
class SomeService:
    INPUT_STATE = "PrismQ.T.SomeState"
    OUTPUT_STATE = "PrismQ.T.NextState"
    
    def process_oldest_story(self) -> ProcessingResult:
        """Process the oldest story in INPUT_STATE."""
        # Find oldest story
        # Process it
        # Update to OUTPUT_STATE
        # Return result
```

### Workflow File (`*_workflow.py`)
```python
def get_wait_interval(pending_count: int) -> float:
    """Calculate wait interval based on workload.
    
    Returns:
        - 30.0 seconds when 0 items (wait for new items)
        - 0.001 seconds (1 ms) when > 0 items (between iterations)
    """
    if pending_count == 0:
        return 30.0  # 30 seconds when idle
    else:
        return 0.001  # 1 ms between iterations

def main():
    while True:
        # Get pending count
        pending = count_pending_stories()
        
        if pending == 0:
            wait = get_wait_interval(0)
            print(f"Waiting {wait}s...")
            time.sleep(wait)
            continue
        
        # Process oldest
        result = service.process_oldest_story()
        
        # Wait 1ms before next iteration
        time.sleep(0.001)
```

### Run.bat
```batch
@echo off
REM Start Ollama if needed
call ..\common\start_ollama.bat

REM Setup environment
call :setup_env

echo ========================================
echo Module.Name - CONTINUOUS MODE
echo ========================================

python ..\..\..\Path\To\Module\src\module_workflow.py
```

## Modules Status

### ✅ Correctly Implemented
- **Step 01 (PrismQ.T.Idea.From.User)** - Has From.User, interactive mode OK
- **Step 02 (PrismQ.T.Story.From.Idea)** - Continuous with 30s wait
- **Step 03 (PrismQ.T.Title.From.Idea)** - Fixed: continuous with 30s wait
- **Step 04 (PrismQ.T.Content.From.Idea.Title)** - Fixed: workflow runner added
- **Step 05 (PrismQ.T.Review.Title.From.Content.Idea)** - Continuous with 30s wait
- **Step 06 (PrismQ.T.Review.Content.From.Title.Idea)** - Continuous with 30s wait
- **Step 07 (PrismQ.T.Review.Title.From.Content)** - Fixed: workflow runner added
- **Step 08 (PrismQ.T.Title.From.Script.Review.Title)** - CONTINUOUS MODE: interactive loop (user input driven)
- **Step 09 (PrismQ.T.Script.From.Title.Review.Script)** - CONTINUOUS MODE: interactive loop (user input driven)
- **Step 10 (PrismQ.T.Review.Content.From.Title)** - CONTINUOUS MODE: interactive loop (user input driven)
- **Step 11 (PrismQ.T.Review.Content.Grammar)** - Fixed: workflow runner added (grammar_workflow.py)
- **Step 12 (PrismQ.T.Review.Content.Tone)** - Fixed: workflow runner added (tone_workflow.py)
- **Step 13 (PrismQ.T.Review.Content.Content)** - Fixed: workflow runner added (content_review_workflow.py)
- **Step 14 (PrismQ.T.Review.Content.Consistency)** - Fixed: workflow runner added (consistency_workflow.py)
- **Step 15 (PrismQ.T.Review.Content.Editing)** - Fixed: workflow runner added (editing_workflow.py)
- **Step 16 (PrismQ.T.Review.Title.Readability)** - Fixed: workflow runner added (title_readability_workflow.py)
- **Step 17 (PrismQ.T.Review.Content.Readability)** - Fixed: workflow runner added (script_readability_workflow.py)
- **Step 18 (PrismQ.T.Story.Review)** - CONTINUOUS MODE (workflow pending implementation)
- **Step 19 (PrismQ.T.Story.Polish)** - CONTINUOUS MODE (workflow pending implementation)
- **Step 20 (PrismQ.T.Publishing)** - CONTINUOUS MODE (workflow pending implementation)

### ⚠️ Need Review/Update
Steps 21-30 may need similar updates depending on their execution model.

## Verification Checklist

For each non-From.User module:
- [ ] No Manual.bat file exists
- [ ] Has *_service.py with process_oldest_story()
- [ ] Has *_workflow.py with continuous loop
- [ ] Implements 30-second wait when no items
- [ ] Run.bat calls workflow, not interactive
- [ ] Documentation mentions 30-second wait
- [ ] --manual/--interactive marked [DEBUG ONLY]

## References

- Step 02: Reference implementation (dynamic wait)
- Step 03: Example of fixing incorrect manual mode
- Step 04 & 07: Workflow runner templates
- Steps 11-17: Grammar/Tone/Content/Consistency/Editing/Readability workflow runners
