# UserFeedbackSource

**Collect and analyze feedback from your own channel's comments and direct messages**

## Overview

UserFeedbackSource is a PrismQ module that gathers direct feedback from your audience through YouTube comments. It provides sentiment analysis, topic extraction, and actionability scoring to help identify valuable content ideas from your community.

## Features

- **YouTube Comments**: Fetch comments from your channel videos using YouTube Data API
- **Sentiment Analysis**: Analyze comment sentiment using VADER (optimized for social media)
- **Topic Extraction**: Extract key topics and themes from feedback
- **Intent Detection**: Identify questions, suggestions, complaints, and praise
- **Universal Metrics**: Engagement, relevance, and actionability scoring
- **Deduplication**: Automatic detection and handling of duplicate comments
- **SQLite Storage**: Persistent storage with efficient querying

## Installation

```bash
cd Sources/Community/UserFeedbackSource
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# YouTube API Configuration
YOUTUBE_API_KEY=your_api_key_here
USER_FEEDBACK_YOUTUBE_CHANNEL_ID=your_channel_id

# Database Configuration
USER_FEEDBACK_DATABASE_URL=sqlite:///user_feedback.s3db

# Scraping Configuration
USER_FEEDBACK_MAX_COMMENTS=100
```

### Getting YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key to your `.env` file

### Finding Your Channel ID

1. Go to your YouTube Studio
2. Click on Settings → Channel → Advanced settings
3. Copy your Channel ID

## Usage

### Command Line Interface

```bash
# Scrape comments from your channel
python -m src.cli scrape --channel-id UCxxxxx --max-videos 10

# List collected signals
python -m src.cli list --limit 20

# Filter by sentiment
python -m src.cli list --sentiment positive

# Show statistics
python -m src.cli stats

# Clear all data
python -m src.cli clear
```

### Python API

```python
from src.core.config import Config
from src.core.database import Database
from src.core.sentiment_analyzer import SentimentAnalyzer
from src.core.community_processor import CommunityProcessor
from src.plugins.youtube_comments_plugin import YouTubeCommentsPlugin

# Initialize
config = Config()
db = Database(config.database_url)
sentiment_analyzer = SentimentAnalyzer()
processor = CommunityProcessor(sentiment_analyzer)

# Scrape comments
plugin = YouTubeCommentsPlugin(config)
raw_comments = plugin.scrape(channel_id="UCxxxxx", max_videos=10)

# Process and store
for comment_data in raw_comments:
    signal = processor.process_comment(
        text=comment_data['text'],
        author=comment_data['author'],
        source='user_feedback',
        source_id=comment_data['source_id'],
        platform='youtube',
        parent_content=comment_data['parent_content'],
        upvotes=comment_data['upvotes'],
        replies=comment_data['replies'],
        timestamp=comment_data['timestamp']
    )
    db.insert_signal(signal)

# Query signals
signals = db.get_all_signals(limit=20)
for signal in signals:
    print(f"{signal['content']['author']}: {signal['content']['text'][:50]}...")
    print(f"Sentiment: {signal['analysis']['sentiment']}")
    print(f"Actionability: {signal['universal_metrics']['actionability']}")
```

## Data Model

### Community Signal Format

```python
{
    'source': 'user_feedback',
    'source_id': 'comment_id',
    'content': {
        'type': 'comment',
        'text': 'Comment text',
        'title': None,
        'author': 'username'
    },
    'context': {
        'platform': 'youtube',
        'parent_content': 'video_id',
        'category': 'technology',
        'timestamp': '2024-01-01T12:00:00'
    },
    'metrics': {
        'upvotes': 50,
        'replies': 10,
        'reactions': {}
    },
    'analysis': {
        'sentiment': 'positive',
        'sentiment_score': 0.75,
        'topics': ['python', 'tutorial'],
        'intent': 'question'
    },
    'universal_metrics': {
        'engagement_score': 7.5,
        'relevance_score': 8.2,
        'actionability': 6.8
    }
}
```

## Architecture

The module follows SOLID principles:

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Extensible through plugins
- **Liskov Substitution**: Plugin interface is properly abstracted
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Dependencies injected, not hardcoded

### Directory Structure

```
UserFeedbackSource/
├── src/
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database operations
│   │   ├── metrics.py           # Universal metrics
│   │   ├── sentiment_analyzer.py # Sentiment analysis
│   │   └── community_processor.py # Data transformation
│   └── plugins/
│       ├── __init__.py          # Plugin interface
│       └── youtube_comments_plugin.py
├── _meta/
│   ├── docs/                    # Documentation
│   ├── issues/                  # Issue tracking
│   └── tests/                   # Unit tests
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## API Rate Limits

YouTube Data API has quota limits:

- **Default quota**: 10,000 units/day
- **Comment list**: 1 unit per request
- **Search**: 100 units per request

Each video's comments cost ~1-2 units, so you can fetch comments from ~5,000-10,000 videos per day.

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black src/
flake8 src/
mypy src/
```

## Privacy Considerations

- Only collect publicly available comments
- Respect YouTube's Terms of Service
- Consider anonymizing data for public datasets
- Be mindful of GDPR/CCPA if storing user data

## Related Modules

- **CommentMiningSource**: Global comment analysis across platforms
- **QASource**: Q&A platform integration
- **PromptBoxSource**: User-submitted prompts

## Support

For issues or questions, see the `_meta/issues/` directory.
