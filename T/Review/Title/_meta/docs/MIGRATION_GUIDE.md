# Migration Guide: Adopting Modular Prompt Templates

This guide explains how to migrate existing title review modules to use the new modular prompt template system.

## Overview

The modular prompt system centralizes title review prompts in:
- **Location**: `T/Review/Title/_meta/prompts/`
- **API**: `T/Review/Title/prompts.py`
- **Benefits**: DRY principle, reusability, consistency, maintainability

## Affected Modules

The following modules can benefit from migrating to the modular system:

1. **T.Review.Title.From.Content.Idea** (`PrismQ.T.Review.Title.From.Content.Idea`)
   - Current: Uses hardcoded prompts or manual composition
   - Should use: `get_v1_review_prompt()` or `compose_review_prompt_with_idea()`

2. **T.Review.Title.From.Content** (`PrismQ.T.Review.Title.From.Content`)
   - Current: Uses separate prompt files in `_meta/prompts/`
   - Should use: `get_v2_review_prompt()` or `compose_review_prompt_content_only()`

## Migration Steps

### Step 1: Identify Current Prompt Usage

Look for:
- Direct file reads from `_meta/prompts/*.txt`
- String formatting or template substitution
- Hardcoded prompt text in code

Example (old approach):
```python
# Old: Reading from local prompt file
prompt_file = Path(__file__).parent / "_meta" / "prompts" / "title_review_v1.txt"
with open(prompt_file, 'r') as f:
    prompt_template = f.read()

prompt = prompt_template.format(
    title_text=title,
    content_text=content,
    idea_summary=idea,
    target_audience=audience
)
```

### Step 2: Replace with Modular API

Example (new approach):
```python
# New: Using modular prompt API
from T.Review.Title.prompts import get_v1_review_prompt

prompt = get_v1_review_prompt(
    title_text=title,
    content_text=content,
    idea_summary=idea,
    target_audience=audience
)
```

### Step 3: Update Tests

Update test imports and verify functionality:

```python
# Old imports
from T.Review.Title.From.Content._meta.prompts import ...

# New imports
from T.Review.Title.prompts import (
    get_v1_review_prompt,
    get_v2_review_prompt,
    compose_comparison_prompt
)
```

### Step 4: Verify Behavior

Run existing tests to ensure:
- Prompt composition works correctly
- No unresolved placeholders
- AI responses remain consistent
- JSON output parsing still works

## Module-Specific Migration

### T.Review.Title.From.Content.Idea

**Current State:**
- Implements `review_title_by_content_and_idea()` function
- Uses `by_content_and_idea.py` implementation
- May have hardcoded or manual prompt composition

**Migration:**
```python
# In T/Review/Title/From/Content/Idea/by_content_and_idea.py
from T.Review.Title.prompts import get_v1_review_prompt

def review_title_by_content_and_idea(
    title_text: str,
    content_text: str,
    idea_summary: str,
    # ... other params
):
    # Generate prompt using modular system
    prompt = get_v1_review_prompt(
        title_text=title_text,
        content_text=content_text,
        idea_summary=idea_summary,
        target_audience=target_audience or ""
    )
    
    # Send to AI model
    # ... rest of implementation
```

### T.Review.Title.From.Content

**Current State:**
- Implements `review_title_by_content_v2()` function
- Has separate prompt files in `_meta/prompts/`
- Uses `by_content_v2.py` implementation

**Migration:**
```python
# In T/Review/Title/From/Content/by_content_v2.py
from T.Review.Title.prompts import get_v2_review_prompt, compose_comparison_prompt

def review_title_by_content_v2(
    title_text: str,
    content_text: str,
    # ... other params
):
    # Generate prompt using modular system
    prompt = get_v2_review_prompt(
        title_text=title_text,
        content_text=content_text
    )
    
    # Send to AI model
    # ... rest of implementation
```

## Custom Weights Example

If a module needs different evaluation weights:

```python
from T.Review.Title.prompts import compose_review_prompt_content_only

# Define custom weights
custom_weights = {
    "content_weight": 50,  # Higher emphasis on content
    "engagement_weight": 30,
    "seo_weight": 20,
}

# Use custom weights
prompt = compose_review_prompt_content_only(
    title_text=title,
    content_text=content,
    weights=custom_weights
)
```

## Comparison Prompts

For version comparison (v1 vs v2, v2 vs v3, etc.):

```python
from T.Review.Title.prompts import compose_comparison_prompt

prompt = compose_comparison_prompt(
    title_current="Enhanced Title v2",
    title_previous="Original Title v1",
    content_text=content,
    score_current=78,
    score_previous=65,
    feedback_previous="Previous review feedback..."
)
```

## Backward Compatibility

The modular system maintains compatibility with existing code:

### Option 1: Drop-in Replacement
Replace local prompt files with API calls (minimal changes)

### Option 2: Gradual Migration
Keep existing code working while adding new features that use modular prompts

### Option 3: Deprecation Path
1. Mark old prompt files as deprecated
2. Add warnings when old methods are used
3. Provide migration timeline
4. Remove old files after migration complete

## Testing Migration

### Before Migration
```bash
# Run existing tests
cd /home/runner/work/PrismQ/PrismQ
python3 -m pytest T/Review/Title/From/Content/_meta/tests/ -v
python3 -m pytest T/Review/Title/From/Content/Idea/_meta/tests/ -v
```

### After Migration
```bash
# Verify modular prompts work
python3 -m pytest T/Review/Title/_meta/tests/test_prompts.py -v

# Verify existing functionality unchanged
python3 -m pytest T/Review/Title/From/Content/_meta/tests/ -v
python3 -m pytest T/Review/Title/From/Content/Idea/_meta/tests/ -v
```

## Benefits of Migration

1. **DRY Principle**: No duplicated evaluation criteria
2. **Single Source of Truth**: One place to update prompts
3. **Consistency**: Same evaluation approach across modules
4. **Flexibility**: Easy to customize weights and contexts
5. **Maintainability**: Centralized prompt management
6. **Testability**: Comprehensive test coverage

## Troubleshooting

### Issue: Import errors

**Solution**: Ensure Python path includes project root
```python
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))
```

### Issue: Unresolved placeholders in prompts

**Solution**: Check that all required parameters are provided
```python
# This will raise an error if variables aren't provided
prompt = get_v1_review_prompt(
    title_text=title,        # Required
    content_text=content,    # Required
    idea_summary=idea,       # Required
    target_audience=audience # Optional, defaults to "General audience"
)
```

### Issue: Tests fail after migration

**Solution**: 
1. Check prompt composition logic
2. Verify weights match expected values
3. Ensure JSON output format unchanged
4. Compare old vs new prompt outputs

## Next Steps

After migrating to modular prompts:

1. **Remove duplicate prompt files** in module-specific `_meta/prompts/` directories
2. **Update module READMEs** to reference central prompt system
3. **Add migration notes** in CHANGELOG
4. **Document custom usage** for module-specific needs

## Support

For questions or issues:
- See: `T/Review/Title/_meta/prompts/README.md`
- Examples: `T/Review/Title/_meta/examples/modular_prompt_usage.py`
- Tests: `T/Review/Title/_meta/tests/test_prompts.py`
- API: `T/Review/Title/prompts.py`

## Timeline (Suggested)

1. **Phase 1**: Adopt modular prompts in new code (✅ Complete)
2. **Phase 2**: Migrate T.Review.Title.From.Content.Idea (Pending)
3. **Phase 3**: Migrate T.Review.Title.From.Content (Pending)
4. **Phase 4**: Remove duplicate prompt files (After verification)
5. **Phase 5**: Update all documentation (Final step)
