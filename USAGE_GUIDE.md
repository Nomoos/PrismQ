# PrismQ Usage Guide

Quick start guide for common tasks in the PrismQ repository.

## 📦 Module Management

### View Module Tree

Open the interactive module tree visualization:

```bash
# Windows
start docs\repository-tree.html

# macOS / Linux
open docs/repository-tree.html
```

See [docs/MODULE_TREE.md](docs/MODULE_TREE.md) for detailed usage.

### Create New Module

```bash
# Windows
scripts\add-module.bat

# Cross-platform
python -m scripts.add_module.add_module

# With module name
scripts\add-module.bat PrismQ.MyModule
```

See [scripts/README.md](scripts/README.md) for detailed options.

### Sync Modules

```bash
# Windows - Sync all modules
scripts\sync-modules.bat

# Cross-platform
python scripts/sync_modules.py

# Sync recursively (including nested modules)
scripts\sync-modules.bat --recursive
```

### Repository Builder & Checker

Validate GitHub CLI and derive module hierarchy:

```bash
# Windows - Setup environment (first time only)
scripts\repo-builder\setup_env.bat

# Run with module name
scripts\repo-builder\run.bat PrismQ.IdeaInspiration

# Run with GitHub URL
scripts\repo-builder\run.bat https://github.com/Nomoos/PrismQ.IdeaInspiration

# Cross-platform
cd scripts/repo-builder
python repo_builder.py <module_name_or_url>
```

See [scripts/repo-builder/README.md](scripts/repo-builder/README.md) for detailed documentation.

## 🧪 Testing

### Test Batch Scripts

```bash
cd scripts
python3 -m pytest test_bat_scripts.py -v
```

**Expected Results:**
- ✅ 12 core functionality tests should pass
- ⚠️ 2 tests may fail if dependencies not installed (normal on first run)

## 🔄 Common Workflows

### Regenerate Module Tree

After adding or removing modules:

```bash
cd docs
python3 generate_tree.py
```

### List Configured Modules

```bash
scripts\sync-modules.bat --list
```

### Sync Specific Module

```bash
scripts\sync-modules.bat src\RepositoryTemplate
```

## 📚 Additional Documentation

- [README.md](README.md) - Project overview
- [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md) - Architecture details
- [docs/MODULE_MANAGEMENT.md](docs/MODULE_MANAGEMENT.md) - Module creation and sync
- [scripts/README.md](scripts/README.md) - Comprehensive script documentation
