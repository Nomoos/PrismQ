# Classification Module - User Guide

## Overview

This package provides reusable content classifiers and a unified content model that works across text, video, and audio sources. All classifiers are designed to be platform-independent and work with standard metadata fields.

## Features

### Primary Category Classifier

Categorizes content into 8 primary categories optimized for short-form video:

1. **Storytelling** - Narratives, fictional or real (Storytime, POV, confessionals, AITA, TIFU)
2. **Entertainment** - Quick fun content (memes, comedy, pranks, fails, reactions, edits)
3. **Education / Informational** - Explainers, tutorials, facts, productivity hacks, news bites
4. **Lifestyle / Vlog** - Daily life, beauty, fashion, fitness, food, travel, GRWM
5. **Gaming** - Gameplay clips, highlights, speedruns, walkthroughs
6. **Challenges & Trends** - Social challenges, trending sounds, AR effects
7. **Reviews & Commentary** - Product reviews, reactions, opinion commentary
8. **Unusable** - Content not useful for story generation (Music, ASMR, Promotional, Pets, Sports, News)

### Story Detector

Binary classifier that identifies story-based content using weighted keyword analysis across title, description, tags, and subtitles.

### Generalized Text Classifier

Unified text classification that works with the IdeaInspiration model:
- Scores multiple text fields (title, description, content)
- Integrates category and story classification
- Provides detailed field-level scoring
- Works across text, video (with subtitles), and audio (with transcriptions)

### IdeaInspiration Model

Unified data structure for representing content across different media types:
- **IdeaInspiration**: Core data model with title, description, content, keywords
- **IdeaInspirationExtractor**: Extract content from text, video, and audio sources
- **IdeaInspirationBuilder**: Build IdeaInspiration objects with fluent API

## Usage Examples

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

### Generalized Text Classification

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

### Building IdeaInspiration Objects

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

See [API Documentation](./API.md) for complete API reference.

## Migration Note

This package was migrated from `PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource` and enhanced with the new primary category taxonomy. The taxonomy was designed specifically for short-form vertical video classification.

## Support

For questions, issues, or feature requests, please open an issue on GitHub.
