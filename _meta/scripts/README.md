# PrismQ Scripts

This directory contains scripts for the PrismQ content production workflow.

## 🚀 Quick Start

**New to PrismQ Scripts?** Check **[NEXT_STEPS.md](NEXT_STEPS.md)** for guidance on your current progress and what to do next in the pipeline.

## New Numbered Module Structure

Each module has its own numbered directory with `Run.bat` and `Preview.bat` scripts:
- **Run.bat** - Runs the module in production mode (saves to database)
- **Preview.bat** - Runs in preview/testing mode (no database save, extensive logging)

### T Module - Text Generation Pipeline (01-20)

| # | Directory | Description |
|---|-----------|-------------|
| 01 | `01_PrismQ.T.Idea.Creation/` | Idea creation from inspiration |
| 02 | `02_PrismQ.T.Story.From.Idea/` | Generate stories from ideas |
| 03 | `03_PrismQ.T.Title.From.Idea/` | Generate initial titles from ideas |
| 04 | `04_PrismQ.T.Script.From.Title.Idea/` | Generate scripts from title + idea |
| 05 | `05_PrismQ.T.Review.Title.By.Script.Idea/` | Review title against script and idea |
| 06 | `06_PrismQ.T.Review.Script.By.Title.Idea/` | Review script against title and idea |
| 07 | `07_PrismQ.T.Review.Title.By.Script/` | Review title against script |
| 08 | `08_PrismQ.T.Title.From.Script.Review.Title/` | Refine title from review feedback |
| 09 | `09_PrismQ.T.Script.From.Title.Review.Script/` | Refine script from review feedback |
| 10 | `10_PrismQ.T.Review.Script.By.Title/` | Final script review |
| 11 | `11_PrismQ.T.Review.Script.Grammar/` | Grammar validation |
| 12 | `12_PrismQ.T.Review.Script.Tone/` | Tone consistency check |
| 13 | `13_PrismQ.T.Review.Script.Content/` | Content accuracy validation |
| 14 | `14_PrismQ.T.Review.Script.Consistency/` | Style consistency check |
| 15 | `15_PrismQ.T.Review.Script.Editing/` | Final editing pass |
| 16 | `16_PrismQ.T.Review.Title.Readability/` | Title readability check |
| 17 | `17_PrismQ.T.Review.Script.Readability/` | Script readability check |
| 18 | `18_PrismQ.T.Story.Review/` | Expert GPT story review |
| 19 | `19_PrismQ.T.Story.Polish/` | Expert GPT story polish |
| 20 | `20_PrismQ.T.Publishing/` | Text publishing with SEO |

### A Module - Audio Generation Pipeline (21-25)

| # | Directory | Description |
|---|-----------|-------------|
| 21 | `21_PrismQ.A.Voiceover/` | Voiceover recording |
| 22 | `22_PrismQ.A.Narrator/` | Narrator selection |
| 23 | `23_PrismQ.A.Normalized/` | Audio normalization (LUFS) |
| 24 | `24_PrismQ.A.Enhancement/` | Audio enhancement (EQ, compression) |
| 25 | `25_PrismQ.A.Publishing/` | Audio publishing (RSS, platforms) |

### V Module - Video Generation Pipeline (26-28)

| # | Directory | Description |
|---|-----------|-------------|
| 26 | `26_PrismQ.V.Scene/` | Scene planning |
| 27 | `27_PrismQ.V.Keyframe/` | Keyframe generation |
| 28 | `28_PrismQ.V.Video/` | Video assembly |

### P Module - Publishing (29)

| # | Directory | Description |
|---|-----------|-------------|
| 29 | `29_PrismQ.P.Publishing/` | Multi-platform publishing |

### M Module - Metrics & Analytics (30)

| # | Directory | Description |
|---|-----------|-------------|
| 30 | `30_PrismQ.M.Analytics/` | Metrics collection and analytics |

## Usage

### Windows

Navigate to any numbered module directory and run:

```batch
cd _meta\scripts\01_PrismQ.T.Idea.Creation
Preview.bat   REM For testing (no database save)
Run.bat       REM For production (saves to database)
```

### Example Workflow

```batch
REM Step 1: Create idea
cd _meta\scripts\01_PrismQ.T.Idea.Creation
Preview.bat

REM Step 2: Generate story from idea
cd ..\02_PrismQ.T.Story.From.Idea
Preview.bat

REM Step 3: Generate title from idea
cd ..\03_PrismQ.T.Title.From.Idea
Preview.bat

REM Continue through workflow...
```

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
