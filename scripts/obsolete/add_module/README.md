# Add Module Package

Refactored PrismQ module creation toolkit with single responsibility principle.

## Structure

The `add_module` package is organized into focused modules:

### Core Modules

- **`__init__.py`** - Package initialization, exports `ModuleCreator`
- **`__main__.py`** - CLI entry point with Click commands
- **`module_creator.py`** - Main orchestrator class that coordinates all operations

### Utility Modules

- **`url_parser.py`** - GitHub URL parsing functionality
  - `parse_github_url()` - Parse various GitHub URL formats

- **`path_utils.py`** - Path and naming utilities
  - `derive_module_path()` - Convert repo name to module path
  - `derive_remote_name()` - Generate git remote names

- **`github_client.py`** - GitHub API client management
  - `get_github_client()` - Get authenticated GitHub client

- **`module_structure.py`** - Module structure creation
  - `create_module_structure()` - Create directory structure and files
  - `_copy_template()` - Copy from template
  - `_create_basic_structure()` - Create basic structure
  - `_create_module_config()` - Create configuration files

- **`git_operations.py`** - Git repository operations
  - `initialize_git_repo()` - Initialize git repository
  - `create_github_repositories()` - Create GitHub repositories
  - `setup_nested_subtree()` - Set up git subtree hierarchy

## Usage

### As a Package

```python
from add_module import ModuleCreator

creator = ModuleCreator(repo_root)
owner, repo = creator.parse_github_url("https://github.com/Owner/Repo")
```

### As a CLI Tool

There are two CLI interfaces available:

#### Legacy CLI (Interactive Mode - Recommended for Beginners)

Supports interactive mode where you can paste just a GitHub URL:

```bash
# Run without arguments for interactive mode
python -m scripts.add_module

# Or with command-line arguments
python -m scripts.add_module --github-url "https://github.com/Owner/Repo"
```

**Interactive Mode Example:**
```
$ python -m scripts.add_module
========================================================
        PrismQ Module Creation Script
========================================================

Enter the GitHub repository URL: https://github.com/Nomoos/PrismQ.MyModule
```

#### New CLI (Command-Line Only)

Does NOT support interactive mode. Requires module name as argument:

```bash
# Required: specify module name
python -m scripts.add_module.add_module PrismQ.NewModule --owner Nomoos --public
```

## Benefits of Refactoring

1. **Single Responsibility** - Each module has one clear purpose
2. **Testability** - Easier to test individual components
3. **Maintainability** - Changes isolated to specific files
4. **Reusability** - Components can be imported independently
5. **Clarity** - Clear separation of concerns

## Module Responsibilities

| Module | Responsibility | LOC |
|--------|---------------|-----|
| `url_parser.py` | Parse GitHub URLs | ~40 |
| `path_utils.py` | Path/name derivation | ~60 |
| `github_client.py` | GitHub authentication | ~35 |
| `module_structure.py` | Create module files | ~280 |
| `git_operations.py` | Git operations | ~330 |
| `module_creator.py` | Orchestration | ~100 |
| `__main__.py` | CLI interface | ~140 |

## Testing

All existing tests pass without modification:

```bash
cd scripts
python -m pytest tests/test_add_module.py -v
```

The tests import from `add_module.module_creator` instead of the monolithic file.
