# Git Utilities

A collection of utility scripts for managing nested git repositories and submodules in the PrismQ workspace.

## Scripts Overview

### 1. check-submodules
**Purpose:** Validates if each folder in any mod/ directory is mapped in the nearest parent's .gitmodules

**Usage:**
```bash
# Windows
scripts\check-submodules.bat

# Linux/Mac
python scripts/git-utils/check_submodules.py
```

**What it does:**
- Recursively finds all mod/ directories
- Checks if each subdirectory is mapped in parent's .gitmodules
- Reports mapped and unmapped repositories
- Distinguishes between git repos and regular folders

**Output Example:**
```
📁 mod
   Parent: .
   ✅ Mapped RepositoryTemplate
   ✅ Mapped IdeaInspiration
   ⚠️  NOT mapped (is git repo) NewModule
```

### 2. map-submodules
**Purpose:** Automatically adds unmapped git repositories in mod/ directories to .gitmodules

**Usage:**
```bash
# Windows
scripts\map-submodules.bat

# Linux/Mac
python scripts/git-utils/map_submodules.py
```

**What it does:**
- Finds all git repositories in mod/ directories
- Checks if they're already mapped in .gitmodules
- Uses `git submodule add` to register unmapped repos
- Processes from deepest to shallowest (avoids "modified content" errors)

**Output Example:**
```
📁 mod/Sources
   Parent: mod/IdeaInspiration
   URL: https://github.com/Nomoos/PrismQ.IdeaInspiration.Sources.git
   ✅ Added: mod/Sources
```

### 3. git-commit-all
**Purpose:** Commits all changes in all repositories with a single commit message

**Usage:**
```bash
# Windows
scripts\git-commit-all.bat "Your commit message"

# Linux/Mac
python scripts/git-utils/git_commit_all.py "Your commit message"
```

**What it does:**
- Finds all git repositories recursively
- Runs `git add -A` in each repository
- Commits changes with the provided message
- Processes from deepest to shallowest
- Reports clean, committed, and failed repositories

**Output Example:**
```
📁 mod/IdeaInspiration
   ✅ Committed successfully

📁 .
   ✅ Committed successfully
```

### 4. git-push-all
**Purpose:** Pushes all repositories to their remotes recursively

**Usage:**
```bash
# Windows
scripts\git-push-all.bat

# Linux/Mac
python scripts/git-utils/git_push_all.py
```

**What it does:**
- Finds all git repositories recursively
- Pushes each repository to origin
- Skips repositories without remotes
- Processes from deepest to shallowest
- Reports pushed, up-to-date, and failed repositories

**Output Example:**
```
📁 mod/IdeaInspiration (main)
   ✅ Pushed successfully

📁 . (main)
   ✅ Already up to date
```

## Workflow Example

Complete workflow for adding and registering new repositories:

```bash
# 1. Create/clone repositories only
scripts\add-repo.bat PrismQ.Module.SubModule

# 2. Verify what's mapped
scripts\check-submodules.bat

# 3. Map any unmapped repositories
scripts\map-submodules.bat

# 4. Commit all changes
scripts\git-commit-all.bat "Add new submodules"

# 5. Push to remote
scripts\git-push-all.bat

# 6. Verify final state
scripts\check-submodules.bat
```

## Design Philosophy

### Separation of Concerns
Each script has a single, clear responsibility:
- **add-repo**: Repository creation/cloning only
- **check-submodules**: Validation only
- **map-submodules**: Submodule registration only
- **git-commit-all**: Committing changes only
- **git-push-all**: Pushing changes only

### Deepest-to-Shallowest Processing
All scripts that modify repositories process from deepest to shallowest level to avoid:
- "modified content" errors in parent repositories
- Dependency issues between nested submodules
- Race conditions in git operations

### Recursive mod/ Discovery
Following the pattern from `git_pull_all.bat`:
- Recursively finds all mod/ directories at any depth
- No hardcoded paths or depth limits
- Works with any level of nesting

### Error Handling
- Clear error messages with emoji indicators
- Continues processing on errors (doesn't fail fast)
- Summary report at the end
- Non-zero exit codes on failure

## Testing

All scripts have been tested with:
- Empty mod/ directories
- Single-level nesting (PrismQ → Module)
- Multi-level nesting (PrismQ → A → B → C)
- Mixed mapped/unmapped repositories
- Repositories without remotes

## Requirements

- Python 3.8 or higher
- Git installed and in PATH
- Windows (for .bat wrappers) or Linux/Mac (run .py directly)

## Architecture

```
scripts/
├── add-repo.bat                    # Repository creation wrapper
├── check-submodules.bat            # Validation wrapper
├── map-submodules.bat              # Registration wrapper
├── git-commit-all.bat              # Commit wrapper
├── git-push-all.bat                # Push wrapper
├── git_pull_all.bat                # Pull wrapper (existing)
├── add-repo-with-submodule/        # Repository creation logic
└── git-utils/                      # Git utility implementations
    ├── check_submodules.py         # Validation implementation
    ├── map_submodules.py           # Registration implementation
    ├── git_commit_all.py           # Commit implementation
    ├── git_push_all.py             # Push implementation
    └── README.md                   # This file
```

## Future Enhancements

Possible additions:
- `git-status-all`: Show status of all repositories
- `git-fetch-all`: Fetch from all remotes
- `git-clean-all`: Clean all repositories
- `unmap-submodules`: Remove submodule mappings
- Configuration file for custom mod/ directory names
