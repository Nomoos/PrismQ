# PrismQ Scripts

Utility scripts for managing the PrismQ modular repository on Windows.

## Module Creation Script

This script helps you create new PrismQ modules with the proper structure and configuration.

### Available Script

- **`add-module.bat`** - Windows module creation script

### Quick Start

```batch
# Run the interactive script
scripts\add-module.bat
```

The script will interactively prompt you for:

**Option 1: GitHub URL Input (Recommended)**
- GitHub repository URL (e.g., `https://github.com/Nomoos/PrismQ.MyModule.git` or `Nomoos/PrismQ.MyModule`)
- Module description (optional)

The script automatically:
- Parses the GitHub URL to extract owner and repository name
- Derives the module path from the repository name (e.g., `PrismQ.IdeaInspiration.Sources` → `src/IdeaInspiration/src/Sources`)
- Copies the complete RepositoryTemplate structure (if available)

**Option 2: Manual Input**
- Module name (e.g., `MyNewModule`)
- Module description
- GitHub owner/organization (default: `Nomoos`)

The script then:
1. Creates the module directory structure (with nested paths if needed)
2. Copies files from RepositoryTemplate (if available) or creates basic structure
3. Generates configuration files (`module.json`, `README.md`, `pyproject.toml`)
4. Initializes a Git repository in the module directory
5. Sets up the remote URL for the module
6. Creates an initial commit in the module
7. Adds the remote to the parent repository
8. Adds and commits the module to the parent repository

### Examples

**Example 1: Using GitHub URL for simple module**
```batch
scripts\add-module.bat
# Select option: 1
# GitHub URL: https://github.com/Nomoos/PrismQ.MyNewModule.git
# Description: My new module for PrismQ
```
Result: 
- Creates `src/MyNewModule/` with complete template structure
- Adds remote to parent repository
- Commits module to parent repository automatically

**Example 2: Using GitHub URL for nested module**
```batch
scripts\add-module.bat
# Select option: 1
# GitHub URL: Nomoos/PrismQ.IdeaInspiration.Classification
# Description: Classify idea inspirations
```
Result: 
- Creates `src/IdeaInspiration/src/Classification/` with complete template structure
- Adds remote to parent repository
- Commits module to parent repository automatically

**Example 3: Using manual input**
```batch
scripts\add-module.bat
# Select option: 2
# Module name: MyModule
# Description: A new PrismQ module
# GitHub owner: MyOrg
```
Result: 
- Creates `src/MyModule/` with complete template structure
- Adds remote to parent repository
- Commits module to parent repository automatically

## Module Synchronization Script

This script automates the synchronization of first-level modules from their separate repositories into the main PrismQ repository using Git subtree.

### Available Script

- **`sync-modules.bat`** - Windows synchronization script

### Quick Start

```batch
# Sync all modules
scripts\sync-modules.bat

# Sync specific module
scripts\sync-modules.bat src\RepositoryTemplate

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

**In `sync-modules.bat`:**

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

```batch
scripts\sync-modules.bat
```

### Sync Single Module

When you only want to update one specific module:

```batch
scripts\sync-modules.bat src\RepositoryTemplate
```

### List Configured Modules

See which modules are configured for synchronization:

```batch
scripts\sync-modules.bat --list
```

## Integration into Module Template

To use this sync approach in your module development workflow:

### 1. Create Separate Module Repository

Create a new repository for your module using the RepositoryTemplate structure:

```batch
REM Example: Creating PrismQ.NewModule repository
git clone https://github.com/Nomoos/PrismQ.RepositoryTemplate.git PrismQ.NewModule
cd PrismQ.NewModule

REM Update module-specific content
REM ... make your changes ...

REM Push to your module repository
git remote set-url origin https://github.com/Nomoos/PrismQ.NewModule.git
git push -u origin main
```

### 2. Add Module to Sync Configuration

Update the sync scripts in the main PrismQ repository to include your new module.

### 3. Run Initial Sync

First sync will pull the module into the main repository:

```batch
scripts\sync-modules.bat src\NewModule
```

### 4. Development Workflow

#### Option A: Develop in Module Repository

1. Work in the separate module repository
2. Commit and push changes to module repo
3. Sync to main PrismQ repo using sync script

```batch
REM In module repository
cd PrismQ.NewModule
REM ... make changes ...
git commit -am "Update feature"
git push

REM In main PrismQ repository
cd PrismQ
scripts\sync-modules.bat src\NewModule
```

#### Option B: Develop in Main Repository

1. Work in the main PrismQ repository
2. Commit changes
3. Push to module repository using subtree push

```batch
REM In main PrismQ repository
cd PrismQ
REM ... make changes to src\NewModule ...
git commit -am "Update module"

REM Push changes to module repository
git subtree push --prefix=src/NewModule newmodule-remote main
```

## Troubleshooting

### Remote Already Exists

If you see "Remote already exists", the script will use the existing remote. To update the URL:

```batch
git remote set-url remote-name new-url
```

### Fetch Fails / Repository Not Found

This usually means:
1. The module repository doesn't exist yet (create it first)
2. Incorrect repository URL (check configuration)
3. No access permissions (verify GitHub access)

### Merge Conflicts

If sync encounters conflicts:

```batch
REM Resolve conflicts manually
git status  REM See conflicted files
REM Edit files to resolve conflicts
git add .
git commit -m "Resolve sync conflicts"
```

### First Sync Fails

When syncing a module for the first time with existing content:

```batch
REM Use --allow-unrelated-histories
git subtree add --prefix=src/Module remote-name main --squash
```

## Advanced Usage

### Push Changes Back to Module Repository

After making changes in the main repository:

```batch
git subtree push --prefix=src/RepositoryTemplate repositorytemplate-remote main

REM This updates the module repository with changes made in main repo
```

### Fetch Without Merging

To see what changes are available without merging:

```batch
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
