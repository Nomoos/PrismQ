# QASource

**Collect and analyze questions from Q&A platforms like StackExchange**

## Overview

QASource is a PrismQ module that gathers questions from Q&A platforms, primarily StackExchange sites (Stack Overflow, Ask Ubuntu, etc.). It provides sentiment analysis, topic extraction, and actionability scoring.

## Features

- **StackExchange API Integration**: Official API v2.3 support
- **Multi-Site Support**: Query multiple StackExchange sites simultaneously
- **Tag Filtering**: Filter questions by specific tags
- **Sentiment Analysis**: Analyze question sentiment using VADER
- **Topic Extraction**: Extract key topics from questions
- **Universal Metrics**: Engagement, relevance, and actionability scoring
- **SQLite Storage**: Persistent storage with efficient querying

## Installation

```bash
cd Sources/Community/QASource
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# StackExchange API Configuration
STACKEXCHANGE_API_KEY=optional_api_key
QA_STACKEXCHANGE_SITES=stackoverflow,askubuntu,superuser
QA_TAGS=python,javascript,programming
QA_MAX_QUESTIONS=100

# Database Configuration
QA_DATABASE_URL=sqlite:///qa_source.s3db
```

### Getting StackExchange API Key (Optional)

An API key is optional but increases your daily quota from 300 to 10,000 requests:

1. Go to [StackApps](https://stackapps.com/)
2. Register your application
3. Get your API key
4. Add it to your `.env` file

## Usage

### Command Line Interface

```bash
# Scrape questions from configured sites
python -m src.cli scrape

# Specify custom sites and tags
python -m src.cli scrape --sites stackoverflow,askubuntu --tags python,linux

# List collected signals
python -m src.cli list --limit 20

# Show statistics
python -m src.cli stats
```

### Python API

```python
from src.core.config import Config
from src.core.database import Database
from src.core.sentiment_analyzer import SentimentAnalyzer
from src.core.community_processor import CommunityProcessor
from src.plugins.stackexchange_plugin import StackExchangePlugin

# Initialize
config = Config()
db = Database(config.database_url)
processor = CommunityProcessor(SentimentAnalyzer())

# Scrape questions
plugin = StackExchangePlugin(config)
questions = plugin.scrape(
    sites=['stackoverflow'],
    tags=['python', 'machine-learning'],
    max_questions=50
)

# Process and store
for q in questions:
    signal = processor.process_question(
        text=q['text'],
        title=q['title'],
        author=q['author'],
        source='qa',
        source_id=q['source_id'],
        platform=q['platform'],
        upvotes=q['upvotes'],
        answers=q['answers'],
        views=q['views'],
        timestamp=q['timestamp'],
        tags=q['tags']
    )
    db.insert_signal(signal)
```

## API Rate Limits

- **Without API key**: 300 requests/day
- **With API key**: 10,000 requests/day
- **Per request**: 100 questions max

## Related Modules

- **UserFeedbackSource**: Own channel feedback
- **CommentMiningSource**: Global comment analysis
- **PromptBoxSource**: User-submitted prompts
