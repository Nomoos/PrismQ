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
- **Iterate on Script** - Feedback loop for script improvement (up to 3 iterations)

### Workflow Tools
- **Show workflow status** - See progress through Idea → Title → Script stages
- **Export content** - Save your work to a file
- **Reset session** - Start fresh

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
| `9` | Iterate on Script (feedback loop) |
| `10` | Show workflow status |
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
✓ Demo Idea loaded: 'The Echo'

> 5    # Generate title

> 7    # Generate script

> 11   # Export content
```

## Files

| File | Description |
|------|-------------|
| `run_text_client.py` | Main interactive Python client |
| `run_text_client.sh` | Bash launcher script |
| `run_text_client.ps1` | PowerShell launcher script |
| `README.md` | This documentation |

## Requirements

- Python 3.8+
- No external dependencies (uses PrismQ internal modules)

## Integration

The text client follows the PrismQ workflow:

```
Idea Creation → Title Generation → Script Draft → Review & Iterate → Export
```

Each stage builds on the previous, maintaining version tracking and supporting
the iterative co-improvement process that is central to PrismQ.

## Related Documentation

- [T Module README](../../README.md) - Text Generation Pipeline overview
- [Title & Script Workflow](../../TITLE_SCRIPT_WORKFLOW.md) - Complete workflow guide
- [Workflow State Machine](../../WORKFLOW_STATE_MACHINE.md) - Visual state diagram

---

*Part of PrismQ Content Production Platform*
