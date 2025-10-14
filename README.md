# PrismQ

A modular AI-powered content generation ecosystem. Each subfolder follows the [RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate) structure.

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