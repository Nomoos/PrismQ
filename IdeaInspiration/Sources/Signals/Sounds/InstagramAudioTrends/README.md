# InstagramAudioTrendsSource

**Audio trends on Instagram Reels**

## Overview

InstagramAudioTrendsSource collects audio trend signals from Instagram Reels to identify viral sounds and music. This source is part of the PrismQ.IdeaInspiration ecosystem and provides early indicators of trending audio for content creation strategy.

## Features

- ✅ Collects trending Instagram Reels audio
- ✅ Tracks audio usage counts and trends
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
cd Sources/Signals/Sounds/InstagramAudioTrends

# Install dependencies
pip install -e .
```

## Dependencies

- `instaloader` - Instagram data access (optional - runs in stub mode if not available)
- `ConfigLoad` - Configuration management
- `SQLite` - Data persistence
- `pytest`, `pytest-cov` - Testing

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:
- `DATABASE_PATH` - Path to SQLite database (default: `signals_instagram_audio_trends.db`)
- `MAX_RESULTS` - Maximum audio trends per scrape (default: 25)
- `TIMEFRAME_DAYS` - Time range for trends (default: 7)
- `RETRY_DELAY_SECONDS` - Delay between API calls (default: 2)

## Usage

### CLI Commands

#### Scrape Audio Signals
```bash
# Scrape trending audio
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
python -m src.cli export audio.csv --format csv

# Export to JSON
python -m src.cli export audio.json --format json
```

#### Clear Database
```bash
python -m src.cli clear
```

## Operational Modes

### Production Mode (with instaloader)
Requires instaloader installation:
```bash
pip install instaloader
```

### Stub Mode (without instaloader)
Runs with sample data for testing and development. Automatically activates if instaloader is not installed.

## Architecture

```
InstagramAudioTrends/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── signal_processor.py    # Signal transformation
│   └── plugins/
│       ├── __init__.py             # SignalPlugin base class
│       └── instagram_audio_trends_plugin.py  # Instagram implementation
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
