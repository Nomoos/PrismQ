# PrismQ Usage Guide

## Batch Script Testing

### Running Tests

To verify that the Windows batch scripts are properly configured:

```bash
cd scripts
python3 -m pytest test_bat_scripts.py -v
```

### What Gets Tested

The test suite validates:
- ✅ Batch file existence and structure
- ✅ Python module accessibility
- ✅ Virtual environment setup scripts
- ✅ Requirements files
- ✅ Error handling and exit codes
- ✅ File encoding

### Expected Results

- **12 tests should pass** - Core functionality tests
- **2 tests may fail** - These require dependencies (PyGithub, GitPython) to be installed

This is normal and expected behavior. The batch files will install dependencies on first run.

## Repository Tree View

### Viewing the Tree

Simply open `docs/repository-tree.html` in any web browser:

```bash
# On Windows
start docs\repository-tree.html

# On macOS
open docs/repository-tree.html

# On Linux
xdg-open docs/repository-tree.html
```

### Features

1. **Collapsible Folders** - Click any folder to expand or collapse its contents
2. **Search** - Type in the search box to find files and folders
   - Matching items are highlighted in yellow
   - Parent folders auto-expand to show matches
3. **Expand All / Collapse All** - Quick navigation buttons
4. **Statistics** - View total folders, files, and maximum depth

### Regenerating the Tree

If the repository structure changes:

```bash
cd docs
python3 generate_tree.py
```

This will:
1. Scan the entire repository
2. Generate `repository-tree-data.json`
3. Create `repository-tree.html` with embedded data
4. Display statistics

### Search Examples

- Search for `.bat` to find all batch files
- Search for `README` to find all README files
- Search for `scripts` to find all script-related items
- Search for module names like `IdeaInspiration`

## Directory Structure

```
PrismQ/
├── docs/                          # Documentation and tools
│   ├── repository-tree.html       # Interactive tree view (open this!)
│   ├── repository-tree-data.json  # Tree structure data
│   ├── generate_tree.py           # Generator script
│   └── README.md                  # Documentation README
├── scripts/                       # Utility scripts
│   ├── test_bat_scripts.py        # Batch script tests
│   ├── add-module.bat             # Module creation script
│   ├── sync-modules.bat           # Module sync script
│   └── README.md                  # Scripts documentation
└── src/                           # Source modules
    ├── RepositoryTemplate/        # Template module
    └── IdeaInspiration/           # Idea generation module
```

## Quick Commands

```bash
# Test batch scripts
cd scripts && python3 -m pytest test_bat_scripts.py -v

# View repository tree
# (Open docs/repository-tree.html in browser)

# Regenerate tree view
cd docs && python3 generate_tree.py

# Create a new module
scripts\add-module.bat  # Windows
python scripts/add_module  # Cross-platform

# Sync modules
scripts\sync-modules.bat  # Windows
python scripts/sync_modules  # Cross-platform
```

## Additional Resources

- [Main README](README.md) - Project overview
- [Scripts README](scripts/README.md) - Detailed script documentation
- [Docs README](docs/README.md) - Documentation guide
