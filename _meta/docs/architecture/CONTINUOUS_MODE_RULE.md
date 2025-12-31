# Architecture Rule: Continuous Mode for Non-From.User Modules

## Rule Statement

**Only modules with "From.User" in their name should support manual/interactive input modes.**

All other modules must:
1. Run in continuous mode (processing items from database)
2. Wait 30 seconds when no items are available to process
3. NOT have Manual.bat scripts
4. Mark any --manual or --interactive flags as "[DEBUG ONLY]"

## Rationale

- **From.User modules** accept direct user input and are inherently interactive
- **All other modules** process data from previous pipeline steps and should run autonomously
- The 30-second wait prevents busy-waiting while allowing responsive processing when items are available

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
    """Dynamic wait based on workload."""
    if pending_count == 0:
        return 30.0  # 30 seconds when idle
    elif pending_count >= 100:
        return 0.001  # 1 ms when busy
    else:
        # Linear interpolation
        return 0.001 + 0.999 * (100 - pending_count) / 99

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
        
        # Wait before next
        remaining = pending - 1
        time.sleep(get_wait_interval(remaining))
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
- **Step 07 (PrismQ.T.Review.Title.From.Content)** - Fixed: workflow runner added

### ⚠️ Need Review/Update
Steps 05-06, 08-30 may need similar updates depending on their execution model.

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
