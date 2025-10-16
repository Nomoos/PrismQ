# Usage Examples

This document provides practical examples of using the subtree converter.

## Basic Usage

### Running from Command Line

```bash
# Navigate to PrismQ root or any subdirectory
cd /path/to/PrismQ

# Run the converter
python -m scripts.subtree-converter
# or
python scripts/subtree-converter/cli.py
```

### Expected Output

```
PrismQ root : /path/to/PrismQ
MOD root    : /path/to/PrismQ/mod

=== Step 1: Nested repos -> subtree in MODULE ROOT ===
[INFO] Backing up existing path: /path/to/module/nested -> /path/to/module/nested.pre_subtree.20231016_123456
[DO] git -C /path/to/module subtree add --prefix="nested" remote_name main --squash
[CLEAN] Removing backup: /path/to/module/nested.pre_subtree.20231016_123456

=== Step 2: Module ROOTS -> subtree in PrismQ under <Module> ===
[INFO] Backing up existing path: /path/to/PrismQ/Module -> /path/to/PrismQ/Module.pre_subtree.20231016_123457
[DO] git -C /path/to/PrismQ subtree add --prefix="Module" remote_name main --squash
[CLEAN] Removing backup: /path/to/PrismQ/Module.pre_subtree.20231016_123457

Done. Commit changes (squash commits from subtree).
To update later:
  git subtree pull --prefix=PATH REMOTE BRANCH --squash
To export changes to upstream:
  git subtree push --prefix=PATH REMOTE BRANCH
```

## Programmatic Usage

### As a Library

```python
import sys
sys.path.insert(0, 'scripts/subtree-converter')

from backup_manager import BackupManager
from command_runner import SubprocessCommandRunner
from git_operations import GitOperationsImpl
from path_resolver import PathResolver
from repository_scanner import RepositoryScanner
from subtree_manager import SubtreeManager
from cli import SubtreeConverter

# Initialize dependencies (Dependency Injection)
runner = SubprocessCommandRunner()
git_ops = GitOperationsImpl(runner)
backup_mgr = BackupManager()
path_resolver = PathResolver()
scanner = RepositoryScanner()
subtree_mgr = SubtreeManager(git_ops, backup_mgr, path_resolver)

# Find PrismQ root
prismq_root = path_resolver.find_prismq_root()
mod_root = prismq_root / "mod"

# Create converter
converter = SubtreeConverter(scanner, subtree_mgr, git_ops, path_resolver)

# Run conversion
converter.convert_nested_to_subtrees(mod_root)
converter.convert_modules_to_subtrees(prismq_root, mod_root)
```

### Custom Command Runner

```python
from command_runner import CommandRunner, CommandResult
from pathlib import Path

class LoggingCommandRunner:
    """Command runner that logs all commands."""
    
    def __init__(self, base_runner: CommandRunner):
        self._base_runner = base_runner
        
    def run(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        check: bool = True,
        capture: bool = False,
    ) -> CommandResult:
        print(f"[LOG] Running: {' '.join(cmd)}")
        if cwd:
            print(f"[LOG] In directory: {cwd}")
        return self._base_runner.run(cmd, cwd, check, capture)

# Use it
base_runner = SubprocessCommandRunner()
logging_runner = LoggingCommandRunner(base_runner)
git_ops = GitOperationsImpl(logging_runner)
# ... rest of setup
```

### Testing with Mocks

```python
from unittest.mock import MagicMock
from pathlib import Path

# Create mocks
git_ops = MagicMock()
git_ops.get_remote_url.return_value = "https://github.com/test/repo.git"
git_ops.get_default_branch.return_value = "main"

backup_mgr = MagicMock()
backup_mgr.create_backup.return_value = None

# Create subtree manager with mocks
subtree_mgr = SubtreeManager(git_ops, backup_mgr, PathResolver())

# Test operations
subtree_mgr.add_subtree(
    Path("/test/repo"),
    "prefix",
    "https://github.com/test/repo.git",
    "main",
    "remote_name",
)

# Verify calls
git_ops.ensure_remote.assert_called_once()
git_ops.subtree_add.assert_called_once()
```

## Advanced Usage

### Scanning Repositories Only

```python
from path_resolver import PathResolver
from repository_scanner import RepositoryScanner

# Find repositories
resolver = PathResolver()
scanner = RepositoryScanner()

prismq_root = resolver.find_prismq_root()
mod_root = prismq_root / "mod"

# Get nested repos
nested_repos = scanner.find_nested_repositories(mod_root)
for repo in nested_repos:
    print(f"Nested: {repo.path}")
    print(f"  Module: {repo.module_name}")
    print(f"  Relative path: {repo.relative_in_module}")

# Get module roots
module_repos = scanner.find_module_roots(mod_root)
for repo in module_repos:
    print(f"Module: {repo.module_name} at {repo.path}")
```

### Manual Git Operations

```python
from command_runner import SubprocessCommandRunner
from git_operations import GitOperationsImpl
from pathlib import Path

runner = SubprocessCommandRunner()
git_ops = GitOperationsImpl(runner)

repo_path = Path("/path/to/repo")

# Get remote URL
url = git_ops.get_remote_url(repo_path)
print(f"Remote URL: {url}")

# Get default branch
branch = git_ops.get_default_branch(repo_path)
print(f"Default branch: {branch}")

# Ensure remote exists
git_ops.ensure_remote(repo_path, "upstream", "https://github.com/user/repo.git")

# Add subtree
git_ops.subtree_add(repo_path, "vendor/lib", "upstream", "main")
```

### Backup Management

```python
from backup_manager import BackupManager
from pathlib import Path

mgr = BackupManager()

target = Path("/path/to/directory")

# Create backup
backup_path = mgr.create_backup(target)
if backup_path:
    print(f"Backup created: {backup_path}")
    
    # Try something risky
    try:
        # ... risky operation ...
        pass
    except Exception:
        # Restore on failure
        mgr.restore_backup(backup_path, target)
    else:
        # Clean up on success
        mgr.cleanup_backup(backup_path)
```

## Error Handling

### Catching Specific Errors

```python
from exceptions import (
    SubtreeConverterError,
    CommandExecutionError,
    RepositoryNotFoundError,
    BackupError,
    PathResolutionError,
)

try:
    converter.convert_nested_to_subtrees(mod_root)
except CommandExecutionError as e:
    print(f"Git command failed: {e}")
except RepositoryNotFoundError as e:
    print(f"Repository not found: {e}")
except BackupError as e:
    print(f"Backup operation failed: {e}")
except PathResolutionError as e:
    print(f"Path resolution failed: {e}")
except SubtreeConverterError as e:
    print(f"Converter error: {e}")
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/convert-to-subtrees.yml
name: Convert to Subtrees
on:
  workflow_dispatch:

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run subtree converter
        run: |
          python -m scripts.subtree-converter
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Convert nested repos to subtrees"
          git push
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if any nested repositories exist
if python scripts/subtree-converter/repository_scanner.py; then
    echo "Warning: Nested repositories detected"
    echo "Consider running: python -m scripts.subtree-converter"
fi
```

## Troubleshooting

### Common Issues

**Issue**: "Could not find .git above current location"
```bash
# Solution: Run from PrismQ directory or subdirectory
cd /path/to/PrismQ
python -m scripts.subtree-converter
```

**Issue**: "Module directory not found"
```bash
# Solution: Ensure mod/ directory exists
mkdir -p mod
```

**Issue**: Command execution fails
```python
# Solution: Check git is installed and working
from command_runner import SubprocessCommandRunner
runner = SubprocessCommandRunner()
result = runner.run(["git", "--version"], capture=True, check=False)
print(result.stdout)
```

## Performance Tips

1. **Backup locations**: Backups are created in the same directory with timestamp suffixes
2. **Remote caching**: Remote URLs are fetched once per repository
3. **Branch detection**: Uses cached git metadata when possible
4. **Parallel processing**: Could be added for multiple repositories (future enhancement)

## Safety Features

1. **Automatic backups**: Original directories are backed up before conversion
2. **Rollback on failure**: Backups are restored if subtree add fails
3. **Cleanup on success**: Backups are removed after successful conversion
4. **Dry-run mode**: Could be added for preview (future enhancement)

## Next Steps

After conversion:

```bash
# Verify the conversion
git status
git log --oneline -10

# Update subtrees later
git subtree pull --prefix=Module upstream main --squash

# Push changes back to upstream
git subtree push --prefix=Module upstream main
```
