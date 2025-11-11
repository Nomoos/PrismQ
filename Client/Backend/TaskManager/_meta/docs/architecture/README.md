# Architecture Documentation

This directory contains architectural design documents for the TaskManager system.

## Documents

### Core Architecture
- **[DATA_DRIVEN_ARCHITECTURE.md](DATA_DRIVEN_ARCHITECTURE.md)** - Overview of the data-driven architecture design
- **[DATA_DRIVEN_API.md](DATA_DRIVEN_API.md)** - Data-driven API implementation details
- **[TASKMANAGER_ORGANIZATION.md](TASKMANAGER_ORGANIZATION.md)** - Project structure and organization

### Component Analysis
- **[CUSTOM_HANDLERS_ANALYSIS.md](CUSTOM_HANDLERS_ANALYSIS.md)** - Analysis of custom handler implementations

## Key Concepts

The TaskManager uses a **data-driven architecture** where:
- API endpoints are defined in the database, not code
- Validation rules are configured via database records
- Actions are executed dynamically based on database configuration
- No code deployment needed to add new endpoints

This design enables rapid development, easier testing, and better parallelization of work.
