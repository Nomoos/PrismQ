# Module Hierarchy and Organization

## Principle: Common at Top, Specific at Bottom

This document describes how the PrismQ codebase follows the principle of keeping common/general functionality in top-level modules and specific functionality in lower-level modules.

## Module Hierarchy

```
PrismQ/
├── src/                          # TOP LEVEL - General/Common functionality
│   ├── startup.py                # ✅ General DB + AI configuration (USE THIS)
│   ├── config.py                 # ✅ General environment configuration
│   ├── idea.py                   # ✅ General Idea database operations
│   └── story.py                  # ✅ General Story database operations
│
└── T/                            # LOWER LEVELS - Specific functionality
    └── Content/
        └── From/
            └── Idea/
                └── Title/
                    └── src/
                        ├── ai_config.py          # ✅ Wrapper - RE-USES src/startup.py
                        ├── content_generator.py   # ✅ Specific to Content generation
                        └── ai_content_generator.py # ✅ Specific to Content AI
```

## ✅ Correct Pattern (After Refactoring)

### Top Level: General Functionality

**`src/startup.py`** - General startup utilities
```python
# Constants - used by all modules
DEFAULT_AI_MODEL = "qwen3:32b"
DEFAULT_AI_API_BASE = "http://localhost:11434"
AI_TEMPERATURE_MIN = 0.6
AI_TEMPERATURE_MAX = 0.8

# Classes - reusable across all scripts
@dataclass
class AISettings:
    """General AI settings - used by any script"""
    model: str = DEFAULT_AI_MODEL
    api_base: str = DEFAULT_AI_API_BASE
    ...

@dataclass
class StartupConfig:
    """General startup configuration"""
    database_path: str
    ai_settings: AISettings
    ...

# Factory - composition root pattern
def create_startup_config(...) -> StartupConfig:
    """Create general config - call from main()"""
    ...
```

**Use Case**: Any script in PrismQ that needs DB or AI configuration

### Lower Level: Specific Functionality

**`T/Content/From/Idea/Title/src/ai_config.py`** - Content-specific wrapper
```python
# RE-USES top-level module (no duplication)
from src.startup import (
    DEFAULT_AI_MODEL,
    DEFAULT_AI_API_BASE,
    AI_TEMPERATURE_MIN,
    AI_TEMPERATURE_MAX,
    AISettings,
    create_startup_config,
)

# Wrapper functions for backward compatibility
def get_local_ai_model() -> str:
    """Wrapper - uses top-level constant"""
    return DEFAULT_AI_MODEL

def get_local_ai_temperature() -> float:
    """Wrapper - uses top-level constants"""
    return random.uniform(AI_TEMPERATURE_MIN, AI_TEMPERATURE_MAX)
```

**Use Case**: Content generation specific code that needs AI config

**`T/Content/From/Idea/Title/src/content_generator.py`** - Content-specific logic
```python
# This contains ONLY content generation specific logic
# Uses general AI config from top level
class ContentGenerator:
    """Content-specific business logic"""
    ...
```

## ❌ Anti-Pattern (Before Refactoring)

**Problem**: Lower-level module duplicated general functionality

```python
# T/Content/From/Idea/Title/src/ai_config.py (BEFORE - BAD)
def get_local_ai_model() -> str:
    """Hardcoded in lower module - duplication!"""
    return "qwen3:32b"  # ❌ Duplicates src/startup.py

def get_local_ai_temperature() -> float:
    """Hardcoded in lower module - duplication!"""
    MIN_TEMPERATURE = 0.6  # ❌ Duplicates src/startup.py
    MAX_TEMPERATURE = 0.8  # ❌ Duplicates src/startup.py
    return random.uniform(MIN_TEMPERATURE, MAX_TEMPERATURE)
```

**Issues**:
- Code duplication
- Hard to maintain (change in two places)
- Inconsistency risk
- Violates DRY principle

## Benefits of Current Organization

### 1. Single Source of Truth
- AI model defined once in `src/startup.py`
- All modules use the same value
- Change once, applies everywhere

### 2. Clear Separation
- **Top level**: "What is common?"
  - Database path
  - AI model configuration
  - Environment settings
  
- **Lower level**: "What is specific?"
  - Content generation logic
  - Prompt engineering
  - Workflow-specific code

### 3. Easy Testing
```python
# Test with custom config (top level)
config = StartupConfig(
    database_path="/test/db",
    ai_settings=AISettings(model="test-model")
)

# Inject into lower-level code
generator = ContentGenerator(config)
```

### 4. Maintainability
- Change AI model: Edit one constant in `src/startup.py`
- All modules automatically use new value
- No risk of inconsistency

## How to Decide: Top or Bottom?

### Put in TOP level (`src/`) if:
- ✅ Used by multiple modules
- ✅ General configuration (DB, AI, env)
- ✅ Reusable across different workflows
- ✅ Core business objects (Idea, Story)
- ✅ Constants and defaults

### Put in LOWER level (`T/*/`) if:
- ✅ Specific to one workflow
- ✅ Domain-specific logic
- ✅ Uses (not duplicates) top-level modules
- ✅ Workflow-specific models
- ✅ Custom implementations

## Migration Guide

### For Existing Lower-Level Modules

If you have a lower-level module with general functionality:

**Step 1**: Identify what's general
```python
# In lower module - what is general?
MODEL = "qwen3:32b"  # ✅ General - all scripts use same model
TEMP_MIN = 0.6       # ✅ General - common config
TEMP_MAX = 0.8       # ✅ General - common config

# What is specific?
CONTENT_SPECIFIC_SETTING = "..."  # ✅ Specific - keep here
```

**Step 2**: Move general to top level
```python
# Move to src/startup.py
DEFAULT_AI_MODEL = "qwen3:32b"
AI_TEMPERATURE_MIN = 0.6
AI_TEMPERATURE_MAX = 0.8
```

**Step 3**: Import and use in lower level
```python
# In lower module - use top level
from src.startup import (
    DEFAULT_AI_MODEL,
    AI_TEMPERATURE_MIN,
    AI_TEMPERATURE_MAX
)

def get_model():
    return DEFAULT_AI_MODEL  # Uses top level
```

### For New Modules

**When creating new functionality:**

1. **Start at top level**: Is this general? → Add to `src/`
2. **If specific**: Create in appropriate `T/*/` path
3. **Import from top**: Use `from src.startup import ...`
4. **Never duplicate**: Always import, never copy-paste

## Verification

Run the comprehensive test to verify proper organization:

```bash
python3 test_startup_infrastructure.py
```

Expected output:
```
✅ PASSED: General Startup Module
✅ PASSED: Step 04 AI Config
✅ PASSED: Step 04 Integration

✓ Using top-level src.startup module (DEFAULT_AI_MODEL=qwen3:32b)
```

The line "Using top-level src.startup module" confirms that lower-level modules are properly using (not duplicating) top-level functionality.

## Summary

**Current State**: ✅ CORRECT
- **Top level** (`src/startup.py`): General DB + AI configuration
- **Lower level** (`T/Content/.../ai_config.py`): Wrapper that USES top level
- No duplication
- Single source of truth
- Easy to maintain

**Principle Applied**: Common things in top modules, specific functionality in lower modules.
