# Creative Sources

Creative inspiration and artistic reference materials.

## Overview

Creative sources provide artistic and narrative inspiration including music, storytelling structures, and visual aesthetics.

## Sources

### ✅ LyricSnippetsSource (Complete)
**Status**: Fully implemented and tested

Trending lyric excerpts and musical phrases from Genius API and manual imports.

**Features**:
- Genius API integration for lyric scraping
- Manual import from JSON/CSV
- Creative metrics (emotional impact, versatility, inspiration value)
- SQLite database with deduplication
- 17/17 tests passing

**Usage**:
```bash
cd LyricSnippets
python -m src.cli scrape --query "love songs" --max-results 20
python -m src.cli list --limit 10
```

### ✅ VisualMoodboardSource (Complete)
**Status**: Fully implemented

Visual trends and aesthetic themes from Unsplash and manual curation.

**Features**:
- Unsplash API integration for visual inspiration
- Random and curated photo fetching
- Manual import of visual collections
- Creative metrics for visual content
- Image URL storage

**Usage**:
```bash
cd VisualMoodboard
python -m src.cli scrape --query "minimalist design"
python -m src.cli random --count 15
python -m src.cli list
```

### ✅ ScriptBeatsSource (Complete)
**Status**: Fully implemented

Narrative structures and story beats for storytelling inspiration.

**Features**:
- 6 built-in story structure templates:
  - Save the Cat! (15-Beat)
  - Hero's Journey (Campbell)
  - Three-Act Structure
  - Five-Act Structure (Freytag)
  - Kishōtenketsu (4-Act Asian)
  - Seven-Point Story Structure
- Manual import of custom narratives
- Detailed beat breakdowns
- Structure metrics and analysis

**Usage**:
```bash
cd ScriptBeats
python -m src.cli load-templates
python -m src.cli list-templates
python -m src.cli show-template --template-id save_the_cat
```

## Purpose

Creative sources help identify:
- Emotional themes and tones
- Narrative structures
- Visual trends and aesthetics
- Cultural artistic movements
- Creative inspiration patterns

## Architecture

All Creative sources follow a consistent SOLID architecture:

```
<Source>/
├── src/
│   ├── cli.py                 # Command-line interface
│   ├── core/
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # Database operations
│   │   └── metrics.py        # Creative metrics schema
│   └── plugins/
│       ├── <api>_plugin.py   # API integration
│       └── manual_import_plugin.py  # Manual curation
└── _meta/tests/              # Comprehensive test suite
```

## Creative Metrics

All sources track:
- **Emotional Impact**: 0-10 scale
- **Versatility**: Reusability across projects (0-10)
- **Inspiration Value**: Overall creative potential (0-10)
- **Themes**: Tagged thematic elements
- **Mood**: Emotional tone descriptors
- **Style**: Artistic style classifications

## Design Principles

All Creative sources follow **SOLID principles**:
- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extensible through plugins
- **Liskov Substitution**: All plugins implement SourcePlugin interface
- **Interface Segregation**: Focused, minimal interfaces
- **Dependency Inversion**: Depends on abstractions

## Copyright & Licensing

**IMPORTANT**: All sources are designed for creative inspiration and research.

- Always respect copyright and licensing
- Track attribution information
- Only use content with appropriate permissions
- Consider fair use implications

## Contributing

When adding new sources or features:
1. Follow the established architecture
2. Implement comprehensive tests (>80% coverage)
3. Document APIs and usage
4. Respect licensing and attribution requirements

