# Architecture Overview

This document provides a high-level overview of the subtree converter architecture.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              SubtreeConverter                         │  │
│  │  (Orchestrates high-level conversion workflow)       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ SubtreeManager │  │ RepoScanner    │  │ PathResolver │  │
│  │ (Subtree ops)  │  │ (Find repos)   │  │ (Path utils) │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ GitOperations  │  │ BackupManager  │  │CommandRunner │  │
│  │ (Git commands) │  │ (Backup/restore│  │ (Execute cmd)│  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      System Layer                            │
│         subprocess, shutil, pathlib, os                      │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### CLI Layer
- **SubtreeConverter**: Orchestrates the conversion workflow
  - Coordinates nested repository conversion
  - Coordinates module root conversion
  - Handles high-level error reporting

### Business Logic Layer
- **SubtreeManager**: Manages subtree operations
  - Orchestrates backup, remote setup, and subtree add
  - Handles rollback on failure
  
- **RepositoryScanner**: Discovers repositories
  - Finds nested git repositories
  - Identifies module roots
  
- **PathResolver**: Path manipulation
  - Finds PrismQ root
  - Sanitizes remote names
  - Normalizes paths

### Infrastructure Layer
- **GitOperations**: Git command abstraction
  - Remote management (add, update)
  - Branch detection
  - Subtree operations
  
- **BackupManager**: Backup/restore operations
  - Creates timestamped backups
  - Restores on failure
  - Cleans up on success
  
- **CommandRunner**: Command execution abstraction
  - Executes shell commands
  - Captures output
  - Handles errors

### System Layer
- Standard Python libraries for OS operations

## Data Flow

### Nested Repository Conversion

```
1. Find PrismQ root
   └─> PathResolver.find_prismq_root()

2. Scan for nested repos
   └─> RepositoryScanner.find_nested_repositories()

3. For each nested repo:
   a. Get remote URL
      └─> GitOperations.get_remote_url()
   
   b. Get default branch
      └─> GitOperations.get_default_branch()
   
   c. Normalize path
      └─> PathResolver.normalize_path_in_module()
   
   d. Sanitize remote name
      └─> PathResolver.sanitize_remote_name()
   
   e. Add as subtree
      └─> SubtreeManager.add_subtree()
          ├─> BackupManager.create_backup()
          ├─> GitOperations.ensure_remote()
          ├─> GitOperations.subtree_add()
          └─> BackupManager.cleanup_backup()
               OR
          └─> BackupManager.restore_backup() (on failure)
```

### Module Root Conversion

```
1. Scan for module roots
   └─> RepositoryScanner.find_module_roots()

2. For each module root:
   a. Get remote URL
      └─> GitOperations.get_remote_url()
   
   b. Get default branch
      └─> GitOperations.get_default_branch()
   
   c. Sanitize remote name
      └─> PathResolver.sanitize_remote_name()
   
   d. Add as subtree
      └─> SubtreeManager.add_subtree()
          (same steps as nested repo conversion)
```

## Dependency Graph

```
┌──────────────────┐
│ SubtreeConverter │
└────────┬─────────┘
         │
         ├─> RepositoryScanner
         │
         ├─> PathResolver
         │
         ├─> GitOperations ──┐
         │                   │
         └─> SubtreeManager ─┤
                   │         │
                   ├─────────┘
                   │
                   ├─> BackupManager
                   │
                   └─> PathResolver

GitOperations ──> CommandRunner
```

## Protocol-Based Design

### Protocols (Interfaces)

```python
CommandRunner Protocol:
├─ run(cmd, cwd, check, capture) -> CommandResult

GitOperations Protocol:
├─ get_remote_url(repo_path, remote) -> str | None
├─ get_default_branch(repo_path) -> str
├─ ensure_remote(repo_path, name, url) -> None
└─ subtree_add(repo_path, prefix, remote, branch) -> None
```

### Implementations

```python
SubprocessCommandRunner implements CommandRunner
└─ Uses subprocess module

GitOperationsImpl implements GitOperations
└─ Uses CommandRunner (injected dependency)

BackupManager (concrete class)
└─ Uses shutil, pathlib

PathResolver (concrete class)
└─ Uses pathlib, os

RepositoryScanner (concrete class)
└─ Uses pathlib, os
```

## Error Handling Strategy

```
Exception Hierarchy:
SubtreeConverterError (base)
├─ CommandExecutionError (command failures)
├─ RepositoryNotFoundError (missing repos)
├─ BackupError (backup/restore failures)
└─ PathResolutionError (path issues)

Error Flow:
1. Low-level errors caught and wrapped
2. Specific exceptions raised with context
3. Backup restoration on failures
4. High-level error reporting to user
```

## Testing Strategy

### Unit Tests
- Each module tested in isolation
- Dependencies mocked
- Focus on single responsibility

### Test Coverage
```
CommandRunner: 3 tests
├─ Successful execution
├─ Failed execution with check
└─ Failed execution without check

PathResolver: 4 tests
├─ Remote name sanitization
├─ Path normalization
├─ Root finding
└─ Error cases

BackupManager: 4 tests
├─ Create backup (existing)
├─ Create backup (non-existing)
├─ Restore backup
└─ Cleanup backup

GitOperations: 6 tests
├─ Get remote URL (success/failure)
├─ Get default branch (multiple methods)
└─ Ensure remote (add/update)

RepositoryScanner: 2 tests
├─ Find nested repositories
└─ Find module roots

SubtreeManager: 3 tests
├─ Add subtree (success)
├─ Add subtree with backup
└─ Restore on failure

CommandResult: 1 test
└─ Success property
```

## Extensibility Points

### Adding New Command Runner
```python
class RemoteCommandRunner:
    """Execute commands via SSH."""
    def run(self, cmd, ...) -> CommandResult:
        # SSH implementation
```

### Adding New Git Backend
```python
class LibGit2Operations:
    """Git operations using libgit2."""
    def __init__(self, repo_path):
        # libgit2 setup
```

### Adding Logging
```python
class LoggingCommandRunner:
    """Wrapper that logs all commands."""
    def __init__(self, base_runner):
        self._base = base_runner
    
    def run(self, cmd, ...):
        log.info(f"Running: {cmd}")
        return self._base.run(cmd, ...)
```

### Adding Dry-Run Mode
```python
class DryRunCommandRunner:
    """Simulates commands without executing."""
    def run(self, cmd, ...):
        print(f"Would run: {cmd}")
        return CommandResult(0, "", "")
```

## Configuration

### Current (Hard-coded)
- Remote names: `st_{module}_{path}`
- Backup naming: `{path}.pre_subtree.{timestamp}`
- Default branch fallback: "main"

### Future (Configurable)
```python
class Config:
    remote_prefix: str = "st_"
    backup_suffix: str = "pre_subtree"
    default_branch: str = "main"
    squash: bool = True
```

## Performance Characteristics

### Time Complexity
- Repository scanning: O(n) where n = number of directories
- Git operations: O(m) where m = number of repositories
- Overall: O(n + m * k) where k = git operations per repo

### Space Complexity
- Memory: O(m) for storing repository list
- Disk: O(s) for backups where s = size of directories

### Bottlenecks
- Git operations (network-bound)
- Directory backups (I/O-bound)
- Not CPU-bound

### Optimization Opportunities
1. Parallel repository processing
2. Incremental backups
3. Remote URL caching
4. Lazy evaluation of repository list

## Security Considerations

1. **Input Validation**
   - Path traversal prevention
   - Command injection prevention
   - Remote name sanitization

2. **Backup Safety**
   - Timestamped backups prevent overwriting
   - Atomic operations where possible
   - Rollback on failure

3. **Command Execution**
   - No shell=True (prevents injection)
   - Validated arguments
   - Error handling

## Future Enhancements

1. **Dry-run mode**: Preview changes without executing
2. **Parallel processing**: Convert multiple repos concurrently
3. **Configuration file**: YAML/JSON config for behavior
4. **Progress bars**: Visual feedback for long operations
5. **Logging**: Structured logging with levels
6. **History tracking**: Record conversions for audit
7. **Selective conversion**: Convert specific repositories only
8. **Conflict resolution**: Handle merge conflicts automatically

## Maintenance Guidelines

### Adding New Features
1. Identify the appropriate layer
2. Create new module if needed
3. Define protocol if abstraction needed
4. Write tests first (TDD)
5. Implement feature
6. Update documentation

### Fixing Bugs
1. Write failing test that reproduces bug
2. Fix the issue
3. Verify test passes
4. Run full test suite
5. Update documentation if needed

### Refactoring
1. Ensure full test coverage first
2. Make small, incremental changes
3. Run tests after each change
4. Keep commits focused
5. Update documentation

## Dependencies

### External
- Python 3.10+ (type hints, pattern matching)
- Git 2.x+ (subtree command)

### Internal (Python stdlib)
- subprocess (command execution)
- pathlib (path handling)
- shutil (file operations)
- os (OS interface)
- time (timestamps)

### Testing
- pytest (test framework)
- unittest.mock (mocking)

### Development
- ruff (linting)
- mypy (type checking)
