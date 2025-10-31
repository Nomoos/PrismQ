# KnowYourMemeSource

**Meme database and documentation from KnowYourMeme**

## Overview

KnowYourMemeSource collects meme signals from the KnowYourMeme database. This source is part of the PrismQ.IdeaInspiration ecosystem and provides detailed information about meme origins, evolution, and cultural context.

## Features

- ✅ Collects meme data from KnowYourMeme
- ✅ Tracks meme popularity and evolution
- ✅ Calculates trend velocity and acceleration
- ✅ Universal signal metrics (trend strength, virality score)
- ✅ SQLite database with deduplication
- ✅ CLI interface for easy management
- ✅ SOLID architecture with plugin system
- ✅ Comprehensive test coverage
- ✅ Stub mode for testing

## Installation

```bash
# Navigate to this directory
cd Sources/Signals/Memes/KnowYourMeme

# Install dependencies
pip install -e .
```

## Dependencies

- `requests`, `BeautifulSoup4` - Web scraping
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_know_your_meme.db`)
- `MAX_RESULTS` - Maximum memes per scrape (default: 25)
- `TIMEFRAME_DAYS` - Time range for trends (default: 7)
- `RETRY_DELAY_SECONDS` - Delay between API calls (default: 2)

## Usage

### CLI Commands

#### Scrape Meme Signals
```bash
# Scrape trending memes
python -m src.cli scrape

# Scrape with custom limit
python -m src.cli scrape --limit 10
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
python -m src.cli export memes.csv --format csv

# Export to JSON
python -m src.cli export memes.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

## Operational Modes

### Production Mode
Scrapes from KnowYourMeme.com

### Stub Mode
Runs with sample data for testing and development.

## Architecture

```
KnowYourMeme/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── know_your_meme_plugin.py  # KnowYourMeme implementation
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
