# Documentation

This directory contains additional documentation and tools for the PrismQ repository.

## Files

### Repository Module Tree View

- **`repository-tree.html`** - Interactive HTML page with collapsible module tree view
- **`repository-tree-data.json`** - JSON data representing the module hierarchy
- **`generate_tree.py`** - Python script to generate the module tree

### Using the Repository Module Tree View

The repository module tree view provides an interactive visualization of the PrismQ module hierarchy using the PrismQ naming convention (e.g., PrismQ.IdeaInspiration.Sources):

- **Collapsible modules** - Click on modules to expand/collapse their sub-modules
- **Search functionality** - Search for modules by name
- **Statistics** - View total modules and maximum depth
- **Dark theme** - VS Code-inspired dark theme for comfortable viewing
- **Expand All / Collapse All** - Quick navigation buttons

#### Opening the Tree View

Simply open `repository-tree.html` in any modern web browser. The tree data is embedded in the HTML file, so no server is required.

#### Regenerating the Tree View

If the repository structure changes, regenerate the tree view:

```bash
cd docs
python3 generate_tree.py
```

This will:
1. Scan the repository structure for modules (based on `src/` directories)
2. Generate `repository-tree-data.json` with the module hierarchy
3. Generate `repository-tree.html` with embedded data
4. Display module statistics

#### Features Demonstrated

1. **Collapsible Modules** - Click any module to expand/collapse its sub-modules
2. **Search** - Type in the search box to filter and highlight matching modules
3. **Visual Indicators** - Module icons change when opened, search results are highlighted
4. **Statistics** - View total module count and hierarchy depth at the bottom

## Screenshots

- Module tree with collapsed view
- Expanded module hierarchy showing all PrismQ modules
- Search functionality highlighting matching modules

## Purpose

The module tree view provides:
- Easy navigation of the modular repository structure
- Quick location of specific modules
- Visual understanding of the module hierarchy using PrismQ naming convention (PrismQ.Module.SubModule)
- Documentation of the repository organization
