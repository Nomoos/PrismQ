# SocialChallengeSource

**Viral social media challenges**

## Overview

SocialChallengeSource tracks viral social media challenges across platforms. This source is part of the PrismQ.IdeaInspiration ecosystem and provides insights into emerging challenge trends for content creation.

## Features

- ✅ Tracks viral social media challenges
- ✅ Identifies challenge origins and participation rates
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
cd Sources/Signals/Challenges/SocialChallenge

# Install dependencies
pip install -e .
```

## Dependencies

- `requests` - Web requests
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_social_challenge.db`)
- `MAX_RESULTS` - Maximum challenges per scrape (default: 25)
- `TIMEFRAME_DAYS` - Time range for tracking (default: 7)
- `RETRY_DELAY_SECONDS` - Delay between scrapes (default: 2)

## Usage

### CLI Commands

#### Scrape Challenge Signals
```bash
# Track trending challenges
python -m src.cli scrape

# Track with custom limit
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
python -m src.cli export challenges.csv --format csv

# Export to JSON
python -m src.cli export challenges.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

## Operational Modes

### Production Mode
Tracks challenges from configured platforms

### Stub Mode
Runs with sample data for testing and development.

## Architecture

```
SocialChallenge/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── social_challenge_plugin.py  # Challenge tracking implementation
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
