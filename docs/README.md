# Documentation

This directory contains additional documentation and tools for the PrismQ repository.

## Files

### Repository Tree View

- **`repository-tree.html`** - Interactive HTML page with collapsible repository tree view
- **`repository-tree-data.json`** - JSON data representing the repository structure
- **`generate_tree.py`** - Python script to generate the tree view

### Using the Repository Tree View

The repository tree view provides an interactive visualization of the PrismQ repository structure with the following features:

- **Collapsible folders** - Click on folders to expand/collapse their contents
- **Search functionality** - Search for files and folders by name or path
- **Statistics** - View total folders, files, and maximum depth
- **Dark theme** - VS Code-inspired dark theme for comfortable viewing
- **Keyboard shortcuts** - Expand All / Collapse All buttons for quick navigation

#### Opening the Tree View

Simply open `repository-tree.html` in any modern web browser. The tree data is embedded in the HTML file, so no server is required.

#### Regenerating the Tree View

If the repository structure changes, regenerate the tree view:

```bash
cd docs
python3 generate_tree.py
```

This will:
1. Scan the repository structure
2. Generate `repository-tree-data.json`
3. Generate `repository-tree.html` with embedded data
4. Display statistics about the repository

#### Features Demonstrated

1. **Collapsible Branches** - Click any folder to expand/collapse its children
2. **Search** - Type in the search box to filter and highlight matching files/folders
3. **Visual Indicators** - Folder icons change when opened, search results are highlighted
4. **Statistics** - View total counts at the bottom of the page

## Screenshots

- Initial view with collapsed folders
- Expanded scripts folder showing .bat files and Python modules
- Search functionality highlighting matching items

## Purpose

The tree view provides:
- Easy navigation of the modular repository structure
- Quick location of files and folders
- Visual understanding of the repository hierarchy
- Documentation of the repository organization
