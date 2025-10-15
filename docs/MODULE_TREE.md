# Module Tree View

Interactive visualization of the PrismQ module hierarchy.

## Features

- **Collapsible modules** - Click to expand/collapse sub-modules
- **Search functionality** - Find modules by name
- **Statistics** - View total modules and maximum depth
- **Dark theme** - VS Code-inspired design
- **Expand All / Collapse All** - Quick navigation buttons

## Usage

### Opening the Tree View

Simply open `repository-tree.html` in any modern web browser:

```bash
# Windows
start docs\repository-tree.html

# macOS
open docs/repository-tree.html

# Linux
xdg-open docs/repository-tree.html
```

The tree data is embedded in the HTML file, so no server is required.

### Navigation

1. **Expand/Collapse** - Click any module name to toggle its children
2. **Search** - Type in the search box to filter modules
   - Matching modules are highlighted
   - Parent modules auto-expand to show matches
3. **Expand All** - Click button to expand entire tree
4. **Collapse All** - Click button to collapse entire tree

### Search Examples

- Search for `IdeaInspiration` to find all related modules
- Search for `Sources` to find source-related modules
- Search for `Content` to find content processing modules
- Search for `Shorts` to find short-form content modules

## Regenerating the Tree

If the repository structure changes, regenerate the tree view:

```bash
cd docs
python3 generate_tree.py
```

This will:
1. Scan the repository for modules (based on `src/` directories)
2. Generate `repository-tree-data.json` with the hierarchy
3. Generate `repository-tree.html` with embedded data
4. Display module statistics

## Module Naming Convention

The tree uses PrismQ's dot notation:
- `PrismQ.IdeaInspiration`
- `PrismQ.IdeaInspiration.Sources`
- `PrismQ.IdeaInspiration.Sources.Content`
- `PrismQ.IdeaInspiration.Sources.Content.Shorts`

Each level represents a nested `src/` directory in the repository structure.
