# Recursive Module Hierarchy Usage Guide

## Overview

The submodule converter now supports fully recursive nested module hierarchies, allowing you to have modules within modules to arbitrary depths.

## Use Case

This feature is designed for complex project structures like:

```
PrismQ/
  mod/
    IdeaInspiration/              # AI inspiration gathering
      mod/
        Classification/            # Content classification
          mod/
            Analysis/              # Deep analysis tools
        DataCollection/            # Data collection tools
```

Each module can have its own `mod/` directory containing sub-modules, which are independent git repositories with their own remote URLs.

## How It Works

### Module Identification

A **module** is any git repository that is directly under a `mod/` directory:
- `mod/IdeaInspiration/` ✓ (module root, top-level)
- `mod/IdeaInspiration/mod/Classification/` ✓ (module root, nested)
- `mod/IdeaInspiration/mod/Classification/SomeRepo/` ✗ (nested repo, not a module)

### Processing Order

The converter processes modules in **depth-first order** (deepest first):

1. Deepest modules are converted to submodules in their parent modules
2. Then parent modules are converted to submodules in their parents
3. Finally, top-level modules are converted to submodules in PrismQ root

This ensures that when a module is converted, all its nested modules are already submodules.

## Example Scenario

### Initial Structure

```
PrismQ/.git
  mod/
    IdeaInspiration/.git
      (git remote: https://github.com/user/PrismQ.IdeaInspiration.git)
      mod/
        Classification/.git
          (git remote: https://github.com/user/PrismQ.IdeaInspiration.Classification.git)
          README.md
          src/
        DataCollection/.git
          (git remote: https://github.com/user/PrismQ.IdeaInspiration.DataCollection.git)
```

### Conversion Process

**Step 1: Find all modules by depth**
```
Depth 1 (deepest):
  - Classification (parent: IdeaInspiration)
  - DataCollection (parent: IdeaInspiration)

Depth 0 (top-level):
  - IdeaInspiration (parent: None)
```

**Step 2: Convert deepest modules first**

```bash
# Classification
cd IdeaInspiration
git submodule add -b main \
  https://github.com/user/PrismQ.IdeaInspiration.Classification.git \
  mod/Classification

# DataCollection
cd IdeaInspiration
git submodule add -b main \
  https://github.com/user/PrismQ.IdeaInspiration.DataCollection.git \
  mod/DataCollection
```

**Step 3: Convert top-level modules**

```bash
# IdeaInspiration (now contains submodules)
cd PrismQ
git submodule add -b main \
  https://github.com/user/PrismQ.IdeaInspiration.git \
  mod/IdeaInspiration
```

### Final Structure

```
PrismQ/.git
  .gitmodules (contains: mod/IdeaInspiration)
  mod/
    IdeaInspiration/
      .git (submodule link)
      .gitmodules (contains: mod/Classification, mod/DataCollection)
      mod/
        Classification/
          .git (submodule link)
          README.md
          src/
        DataCollection/
          .git (submodule link)
```

## Depth Calculation

The converter calculates depth by counting "mod" directories in the path:

| Path | Depth |
|------|-------|
| `mod/IdeaInspiration` | 0 (one "mod") |
| `mod/IdeaInspiration/mod/Classification` | 1 (two "mod"s) |
| `mod/IdeaInspiration/mod/Classification/mod/Analysis` | 2 (three "mod"s) |

## Running the Converter

```bash
# From PrismQ root
cd /path/to/PrismQ
python -m scripts.submodule-converter
```

The converter will:
1. Scan all `mod/` directories recursively
2. Identify all modules at all depths
3. Process them in depth-first order
4. Create backups before each operation
5. Rollback on failure

## After Conversion

### Cloning with Submodules

```bash
# Clone PrismQ
git clone https://github.com/user/PrismQ.git
cd PrismQ

# Initialize all submodules recursively
git submodule update --init --recursive
```

The `--recursive` flag is **crucial** for nested submodules!

### Updating Submodules

```bash
# Update all submodules to latest
git submodule update --remote --recursive

# Update specific nested submodule
cd mod/IdeaInspiration
git submodule update --remote mod/Classification
```

### Working with Nested Submodules

```bash
# Make changes in nested submodule
cd mod/IdeaInspiration/mod/Classification
git checkout main
# ... make changes ...
git add .
git commit -m "Update classification logic"
git push

# Update parent submodule reference
cd ../../  # Back to IdeaInspiration
git add mod/Classification
git commit -m "Update Classification submodule"
git push

# Update PrismQ reference
cd ../..  # Back to PrismQ
git add mod/IdeaInspiration
git commit -m "Update IdeaInspiration submodule"
git push
```

## Best Practices

### 1. Module Organization

- Keep module names descriptive and unique
- Use consistent naming: `PrismQ.Module.SubModule`
- Document dependencies between modules

### 2. Remote URLs

- Ensure all modules have proper remote URLs before conversion
- Use HTTPS or SSH consistently
- Test that all remotes are accessible

### 3. Branches

- Use a consistent default branch (main/master)
- Document branch strategies in each module
- Consider using the same branch name across all modules

### 4. Pre-Conversion Checklist

- ✅ All modules have remotes configured
- ✅ All changes are committed and pushed
- ✅ Working directory is clean
- ✅ All nested modules are pushed to their remotes
- ✅ Backups exist (converter creates them automatically)

### 5. Post-Conversion

- Test `git submodule update --init --recursive`
- Verify all modules are accessible
- Update CI/CD pipelines to handle recursive submodules
- Document the new structure for team members

## Troubleshooting

### Problem: "fatal: not a git repository"

**Cause**: Trying to convert before all nested repos have remotes

**Solution**: 
```bash
# Check all repos have remotes
find mod -name .git -type d | while read repo; do
  cd "$(dirname "$repo")"
  echo "Checking $(pwd)"
  git remote -v
  cd -
done
```

### Problem: Submodule not initialized after cloning

**Cause**: Forgot `--recursive` flag

**Solution**:
```bash
git submodule update --init --recursive
```

### Problem: Can't push changes in nested submodule

**Cause**: Submodule is in detached HEAD state

**Solution**:
```bash
cd mod/IdeaInspiration/mod/Classification
git checkout main
# Now make changes
```

### Problem: Conversion fails mid-way

**Cause**: Network issue, permission problem, etc.

**Solution**: The converter automatically restores from backup. You can re-run:
```bash
python -m scripts.submodule-converter
```

## Advanced: Programmatic Usage

```python
from pathlib import Path
from scripts.submodule_converter import (
    RepositoryScanner,
    SubmoduleManager,
    SubmoduleConverter,
    GitOperationsImpl,
    SubprocessCommandRunner,
    BackupManager,
    PathResolver,
)

# Initialize components
runner = SubprocessCommandRunner()
git_ops = GitOperationsImpl(runner)
backup_mgr = BackupManager()
path_resolver = PathResolver()
scanner = RepositoryScanner()
submodule_mgr = SubmoduleManager(git_ops, backup_mgr, path_resolver)

# Create converter
converter = SubmoduleConverter(scanner, submodule_mgr, git_ops, path_resolver)

# Find PrismQ root
prismq_root = path_resolver.find_prismq_root()
mod_root = prismq_root / "mod"

# Scan for modules
module_repos = scanner.find_module_roots(mod_root)

# Inspect before converting
for repo in module_repos:
    print(f"Module: {repo.module_name}")
    print(f"  Depth: {repo.depth}")
    print(f"  Parent: {repo.parent_module or 'None (top-level)'}")

# Run conversion
converter.convert_modules_to_submodules(prismq_root, mod_root)
```

## Comparison: Before vs. After

### Before (Git Repositories)

**Pros:**
- Simple structure
- Easy to understand
- No submodule complexity

**Cons:**
- Can't version independently
- All-or-nothing updates
- Hard to reuse across projects
- No clear module boundaries

### After (Git Submodules)

**Pros:**
- Independent versioning per module
- Can pin specific versions
- Reusable across projects
- Clear module boundaries
- Each module has its own history

**Cons:**
- More complex to manage
- Requires `--recursive` flag
- Need to update parent repos
- Learning curve for team

## References

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [PrismQ Submodule Converter README](./README.md)
- [SOLID Principles Documentation](./SOLID_PRINCIPLES.md)
- [Architecture Overview](./ARCHITECTURE.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test cases in `test_subtree_converter.py`
3. Open an issue on GitHub
4. Consult the architecture documentation
