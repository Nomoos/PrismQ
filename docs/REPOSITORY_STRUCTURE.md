# Repository Structure

PrismQ uses a nested modular architecture where each module follows the RepositoryTemplate pattern.

## Module Structure

Each module follows this standard structure:

```
ModuleName/
├── docs/              # Module documentation
├── issues/            # Module-specific issue tracking
│   ├── new/          # New issues
│   ├── wip/          # Work in progress
│   └── done/         # Completed issues
├── scripts/          # Module utility scripts
├── mod/              # Module source code (can contain nested modules)
└── tests/            # Module tests
```

## Current Module Hierarchy

- **RepositoryTemplate** - Template module structure
- **IdeaInspiration** - Idea generation and inspiration
  - **Sources** - Various content sources
    - **Content** - Content processing
      - **Shorts** - Short-form content handling
        - **YouTubeShortsSource** - YouTube Shorts source

## Module Naming Convention

Nested modules follow a dot notation based on their path:

- `mod/RepositoryTemplate` → `PrismQ.RepositoryTemplate`
- `mod/IdeaInspiration/mod/Sources` → `PrismQ.IdeaInspiration.Sources`
- `mod/IdeaInspiration/mod/Sources/mod/Content/mod/Shorts/mod/YouTubeShortsSource` → `PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeShortsSource`

## Module Principles

Each module:
- Has a single, well-defined responsibility
- Maintains its own documentation
- Manages its own issues and workflows
- Contains its own tests
- Can be developed independently

## Interactive Visualization

For an interactive view of the module hierarchy, see [repository-tree.html](repository-tree.html).
