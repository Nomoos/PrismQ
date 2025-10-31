# Implement Events Category Sources

**Type**: Feature
**Priority**: Medium
**Status**: New
**Category**: Events
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement all Events category sources for collecting scheduled and recurring events that drive content opportunities.

## Sources

### Events
- **CalendarHolidaysSource** - Holidays, observances, and special days
- **SportsHighlightsSource** - Major sports events and highlights
- **EntertainmentReleasesSource** - Movie, TV, game, music releases

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Implement all 3 Events sources following SOLID principles
2. Extract event schedules and metadata
3. Predict content opportunities around events
4. Transform data to unified event signal format
5. Store in SQLite databases with deduplication

## Key Features (Common Across All Sources)

### Data Collection
- Event metadata (name, type, date, time, location)
- Event attributes (participants, significance, recurring)
- Pre-event buildup and post-event coverage windows
- Related events and series
- Historical data and patterns
- Audience interest indicators

### Scraping Methods
- Calendar APIs (Google Calendar, Calendarific)
- Sports APIs (ESPN, The Sports DB)
- Entertainment databases (TMDB, IGDB, MusicBrainz)
- Web scraping for event listings
- RSS feeds for release schedules

### Universal Metrics
- Event significance scoring
- Audience interest estimates
- Content opportunity window
- Recurrence pattern
- Cross-platform normalization

## Technical Requirements

### Architecture (Example: CalendarHolidays)
```
CalendarHolidays/
├── src/
│   ├── cli.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── event_processor.py
│   └── plugins/
│       ├── __init__.py
│       └── calendar_api_plugin.py
```

### Dependencies (Varies by Source)
- holidays (Python holidays library)
- calendarific API
- ESPN API or thesportsdb
- tmdbsimple (The Movie Database)
- IGDB API wrapper (video games)
- SQLite, ConfigLoad (all sources)

### Data Model (Generic Event Signal)
```python
{
    'source': 'event_source_name',
    'source_id': 'event_id',
    'event': {
        'name': 'Event Name',
        'type': 'holiday|sports|movie|game|music',
        'date': '2025-12-25',
        'recurring': True,
        'recurrence_pattern': 'annual'
    },
    'significance': {
        'scope': 'global|national|regional|local',
        'importance': 'major|moderate|minor',
        'audience_size_estimate': 1000000000
    },
    'content_window': {
        'pre_event_days': 14,  # start coverage 2 weeks before
        'post_event_days': 7,  # continue coverage 1 week after
        'peak_day': '2025-12-25'
    },
    'metadata': {
        'participants': ['team1', 'team2'],  # for sports
        'genre': ['action', 'adventure'],  # for entertainment
        'country': 'US'  # for holidays
    },
    'universal_metrics': {
        'significance_score': 9.5,
        'content_opportunity': 8.8,
        'audience_interest': 9.2
    }
}
```

## Success Criteria

- [ ] All 3 Events sources implemented
- [ ] Each source follows SOLID principles
- [ ] Event schedules extracted and stored
- [ ] Content opportunity windows calculated
- [ ] Recurring event patterns identified
- [ ] Deduplication working for all sources
- [ ] Data transforms to unified format
- [ ] CLI interfaces consistent
- [ ] Comprehensive tests (>80% coverage)
- [ ] Documentation complete

## Implementation Priority

1. **CalendarHolidaysSource** - Easiest to implement, predictable data
2. **EntertainmentReleasesSource** - Rich APIs available (TMDB, IGDB)
3. **SportsHighlightsSource** - More complex, event-driven

## Related Issues

- #001 - Unified Pipeline Integration
- #008 - Advanced Source Integrations

## API Considerations

### Calendar/Holidays
- Calendarific API: https://calendarific.com/api-documentation
- Python holidays library (no API needed)
- Google Calendar API (for custom calendars)

### Sports
- ESPN API (unofficial)
- TheSportsDB API: https://www.thesportsdb.com/api.php
- SportsData.io (paid)

### Entertainment
- TMDB API: https://developers.themoviedb.org/
- IGDB (Twitch): https://api-docs.igdb.com/
- MusicBrainz: https://musicbrainz.org/doc/Development

## Estimated Effort

4-5 weeks total
- CalendarHolidays: 1 week
- EntertainmentReleases: 2 weeks
- SportsHighlights: 2 weeks

## Notes

Event-based content creation is highly effective because audiences are actively interested in events before, during, and after they occur. These sources enable proactive content planning and timely publication.

Consider building a content calendar feature that uses event data to suggest content topics and optimal publish times.
