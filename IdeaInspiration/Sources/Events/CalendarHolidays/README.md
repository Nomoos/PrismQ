# CalendarHolidays Source

**PrismQ module for gathering event inspirations from calendar holidays and observances**

## Overview

CalendarHolidays is a PrismQ source module that collects holidays, observances, and special days from various calendars to identify content opportunities around these events.

## Features

- Scrapes holidays from Python holidays library (no API key needed)
- Supports 100+ countries
- Calculates content windows (pre/post event coverage)
- Assigns significance and importance scores
- Identifies recurring events
- Stores in SQLite database with deduplication
- Unified event signal format for cross-platform compatibility

## Installation

1. Navigate to this directory:
   ```bash
   cd Sources/Events/CalendarHolidays
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

### Scrape Holidays

Scrape holidays for a specific country and year:

```bash
python -m src.cli scrape --country US --year 2025
python -m src.cli scrape --country GB --year 2025
python -m src.cli scrape --country CA --year 2025
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
CALENDAR_HOLIDAYS_DB_PATH=/path/to/data/calendar_holidays.db

# Default country (ISO 3166-1 alpha-2 code)
CALENDAR_DEFAULT_COUNTRY=US

# Default year
CALENDAR_DEFAULT_YEAR=2025

# Max events to fetch
CALENDAR_MAX_EVENTS=100
```

## Supported Countries

The Python holidays library supports 100+ countries including:
- US (United States)
- GB (United Kingdom)
- CA (Canada)
- AU (Australia)
- DE (Germany)
- FR (France)
- IT (Italy)
- ES (Spain)
- MX (Mexico)
- BR (Brazil)
- IN (India)
- JP (Japan)
- CN (China)
- And many more...

## Event Signal Format

Each holiday is transformed into a unified event signal:

```python
{
    'source': 'calendar_holidays',
    'source_id': 'US_Christmas_Day_2025-12-25',
    'event': {
        'name': 'Christmas Day',
        'type': 'holiday',
        'date': '2025-12-25',
        'recurring': True,
        'recurrence_pattern': 'annual'
    },
    'significance': {
        'scope': 'global',
        'importance': 'major',
        'audience_size_estimate': 2000000000
    },
    'content_window': {
        'pre_event_days': 21,
        'post_event_days': 14,
        'peak_day': '2025-12-25'
    },
    'metadata': {
        'country': 'US',
        'description': 'Christmas Day - US holiday'
    },
    'universal_metrics': {
        'significance_score': 10.0,
        'content_opportunity': 9.0,
        'audience_interest': 10.0
    }
}
```

## Architecture

```
CalendarHolidays/
├── src/
│   ├── cli.py                      # Command-line interface
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # SQLite operations
│   │   ├── metrics.py              # Universal metrics
│   │   └── event_processor.py     # Event processing
│   └── plugins/
│       ├── __init__.py             # Plugin base class
│       └── calendar_holidays_plugin.py  # Holidays library plugin
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

- **Sources/Events/SportsHighlights** - Sports events source
- **Sources/Events/EntertainmentReleases** - Entertainment releases source
- **Model** - Core IdeaInspiration data model
- **Classification** - Content categorization
- **Scoring** - Content evaluation

## License

Proprietary - All Rights Reserved - Copyright (c) 2025 PrismQ
