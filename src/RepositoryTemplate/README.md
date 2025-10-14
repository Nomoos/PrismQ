# PrismQ.RepositoryTemplate

Template module demonstrating the standard structure for all PrismQ modules.

## Purpose

This module serves as the template and reference implementation for creating new PrismQ modules. Each module in PrismQ follows this structure to ensure consistency and maintainability.

## Module Structure

```
RepositoryTemplate/
├── docs/              # Module documentation
├── issues/            # Module-specific issue tracking
│   ├── new/          # New issues
│   ├── wip/          # Work in progress
│   └── done/         # Completed issues
├── scripts/          # Module utility scripts
├── src/              # Module source code
└── tests/            # Module tests
```

## Responsibilities

- Provide a template structure for new modules
- Define standard conventions for module organization
- Serve as a reference implementation

## Related Modules

See the [main repository](https://github.com/Nomoos/PrismQ.RepositoryTemplate) for detailed template information.

## Module Synchronization

When using this template to create a new module that will be synced with the main PrismQ repository:

### 1. Create Module Repository

```bash
# Clone the template
git clone https://github.com/Nomoos/PrismQ.RepositoryTemplate.git PrismQ.YourModule
cd PrismQ.YourModule

# Update to your module repository
git remote set-url origin https://github.com/Nomoos/PrismQ.YourModule.git
git push -u origin main
```

### 2. Create REMOTE.md File (Recommended)

Create a `REMOTE.md` file in your module root to specify the remote repository configuration:

```markdown
# Remote Repository Configuration

This module is synchronized with its own repository.

## Repository Information

- **Remote URL**: `https://github.com/Nomoos/PrismQ.YourModule.git`
- **Remote Name**: `yourmodule-remote`
- **Branch**: `main`

## Configuration Format

This file uses a standard format that can be read by automation tools:

```
REMOTE_URL=https://github.com/Nomoos/PrismQ.YourModule.git
REMOTE_NAME=yourmodule-remote
BRANCH=main
```
```

The sync scripts will automatically discover your module via the `REMOTE.md` file.

### 3. Alternative: Manual Script Configuration

Alternatively, add your module to the sync script configuration in the main PrismQ repository:

**In `scripts/sync-modules.sh`:**
```bash
declare -a MODULES=(
    # ... existing modules ...
    "src/YourModule|yourmodule-remote|https://github.com/Nomoos/PrismQ.YourModule.git|main"
)
```

**In `scripts/sync-modules.bat`:**
```batch
set "modules[N]=src/YourModule|yourmodule-remote|https://github.com/Nomoos/PrismQ.YourModule.git|main"
set module_count=N+1
```

### 4. Sync to Main Repository

```bash
# From main PrismQ repository
./scripts/sync-modules.sh src/YourModule
```

The sync uses **git subtree** for bidirectional synchronization between module and main repositories.

For complete synchronization documentation, see [../../scripts/README.md](../../scripts/README.md).

