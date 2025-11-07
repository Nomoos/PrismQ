# Client Module Migration Notice

## Status

The Web Client control panel module has been **moved to a separate repository** for better modularity and independent development.

## Background

The Client module was previously part of the PrismQ.IdeaInspiration monorepo, located at `./Client/`. As of the repository restructuring, it has been extracted into its own repository to:

- Enable independent versioning and release cycles
- Reduce the complexity of the main IdeaInspiration repository
- Allow focused development on the web interface separately from data processing modules
- Improve build and deployment workflows

## What Was Moved

The following components were part of the Client module:
- **Backend**: FastAPI-based REST API server (Python 3.10+)
- **Frontend**: Vue 3 + TypeScript web application
- **Documentation**: Client-specific architecture and setup guides
- **Scripts**: Client launcher scripts (`run_both.bat`, `run_backend.bat`, `run_frontend.bat`)

## Current Repository Structure

The PrismQ.IdeaInspiration repository now focuses on core data processing modules:
- **Classification** - Content categorization and story detection
- **ConfigLoad** - Centralized configuration management
- **Model** - Core IdeaInspiration data model
- **Scoring** - Content scoring and evaluation engine
- **Sources** - Content source integrations (24 sources)

## References Cleanup

The following files have been updated to remove Client references:
- `README.md` - Removed Client from module list and quick start
- `_meta/docs/ARCHITECTURE.md` - Updated system diagrams to remove Client orchestration layer
- `_meta/docs/SETUP.md` - Removed Client setup references
- `_meta/_scripts/activate_env.ps1` - Removed Client from available projects
- `_meta/_scripts/activate_env.sh` - Removed Client from available projects
- Removed: `_meta/_scripts/run_both.bat`, `run_backend.bat`, `run_frontend.bat`

## For Developers

If you need to work with the Web Client:
- The Client module functionality is now in a separate repository (to be determined/announced)
- This repository focuses on the core data processing pipeline
- Integration between Client and processing modules is maintained through the shared Model interfaces

## Historical Note

References to the Client module may still appear in:
- Issue documentation in `_meta/issues/` (historical context)
- Research documents in `_meta/research/` (historical analysis)
- Commit history and git logs

These references are preserved for historical accuracy but should not be considered current architecture.
