# T/Content/From/Idea/Title - AI Content Generation

**Namespace**: `PrismQ.T.Content.From.Idea.Title`

Generate content drafts from idea and title using **local AI models only**.

## Purpose

Create content (v1) from the original idea and title using Qwen3:32b via Ollama.

**ALL generation goes through local AI models. No fallback to rule-based generation.**

## 🤖 AI-Powered Content Generation

### Input to AI
- **Title** (Titulek) - the content title
- **Idea text** - concept, synopsis, premise from the Idea object  
- **Seed** - one word randomly picked from 500 predefined variations (e.g., "pudding", "fire", "ocean", "Chicago", "Germany", "chill")

### Features
- **Qwen3:32b Model**: High-quality content generation
- **500 Seed Variations**: Simple words for creative inspiration (food, places, feelings, colors, etc.)
- **Platform Optimization**: YouTube Shorts, TikTok, Instagram Reels
- **No Fallback**: Error if AI unavailable (ensures AI is always used)
- **Production Ready**: Comprehensive validation, error handling, logging, and security

## Production Readiness Features

### ✅ Parameter Validation
- **Title**: Max 500 characters, non-empty
- **Idea text**: Max 10,000 characters, non-empty
- **Duration**: Positive values, target ≤ max
- **Configuration**: All parameters validated before generation

### ✅ Error Handling & Resilience
- Specific exceptions for different failure modes (timeout, connection, HTTP errors)
- Detailed error messages with actionable information
- Proper error propagation with context
- Empty response validation
- AI availability checks before generation

### ✅ Logging & Observability
- Debug logging for API calls (model, temperature, URL)
- Character count logging for generated content
- Warning for short generated content (< 50 chars)
- Error logging with full context
- Story processing tracking with IDs

### ✅ Idempotency
- Checks prevent duplicate content generation
- Story service validates content_id before generation
- Safe re-runs without duplicate work

### ✅ Security
- Input sanitization prevents injection attacks
- Null byte removal from inputs
- UTF-8 encoding validation
- Length limits on all text inputs
- No secrets logged (only metadata)

### ✅ Performance & Scalability
- Configurable timeouts (default: 120s)
- Connection error handling
- Proper timeout exceptions
- AI model availability caching

## Quick Start

```python
from T.Content.From.Idea.Title.src import (
    ContentGenerator,
    ContentGeneratorConfig,
    PlatformTarget,
    ContentStructure,
    ContentTone,
    generate_content,
    get_random_seed,
    SEED_VARIATIONS
)

# Option 1: Use ContentGenerator (requires Idea object)
config = ContentGeneratorConfig(
    platform_target=PlatformTarget.YOUTUBE_MEDIUM,
    target_duration_seconds=90,
    structure_type=ContentStructure.HOOK_DELIVER_CTA,
    tone=ContentTone.ENGAGING
)
generator = ContentGenerator(config=config)
content = generator.generate_content_v1(idea, title)

# Option 2: Use generate_content directly (simpler)
content_text = generate_content(
    title="The Mystery of the Abandoned House",
    idea_text="A girl discovers a time-loop in an abandoned house",
    target_duration_seconds=90,
    seed="midnight"  # Optional: specify seed, otherwise random
)

# Check available seeds
print(f"Total seeds: {len(SEED_VARIATIONS)}")  # 500
print(f"Random seed: {get_random_seed()}")  # e.g., "ocean"
```

## Seed Variations

The module includes ~500 simple seed words organized by category:

| Category | Examples |
|----------|----------|
| Food & Drinks | pudding, chocolate, coffee, honey, cheese |
| Elements & Nature | fire, water, ocean, mountain, forest |
| Family & People | sister, brother, mother, friend, hero |
| US Cities | Chicago, New York, Los Angeles, Miami |
| Countries | Germany, Japan, France, Brazil, Egypt |
| Continents | Asia, Europe, Africa, America |
| Feelings & Moods | chill, warm, happy, sad, brave |
| Time & Seasons | morning, midnight, spring, winter |
| Colors | red, blue, golden, crimson, azure |
| Animals | lion, eagle, dolphin, dragon, phoenix |
| Objects | mirror, clock, sword, crown, candle |
| Abstract | dream, secret, magic, destiny, freedom |

## Configuration

```python
# ContentGeneratorConfig - Full configuration
config = ContentGeneratorConfig(
    platform_target=PlatformTarget.YOUTUBE_MEDIUM,
    target_duration_seconds=90,
    max_duration_seconds=175,
    structure_type=ContentStructure.HOOK_DELIVER_CTA,
    tone=ContentTone.ENGAGING,
    audience={
        "age_range": "13-23",
        "gender": "Female",
        "country": "United States"
    },
    words_per_second=2.5,
    include_cta=True
)

# AIContentGeneratorConfig (for direct AI use)
ai_config = AIContentGeneratorConfig(
    model="qwen3:32b",
    api_base="http://localhost:11434",
    temperature=0.7,
    max_tokens=2000,
    timeout=120
)
```

## Error Handling

AI is **required**. Comprehensive error handling for production use:

```python
from T.Content.From.Idea.Title.src import ContentGenerator

generator = ContentGenerator()

# Check availability
if not generator.is_ai_available():
    print("ERROR: Start Ollama with: ollama run qwen3:32b")

# Generation with proper error handling
try:
    content = generator.generate_content_v1(idea, title)
except ValueError as e:
    print(f"Invalid parameters: {e}")
except RuntimeError as e:
    print(f"AI generation failed: {e}")
```

### Error Types
- **ValueError**: Invalid input parameters (empty title, duration < 0, etc.)
- **RuntimeError**: AI unavailable, timeout, connection error, generation failure
- **Specific errors**: Timeout, ConnectionError, HTTPError with detailed messages

## Workflow Position

**Stage 3** in MVP workflow:

```
Stage 1: PrismQ.T.Idea.Creation
    ↓
Stage 2: PrismQ.T.Title.From.Idea (v1)
    ↓
Stage 3: PrismQ.T.Content.From.Idea.Title (v1) ← THIS STATE
    ↓
Stage 4: PrismQ.T.Review.Title.ByScript
```

## Module Structure

```
T/Content/From/Idea/Title/
├── README.md (updated with production features)
├── requirements.txt
└── src/
    ├── __init__.py                          # Exports
    ├── ai_config.py                         # AI configuration wrapper
    ├── ai_content_generator.py              # AI generation (Qwen3:32b)
    │   ├── SEED_VARIATIONS                  # 500 seed words
    │   ├── get_random_seed()                # Pick random seed
    │   ├── _sanitize_text_input()           # Input sanitization
    │   ├── AIContentGenerator               # Main AI class
    │   └── generate_content()               # Convenience function
    ├── content_generator.py                 # ContentGenerator class
    │   ├── ContentGeneratorConfig           # Full configuration
    │   ├── ContentV1                        # Content model
    │   └── ContentGenerator                 # Main generator
    ├── content_from_idea_title_interactive.py # Interactive CLI
    └── story_content_service.py             # State-based processing
        ├── StoryContentService              # Legacy service
        └── ContentFromIdeaTitleService      # State-based service
```

## Production Features

### Validation
- All inputs validated before processing
- Length limits enforced
- Type checking on all parameters
- Null and empty string checks

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
# Logs include:
# - Story IDs for tracking
# - Character counts
# - State transitions
# - Error details with context
```

### Idempotency
```python
# Safe to call multiple times
result = service.process_oldest_story()
# If story already has content, returns error without regenerating
```

### Security
- No SQL injection (uses parameterized queries via ORM)
- Input sanitization prevents malicious payloads
- No secrets in logs
- Length limits prevent DoS

## Example

**Input:**
- Title: "The Mystery of the Abandoned House"
- Idea: "A girl discovers a time-loop in an abandoned house"
- Seed: "midnight" (randomly selected)

**AI Prompt includes:**
```
TITLE: "The Mystery of the Abandoned House"
IDEA: A girl discovers a time-loop in an abandoned house
INSPIRATION SEED: midnight
TARGET: 90 seconds
```

**Output:**
- AI-generated content text (~225 words for 90s)
- Sections: introduction, body, conclusion
- Metadata: ai_generated=True
