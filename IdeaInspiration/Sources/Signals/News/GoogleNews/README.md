# GoogleNewsSource

**News articles from Google News**

## Overview

GoogleNewsSource collects news signals from Google News to identify breaking news, trending topics, and emerging stories. This source is part of the PrismQ.IdeaInspiration ecosystem and provides timely content opportunities based on current events.

## Features

- ✅ Collects top news headlines from Google News
- ✅ Searches news by keywords
- ✅ Fetches news for specific topics
- ✅ Universal signal metrics (trend strength, virality score)
- ✅ SQLite database with deduplication
- ✅ CLI interface for easy management
- ✅ SOLID architecture with plugin system
- ✅ Comprehensive test coverage
- ✅ Stub mode for testing without API

## Installation

```bash
# Navigate to this directory
cd Sources/Signals/News/GoogleNews

# Install dependencies
pip install -e .
```

## Dependencies

- `gnews` - Google News API (optional - runs in stub mode if not available)
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_google_news.db`)
- `MAX_RESULTS` - Maximum news items per scrape (default: 25)
- `LANGUAGE` - Language code (default: en)
- `GOOGLE_NEWS_REGION` - Country code (default: US)

## Usage

### CLI Commands

#### Scrape Top News
```bash
# Scrape top headlines
python -m src.cli scrape

# Scrape with custom limit
python -m src.cli scrape --limit 10
```

#### Search News
```bash
# Search for specific topics
python -m src.cli scrape --keywords "artificial intelligence"

# Search with topic
python -m src.cli scrape --topic "technology"
```

#### List Signals
```bash
# List all signals
python -m src.cli list

# List with limit
python -m src.cli list --limit 20
```

#### Show Statistics
```bash
python -m src.cli stats
```

#### Export Data
```bash
# Export to CSV
python -m src.cli export news.csv --format csv

# Export to JSON
python -m src.cli export news.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

### Python API

```python
from src.core.config import GoogleNewsConfig
from src.plugins.google_news_plugin import GoogleNewsPlugin
from src.core.database import SignalDatabase

# Initialize
config = GoogleNewsConfig()
plugin = GoogleNewsPlugin(config)
db = SignalDatabase(config.database_path)

# Scrape top news
signals = plugin.scrape(limit=10)

# Search for news
signals = plugin.scrape(keywords="climate change", limit=5)

# Store in database
for signal in signals:
    db.store_signal(signal, source='google_news')

# Query signals
recent_signals = db.get_recent_signals(limit=20)
```

## Signal Format

Each news signal includes:

```python
{
    'source_id': 'article_title_slug_20251030',
    'signal_type': 'news',
    'name': 'Article Headline',
    'description': 'Article summary or description',
    'tags': ['google_news', 'news', 'topic'],
    'metrics': {
        'volume': 100,              # Base volume for news
        'velocity': 0.0,            # Growth rate (requires historical data)
        'acceleration': 0.0,        # Change in velocity
        'geographic_spread': ['global']
    },
    'temporal': {
        'first_seen': '2025-10-30T20:00:00Z',  # Publication date
        'peak_time': None,
        'current_status': 'active'
    },
    'extra': {
        'platform': 'google_news',
        'publisher': 'News Source Name',
        'url': 'https://example.com/article',
        'keywords': 'search_term',  # If searched
        'topic': 'topic_name'       # If topic-based
    }
}
```

## Operational Modes

### Production Mode (with gnews)
Requires gnews installation:
```bash
pip install gnews
```

### Stub Mode (without gnews)
Runs with sample data for testing and development. Automatically activates if gnews is not installed.

## Architecture

```
GoogleNews/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── google_news_plugin.py   # Google News implementation
├── tests/                          # Test suite
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e .[dev]

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test
pytest tests/test_google_news_plugin.py -v
```

### Code Quality

This implementation follows SOLID principles:
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugins
- **Liskov Substitution**: All plugins interchangeable
- **Interface Segregation**: Minimal plugin interface
- **Dependency Inversion**: Depends on abstractions

## Integration

GoogleNewsSource integrates with:
- **Model** - IdeaInspiration data model
- **ConfigLoad** - Centralized configuration
- **Unified Pipeline** - End-to-end processing
- **Signals Ecosystem** - Other signal sources

## News Categories

The gnews library supports various topics:
- WORLD
- NATION
- BUSINESS
- TECHNOLOGY
- ENTERTAINMENT
- SPORTS
- SCIENCE
- HEALTH

## Known Limitations

- gnews is a lightweight wrapper and may have rate limits
- News data freshness depends on Google News update frequency
- Stub mode provides sample data only (for testing)
- Velocity and acceleration metrics require historical data

## Troubleshooting

### gnews Import Error
```
Warning: gnews not installed
```
**Solution**: Install with `pip install gnews` or use stub mode

### API Errors
```
Error scraping Google News: ...
```
**Solutions**:
- Check internet connection
- Verify gnews is up to date
- Use stub mode for testing

### Database Locked
```
Database is locked
```
**Solution**: Close other connections to the database

## License

Proprietary - Part of PrismQ.IdeaInspiration ecosystem

## Status

✅ **IMPLEMENTED** - Fully functional with stub mode support

## Contributing

1. Follow the implementation guide in `Sources/Signals/IMPLEMENTATION_GUIDE.md`
2. Write tests for new features
3. Update documentation
4. Ensure code coverage >80%
5. Follow SOLID principles

## Support

For issues or questions:
- Check implementation guide: `Sources/Signals/IMPLEMENTATION_GUIDE.md`
- Reference: `Sources/Signals/Trends/GoogleTrends/`
- Issue tracker: `_meta/issues/`
