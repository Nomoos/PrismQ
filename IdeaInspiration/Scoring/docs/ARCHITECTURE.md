# Architecture - PrismQ.IdeaInspiration.Scoring

## Overview

This module acts as a **Classifier/Enrichment Layer** for IdeaInspiration objects. It does NOT define the IdeaInspiration model - that comes from external modules like PrismQ.IdeaCollector. Instead, this module:

1. Accepts existing IdeaInspiration objects
2. Analyzes their content  
3. Returns detailed `ScoreBreakdown` objects with scoring for various aspects

## Design Pattern: Enrichment/Classifier

```
┌─────────────────────────────────────┐
│   PrismQ.IdeaCollector              │
│   (or similar module)               │
│                                     │
│   Creates IdeaInspiration objects   │
└────────────┬────────────────────────┘
             │
             │ IdeaInspiration
             ▼
┌─────────────────────────────────────┐
│  PrismQ.IdeaInspiration.Scoring     │
│  (This Module - Classifier)         │
│                                     │
│  Enriches with:                     │
│  - Overall Score                    │
│  - Title Score                      │
│  - Description Score                │
│  - Text Quality Score               │
│  - Engagement Score                 │
│  - Readability Score                │
│  - Sentiment Score                  │
│  - SEO Score (placeholder)          │
│  - Tags Score (placeholder)         │
│  - Similarity Score (placeholder)   │
└────────────┬────────────────────────┘
             │
             │ ScoreBreakdown
             ▼
┌─────────────────────────────────────┐
│   Downstream Modules                │
│   (Content selection, ranking, etc) │
└─────────────────────────────────────┘
```

## Components

### 1. ScoreBreakdown (`src/models.py`)

The primary output model containing detailed scoring information:

```python
@dataclass
class ScoreBreakdown:
    overall_score: float          # Combined overall score (0-100)
    title_score: float            # Title quality and effectiveness
    description_score: float      # Description quality
    text_quality_score: float     # Content text quality
    engagement_score: float       # Engagement metrics (if available)
    readability_score: float      # Text readability
    sentiment_score: float        # Sentiment analysis
    seo_score: float             # SEO optimization (placeholder)
    tags_score: float            # Tags quality (placeholder)
    similarity_score: float      # Content similarity (placeholder)
    score_details: Dict          # Detailed breakdown
```

### 2. ScoringEngine (`src/scoring/__init__.py`)

Main scoring engine that:
- Accepts IdeaInspiration objects (via duck typing)
- Analyzes text quality, engagement, readability, sentiment
- Returns ScoreBreakdown objects

### 3. TextScorer (`src/scoring/text_scorer.py`)

Internal component providing text analysis:
- Readability metrics (Flesch Reading Ease, Flesch-Kincaid)
- Sentiment analysis
- Structure and coherence evaluation
- Title/description quality scoring

## Usage Pattern

### In Production

```python
# 1. Get IdeaInspiration from another module
from prismq.ideacollector import IdeaInspiration  # External module

# 2. Initialize scoring engine
from src.scoring import ScoringEngine
from src.models import ScoreBreakdown

engine = ScoringEngine()

# 3. Enrich IdeaInspiration with scores
idea = IdeaInspiration(...)  # From collector module
score_breakdown = engine.score_idea_inspiration(idea)

# 4. Use scores for ranking, filtering, etc.
if score_breakdown.overall_score > 70:
    # High-quality content
    process_idea(idea, score_breakdown)
```

### Current Implementation (Development)

Since IdeaInspiration is defined externally, we use mock objects for testing and demonstration:

```python
# Mock for testing/demo purposes
class MockIdeaInspiration:
    def __init__(self, title, description, text_content, metadata=None):
        self.title = title
        self.description = description
        self.text_content = text_content
        self.metadata = metadata or {}

# Real usage will import IdeaInspiration from external module
```

## Integration Points

### Expected IdeaInspiration Interface

The scoring engine expects objects with these attributes:

```python
class IdeaInspiration:
    title: str              # Required
    description: str        # Required
    text_content: str       # Required
    metadata: Dict          # Optional (for engagement metrics)
```

### Metadata Format for Engagement Scoring

**YouTube Format:**
```python
metadata = {
    'statistics': {
        'viewCount': '100000',
        'likeCount': '5000',
        'commentCount': '250'
    }
}
```

**Reddit Format:**
```python
metadata = {
    'score': 1500,
    'num_comments': 75,
    'num_views': 50000  # Optional
}
```

## Future Enhancements

### Placeholder Scores

Currently set to 0.0, ready for future implementation:

1. **SEO Score**: Keyword optimization, meta tags, URL structure
2. **Tags Score**: Tag relevance, coverage, quality
3. **Similarity Score**: Content similarity to existing ideas

### Advanced AI Models

The architecture supports future integration of:
- Transformer models (BERT, RoBERTa) for semantic analysis
- Sentence transformers for similarity scoring
- OpenAI Whisper for audio transcription
- Computer vision models for video analysis

## Testing Strategy

Tests use mock IdeaInspiration objects since the real model is external:

```python
class MockIdeaInspiration:
    """Mock for testing the scoring engine."""
    def __init__(self, title, description, text_content, metadata=None):
        self.title = title
        self.description = description
        self.text_content = text_content
        self.metadata = metadata or {}
```

This allows testing without dependencies on external modules.

## Separation of Concerns

### What This Module DOES:
✅ Score existing IdeaInspiration objects
✅ Provide detailed score breakdowns
✅ Analyze text quality, readability, sentiment
✅ Calculate engagement scores
✅ Act as classifier/enrichment layer

### What This Module DOES NOT:
❌ Define IdeaInspiration model (comes from PrismQ.IdeaCollector)
❌ Collect or gather ideas
❌ Store or persist IdeaInspiration objects
❌ Make decisions about which ideas to use

This separation ensures clean module boundaries and prevents circular dependencies in the PrismQ ecosystem.
