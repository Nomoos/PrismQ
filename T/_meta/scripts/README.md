# PrismQ.T Scripts

Interactive scripts for the PrismQ Text Generation Pipeline.

## Quick Start

### Interactive Text Client

The interactive text client provides a quick way to work with the text generation pipeline:

```bash
# Linux/macOS
./run_text_client.sh

# Windows PowerShell
.\run_text_client.ps1

# Or directly with Python
python run_text_client.py
```

### Command Line Options

```bash
# Start with demo data loaded
./run_text_client.sh --demo

# Check module availability
./run_text_client.sh --check
```

## Batch Scripts (Windows .bat)

Each workflow step can be run as a separate process using batch scripts. State is persisted between steps.

### Individual Step Scripts

| Script | Description |
|--------|-------------|
| `step1_create_idea.bat` | Create a new idea interactively |
| `step2_generate_title.bat` | Generate title from current idea |
| `step3_generate_script.bat` | Generate script draft |
| `step4_iterate_script.bat` | Iterate on script (run multiple times) |
| `step5_export.bat` | Export all content to file |
| `load_demo.bat` | Load demo idea for testing |
| `show_status.bat` | Show workflow status and versions |
| `run_all_steps.bat` | Run all steps sequentially |

### Usage

```batch
REM Run each step as separate process
step1_create_idea.bat
step2_generate_title.bat
step3_generate_script.bat
step4_iterate_script.bat   REM Can run multiple times
step5_export.bat

REM Or run all steps at once
run_all_steps.bat

REM Quick start with demo
load_demo.bat
step2_generate_title.bat
step3_generate_script.bat
```

### Command Line Actions

You can also run individual actions directly with Python:

```bash
python run_text_client.py --action create_idea
python run_text_client.py --action generate_title
python run_text_client.py --action generate_script
python run_text_client.py --action iterate_script
python run_text_client.py --action export
python run_text_client.py --action status
python run_text_client.py --action load_demo
python run_text_client.py --action reset
```

## Features

The Interactive Text Client allows you to:

### Idea Management
- **Create new Idea** - Interactive prompts for creating content ideas
- **Load demo Idea** - Quick start with pre-loaded "The Echo" horror story
- **View current Idea** - Display all idea fields and metadata
- **Edit Idea fields** - Modify existing idea properties

### Title Generation
- **Generate Title variants** - Create multiple title options from your idea
- **Select or customize** - Choose from variants or enter custom title

### Script Development
- **Generate Script draft** - Create initial script structure
- **View current Script** - Display script content with formatting
- **Iterate on Script** - Unlimited feedback loop for script improvement

### Workflow Tools
- **Show workflow status** - See version counts and next item to process (lowest version)
- **Export content** - Save your work to a file
- **Reset session** - Start fresh (resets all versions to 0)

### Version Tracking & Processing Order
The client tracks versions for each content type (Idea, Title, Script). The workflow status shows:
- Current version count for each item
- **Next to process** recommendation based on lowest version count

This ensures balanced progression through the workflow by always suggesting work on the item with the least iterations.

### State Persistence
When using batch scripts or `--action` mode, state is automatically saved to a SQLite database (`text_client_state.db`). This allows:
- Running each step as a separate process
- Resuming work after closing the terminal
- Sharing state between interactive and batch modes
- Full transaction support and data integrity

## Menu Commands

| Command | Description |
|---------|-------------|
| `1` | Create new Idea |
| `2` | Load demo Idea |
| `3` | View current Idea |
| `4` | Edit Idea fields |
| `5` | Generate Title from Idea |
| `6` | View current Title |
| `7` | Generate Script draft |
| `8` | View current Script |
| `9` | Iterate on Script (unlimited feedback loop) |
| `10` | Show workflow status (next to process by lowest version) |
| `11` | Export current content |
| `12` | Reset session |
| `h` | Show menu |
| `s` | Show session summary |
| `q` | Quit |

## Module Dependencies

The client works best with these PrismQ modules:

- **T/Idea/Model** - Core Idea data model
- **T/Script** - Script generation and writing

The client gracefully handles missing modules, showing limited functionality.

## Example Session

```
╔══════════════════════════════════════════════════════════════════════════════╗
║               PrismQ.T - Interactive Text Client                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Welcome to the PrismQ Text Generation Pipeline!
This interactive client helps you create and refine content.

──────────────────────────────────────────────────
Module Availability
──────────────────────────────────────────────────
✓ Idea model loaded (T/Idea/Model)
✓ ScriptWriter loaded (T/Script)

> 2    # Load demo idea

──────────────────────────────────────────────────
Loading Demo Idea
──────────────────────────────────────────────────
✓ Demo Idea loaded: 'The Echo' (version 1)

> 10   # Show workflow status

──────────────────────────────────────────────────
Workflow Status
──────────────────────────────────────────────────

Content Status & Version Counts:
  ✓ Idea: version 1
  ○ Title: version 0
  ○ Script: version 0

➤ Next to process (lowest version): Title

> 5    # Generate title (follows recommendation)

> 7    # Generate script

> 9    # Iterate on script (unlimited)
```

## Files

| File | Description |
|------|-------------|
| `run_text_client.py` | Main interactive Python client |
| `run_text_client.sh` | Bash launcher script |
| `run_text_client.ps1` | PowerShell launcher script |
| `step1_create_idea.bat` | Batch: Create idea |
| `step2_generate_title.bat` | Batch: Generate title |
| `step3_generate_script.bat` | Batch: Generate script |
| `step4_iterate_script.bat` | Batch: Iterate script |
| `step5_export.bat` | Batch: Export content |
| `load_demo.bat` | Batch: Load demo idea |
| `show_status.bat` | Batch: Show status |
| `run_all_steps.bat` | Batch: Run all steps |
| `README.md` | This documentation |

## Requirements

- Python 3.8+
- No external dependencies (uses PrismQ internal modules)

## Integration

The text client follows the PrismQ workflow:

```
Idea Creation → Title Generation → Script Draft → Review & Iterate (unlimited) → Export
```

Each stage builds on the previous, maintaining version tracking. The next item for
processing is picked by lowest version count, ensuring balanced workflow progression.

## Database Schema

The system uses a **SQLite database** with only **4 core tables**:

```sql
Story (id, state, current_title_version_id FK, current_script_version_id FK, 
       title, concept, premise, logline, hook, skeleton, emotional_arc, 
       twist, climax, tone_guidance, target_audience, genre, created_at, updated_at)
TitleVersion (id, story_id FK, version, text, created_at)
ScriptVersion (id, story_id FK, version, text, created_at)
Review (id, story_id FK, review_type, reviewed_title_version_id FK NULL, 
        reviewed_script_version_id FK NULL, feedback, score, created_at)
```

### Process State (Story.state)

The `Story.state` field stores the **next process name** following PrismQ naming conventions:

| State | Description |
|-------|-------------|
| `PrismQ.T.Initial` | Initial state, no content |
| `PrismQ.T.Idea.Creation` | Idea created |
| `PrismQ.T.Title.By.Idea` | Title generated from idea |
| `PrismQ.T.Script.By.Title` | Script generated from title |
| `PrismQ.T.Script.Iteration` | Script iteration (unlimited) |
| `PrismQ.T.Export` | Content exported |

### Review Types
- **TitleReview**: `review_type='title'`, only `reviewed_title_version_id` set
- **ScriptReview**: `review_type='script'`, only `reviewed_script_version_id` set  
- **StoryReview**: `review_type='story'`, both version IDs set

See [Database Design Document](../docs/DATABASE_DESIGN.md) for full schema and implementation details.

## Related Documentation

- [Database Design](../docs/DATABASE_DESIGN.md) - Full database schema and design decisions
- [T Module README](../../README.md) - Text Generation Pipeline overview
- [Title & Script Workflow](../../TITLE_SCRIPT_WORKFLOW.md) - Complete workflow guide
- [Workflow State Machine](../../WORKFLOW_STATE_MACHINE.md) - Visual state diagram

---

*Part of PrismQ Content Production Platform*
