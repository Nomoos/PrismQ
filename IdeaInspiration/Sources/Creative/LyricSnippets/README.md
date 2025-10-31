# LyricSnippetsSource

**PrismQ Creative Source** for gathering lyrical and poetic inspiration from song lyrics.

## Overview

LyricSnippetsSource collects meaningful lyric snippets from various sources to provide creative inspiration for content generation projects. It extracts emotional themes, narrative elements, and artistic expressions from popular songs.

## Features

- **Genius API Integration**: Scrape trending and specific songs from Genius
- **Manual Curation**: Import custom lyric collections from JSON/CSV
- **Creative Metrics**: Track emotional impact, versatility, and inspiration value
- **Attribution Tracking**: Maintain creator credits and licensing information
- **Unified Format**: Transform all sources into standardized creative resource format

## Installation

```bash
cd Sources/Creative/LyricSnippets
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in your PrismQ working directory:

```env
# Database configuration
DATABASE_URL=sqlite:///lyric_snippets.s3db

# Genius API (get from https://genius.com/api-clients)
GENIUS_API_KEY=your_genius_api_key_here
GENIUS_MAX_RESULTS=50
```

## Usage

### Scrape from Genius API

```bash
# Search for lyric snippets
python -m src.cli scrape --query "love songs"
python -m src.cli scrape --query "hip hop" --max-results 20

# Get a specific song
python -m src.cli scrape-song --title "Bohemian Rhapsody" --artist "Queen"
```

### Import from Files

```bash
# Import from JSON
python -m src.cli import-file --file lyrics.json

# Import from CSV
python -m src.cli import-file --file lyrics.csv
```

#### JSON Format

```json
[
  {
    "title": "Song Title - Artist",
    "content": "Lyric snippet text...",
    "creator": "Artist Name",
    "work_title": "Song Title",
    "themes": ["love", "loss"],
    "mood": "melancholic",
    "style": "modern",
    "license": "All Rights Reserved",
    "emotional_impact": 8.5,
    "versatility": 6.0,
    "inspiration_value": 7.5
  }
]
```

#### CSV Format

```csv
title,content,creator,work_title,themes,mood,style,license,emotional_impact,versatility,inspiration_value
"Song - Artist","Lyrics...","Artist","Song","love,loss","melancholic","modern","All Rights Reserved",8.5,6.0,7.5
```

### List and Statistics

```bash
# List collected snippets
python -m src.cli list --limit 20
python -m src.cli list --source genius

# Show statistics
python -m src.cli stats

# Clear database
python -m src.cli clear
```

## Data Model

Each lyric snippet is stored with:

```python
{
    'source': 'genius|manual',
    'source_id': 'unique_id',
    'title': 'Song Title - Artist',
    'content': 'Lyric snippet text...',
    'tags': 'lyrics,genius,artist_name',
    'score': 7.5,  # Inspiration value
    'score_dictionary': {
        'emotional_impact': 8.5,
        'versatility': 6.0,
        'inspiration_value': 7.5,
        'content_type': 'lyrics',
        'content_format': 'text',
        'creator': 'Artist Name',
        'work_title': 'Song Title',
        'themes': ['love', 'loss'],
        'mood': 'melancholic',
        'style': 'modern',
        'license_type': 'All Rights Reserved'
    }
}
```

## Creative Metrics

### Core Metrics (0-10 scale)
- **Emotional Impact**: How powerfully the lyrics evoke emotion
- **Versatility**: Reusability across different projects
- **Inspiration Value**: Overall creative inspiration potential

### Thematic Elements
- **Themes**: Tagged themes (love, loss, triumph, etc.)
- **Mood**: Emotional tone (melancholic, uplifting, dramatic)
- **Style**: Artistic style (modern, classical, abstract)

## API Access

### Genius API

1. Create account at https://genius.com/
2. Create API client at https://genius.com/api-clients
3. Copy API token to `.env` as `GENIUS_API_KEY`
4. Free tier includes reasonable rate limits

## Architecture

```
LyricSnippets/
├── src/
│   ├── cli.py                 # Command-line interface
│   ├── __main__.py           # Entry point
│   ├── core/
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database operations
│   │   └── metrics.py        # Creative metrics schema
│   └── plugins/
│       ├── genius_plugin.py  # Genius API integration
│       └── manual_import_plugin.py  # File import
├── _meta/tests/              # Test suite
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Design Principles

This source follows SOLID principles:

- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugins without modifying core
- **Liskov Substitution**: All plugins implement SourcePlugin interface
- **Interface Segregation**: Focused, minimal interfaces
- **Dependency Inversion**: Depends on abstractions (SourcePlugin)

## Copyright & Licensing

**IMPORTANT**: This tool is designed for creative inspiration and research purposes.

- Always respect copyright and licensing
- Track attribution and license information
- Only use lyrics with appropriate permissions
- Consider fair use implications
- Consult legal counsel for commercial use

Most song lyrics are copyrighted. This tool:
- Extracts short snippets (fair use consideration)
- Maintains attribution to original creators
- Tracks licensing information
- Does not distribute full lyrics

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=html
```

## Examples

### Example 1: Trending Lyrics

```bash
# Scrape trending songs
python -m src.cli scrape --query "trending" --max-results 10
python -m src.cli list --limit 10
```

### Example 2: Genre-Specific

```bash
# Hip hop lyrics
python -m src.cli scrape --query "hip hop classics" --max-results 20

# Country ballads
python -m src.cli scrape --query "country love songs" --max-results 15
```

### Example 3: Manual Collection

Create `my_lyrics.json`:
```json
[
  {
    "title": "Custom Lyric 1",
    "content": "Your curated lyric snippet...",
    "themes": ["inspiration", "motivation"],
    "mood": "uplifting",
    "emotional_impact": 9.0
  }
]
```

```bash
python -m src.cli import-file --file my_lyrics.json
```

## Contributing

When adding new features:
1. Follow SOLID principles
2. Add comprehensive tests
3. Update documentation
4. Respect copyright and licensing

## License

Proprietary - PrismQ

## Related Sources

- **ScriptBeatsSource**: Narrative structures and story beats
- **VisualMoodboardSource**: Visual aesthetics and design inspiration
