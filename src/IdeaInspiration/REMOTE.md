# Remote Repository Configuration

This module is synchronized with its own repository.

## Repository Information

- **Remote URL**: `https://github.com/Nomoos/PrismQ.IdeaInspiration.git`
- **Remote Name**: `ideainspiration-remote`
- **Branch**: `main`

## Synchronization

This module can be developed independently in its repository and synced to the main PrismQ repository using the automated sync scripts.

### Sync from Module Repository to Main

```bash
# From main PrismQ repository
./scripts/sync-modules.sh src/IdeaInspiration
```

### Push from Main to Module Repository

```bash
# From main PrismQ repository
git subtree push --prefix=src/IdeaInspiration ideainspiration-remote main
```

## Development Workflow

1. **Option A: Work in Module Repository**
   - Clone: `git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git`
   - Make changes and commit
   - Sync to main: `./scripts/sync-modules.sh src/IdeaInspiration`

2. **Option B: Work in Main Repository**
   - Make changes in `src/IdeaInspiration/`
   - Commit changes
   - Push to module: `git subtree push --prefix=src/IdeaInspiration ideainspiration-remote main`

## Configuration Format

This file uses a standard format that can be read by automation tools:

```
REMOTE_URL=https://github.com/Nomoos/PrismQ.IdeaInspiration.git
REMOTE_NAME=ideainspiration-remote
BRANCH=main
```
