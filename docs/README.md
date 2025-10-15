# Documentation

Documentation and tools for the PrismQ repository.

## 📚 Documentation Files

- **[REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md)** - Module architecture and naming conventions
- **[MODULE_MANAGEMENT.md](MODULE_MANAGEMENT.md)** - Creating and syncing modules
- **[MODULE_TREE.md](MODULE_TREE.md)** - Interactive module tree view guide

## 🛠️ Tools

- **[repository-tree.html](repository-tree.html)** - Interactive module tree visualization
- **[generate_tree.py](generate_tree.py)** - Script to regenerate the tree view

## 🌳 Module Tree View

The interactive module tree provides:
- Collapsible module navigation
- Search functionality
- Module statistics
- Dark theme design

**Quick Start:**
1. Open `repository-tree.html` in any browser
2. Click modules to expand/collapse
3. Use search to find specific modules

To regenerate after structure changes:
```bash
cd docs
python3 generate_tree.py
```

See [MODULE_TREE.md](MODULE_TREE.md) for detailed usage.
