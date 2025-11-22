# PrismQ.T.Idea.Inspiration Scripts

Utility scripts for repository maintenance and development automation.

## Quick Start

**New to PrismQ Web Client?** See the **[Quick Start Guide](QUICK_START.md)** for easy setup instructions.

## Available Scripts

### PrismQ Web Client Launchers (Windows)

#### run_backend.bat

**Purpose:** Start the FastAPI Backend server for the PrismQ Web Client

**Description:**
Launches the Backend server in development mode with auto-reload enabled. Automatically activates the Python virtual environment and starts uvicorn.

**Usage:**
```cmd
_meta\_scripts\run_backend.bat
```

**Features:**
- Automatically creates virtual environment if missing
- Detects and recreates broken virtual environments
- Automatically activates virtual environment
- Auto-installs required dependencies
- Starts server on http://localhost:8000
- Enables auto-reload for development
- Provides helpful error messages with troubleshooting tips

**Requirements:**
- Python 3.10+ installed and in PATH
- Dependencies will be installed automatically from `Client/Backend/requirements.txt`

**Note:** The script will automatically create and configure the virtual environment on first run, or recreate it if it becomes corrupted (e.g., if Python was reinstalled at a different location).

---

#### run_frontend.bat

**Purpose:** Start the Vue 3 Frontend development server

**Description:**
Launches the Frontend development server with hot module replacement. Automatically installs npm dependencies if needed.

**Usage:**
```cmd
_meta\_scripts\run_frontend.bat
```

**Features:**
- Checks for Node.js installation
- Automatically installs npm dependencies if needed
- Starts server on http://localhost:5173
- Enables hot module replacement
- Provides helpful error messages

**Requirements:**
- Node.js 18+ (24.11.0+ recommended)
- npm 8+

---

#### run_both.bat

**Purpose:** Start both Backend and Frontend servers simultaneously and open in browser

**Description:**
Launches both the Backend and Frontend servers in separate console windows, waits for them to start, and automatically opens the Frontend application in your default web browser. This is the easiest way to start the full PrismQ Web Client for development.

**Usage:**
```cmd
_meta\_scripts\run_both.bat
```

**Features:**
- Opens two separate console windows (one for Backend, one for Frontend)
- Starts Backend first, then Frontend
- Waits for servers to fully start (10 seconds)
- Automatically opens http://localhost:5173 in your default browser
- Shows both server URLs
- Both servers can be stopped by closing their respective console windows

**What Gets Started:**
- Backend server: http://localhost:8000
- Frontend server: http://localhost:5173
- Browser opens automatically to the Frontend

**Requirements:**
- All requirements from `run_backend.bat` and `run_frontend.bat`

---

### check_wip_issues.py

**Purpose:** Automated checker for issues in the WIP (Work In Progress) folder

**Description:**
Scans all issue files in `_meta/issues/wip/` and analyzes their state to ensure they are correctly categorized. Helps maintain clean issue tracking by identifying:
- Issues with incorrect status fields
- Completed issues that should be moved to `done/`
- Issues that need attention or verification

**Usage:**
```bash
python scripts/check_wip_issues.py
```

**Output:**
- Detailed analysis of each issue in WIP
- Metadata extraction (title, type, priority, status)
- Completion status analysis (checklist progress)
- Recommendations for each issue
- Summary of findings and next steps

**Features:**
- Extracts issue metadata from markdown files
- Analyzes completion indicators (checkboxes, markers)
- Calculates completion percentages
- Identifies status field mismatches
- Generates actionable recommendations

**When to Use:**
- Before major releases to verify issue states
- Monthly as part of issue tracking maintenance
- When reviewing project progress
- Before moving issues between folders

**Example Output:**
```
================================================================================
WIP ISSUES STATUS CHECK
================================================================================

Found 3 issue file(s) in WIP

--------------------------------------------------------------------------------
Issue: 027-source-implementation-master-plan.md
  Title: Source Implementation Master Plan
  Type: Epic
  Priority: High
  Status: In Progress
  
  Checklist: 5/18 items completed (27.8%)
  🚧 Contains WIP markers
  
  Recommendations:
    🚧 Checklist progress: 5/18 (27.8%) - actively in progress

... (analysis of remaining 2 issues in WIP folder)

================================================================================
SUMMARY
================================================================================

🚧 Issues actively in progress (1):
   - 027-source-implementation-master-plan.md

... (additional categories: issues to move, issues needing attention, next steps)
```

*Note: This is a partial example. The full output includes analysis of all issues in the WIP folder.*

---

### generate_signal_sources.py

**Purpose:** Scaffolding generator for new Signal source implementations

**Description:**
Generates boilerplate code and directory structure for new Signal sources following the established patterns.

**Usage:**
```bash
python scripts/generate_signal_sources.py [source_name]
```

**Note:** See the script file for detailed usage instructions.

---

## Adding New Scripts

When adding new utility scripts to this directory:

1. **Name clearly:** Use descriptive names like `verb_noun.py`
2. **Add shebang:** Start with `#!/usr/bin/env python3`
3. **Document:** Add docstring explaining purpose and usage
4. **Make executable:** `chmod +x scripts/your_script.py`
5. **Update this README:** Add entry in the "Available Scripts" section
6. **Add help:** Support `--help` flag for command-line scripts

---

## Script Standards

All scripts in this directory should follow these standards:

### Python Style
- Follow PEP 8
- Use type hints
- Include comprehensive docstrings
- Handle errors gracefully

### Documentation
- Clear purpose statement
- Usage examples
- Expected input/output
- Error handling explanation

### Error Handling
- Validate input parameters
- Provide helpful error messages
- Exit with appropriate codes (0 for success, non-zero for errors)
- Use try/except for expected failures

### Compatibility
- Python 3.8+
- Cross-platform (Windows, Linux, macOS)
- Minimal external dependencies
- Document required packages

---

## Related Documentation

- **Issue Tracking:** `_meta/issues/README.md`
- **Project Roadmap:** `_meta/issues/ROADMAP.md`
- **Contributing:** `_meta/docs/CONTRIBUTING.md`

---

**Last Updated:** 2025-10-30
