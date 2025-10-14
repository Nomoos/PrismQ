# PrismQ Scripts

Utility scripts for managing the PrismQ modular repository.

## Module Creation Scripts

These scripts help you create new PrismQ modules with the proper structure and configuration.

### Available Scripts

- **`add-module.sh`** - Linux/macOS module creation script
- **`add-module.bat`** - Windows module creation script

### Quick Start

#### Linux/macOS

```bash
# Make script executable (first time only)
chmod +x scripts/add-module.sh

# Run the interactive script
./scripts/add-module.sh
```

#### Windows

```batch
# Run the interactive script
scripts\add-module.bat
```

The script will interactively prompt you for:
- Module name (e.g., `MyNewModule`)
- Module description
- GitHub owner/organization (default: `Nomoos`)

It will then:
1. Create the module directory structure
2. Generate configuration files (`module.json`, `README.md`, etc.)
3. Initialize a Git repository
4. Set up the remote URL
5. Create an initial commit

## Module Synchronization Scripts

These scripts automate the synchronization of first-level modules from their separate repositories into the main PrismQ repository using Git subtree.

### Available Scripts

- **`sync-modules.sh`** - Linux/macOS synchronization script
- **`sync-modules.bat`** - Windows synchronization script

## Quick Start

### Linux/macOS

```bash
# Make script executable (first time only)
chmod +x scripts/sync-modules.sh

# Sync all modules
./scripts/sync-modules.sh

# Sync specific module
./scripts/sync-modules.sh src/RepositoryTemplate

# List configured modules
./scripts/sync-modules.sh --list

# Show help
./scripts/sync-modules.sh --help
```

### Windows

```batch
# Sync all modules
scripts\sync-modules.bat

# Sync specific module
scripts\sync-modules.bat src/RepositoryTemplate

# List configured modules
scripts\sync-modules.bat --list

# Show help
scripts\sync-modules.bat --help
```

## How It Works

The sync scripts use **Git subtree** to manage module synchronization:

1. **Configuration**: Each first-level module is configured with its remote repository URL
2. **Remote Management**: Scripts automatically add Git remotes if they don't exist
3. **Subtree Pull**: Uses `git subtree pull` to merge changes from module repositories
4. **Squash Commits**: Combines module commits into a single commit in the main repo

### Benefits of Git Subtree

- ✅ Full code in main repository (no external dependencies)
- ✅ Bidirectional sync (pull from and push to module repos)
- ✅ Preserves history
- ✅ No `.gitmodules` file needed
- ✅ Works with standard Git commands

## Configuration

There are two ways to configure modules for synchronization:

### Option 1: REMOTE.md File (Recommended)

Each module can have a `REMOTE.md` file in its root directory that specifies the remote repository configuration. This is the recommended approach as it keeps configuration with the module.

**Create `src/YourModule/REMOTE.md`:**

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

The sync script will automatically discover and use modules with `REMOTE.md` files.

### Option 2: Script Configuration

Alternatively, edit the configuration array in the script:

**In `sync-modules.sh` (Linux/macOS):**

```bash
declare -a MODULES=(
    "src/RepositoryTemplate|repositorytemplate-remote|https://github.com/Nomoos/PrismQ.RepositoryTemplate.git|main"
    "src/IdeaInspiration|ideainspiration-remote|https://github.com/Nomoos/PrismQ.IdeaInspiration.git|main"
    # Add your new module:
    "src/YourModule|yourmodule-remote|https://github.com/Nomoos/PrismQ.YourModule.git|main"
)
```

**In `sync-modules.bat` (Windows):**

```batch
set "modules[0]=src/RepositoryTemplate|repositorytemplate-remote|https://github.com/Nomoos/PrismQ.RepositoryTemplate.git|main"
set "modules[1]=src/IdeaInspiration|ideainspiration-remote|https://github.com/Nomoos/PrismQ.IdeaInspiration.git|main"
REM Add your new module:
set "modules[2]=src/YourModule|yourmodule-remote|https://github.com/Nomoos/PrismQ.YourModule.git|main"

REM Update module count
set module_count=3
```

### Configuration Format

```
module_path|remote_name|remote_url|branch
```

- **module_path**: Relative path to module (e.g., `src/RepositoryTemplate`)
- **remote_name**: Name for Git remote (e.g., `repositorytemplate-remote`)
- **remote_url**: GitHub repository URL
- **branch**: Branch to sync from (usually `main`)

## Usage Examples

### Sync All Modules

This is the most common operation - sync all configured first-level modules:

```bash
# Linux/macOS
./scripts/sync-modules.sh

# Windows
scripts\sync-modules.bat
```

### Sync Single Module

When you only want to update one specific module:

```bash
# Linux/macOS
./scripts/sync-modules.sh src/RepositoryTemplate

# Windows
scripts\sync-modules.bat src\RepositoryTemplate
```

### List Configured Modules

See which modules are configured for synchronization:

```bash
# Linux/macOS
./scripts/sync-modules.sh --list

# Windows
scripts\sync-modules.bat --list
```

## Integration into Module Template

To use this sync approach in your module development workflow:

### 1. Create Separate Module Repository

Create a new repository for your module using the RepositoryTemplate structure:

```bash
# Example: Creating PrismQ.NewModule repository
git clone https://github.com/Nomoos/PrismQ.RepositoryTemplate.git PrismQ.NewModule
cd PrismQ.NewModule

# Update module-specific content
# ... make your changes ...

# Push to your module repository
git remote set-url origin https://github.com/Nomoos/PrismQ.NewModule.git
git push -u origin main
```

### 2. Add Module to Sync Configuration

Update the sync scripts in the main PrismQ repository to include your new module.

### 3. Run Initial Sync

First sync will pull the module into the main repository:

```bash
./scripts/sync-modules.sh src/NewModule
```

### 4. Development Workflow

#### Option A: Develop in Module Repository

1. Work in the separate module repository
2. Commit and push changes to module repo
3. Sync to main PrismQ repo using sync script

```bash
# In module repository
cd PrismQ.NewModule
# ... make changes ...
git commit -am "Update feature"
git push

# In main PrismQ repository
cd PrismQ
./scripts/sync-modules.sh src/NewModule
```

#### Option B: Develop in Main Repository

1. Work in the main PrismQ repository
2. Commit changes
3. Push to module repository using subtree push

```bash
# In main PrismQ repository
cd PrismQ
# ... make changes to src/NewModule ...
git commit -am "Update module"

# Push changes to module repository
git subtree push --prefix=src/NewModule newmodule-remote main
```

## Troubleshooting

### Remote Already Exists

If you see "Remote already exists", the script will use the existing remote. To update the URL:

```bash
git remote set-url remote-name new-url
```

### Fetch Fails / Repository Not Found

This usually means:
1. The module repository doesn't exist yet (create it first)
2. Incorrect repository URL (check configuration)
3. No access permissions (verify GitHub access)

### Merge Conflicts

If sync encounters conflicts:

```bash
# Resolve conflicts manually
git status  # See conflicted files
# Edit files to resolve conflicts
git add .
git commit -m "Resolve sync conflicts"
```

### First Sync Fails

When syncing a module for the first time with existing content:

```bash
# Use --allow-unrelated-histories
git subtree add --prefix=src/Module remote-name main --squash
```

## Advanced Usage

### Push Changes Back to Module Repository

After making changes in the main repository:

```bash
# Linux/macOS
git subtree push --prefix=src/RepositoryTemplate repositorytemplate-remote main

# This updates the module repository with changes made in main repo
```

### Fetch Without Merging

To see what changes are available without merging:

```bash
git fetch remote-name main
git diff HEAD..remote-name/main -- src/Module
```

## Best Practices

1. **Regular Syncs**: Run sync script regularly to keep modules up-to-date
2. **Module Independence**: Keep modules independent with minimal cross-dependencies
3. **Atomic Commits**: Make focused commits in module repositories
4. **Testing**: Test changes in module repo before syncing to main repo
5. **Documentation**: Keep module READMEs updated
6. **Branching**: Use branches in module repos for features, sync from `main`

## Automation

### GitHub Actions

You can automate syncing with GitHub Actions:

```yaml
name: Sync Modules

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync Modules
        run: |
          ./scripts/sync-modules.sh
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git push
```

### Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily sync at 2 AM
0 2 * * * cd /path/to/PrismQ && ./scripts/sync-modules.sh >> /var/log/prismq-sync.log 2>&1
```

## Related Documentation

- [Git Subtree Documentation](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- [PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate)
- [Main README](../README.md)

## Support

For issues with the sync scripts:
1. Check script output for error messages
2. Verify module repository exists and is accessible
3. Ensure you have the latest version of Git (2.x+)
4. Review configuration format in script

---

**Note**: These scripts manage first-level modules only (e.g., `src/RepositoryTemplate`, `src/IdeaInspiration`). Nested modules within these are managed as part of their parent module's repository.
