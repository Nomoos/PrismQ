# Project Documentation

This directory contains project-level documentation for the PrismQ.T.Idea.Inspiration repository.

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

**Essential Starting Points**:
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** ⭐ - Quick navigation guide for the project
- **[ISSUE_MANAGEMENT.md](./ISSUE_MANAGEMENT.md)** - Issue workflow and tracking guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture, module organization patterns, and design decisions
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - How to contribute to the project

**Standards & Guidelines**:
- **[SOLID_PRINCIPLES.md](./SOLID_PRINCIPLES.md)** ⭐ - SOLID design principles guide with Python examples
- **[README_STANDARDS.md](./README_STANDARDS.md)** - Standards for writing README files in the PrismQ ecosystem
- **[PYTHON_PACKAGING_STANDARD.md](./PYTHON_PACKAGING_STANDARD.md)** - Python packaging and configuration standards
- **[PYTHON_VERSION_DECISION.md](./PYTHON_VERSION_DECISION.md)** - Python 3.10 version requirement and rationale
- **[PYTHON_LAUNCHER_GUIDE.md](./PYTHON_LAUNCHER_GUIDE.md)** - How to use `py` launcher for version management
- **[LOGGING_BEST_PRACTICES.md](./LOGGING_BEST_PRACTICES.md)** - Logging standards and best practices

**Setup & Development**:
- **[SETUP.md](./SETUP.md)** - Development environment setup guide
- **[BATCH_PROCESSING.md](./BATCH_PROCESSING.md)** - Batch processing patterns and guidelines
- **[MODULE_DISCOVERY.md](./MODULE_DISCOVERY.md)** - Module discovery and dynamic loading

**Planning & History**:
- **[FUTURE_ENHANCEMENTS.md](./FUTURE_ENHANCEMENTS.md)** - Planned features and architectural improvements
- **[IMPLEMENTATION_HISTORY.md](./IMPLEMENTATION_HISTORY.md)** - Historical record of major implementations
- **[archive/](./archive/)** - Archived phase documentation (Phase 0, Phase 1 complete)

### 🛠️ Development Guides ([development/](./development/))

- **[VIRTUAL_ENVIRONMENTS.md](./development/VIRTUAL_ENVIRONMENTS.md)** - Virtual environment strategy and setup (consolidated)
- **[DATABASE.md](./development/DATABASE.md)** - Database integration guide (consolidated)
- **[TESTING.md](./development/TESTING.md)** - Testing and coverage guide (consolidated)
- **[DIRENV_SETUP.md](./development/DIRENV_SETUP.md)** - direnv configuration for automatic environment activation
- **[MIGRATION.md](./development/MIGRATION.md)** - Guide for migrating modules to use EnvLoad

### 🎯 SOLID Principles ([solid/](./solid/))

Central location for SOLID design principle resources:

- **[SOLID_PRINCIPLES.md](./SOLID_PRINCIPLES.md)** - Comprehensive SOLID principles guide
- **[solid/code_reviews/](./solid/code_reviews/)** - SOLID compliance code reviews
  - Core Modules (Classification, EnvLoad, Model, Scoring)
  - Video and Text Modules

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

### 🔄 Queue System ([queue/](./queue/))

SQLite-based persistent task queue for distributed work processing:

- **[QUEUE_ARCHITECTURE.md](./queue/QUEUE_ARCHITECTURE.md)** - System architecture, design decisions, and component overview
  - Why SQLite vs MySQL/PostgreSQL/Redis
  - Database schema and concurrency model
  - WAL mode and Windows optimization
  - Integration with PrismQ ecosystem
- **[QUEUE_API_REFERENCE.md](./queue/QUEUE_API_REFERENCE.md)** - Complete API documentation
  - QueueDatabase, Task, Worker, TaskLog classes
  - Usage examples and error handling
  - Best practices and performance tips
- **[QUEUE_CONFIGURATION.md](./queue/QUEUE_CONFIGURATION.md)** - Configuration and tuning guide
  - PRAGMA settings explained (WAL, synchronous, busy_timeout, etc.)
  - Platform-specific configuration (Windows, Linux, macOS)
  - Performance tuning for different workloads
- **[QUEUE_QUICK_START.md](./queue/QUEUE_QUICK_START.md)** - Getting started guide
  - Installation and setup
  - Basic usage examples
  - Common operations and troubleshooting
- **[QUEUE_INTEGRATION.md](./queue/QUEUE_INTEGRATION.md)** - Integration and migration guide
  - BackgroundTaskManager integration
  - Use case examples (video processing, user actions, scheduling)
  - Migration strategy and rollback plan

## Documentation Guidelines

### Where to Add New Documentation

- **Core architecture/design**: Repository root (`_meta/docs/`)
- **Development guides**: `_meta/docs/development/`
- **Architecture decisions**: `_meta/docs/decisions/`
- **Research documents**: `_meta/research/`
- **Documentation standards**: `_meta/docs/` or `_meta/docs/templates/`

### Documentation Best Practices

1. **Use clear, descriptive titles** - Make it easy to find what you're looking for
2. **Include dates and status** - Track when documents were created/updated
3. **Link related documents** - Help readers find additional context
4. **Follow SOLID documentation principles** - Single responsibility, well-scoped topics
5. **Keep consolidation in mind** - Combine related documents when possible
6. **Avoid duplication** - Each piece of information should exist in exactly ONE place

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
