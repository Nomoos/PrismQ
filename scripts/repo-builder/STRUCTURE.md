# Repository Builder Module Structure

This document describes the modular structure of the PrismQ Repository Builder after refactoring.

## Module Overview

```
repo-builder/
├── exceptions.py       # Custom exception classes
├── validation.py       # GitHub CLI validation
├── parsing.py          # URL and module name parsing
├── display.py          # Output formatting
├── repository.py       # Repository operations
├── cli.py              # CLI interface and main functions
├── __init__.py         # Package initialization
├── __main__.py         # Module entry point
├── repo_builder.py     # Backward compatibility wrapper
└── test_repo_builder.py  # Tests (unchanged)
```

## Module Responsibilities

### exceptions.py (17 lines)
Defines custom exception classes:
- `RepoBuilderError` - Base exception
- `GitHubCLIError` - GitHub CLI authentication errors
- `ModuleParseError` - Module name parsing errors

### validation.py (52 lines)
GitHub CLI validation:
- `validate_github_cli()` - Check if GitHub CLI is installed and authenticated

### parsing.py (113 lines)
URL and module name parsing:
- `parse_github_url()` - Extract module name from GitHub URL
- `derive_module_chain()` - Build module hierarchy from root to deepest

### display.py (30 lines)
Output formatting:
- `display_module_chain()` - Pretty-print the module chain

### repository.py (137 lines)
Repository operations:
- `repository_exists()` - Check if GitHub repository exists
- `get_repository_path()` - Map module name to local path
- `create_git_chain()` - Create or update repository chain

### cli.py (101 lines)
CLI interface:
- `get_module_input_interactive()` - Prompt user for input
- `run_git_creation()` - Main workflow for creating repositories
- `main()` - Entry point function

### __init__.py (46 lines)
Package initialization that re-exports all public functions and classes for easy importing.

### __main__.py (30 lines)
Entry point when running as a module with `python -m repo_builder`.

### repo_builder.py (47 lines)
Backward compatibility wrapper that re-exports all functions, allowing the script to be run directly with `python repo_builder.py`.

## Import Flexibility

All modules support both relative and absolute imports internally through try/except blocks:

```python
# In the module code itself, this pattern is used:
try:
    from .exceptions import RepoBuilderError  # Relative import (package context)
except ImportError:
    from exceptions import RepoBuilderError   # Absolute import (standalone context)
```

This internal implementation allows the code to be used in multiple ways:

1. **As a standalone script** (from the directory):
   ```bash
   python repo_builder.py PrismQ.IdeaInspiration
   ```

2. **As a module** (if properly installed or in PYTHONPATH):
   ```bash
   python -m repo_builder PrismQ.IdeaInspiration
   ```

3. **As a library** (when imported in other Python code):
   ```python
   # Requires the repo-builder directory to be in PYTHONPATH
   # or installed as a package
   from repo_builder import parse_github_url
   module_name = parse_github_url("https://github.com/Nomoos/PrismQ.IdeaInspiration")
   ```

## Benefits of Modularization

1. **Single Responsibility**: Each module has a clear, focused purpose
2. **Better Maintainability**: Easier to find and modify specific functionality
3. **Improved Testability**: Modules can be tested independently
4. **Code Reusability**: Functions can be imported and used programmatically
5. **Backward Compatibility**: Original `repo_builder.py` still works as before
6. **Reduced Complexity**: Smaller files are easier to understand and navigate
