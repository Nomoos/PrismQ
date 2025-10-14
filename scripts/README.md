# PrismQ Scripts

Utility scripts for managing the PrismQ modular repository on Windows.

## Module Creation Script

This script helps you create new PrismQ modules with the proper structure and configuration.

### Available Scripts

- **`add-module.bat`** - Windows wrapper script (sets up Python environment and runs add_module.py)
- **`add_module.py`** - Python implementation with GitHub API integration
- **`setup_env.bat`** - Virtual environment setup script

### Python Implementation

The module creation script is now implemented in Python for better:
- **Testability** - Can be tested with pytest
- **Cross-platform compatibility** - Works on Windows, Linux, and macOS
- **GitHub integration** - Uses PyGithub for robust API access
- **Maintainability** - Easier to debug and extend
- **Error handling** - Better validation and error messages

### Prerequisites

- Python 3.11 or higher
- Git
- GitHub CLI (`gh`) authenticated (run `gh auth login`)

### Quick Start

```batch
# Run the interactive script (Windows)
scripts\add-module.bat

# Or run Python script directly (any platform)
python scripts/add_module.py

# With command-line options
python scripts/add_module.py --github-url "Nomoos/PrismQ.MyModule" --description "My module"
```

The first time you run `add-module.bat`, it will automatically:
1. Create a Python virtual environment in `scripts/.venv/`
2. Install required dependencies (PyGithub, GitPython, click)
3. Run the Python script

The virtual environment is reused for subsequent runs.

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
7. **Creates GitHub repositories for all hierarchy levels** (using GitHub CLI)
8. Pushes the module to its GitHub repository
9. Adds remotes to the parent repository for all hierarchy levels
10. Adds and commits the module to the parent repository

### Examples

**Example 1: Interactive mode (Windows)**
```batch
scripts\add-module.bat
# Select option: 1
# GitHub URL: https://github.com/Nomoos/PrismQ.MyNewModule.git
# Description: My new module for PrismQ
```

**Example 2: Command-line mode (any platform)**
```bash
# Using GitHub URL
python scripts/add_module.py --github-url "Nomoos/PrismQ.MyModule" --description "My module"

# Using module name
python scripts/add_module.py --module-name "MyModule" --description "My module" --owner "Nomoos"
```

**Example 3: Nested module**
```batch
scripts\add-module.bat
# Select option: 1
# GitHub URL: Nomoos/PrismQ.IdeaInspiration.Classification
# Description: Classify idea inspirations
```
Result: 
- Creates `src/IdeaInspiration/src/Classification/` with complete template structure
- **Creates GitHub repositories**: PrismQ.IdeaInspiration, PrismQ.IdeaInspiration.Classification
- Adds remotes to parent repository
- Pushes module to GitHub
- Commits module to parent repository automatically

### Hierarchical Module Creation

The script supports creating deeply nested modules and automatically creates all parent repositories:

**Example: Deep nesting**
```batch
scripts\add-module.bat
# Select option: 1
# GitHub URL: Nomoos/PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource
```

This will:
1. Check and create repositories for each level:
   - `PrismQ.IdeaInspiration`
   - `PrismQ.IdeaInspiration.Sources`
   - `PrismQ.IdeaInspiration.Sources.Content`
   - `PrismQ.IdeaInspiration.Sources.Content.Shorts`
   - `PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource`
2. Create module at: `src/IdeaInspiration/src/Sources/src/Content/src/Shorts/src/YouTubeSource/`
3. Push the module to its GitHub repository
4. Add all remotes to the main PrismQ repository
5. Set up git subtree relationships

**Requirements:**
- GitHub CLI (`gh`) must be installed and authenticated
- Run `gh auth login` if repositories cannot be created

## Module Synchronization Script

This script automates the synchronization of first-level modules from their separate repositories into the main PrismQ repository using Git subtree.

### Available Scripts

- **`sync-modules.bat`** - Windows wrapper script (sets up Python environment and runs sync_modules.py)
- **`sync_modules.py`** - Python implementation with improved error handling

### Python Implementation

The module sync script is now implemented in Python for better:
- **Error handling** - Clear error messages and validation
- **Testability** - Can be tested with pytest
- **Cross-platform compatibility** - Works on Windows, Linux, and macOS
- **Maintainability** - Easier to debug and extend
- **Module discovery** - Automatically discovers modules from module.json files

### Quick Start

```batch
# Windows - Sync all first-level modules
scripts\sync-modules.bat

# Windows - Recursively sync all modules (including nested)
scripts\sync-modules.bat --recursive

# Sync specific module
scripts\sync-modules.bat src\RepositoryTemplate

# List configured modules
scripts\sync-modules.bat --list

# Cross-platform - Direct Python usage
python scripts/sync_modules.py
python scripts/sync_modules.py --recursive
python scripts/sync_modules.py --list
python scripts/sync_modules.py src/RepositoryTemplate
```

**Key Features:**
- **Recursive sync**: Use `--recursive` flag to discover and sync all nested modules automatically
- **Works from anywhere**: Can be run from the main repo or from within any submodule
- **Automatic discovery**: Finds all modules with `module.json` files

The first time you run `sync-modules.bat`, it will automatically set up the Python virtual environment and install dependencies (same environment as add-module.bat).

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

## Module Structure and Git Directories

### Why Modules Have `.git` and `.github` Directories

Each module in the PrismQ repository has its own `.git` and `.github` directories. This is **intentional and not duplication**:

**`.git` Directories:**
- Modules are **separate git repositories** that can be independently developed
- The `.git` directory allows modules to have their own git history
- Git subtree is used to sync between the module repo and the main PrismQ repo
- The parent repository's git automatically ignores nested `.git` directories (they're not tracked)
- This enables a **bidirectional workflow**: develop in either the module repo or main repo
- When you see `.git` in a module directory, it's there to support independent module development

**Important:** The `.git` directories in modules are NOT part of the parent repository's git history. They exist in your working tree but are automatically ignored by git. This is standard behavior for nested git repositories and git subtree workflows.

**`.github` Directories:**
- Contains module-specific GitHub configuration (issue templates, PR templates, etc.)
- Allows each module to have its own GitHub Actions workflows (if needed)
- Provides module-specific Copilot instructions
- Not duplicative since these are module-specific configurations
- These ARE tracked in git (unlike `.git` directories)

This architecture provides:
- ✅ **Module independence**: Each module can be developed, tested, and versioned separately
- ✅ **Flexible workflows**: Work in module repo OR main repo
- ✅ **Easy synchronization**: Git subtree handles syncing automatically
- ✅ **No external dependencies**: Full code available in main repo

### Verifying the Setup

You can verify that `.git` directories are properly ignored:
```bash
# Check git status - .git directories should not appear
git status

# Check what's tracked in modules
git ls-files src/
# You'll see .github files are tracked, but no .git files
```

## Configuration

Modules are configured using `module.json` files in each module directory:

### Module Configuration with module.json

Each module should have a `module.json` file in its root directory:

**Create `src/YourModule/module.json`:**

```json
{
  "remote": {
    "url": "https://github.com/Nomoos/PrismQ.YourModule.git"
  }
}
```

The sync script will automatically:
1. Discover all modules with `module.json` files
2. Extract the remote URL
3. Derive the remote name from the URL (e.g., `prismq-yourmodule`)
4. Set up git remotes and sync using git subtree

### Hardcoded Fallback

The sync script also includes hardcoded configurations for core modules:
- `src/RepositoryTemplate` - Template module structure
- `src/IdeaInspiration` - Idea generation module

These will be used if `module.json` files are not found.

### Migration from REMOTE.md

If you have old `REMOTE.md` files, migrate to `module.json`:

**Old format (REMOTE.md):**
```
REMOTE_URL=https://github.com/Nomoos/PrismQ.YourModule.git
REMOTE_NAME=yourmodule-remote
BRANCH=main
```

**New format (module.json):**
```json
{
  "remote": {
    "url": "https://github.com/Nomoos/PrismQ.YourModule.git"
  }
}
```

The remote name and branch are automatically derived.

## Usage Examples

### Sync All First-Level Modules

Sync all configured first-level modules from the main repository:

```batch
scripts\sync-modules.bat
```

### Recursively Sync All Modules

Discover and sync all modules including nested ones:

```batch
# From main repository
scripts\sync-modules.bat --recursive

# Or direct Python
python scripts/sync_modules.py --recursive
```

This will:
1. Recursively scan for all `module.json` files
2. Discover nested modules at any depth (e.g., `src/IdeaInspiration/src/Sources/src/Content`)
3. Sync each module from its configured remote repository

### Sync from Within a Submodule

The script works from any location in the repository hierarchy:

```batch
# Navigate to a submodule
cd src\IdeaInspiration

# Run sync from the submodule (paths are relative to git root)
..\..\scripts\sync-modules.bat

# Or sync recursively from submodule
..\..\scripts\sync-modules.bat --recursive
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

# With recursive discovery
scripts\sync-modules.bat --list --recursive
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
