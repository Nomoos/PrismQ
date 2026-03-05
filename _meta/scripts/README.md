# PrismQ Scripts

This directory contains scripts for the PrismQ content production workflow.

## 📚 Documentation

- **[../docs/FUNKCIONALITA_AKTUALNI.md](../docs/FUNKCIONALITA_AKTUALNI.md)** - 🇨🇿 Kompletní shrnutí současné funkcionality (Current functionality summary in Czech)
- **[../proposals/FUNKCIONALITA_NAVRH.md](../proposals/FUNKCIONALITA_NAVRH.md)** - 🇨🇿 Návrh dalšího vývoje a priorit (Future development recommendations in Czech)
- **[../docs/FUNKCIONALITA_DETAIL.md](../docs/FUNKCIONALITA_DETAIL.md)** - 🇨🇿 Detailní popis kroků implementovaných modulů (Detailed step-by-step module documentation in Czech)
- **[../docs/NEXT_STEPS.md](../docs/NEXT_STEPS.md)** - Next steps guide and workflow progress
- **[../reports/TASK_COMPLETION.md](../reports/TASK_COMPLETION.md)** - Task completion history
- **[../reports/VALIDATION_REPORT.md](../reports/VALIDATION_REPORT.md)** - Mermaid diagram validation report

## 🚀 Quick Start

**New to PrismQ Scripts?** Check **[../docs/NEXT_STEPS.md](../docs/NEXT_STEPS.md)** for guidance on your current progress and what to do next in the pipeline.

**Want to understand what's implemented?** See **[../docs/FUNKCIONALITA_AKTUALNI.md](../docs/FUNKCIONALITA_AKTUALNI.md)** for a complete analysis.

**Need detailed step-by-step breakdown?** Read **[../docs/FUNKCIONALITA_DETAIL.md](../docs/FUNKCIONALITA_DETAIL.md)** for technical details of each module (format: 01.1, 01.2, 02.1, etc.).

**Planning future development?** Read **[../proposals/FUNKCIONALITA_NAVRH.md](../proposals/FUNKCIONALITA_NAVRH.md)** for prioritized recommendations.

## New Numbered Module Structure

Each module has its own numbered directory with `Run.bat` and `Preview.bat` scripts:
- **Run.bat** - Runs the module in production mode (saves to database)
- **Preview.bat** - Runs in preview/testing mode (no database save, extensive logging)

### Monitor (00)

| # | Directory | Description |
|---|-----------|-------------|
| 00 | `00_PrismQ.Monitor/` | Pipeline monitor — real-time story state distribution |

### T Module - Text Generation Pipeline (01-20)

| # | Directory | Description |
|---|-----------|-------------|
| 01 | `01_PrismQ.T.Idea.From.User/` | Idea creation from inspiration |
| 02 | `02_PrismQ.T.Story.From.Idea/` | Generate stories from ideas |
| 03 | `03_PrismQ.T.Title.From.Idea/` | Generate initial titles from ideas |
| 04 | `04_PrismQ.T.Content.From.Idea.Title/` | Generate content from title + idea |
| 05 | `05_PrismQ.T.Review.Title.From.Content.Idea/` | Review title against content and idea |
| 06 | `06_PrismQ.T.Review.Content.From.Title.Idea/` | Review content against title and idea |
| 07 | `07_PrismQ.T.Review.Title.From.Content/` | Review title against content |
| 08 | `08_PrismQ.T.Title.From.Title.Review.Content/` | Refine title from review feedback |
| 09 | `09_PrismQ.T.Content.From.Title.Content.Review/` | Refine content from review feedback |
| 10 | `10_PrismQ.T.Review.Content.From.Title/` | Quality gate: final content review |
| 11 | `11_PrismQ.T.Review.Content.Grammar/` | Grammar validation (≥ 95) |
| 12 | `12_PrismQ.T.Review.Content.Tone/` | Tone consistency check (≥ 90) |
| 13 | `13_PrismQ.T.Review.Content.Content/` | Content accuracy validation (≥ 85) |
| 14 | `14_PrismQ.T.Review.Content.Consistency/` | Consistency check (≥ 85) |
| 15 | `15_PrismQ.T.Review.Content.Editing/` | Final editing pass (≥ 85) |
| 16 | `16_PrismQ.T.Review.Title.Readability/` | Title readability check (≥ 85) |
| 17 | `17_PrismQ.T.Review.Content.Readability/` | Content readability / voiceover check (≥ 90) |
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
cd _meta\scripts\01_PrismQ.T.Idea.From.User
Run.bat
```

### Run Mode

All modules from **Step 02 onwards** run continuously by default:

- **Runs indefinitely** until cancelled with Ctrl+C or by closing the window
- **Waits 30 seconds** when no items are available to process (prevents busy-waiting)
- **Waits 1ms between iterations** when items are being processed (high throughput)
- **Saves to database** automatically after each successful processing step

This means you can start multiple steps in parallel in separate windows - each will
automatically pick up work as soon as the previous step produces output.

### Step 00: Monitor

`00_PrismQ.Monitor/Run.bat` launches a real-time dashboard that refreshes every 30 seconds
and shows how many stories are waiting in each pipeline state. Start it at any time to
observe pipeline progress without interfering with processing.

### Step 03: Parallel Workers (Orchestrator)

`03_PrismQ.T.Title.From.Idea/Run.bat` calls `orchestrate.py`, which reads
`workflow.json` and launches the configured number of parallel worker windows
automatically. To change the number of parallel title-generation workers, edit
`worker_count` in `03_PrismQ.T.Title.From.Idea/workflow.json`.

### Example Workflow

```batch
REM Step 1: Create idea (interactive - provides user input)
cd _meta\scripts\01_PrismQ.T.Idea.From.User
Run.bat

REM Step 2-20: Start all pipeline steps in separate windows
REM Each picks up work from database automatically
cd _meta\scripts\02_PrismQ.T.Story.From.Idea
Run.bat

cd _meta\scripts\03_PrismQ.T.Title.From.Idea
Run.bat

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
└── README.md                     # This file

_meta/reports/
└── VALIDATION_REPORT.md          # Detailed validation report
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
