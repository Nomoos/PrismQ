# PrismQ.IdeaInspiration Scripts

Utility scripts for repository maintenance and development automation.

## Available Scripts

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
