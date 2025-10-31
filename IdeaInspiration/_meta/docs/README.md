# Project Documentation

This directory contains project-level documentation for the PrismQ.IdeaInspiration repository.

## Purpose

Project-level documentation that applies to the entire repository, including:
- Architecture decisions
- Development guidelines
- Integration guides
- Contributing guidelines
- Design principles

## Documentation Files

### Core Documentation
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture, module organization patterns, and design decisions
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - How to contribute to the project

### Database & Integration
- **[DATABASE_INTEGRATION.md](./DATABASE_INTEGRATION.md)** - Dual-save architecture implementation guide
- **[DATABASE_INTEGRATION_SUMMARY.md](./DATABASE_INTEGRATION_SUMMARY.md)** - Executive summary of dual-save pattern

### Model & Data Architecture
- **[MODEL_EXTENSION_RESEARCH.md](./MODEL_EXTENSION_RESEARCH.md)** - Comprehensive research on extending IdeaInspiration Model (30,000+ characters)
  - Source/Content/Idea separation analysis
  - New entity types (Signal, Category, Attachment, Channel, Collection)
  - Source → Idea transformation pipeline
  - Blending strategies (topic, trend, multi-platform, temporal)
- **[MODEL_QUESTIONS_ANSWERS.md](./MODEL_QUESTIONS_ANSWERS.md)** - Quick reference Q&A for Model extension questions

### Development & Tooling
- **[DIRENV_SETUP.md](./DIRENV_SETUP.md)** - direnv configuration and setup
- **[LOGGING_BEST_PRACTICES.md](./LOGGING_BEST_PRACTICES.md)** - Logging standards and best practices
- **[SCRIPT_STANDARDIZATION_RECOMMENDATION.md](./SCRIPT_STANDARDIZATION_RECOMMENDATION.md)** - Script format recommendations
- **[SCRIPT_FORMAT_DECISION.md](./SCRIPT_FORMAT_DECISION.md)** - PowerShell vs Batch decisions
- **[VENV_STRATEGY_DECISION.md](./VENV_STRATEGY_DECISION.md)** - Virtual environment strategy
- **[VENV_STRATEGY_EXECUTIVE_SUMMARY.md](./VENV_STRATEGY_EXECUTIVE_SUMMARY.md)** - venv strategy summary
- **[VIRTUAL_ENV_PER_PROJECT.md](./VIRTUAL_ENV_PER_PROJECT.md)** - Per-project virtual environment guide

## Structure

Documentation files should be organized by topic. Common documentation includes:
- `ARCHITECTURE.md` - System architecture and design
- `CONTRIBUTING.md` - How to contribute to the project
- `DEVELOPMENT.md` - Development setup and workflows
- `DEPLOYMENT.md` - Deployment instructions
- `SOLID_PRINCIPLES.md` - SOLID design principles guide

## Note

Individual modules (Classification, Scoring, Sources, etc.) may have their own `docs/` or `_meta/docs/` folders for module-specific documentation. This directory is for repository-level documentation.
