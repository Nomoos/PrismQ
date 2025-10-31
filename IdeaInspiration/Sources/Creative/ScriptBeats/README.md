# ScriptBeatsSource

**PrismQ Creative Source** for gathering narrative structures and story beats.

## Status

🚧 **In Development** - Core structure implemented, manual curation focus.

## Overview

ScriptBeatsSource collects narrative structures, story beats, and screenplay elements from various sources. It focuses on manual curation of proven story structures, character arcs, and narrative devices.

## Planned Features

- **Manual Import**: Import story structures from JSON/CSV
- **Beat Sheet Templates**: Save's Cat's Beats, Hero's Journey, etc.
- **Character Arc Tracking**: Store character development patterns
- **Structure Metrics**: Track narrative effectiveness and versatility
- **Genre Classification**: Categorize by story type and genre

## Architecture

Based on LyricSnippetsSource with focus on manual curation:

```
ScriptBeats/
├── src/
│   ├── cli.py                  # CLI for narrative collection
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Story structure storage
│   │   └── metrics.py         # Narrative metrics
│   └── plugins/
│       ├── manual_import_plugin.py  # JSON/CSV import
│       └── template_plugin.py       # Built-in templates
└── _meta/tests/               # Test suite
```

## Configuration

```env
DATABASE_URL=sqlite:///script_beats.s3db
```

## Data Model

```python
{
    'source': 'manual|template',
    'source_id': 'unique_id',
    'title': 'Three-Act Structure - Hero\'s Journey',
    'content': 'Detailed beat-by-beat breakdown...',
    'tags': 'narrative,structure,hero',
    'score': 9.0,
    'score_dictionary': {
        'emotional_impact': 8.5,
        'versatility': 9.5,
        'inspiration_value': 9.0,
        'content_type': 'narrative',
        'content_format': 'text',
        'structure_type': 'three-act',
        'genre': ['adventure', 'drama'],
        'themes': ['transformation', 'conflict'],
        'beat_count': 15
    }
}
```

## Built-in Templates

- Save the Cat! 15 Beats
- Hero's Journey (Campbell)
- Three-Act Structure
- Five-Act Structure (Freytag's Pyramid)
- Kishotenketsu (4-Act Asian)
- Seven-Point Story Structure

## Next Steps

1. Implement manual import plugin
2. Add built-in story structure templates
3. Create beat sheet validation
4. Add narrative analysis tools
5. Complete test suite

## License

Proprietary - PrismQ
