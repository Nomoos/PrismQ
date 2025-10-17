# PrismQ

A modular AI-powered content generation ecosystem. Each module follows the [RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate) structure.

## 📚 Documentation

- **[Usage Guide](USAGE_GUIDE.md)** - Quick start for scripts and tools
- **[Repository Structure](docs/REPOSITORY_STRUCTURE.md)** - Module architecture and organization
- **[Module Management](docs/MODULE_MANAGEMENT.md)** - Creating and syncing modules
- **[Module Tree View](docs/repository-tree.html)** - Interactive visualization 🌳

## 🛠️ Quick Start

```bash
# Create a new module
scripts\add-module.bat                    # Windows
python -m scripts.add_module.add_module   # Cross-platform

# Sync modules from remote repositories
scripts\sync-modules.bat                  # Windows
python scripts/sync_modules.py            # Cross-platform

# View interactive module tree
# Open docs/repository-tree.html in browser
```

## 📦 Modules

- **[RepositoryTemplate](mod/RepositoryTemplate/README.md)** - Template module structure
- **[IdeaInspiration](mod/IdeaInspiration/README.md)** - Idea generation and inspiration

See [docs/repository-tree.html](docs/repository-tree.html) for the complete module hierarchy.

## 🔧 Scripts

### Available Scripts

- **submodule-converter.bat** - Convert nested repositories to git submodules
  - See [scripts/submodule-converter/README.md](scripts/submodule-converter/README.md) for details
  - Preserves mod/ directory structure for nested modules
  - Example: `scripts\submodule-converter.bat` (Windows) or use the Python module directly

- **add-repo.bat** - Repository builder with submodule support
  - Wrapper for the add-repo-with-submodule tool
  - See [scripts/add-repo-with-submodule/README.md](scripts/add-repo-with-submodule/README.md) for details
  - Example: `scripts\add-repo.bat PrismQ.ModuleName`

For detailed documentation on each script, see the respective README files in the scripts directory.

## 📖 Additional Resources

- [RepositoryTemplate Documentation](https://github.com/Nomoos/PrismQ.RepositoryTemplate)
