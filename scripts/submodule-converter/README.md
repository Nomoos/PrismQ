# PrismQ Submodule Converter

A modular tool for converting nested git repositories to git submodules, following SOLID principles with proper separation of concerns.

## Features

- **SOLID Principles**: Each module has a single responsibility with clear interfaces
- **Dependency Injection**: Components are loosely coupled and easily testable
- **Type Safety**: Full type hints for all functions and classes
- **Error Handling**: Comprehensive exception hierarchy for different error types
- **Backup & Recovery**: Automatic backup before operations with rollback on failure
- **Two-Phase Conversion**: 
  1. Convert nested repos to submodules in module roots
  2. Convert module roots to submodules in PrismQ root

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

For each nested git repository found within a module:

1. Scan the mod directory tree for `.git` folders
2. Identify repositories that are not module roots
3. Get the remote URL and default branch
4. Backup the existing directory
5. Add as submodule to the module root
6. Clean up backup on success, restore on failure

### Phase 2: Module Roots

For each module root repository:

1. Identify module root directories (first level under mod/)
2. Get the remote URL and default branch
3. Backup the existing directory
4. Add as submodule to PrismQ root (without mod/ prefix)
5. Clean up backup on success, restore on failure

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
