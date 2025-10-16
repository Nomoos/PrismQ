# Sync Modules Package

Refactored PrismQ module synchronization toolkit with single responsibility principle.

## Structure

The `sync_modules` package is organized into focused modules:

### Core Modules

- **`__init__.py`** - Package initialization, exports `ModuleSyncer`
- **`__main__.py`** - CLI entry point with Click commands
- **`module_syncer.py`** - Main orchestrator class that coordinates all operations

### Utility Modules

- **`path_utils.py`** - Path and naming utilities
  - `derive_remote_name()` - Generate git remote names from URLs

- **`module_discovery.py`** - Module discovery functionality
  - `discover_modules_from_json()` - Discover modules from module.json files
  - `get_hardcoded_modules()` - Get hardcoded module list
  - `_discover_first_level_modules()` - First-level discovery
  - `_discover_modules_recursive()` - Recursive discovery
  - `_add_module_from_config()` - Parse module.json config

- **`git_sync.py`** - Git synchronization operations
  - `validate_and_set_origin()` - Validate/set git origin
  - `sync_module()` - Sync a module using git subtree

## Usage

### As a Package

```python
from sync_modules import ModuleSyncer

syncer = ModuleSyncer(repo_root)
syncer.discover_modules_from_json()
syncer.sync_all()
```

### As a CLI Tool

```bash
# Using the wrapper script
python scripts/sync_modules.py --list

# Using the package directly
python -m sync_modules --recursive

# Sync specific module
python scripts/sync_modules.py src/MyModule
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
| `path_utils.py` | Remote name derivation | ~25 |
| `module_discovery.py` | Module discovery logic | ~140 |
| `git_sync.py` | Git sync operations | ~130 |
| `module_syncer.py` | Orchestration | ~100 |
| `__main__.py` | CLI interface | ~95 |

## CLI Options

```
Options:
  -l, --list-only  List configured modules without syncing
  --sync-all       Sync all modules (default behavior)
  -r, --recursive  Recursively discover all modules (not just first-level)
  --help           Show this message and exit.
```

## Examples

```bash
# List all modules
python sync_modules.py --list

# Sync all first-level modules (default)
python sync_modules.py

# Sync all modules recursively
python sync_modules.py --recursive

# Sync specific module
python sync_modules.py src/RepositoryTemplate
```

## Module Discovery

Modules are discovered in two ways:

1. **Automatic** - Scans for `module.json` files in src/ directory
2. **Hardcoded** - Includes known modules (RepositoryTemplate, IdeaInspiration)

The `module.json` file should contain:

```json
{
  "remote": {
    "url": "https://github.com/Owner/Repo.git"
  }
}
```
