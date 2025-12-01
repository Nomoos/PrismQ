# PrismQ Scripts

This directory contains scripts for the PrismQ content production workflow.

## Workflow Module Scripts

Each workflow step has batch files (Windows) and shell scripts (Linux/macOS) for interactive execution:

### 01_Idea - PrismQ.T.Idea.Creation
- `PrismQ.T.Idea.Creation.bat` - Interactive idea creation
- `PrismQ.T.Idea.Creation.Preview.bat` - Preview mode (no DB save)
- `setup_env.bat` / `setup_env.sh` - Environment setup

### 02_Title - PrismQ.T.Title.From.Idea
- `PrismQ.T.Title.From.Idea.bat` - Generate titles from ideas
- `PrismQ.T.Title.From.Idea.Preview.bat` - Preview mode
- `setup_env.bat` / `setup_env.sh` - Environment setup

### 03_Script - PrismQ.T.Script.From.Idea.Title
- `PrismQ.T.Script.From.Idea.Title.bat` - Generate scripts from idea+title
- `PrismQ.T.Script.From.Idea.Title.Preview.bat` - Preview mode
- `setup_env.bat` / `setup_env.sh` - Environment setup

### 04_Review_Title - PrismQ.T.Review.Title.From.Script
- `PrismQ.T.Review.Title.From.Script.bat` - Review title against script
- `PrismQ.T.Review.Title.From.Script.Preview.bat` - Preview mode
- `setup_env.bat` / `setup_env.sh` - Environment setup

### 05_Review_Script - PrismQ.T.Review.Script.From.Title
- `PrismQ.T.Review.Script.From.Title.bat` - Review script against title
- `PrismQ.T.Review.Script.From.Title.Preview.bat` - Preview mode
- `setup_env.bat` / `setup_env.sh` - Environment setup

### 06_Title_From_Review - PrismQ.T.Title.From.Script.Review.Title
- `PrismQ.T.Title.From.Script.Review.Title.bat` - Improve title from review
- `PrismQ.T.Title.From.Script.Review.Title.Preview.bat` - Preview mode
- `setup_env.bat` / `setup_env.sh` - Environment setup

### 07_Script_From_Review - PrismQ.T.Script.From.Title.Review.Script
- `PrismQ.T.Script.From.Title.Review.Script.bat` - Improve script from review
- `PrismQ.T.Script.From.Title.Review.Script.Preview.bat` - Preview mode
- `setup_env.bat` / `setup_env.sh` - Environment setup

## Usage

### Windows
```batch
cd _meta\scripts\01_Idea
PrismQ.T.Idea.Creation.Preview.bat
```

### Linux/macOS
```bash
cd _meta/scripts/01_Idea
source setup_env.sh
python ../../../T/Idea/Creation/src/idea_creation_interactive.py --preview
```

## Virtual Environments

Each module has its own virtual environment in the corresponding T/ module directory:
- `T/Idea/Creation/.venv`
- `T/Title/From/Idea/.venv`
- `T/Script/From/Idea/Title/.venv`
- `T/Review/Title/From/Script/.venv`
- `T/Review/Script/From/Title/.venv`
- `T/Title/From/Title/Review/Script/.venv`
- `T/Script/From/Title/Review/Script/.venv`

---

# Mermaid State Diagram Validator

This script validates mermaid state diagrams in the PrismQ repository, specifically the workflow state machine defined in `WORKFLOW.md`.

## Purpose

The validator checks for:
- ✅ Syntax validity of mermaid state diagrams
- ✅ State name consistency
- ✅ Transition completeness
- ✅ Terminal state reachability
- ✅ Composite state structure validation
- ✅ Unreachable states detection
- ⚠️  Missing entry/exit points in composite states

## Usage

### Run the validator

```bash
node _meta/scripts/validate-mermaid-states.js
```

Or from the project root:

```bash
cd PrismQ
node _meta/scripts/validate-mermaid-states.js
```

### Output

The script provides detailed information about:

1. **Summary Statistics**
   - Total number of states
   - Total number of transitions
   - Composite states count
   - Start state identification
   - Terminal states identification

2. **State Listing**
   - All states in the diagram
   - Composite states marked
   - Terminal states marked

3. **Composite State Details**
   - Substates within each composite state

4. **Validation Results**
   - ✅ Errors (if any)
   - ⚠️  Warnings (if any)
   - Final verdict (VALID/INVALID)

## Example Output

```
🔍 Validating Mermaid State Diagrams

File: /home/runner/work/PrismQ/PrismQ/WORKFLOW.md

Found 1 mermaid diagram(s)

======================================================================
📊 Diagram #1 (Lines 11-115)
======================================================================

📈 Summary:
  States: 27
  Transitions: 72
  Composite States: 1
  Start State: IdeaInspiration
  Terminal States: Archived

📋 States Found:
  - AnalyticsReviewAudio
  - AnalyticsReviewText
  - AnalyticsReviewVideo
  - Archived [terminal]
  - AudioPublishing
  - Idea [composite]
  ...

✅ No errors found

──────────────────────────────────────────────────────────────────────
✅ Diagram is VALID
──────────────────────────────────────────────────────────────────────

======================================================================
✅ VALIDATION PASSED - All diagrams are valid
======================================================================
```

## Validation Rules

### 1. Start State Detection
- Checks for `[*] --> StateX` pattern
- Ensures exactly one start state exists

### 2. Terminal State Detection
- Identifies states that only transition to themselves or terminal states
- Marks `Archived` as terminal state

### 3. Reachability Analysis
- Verifies all states are reachable from the start state
- Excludes substates of composite states (they have internal entry/exit points)

### 4. Composite State Validation
- Checks for proper entry points: `[*] --> substate`
- Checks for proper exit points: `substate --> [*]`

### 5. Dead-end Detection
- Warns about states with no outgoing transitions (unless terminal)

## Exit Codes

- `0` - Validation passed
- `1` - Validation failed with errors

## Integration

This validator can be integrated into:
- Pre-commit hooks
- CI/CD pipelines
- Documentation validation workflows

## Requirements

- Node.js >= 18.0.0
- No external dependencies (uses only Node.js built-in modules)

## Testing

The validator includes a comprehensive test suite to ensure reliability:

```bash
node _meta/scripts/test-validator.js
```

The test suite validates:
- Simple state diagrams
- Composite states
- Multiple transitions
- Comment handling
- Error detection

## File Structure

```
_meta/scripts/
├── validate-mermaid-states.js    # Main validation script
├── test-validator.js             # Test suite
├── VALIDATION_REPORT.md          # Detailed validation report
└── README.md                      # This file
```

## Limitations

- Currently only validates `stateDiagram-v2` syntax
- Does not validate visual rendering
- Does not check for conflicting state names
- Limited to single file validation (WORKFLOW.md)

## Future Enhancements

- [ ] Support for multiple file validation
- [ ] JSON output format for CI/CD integration
- [ ] Visual diagram generation
- [ ] State transition matrix export
- [ ] Cycle detection
- [ ] Dead code analysis (unreachable state chains)

## Related Documentation

- [WORKFLOW.md](../WORKFLOW.md) - Complete state machine documentation
- [Content Production Workflow Research](../research/content-production-workflow-states.md)

---

*Part of PrismQ Content Production Platform*
