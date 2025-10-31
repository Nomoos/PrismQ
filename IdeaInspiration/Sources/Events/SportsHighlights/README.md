# SportsHighlights Source

**PrismQ module for gathering event inspirations from sports events and highlights**

## Overview

SportsHighlights is a PrismQ source module that collects sports events, games, and highlights from various sports leagues and competitions to identify content opportunities around these events.

## Features

- Scrapes sports events from TheSportsDB API (free tier available)
- Supports multiple sports and leagues worldwide
- Calculates content windows (pre/post event coverage)
- Assigns significance and importance scores
- Estimates viewership and audience interest
- Stores in SQLite database with deduplication
- Unified event signal format for cross-platform compatibility

## Installation

1. Navigate to this directory:
   ```bash
   cd Sources/Events/SportsHighlights
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

## Usage

### Scrape Next Events

Scrape upcoming events from popular leagues:

```bash
python -m src.cli scrape --next
```

### Scrape Specific League

```bash
python -m src.cli scrape --league "English Premier League" --next
python -m src.cli scrape --league "NBA" --next
```

### Scrape Events by Date

```bash
python -m src.cli scrape --date 2025-01-15
```

### List Collected Events

```bash
python -m src.cli list --limit 20
```

### View Statistics

```bash
python -m src.cli stats
```

### Clear Database

```bash
python -m src.cli clear
```

## Configuration

Edit `.env` file:

```env
# Database path
SPORTS_HIGHLIGHTS_DB_PATH=/path/to/data/sports_highlights.db

# TheSportsDB API key (3 is the free test key)
THESPORTSDB_API_KEY=3

# Default sport and league
SPORTS_DEFAULT_SPORT=Soccer
SPORTS_DEFAULT_LEAGUE=English Premier League

# Max events to fetch
SPORTS_MAX_EVENTS=50
```

## Supported Sports & Leagues

TheSportsDB supports numerous sports and leagues including:

**Soccer/Football:**
- English Premier League
- Spanish La Liga
- German Bundesliga
- Italian Serie A
- French Ligue 1
- UEFA Champions League

**American Sports:**
- NBA (Basketball)
- NFL (American Football)
- MLB (Baseball)
- NHL (Ice Hockey)

**Other Sports:**
- Tennis
- Cricket
- Rugby
- Golf
- And many more...

## Event Signal Format

Each sports event is transformed into a unified event signal:

```python
{
    'source': 'thesportsdb',
    'source_id': '123456',
    'event': {
        'name': 'Manchester United vs Liverpool',
        'type': 'sports',
        'date': '2025-03-15',
        'recurring': False,
        'recurrence_pattern': None
    },
    'significance': {
        'scope': 'international',
        'importance': 'major',
        'audience_size_estimate': 500000000
    },
    'content_window': {
        'pre_event_days': 7,
        'post_event_days': 3,
        'peak_day': '2025-03-15'
    },
    'metadata': {
        'sport': 'Soccer',
        'league': 'English Premier League',
        'season': '2024-2025',
        'venue': 'Old Trafford',
        'participants': ['Manchester United', 'Liverpool']
    },
    'universal_metrics': {
        'significance_score': 9.0,
        'content_opportunity': 7.65,
        'audience_interest': 9.5
    }
}
```

## API Information

This module uses [TheSportsDB API](https://www.thesportsdb.com/api.php):
- Free tier available with test key: `3`
- Patreon subscription for higher limits
- Extensive coverage of sports worldwide

## Architecture

```
SportsHighlights/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # SQLite operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── event_processor.py     # Event processing
│   └── plugins/
│       ├── __init__.py             # Plugin base class
│       └── thesportsdb_plugin.py   # TheSportsDB API plugin
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
black src/
flake8 src/
mypy src/
```

## Related Modules

- **Sources/Events/CalendarHolidays** - Holiday events source
- **Sources/Events/EntertainmentReleases** - Entertainment releases source
- **Model** - Core IdeaInspiration data model
- **Classification** - Content categorization
- **Scoring** - Content evaluation

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
