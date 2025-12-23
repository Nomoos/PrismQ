# Module Hierarchy and Layering Principles

## Overview

This document describes the PrismQ module hierarchy based on **hierarchical responsibility** where each module is responsible only for its own level of abstraction.

## Module Levels

### 1. src/ (PrismQ) - Cross-Cutting Concerns

**Responsibility**: Most generic, cross-cutting functionality used across the entire project.

**Contains**:
- Database configuration (`DatabaseConfig`)
- Environment configuration (`Config`)
- Cross-cutting utilities (used by all modules regardless of type)

**Does NOT contain**:
- Content-specific logic
- AI generation (that's content processing, not cross-cutting)
- Workflow-specific code

**Example**:
```python
from src.startup import DatabaseConfig, create_database_config

db_config = create_database_config()
db_path = db_config.get_database_path()
```

---

### 2. T/ (PrismQ.T) - Content Framework

**Responsibility**: General utilities and abstractions for working with content.

**Contains**:
- Content-agnostic helpers
- Shared interfaces
- Base classes for content operations

---

### 3. T/Content/ (PrismQ.T.Content) - Content Processing

**Responsibility**: Generic functionality for handling content (processing, validation, transformation, generation).

**Contains**:
- AI configuration for content generation (`AISettings`)
- Content processing utilities
- Generation helpers

**Independent of**: Content origin (Idea, Story, etc.)

**Example**:
```python
from T.Content.src.ai_config import AISettings, create_ai_config

ai_settings = create_ai_config()
model = ai_settings.get_model()  # qwen3:32b
```

**Why AI is here, not in src/**:
- AI is used for **content generation/processing**
- Not all PrismQ modules need AI (database utilities, config, etc.)
- Content-specific concern, not cross-cutting

---

### 4. T/Content/From/ (PrismQ.T.Content.From) - Source-Based Content

**Responsibility**: Shared functionality for all content derived from a source.

**Contains**:
- Source-level abstractions
- Common patterns for content from sources

---

### 5. T/Content/From/Idea/ (PrismQ.T.Content.From.Idea) - Idea-Derived Content

**Responsibility**: Shared logic for all content derived from an Idea.

**Contains**:
- Idea-to-content transformations
- Common Idea-based workflows
- Applies to titles, scripts, descriptions generated from Ideas

---

### 6. T/Content/From/Idea/Title/ (PrismQ.T.Content.From.Idea.Title) - Title-Specific

**Responsibility**: ONLY title-specific functionality.

**Contains**:
- Title generation logic
- Title-specific validation
- Title workflow

**Does NOT contain**:
- Generic Idea logic (that's one level up)
- Generic content logic (that's two levels up)
- AI configuration (that's at T/Content/)

**Example**:
```python
# Title module imports from T/Content
from T.Content.src.ai_config import create_ai_config

# Title-specific logic
class TitleGenerator:
    def __init__(self):
        self.ai_settings = create_ai_config()
```

---

## Module Boundaries Rules

### Higher-Level Modules

**Must**:
- Contain generic, reusable logic
- Be independent of lower levels
- Have no dependencies on lower modules

**Example**: `src/` cannot import from `T/Content/`

### Lower-Level Modules

**Must**:
- Contain only specialized functionality
- Import from higher levels (not duplicate)
- Depend on higher-level modules

**Example**: `T/Content/From/Idea/Title/` imports from `T/Content/`

### No Duplication Rule

If logic is reusable by more than one module, it **must be moved upward** to the appropriate level.

**Wrong**:
```python
# T/Content/From/Idea/Title/src/ai_config.py
DEFAULT_AI_MODEL = "qwen3:32b"  # ❌ Duplication!
```

**Correct**:
```python
# T/Content/src/ai_config.py
DEFAULT_AI_MODEL = "qwen3:32b"  # ✓ Defined once

# T/Content/From/Idea/Title/src/ai_config.py  
from T.Content.src.ai_config import DEFAULT_AI_MODEL  # ✓ Import
```

---

## Decision Tree: Where Does This Code Belong?

### Ask These Questions:

1. **Is it used across ALL PrismQ modules?**
   - YES → `src/` (e.g., database, environment config)
   - NO → Continue...

2. **Is it for content processing/generation?**
   - YES → `T/Content/` (e.g., AI settings, generation)
   - NO → Continue...

3. **Is it specific to content from a source?**
   - YES → `T/Content/From/` 
   - NO → Continue...

4. **Is it specific to Idea-derived content?**
   - YES → `T/Content/From/Idea/`
   - NO → Continue...

5. **Is it ONLY for titles?**
   - YES → `T/Content/From/Idea/Title/`

---

## Examples

### ✓ Correct Hierarchy

**Database Configuration** → `src/startup.py`
- Used by all modules (Idea, Story, Content, etc.)
- Cross-cutting concern

**AI Configuration** → `T/Content/src/ai_config.py`
- Used for content generation
- Content-specific, not cross-cutting

**Title Generation** → `T/Content/From/Idea/Title/src/content_generator.py`
- Specific to title workflow
- Imports AI config from `T/Content/`

### ❌ Wrong Hierarchy

**AI Configuration** in `src/` ❌
- Too broad - not all modules need AI
- Implies AI is cross-cutting (it's not)

**Database Configuration** in `T/Content/` ❌
- Too narrow - many modules need database
- Database is cross-cutting

---

## Module Layout Convention

Each module follows the same internal structure:

```
ModuleName/
├── src/              # Source code
│   ├── __init__.py
│   └── *.py
├── _meta/            # Metadata, docs, tests
│   ├── docs/
│   ├── examples/
│   └── tests/
└── __init__.py
```

---

## Verification

Run this test to verify hierarchy:

```python
# Test 1: src/ - Cross-cutting
from src.startup import DatabaseConfig
db = DatabaseConfig(database_path="/path/to/db")

# Test 2: T/Content/ - Content processing
from T.Content.src.ai_config import AISettings
ai = AISettings()

# Test 3: Title imports from T/Content (no duplication)
from T.Content.From.Idea.Title.src.ai_config import get_local_ai_model
# This imports from T/Content, not duplicate
```

---

## Summary

| Level | Scope | Examples |
|-------|-------|----------|
| `src/` | Cross-cutting | Database, Config |
| `T/` | Content framework | Base classes |
| `T/Content/` | Content processing | AI, generation |
| `T/Content/From/` | Source-based | Source abstractions |
| `T/Content/From/Idea/` | Idea-derived | Idea transformations |
| `T/Content/From/Idea/Title/` | Title-specific | Title generation |

**Key Principle**: Each level contains ONLY what belongs at that level of abstraction. No duplication, no mixing concerns.
