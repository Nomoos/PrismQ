# AI Configuration Placement - Final Structure

## Summary

AI configuration has been correctly placed at **T/src/** (PrismQ.T foundation level) because it is used across multiple Text domains (Content, Publishing, Story).

## Why T/src/ (Foundation Level)?

According to coding guidelines:
> "If logic is shared across multiple Text domains, move it up to PrismQ.T (or to PrismQ if fully cross-cutting)."

**Evidence of cross-domain usage:**
- `T/Content/From/Idea/Title/` - Uses AI for content generation
- `T/Publishing/SEO/Keywords/` - Uses AI for metadata generation  
- `T/Story/Review/` - Uses AI for story prompts
- Future Text domains will also use AI

**Not cross-cutting (PrismQ level):**
- AI is specific to Text domain
- Audio domain (PrismQ.A) would have its own AI config
- Database is at PrismQ level (truly cross-cutting)

## Module Hierarchy

```
PrismQ (src/)
├─ startup.py - Database config (cross-cutting across all domains)
└─ config.py - Environment config (cross-cutting)

PrismQ.T (T/src/)
├─ ai_config.py - AI config for Text domain ← SOURCE OF TRUTH
└─ __init__.py - Exports AI configuration

PrismQ.T.Content (T/Content/src/)
├─ ai_config.py - Re-exports from T/src (backward compatibility)
└─ __init__.py - Re-exports from T/src

PrismQ.T.Content.From.Idea.Title (T/Content/From/Idea/Title/src/)
├─ ai_config.py - Wrapper that uses T/src (backward compatibility)
└─ content_generator.py - Uses AI from T/src

PrismQ.T.Publishing.SEO.Keywords
└─ ai_metadata_generator.py - Uses AI (should use T/src)

PrismQ.T.Story.Review
└─ prompts.py - Uses AI (should use T/src)
```

## Usage Patterns

### Recommended (New Code)

```python
# Import directly from T foundation
from T.src.ai_config import AISettings, create_ai_config, check_ollama_available

def main():
    # Create AI config at composition root
    ai_settings = create_ai_config()
    
    # Check availability
    if not check_ollama_available():
        raise RuntimeError("Ollama not available")
    
    # Use in your domain logic
    model = ai_settings.get_model()
    temperature = ai_settings.get_random_temperature()
    api_base = ai_settings.get_api_base()
```

### Backward Compatible (Existing Code)

```python
# Via T/Content (re-exports from T/src)
from T.Content.src.ai_config import AISettings, create_ai_config

# Via Title module (wrappers)
from T.Content.From.Idea.Title.src.ai_config import get_local_ai_model
```

## Benefits of Current Structure

1. **Single Source of Truth**
   - AI config defined once at T/src/ai_config.py
   - All Text domains import from there
   - No duplication across modules

2. **Correct Abstraction Level**
   - T/src = Text foundation (shared by all Text domains)
   - Used by Content, Publishing, Story, etc.
   - Follows module hierarchy principles

3. **Easy to Maintain**
   - Change AI model: Edit one file (T/src/ai_config.py)
   - All Text domains automatically updated
   - Clear ownership and responsibility

4. **Follows Coding Guidelines**
   - Generic functionality at higher levels
   - Specialized functionality at lower levels
   - Dependencies flow: specialized → generic
   - No circular dependencies

## Files and Their Roles

### Source of Truth
- **T/src/ai_config.py** - Defines AI configuration for Text domain
  - Constants: `DEFAULT_AI_MODEL`, `AI_TEMPERATURE_MIN/MAX`
  - Classes: `AISettings`
  - Functions: `create_ai_config()`, `check_ollama_available()`

### Re-exporters (Backward Compatibility)
- **T/Content/src/ai_config.py** - Re-exports from T/src
- **T/Content/src/__init__.py** - Re-exports from T/src
- **T/Content/From/Idea/Title/src/ai_config.py** - Wrapper using T/src

### Module Exports
- **T/src/__init__.py** - Exports AI configuration for Text domain
- **src/__init__.py** - Exports database configuration (cross-cutting)

## Verification

Run `python3 test_ai_hierarchy.py` to verify:
- ✅ AI config exists at T/src (foundation level)
- ✅ T/Content re-exports from T/src
- ✅ Title module references T/src
- ✅ Single source of truth maintained

## Future Considerations

### When adding new Text domains:
```python
# New domain: T/Description/
from T.src.ai_config import AISettings, create_ai_config
# Uses foundation AI config automatically
```

### When adding Audio domain:
```python
# Audio would have its own AI config at A/src/ai_config.py
# Separate from Text domain
```

### Cross-cutting AI (unlikely):
If AI becomes needed by ALL domains (Text, Audio, Video), then move to:
- `src/ai_config.py` - Truly cross-cutting
- But currently AI is Text-specific

## Decision Tree

**Where should AI config be?**

1. Used across entire PrismQ (Text, Audio, Video)?
   → `src/ai_config.py` (PrismQ level)

2. Used across all Text domains (Content, Publishing, Story)?
   → `T/src/ai_config.py` (PrismQ.T foundation) ← **CURRENT**

3. Used only for Content generation?
   → `T/Content/src/ai_config.py` (PrismQ.T.Content)

4. Used only for Title generation?
   → `T/Content/From/Idea/Title/src/ai_config.py` (specific)

**Current placement is #2 because AI is used by multiple Text domains.**

## Conclusion

✅ **AI configuration is correctly placed at T/src/ (Text foundation level)**

This follows module hierarchy principles, eliminates duplication, and provides a single source of truth for all Text domain AI operations.
