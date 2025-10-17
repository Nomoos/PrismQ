# Add Repository with Submodule

A Python CLI tool that creates GitHub repositories and automatically registers them as git submodules. This tool extends the functionality of `repo-builder` by adding submodule registration after repository creation.

## Features

- **Repository Creation**: Uses repo-builder to create/clone GitHub repositories
- **Submodule Registration**: Automatically adds repositories as git submodules
- **Chain Processing**: Handles entire module hierarchy from root to deepest
- **Auto-Commit**: Commits .gitmodules changes to parent repositories
- **Auto-Push**: Automatically pushes changes to remote repository
- **Same Interface**: Compatible with repo-builder input format

## What It Does

1. Creates GitHub repositories (via repo-builder)
2. Clones repositories locally (via repo-builder)
3. **Registers each repository as a git submodule in its parent** ⭐
4. **Commits changes to parent .gitmodules** ⭐
5. **Pushes changes to remote repository** ⭐
6. Provides next steps for the user

## Prerequisites

- Python 3.8 or higher
- GitHub CLI (`gh`) installed and authenticated
- Git installed
- repo-builder in parent directory (scripts/repo-builder)

## Installation

No installation required. The script is part of the PrismQ repository.

## Usage

### Command Line

```bash
# Navigate to the scripts directory
cd scripts/add-repo-with-submodule

# Run with module name
python -m add_repo_with_submodule PrismQ.IdeaInspiration.NewModule

# Run with GitHub URL
python -m add_repo_with_submodule https://github.com/Nomoos/PrismQ.NewModule

# Interactive mode (prompts for input)
python -m add_repo_with_submodule
```

### Running from Repository Root

```bash
# From PrismQ root directory
python -m scripts.add-repo-with-submodule PrismQ.IdeaInspiration.NewModule
```

## Examples

### Example 1: Simple Two-Level Module

```bash
python -m add_repo_with_submodule PrismQ.MyModule
```

**What happens:**
1. Creates/clones `PrismQ` (if needed)
2. Creates/clones `PrismQ.MyModule`
3. Adds `PrismQ.MyModule` as submodule in `PrismQ/mod/MyModule`
4. Commits to `PrismQ` repository

### Example 2: Nested Three-Level Module

```bash
python -m add_repo_with_submodule PrismQ.IdeaInspiration.Sources
```

**What happens:**
1. Creates/clones `PrismQ`
2. Creates/clones `PrismQ.IdeaInspiration` → submodule in `PrismQ`
3. Creates/clones `PrismQ.IdeaInspiration.Sources` → submodule in `PrismQ.IdeaInspiration`
4. Commits changes to both `PrismQ` and `PrismQ.IdeaInspiration`

### Example 3: Deep Nesting

```bash
python -m add_repo_with_submodule PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource
```

**Creates hierarchy:**
```
PrismQ/                                                      (root repo)
└── mod/Idea/                                                [submodule]
    └── mod/Sources/                                         [submodule]
        └── mod/Content/                                     [submodule]
            └── mod/Shorts/                                  [submodule]
                └── mod/YouTubeShortsSource/                 [submodule]
```

## Output Example

```
🚀 Add Repository with Submodule
==================================================
🔍 Validating GitHub CLI authentication...
✅ GitHub CLI is authenticated

📂 Working directory: /home/runner/work/PrismQ/PrismQ

🔍 Processing input: PrismQ.IdeaInspiration.NewModule

📦 Creating/cloning repositories...
Repository PrismQ already exists.
Repository PrismQ already cloned locally.
Repository PrismQ.IdeaInspiration already exists.
Repository PrismQ.IdeaInspiration already cloned locally.
Creating repository PrismQ.IdeaInspiration.NewModule from template...
Repository PrismQ.IdeaInspiration.NewModule created successfully.

📦 Registering repositories as submodules...
==================================================

🔗 Adding PrismQ.IdeaInspiration as submodule in PrismQ...
   URL: https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   Path: mod/IdeaInspiration
   ✅ Added as submodule
   ✅ Committed to parent
   ✅ Pushed to remote

🔗 Adding PrismQ.IdeaInspiration.NewModule as submodule in PrismQ.IdeaInspiration...
   URL: https://github.com/Nomoos/PrismQ.IdeaInspiration.NewModule.git
   Path: mod/NewModule
   ✅ Added as submodule
   ✅ Committed to parent
   ✅ Pushed to remote

==================================================
✅ All operations complete!

💡 Next steps:
   • Review changes with: git status
   • Changes have been pushed to remote
   • Initialize submodules in other clones with:
     git submodule update --init --recursive
```

## Comparison with repo-builder

| Feature | repo-builder | add-repo-with-submodule |
|---------|-------------|------------------------|
| Creates GitHub repos | ✅ Yes | ✅ Yes (via repo-builder) |
| Clones locally | ✅ Yes | ✅ Yes (via repo-builder) |
| Registers as submodules | ❌ No | ✅ Yes |
| Updates .gitmodules | ❌ No | ✅ Yes |
| Commits to parent | ❌ No | ✅ Yes |
| Pushes to remote | ❌ No | ✅ Yes |
| Parent tracks child | ❌ No | ✅ Yes |

## How It Works

### 1. Import repo-builder Functions
```python
from parsing import derive_module_chain
from repository import create_git_chain, get_repository_path
```

### 2. Create Repositories (via repo-builder)
```python
chain = derive_module_chain(module_input)
create_git_chain(chain, workspace)
```

### 3. Add as Submodules (new functionality)
```python
for module in chain[1:]:  # Skip PrismQ root
    parent = get_parent_module(module)
    add_git_submodule(parent_path, repo_url, relative_path)
    commit_submodule_changes(parent_path, module)
    push_submodule_changes(parent_path)
```

## Architecture

```
add-repo-with-submodule/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point for python -m
├── add_repo_submodule.py    # Main logic
├── submodule_operations.py  # Git submodule operations
├── cli.py                   # CLI interface
├── exceptions.py            # Custom exceptions
├── requirements.txt         # Dependencies (none)
└── README.md                # This file
```

## Error Handling

The tool provides clear error messages:

- **Parent not found**: If parent repository doesn't exist
- **Submodule already exists**: If submodule is already registered
- **Git command fails**: If git submodule add or commit fails
- **GitHub CLI errors**: If gh commands fail

Example:
```
❌ Error: Parent repository not found or not a git repo: /path/to/parent
```

## Configuration

Default configuration:
- **Branch tracking**: `main`
- **Auto-commit**: Yes (commits to parent after adding submodule)
- **Auto-push**: Yes (automatically pushes changes to remote)

## Limitations

- Automatically pushes changes to remote (commits are immediately visible)
- Does not auto-initialize submodules (user must run `git submodule update --init`)
- Requires parent repository to exist as git repo
- No rollback capability (Option 3 feature)

## Future Enhancements

See feature issues in `issues/new/`:
- **Option 2**: Smart Submodule Manager with auto-initialization
- **Option 3**: Full Integration with backup/rollback support

## Development

### Project Structure
- **add_repo_submodule.py**: Main workflow logic
- **submodule_operations.py**: Git submodule commands
- **cli.py**: Command-line interface
- **exceptions.py**: Custom exception classes

### Adding Features
To add new features:
1. Add functions to appropriate module
2. Update main workflow in add_repo_submodule.py
3. Update README with new functionality
4. Add tests

## Troubleshooting

### "Parent repository not found"
**Solution**: Ensure parent repository exists and is a git repo

### "Submodule already exists"
**Solution**: Check .gitmodules in parent, remove existing entry if needed

### "Git not installed"
**Solution**: Install git and ensure it's in PATH

### "GitHub CLI not authenticated"
**Solution**: Run `gh auth login`

## Related Documentation

- `HOW_REPO_BUILDER_WORKS.md` - Detailed repo-builder documentation
- `SUBMODULE_SUPPORT_ANALYSIS.md` - Full analysis of submodule support
- `SUBMODULE_WORKFLOW_DIAGRAM.md` - Visual workflow diagrams
- `QUICK_DECISION_GUIDE.md` - Implementation options guide

## License

Same as PrismQ repository license.
