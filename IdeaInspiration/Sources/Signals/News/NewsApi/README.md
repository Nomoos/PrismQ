# NewsApiSource

**News articles from NewsAPI**

## Overview

NewsApiSource collects news signals from NewsAPI to identify breaking news, trending topics, and emerging stories. This source is part of the PrismQ.IdeaInspiration ecosystem and provides timely content opportunities based on current events.

## Features

- ✅ Collects news headlines from NewsAPI
- ✅ Searches news by keywords and topics
- ✅ Calculates trend velocity and acceleration
- ✅ Universal signal metrics (trend strength, virality score)
- ✅ SQLite database with deduplication
- ✅ CLI interface for easy management
- ✅ SOLID architecture with plugin system
- ✅ Comprehensive test coverage
- ✅ Stub mode for testing without API key

## Installation

```bash
# Navigate to this directory
cd Sources/Signals/News/NewsApi

# Install dependencies
pip install -e .
```

## Dependencies

- `newsapi-python` - NewsAPI client (optional - runs in stub mode if not available)
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_news_api.db`)
- `NEWS_API_API_KEY` - Your NewsAPI key (required for production mode)
- `MAX_RESULTS` - Maximum news articles per scrape (default: 25)
- `TIMEFRAME_DAYS` - Time range for news (default: 7)
- `RETRY_DELAY_SECONDS` - Delay between API calls (default: 2)

## Usage

### CLI Commands

#### Scrape News Signals
```bash
# Scrape top headlines
python -m src.cli scrape

# Scrape with custom limit
python -m src.cli scrape --limit 10

# Search for specific topics
python -m src.cli scrape --query "technology"
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

## Operational Modes

### Production Mode (with NewsAPI key)
Requires NewsAPI key in `.env`:
```bash
NEWS_API_API_KEY=your_api_key_here
```

Get your API key at: https://newsapi.org/

### Stub Mode (without API key)
Runs with sample data for testing and development. Automatically activates if API key is not configured.

## Architecture

```
NewsApi/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── news_api_plugin.py      # NewsAPI implementation
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
```

### Code Quality

This implementation follows SOLID principles:
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugins
- **Liskov Substitution**: All plugins interchangeable
- **Interface Segregation**: Minimal plugin interface
- **Dependency Inversion**: Depends on abstractions

## License

Proprietary - Part of PrismQ.IdeaInspiration ecosystem

## Status

✅ **IMPLEMENTED** - Fully functional with stub mode support
