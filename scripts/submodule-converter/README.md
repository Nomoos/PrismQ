# PrismQ Submodule Converter

A modular tool for converting nested git repositories to git submodules, following SOLID principles with proper separation of concerns. **Now supports fully recursive nested module hierarchies!**

## Features

- **SOLID Principles**: Each module has a single responsibility with clear interfaces
- **Dependency Injection**: Components are loosely coupled and easily testable
- **Type Safety**: Full type hints for all functions and classes
- **Error Handling**: Comprehensive exception hierarchy for different error types
- **Backup & Recovery**: Automatic backup before operations with rollback on failure
- **Recursive Conversion**: Handles arbitrarily deep nested module hierarchies
- **Two-Phase Conversion**: 
  1. Convert nested repos to submodules in module roots
  2. Convert module roots to submodules in their parent context (depth-first)

## Recursive Module Hierarchy Support

The converter now fully supports recursive nested module structures like:

```
PrismQ/
  mod/
    IdeaInspiration/.git              <- Top-level module (depth 0)
      mod/
        Classification/.git            <- Nested module (depth 1)
          SomeRepo/.git                <- Nested repo (not a module)
          mod/
            DeepModule/.git            <- Deeply nested module (depth 2)
        DataCollection/.git            <- Another nested module (depth 1)
```

Processing order (deepest first):
1. DeepModule → submodule in Classification/mod/
2. Classification → submodule in IdeaInspiration/mod/
3. DataCollection → submodule in IdeaInspiration/mod/
4. IdeaInspiration → submodule in PrismQ/mod/

## Architecture

### Modules

- **exceptions.py**: Custom exception classes for error handling
- **command_runner.py**: Command execution abstraction (Protocol-based)
- **git_operations.py**: Git-specific operations (remotes, branches, submodules)
- **repository_scanner.py**: Repository discovery and classification
- **submodule_manager.py**: High-level submodule operations
- **backup_manager.py**: Backup and restore functionality
- **path_resolver.py**: Path resolution and sanitization
- **cli.py**: Main workflow orchestration

### Design Principles

1. **Single Responsibility Principle (SRP)**: Each class has one reason to change
   - `CommandRunner`: Execute commands
   - `GitOperations`: Git-specific operations
   - `BackupManager`: Backup/restore operations
   - `PathResolver`: Path manipulation
   - `RepositoryScanner`: Find repositories
   - `SubmoduleManager`: Manage submodule operations
   - `SubmoduleConverter`: Orchestrate conversion workflow

2. **Open/Closed Principle (OCP)**: Open for extension, closed for modification
   - Protocol-based interfaces allow different implementations
   - New command runners or git operations can be added without changing existing code

3. **Liskov Substitution Principle (LSP)**: Subtypes are substitutable
   - `SubprocessCommandRunner` implements `CommandRunner` protocol
   - Any implementation of protocols can be swapped without breaking code

4. **Interface Segregation Principle (ISP)**: Focused interfaces
   - `CommandRunner` protocol has minimal interface
   - `GitOperations` protocol provides only necessary operations

5. **Dependency Inversion Principle (DIP)**: Depend on abstractions
   - High-level modules depend on protocols, not concrete implementations
   - Dependencies are injected rather than created internally

## Usage

### Command Line

```bash
# Run from PrismQ root or any subdirectory
python -m submodule-converter

# Or directly
cd scripts/submodule-converter
python cli.py
```

### As a Library

```python
from submodule_converter import (
    SubmoduleConverter,
    SubprocessCommandRunner,
    GitOperationsImpl,
    BackupManager,
    PathResolver,
    RepositoryScanner,
    SubmoduleManager,
)

# Initialize dependencies
runner = SubprocessCommandRunner()
git_ops = GitOperationsImpl(runner)
backup_mgr = BackupManager()
path_resolver = PathResolver()
scanner = RepositoryScanner()
submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

# Create converter
converter = SubmoduleConverter(scanner, submodule_mgr, git_ops, path_resolver)

# Run conversion
prismq_root = path_resolver.find_prismq_root()
mod_root = prismq_root / "mod"
converter.convert_nested_to_submodules(prismq_root, mod_root)
converter.convert_modules_to_submodules(prismq_root, mod_root)
```

## Requirements

- Python 3.10+
- Git 2.x+
- Write access to PrismQ repository

## How It Works

### Phase 1: Nested Repositories

For each nested git repository found within a module (not including module roots):

1. Scan the mod directory tree for `.git` folders
2. Identify repositories that are not module roots (not directly under mod/)
3. Get the remote URL and default branch
4. Determine the immediate parent module
5. Backup the existing directory
6. Add as submodule to the parent module
7. Clean up backup on success, restore on failure

### Phase 2: Module Roots (Recursive)

For each module root repository, processed in depth-first order (deepest first):

1. Scan for all module root directories (directly under any mod/ directory)
2. Calculate nesting depth by counting "mod" directories in path
3. Sort by depth (deepest first) to ensure inner modules are processed before outer ones
4. For each module root:
   - Get the remote URL and default branch
   - Identify parent module (if nested) or use PrismQ root (if top-level)
   - Backup the existing directory
   - Add as submodule to parent context with mod/ prefix
   - Clean up backup on success, restore on failure

### Example Processing Order

Given structure:
```
mod/
  IdeaInspiration/.git (depth 0)
    mod/
      Classification/.git (depth 1)
        mod/
          Analysis/.git (depth 2)
      DataCollection/.git (depth 1)
```

Processing order:
1. **Step 1**: Any nested repos (non-modules) within Analysis, Classification, DataCollection, IdeaInspiration
2. **Step 2**: Module roots in depth-first order:
   - Analysis (depth 2) → submodule in Classification/mod/
   - Classification (depth 1) → submodule in IdeaInspiration/mod/
   - DataCollection (depth 1) → submodule in IdeaInspiration/mod/
   - IdeaInspiration (depth 0) → submodule in PrismQ/mod/

## Error Handling

The tool provides specific exceptions for different error scenarios:

- `CommandExecutionError`: Command execution failed
- `RepositoryNotFoundError`: Git repository not found
- `BackupError`: Backup/restore operation failed
- `PathResolutionError`: Path resolution failed
- `SubtreeConverterError`: Base exception for all converter errors

All operations use backup/restore to ensure data safety.

## Testing

See `test_subtree_converter.py` for comprehensive test coverage.

## Contributing

Follow the SOLID principles and maintain:
- Type hints for all functions
- Google-style docstrings
- Single responsibility per class
- Protocol-based interfaces for extensibility
