# T/Script/From/Idea/Title - AI Script Generation

**Namespace**: `PrismQ.T.Content.From.Idea.Title`

Generate script drafts from idea and title using **local AI models only**.

## Purpose

Create script (v1) from the original idea and title using Qwen2.5-14B-Instruct via Ollama.

**ALL generation goes through local AI models. No fallback to rule-based generation.**

## 🤖 AI-Powered Script Generation

### Input to AI
- **Title** (Titulek) - the script title
- **Idea text** - concept, synopsis, premise from the Idea object  
- **Seed** - one word randomly picked from 500 predefined variations (e.g., "pudding", "fire", "ocean", "Chicago", "Germany", "chill")

### Features
- **Qwen2.5-14B-Instruct Model**: High-quality content generation
- **500 Seed Variations**: Simple words for creative inspiration (food, places, feelings, colors, etc.)
- **Platform Optimization**: YouTube Shorts, TikTok, Instagram Reels
- **No Fallback**: Error if AI unavailable (ensures AI is always used)

## Quick Start

```python
from T.Script.From.Idea.Title.src import (
    ContentGenerator,
    ContentGeneratorConfig,
    generate_content,
    get_random_seed,
    SEED_VARIATIONS
)

# Option 1: Use ContentGenerator (requires Idea object)
config = ContentGeneratorConfig(
    ai_model="qwen2.5:14b-instruct",
    target_duration_seconds=90
)
generator = ContentGenerator(config=config)
script = generator.generate_content_v1(idea, title)

# Option 2: Use generate_content directly (simpler)
content_text = generate_content(
    title="The Mystery of the Abandoned House",
    idea_text="A girl discovers a time-loop in an abandoned house",
    target_duration_seconds=90,
    seed="midnight"  # Optional: specify seed, otherwise random
)

# Check available seeds
print(f"Total seeds: {len(SEED_VARIATIONS)}")  # ~500
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
# ContentGeneratorConfig
config = ContentGeneratorConfig(
    platform_target=PlatformTarget.YOUTUBE_MEDIUM,
    target_duration_seconds=90,
    structure_type=ContentStructure.HOOK_DELIVER_CTA,
    tone=ContentTone.ENGAGING,
    ai_model="qwen2.5:14b-instruct",
    ai_api_base="http://localhost:11434",
    ai_temperature=0.7,
    ai_timeout=120
)

# AIScriptGeneratorConfig (for direct use)
ai_config = AIScriptGeneratorConfig(
    model="qwen2.5:14b-instruct",
    api_base="http://localhost:11434",
    temperature=0.7,
    max_tokens=2000,
    timeout=120
)
```

## Error Handling

AI is **required**. If Ollama is not running, a `RuntimeError` is raised:

```python
from T.Script.From.Idea.Title.src import ContentGenerator

generator = ContentGenerator()

# Check availability
if not generator.is_ai_available():
    print("ERROR: Start Ollama with: ollama run qwen2.5:14b-instruct")

# This raises RuntimeError if AI unavailable
try:
    script = generator.generate_content_v1(idea, title)
except RuntimeError as e:
    print(f"AI required but not available: {e}")
```

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
T/Script/From/Idea/Title/
├── README.md
└── src/
    ├── __init__.py              # Exports
    ├── ai_content_generator.py   # AI generation (Qwen2.5-14B-Instruct)
    │   ├── SEED_VARIATIONS      # 500 seed words
    │   ├── get_random_seed()    # Pick random seed
    │   ├── AIContentGenerator    # Main AI class
    │   └── generate_content()    # Convenience function
    ├── content_generator.py      # ContentGenerator class
    └── story_content_service.py  # State-based processing
```

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
