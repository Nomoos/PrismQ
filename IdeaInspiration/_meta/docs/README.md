# Project Documentation

This directory contains project-level documentation for the PrismQ.IdeaInspiration repository.

## Purpose

Project-level documentation that applies to the entire repository, including:
- Architecture decisions
- Development guidelines
- Integration guides
- Contributing guidelines
- Design principles

## Documentation Structure

Documentation is organized into the following categories:

### 📋 Core Documentation (Repository Root)

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture, module organization patterns, and design decisions
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - How to contribute to the project
- **[PYTHON_PACKAGING_STANDARD.md](./PYTHON_PACKAGING_STANDARD.md)** - Python packaging and configuration standards
- **[PYTHON_VERSION_DECISION.md](./PYTHON_VERSION_DECISION.md)** - Python 3.10 version requirement and rationale
- **[PYTHON_LAUNCHER_GUIDE.md](./PYTHON_LAUNCHER_GUIDE.md)** - How to use `py` launcher for version management
- **[SETUP.md](./SETUP.md)** - Development environment setup guide
- **[LOGGING_BEST_PRACTICES.md](./LOGGING_BEST_PRACTICES.md)** - Logging standards and best practices
- **[BATCH_PROCESSING.md](./BATCH_PROCESSING.md)** - Batch processing patterns and guidelines
- **[MODULE_DISCOVERY.md](./MODULE_DISCOVERY.md)** - Module discovery and dynamic loading

### 🛠️ Development Guides ([development/](./development/))

- **[VIRTUAL_ENVIRONMENTS.md](./development/VIRTUAL_ENVIRONMENTS.md)** - Virtual environment strategy and setup (consolidated)
- **[DATABASE.md](./development/DATABASE.md)** - Database integration guide (consolidated)
- **[TESTING.md](./development/TESTING.md)** - Testing and coverage guide (consolidated)
- **[DIRENV_SETUP.md](./development/DIRENV_SETUP.md)** - direnv configuration for automatic environment activation
- **[MIGRATION.md](./development/MIGRATION.md)** - Guide for migrating modules to use ConfigLoad

### 🎯 Architecture Decisions ([decisions/](./decisions/))

- **[SCRIPT_FORMAT_DECISION.md](./decisions/SCRIPT_FORMAT_DECISION.md)** - PowerShell vs Batch script format decisions
- **[SCRIPT_STANDARDIZATION_RECOMMENDATION.md](./decisions/SCRIPT_STANDARDIZATION_RECOMMENDATION.md)** - Script standardization recommendations

### 📦 Model & Data Architecture

- **[MODEL_EXTENSION_RESEARCH.md](./MODEL_EXTENSION_RESEARCH.md)** - Comprehensive research on extending IdeaInspiration Model
  - Source/Content/Idea separation analysis
  - New entity types (Signal, Category, Attachment, Channel, Collection)
  - Source → Idea transformation pipeline
  - Blending strategies (topic, trend, multi-platform, temporal)
- **[MODEL_QUESTIONS_ANSWERS.md](./MODEL_QUESTIONS_ANSWERS.md)** - Quick reference Q&A for Model extension questions

### 📁 Archive ([archive/](./archive/))

Historical documentation that has been superseded or completed:

#### Migrations ([archive/migrations/](./archive/migrations/))
- **[SINGLE_DB_MIGRATION_COMPLETE.md](./archive/migrations/SINGLE_DB_MIGRATION_COMPLETE.md)** - Single database migration completion summary
- **[SINGLE_DB_IMPLEMENTATION_SUMMARY.md](./archive/migrations/SINGLE_DB_IMPLEMENTATION_SUMMARY.md)** - Single database implementation details
- **[SINGLE_DB_MIGRATION_GUIDE.md](./archive/migrations/SINGLE_DB_MIGRATION_GUIDE.md)** - Migration guide from dual-save to single database
- **[SINGLE_DB_MIGRATION_STATUS.md](./archive/migrations/SINGLE_DB_MIGRATION_STATUS.md)** - Migration status tracker

#### Decisions (Archived) ([archive/decisions/](./archive/decisions/))
- **[VENV_STRATEGY_DECISION.md](./archive/decisions/VENV_STRATEGY_DECISION.md)** - Virtual environment strategy decision (full analysis)
- **[VENV_STRATEGY_EXECUTIVE_SUMMARY.md](./archive/decisions/VENV_STRATEGY_EXECUTIVE_SUMMARY.md)** - VENV strategy executive summary
- **[VENV_STRATEGY_VISUAL_DECISION.md](./archive/decisions/VENV_STRATEGY_VISUAL_DECISION.md)** - Visual decision guide
- **[VIRTUAL_ENV_PER_PROJECT.md](./archive/decisions/VIRTUAL_ENV_PER_PROJECT.md)** - Per-project virtual environment guide
- **[WHICH_STRATEGY_ANSWER.md](./archive/decisions/WHICH_STRATEGY_ANSWER.md)** - Direct answer to strategy question

#### Deprecated Architecture ([archive/](./archive/))
- **[DATABASE_INTEGRATION.md](./archive/DATABASE_INTEGRATION.md)** - Old dual-save architecture (deprecated)
- **[DATABASE_INTEGRATION_SUMMARY.md](./archive/DATABASE_INTEGRATION_SUMMARY.md)** - Old dual-save pattern (deprecated)

#### Validation Reports ([archive/validation/](./archive/validation/))
- **[COVERAGE_SUMMARY.md](./archive/validation/COVERAGE_SUMMARY.md)** - Test coverage analysis summary (88.7% overall)
- **[TEST_COVERAGE_REPORT.md](./archive/validation/TEST_COVERAGE_REPORT.md)** - Detailed coverage report
- **[COVERAGE_IMPROVEMENT_PLAN.md](./archive/validation/COVERAGE_IMPROVEMENT_PLAN.md)** - Coverage improvement action plan
- **[COVERAGE_ANALYSIS_COMPLETE.md](./archive/validation/COVERAGE_ANALYSIS_COMPLETE.md)** - Complete coverage analysis
- **[TESTING_QUICK_REFERENCE.md](./archive/validation/TESTING_QUICK_REFERENCE.md)** - Legacy testing reference (superseded by development/TESTING.md)
- Repository purpose validation reports (completed November 2025)

#### Other ([archive/completed_issues/](./archive/completed_issues/))
- **[LEGACY_CLEANUP_SUMMARY.md](./archive/completed_issues/LEGACY_CLEANUP_SUMMARY.md)** - Summary of legacy content cleanup (November 2025)
- **[107-live-logs-ui-implementation.md](./archive/completed_issues/107-live-logs-ui-implementation.md)** - Live logs UI implementation notes

## Documentation Guidelines

### Where to Add New Documentation

- **Core architecture/design**: Repository root (`_meta/docs/`)
- **Development guides**: `_meta/docs/development/`
- **Architecture decisions**: `_meta/docs/decisions/`
- **Research documents**: Repository root (`_meta/docs/`)
- **Completed projects/migrations**: `_meta/docs/archive/`
- **Validation reports**: `_meta/docs/archive/validation/`

### Documentation Best Practices

1. **Use clear, descriptive titles** - Make it easy to find what you're looking for
2. **Include dates and status** - Track when documents were created/updated
3. **Link related documents** - Help readers find additional context
4. **Archive superseded docs** - Move old versions to `archive/` with clear notes
5. **Keep consolidation in mind** - Combine related documents when possible

## Module-Specific Documentation

Individual modules (Classification, Scoring, Sources, etc.) maintain their own documentation:

- **User-facing**: `module/docs/` - User guides, setup, API reference
- **Internal/development**: `module/_meta/docs/` - Implementation details, research, technical decisions

This separation allows for:
- Clear distinction between user and developer documentation
- Module autonomy in documentation structure
- Easier navigation and maintenance

## Related Documentation

- [Repository README](../../README.md) - Main repository overview
- [Issue Tracking](./../issues/README.md) - Issue management system
- [Scripts Documentation](./../_scripts/README.md) - Automation scripts
