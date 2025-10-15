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

- **[RepositoryTemplate](src/RepositoryTemplate/README.md)** - Template module structure
- **[IdeaInspiration](src/IdeaInspiration/README.md)** - Idea generation and inspiration

See [docs/repository-tree.html](docs/repository-tree.html) for the complete module hierarchy.

## 🔧 Scripts

See [scripts/README.md](scripts/README.md) for detailed script documentation.

## 📖 Additional Resources

- [RepositoryTemplate Documentation](https://github.com/Nomoos/PrismQ.RepositoryTemplate)
- [Contribution Guidelines](docs/CONTRIBUTING.md) (coming soon)
