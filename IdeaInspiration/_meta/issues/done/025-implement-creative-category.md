# Implement Creative Category Sources

**Type**: Feature
**Priority**: Low
**Status**: New
**Category**: Creative
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement all Creative category sources for collecting creative resources and inspiration including lyric snippets, narrative structures, and visual aesthetics.

## Sources

### Creative
- **LyricSnippetsSource** - Song lyrics and poetry for creative inspiration
- **ScriptBeatsSource** - Story structures and narrative beats
- **VisualMoodboardSource** - Visual aesthetics and design inspiration

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Implement all 3 Creative sources following SOLID principles
2. Extract creative elements and patterns
3. Support manual curation and automated discovery
4. Transform data to unified creative resource format
5. Store in SQLite databases with deduplication

## Key Features (Common Across All Sources)

### Data Collection
- Creative element metadata (text, image, video, audio)
- Source attribution (artist, creator, work)
- Thematic tags and categories
- Mood/emotion indicators
- Usage rights and licensing info
- Curated collections

### Methods
- Manual curation and tagging
- Web scraping (lyrics sites, story databases)
- API integration (Genius, Unsplash, Pinterest)
- File imports (local collections)
- AI-powered pattern extraction

### Universal Metrics
- Emotional impact scoring
- Thematic relevance
- Versatility (reusability across projects)
- Inspiration value

## Technical Requirements

### Architecture (Example: LyricSnippets)
```
LyricSnippets/
├── src/
│   ├── cli.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── metrics.py
│   │   └── creative_processor.py
│   └── plugins/
│       ├── __init__.py
│       ├── genius_plugin.py
│       └── manual_import_plugin.py
```

### Dependencies (Varies by Source)
- lyricsgenius (Genius API)
- unsplash-python (Unsplash API)
- pinterest-api (Pinterest - unofficial)
- Pillow (image processing)
- SQLite, ConfigLoad (all sources)

### Data Model (Generic Creative Resource)
```python
{
    'source': 'creative_source_name',
    'source_id': 'resource_id',
    'resource': {
        'type': 'lyrics|narrative|visual',
        'content': 'Creative content',
        'title': 'Resource title',
        'format': 'text|image|video|audio'
    },
    'attribution': {
        'creator': 'Creator name',
        'work': 'Original work title',
        'license': 'CC-BY|All Rights Reserved|etc'
    },
    'metadata': {
        'themes': ['love', 'loss', 'triumph'],
        'mood': 'melancholic|uplifting|dramatic',
        'style': 'modern|classical|abstract',
        'medium': 'poetry|screenplay|painting'
    },
    'universal_metrics': {
        'emotional_impact': 7.8,
        'versatility': 6.5,
        'inspiration_value': 8.2
    }
}
```

## Success Criteria

- [ ] All 3 Creative sources implemented
- [ ] Each source follows SOLID principles
- [ ] Creative elements extracted
- [ ] Manual curation supported
- [ ] Automated discovery working (where applicable)
- [ ] Attribution and licensing tracked
- [ ] Data transforms to unified format
- [ ] CLI interfaces consistent
- [ ] Comprehensive tests (>80% coverage)
- [ ] Documentation complete

## Implementation Priority

1. **LyricSnippetsSource** - Text-based, API available (Genius)
2. **VisualMoodboardSource** - Rich APIs (Unsplash, Pinterest)
3. **ScriptBeatsSource** - More manual, requires curation

## Related Issues

- #001 - Unified Pipeline Integration

## API Considerations

### Lyrics (Genius)
- Genius API: https://docs.genius.com/
- Free tier available
- Lyrics extraction from web pages

### Visual (Unsplash, Pinterest)
- Unsplash API: https://unsplash.com/developers
- Pinterest API: unofficial libraries
- Consider copyright and licensing

### Narrative/Scripts
- No major APIs
- Manual import primary method
- Consider building internal database

## Estimated Effort

4-6 weeks total
- LyricSnippetsSource: 1-2 weeks
- VisualMoodboardSource: 2 weeks
- ScriptBeatsSource: 1-2 weeks

## Notes

Creative sources are supplementary and provide inspiration rather than direct content ideas. Lower priority than content and signal sources but valuable for adding creative depth to generated content.

**Copyright Notice**: Be extremely careful with licensing and attribution. Only use content with appropriate licenses or permissions.
