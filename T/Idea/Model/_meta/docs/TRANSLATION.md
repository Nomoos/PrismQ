# Multi-Language Story Translation Guide

Complete guide for implementing multi-language story translations with AI-driven feedback loop.

## Overview

The PrismQ.T module now supports multi-language story translations with a controlled feedback loop between AI Translator and AI Reviewer. This ensures translated Title and Text maintain the same meaning as the original while allowing for minor length differences (video timing can be adjusted).

## Architecture

### Database Design

Following best practices for multi-language content management:

**One Story ID with Multiple Language Rows**
- Each story has a single `story_id` in the `ideas` table
- Translations are stored in the `story_translations` table
- Composite key: `(story_id, language_code)` ensures uniqueness
- Original language designated in `ideas.original_language` field

**Schema:**

```sql
-- ideas table (extended)
CREATE TABLE ideas (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    concept TEXT NOT NULL,
    -- ... other fields ...
    original_language TEXT DEFAULT 'en',  -- ISO 639-1 code
    -- ... metadata fields ...
);

-- story_translations table
CREATE TABLE story_translations (
    id INTEGER PRIMARY KEY,
    story_id INTEGER NOT NULL,           -- Links to ideas.id
    language_code TEXT NOT NULL,          -- ISO 639-1 (en, cs, es, etc.)
    title TEXT NOT NULL,                  -- Translated title
    text TEXT NOT NULL,                   -- Translated story text
    
    -- Translation Process
    status TEXT DEFAULT 'draft',          -- Workflow status
    iteration_count INTEGER DEFAULT 0,    -- Feedback iterations
    max_iterations INTEGER DEFAULT 2,     -- Loop limit
    translator_id TEXT,                   -- AI Translator identifier
    reviewer_id TEXT,                     -- AI Reviewer identifier
    
    -- Feedback Loop
    feedback_history TEXT,                -- JSON: list of feedback
    last_feedback TEXT,                   -- Summary of last feedback
    meaning_verified INTEGER DEFAULT 0,   -- Boolean: meaning matches
    
    -- Metadata
    translated_from TEXT DEFAULT 'en',    -- Source language
    version INTEGER DEFAULT 1,            -- Translation version
    created_at TEXT,
    updated_at TEXT,
    approved_at TEXT,
    published_at TEXT,
    notes TEXT,
    
    FOREIGN KEY (story_id) REFERENCES ideas(id) ON DELETE CASCADE,
    UNIQUE(story_id, language_code)
);
```

## Translation Workflow

### Step-by-Step Process

**1. Create Original Story**

```python
from src.idea import Idea, ContentGenre
from src.idea_db import IdeaDatabase

# Create database
db = IdeaDatabase("stories.db")
db.connect()
db.create_tables()

# Create original story (English)
story = Idea(
    title="The Echo",
    concept="A girl hears her own voice from the future",
    synopsis="A teenage girl starts hearing a voice identical to her own...",
    original_language="en",  # Designate original language
    genre=ContentGenre.HORROR,
    length_target="60 seconds video / 500 words text"
)

story_id = db.insert_idea(story.to_dict())
```

**2. Create Translation**

```python
from src.story_translation import StoryTranslation, TranslationStatus

# AI Translator creates Czech translation
czech_translation = StoryTranslation(
    story_id=story_id,
    language_code="cs",
    title="Echo",
    text="Teenager objeví, že může slyšet svůj budoucí hlas...",
    translator_id="AI-Translator-GPT4",
    translated_from="en"
)

db.insert_translation(czech_translation.to_dict())
```

**3. Submit for Review**

```python
# Mark ready for review
czech_translation.submit_for_review()
db.update_translation(story_id, "cs", czech_translation.to_dict())
```

**4. AI Reviewer Checks Translation**

```python
# Retrieve translation for review
trans_dict = db.get_translation(story_id, "cs")
translation = StoryTranslation.from_dict(trans_dict)

# AI Reviewer compares to original
# - Checks if meaning is preserved
# - Verifies tone matches
# - Ensures key facts are present
# - Length differences are acceptable

# If issues found:
translation.add_feedback(
    reviewer_id="AI-Reviewer-Claude",
    issues=[
        "Opening line lacks suspense of original",
        "Technical term 'echo' not translated consistently"
    ],
    suggestions=[
        "Add ominous tone to first sentence",
        "Use 'ozvěna' throughout instead of mixing terms"
    ],
    meaning_score=75,  # 0-100 score
    notes="Good attempt but needs revision for tone"
)

db.update_translation(story_id, "cs", translation.to_dict())
```

**5. Feedback Loop - Translator Revises**

```python
# Translator retrieves feedback
trans_dict = db.get_translation(story_id, "cs")
translation = StoryTranslation.from_dict(trans_dict)

# Check if can request revision
if translation.can_request_revision():
    # Update content based on feedback
    translation.update_content(
        text="Teenager zjistí, že slyší svůj budoucí hlas - varující ji před smrtí..."
    )
    
    translation.submit_for_review()
    db.update_translation(story_id, "cs", translation.to_dict())
else:
    print(f"Max iterations ({translation.max_iterations}) reached")
```

**6. Second Review - Approval**

```python
# Retrieve for second review
trans_dict = db.get_translation(story_id, "cs")
translation = StoryTranslation.from_dict(trans_dict)

# AI Reviewer checks again
translation.add_feedback(
    reviewer_id="AI-Reviewer-Claude",
    issues=[],  # No issues found
    suggestions=[],
    meaning_score=93,
    notes="Perfect! Suspense and meaning preserved."
)

db.update_translation(story_id, "cs", translation.to_dict())

# Translation automatically approved (meaning_score >= 85 and no issues)
assert translation.status == TranslationStatus.APPROVED
assert translation.meaning_verified == True
```

**7. Publish Translation**

```python
trans_dict = db.get_translation(story_id, "cs")
translation = StoryTranslation.from_dict(trans_dict)

translation.publish()
db.update_translation(story_id, "cs", translation.to_dict())

print(f"Czech translation published at: {translation.published_at}")
```

## Translation Feedback Loop

### Solving the Feedback Loop

The feedback loop is **solved** by making it **finite and goal-driven**:

**1. Maximum Iterations**
- Default: 2 iterations (configurable via `max_iterations`)
- Prevents infinite loops
- Forces decision after limited revisions

**2. Automatic Approval Criteria**
- No issues found (`len(issues) == 0`)
- AND meaning score ≥ 85
- Automatically sets `status = APPROVED` and `meaning_verified = True`

**3. Iteration Tracking**
- `iteration_count` increments with each feedback
- `can_request_revision()` checks against `max_iterations`
- External workflow respects the limit

**Example Loop:**

```python
# Iteration 1: First review finds issues
translation.add_feedback(
    reviewer_id="AI-Reviewer",
    issues=["Issue 1", "Issue 2"],
    suggestions=["Fix 1", "Fix 2"],
    meaning_score=75
)
# Result: status = REVISION_NEEDED, iteration_count = 1

# Translator revises, submits again

# Iteration 2: Still needs work
translation.add_feedback(
    reviewer_id="AI-Reviewer",
    issues=["Issue 3"],
    suggestions=["Fix 3"],
    meaning_score=82
)
# Result: status = REVISION_NEEDED, iteration_count = 2

# Check if can continue
if not translation.can_request_revision():
    # Max reached - escalate to manual review or accept as-is
    print("Maximum iterations reached. Escalating to human reviewer.")
```

### Reviewer Focus

To keep feedback loop efficient:

**Focus on Critical Issues:**
- Meaning deviations (facts wrong, intent lost)
- Tone mismatches (serious vs. casual)
- Missing key elements (names, numbers, calls to action)
- Terminology inconsistencies

**Ignore Minor Differences:**
- Stylistic variations
- Length differences (video can be stretched)
- Word-for-word matching (not required)
- Grammar nuances (if meaning clear)

## Multi-Language Management

### Referencing Same Story Across Languages

All translations share the same `story_id`:

```python
# Original English story
story_id = 42

# Czech translation
czech = StoryTranslation(story_id=42, language_code="cs", ...)

# Spanish translation
spanish = StoryTranslation(story_id=42, language_code="es", ...)

# German translation  
german = StoryTranslation(story_id=42, language_code="de", ...)

# All reference the same story
assert czech.story_id == spanish.story_id == german.story_id
```

### Querying Available Languages

```python
# Get all available languages for a story
languages = db.get_available_languages(story_id=42)
print(languages)  # ['cs', 'de', 'es']

# Get all translations
translations = db.get_all_translations(story_id=42)
for trans in translations:
    print(f"{trans['language_code']}: {trans['title']} ({trans['status']})")
```

### Using Original Language

```python
# Retrieve original story
original = db.get_idea(story_id)
original_lang = original['original_language']  # 'en'

# Translator can use original as reference
original_text = original['synopsis']  # or full script text

# When translating to new language
french = StoryTranslation(
    story_id=story_id,
    language_code="fr",
    title="L'Écho",
    text="Une adolescente découvre...",
    translated_from=original_lang  # Reference original
)
```

### Translation Context for AI

When providing context to AI Translator:

```python
# Get original story
original_story = db.get_idea(story_id)

# Get existing translations (for consistency)
existing_translations = db.get_all_translations(story_id)

# Build context for translator
context = {
    "original_language": original_story['original_language'],
    "original_title": original_story['title'],
    "original_text": original_story['synopsis'],  # or full text
    "tone_guidance": original_story['tone_guidance'],
    "existing_translations": [
        {
            "language": t['language_code'],
            "title": t['title']
        }
        for t in existing_translations
    ]
}

# AI Translator uses this context to ensure consistency
```

## Best Practices

### 1. Designate Original Language

Always set `original_language` when creating story:

```python
idea = Idea(
    title="...",
    concept="...",
    original_language="en",  # ISO 639-1 code
    ...
)
```

### 2. Use ISO 639-1 Language Codes

Standard 2-letter codes:
- `en` - English
- `cs` - Czech
- `es` - Spanish
- `de` - German
- `fr` - French
- `ja` - Japanese
- `zh` - Chinese
- etc.

### 3. Set Appropriate Max Iterations

```python
# For high-quality content
translation = StoryTranslation(
    ...,
    max_iterations=3  # Allow more refinement
)

# For rapid production
translation = StoryTranslation(
    ...,
    max_iterations=1  # Single review pass
)
```

### 4. Track Translation Quality

```python
# Get translations needing review
pending = db.get_translations_by_status("pending_review")

# Get translations needing revision
needs_work = db.get_translations_by_status("revision_needed")

# Monitor feedback scores
for trans_dict in db.get_all_translations(story_id):
    if trans_dict['feedback_history']:
        latest = trans_dict['feedback_history'][-1]
        score = latest.get('meaning_score', 0)
        print(f"{trans_dict['language_code']}: {score}/100")
```

### 5. Maintain Translation Consistency

Use existing translations as reference:

```python
# When translating to new language, reference existing ones
existing = db.get_all_translations(story_id)

context_for_ai = f"""
Original (en): {original_title}
Czech (cs): {existing[0]['title']}
Spanish (es): {existing[1]['title']}

Please translate to German maintaining consistency with existing translations.
"""
```

## Video Timing Considerations

From the problem statement:

> Length doesn't matter because we can stretch video, just keep it under 3 minutes for every language, so in original took appropriate reserve.

**Guidelines:**

1. **Original Content**: Leave room for expansion in translations (~20% reserve)
2. **Translations**: Aim for similar length but focus on meaning preservation
3. **Maximum Length**: Keep all versions under 3 minutes (or specified target)
4. **Video Adjustment**: Production can stretch/compress video to match audio

```python
idea = Idea(
    title="...",
    concept="...",
    length_target="60-90 seconds (reserve for translations)",
    ...
)
```

## Database Maintenance

### Cascade Deletion

Translations are automatically deleted when story is deleted:

```python
# Delete story
db.delete_idea(story_id)

# All translations automatically deleted via CASCADE
assert len(db.get_available_languages(story_id)) == 0
```

### Backup Translations

```python
import json

# Export translations for backup
translations = db.get_all_translations(story_id)

with open(f"story_{story_id}_translations.json", "w") as f:
    json.dump(translations, f, indent=2, ensure_ascii=False)
```

## Integration with PrismQ Workflow

### Position in Workflow

```
IdeaInspiration → Idea → Script → Review → TextPublishing
                                               ↓
                                         PublishedText (original)
                                               ↓
                                    ┌──────────┴──────────┐
                                    ↓                     ↓
                              Translation            Translation
                              (Language 1)           (Language 2)
                                    ↓                     ↓
                              Feedback Loop         Feedback Loop
                                    ↓                     ↓
                              Published             Published
```

### Multiple Format Publishing

Each language translation can be published in multiple formats:

```python
# Original idea supports multiple formats
idea = Idea(
    title="...",
    target_platforms=["youtube", "tiktok", "medium"],
    target_formats=["text", "audio", "video"],
    original_language="en"
)

# Each translation inherits multi-format capability
# Czech version → text (blog), audio (podcast), video (YouTube)
# Spanish version → text (blog), audio (podcast), video (YouTube)
# etc.
```

## API Reference

See individual module documentation:
- [`src/story_translation.py`](../src/story_translation.py) - StoryTranslation model
- [`src/idea_db.py`](../src/idea_db.py) - Database methods
- [`src/idea.py`](../src/idea.py) - Extended Idea model

## Example Scripts

See [`_meta/examples/`](../examples/) for:
- `translation_workflow.py` - Complete workflow example
- `batch_translate.py` - Batch translation script
- `quality_report.py` - Translation quality monitoring

## Testing

Run translation tests:

```bash
# All tests
pytest _meta/tests/

# Translation model tests
pytest _meta/tests/test_story_translation.py

# Database tests
pytest _meta/tests/test_translation_db.py

# Integration tests
pytest _meta/tests/test_translation_db.py::TestCompleteTranslationWorkflow
```

## Troubleshooting

### Issue: Feedback loop doesn't stop

**Solution**: Check `max_iterations` is set and `can_request_revision()` is respected:

```python
if translation.can_request_revision():
    # Continue loop
else:
    # Stop and escalate
```

### Issue: Foreign key constraint fails

**Solution**: Ensure foreign keys are enabled:

```python
db = IdeaDatabase("stories.db")
db.connect()
# Foreign keys enabled automatically in connect()
```

### Issue: Can't retrieve translation

**Solution**: Verify story_id and language_code match exactly:

```python
# Check available languages
langs = db.get_available_languages(story_id)
print(f"Available: {langs}")

# Use exact code
trans = db.get_translation(story_id, "cs")  # Not "CS" or "cz"
```

## See Also

- [Database Guide](DATABASE.md) - Database operations
- [Idea Model Guide](FIELDS.md) - Idea model fields
- [Quick Start](QUICK_START.md) - Getting started guide
