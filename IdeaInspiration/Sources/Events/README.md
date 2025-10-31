# Events Sources

Scheduled events and cultural moments that drive content opportunities.

## Overview

Events sources track scheduled occurrences including holidays, sports events, and entertainment releases that create natural content opportunities.

## Implemented Sources

### ✅ [CalendarHolidaysSource](./CalendarHolidays/)
Holidays, observances, and special days from 100+ countries.

**Features**:
- Python `holidays` library (no API key needed)
- Automatic recurrence detection
- Global to local scope classification
- Tested and working

**Usage**:
```bash
cd CalendarHolidays
python -m src.cli scrape --country US --year 2025
```

### ✅ [SportsHighlightsSource](./SportsHighlights/)
Major sports events, games, and highlights from worldwide leagues.

**Features**:
- TheSportsDB API integration
- Multiple sports and leagues
- Championship and playoff detection
- Expected viewership estimation

**Usage**:
```bash
cd SportsHighlights
python -m src.cli scrape --next
```

### ✅ [EntertainmentReleasesSource](./EntertainmentReleases/)
Movie, TV, game, and music releases from entertainment databases.

**Features**:
- TMDB API for movies and TV shows
- Blockbuster classification
- Franchise detection
- Popularity and rating metrics

**Usage**:
```bash
cd EntertainmentReleases
python -m src.cli scrape --media-type movie
```

## Unified Event Signal Format

All sources use a consistent data format:

```python
{
    'source': 'source_name',
    'source_id': 'unique_id',
    'event': {...},
    'significance': {...},
    'content_window': {...},
    'metadata': {...},
    'universal_metrics': {...}
}
```

See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for complete details.

## Purpose

Events sources help identify:
- Upcoming content opportunities
- Seasonal themes and topics
- Cultural moments to leverage
- Timely content hooks
- Audience attention peaks

## Related Documentation

- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Complete technical details
- [Issue #023](../../_meta/issues/done/023-implement-events-category.md) - Original requirements
