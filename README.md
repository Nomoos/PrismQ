# PrismQ

A modular AI-powered content generation ecosystem. Each subfolder follows the [RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate) structure.

📖 **[Usage Guide](USAGE_GUIDE.md)** - Quick start guide for batch scripts and repository tree view

## Repository Structure

PrismQ uses a nested modular architecture where each module follows the RepositoryTemplate pattern with the following structure:

```
ModuleName/
├── docs/              # Module documentation
├── issues/            # Module-specific issue tracking
│   ├── new/          # New issues
│   ├── wip/          # Work in progress
│   └── done/         # Completed issues
├── scripts/          # Module utility scripts
├── src/              # Module source code (can contain nested modules)
└── tests/            # Module tests
```

### Modules

- **RepositoryTemplate** - Template module structure
- **IdeaInspiration** - Idea generation and inspiration
  - **Sources** - Various content sources
    - **Content** - Content processing
      - **Shorts** - Short-form content handling
        - **YouTubeShortsSource** - YouTube Shorts source (PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource)

Each module has single responsibility and maintains its own documentation, issues, scripts, source code, and tests.

## Module Naming Convention

Nested modules follow a dot notation based on their path:
- `src/RepositoryTemplate` → `PrismQ.RepositoryTemplate`
- `src/IdeaInspiration/src/Sources` → `PrismQ.IdeaInspiration.Sources`
- `src/IdeaInspiration/src/Sources/src/Content/src/Shorts/src/YouTubeShortsSource` → `PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource`

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

### Quick Start

```bash
# Windows - Sync all modules
scripts\sync-modules.bat

# Cross-platform - Direct Python usage
python scripts/sync_modules.py
```

For detailed usage, configuration, and integration guide, see [scripts/README.md](scripts/README.md).

## Repository Module Tree View

An interactive HTML-based module tree view is available to explore the complete module hierarchy:

📄 [**View Module Tree**](docs/repository-tree.html)

Features:
- 🌳 Collapsible module navigation using PrismQ naming convention
- 🔍 Search functionality for modules
- 📊 Module statistics (7 modules, depth 5)
- 🎨 Dark theme with VS Code-inspired design

See [docs/README.md](docs/README.md) for more information.
