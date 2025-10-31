# VisualMoodboardSource

**PrismQ Creative Source** for gathering visual aesthetics and design inspiration.

## Status

🚧 **In Development** - Core structure implemented, plugin integration in progress.

## Overview

VisualMoodboardSource collects visual inspiration from various sources including stock photo sites, Pinterest, and manual curation. It extracts aesthetic themes, color palettes, composition styles, and visual trends.

## Planned Features

- **Unsplash API Integration**: Scrape trending and themed images from Unsplash
- **Manual Curation**: Import custom visual collections from JSON/CSV
- **Creative Metrics**: Track visual impact, versatility, and inspiration value
- **Metadata Tracking**: Colors, composition, style, mood
- **Attribution Tracking**: Maintain creator credits and licensing information

## Architecture

Based on LyricSnippetsSource architecture with adaptations for visual content:

```
VisualMoodboard/
├── src/
│   ├── cli.py                  # CLI commands for visual collection
│   ├── core/
│   │   ├── config.py          # Unsplash API configuration
│   │   ├── database.py        # Image metadata storage
│   │   └── metrics.py         # Visual creative metrics
│   └── plugins/
│       ├── unsplash_plugin.py # Unsplash API integration
│       └── manual_import_plugin.py  # File/JSON import
└── _meta/tests/               # Test suite
```

## Configuration

```env
DATABASE_URL=sqlite:///visual_moodboard.s3db
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
UNSPLASH_MAX_RESULTS=30
```

## Data Model

```python
{
    'source': 'unsplash|manual',
    'source_id': 'unique_id',
    'title': 'Image Title',
    'url': 'https://image-url.jpg',
    'tags': 'visual,aesthetic,modern',
    'score': 8.5,
    'score_dictionary': {
        'emotional_impact': 9.0,
        'versatility': 7.5,
        'inspiration_value': 8.5,
        'content_type': 'visual',
        'content_format': 'image',
        'creator': 'Photographer Name',
        'themes': ['minimalist', 'nature'],
        'mood': 'serene',
        'style': 'modern',
        'colors': ['#FF5733', '#C70039'],
        'license_type': 'Unsplash License'
    }
}
```

## Next Steps

1. Complete Unsplash plugin implementation
2. Add image download and local storage
3. Implement color palette extraction
4. Add visual similarity scoring
5. Complete test suite

## License

Proprietary - PrismQ
