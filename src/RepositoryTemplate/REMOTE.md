# Remote Repository Configuration

This module is synchronized with its own repository.

## Repository Information

- **Remote URL**: `https://github.com/Nomoos/PrismQ.RepositoryTemplate.git`
- **Remote Name**: `repositorytemplate-remote`
- **Branch**: `main`

## Synchronization

This module can be developed independently in its repository and synced to the main PrismQ repository using the automated sync scripts.

### Sync from Module Repository to Main

```bash
# From main PrismQ repository
./scripts/sync-modules.sh src/RepositoryTemplate
```

### Push from Main to Module Repository

```bash
# From main PrismQ repository
git subtree push --prefix=src/RepositoryTemplate repositorytemplate-remote main
```

## Development Workflow

1. **Option A: Work in Module Repository**
   - Clone: `git clone https://github.com/Nomoos/PrismQ.RepositoryTemplate.git`
   - Make changes and commit
   - Sync to main: `./scripts/sync-modules.sh src/RepositoryTemplate`

2. **Option B: Work in Main Repository**
   - Make changes in `src/RepositoryTemplate/`
   - Commit changes
   - Push to module: `git subtree push --prefix=src/RepositoryTemplate repositorytemplate-remote main`

## Configuration Format

This file uses a standard format that can be read by automation tools:

```
REMOTE_URL=https://github.com/Nomoos/PrismQ.RepositoryTemplate.git
REMOTE_NAME=repositorytemplate-remote
BRANCH=main
```
