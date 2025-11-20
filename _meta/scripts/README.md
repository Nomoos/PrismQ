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

- [WORKFLOW.md](../../WORKFLOW.md) - Complete state machine documentation
- [Content Production Workflow Research](../research/content-production-workflow-states.md)

---

*Part of PrismQ Content Production Platform*
