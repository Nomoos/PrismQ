# General Startup Infrastructure Implementation

## Problem Statement

Create a general startup for most of the scripts where:
- Database connection is needed
- Ollama local AI is needed

Also analyze and address requirements from PR #267.

## Solution Implemented

### 1. General Startup Module (`src/startup.py`)

Created a centralized startup module that provides reusable functions for:

#### Database Configuration
- `get_database_path(config=None)` - Returns the path to the shared database (db.s3db)
- Works with existing `Config` class from `src/config.py`
- Can be used across all scripts for consistent database access

#### AI Configuration (Ollama)
- `get_local_ai_model()` - Returns fixed model name: `qwen3:32b`
- `get_local_ai_temperature()` - Returns random temperature between 0.6 and 0.8
- `get_local_ai_api_base()` - Returns Ollama API URL: `http://localhost:11434`
- `get_local_ai_config()` - Returns complete config tuple (model, temperature, api_base)

#### Ollama Availability
- `check_ollama_available(api_base, model, timeout)` - Checks if Ollama is running
- Verifies model availability
- Graceful failure handling

#### Environment Initialization
- `initialize_environment(check_ai, interactive)` - One-call setup for DB + AI
- Returns Config instance and AI availability status

### 2. AI Config Module for Step 04

Created `T/Script/From/Idea/Title/src/ai_config.py` that:
- Re-exports functions from `src.startup` for convenience
- Provides local AI configuration specific to Step 04
- Maintains consistency with global configuration approach

### 3. Step 04 Refactoring (Content Generation)

Updated implementation to match PR #267 requirements:

#### Updated `script_generator.py`:
- **Removed**: `platform_target`, `structure_type`, `tone` from `ScriptGeneratorConfig`
- **Removed**: `structure_type`, `platform_target` from `ScriptV1` dataclass
- **Added**: `audience` configuration to `ScriptGeneratorConfig` (Age 13-23, Female, USA)
- **Added**: `max_duration_seconds` (175s) and updated `target_duration_seconds` (120s)
- **Added**: `audience` dict to `ScriptV1` dataclass
- **Updated**: Uses global AI functions via `ai_config` module
- **Updated**: Multiplatform approach (not tied to specific platforms)

#### Updated `ai_script_generator.py`:
- **Removed**: `platform` and `tone` parameters from `generate_content()`
- **Removed**: `_get_platform_instructions()` method (no longer needed)
- **Added**: `audience` parameter to `generate_content()`
- **Added**: `max_duration_seconds` parameter (default: 175s)
- **Updated**: `target_duration_seconds` default from 90s to 120s
- **Completely rewrote**: `_create_content_prompt()` with optimized structure for local models

#### New Prompt Structure:
```
SYSTEM INSTRUCTION:
You are a professional video script writer.
Follow instructions exactly. Do not add extra sections or explanations.

TASK:
Generate a video script.

INPUTS:
TITLE: [Title]
IDEA: [Idea]
INSPIRATION SEED: [Single word used only as creative inspiration]

TARGET AUDIENCE:
- Age: 13–23
- Gender: Female
- Country: United States

REQUIREMENTS:
1. Hook must strongly capture attention within the first 5 seconds.
2. Deliver the main idea clearly and coherently.
3. End with a clear and natural call-to-action.
4. Maintain consistent engaging tone throughout.
5. Use the inspiration seed subtly (symbolic or thematic, not literal repetition).

OUTPUT RULES:
- Output ONLY the script text.
- No headings, no labels, no explanations.
- Do not mention the word "hook", "CTA", or any structure explicitly.
- The first sentence must create immediate curiosity or tension.
```

## Benefits

### Reusability
- Any script can now import and use database/AI configuration functions
- Consistent configuration across all modules
- Similar pattern to existing database utilities

### Maintainability
- Single source of truth for AI model configuration
- Easy to update AI model or settings globally
- Clear separation of concerns

### Flexibility
- Random temperature for creative variety
- Configurable timeout and other parameters
- Easy to extend with additional configuration

### Testability
- Functions can be tested independently
- Mock-friendly design
- Clear interfaces

## Usage Examples

### For New Scripts

```python
from src.startup import (
    get_database_path,
    get_local_ai_config,
    check_ollama_available
)

# Get database path
db_path = get_database_path()

# Check if AI is available
if not check_ollama_available():
    print("ERROR: Ollama is not available!")
    exit(1)

# Get AI configuration
model, temperature, api_base = get_local_ai_config()

# Use in your script...
```

### For Step 04 (Content Generation)

```python
from T.Script.From.Idea.Title.src.ai_config import (
    get_local_ai_model,
    get_local_ai_temperature
)

# Get model and temperature
model = get_local_ai_model()  # qwen3:32b
temp = get_local_ai_temperature()  # Random 0.6-0.8

# Configuration is now centralized and consistent
```

## Migration Path for Existing Scripts

Old approach:
```python
db_path = "C:/PrismQ/db.s3db"  # Hardcoded
ai_model = "qwen3:32b"  # Hardcoded
ai_temp = 0.7  # Hardcoded
```

New approach:
```python
from src.startup import get_database_path, get_local_ai_config

db_path = get_database_path()  # Centralized
ai_model, ai_temp, api_base = get_local_ai_config()  # Centralized
```

## Files Created/Modified

### Created:
1. `src/startup.py` - Main startup utilities module
2. `src/STARTUP_README.md` - Comprehensive documentation
3. `T/Script/From/Idea/Title/src/ai_config.py` - Step 04 AI config wrapper

### Modified:
4. `src/__init__.py` - Export new startup functions
5. `T/Script/From/Idea/Title/src/script_generator.py` - Use global AI config
6. `T/Script/From/Idea/Title/src/ai_script_generator.py` - New prompt structure

## Alignment with PR #267

This implementation addresses the PR #267 requirements:
- ✅ Global AI configuration (similar to database path pattern)
- ✅ Multiplatform approach (removed platform-specific targeting)
- ✅ Audience targeting (Age 13-23, Female, USA)
- ✅ Duration updates (120s target, 175s max)
- ✅ Optimized prompt structure for local models
- ✅ Removed platform/structure/tone parameters

## Testing

All functions have been tested and verified:
- Database path retrieval works
- AI configuration functions return correct values
- Ollama availability check works (returns False when not running)
- AI config module correctly re-exports from startup
- Random temperature generates values in expected range (0.6-0.8)

## Next Steps (Optional)

While not part of the core requirement, additional improvements could include:
1. Rename T/Script → T/Content directory structure (mentioned in PR comments)
2. Update test files to match new structure
3. Update documentation folder names
4. Document Title table schema in detail

These are tracked in the PR #267 checklist.

## Conclusion

The general startup infrastructure is now in place and provides:
- Reusable database configuration for all scripts
- Centralized Ollama local AI configuration
- Consistent approach across modules
- Easy to use and maintain

The implementation follows existing patterns (like `Config` class) and integrates seamlessly with the current codebase.
