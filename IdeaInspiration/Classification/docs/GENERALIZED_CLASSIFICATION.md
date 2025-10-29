# Generalized Text Classification Guide

## Overview

Version 2.1.0 introduces generalized text classification with support for text, video, and audio content through a unified `IdeaInspiration` model.

## Architecture

### IdeaInspiration Model

The core data structure that represents content across different media types:

```python
from prismq.idea.classification import IdeaInspiration

inspiration = IdeaInspiration(
    title="Content Title",
    description="Content description",
    content="Full text content (body, subtitles, or transcription)",
    keywords=["keyword1", "keyword2"],
    source_type="text",  # or "video" or "audio"
    metadata={"custom": "data"}
)
```

**Key Features:**
- Unified format for text, video (with subtitles), and audio (with transcriptions)
- Automatic validation and normalization
- Conversion to/from dictionaries
- Combined text access via `all_text` property

### Extract Pattern

The `IdeaInspirationExtractor` provides methods to extract content from different sources:

```python
from prismq.idea.classification import IdeaInspirationExtractor

extractor = IdeaInspirationExtractor()

# From text content
text_insp = extractor.extract_from_text(
    title="Article Title",
    description="Article description",
    body="Full article text...",
    tags=["article", "blog"]
)

# From video with subtitles
video_insp = extractor.extract_from_video(
    title="Video Title",
    description="Video description",
    subtitle_text="Subtitle text from video...",
    tags=["video", "shorts"]
)

# From audio with transcription
audio_insp = extractor.extract_from_audio(
    title="Podcast Episode",
    description="Episode description",
    transcription="Transcribed audio text...",
    tags=["podcast", "audio"]
)

# Auto-detect from metadata
metadata = {
    'title': 'Content',
    'description': 'Description',
    'subtitle_text': 'Subtitles...',  # Triggers video detection
    'tags': ['tag1', 'tag2']
}
auto_insp = extractor.extract_from_metadata(metadata)
```

**Features:**
- Auto-detection of content type
- Keyword extraction from tags
- Simple keyword extraction from text (basic heuristics)
- Metadata preservation

### Builder Pattern

The `IdeaInspirationBuilder` provides a fluent API for step-by-step construction:

```python
from prismq.idea.classification import IdeaInspirationBuilder

builder = IdeaInspirationBuilder()

inspiration = (builder
    .set_title("My Title")
    .set_description("My description")
    .set_content("My content text")
    .add_keyword("keyword1")
    .add_keywords(["keyword2", "keyword3"])
    .set_source_type("video")
    .add_metadata("platform", "youtube")
    .extract_keywords_from_content(max_keywords=5)
    .build())
```

**Features:**
- Chainable methods for fluent API
- Automatic keyword extraction from content
- Validation before building
- Reusable builder with `reset()` method
- Can populate from metadata dictionaries

### TextClassifier

The `TextClassifier` provides unified classification across all content types:

```python
from prismq.idea.classification import TextClassifier

classifier = TextClassifier()

# Classify an IdeaInspiration object
result = classifier.classify(inspiration)

print(f"Category: {result.category.value}")
print(f"Is Story: {result.is_story}")
print(f"Story Confidence: {result.story_confidence:.2%}")
print(f"Combined Score: {result.combined_score:.2%}")

# Field-level scores
for field, score in result.field_scores.items():
    print(f"{field}: {score:.2f}")

# Matched indicators
print(f"Indicators: {result.indicators}")
```

**Features:**
- Integrates CategoryClassifier and StoryDetector
- Scores individual text fields (title, description, content, keywords)
- Provides combined confidence score
- Works with any source type (text, video, audio)
- Batch classification support

## Use Cases

### 1. Processing YouTube Shorts with Subtitles

```python
from prismq.idea.classification import IdeaInspirationExtractor, TextClassifier

extractor = IdeaInspirationExtractor()
classifier = TextClassifier()

# Extract from YouTube Shorts metadata
inspiration = extractor.extract_from_video(
    title="My Crazy Experience at Work",
    description="You won't believe what happened!",
    subtitle_text="So I was at work yesterday when my boss...",
    tags=["storytime", "work", "drama"]
)

# Classify
result = classifier.classify(inspiration)

if result.is_story and result.category.is_usable_for_stories:
    print("✓ This is story content suitable for inspiration")
    print(f"  Category: {result.category.value}")
    print(f"  Confidence: {result.combined_score:.2%}")
```

### 2. Processing Podcast Transcriptions

```python
# Extract from podcast with transcription
inspiration = extractor.extract_from_audio(
    title="Episode 42: The Future of AI",
    description="Discussion about artificial intelligence",
    transcription="Welcome to the podcast. Today we're talking about...",
    tags=["podcast", "ai", "technology"]
)

# Classify
result = classifier.classify(inspiration)
print(f"Category: {result.category.value}")
print(f"Educational content: {result.category == PrimaryCategory.EDUCATION}")
```

### 3. Building Content Programmatically

```python
from prismq.idea.classification import IdeaInspirationBuilder, TextClassifier

builder = IdeaInspirationBuilder()
classifier = TextClassifier()

# Build inspiration from scraped data
inspiration = (builder
    .set_title("Tutorial: Machine Learning Basics")
    .set_description("Learn ML fundamentals")
    .set_content("Machine learning is a subset of artificial intelligence...")
    .set_source_type("text")
    .extract_keywords_from_content(max_keywords=10)
    .build())

# Classify
result = classifier.classify(inspiration)
```

### 4. Batch Processing Mixed Content

```python
# Process mixed content types
metadata_batch = [
    {'title': 'Story', 'subtitle_text': 'Story text...', 'tags': ['story']},
    {'title': 'Tutorial', 'body': 'Tutorial text...', 'tags': ['tutorial']},
    {'title': 'Podcast', 'transcription': 'Audio text...', 'tags': ['podcast']}
]

# Extract all
inspirations = [extractor.extract_from_metadata(m) for m in metadata_batch]

# Classify all
results = classifier.classify_batch(inspirations)

for insp, result in zip(inspirations, results):
    print(f"{insp.title} ({insp.source_type}): {result.category.value}")
```

## Integration with Existing Classifiers

The new components are fully compatible with existing classifiers:

```python
from prismq.idea.classification import (
    CategoryClassifier,
    StoryDetector,
    IdeaInspiration
)

# Use existing classifiers directly
category_classifier = CategoryClassifier()
story_detector = StoryDetector()

inspiration = IdeaInspiration(
    title="My Story",
    description="Story description",
    keywords=["story", "drama"]
)

# Classify with existing classifiers
category_result = category_classifier.classify(
    title=inspiration.title,
    description=inspiration.description,
    tags=inspiration.keywords
)

is_story, confidence, indicators = story_detector.detect(
    title=inspiration.title,
    description=inspiration.description,
    tags=inspiration.keywords
)
```

## Best Practices

### 1. Use Extract for Raw Data

When you have raw metadata from APIs or scraping:

```python
extractor = IdeaInspirationExtractor()
inspiration = extractor.extract_from_metadata(raw_metadata)
```

### 2. Use Builder for Programmatic Construction

When building content programmatically with control:

```python
builder = IdeaInspirationBuilder()
inspiration = (builder
    .set_title(title)
    .set_description(description)
    .extract_keywords_from_content()
    .build())
```

### 3. Validate Before Classification

```python
if inspiration.has_content:
    result = classifier.classify(inspiration)
else:
    print("Insufficient content to classify")
```

### 4. Use Field Scores for Filtering

```python
result = classifier.classify(inspiration)

# Filter by field quality
if result.field_scores['title'] > 0.5 and result.combined_score > 0.6:
    print("High quality content")
```

### 5. Batch Process for Efficiency

```python
# Process multiple items at once
inspirations = [extractor.extract_from_metadata(m) for m in metadata_list]
results = classifier.classify_batch(inspirations)
```

## Migration Guide

### From Direct Field Classification

**Before:**
```python
classifier = CategoryClassifier()
result = classifier.classify(title="...", description="...", tags=[...])
```

**After (Option 1 - Still supported):**
```python
classifier = CategoryClassifier()
result = classifier.classify(title="...", description="...", tags=[...])
```

**After (Option 2 - New unified approach):**
```python
text_classifier = TextClassifier()
result = text_classifier.classify_text_fields(
    title="...",
    description="...",
    keywords=[...]
)
```

### From Metadata Dictionaries

**Before:**
```python
classifier = CategoryClassifier()
result = classifier.classify_from_metadata(metadata)
```

**After:**
```python
extractor = IdeaInspirationExtractor()
text_classifier = TextClassifier()

inspiration = extractor.extract_from_metadata(metadata)
result = text_classifier.classify(inspiration)
```

## Advanced Features

### Custom Keyword Extraction

```python
builder = IdeaInspirationBuilder()
inspiration = (builder
    .set_title("Title with many words about programming")
    .set_description("More text about Python and coding")
    .extract_keywords_from_content(
        max_keywords=10,
        merge_with_existing=True  # Keep manually added keywords
    )
    .build())

print(inspiration.keywords)  # Extracted keywords
```

### Metadata Preservation

```python
inspiration = extractor.extract_from_video(
    title="Video",
    description="Description",
    subtitle_text="Subtitles",
    metadata={
        'platform': 'youtube',
        'duration': 60,
        'views': 1000,
        'custom_field': 'value'
    }
)

# Access metadata later
print(inspiration.metadata['platform'])  # 'youtube'
print(inspiration.metadata['duration'])  # 60
```

### Serialization

```python
# Convert to dict for storage
data = inspiration.to_dict()

# Store in database, send over network, etc.
# ...

# Restore from dict
restored = IdeaInspiration.from_dict(data)
```

## Performance Considerations

- All processing is local (no external API calls)
- Zero external costs
- Fast keyword extraction using simple heuristics
- Efficient batch processing
- Minimal memory footprint

## Future Enhancements

Potential future additions for local AI integration:
- Transformer-based keyword extraction
- Semantic similarity for better classification
- Local embedding models for content understanding
- Multi-language support
- Advanced NLP features using local models

## Support

For questions or issues:
- See [example_generalized.py](../example_generalized.py) for working examples
- Check the [main README](../README.md) for installation and setup
- Open an issue on GitHub for bugs or feature requests
