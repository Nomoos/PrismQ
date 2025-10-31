# Community Sources

Direct audience feedback and community-driven insights.

## Overview

Community sources capture direct input from audiences including questions, comments, feedback, and user-submitted content. These represent the voice of the audience and provide invaluable insights for content ideation.

## Sources

### ✅ Implemented Sources

- **UserFeedbackSource**: Your own channel comments and DMs
  - Full implementation with YouTube Comments API integration
  - Sentiment analysis using VADER
  - Topic extraction and intent detection
  - Universal metrics (engagement, relevance, actionability)
  - See [UserFeedbackSource/README.md](./UserFeedbackSource/README.md)

- **QASource**: Q&A platforms (StackExchange/Quora)
  - StackExchange API integration
  - Multi-site support (Stack Overflow, Ask Ubuntu, etc.)
  - Tag-based filtering
  - Question/answer quality metrics
  - See [QASource/README.md](./QASource/README.md)

### 📋 Placeholder Implementations

- **CommentMiningSource**: Global platform comments (YouTube/IG/TikTok)
  - Placeholder structure provided
  - Full implementation would include multi-platform comment scraping
  - See [CommentMiningSource/README.md](./CommentMiningSource/README.md)

- **PromptBoxSource**: User-submitted prompts and forms
  - Placeholder structure provided
  - Full implementation would include form endpoints and voting system
  - See [PromptBoxSource/README.md](./PromptBoxSource/README.md)

## Purpose

Community sources help identify:
- Audience questions and pain points
- Direct content requests
- User sentiment and reactions
- Community needs and interests
- Engagement patterns
- Trending topics in discussions

## Common Features

All community sources share:

- **Sentiment Analysis**: VADER-based sentiment detection optimized for social media
- **Topic Extraction**: Automatic keyword and theme identification
- **Intent Detection**: Classify as question, suggestion, complaint, or praise
- **Universal Metrics**: 
  - Engagement score (upvotes, replies, reactions)
  - Relevance score (sentiment confidence, topic density)
  - Actionability score (content creation potential)
- **SQLite Storage**: Efficient persistent storage with deduplication
- **CLI Interface**: Consistent command-line tools

## Architecture

All sources follow SOLID principles:

- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugin architecture
- **Liskov Substitution**: Plugins properly abstracted
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Dependencies injected, not hardcoded

## Data Model

All sources transform data into a unified community signal format:

```python
{
    'source': 'community_source_name',
    'source_id': 'unique_id',
    'content': {
        'type': 'question|comment|feedback|prompt',
        'text': 'Content text',
        'title': 'Title (for Q&A)',
        'author': 'username'
    },
    'context': {
        'platform': 'youtube|stackoverflow|etc',
        'parent_content': 'video_id or post_id',
        'category': 'technology|gaming|etc',
        'timestamp': 'ISO 8601 timestamp'
    },
    'metrics': {
        'upvotes': 50,
        'replies': 10,
        'reactions': {'helpful': 5}
    },
    'analysis': {
        'sentiment': 'positive|negative|neutral',
        'sentiment_score': 0.75,  # -1 to 1
        'topics': ['python', 'tutorial'],
        'intent': 'question|suggestion|complaint|praise'
    },
    'universal_metrics': {
        'engagement_score': 7.5,   # 0-10
        'relevance_score': 8.2,    # 0-10
        'actionability': 6.8       # 0-10
    }
}
```

## Getting Started

### 1. UserFeedbackSource (Recommended First)

```bash
cd UserFeedbackSource
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your YouTube API key and channel ID
python -m src.cli scrape --max-videos 10
```

### 2. QASource

```bash
cd QASource
pip install -r requirements.txt
cp .env.example .env
# Edit .env with StackExchange sites and tags
python -m src.cli scrape --sites stackoverflow --tags python,javascript
```

## Development Status

| Source | Status | Completeness |
|--------|--------|--------------|
| UserFeedbackSource | ✅ Complete | 100% - Full implementation |
| QASource | ✅ Complete | 100% - Full StackExchange integration |
| CommentMiningSource | 📋 Placeholder | 30% - Structure only |
| PromptBoxSource | 📋 Placeholder | 30% - Structure only |

## Future Enhancements

For placeholder implementations:

**CommentMiningSource**:
- YouTube trending video comment scraping
- Instagram Graph API integration
- TikTok unofficial API integration
- Cross-platform sentiment trend analysis

**PromptBoxSource**:
- Web form endpoint creation
- Email submission processing
- Voting/ranking system
- Duplicate detection and merging

## Related Modules

- **Classification**: Content categorization
- **Scoring**: Universal metrics calculation
- **Model**: IdeaInspiration data model
