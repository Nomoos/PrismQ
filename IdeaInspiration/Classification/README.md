# PrismQ.IdeaInspiration.Classification

**Platform-agnostic content classification with generalized text analysis**

## Overview

This package provides reusable content classifiers and a unified content model that works across text, video, and audio sources. All classifiers are designed to be platform-independent and work with standard metadata fields.

**New in v2.1.0**: Generalized text classification with IdeaInspiration model, Extract and Builder patterns, and unified TextClassifier.

## Features

### 🎯 Primary Category Classifier
Categorizes content into 8 primary categories optimized for short-form video:

1. **Storytelling** - Narratives, fictional or real (Storytime, POV, confessionals, AITA, TIFU)
2. **Entertainment** - Quick fun content (memes, comedy, pranks, fails, reactions, edits)
3. **Education / Informational** - Explainers, tutorials, facts, productivity hacks, news bites
4. **Lifestyle / Vlog** - Daily life, beauty, fashion, fitness, food, travel, GRWM
5. **Gaming** - Gameplay clips, highlights, speedruns, walkthroughs
6. **Challenges & Trends** - Social challenges, trending sounds, AR effects
7. **Reviews & Commentary** - Product reviews, reactions, opinion commentary
8. **Unusable** - Content not useful for story generation (Music, ASMR, Promotional, Pets, Sports, News)

### 📖 Story Detector
Binary classifier that identifies story-based content using weighted keyword analysis across title, description, tags, and subtitles.

### 🔤 Generalized Text Classifier (NEW)
Unified text classification that works with the IdeaInspiration model:
- Scores multiple text fields (title, description, content)
- Integrates category and story classification
- Provides detailed field-level scoring
- Works across text, video (with subtitles), and audio (with transcriptions)

### 💡 IdeaInspiration Model (NEW)
Unified data structure for representing content across different media types:
- **IdeaInspiration**: Core data model with title, description, content, keywords
- **IdeaInspirationExtractor**: Extract content from text, video, and audio sources
- **IdeaInspirationBuilder**: Build IdeaInspiration objects with fluent API

## Installation

### From Source (Development)

```bash
git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification.git
cd PrismQ.IdeaInspiration.Classification
pip install -e .
```

### From PyPI (Future)

```bash
pip install prismq-idea-classification
```

## Usage

### Category Classification

```python
from prismq.idea.classification import CategoryClassifier, PrimaryCategory

# Initialize classifier
classifier = CategoryClassifier()

# Classify content
result = classifier.classify(
    title="My AITA Story - Was I Wrong?",
    description="Let me tell you about what happened yesterday...",
    tags=['storytime', 'aita', 'confession'],
    subtitle_text="So this happened to me at work..."
)

print(f"Category: {result.category.value}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Usable for stories: {result.category.is_usable_for_stories}")
print(f"Indicators: {result.indicators}")
print(f"Description: {result.category.description}")
```

### Story Detection

```python
from prismq.idea.classification import StoryDetector

# Initialize detector
detector = StoryDetector(confidence_threshold=0.3)

# Detect if content is a story
is_story, confidence, indicators = detector.detect(
    title="My Toxic Relationship Experience",
    description="This is my true story about what happened...",
    tags=['storytime', 'relationship', 'drama'],
    subtitle_text="I was dating someone for 2 years when..."
)

print(f"Is story: {is_story}")
print(f"Confidence: {confidence:.2f}")
print(f"Story indicators: {indicators}")
```

### Generalized Text Classification (NEW)

```python
from prismq.idea.classification import (
    TextClassifier,
    IdeaInspirationExtractor,
    IdeaInspirationBuilder
)

# Initialize classifier and extractor
classifier = TextClassifier()
extractor = IdeaInspirationExtractor()

# Extract from video with subtitles
video_inspiration = extractor.extract_from_video(
    title="My True Story - AITA?",
    description="This is my personal experience",
    subtitle_text="Let me tell you what happened...",
    tags=["story", "aita", "confession"]
)

# Classify with detailed scoring
result = classifier.classify(video_inspiration)

print(f"Category: {result.category.value}")
print(f"Is Story: {result.is_story}")
print(f"Story Confidence: {result.story_confidence:.2%}")
print(f"Combined Score: {result.combined_score:.2%}")
print(f"Field Scores: {result.field_scores}")
```

### Building IdeaInspiration Objects (NEW)

```python
from prismq.idea.classification import IdeaInspirationBuilder

# Build with fluent API
builder = IdeaInspirationBuilder()
inspiration = (builder
    .set_title("Epic Gaming Highlights")
    .set_description("Best moments from stream")
    .set_content("Gameplay subtitles...")
    .add_keyword("gaming")
    .add_keyword("highlights")
    .set_source_type("video")
    .extract_keywords_from_content(max_keywords=5)
    .build())

# Classify the built inspiration
result = classifier.classify(inspiration)
```

### Batch Processing

```python
classifier = CategoryClassifier()

videos = [
    {'title': 'Story Time - AITA', 'description': 'My story', 'tags': ['story']},
    {'title': 'Funny Meme Compilation', 'description': 'Comedy', 'tags': ['funny']},
    {'title': 'How to Code Python', 'description': 'Tutorial', 'tags': ['tutorial']},
    {'title': 'Day in My Life Vlog', 'description': 'Daily routine', 'tags': ['vlog']},
    {'title': 'Fortnite Gameplay', 'description': 'Gaming', 'tags': ['gaming']},
]

for video in videos:
    result = classifier.classify_from_metadata(video)
    print(f"{video['title']}: {result.category.value} ({result.confidence:.2f})")
```

## Package Structure

```
PrismQ.IdeaInspiration.Classification/
├── prismq/
│   └── idea/
│       └── classification/
│           ├── __init__.py              # Package exports
│           ├── categories.py            # Category enums and models
│           ├── category_classifier.py   # Primary category classifier
│           └── story_detector.py        # Story detection classifier
├── tests/
│   ├── test_category_classifier.py      # Category classifier tests
│   ├── test_story_detector.py           # Story detector tests
│   └── test_story_detection_integration.py
├── setup.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Testing

Run the comprehensive test suite (48 tests):

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=prismq --cov-report=html

# Run specific test file
pytest tests/test_category_classifier.py -v
pytest tests/test_story_detector.py -v
```

## Design Principles

1. **Platform Agnostic** - No platform-specific code or dependencies
2. **Minimal Requirements** - Only standard text fields (title, description, tags, subtitles)
3. **Local Processing** - All computation happens locally, no external API calls
4. **Zero Cost** - No external AI service fees
5. **Well Tested** - Comprehensive test coverage with realistic examples
6. **High Performance** - Pure Python, optimized for speed
7. **Easy Integration** - Simple import and usage patterns

## Category Details

### Usable Categories (Story Generation)

| Category | Description | Example Keywords |
|----------|-------------|------------------|
| Storytelling | Narratives, fictional or real | story, aita, tifu, confession, pov |
| Entertainment | Quick fun content | meme, comedy, funny, prank, fail |
| Education | Explainers, tutorials | tutorial, how to, learn, facts |
| Lifestyle | Daily life, beauty, fashion | vlog, daily life, grwm, routine |
| Gaming | Gameplay clips | gameplay, gaming, speedrun |
| Challenges | Social challenges | challenge, trend, viral |
| Reviews | Product reviews | review, unboxing, opinion |

### Unusable Category

The **Unusable** category is a catch-all for content not relevant to story generation:

- **Music & Performance** - Lip sync, covers, dance, music videos
- **ASMR / Relaxation** - Satisfying loops, whispers, slime
- **Promotional / Branded** - Ads, sponsorships, product drops
- **Pets & Animals** - Cute pets, animal tricks
- **Sports & Highlights** - Goals, matches, training clips
- **News & Current Events** - Breaking news, politics
- **Other** - Uncategorized content

## API Reference

### CategoryClassifier

```python
class CategoryClassifier:
    def classify(
        title: str,
        description: str = "",
        tags: List[str] = None,
        subtitle_text: str = ""
    ) -> CategoryResult
    
    def classify_from_metadata(metadata: Dict) -> CategoryResult
```

### StoryDetector

```python
class StoryDetector:
    def __init__(confidence_threshold: float = 0.3)
    
    def detect(
        title: str,
        description: str = "",
        tags: List[str] = None,
        subtitle_text: str = ""
    ) -> Tuple[bool, float, List[str]]
    
    def detect_from_metadata(metadata: Dict) -> Tuple[bool, float, List[str]]
```

### PrimaryCategory (Enum)

```python
class PrimaryCategory(Enum):
    STORYTELLING = "Storytelling"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education / Informational"
    LIFESTYLE = "Lifestyle / Vlog"
    GAMING = "Gaming"
    CHALLENGES_TRENDS = "Challenges & Trends"
    REVIEWS_COMMENTARY = "Reviews & Commentary"
    UNUSABLE = "Unusable"
    
    @property
    def is_usable_for_stories(self) -> bool
    
    @property
    def description(self) -> str
```

### CategoryResult (NamedTuple)

```python
class CategoryResult(NamedTuple):
    category: PrimaryCategory          # Primary category
    confidence: float                  # Confidence score (0.0-1.0)
    indicators: List[str]              # List of matched indicators
    secondary_matches: Dict[PrimaryCategory, float]  # Other category matches
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification.git
cd PrismQ.IdeaInspiration.Classification

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

When adding new classifiers or features:

1. Follow the platform-agnostic design pattern
2. Require only standard text fields
3. Process locally (no external API calls)
4. Add comprehensive tests (aim for >90% coverage)
5. Update this README with usage examples

## Migration Note

This package was migrated from `PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource` and enhanced with the new primary category taxonomy. The taxonomy was designed specifically for short-form vertical video classification.

## License

MIT License - See LICENSE file for details

## Links

- **Repository**: https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification
- **Issues**: https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification/issues

## Version History

- **v2.0.0** - Added primary category classifier with 8-category taxonomy
- **v1.0.0** - Initial story detector from YouTubeShortsSource migration

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
