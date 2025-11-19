# AI-Based Text Scoring Implementation

## Overview

This document describes the AI-based text scoring system implemented in PrismQ.IdeaInspiration.Scoring. The system provides comprehensive text quality analysis for content evaluation and idea inspiration scoring.

## Architecture

### Components

1. **IdeaInspiration Model** (`src/models.py`)
   - Unified data structure for text, video, and audio content
   - Factory methods for creating instances from various sources
   - Supports YouTube, Reddit, and plain text content

2. **TextScorer** (`src/scoring/text_scorer.py`)
   - AI-powered text quality analysis
   - Readability metrics (Flesch Reading Ease, Flesch-Kincaid Grade)
   - Sentiment analysis
   - Structure and coherence evaluation

3. **Enhanced ScoringEngine** (`src/scoring/__init__.py`)
   - Integrates TextScorer with engagement metrics
   - Provides composite scoring combining multiple factors
   - Supports both text-only and engagement-based scoring

## Features

### Text Quality Metrics

#### 1. Readability Scoring
- **Flesch Reading Ease**: Measures text difficulty (0-100 scale)
- **Flesch-Kincaid Grade Level**: Estimates required education level
- Optimal for ages 13-18 (grade 8-12)

#### 2. Length Analysis
- Evaluates optimal content length
- Target ranges:
  - Articles: 300-1000 words
  - Titles: 50-70 characters, 6-12 words
  - Descriptions: 20-50 words, 1-3 sentences

#### 3. Structure Evaluation
- Sentence length analysis (optimal: 15-20 words)
- Paragraph structure (3-5 sentences per paragraph)
- Overall coherence and flow

#### 4. Sentiment Analysis
- Positive/negative/neutral classification
- Word-based sentiment detection
- Score range: -50 (very negative) to +50 (very positive)

#### 5. Title Relevance
- Keyword matching between title and content
- Measures content-title alignment
- Helps identify clickbait or misleading titles

### Content Type Support

#### Text Content
```python
from src.models import IdeaInspiration
from src.scoring import ScoringEngine

idea = IdeaInspiration.from_text(
    title="Article Title",
    description="Brief description",
    text_content="Full article text..."
)

engine = ScoringEngine()
score = engine.score_idea_inspiration(idea)
```

#### Video Content (with Transcription)
```python
video_data = {
    'id': 'video_id',
    'snippet': {'title': '...', 'description': '...'},
    'statistics': {'viewCount': '100000', ...}
}

transcription = "Video transcription from audio..."
idea = IdeaInspiration.from_youtube_video(video_data, transcription)
score = engine.score_idea_inspiration(idea)
```

#### Reddit Posts
```python
post_data = {
    'title': 'Post title',
    'selftext': 'Post content',
    'score': 1000,
    'num_comments': 50
}

idea = IdeaInspiration.from_reddit_post(post_data)
score = engine.score_idea_inspiration(idea)
```

## Scoring Algorithm

### Composite Score Calculation

**With Engagement Metrics:**
```
Composite Score = 
  Text Quality (40%) +
  Title Quality (20%) +
  Description Quality (10%) +
  Engagement Score (30%)
```

**Text-Only (No Engagement):**
```
Composite Score = 
  Text Quality (50%) +
  Title Quality (30%) +
  Description Quality (20%)
```

### Text Quality Score
```
Text Quality = 
  Readability (25%) +
  Length Score (15%) +
  Structure Score (20%) +
  Sentiment Score (20%) +
  Title Relevance (20%)
```

## Usage Examples

### Basic Text Scoring
```python
from src.scoring import ScoringEngine

engine = ScoringEngine()

result = engine.score_text_content(
    title="Introduction to Machine Learning",
    description="A comprehensive guide to ML fundamentals.",
    text_content="Machine learning is..."
)

print(f"Score: {result['composite_score']:.2f}")
print(f"Readability: {result['text_quality']['readability_score']:.2f}")
print(f"Sentiment: {result['text_quality']['sentiment_category']}")
```

### YouTube Video Analysis
```python
video_data = {
    'id': 'abc123',
    'snippet': {
        'title': "Python Tutorial",
        'description': "Learn Python basics"
    },
    'statistics': {
        'viewCount': '50000',
        'likeCount': '2000',
        'commentCount': '150'
    }
}

transcription = "Welcome to this Python tutorial..."
idea = IdeaInspiration.from_youtube_video(video_data, transcription)
result = engine.score_idea_inspiration(idea)

print(f"Composite Score: {result['composite_score']:.2f}")
print(f"Engagement: {result['engagement_score']:.2f}")
print(f"Text Quality: {result['text_quality']['overall_text_score']:.2f}")
```

## Future Enhancements

### Planned Features

1. **Advanced NLP Models**
   - Integration with transformers (BERT, RoBERTa)
   - Semantic similarity analysis
   - Named entity recognition

2. **Audio Processing**
   - Whisper integration for transcription
   - Speech quality analysis
   - Audio sentiment detection

3. **Video Analysis**
   - Subtitle extraction
   - Visual content analysis
   - Scene detection

4. **Enhanced Sentiment**
   - Emotion classification (joy, anger, sadness, etc.)
   - Aspect-based sentiment analysis
   - Contextual sentiment understanding

5. **Multilingual Support**
   - Language detection
   - Multi-language scoring
   - Cross-language comparison

### Optional Dependencies

For advanced features, install optional dependencies:

```bash
# Transformer models (for semantic analysis)
pip install torch transformers sentence-transformers

# Audio processing (for transcription)
pip install openai-whisper

# Additional utilities
pip install numpy pillow
```

## Performance Considerations

### Target Platform
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

### Optimization Tips

1. **Current Implementation**
   - Rule-based scoring: Fast, no GPU required
   - Suitable for real-time processing
   - Low memory footprint

2. **With AI Models (Future)**
   - Use mixed precision (FP16) for RTX 5090
   - Batch processing for multiple items
   - Model quantization for faster inference
   - CUDA memory management

## Testing

Run the comprehensive test suite:

```bash
# All tests
python -m pytest tests/ -v

# Specific test modules
python -m pytest tests/test_models.py -v
python -m pytest tests/test_text_scorer.py -v
python -m pytest tests/test_scoring.py -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## API Reference

### IdeaInspiration

```python
class IdeaInspiration:
    title: str
    description: str
    text_content: str
    content_type: ContentType
    source_url: Optional[str]
    metadata: Dict[str, Any]
    
    @classmethod
    def from_text(cls, ...) -> IdeaInspiration
    
    @classmethod
    def from_youtube_video(cls, ...) -> IdeaInspiration
    
    @classmethod
    def from_reddit_post(cls, ...) -> IdeaInspiration
```

### TextScorer

```python
class TextScorer:
    def score_text(self, text: str, title: Optional[str]) -> Dict[str, float]
    def calculate_readability(self, text: str) -> Dict[str, float]
    def calculate_sentiment(self, text: str) -> Dict[str, Any]
    def score_title_quality(self, title: str) -> Dict[str, float]
    def score_description_quality(self, description: str) -> Dict[str, float]
```

### ScoringEngine

```python
class ScoringEngine:
    def score_idea_inspiration(self, idea_inspiration) -> Dict[str, Any]
    def score_text_content(self, title: str, description: str, 
                          text_content: str) -> Dict[str, Any]
```

## Contributing

When adding new features:

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider GPU optimization
5. Maintain backward compatibility

## License

Proprietary - PrismQ Development
