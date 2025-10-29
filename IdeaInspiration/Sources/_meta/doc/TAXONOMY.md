# PrismQ Ecosystem Taxonomy

This document provides a comprehensive taxonomy of the PrismQ ecosystem, defining the structure, relationships, and organization of all components within the project.

## Overview

PrismQ is a multi-repository ecosystem designed for idea collection, processing, and management. The system follows a modular architecture where each repository serves a specific purpose while maintaining clear interfaces and dependencies.

## Repository Categories

### Core Repositories

#### 1. PrismQ.Idea.Sources
- **Purpose**: Central navigation, documentation hub, and data models library
- **Type**: Python Library & Documentation Repository
- **Dependencies**: None (models library with documentation)
- **Description**: Serves as the entry point for understanding the PrismQ ecosystem, providing taxonomy documentation, navigation to all other repositories, and Python data models for content sources.

#### 2. PrismQ.IdeaCollector
- **Purpose**: Idea collection and inspiration gathering
- **Type**: Python CLI Application
- **Dependencies**: External APIs (configurable)
- **Description**: Standalone Python CLI tool that gathers idea inspirations from various sources and processes them for storage and analysis.

#### 3. PrismQ.RepositoryTemplate
- **Purpose**: Project template for new PrismQ repositories
- **Type**: Template Repository
- **Dependencies**: None (template only)
- **Description**: Provides a standardized structure for creating new projects within the PrismQ ecosystem, including predefined project structure, configuration files, and licensing.

## Component Relationships

```
PrismQ.Idea.Sources (Documentation Hub)
    ├─ Links to → PrismQ.IdeaCollector
    ├─ Links to → PrismQ.RepositoryTemplate
    └─ Links to → [Future Components]

PrismQ.IdeaCollector (Data Collection)
    └─ Uses → External APIs

PrismQ.RepositoryTemplate (Template)
    └─ Used by → New Repository Creation
```

## Technology Stack

### Languages
- **Python**: Primary language for CLI tools and processing
- **Markdown**: Documentation format
- **YAML/TOML**: Configuration files

### Tools & Frameworks
- **Python 3.x**: Runtime environment
- **pip/pyproject.toml**: Dependency management
- **Git**: Version control
- **GitHub**: Repository hosting and CI/CD

## Organizational Structure

### Documentation Standards
All PrismQ repositories follow these documentation standards:
- `README.md`: Primary project documentation
- `docs/`: Extended documentation directory
- `CONTRIBUTING.md`: Contribution guidelines
- `LICENSE`: Licensing information

### Code Organization
- `src/`: Source code
- `tests/`: Test files
- `scripts/`: Utility scripts
- `docs/`: Documentation

## Access Levels

### Public Repositories
- **PrismQ.IdeaCollector**: Open source
- **PrismQ.RepositoryTemplate**: Open source

### Private Repositories
- **PrismQ.Idea.Sources**: Private (documentation and navigation)

## Future Extensions

The taxonomy is designed to be extensible. Future components may include:
- Processing pipelines
- Storage solutions
- Analysis tools
- Visualization components
- API services

Each new component should:
1. Follow the established naming convention: `PrismQ.[ComponentName]`
2. Include proper documentation
3. Define clear interfaces
4. Document dependencies
5. Update this taxonomy document

## Versioning Strategy

- **Major Version**: Breaking changes to interfaces or architecture
- **Minor Version**: New features or components
- **Patch Version**: Bug fixes and documentation updates

## Maintenance

This taxonomy document should be updated whenever:
- A new repository is added to the ecosystem
- Repository relationships change
- Technology stack is updated
- Organizational standards evolve

---

*Last Updated: 2025-10-12*
