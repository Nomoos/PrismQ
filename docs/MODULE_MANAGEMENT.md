# Module Management

This guide covers creating new modules and synchronizing them with remote repositories.

## Module Synchronization

First-level modules can be developed in separate repositories and synchronized to the main PrismQ repository using automated sync scripts with **git subtree**.

### Configuration

Each first-level module should have a `module.json` file specifying its remote repository:

```json
{
  "remote": {
    "url": "https://github.com/Nomoos/PrismQ.ModuleName.git"
  }
}
```

The sync scripts automatically discover modules with `module.json` files.

### Syncing Modules

```bash
# Windows - Sync all modules
scripts\sync-modules.bat

# Cross-platform - Direct Python usage
python scripts/sync_modules.py

# Sync recursively (including nested modules)
scripts\sync-modules.bat --recursive
python scripts/sync_modules.py --recursive
```

### Creating New Modules

```bash
# Windows
scripts\add-module.bat

# Cross-platform
python -m scripts.add_module.add_module

# With module name or URL
scripts\add-module.bat PrismQ.MyModule
scripts\add-module.bat https://github.com/Nomoos/PrismQ.MyModule
```

## Detailed Documentation

For comprehensive documentation on module creation and synchronization, see:

- [scripts/README.md](../scripts/README.md) - Complete script documentation
- [scripts/add_module/README.md](../scripts/add_module/README.md) - Module creation details
- [scripts/sync_modules/README.md](../scripts/sync_modules/README.md) - Synchronization details

## Benefits of Git Subtree

- ✅ Full code in main repository (no external dependencies)
- ✅ Bidirectional sync (pull from and push to module repos)
- ✅ Preserves history
- ✅ No `.gitmodules` file needed
- ✅ Works with standard Git commands

## Development Workflow

### Option A: Develop in Module Repository

1. Work in the separate module repository
2. Commit and push changes to module repo
3. Sync to main PrismQ repo using sync script

### Option B: Develop in Main Repository

1. Work in the main PrismQ repository
2. Commit changes
3. Push to module repository using subtree push

```bash
git subtree push --prefix=mod/ModuleName modulename-remote main
```
