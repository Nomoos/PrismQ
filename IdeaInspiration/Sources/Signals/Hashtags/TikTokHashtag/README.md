# TikTokHashtagSource

**Trending hashtags on TikTok**

## Overview

TikTokHashtagSource collects hashtag signals from TikTok to identify viral trends and popular topics. This source is part of the PrismQ.IdeaInspiration ecosystem and provides early indicators of trending content on one of the world's fastest-growing social platforms.

## Features

- ✅ Collects trending TikTok hashtags
- ✅ Tracks hashtag view counts and video counts
- ✅ Calculates trend velocity and acceleration
- ✅ Universal signal metrics (trend strength, virality score)
- ✅ SQLite database with deduplication
- ✅ CLI interface for easy management
- ✅ SOLID architecture with plugin system
- ✅ Comprehensive test coverage
- ✅ Stub mode for testing without API

## Installation

```bash
# Navigate to this directory
cd Sources/Signals/Hashtags/TikTokHashtag

# Install dependencies
pip install -e .
```

## Dependencies

- `TikTokApi` - TikTok data access (optional - runs in stub mode if not available)
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_tiktok_hashtag.db`)
- `MAX_RESULTS` - Maximum hashtags per scrape (default: 25)
- `TIMEFRAME_DAYS` - Time range for trends (default: 7)
- `RETRY_DELAY_SECONDS` - Delay between API calls (default: 2)

## Usage

### CLI Commands

#### Scrape Hashtag Signals
```bash
# Scrape trending hashtags
python -m src.cli scrape

# Scrape with custom limit
python -m src.cli scrape --limit 10

# Scrape specific hashtags
python -m src.cli scrape --hashtags "fyp,viral,trending"
```

#### List Signals
```bash
# List all signals
python -m src.cli list

# List with limit
python -m src.cli list --limit 20

# List sorted by volume
python -m src.cli list --sort volume --limit 10
```

#### Show Statistics
```bash
python -m src.cli stats
```

#### Export Data
```bash
# Export to CSV
python -m src.cli export hashtags.csv --format csv

# Export to JSON
python -m src.cli export hashtags.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

### Python API

```python
from src.core.config import TikTokHashtagConfig
from src.plugins.tik_tok_hashtag_plugin import TikTokHashtagPlugin
from src.core.database import SignalDatabase

# Initialize
config = TikTokHashtagConfig()
plugin = TikTokHashtagPlugin(config)
db = SignalDatabase(config.database_path)

# Scrape hashtags
signals = plugin.scrape(limit=10)

# Store in database
for signal in signals:
    db.store_signal(signal, source='tiktok_hashtag')

# Query signals
recent_signals = db.get_recent_signals(limit=20)
```

## Signal Format

Each hashtag signal includes:

```python
{
    'source_id': 'hashtag_name_20251030',
    'signal_type': 'hashtag',
    'name': '#HashtagName',
    'description': 'Hashtag description',
    'tags': ['tiktok', 'hashtag', 'viral'],
    'metrics': {
        'volume': 500000000,        # View count
        'velocity': 85.5,            # Growth rate (0-100)
        'acceleration': 15.2,        # Change in velocity
        'geographic_spread': ['global'],
        'video_count': 2000000       # Number of videos
    },
    'temporal': {
        'first_seen': '2025-10-30T20:00:00Z',
        'peak_time': None,
        'current_status': 'rising'   # rising/peak/stable/declining
    },
    'extra': {
        'platform': 'tiktok',
        'hashtag_type': 'trending'
    }
}
```

## Operational Modes

### Production Mode (with TikTokApi)
Requires TikTokApi installation:
```bash
pip install TikTokApi
```

### Stub Mode (without TikTokApi)
Runs with sample data for testing and development. Automatically activates if TikTokApi is not installed.

## Architecture

```
TikTokHashtag/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── tik_tok_hashtag_plugin.py  # TikTok implementation
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
pytest tests/test_tik_tok_hashtag_plugin.py -v
```

### Code Quality

This implementation follows SOLID principles:
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugins
- **Liskov Substitution**: All plugins interchangeable
- **Interface Segregation**: Minimal plugin interface
- **Dependency Inversion**: Depends on abstractions

## Integration

TikTokHashtagSource integrates with:
- **Model** - IdeaInspiration data model
- **ConfigLoad** - Centralized configuration
- **Unified Pipeline** - End-to-end processing
- **Signals Ecosystem** - Other signal sources

## Known Limitations

- TikTokApi may require periodic updates as TikTok changes their API
- Rate limiting: Respect TikTok's rate limits (implement delays)
- Authentication: Some features may require TikTok account
- Stub mode provides sample data only (for testing)

## Troubleshooting

### TikTokApi Import Error
```
Warning: TikTokApi not installed
```
**Solution**: Install with `pip install TikTokApi` or use stub mode

### API Errors
```
Error scraping TikTok hashtags: ...
```
**Solutions**:
- Check internet connection
- Verify TikTokApi is up to date
- Increase retry delay in `.env`
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
