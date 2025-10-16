# SOLID Principles in Subtree Converter

This document explains how SOLID principles are applied in the Subtree Converter implementation.

## Overview

The subtree converter refactors a monolithic script into a well-structured, maintainable codebase following SOLID principles. Each module has a clear, single responsibility, and components are loosely coupled through dependency injection.

## Single Responsibility Principle (SRP)

**Definition**: A class should have only one reason to change.

### Applied in:

1. **CommandRunner** (`command_runner.py`)
   - **Single Responsibility**: Execute shell commands
   - **One reason to change**: If command execution logic changes

2. **GitOperations** (`git_operations.py`)
   - **Single Responsibility**: Perform git-specific operations
   - **One reason to change**: If git command interface changes

3. **BackupManager** (`backup_manager.py`)
   - **Single Responsibility**: Create and restore directory backups
   - **One reason to change**: If backup strategy changes

4. **PathResolver** (`path_resolver.py`)
   - **Single Responsibility**: Resolve and manipulate file paths
   - **One reason to change**: If path resolution rules change

5. **RepositoryScanner** (`repository_scanner.py`)
   - **Single Responsibility**: Find git repositories in directory tree
   - **One reason to change**: If scanning algorithm changes

6. **SubtreeManager** (`subtree_manager.py`)
   - **Single Responsibility**: Orchestrate subtree operations
   - **One reason to change**: If subtree workflow changes

7. **SubtreeConverter** (`cli.py`)
   - **Single Responsibility**: Coordinate high-level conversion workflow
   - **One reason to change**: If conversion process changes

## Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension, closed for modification.

### Applied in:

1. **Protocol-based Interfaces**
   ```python
   class CommandRunner(Protocol):
       def run(self, cmd: list[str], ...) -> CommandResult: ...
   ```
   - **Open for extension**: New implementations can be added
   - **Closed for modification**: Existing code doesn't change
   - **Example**: Could add `MockCommandRunner`, `RemoteCommandRunner`, etc.

2. **GitOperations Protocol**
   ```python
   class GitOperations(Protocol):
       def get_remote_url(self, ...) -> str | None: ...
       def ensure_remote(self, ...) -> None: ...
   ```
   - **Open for extension**: New git operations can be added
   - **Closed for modification**: Existing operations remain unchanged
   - **Example**: Could add `GitHubGitOperations`, `GitLabGitOperations`

## Liskov Substitution Principle (LSP)

**Definition**: Subtypes must be substitutable for their base types.

### Applied in:

1. **SubprocessCommandRunner implements CommandRunner**
   ```python
   class SubprocessCommandRunner:
       def run(self, ...) -> CommandResult:
           # Implementation using subprocess
   ```
   - Can be substituted anywhere `CommandRunner` is expected
   - Maintains same interface contract
   - No surprising behavior changes

2. **GitOperationsImpl implements GitOperations**
   ```python
   class GitOperationsImpl:
       def __init__(self, runner: CommandRunner): ...
   ```
   - Can be substituted anywhere `GitOperations` is expected
   - Honors the protocol contract
   - Works with any `CommandRunner` implementation

## Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use.

### Applied in:

1. **Focused Protocols**
   - **CommandRunner**: Only `run()` method
   - **GitOperations**: Only git-related methods
   - No monolithic "RepositoryManager" with dozens of methods

2. **Small, Cohesive Classes**
   - Each class provides only what its clients need
   - **BackupManager**: Only backup/restore operations
   - **PathResolver**: Only path manipulation
   - **RepositoryScanner**: Only scanning operations

## Dependency Inversion Principle (DIP)

**Definition**: Depend on abstractions, not concretions.

### Applied in:

1. **High-level modules depend on Protocols**
   ```python
   class SubtreeManager:
       def __init__(
           self,
           git_ops: GitOperations,      # Protocol, not concrete class
           backup_mgr: BackupManager,   # Abstract interface
           path_resolver: PathResolver, # Abstract interface
       ):
   ```

2. **Dependency Injection**
   ```python
   # In main():
   runner = SubprocessCommandRunner()           # Concrete implementation
   git_ops = GitOperationsImpl(runner)          # Injected dependency
   backup_mgr = BackupManager()                 # Injected dependency
   subtree_mgr = SubtreeManager(git_ops, ...)   # Dependencies injected
   ```

3. **Benefits**:
   - Easy to test (inject mocks)
   - Easy to swap implementations
   - No hard dependencies on concrete classes

## Additional Design Principles

### DRY (Don't Repeat Yourself)

- **Common operations extracted**: `sanitize_remote_name`, `find_prismq_root`
- **Reusable components**: `CommandRunner` used by multiple modules
- **No code duplication**: Each operation implemented once

### KISS (Keep It Simple, Stupid)

- **Small, focused functions**: Each function does one thing well
- **Clear naming**: Function names describe what they do
- **Minimal complexity**: No unnecessary abstractions

### Composition Over Inheritance

- **No inheritance hierarchies**: Classes composed of collaborators
- **Favor delegation**: Objects delegate to their dependencies
- **Example**: `SubtreeManager` composes `GitOperations`, `BackupManager`, `PathResolver`

## Testing Benefits

The SOLID design makes testing straightforward:

```python
def test_add_subtree():
    git_ops = MagicMock()        # Mock GitOperations
    backup_mgr = MagicMock()     # Mock BackupManager
    
    subtree_mgr = SubtreeManager(git_ops, backup_mgr, ...)
    # Test in isolation
```

## Extensibility Examples

### Adding a New Command Runner

```python
class RemoteCommandRunner:
    """Execute commands on remote host via SSH."""
    
    def run(self, cmd: list[str], ...) -> CommandResult:
        # SSH implementation
        ...

# Use it
runner = RemoteCommandRunner(host="server.com")
git_ops = GitOperationsImpl(runner)
# Everything else works unchanged!
```

### Adding New Git Operations

```python
class ExtendedGitOperations(GitOperationsImpl):
    """Extended git operations with additional features."""
    
    def get_commit_count(self, repo_path: Path) -> int:
        # New operation
        ...

# Use it
git_ops = ExtendedGitOperations(runner)
# All existing code continues to work
```

## Conclusion

The refactored subtree converter demonstrates:

- **Clear separation of concerns**: Each module has one job
- **Loose coupling**: Components depend on abstractions
- **High testability**: Easy to test in isolation
- **Easy extensibility**: New features can be added without changing existing code
- **Maintainability**: Changes are localized to single modules

This architecture makes the codebase easier to understand, test, and extend while following industry best practices.
