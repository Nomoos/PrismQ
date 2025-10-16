# PrismQ Scripts

Utility scripts for managing the PrismQ modular repository.

## 📦 Available Scripts

### Module Creation

Create new modules with proper structure and GitHub integration.

- **[add_module/](add_module/)** - Module creation implementation
- **`add-module.bat`** - Windows wrapper script

**Quick Start:**
```bash
# Windows
scripts\add-module.bat PrismQ.MyModule

# Cross-platform
python -m scripts.add_module.add_module PrismQ.MyModule
```

See [add_module/README.md](add_module/README.md) for detailed documentation.

### Module Synchronization

Sync modules between local repository and remote GitHub repositories using git subtree.

- **[sync_modules/](sync_modules/)** - Synchronization implementation
- **`sync-modules.bat`** - Windows wrapper script

**Quick Start:**
```bash
# Windows - Sync all modules
scripts\sync-modules.bat

# Cross-platform
python scripts/sync_modules.py

# Sync recursively (including nested modules)
scripts\sync-modules.bat --recursive
```

See [sync_modules/README.md](sync_modules/README.md) for detailed documentation.

## 🧪 Testing

Test the batch scripts to verify proper configuration:

```bash
cd scripts
python3 -m pytest test_bat_scripts.py -v
```

## 📚 Documentation

### Module Creation

- [add_module/README.md](add_module/README.md) - Complete guide
- [add_module/ARCHITECTURE.md](add_module/ARCHITECTURE.md) - Implementation details
- [add_module/URL_PARSING_FEATURE.md](add_module/URL_PARSING_FEATURE.md) - URL input formats

### Module Synchronization

- [sync_modules/README.md](sync_modules/README.md) - Complete guide
- Git subtree workflow and best practices

## 🔧 Prerequisites

- Python 3.11 or higher
- Git
- GitHub CLI (`gh`) authenticated (for module creation)

**GitHub CLI Setup:**
```bash
gh auth login
```

## 💡 Common Tasks

```bash
# Create a new module
scripts\add-module.bat PrismQ.MyModule

# Sync all modules
scripts\sync-modules.bat

# List configured modules
scripts\sync-modules.bat --list

# Sync specific module
scripts\sync-modules.bat src\RepositoryTemplate

# Test scripts
cd scripts && python3 -m pytest test_bat_scripts.py -v
```

## 📖 Additional Resources

- [Main README](../README.md) - Project overview
- [docs/MODULE_MANAGEMENT.md](../docs/MODULE_MANAGEMENT.md) - Module management guide
- [Repository Tree View](../docs/repository-tree.html) - Interactive module visualization
