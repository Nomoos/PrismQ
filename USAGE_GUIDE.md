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

## Repository Module Tree View

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

1. **Collapsible Modules** - Click any module to expand or collapse its sub-modules
2. **Search** - Type in the search box to find modules
   - Matching modules are highlighted in yellow
   - Parent modules auto-expand to show matches
3. **Expand All / Collapse All** - Quick navigation buttons
4. **Statistics** - View total modules and maximum hierarchy depth

The tree shows the PrismQ module hierarchy using the naming convention:
- PrismQ
  - PrismQ.IdeaInspiration
    - PrismQ.IdeaInspiration.Sources
      - PrismQ.IdeaInspiration.Sources.Content
  - PrismQ.RepositoryTemplate

### Regenerating the Tree

If the repository structure changes:

```bash
cd docs
python3 generate_tree.py
```

This will:
1. Scan the entire repository for modules
2. Generate `repository-tree-data.json` with the module hierarchy
3. Create `repository-tree.html` with embedded data
4. Display module statistics

### Search Examples

- Search for `IdeaInspiration` to find all related modules
- Search for `Sources` to find source-related modules
- Search for `Content` to find content processing modules
- Search for `RepositoryTemplate` to find the template module

## Directory Structure

```
PrismQ/
├── docs/                          # Documentation and tools
│   ├── repository-tree.html       # Interactive module tree (open this!)
│   ├── repository-tree-data.json  # Module hierarchy data
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
        └── src/
            └── Sources/           # Sources sub-module
                └── src/
                    └── Content/   # Content sub-module
```

## Quick Commands

```bash
# Test batch scripts
cd scripts && python3 -m pytest test_bat_scripts.py -v

# View repository module tree
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
