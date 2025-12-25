# Source Shared Code

This directory contains shared code and utilities used across all Source module implementations.

## Structure

```
src/
├── __init__.py
├── core/           # Base classes and core utilities
├── schemas/        # Common schema patterns
├── mappers/        # Shared mapping utilities
└── clients/        # Common HTTP client patterns
```

## Purpose

The `src/` directory provides reusable components that can be shared across all source implementations (YouTube, Reddit, HackerNews, TikTok, etc.). This promotes code reuse and consistency across the Source module.

### Core (`core/`)
Base classes, abstract interfaces, and core utilities that all sources can extend or use:
- Base source classes
- Configuration management
- Common authentication patterns
- Shared utilities

### Schemas (`schemas/`)
Common data structure patterns and base schemas that sources can extend:
- Base data models
- Common field definitions
- Validation patterns

### Mappers (`mappers/`)
Shared utilities for transforming platform-specific data into `IdeaInspiration` objects:
- Base mapper classes
- Common transformation functions
- Field mapping utilities

### Clients (`clients/`)
Reusable HTTP client patterns and utilities:
- Base HTTP client
- Rate limiting
- Retry logic
- Authentication helpers

## Usage

Source implementations can import shared code from this directory:

```python
from Source.src.core import BaseSource
from Source.src.mappers import base_mapper
from Source.src.clients import HTTPClient
```

## Platform-Specific Code

For code specific to a single platform (e.g., YouTube-only utilities), use that platform's `src/` directory:
- `YouTube/src/` - YouTube-specific shared code
- `Reddit/src/` - Reddit-specific shared code
- etc.
