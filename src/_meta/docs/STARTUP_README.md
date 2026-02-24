# Startup Module Documentation

## Overview

The `src/startup.py` module provides reusable functions for database connection and Ollama local AI configuration that can be used across all scripts in the PrismQ system.

## Purpose

This module was created to:
- Centralize database path configuration
- Provide global AI model configuration (similar to how database paths are handled)
- Enable consistent Ollama integration across all modules
- Reduce code duplication across different scripts

## Core Functions

### Database Configuration

#### `get_database_path(config=None)`

Returns the absolute path to the PrismQ database file (db.s3db).

```python
from src.startup import get_database_path

db_path = get_database_path()
print(db_path)  # C:/PrismQ/db.s3db (or your configured path)
```

### AI Configuration (Ollama)

#### `get_local_ai_model()`

Returns the fixed model name for local AI operations.

```python
from src.startup import get_local_ai_model

model = get_local_ai_model()
print(model)  # qwen3:32b
```

#### `get_local_ai_temperature()`

Returns a random temperature between 0.6 and 0.8 for creative variety while maintaining coherent output.

```python
from src.startup import get_local_ai_temperature

temp = get_local_ai_temperature()
print(f"{temp:.2f}")  # Random value like 0.67
```

#### `get_local_ai_api_base()`

Returns the Ollama API base URL.

```python
from src.startup import get_local_ai_api_base

api_base = get_local_ai_api_base()
print(api_base)  # http://localhost:11434
```

#### `get_local_ai_config()`

Convenience function that returns all AI configuration parameters in one call.

```python
from src.startup import get_local_ai_config

model, temperature, api_base = get_local_ai_config()
print(f"Model: {model}, Temp: {temperature:.2f}, API: {api_base}")
# Model: qwen3:32b, Temp: 0.72, API: http://localhost:11434
```

### Ollama Availability Check

#### `check_ollama_available(api_base=None, model=None, timeout=5)`

Checks if Ollama is running and the specified model is available.

```python
from src.startup import check_ollama_available

if check_ollama_available():
    print("Ollama is ready!")
else:
    print("Ollama is not available")
```

### Environment Initialization

#### `initialize_environment(check_ai=True, interactive=False)`

Convenience function that initializes the PrismQ environment with database and AI checks.

```python
from src.startup import initialize_environment

config, ai_available = initialize_environment()
if not ai_available:
    print("Warning: Ollama not available!")

db_path = config.database_path
```

## Usage Examples

### Basic Script Setup

```python
#!/usr/bin/env python3
"""Example script using startup utilities."""

from src.startup import (
    get_database_path,
    get_local_ai_config,
    check_ollama_available
)

# Get database path
db_path = get_database_path()
print(f"Using database: {db_path}")

# Check if AI is available
if not check_ollama_available():
    print("ERROR: Ollama is not available!")
    exit(1)

# Get AI configuration
model, temperature, api_base = get_local_ai_config()
print(f"AI Config: {model} @ {temperature:.2f}")

# Your script logic here...
```

### Using with AI Script Generator

```python
from T.Script.From.Idea.Title.src.ai_config import (
    get_local_ai_model,
    get_local_ai_temperature
)

# These functions re-export from src.startup for convenience
model = get_local_ai_model()  # qwen3:32b
temp = get_local_ai_temperature()  # Random 0.6-0.8
```

### Full Environment Setup

```python
from src.startup import initialize_environment

# Initialize with AI check
config, ai_available = initialize_environment(check_ai=True, interactive=False)

if ai_available:
    print("✓ Environment ready (DB + AI)")
else:
    print("✓ Environment ready (DB only)")
    print("⚠ Ollama not available")
```

## Design Philosophy

The startup module follows these principles:

1. **Global Configuration**: Similar to how database paths are configured globally, AI configuration is now centralized
2. **Reusability**: Functions can be imported and used by any script in the PrismQ system
3. **Simplicity**: Simple function calls with sensible defaults
4. **Consistency**: All scripts use the same AI model and configuration approach
5. **Non-interactive by Default**: Suitable for automated workflows and batch processing

## Configuration

The functions use the existing `Config` class from `src/config.py` for database configuration. AI configuration is hardcoded as follows:

- **Model**: `qwen3:32b` (fixed)
- **Temperature**: Random between `0.6` and `0.8` (for variety)
- **API Base**: `http://localhost:11434` (Ollama default)
- **Timeout**: Configurable per request

To change these defaults, edit the functions in `src/startup.py`.

## Module Integration

All new scripts should use these functions for consistency:

```python
# Old approach (deprecated)
db_path = "C:/PrismQ/db.s3db"  # Hardcoded
ai_model = "qwen3:32b"  # Hardcoded
ai_temp = 0.7  # Hardcoded

# New approach (recommended)
from src.startup import get_database_path, get_local_ai_config

db_path = get_database_path()  # Centralized
ai_model, ai_temp, api_base = get_local_ai_config()  # Centralized
```

## See Also

- `src/config.py` - Main configuration class
- `src/idea.py` - Idea database utilities
- `src/story.py` - Story database utilities
- `T/Script/From/Idea/Title/src/ai_config.py` - Step 04 AI configuration wrapper
